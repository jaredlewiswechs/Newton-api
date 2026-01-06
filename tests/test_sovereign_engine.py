#!/usr/bin/env python3
"""
===============================================================================
 SOVEREIGN ENGINE TEST SUITE
===============================================================================

Comprehensive tests for the SovereignEngine constraint enforcement system.

Tests cover:
1. project_future() state projection
2. Boundary definition and enforcement
3. f/g ratio calculation and thresholds
4. Presence mutual exclusion
5. Rollback mechanics
6. Audit trail and proofs
7. Integration with Newton's existing systems

Run with: pytest tests/test_sovereign_engine.py -v
"""

import pytest
import time
from typing import Dict, Any

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from tinytalk_py import (
    Blueprint, field, law, forge, when, finfr,
    LawViolation, Presence, Delta
)
from tinytalk_py.sovereign import (
    SovereignEngine,
    Intent,
    AuditResult,
    Boundary,
    BoundaryType,
    BoundaryRegistry,
    PresenceState,
    PresenceManager,
    project_future,
    calculate_fg_ratio,
    create_sovereign_engine
)
from tinytalk_py.core import ratio


# =============================================================================
# PART 1: PROJECT_FUTURE TESTS
# =============================================================================

class TestProjectFuture:
    """Test the project_future() state projection function."""

    def test_project_future_set_action(self):
        """Test direct value assignment."""
        state = {'balance': 1000, 'name': 'test'}
        intent = Intent('set', {'balance': 500})

        future = project_future(state, intent)

        assert future.state['balance'] == 500
        assert future.state['name'] == 'test'  # Unchanged

    def test_project_future_add_action(self):
        """Test addition operation."""
        state = {'balance': 1000}
        intent = Intent('add', {'balance': 200})

        future = project_future(state, intent)

        assert future.state['balance'] == 1200

    def test_project_future_subtract_action(self):
        """Test subtraction operation."""
        state = {'balance': 1000}
        intent = Intent('withdraw', {'balance': 300})

        future = project_future(state, intent)

        assert future.state['balance'] == 700

    def test_project_future_multiply_action(self):
        """Test multiplication operation."""
        state = {'value': 100}
        intent = Intent('scale', {'value': 2.5})

        future = project_future(state, intent)

        assert future.state['value'] == 250

    def test_project_future_move_action(self):
        """Test delta-based movement."""
        state = {'x': 100, 'y': 50}
        intent = Intent('move', {'x': 10, 'y': -5})

        future = project_future(state, intent)

        assert future.state['x'] == 110
        assert future.state['y'] == 45

    def test_project_future_with_constraints(self):
        """Test projection with output constraints."""
        state = {'balance': 100}
        intent = Intent(
            'withdraw',
            {'balance': 150},  # Would go negative
            constraints={'balance': {'min': 0}}  # But constrained to >= 0
        )

        future = project_future(state, intent)

        assert future.state['balance'] == 0  # Clamped to min

    def test_project_future_with_max_constraint(self):
        """Test projection with max constraint."""
        state = {'value': 90}
        intent = Intent(
            'add',
            {'value': 50},
            constraints={'value': {'max': 100}}
        )

        future = project_future(state, intent)

        assert future.state['value'] == 100  # Clamped to max

    def test_project_future_custom_projector(self):
        """Test custom projection function."""
        def custom_transfer(state, params):
            state = state.copy()
            state['from_account'] -= params['amount']
            state['to_account'] += params['amount']
            return state

        state = {'from_account': 1000, 'to_account': 500}
        intent = Intent('transfer', {'amount': 200})

        future = project_future(state, intent, {'transfer': custom_transfer})

        assert future.state['from_account'] == 800
        assert future.state['to_account'] == 700

    def test_project_future_creates_presence(self):
        """Test that projection returns a Presence object."""
        state = {'x': 0}
        intent = Intent('set', {'x': 100})

        future = project_future(state, intent)

        assert isinstance(future, Presence)
        assert future.timestamp is not None
        assert 'projected' in future.label


