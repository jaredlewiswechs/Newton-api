"""
Newton Core - Server-side verification engine components.

This module contains the core verification infrastructure:
- CDL (Constraint Definition Language) parser
- Forge (verification CPU)
- Vault (encrypted storage)
- Ledger (immutable audit trail)
- Bridge (distributed protocol)
- Logic (verified computation engine)

Install with: pip install newton-computer[server]
"""

# These imports are optional - they require server dependencies
try:
    import sys
    import os

    # Add project root to find core module
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    core_dir = os.path.join(project_root, "core")

    if core_dir not in sys.path:
        sys.path.insert(0, project_root)

    from core.cdl import CDLParser, CDLConstraint
    from core.forge import Forge, ForgeResult, verify, verify_and, verify_or
    from core.vault import Vault, VaultEntry
    from core.ledger import Ledger, LedgerEntry
    from core.logic import LogicEngine, ExecutionResult, ExecutionBounds
    from core.robust import RobustVerifier, mad
    from core.bridge import LocalBridge, NodeIdentity
    from core.shell import ReversibleShell

    __all__ = [
        # CDL
        "CDLParser",
        "CDLConstraint",
        # Forge
        "Forge",
        "ForgeResult",
        "verify",
        "verify_and",
        "verify_or",
        # Vault
        "Vault",
        "VaultEntry",
        # Ledger
        "Ledger",
        "LedgerEntry",
        # Logic
        "LogicEngine",
        "ExecutionResult",
        "ExecutionBounds",
        # Robust
        "RobustVerifier",
        "mad",
        # Bridge
        "LocalBridge",
        "NodeIdentity",
        # Shell
        "ReversibleShell",
    ]

except ImportError:
    # Core modules not available
    __all__ = []
