#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
NEWTON GEOMETRY TESTS
════════════════════════════════════════════════════════════════════════════════

Comprehensive tests for all geometric structures:
    - Constraint Polytope
    - Decision Simplex
    - Governance Lattice
    - Expand/Reduce Manifold
    - Computation Graph
    - Module Hypergraph
    - Complete Topology

════════════════════════════════════════════════════════════════════════════════
"""

import pytest
from newton_geometry import (
    # Polytope
    ConstraintPolytope,
    FeasibilityRegion,
    Boundary,
    # Simplex
    DecisionSimplex,
    Decision,
    RiskLevel,
    # Lattice
    GovernanceLattice,
    SafetyLevel,
    LatticeNode,
    # Manifold
    ExpandReduceManifold,
    FiberBundle,
    TextPoint,
    ConstraintPoint,
    # Graph
    ComputationGraph,
    RequestType,
    GraphNode,
    PathResult,
    # Hypergraph
    ModuleHypergraph,
    NewtonModule,
    Channel,
    # Topology
    NewtonTopology,
    TopologyRegion,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT POLYTOPE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstraintPolytope:
    """Tests for the Constraint Polytope."""

    def test_boundary_creation(self):
        """Test boundary creation with valid parameters."""
        b = Boundary(name="test", f=0.5, g=1.0)
        assert b.ratio == 0.5
        assert b.region == FeasibilityRegion.FIN
        assert b.is_satisfied()

    def test_boundary_at_limit(self):
        """Test boundary at f/g = 1 (boundary region)."""
        b = Boundary(name="test", f=1.0, g=1.0)
        assert abs(b.ratio - 1.0) < 1e-10
        assert b.region == FeasibilityRegion.BOUNDARY
        assert b.is_satisfied()

    def test_boundary_exceeded(self):
        """Test boundary when f/g > 1 (infeasible)."""
        b = Boundary(name="test", f=1.5, g=1.0)
        assert b.ratio == 1.5
        assert b.region == FeasibilityRegion.FINFR
        assert not b.is_satisfied()

    def test_boundary_invalid_g(self):
        """Test that g <= 0 raises ValueError."""
        with pytest.raises(ValueError):
            Boundary(name="test", f=1.0, g=0.0)
        with pytest.raises(ValueError):
            Boundary(name="test", f=1.0, g=-1.0)

    def test_empty_polytope(self):
        """Test empty polytope is always feasible."""
        p = ConstraintPolytope(name="empty")
        assert p.is_feasible()
        assert p.region == FeasibilityRegion.FIN

    def test_polytope_single_constraint_satisfied(self):
        """Test polytope with single satisfied constraint."""
        p = ConstraintPolytope(name="test")
        p.add_boundary(Boundary(name="c1", f=0.3, g=1.0))
        assert p.is_feasible()
        assert p.region == FeasibilityRegion.FIN

    def test_polytope_single_constraint_violated(self):
        """Test polytope with single violated constraint."""
        p = ConstraintPolytope(name="test")
        p.add_boundary(Boundary(name="c1", f=1.5, g=1.0))
        assert not p.is_feasible()
        assert p.region == FeasibilityRegion.FINFR

    def test_polytope_multiple_constraints_all_satisfied(self):
        """Test polytope with multiple satisfied constraints."""
        p = ConstraintPolytope(name="test")
        p.add_boundary(Boundary(name="c1", f=0.3, g=1.0))
        p.add_boundary(Boundary(name="c2", f=0.5, g=1.0))
        p.add_boundary(Boundary(name="c3", f=0.7, g=1.0))
        assert p.is_feasible()
        assert len(p.violated_constraints) == 0

    def test_polytope_one_constraint_violated(self):
        """Test that one violated constraint makes polytope infeasible."""
        p = ConstraintPolytope(name="test")
        p.add_boundary(Boundary(name="c1", f=0.3, g=1.0))
        p.add_boundary(Boundary(name="c2", f=1.5, g=1.0))  # Violated
        p.add_boundary(Boundary(name="c3", f=0.7, g=1.0))
        assert not p.is_feasible()
        assert len(p.violated_constraints) == 1
        assert p.violated_constraints[0].name == "c2"

    def test_polytope_freeze(self):
        """Test that frozen polytope cannot be modified."""
        p = ConstraintPolytope(name="test")
        p.add_boundary(Boundary(name="c1", f=0.5, g=1.0))
        p.freeze()
        with pytest.raises(RuntimeError):
            p.add_boundary(Boundary(name="c2", f=0.3, g=1.0))


# ═══════════════════════════════════════════════════════════════════════════════
# DECISION SIMPLEX TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestDecisionSimplex:
    """Tests for the Decision Simplex."""

    def test_simplex_low_risk_high_clarity_high_capability(self):
        """Test that low risk + high clarity + high capability → ANSWER."""
        s = DecisionSimplex()
        decision, point = s.decide(risk_score=0.1, clarity_score=0.9, capability_score=0.9)
        assert decision == Decision.ANSWER

    def test_simplex_high_risk(self):
        """Test that high risk → REFUSE."""
        s = DecisionSimplex()
        decision, point = s.decide(risk_score=0.95, clarity_score=0.9, capability_score=0.9)
        assert decision == Decision.REFUSE

    def test_simplex_low_clarity(self):
        """Test that low clarity → ASK."""
        s = DecisionSimplex()
        decision, point = s.decide(risk_score=0.1, clarity_score=0.1, capability_score=0.9)
        assert decision == Decision.ASK

    def test_simplex_low_capability(self):
        """Test that low capability → DEFER."""
        s = DecisionSimplex()
        decision, point = s.decide(risk_score=0.1, clarity_score=0.9, capability_score=0.1)
        assert decision == Decision.DEFER

    def test_simplex_point_sums_to_one(self):
        """Test that barycentric coordinates sum to 1."""
        s = DecisionSimplex()
        _, point = s.decide(risk_score=0.5, clarity_score=0.5, capability_score=0.5)
        total = point.answer + point.defer + point.ask + point.refuse
        assert abs(total - 1.0) < 1e-10

    def test_simplex_escalation_to_refuse(self):
        """Test escalation to REFUSE transfers all weight."""
        s = DecisionSimplex()
        from newton_geometry.simplex import SimplexPoint
        point = SimplexPoint(answer=0.6, defer=0.2, ask=0.1, refuse=0.1)
        escalated = s.escalate(point, Decision.REFUSE)
        assert escalated.refuse == 1.0
        assert escalated.answer == 0.0

    def test_simplex_invalid_escalation(self):
        """Test that escalation TO answer raises error."""
        s = DecisionSimplex()
        from newton_geometry.simplex import SimplexPoint
        point = SimplexPoint(answer=0.6, defer=0.2, ask=0.1, refuse=0.1)
        with pytest.raises(ValueError):
            s.escalate(point, Decision.ANSWER)


# ═══════════════════════════════════════════════════════════════════════════════
# GOVERNANCE LATTICE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestGovernanceLattice:
    """Tests for the Governance Lattice."""

    def test_lattice_top_is_refuse(self):
        """Test that REFUSE is the top element."""
        lattice = GovernanceLattice()
        assert lattice.top.decision == Decision.REFUSE

    def test_lattice_bottom_is_answer(self):
        """Test that ANSWER is the bottom element."""
        lattice = GovernanceLattice()
        assert lattice.bottom.decision == Decision.ANSWER

    def test_lattice_join_with_refuse(self):
        """Test that join with REFUSE always returns REFUSE."""
        lattice = GovernanceLattice()
        for d in Decision:
            assert lattice.join(Decision.REFUSE, d) == Decision.REFUSE
            assert lattice.join(d, Decision.REFUSE) == Decision.REFUSE

    def test_lattice_join_with_answer(self):
        """Test that join with ANSWER returns the other decision."""
        lattice = GovernanceLattice()
        for d in Decision:
            assert lattice.join(Decision.ANSWER, d) == d
            assert lattice.join(d, Decision.ANSWER) == d

    def test_lattice_meet_with_answer(self):
        """Test that meet with ANSWER always returns ANSWER."""
        lattice = GovernanceLattice()
        for d in Decision:
            assert lattice.meet(Decision.ANSWER, d) == Decision.ANSWER
            assert lattice.meet(d, Decision.ANSWER) == Decision.ANSWER

    def test_lattice_governance_join_multiple(self):
        """Test governance_join over multiple decisions."""
        lattice = GovernanceLattice()
        # Any REFUSE in the list → result is REFUSE
        assert lattice.governance_join([Decision.ANSWER, Decision.DEFER, Decision.REFUSE]) == Decision.REFUSE
        # No REFUSE, but DEFER → result is DEFER
        assert lattice.governance_join([Decision.ANSWER, Decision.DEFER]) == Decision.DEFER
        # All ANSWER → result is ANSWER
        assert lattice.governance_join([Decision.ANSWER, Decision.ANSWER]) == Decision.ANSWER

    def test_lattice_escalation(self):
        """Test escalation moves up the lattice."""
        lattice = GovernanceLattice()
        # ANSWER escalates to DEFER
        new_decision, _ = lattice.escalate(Decision.ANSWER)
        assert new_decision == Decision.DEFER
        # DEFER escalates to REFUSE
        new_decision, _ = lattice.escalate(Decision.DEFER)
        assert new_decision == Decision.REFUSE
        # REFUSE stays at REFUSE
        new_decision, _ = lattice.escalate(Decision.REFUSE)
        assert new_decision == Decision.REFUSE

    def test_lattice_safe_transition(self):
        """Test safe transition detection."""
        lattice = GovernanceLattice()
        # Moving up is safe
        assert lattice.is_safe_transition(Decision.ANSWER, Decision.DEFER)
        assert lattice.is_safe_transition(Decision.DEFER, Decision.REFUSE)
        # Staying same is safe
        assert lattice.is_safe_transition(Decision.ANSWER, Decision.ANSWER)
        # Moving down is NOT safe
        assert not lattice.is_safe_transition(Decision.REFUSE, Decision.ANSWER)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPAND/REDUCE MANIFOLD TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestExpandReduceManifold:
    """Tests for the Expand/Reduce Manifold."""

    def test_constraint_point_creation(self):
        """Test ConstraintPoint creation and hashing."""
        c = ConstraintPoint(id="c1", constraint_type="balance", content={"min": 0})
        assert c.id == "c1"
        assert c._hash != ""

    def test_constraint_point_equality(self):
        """Test that equal content → equal hash."""
        c1 = ConstraintPoint(id="c1", constraint_type="balance", content={"min": 0})
        c2 = ConstraintPoint(id="c2", constraint_type="balance", content={"min": 0})
        # Same content, same hash
        assert c1._hash == c2._hash
        assert c1 == c2

    def test_text_point_creation(self):
        """Test TextPoint creation."""
        t = TextPoint(text="balance must be >= 0")
        assert t.text == "balance must be >= 0"
        assert t.style == "formal"

    def test_fiber_bundle_basic(self):
        """Test basic fiber bundle operations."""
        bundle = FiberBundle()
        c = ConstraintPoint(id="c1", constraint_type="balance", content={"min": 0})
        fiber = bundle.add_fiber(c)
        assert bundle.get_fiber(c) is fiber

    def test_manifold_register_constraint(self):
        """Test registering a constraint in the manifold."""
        manifold = ExpandReduceManifold()
        c = ConstraintPoint(id="c1", constraint_type="balance", content={"min": 0})
        fiber = manifold.register_constraint(c)
        assert fiber is not None
        assert fiber.base_point == c

    def test_manifold_register_text(self):
        """Test registering text for a constraint."""
        manifold = ExpandReduceManifold()
        c = ConstraintPoint(id="c1", constraint_type="balance", content={"min": 0})
        t = TextPoint(text="balance must be >= 0")

        manifold.register_constraint(c)
        result = manifold.register_text(t, c)
        assert result is True

        texts = manifold.get_equivalent_texts(c)
        assert t in texts


# ═══════════════════════════════════════════════════════════════════════════════
# COMPUTATION GRAPH TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestComputationGraph:
    """Tests for the Computation Graph."""

    def test_graph_deterministic(self):
        """Test that the graph is deterministic."""
        graph = ComputationGraph()
        assert graph.is_deterministic()

    def test_graph_complete(self):
        """Test that all request types have paths."""
        graph = ComputationGraph()
        assert graph.is_complete()

    def test_graph_harmful_to_refuse(self):
        """Test that HARMFUL → REFUSE."""
        graph = ComputationGraph()
        result = graph.classify_and_route(RequestType.HARMFUL)
        assert result.decision == Decision.REFUSE

    def test_graph_question_to_answer(self):
        """Test that QUESTION → ANSWER."""
        graph = ComputationGraph()
        result = graph.classify_and_route(RequestType.QUESTION)
        assert result.decision == Decision.ANSWER

    def test_graph_medical_to_defer(self):
        """Test that MEDICAL_ADVICE → DEFER."""
        graph = ComputationGraph()
        result = graph.classify_and_route(RequestType.MEDICAL_ADVICE)
        assert result.decision == Decision.DEFER

    def test_graph_unknown_to_ask(self):
        """Test that UNKNOWN → ASK."""
        graph = ComputationGraph()
        result = graph.classify_and_route(RequestType.UNKNOWN)
        assert result.decision == Decision.ASK

    def test_graph_path_not_empty(self):
        """Test that paths are not empty."""
        graph = ComputationGraph()
        for req_type in RequestType:
            result = graph.classify_and_route(req_type)
            assert len(result.path) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE HYPERGRAPH TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestModuleHypergraph:
    """Tests for the Module Hypergraph."""

    def test_hypergraph_has_all_modules(self):
        """Test that hypergraph contains all Newton modules."""
        h = ModuleHypergraph()
        for module in NewtonModule:
            assert module in h.modules

    def test_hypergraph_connected(self):
        """Test that hypergraph is connected."""
        h = ModuleHypergraph()
        assert h.is_connected()

    def test_hypergraph_cdl_central(self):
        """Test that CDL has multiple connections (central node)."""
        h = ModuleHypergraph()
        incoming = h.get_channels_to(NewtonModule.CDL)
        outgoing = h.get_channels_from(NewtonModule.CDL)
        assert len(incoming) > 0
        assert len(outgoing) > 0

    def test_hypergraph_path_exists(self):
        """Test path finding between modules."""
        h = ModuleHypergraph()
        exists, path = h.path_exists(NewtonModule.GLASS_BOX, NewtonModule.LEDGER)
        assert exists
        assert len(path) > 0

    def test_hypergraph_layers(self):
        """Test layer classification."""
        h = ModuleHypergraph()
        policy = h.get_layer_modules("policy")
        assert NewtonModule.GLASS_BOX in policy

        execution = h.get_layer_modules("execution")
        assert NewtonModule.FORGE in execution
        assert NewtonModule.TEXTGEN in execution


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETE TOPOLOGY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestNewtonTopology:
    """Tests for the complete Newton Topology."""

    def test_topology_creation(self):
        """Test topology creation with all components."""
        t = NewtonTopology()
        assert t.polytope is not None
        assert t.simplex is not None
        assert t.lattice is not None
        assert t.manifold is not None
        assert t.graph is not None
        assert t.hypergraph is not None

    def test_topology_newton_law_true(self):
        """Test Newton's law: 1 == 1 → True."""
        t = NewtonTopology()
        assert t.newton_law(1, 1) is True
        assert t.newton_law("test", "test") is True
        assert t.newton_law([1, 2], [1, 2]) is True

    def test_topology_newton_law_false(self):
        """Test Newton's law: 1 != 1 → False."""
        t = NewtonTopology()
        assert t.newton_law(1, 2) is False
        assert t.newton_law("a", "b") is False

    def test_topology_region_inside(self):
        """Test region detection inside shape."""
        t = NewtonTopology()
        region = t.region_at_point(f=0.5, g=1.0)
        assert region == TopologyRegion.POSSIBLE

    def test_topology_region_boundary(self):
        """Test region detection at boundary."""
        t = NewtonTopology()
        region = t.region_at_point(f=1.0, g=1.0)
        assert region == TopologyRegion.BOUNDARY

    def test_topology_region_outside(self):
        """Test region detection outside shape."""
        t = NewtonTopology()
        region = t.region_at_point(f=1.5, g=1.0)
        assert region == TopologyRegion.IMPOSSIBLE

    def test_topology_locate_feasible(self):
        """Test locating a feasible point."""
        t = NewtonTopology()
        state = t.locate(
            constraints=[{"name": "c1", "f": 0.5, "g": 1.0}],
            risk_score=0.1,
            clarity_score=0.9,
            capability_score=0.9,
            request_type=RequestType.QUESTION,
        )
        assert state.can_execute is True
        assert state.decision == Decision.ANSWER

    def test_topology_locate_infeasible(self):
        """Test locating an infeasible point."""
        t = NewtonTopology()
        state = t.locate(
            constraints=[{"name": "c1", "f": 1.5, "g": 1.0}],  # Violated
            risk_score=0.1,
            clarity_score=0.9,
            capability_score=0.9,
            request_type=RequestType.QUESTION,
        )
        assert state.can_execute is False
        assert state.decision == Decision.REFUSE  # Escalated due to infeasibility

    def test_topology_execute(self):
        """Test full execution through topology."""
        t = NewtonTopology()
        can_execute, decision, state = t.execute(
            constraints=[{"name": "c1", "f": 0.5, "g": 1.0}],
            request_type=RequestType.QUESTION,
        )
        assert can_execute is True
        assert decision == Decision.ANSWER

    def test_topology_combine_decisions(self):
        """Test combining decisions uses lattice join."""
        t = NewtonTopology()
        combined = t.combine_decisions([Decision.ANSWER, Decision.DEFER])
        assert combined == Decision.DEFER

    def test_topology_is_inside_shape(self):
        """Test multi-dimensional shape containment."""
        t = NewtonTopology()
        point = {
            "dim1": (0.5, 1.0),
            "dim2": (0.3, 1.0),
        }
        assert t.is_inside_shape(point) is True

        point_outside = {
            "dim1": (0.5, 1.0),
            "dim2": (1.5, 1.0),  # Outside
        }
        assert t.is_inside_shape(point_outside) is False


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """Integration tests for the complete geometry system."""

    def test_full_pipeline_safe_request(self):
        """Test a safe request flows through the entire system."""
        topology = NewtonTopology()

        # A simple question with all constraints satisfied
        can_execute, decision, state = topology.execute(
            constraints=[
                {"name": "risk", "f": 0.2, "g": 1.0},
                {"name": "clarity", "f": 0.1, "g": 1.0},
            ],
            request_type=RequestType.QUESTION,
            risk_score=0.1,
            clarity_score=0.9,
            capability_score=0.9,
        )

        assert can_execute is True
        assert decision == Decision.ANSWER
        assert state["polytope"]["region"] == "FIN"
        assert state["graph"]["valid"] is True

    def test_full_pipeline_harmful_request(self):
        """Test a harmful request is rejected."""
        topology = NewtonTopology()

        can_execute, decision, state = topology.execute(
            constraints=[{"name": "safety", "f": 0.1, "g": 1.0}],
            request_type=RequestType.HARMFUL,
            risk_score=0.95,
        )

        assert can_execute is False
        assert decision == Decision.REFUSE

    def test_monotonicity_through_system(self):
        """Test that safety monotonicity is preserved."""
        topology = NewtonTopology()

        # Start with ANSWER
        d1 = Decision.ANSWER

        # Add constraint violation → escalate
        d2 = topology.escalate_decision(d1, "constraint violated")
        assert d2 in (Decision.DEFER, Decision.ASK, Decision.REFUSE)

        # Combine with another decision
        d3 = topology.combine_decisions([d2, Decision.DEFER])
        # Should be at least as safe as d2
        lattice = topology.lattice
        assert lattice.compare(d2, d3) <= 0

    def test_geometry_is_computation(self):
        """
        The fundamental test: the geometry IS the computation.

        We don't check constraints then compute.
        The constraint satisfaction IS the computation.
        """
        topology = NewtonTopology()

        # Inside the shape → computation exists
        inside = topology.is_inside_shape({
            "effort": (0.8, 1.0),
            "resources": (0.5, 1.0),
        })
        assert inside is True

        # Outside the shape → computation doesn't exist
        outside = topology.is_inside_shape({
            "effort": (1.5, 1.0),  # f/g > 1
            "resources": (0.5, 1.0),
        })
        assert outside is False

        # The shape IS the computer
        # There's nothing more to check


# ═══════════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