# =============================================================================
# PART 2: BOUNDARY TESTS
# =============================================================================

class TestBoundarySystem:
    """Test the boundary definition and enforcement system."""

    def test_boundary_creation(self):
        """Test creating a boundary."""
        boundary = Boundary(
            name='max_value',
            type_=BoundaryType.LOGICAL,
            check=lambda d, e: d.changes.get('x', {}).get('to', 0) > 100,
            message='Value exceeds maximum'
        )

        assert boundary.name == 'max_value'
        assert boundary.type_ == BoundaryType.LOGICAL

    def test_boundary_evaluation_not_violated(self):
        """Test boundary that is not violated."""
        boundary = Boundary(
            name='max_value',
            type_=BoundaryType.LOGICAL,
            check=lambda d, e: d.changes.get('x', {}).get('to', 0) > 100
        )

        delta = Delta({'x': {'from': 0, 'to': 50, 'delta': 50}})
        violated, msg = boundary.evaluate(delta, None)

        assert not violated
        assert msg == ""

    def test_boundary_evaluation_violated(self):
        """Test boundary that is violated."""
        boundary = Boundary(
            name='max_value',
            type_=BoundaryType.LOGICAL,
            check=lambda d, e: d.changes.get('x', {}).get('to', 0) > 100,
            message='Value exceeds maximum'
        )

        delta = Delta({'x': {'from': 0, 'to': 150, 'delta': 150}})
        violated, msg = boundary.evaluate(delta, None)

        assert violated
        assert 'Value exceeds maximum' in msg

    def test_boundary_registry(self):
        """Test boundary registry operations."""
        registry = BoundaryRegistry()

        registry.register(
            'no_negative',
            lambda d, e: d.changes.get('balance', {}).get('to', 0) < 0,
            BoundaryType.LOGICAL,
            'Balance cannot be negative'
        )

        registry.register(
            'max_velocity',
            lambda d, e: d.changes.get('velocity', {}).get('to', 0) > 100,
            BoundaryType.PHYSICAL,
            'Velocity limit exceeded'
        )

        # Test valid delta
        delta = Delta({
            'balance': {'from': 100, 'to': 50, 'delta': -50},
            'velocity': {'from': 0, 'to': 50, 'delta': 50}
        })
        violations = registry.evaluate_all(delta, None)
        assert len(violations) == 0

        # Test invalid delta
        delta = Delta({
            'balance': {'from': 100, 'to': -50, 'delta': -150}
        })
        violations = registry.evaluate_all(delta, None)
        assert len(violations) == 1
        assert violations[0][0].name == 'no_negative'

    def test_boundary_registry_clear(self):
        """Test clearing boundaries."""
        registry = BoundaryRegistry()
        registry.register('test', lambda d, e: False)

        registry.clear()

        delta = Delta({})
        violations = registry.evaluate_all(delta, None)
        assert len(violations) == 0

    def test_boundary_types(self):
        """Test all boundary types exist."""
        assert BoundaryType.PHYSICAL
        assert BoundaryType.LOGICAL
        assert BoundaryType.TEMPORAL
        assert BoundaryType.ONTOLOGICAL


# =============================================================================
# PART 3: F/G RATIO TESTS
# =============================================================================

