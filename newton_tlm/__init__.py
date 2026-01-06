#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TLM - Topological Language Machine
A deterministic symbolic language kernel for verified computation.
═══════════════════════════════════════════════════════════════════════════════
"""

from .atom import Atom
from .transaction import Transaction
from .ledger_entry import LedgerEntry
from .phases import Phase, PhaseMachine
from .invariant import canonical_hash, one_equals_one, GoalRegistry
from .reversibility import InverseOperation, Snapshot, SnapshotManager, compute_inverse
from .paradox import ParadoxDetector, ParadoxError, ParadoxResult
from .tlm import NewtonTLM

__version__ = "1.0.0"

__all__ = [
    # Core classes
    "NewtonTLM",
    "Atom",
    "Transaction",
    "LedgerEntry",

    # Phase system
    "Phase",
    "PhaseMachine",

    # Invariant checking
    "canonical_hash",
    "one_equals_one",
    "GoalRegistry",

    # Reversibility
    "InverseOperation",
    "Snapshot",
    "SnapshotManager",
    "compute_inverse",

    # Paradox detection
    "ParadoxDetector",
    "ParadoxError",
    "ParadoxResult",
]
