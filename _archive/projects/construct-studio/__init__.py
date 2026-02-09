"""
Construct Studio v0.1
=====================

A Constraint-First Execution Environment.

Programs don't "fail" — they never exist if they violate invariants.
This is not a rule engine. It's geometric validation of intent.

Core Concepts:
- Matter: Typed values with units (the "solids" in your design space)
- Floor: Containers that define constraint boundaries
- Force (>>): Operations that attempt to move Matter
- Ratio: The collision test - does this fit?
- Ledger: Immutable audit trail of all attempts and outcomes
- ConstructError: Ontological death - the illegal state never existed

Usage:
    from construct_studio import Matter, Floor, Construct, Ledger

    class Budget(Floor):
        limit = Matter(5000, "USD")

    @Construct(floor=Budget)
    def spend(amount):
        cost = Matter(amount, "USD")
        cost >> Budget.limit
        return "Approved"

The constraint IS the instruction.
"""

__version__ = "0.1.0"
__author__ = "Newton"

from .core import (
    Matter,
    Floor,
    Force,
    Ratio,
    Construct,
    ConstructError,
    OntologicalDeath,
    attempt,
)

from .ledger import Ledger, LedgerEntry, global_ledger

from .cartridges import (
    CorporateCard,
    DeploymentQuota,
    RiskBudget,
)

from .engine import ConstructEngine, SimulationResult

__all__ = [
    # Core primitives
    "Matter",
    "Floor",
    "Force",
    "Ratio",
    "Construct",
    "ConstructError",
    "OntologicalDeath",
    "attempt",
    # Ledger
    "Ledger",
    "LedgerEntry",
    "global_ledger",
    # Cartridges
    "CorporateCard",
    "DeploymentQuota",
    "RiskBudget",
    # Engine
    "ConstructEngine",
    "SimulationResult",
]