class TestFGRatio:
    """Test f/g ratio calculation for dimensional analysis."""

    def test_fg_ratio_simple(self):
        """Test simple f/g ratio calculation."""
        delta = Delta({'balance': {'from': 1000, 'to': 200, 'delta': -800}})
        constraints = {'balance': 1000}

        fg = calculate_fg_ratio(delta, constraints)

        assert fg.value == 0.8
        assert fg <= 1.0
        assert not fg > 1.0

    def test_fg_ratio_exceeds_threshold(self):
        """Test f/g ratio that exceeds threshold."""
        delta = Delta({'balance': {'from': 100, 'to': -50, 'delta': -150}})
        constraints = {'balance': 100}

        fg = calculate_fg_ratio(delta, constraints)

        assert fg.value == 1.5
        assert fg > 1.0
        assert fg >= 1.0

    def test_fg_ratio_multiple_fields(self):
        """Test f/g ratio with multiple constrained fields."""
        delta = Delta({
            'account_a': {'from': 1000, 'to': 800, 'delta': -200},
            'account_b': {'from': 500, 'to': 600, 'delta': 100}
        })
        constraints = {'account_a': 1000, 'account_b': 500}

        fg = calculate_fg_ratio(delta, constraints)

        # f = |200| + |100| = 300
        # g = 1000 + 500 = 1500
        assert fg.value == pytest.approx(0.2, rel=0.01)

    def test_fg_ratio_no_constraints(self):
        """Test f/g ratio with no ground constraints."""
        delta = Delta({'x': {'from': 0, 'to': 1000, 'delta': 1000}})
        constraints = {}

        fg = calculate_fg_ratio(delta, constraints)

        assert fg <= 1.0  # Should pass when no constraints

    def test_fg_ratio_with_core_ratio(self):
        """Test integration with core ratio() function."""
        r = ratio(800, 1000)

        assert r.value == 0.8
        assert r < 1.0
        assert not r >= 1.0

    def test_fg_ratio_undefined(self):
        """Test undefined ratio (zero denominator)."""
        r = ratio(100, 0)

        assert r.undefined
        assert r > 1.0  # Undefined always exceeds threshold


# =============================================================================
# PART 4: PRESENCE MANAGEMENT TESTS
# =============================================================================

class TestPresenceManagement:
    """Test presence state and mutual exclusion."""

    def test_presence_registration(self):
        """Test registering presence states."""
        manager = PresenceManager()

        manager.register('locked', exclusive_with=['unlocked'])
        manager.register('unlocked', exclusive_with=['locked'])

        assert manager.is_active('locked') == False
        assert manager.is_active('unlocked') == False

    def test_presence_activation(self):
        """Test activating presence states."""
        manager = PresenceManager()
        manager.register('active')

        success, error = manager.activate('active')

        assert success
        assert error is None
        assert manager.is_active('active')

    def test_presence_conflict_detection(self):
        """Test mutual exclusion conflict detection."""
        manager = PresenceManager()
        manager.register('state_a', exclusive_with=['state_b'])
        manager.register('state_b', exclusive_with=['state_a'])

        # Activate first state
        manager.activate('state_a')
        assert manager.is_active('state_a')

        # Try to activate conflicting state
        success, error = manager.activate('state_b')

        assert not success
        assert 'state_a' in error

    def test_presence_deactivation(self):
        """Test deactivating presence states."""
        manager = PresenceManager()
        manager.register('active', exclusive_with=['inactive'])
        manager.register('inactive', exclusive_with=['active'])

        manager.activate('active')
        manager.deactivate('active')

        # Now can activate the other
        success, _ = manager.activate('inactive')
        assert success

    def test_presence_check_conflicts(self):
        """Test bulk conflict checking."""
        manager = PresenceManager()
        manager.register('a', exclusive_with=['b'])
        manager.register('b', exclusive_with=['a'])

        # Force both active (bypassing normal activation)
        manager._presences['a'].active = True
        manager._presences['b'].active = True

        conflicts = manager.check_conflicts()

        assert len(conflicts) == 1
        assert set(conflicts[0]) == {'a', 'b'}


# =============================================================================
# PART 5: SOVEREIGN ENGINE TESTS
# =============================================================================

