#!/usr/bin/env python3
"""
Newton Geometry - Topological Constraint Framework
===================================================

The computer is a shape.
The shape is the constraint.
The constraint is the truth.
"""

from .polytope import ConstraintPolytope, FeasibilityRegion, Boundary
from .simplex import DecisionSimplex, Decision, RiskLevel
from .lattice import GovernanceLattice, SafetyLevel, LatticeNode
from .manifold import ExpandReduceManifold, FiberBundle, TextPoint, ConstraintPoint
from .graph import ComputationGraph, RequestType, GraphNode, PathResult
from .hypergraph import ModuleHypergraph, NewtonModule, Channel
from .topology import NewtonTopology, TopologyRegion

__all__ = [
    # Polytope
    "ConstraintPolytope",
    "FeasibilityRegion",
    "Boundary",
    # Simplex
    "DecisionSimplex",
    "Decision",
    "RiskLevel",
    # Lattice
    "GovernanceLattice",
    "SafetyLevel",
    "LatticeNode",
    # Manifold
    "ExpandReduceManifold",
    "FiberBundle",
    "TextPoint",
    "ConstraintPoint",
    # Graph
    "ComputationGraph",
    "RequestType",
    "GraphNode",
    "PathResult",
    # Hypergraph
    "ModuleHypergraph",
    "NewtonModule",
    "Channel",
    # Topology
    "NewtonTopology",
    "TopologyRegion",
]

__version__ = "1.0.0"
