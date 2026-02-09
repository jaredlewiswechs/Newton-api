"""
Newton Core - Verified Computation Engine
==========================================
Central package that re-exports all symbols needed by newton_supercomputer.py
and other consumers. Each submodule can also be imported directly.
"""

# ─── CDL (Constraint Definition Language) ─────────────────────────────────────
from .cdl import (
    CDLEvaluator, CDLParser,
    verify, verify_and, verify_or, newton,
)

# Convenience alias used by some workspace scripts
CDL = CDLEvaluator

# ─── Forge (Parallel Verification Engine) ─────────────────────────────────────
from .forge import Forge, ForgeConfig, get_forge

# Alias for legacy callers
VerificationEngine = Forge

# ─── Vault (AES-256-GCM Encrypted Storage) ────────────────────────────────────
from .vault import Vault, VaultConfig, get_vault

EncryptedStorage = Vault

# ─── Ledger (Hash-Chained Immutable Record) ───────────────────────────────────
from .ledger import Ledger, LedgerConfig, get_ledger

ImmutableLedger = Ledger

# ─── Bridge (Distributed Protocol & Consensus) ────────────────────────────────
from .bridge import LocalBridge, NodeIdentity

DistributedProtocol = LocalBridge

# ─── Robust (Adversarial Statistics) ──────────────────────────────────────────
from .robust import RobustVerifier, RobustConfig, mad, modified_zscore

AdversarialStatistics = RobustVerifier

# ─── Grounding (Evidence-Based Claim Verification) ────────────────────────────
from .grounding import GroundingEngine

# ─── Logic (Verified Turing-Complete Computation) ─────────────────────────────
from .logic import LogicEngine, ExecutionBounds, calculate

# ─── Glass Box Components ─────────────────────────────────────────────────────
from .vault_client import get_vault_client
from .policy_engine import PolicyEngine, Policy, PolicyType, PolicyAction, get_policy_engine
from .negotiator import Negotiator, ApprovalStatus, RequestPriority, get_negotiator
from .merkle_anchor import MerkleAnchorScheduler

# ─── Cartridges (Media Specification Generation) ──────────────────────────────
from .cartridges import CartridgeType, get_cartridge_manager

# ─── Gumroad (Payment & License Management) ───────────────────────────────────
from .gumroad import GumroadConfig, get_gumroad_service

# ─── Voice Interface (MOAD - Mother Of All Demos) ─────────────────────────────
# Imported via core.voice_interface directly by newton_supercomputer.py

# ─── Constraint Extraction ────────────────────────────────────────────────────
# Imported via core.constraint_extractor directly by newton_supercomputer.py

# ─── Chatbot Compiler ────────────────────────────────────────────────────────
# Imported via core.chatbot_compiler directly by newton_supercomputer.py


__all__ = [
    # CDL
    "CDL", "CDLEvaluator", "CDLParser",
    "verify", "verify_and", "verify_or", "newton",
    # Forge
    "Forge", "ForgeConfig", "get_forge", "VerificationEngine",
    # Vault
    "Vault", "VaultConfig", "get_vault", "EncryptedStorage",
    # Ledger
    "Ledger", "LedgerConfig", "get_ledger", "ImmutableLedger",
    # Bridge
    "LocalBridge", "NodeIdentity", "DistributedProtocol",
    # Robust
    "RobustVerifier", "RobustConfig", "mad", "modified_zscore", "AdversarialStatistics",
    # Grounding
    "GroundingEngine",
    # Logic
    "LogicEngine", "ExecutionBounds", "calculate",
    # Glass Box
    "get_vault_client", "PolicyEngine", "Policy", "PolicyType", "PolicyAction", "get_policy_engine",
    "Negotiator", "ApprovalStatus", "RequestPriority", "get_negotiator",
    "MerkleAnchorScheduler",
    # Cartridges
    "CartridgeType", "get_cartridge_manager",
    # Gumroad
    "GumroadConfig", "get_gumroad_service",
]

__version__ = "1.0.0"