class TestSovereignEngine:
    """Test the complete SovereignEngine."""

    def test_engine_creation(self):
        """Test creating a SovereignEngine."""
        engine = SovereignEngine()

        assert engine is not None
        assert engine.boundaries is not None
        assert engine.presences is not None

    def test_engine_with_ground_constraints(self):
        """Test engine with ground constraints."""
        engine = SovereignEngine()
        engine.set_ground_constraints({'balance': 1000})

        assert engine._ground_constraints['balance'] == 1000

    def test_engine_register_boundary(self):
        """Test registering boundaries on engine."""
        engine = SovereignEngine()

        engine.boundaries.register(
            'no_overdraft',
            lambda d, e: d.changes.get('balance', {}).get('to', 0) < 0,
            BoundaryType.LOGICAL
        )

        # Boundary is registered
        assert len(engine.boundaries._boundaries[BoundaryType.LOGICAL]) > 0

    def test_engine_execute_valid_intent(self):
        """Test executing a valid intent."""
        engine = create_sovereign_engine(
            ground_constraints={'balance': 1000}
        )

        # Set initial state via field
        engine._field_balance = 1000

        # Add balance field to track
        class BalanceEngine(SovereignEngine):
            balance = field(float, default=1000.0)

        be = BalanceEngine()
        be.set_ground_constraints({'balance': 1000})

        result = be.execute_intent(Intent('withdraw', {'balance': 200}))

        assert result['status'] == 'MOTION_SYNCHRONIZED'
        assert 'proof' in result

    def test_engine_blocks_boundary_violation(self):
        """Test that engine blocks boundary violations."""
        class BalanceEngine(SovereignEngine):
            balance = field(float, default=1000.0)

        engine = BalanceEngine()
        engine.boundaries.register(
            'no_overdraft',
            lambda d, e: d.changes.get('balance', {}).get('to', 0) < 0,
            BoundaryType.LOGICAL
        )

        # Try to overdraft
        with pytest.raises(LawViolation) as exc_info:
            engine.execute_intent(Intent('withdraw', {'balance': 1500}))

        assert 'sovereign_audit' in str(exc_info.value) or 'Audit failed' in str(exc_info.value)
        # Balance should be rolled back
        assert engine.balance == 1000.0

    def test_engine_fg_threshold_enforcement(self):
        """Test f/g threshold enforcement."""
        class BalanceEngine(SovereignEngine):
            balance = field(float, default=1000.0)

        engine = BalanceEngine(fg_threshold=0.5)  # 50% max change
        engine.set_ground_constraints({'balance': 1000})

        # Try to withdraw 60% (exceeds threshold)
        with pytest.raises(LawViolation):
            engine.execute_intent(Intent('withdraw', {'balance': 600}))

        # 40% should work
        result = engine.execute_intent(Intent('withdraw', {'balance': 400}))
        assert result['status'] == 'MOTION_SYNCHRONIZED'

    def test_engine_presence_conflict_law(self):
        """Test ontological integrity law."""
        engine = SovereignEngine()

        engine.define_presence('locked', exclusive_with=['unlocked'])
        engine.define_presence('unlocked', exclusive_with=['locked'])

        # Activate both (directly, bypassing activation check)
        engine.presences._presences['locked'].active = True
        engine.presences._presences['unlocked'].active = True

        # Check conflicts exist
        conflicts = engine.presences.check_conflicts()
        assert len(conflicts) > 0

    def test_engine_audit_log(self):
        """Test audit trail generation."""
        class BalanceEngine(SovereignEngine):
            balance = field(float, default=1000.0)

        engine = BalanceEngine()

        engine.execute_intent(Intent('withdraw', {'balance': 100}))
        engine.execute_intent(Intent('add', {'balance': 50}))

        log = engine.get_audit_log()

        assert len(log) == 2
        assert all(isinstance(entry, AuditResult) for entry in log)
        assert all(entry.passed for entry in log)

    def test_engine_export_proof(self):
        """Test cryptographic proof export."""
        class BalanceEngine(SovereignEngine):
            balance = field(float, default=1000.0)

        engine = BalanceEngine()

        engine.execute_intent(Intent('withdraw', {'balance': 100}))

        audit = engine.get_audit_log()[0]
        proof = engine.export_proof(audit)

        assert 'audit_hash' in proof
        assert 'passed' in proof
        assert 'timestamp' in proof
        assert 'delta_hash' in proof
        assert len(proof['audit_hash']) == 16

    def test_engine_rollback_on_violation(self):
        """Test that state is rolled back on law violation."""
        class MultiFieldEngine(SovereignEngine):
            a = field(float, default=100.0)
            b = field(float, default=200.0)

        engine = MultiFieldEngine()
        engine.boundaries.register(
            'sum_limit',
            lambda d, e: (
                d.changes.get('a', {}).get('to', e.a) +
                d.changes.get('b', {}).get('to', e.b)
            ) > 400,
            BoundaryType.LOGICAL
        )

        initial_a = engine.a
        initial_b = engine.b

        with pytest.raises(LawViolation):
            engine.execute_intent(Intent('set', {'a': 300, 'b': 300}))

        # Both should be rolled back
        assert engine.a == initial_a
        assert engine.b == initial_b


# =============================================================================
# PART 6: FACTORY FUNCTION TESTS
# =============================================================================

class TestFactoryFunction:
    """Test create_sovereign_engine factory."""

    def test_factory_basic(self):
        """Test basic factory usage."""
        engine = create_sovereign_engine()

        assert isinstance(engine, SovereignEngine)

    def test_factory_with_constraints(self):
        """Test factory with ground constraints."""
        engine = create_sovereign_engine(
            ground_constraints={'balance': 1000, 'credit': 500}
        )

        assert engine._ground_constraints['balance'] == 1000
        assert engine._ground_constraints['credit'] == 500

    def test_factory_with_threshold(self):
        """Test factory with custom threshold."""
        engine = create_sovereign_engine(fg_threshold=0.75)

        assert engine.fg_threshold == 0.75

    def test_factory_with_boundaries(self):
        """Test factory with pre-defined boundaries."""
        engine = create_sovereign_engine(
            boundaries=[
                {
                    'name': 'test_boundary',
                    'check': lambda d, e: False,
                    'type': BoundaryType.LOGICAL,
                    'message': 'Test'
                }
            ]
        )

        assert len(engine.boundaries._boundaries[BoundaryType.LOGICAL]) > 0

    def test_factory_with_presences(self):
        """Test factory with pre-defined presences."""
        engine = create_sovereign_engine(
            presences=[
                {'name': 'state_a', 'exclusive_with': ['state_b']},
                {'name': 'state_b', 'exclusive_with': ['state_a']}
            ]
        )

        assert 'state_a' in engine.presences._presences
        assert 'state_b' in engine.presences._presences


# =============================================================================
# PART 7: INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests with Newton's existing systems."""

    def test_integration_with_presence_delta(self):
        """Test that SovereignEngine uses Presence and Delta correctly."""
        class PositionEngine(SovereignEngine):
            x = field(float, default=0.0)
            y = field(float, default=0.0)

        engine = PositionEngine()

        result = engine.execute_intent(Intent('move', {'x': 50, 'y': 25}))

        assert engine.presence_start is not None
        assert engine.presence_end is not None
        assert engine.kinetic_delta is not None

        assert engine.kinetic_delta.changes['x']['delta'] == 50
        assert engine.kinetic_delta.changes['y']['delta'] == 25

    def test_tandem_pair_return_format(self):
        """Test that execute_intent returns (value, proof) tandem pair."""
        class SimpleEngine(SovereignEngine):
            value = field(float, default=100.0)

        engine = SimpleEngine()
        result = engine.execute_intent(Intent('set', {'value': 200}))

        # Should have both value and proof
        assert 'value' in result
        assert 'proof' in result

        # Value should be the delta changes
        assert isinstance(result['value'], dict)

        # Proof should have audit info
        assert 'audit_hash' in result['proof']
        assert 'timestamp' in result['proof']

    def test_custom_projector_integration(self):
        """Test custom projector registration and use."""
        class TransferEngine(SovereignEngine):
            account_a = field(float, default=1000.0)
            account_b = field(float, default=500.0)

        engine = TransferEngine()

        def transfer_projector(state: Dict, params: Dict) -> Dict:
            state = state.copy()
            state['account_a'] -= params['amount']
            state['account_b'] += params['amount']
            return state

        engine.register_projector('transfer', transfer_projector)

        result = engine.execute_intent(Intent('transfer', {'amount': 200}))

        assert result['status'] == 'MOTION_SYNCHRONIZED'
        assert engine.account_a == 800.0
        assert engine.account_b == 700.0


# =============================================================================
# PART 8: PERFORMANCE TESTS
# =============================================================================

class TestPerformance:
    """Performance benchmarks for SovereignEngine."""

    def test_intent_execution_speed(self):
        """Benchmark intent execution speed."""
        class FastEngine(SovereignEngine):
            value = field(float, default=1000.0)

        engine = FastEngine()
        engine.set_ground_constraints({'value': 10000})

        iterations = 1000
        start = time.perf_counter()

        for i in range(iterations):
            engine.execute_intent(Intent('add', {'value': 1}))

        elapsed = time.perf_counter() - start
        ops_per_second = iterations / elapsed

        print(f"\nSovereignEngine: {ops_per_second:.0f} intents/sec")

        # Should handle at least 500 intents/second
        assert ops_per_second > 500, f"Too slow: {ops_per_second} ops/sec"

    def test_boundary_evaluation_speed(self):
        """Benchmark boundary evaluation speed."""
        registry = BoundaryRegistry()

        # Add multiple boundaries
        for i in range(10):
            registry.register(
                f'boundary_{i}',
                lambda d, e: False,  # Always passes
                BoundaryType.LOGICAL
            )

        delta = Delta({
            'x': {'from': 0, 'to': 100, 'delta': 100},
            'y': {'from': 0, 'to': 50, 'delta': 50}
        })

        iterations = 10000
        start = time.perf_counter()

        for _ in range(iterations):
            registry.evaluate_all(delta, None)

        elapsed = time.perf_counter() - start
        ops_per_second = iterations / elapsed

        print(f"\nBoundary Evaluation (10 boundaries): {ops_per_second:.0f} ops/sec")

        assert ops_per_second > 5000

    def test_projection_speed(self):
        """Benchmark project_future speed."""
        state = {'a': 100, 'b': 200, 'c': 300, 'd': 400, 'e': 500}
        intent = Intent('add', {'a': 10, 'b': 20, 'c': 30})

        iterations = 10000
        start = time.perf_counter()

        for _ in range(iterations):
            project_future(state, intent)

        elapsed = time.perf_counter() - start
        ops_per_second = iterations / elapsed

        print(f"\nproject_future: {ops_per_second:.0f} projections/sec")

        assert ops_per_second > 10000


# =============================================================================
# PART 9: EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_intent(self):
        """Test intent with no parameters."""
        state = {'x': 100}
        intent = Intent('set', {})

        future = project_future(state, intent)

        assert future.state['x'] == 100  # Unchanged

    def test_unknown_action(self):
        """Test unknown action defaults to set."""
        state = {'x': 100}
        intent = Intent('unknown_action', {'x': 200})

        future = project_future(state, intent)

        assert future.state['x'] == 200  # Treated as set

    def test_boundary_error_handling(self):
        """Test boundary check that raises exception."""
        def bad_check(d, e):
            raise ValueError("Check failed")

        boundary = Boundary(
            name='bad_boundary',
            type_=BoundaryType.LOGICAL,
            check=bad_check
        )

        delta = Delta({})
        violated, msg = boundary.evaluate(delta, None)

        # Errors are treated as violations (fail-safe)
        assert violated
        assert 'failed' in msg.lower()

    def test_audit_result_hash_determinism(self):
        """Test that audit hashes are deterministic."""
        result1 = AuditResult(
            passed=True,
            fg_ratio=0.5,
            violations=[],
            delta=None
        )

        result2 = AuditResult(
            passed=True,
            fg_ratio=0.5,
            violations=[],
            delta=None
        )

        # Same inputs should produce same hash
        assert result1.audit_hash == result2.audit_hash

    def test_presence_unknown_state(self):
        """Test activating unknown presence state."""
        manager = PresenceManager()

        success, error = manager.activate('nonexistent')

        assert not success
        assert 'Unknown' in error


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
