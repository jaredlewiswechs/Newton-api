"""
PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
NEWTON SUPERCOMPUTER CORE
PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

The Newton Supercomputer is a distributed verification system where:
- The constraint IS the instruction
- The verification IS the computation
- The network IS the processor

Components:
- CDL: Constraint Definition Language (the instruction set)
- Forge: Verification Engine (the CPU)
- Vault: Encrypted Storage (the RAM)
- Ledger: Immutable History (the disk)
- Bridge: Distributed Protocol (the bus)
- Robust: Adversarial-Resistant Statistics

1 == 1. The cloud is weather. We're building shelter.
"""

from .cdl import (
    # Core classes
    CDLEvaluator,
    CDLParser,
    HaltChecker,

    # Constraint types
    AtomicConstraint,
    CompositeConstraint,
    ConditionalConstraint,
    Constraint,

    # Enums
    Domain,
    Operator,

    # Results
    EvaluationResult,

    # Convenience functions
    verify,
    verify_all,
    verify_and,
    verify_or,
    newton,

    # State
    AggregationState,
)

from .forge import (
    Forge,
    ForgeConfig,
    ForgeMetrics,
    VerificationResult,
    get_forge,
    verify_content,
    verify_signal,
    verify_full,
    SAFETY_PATTERNS,
)

from .vault import (
    Vault,
    VaultConfig,
    VaultEntry,
    KeyDerivation,
    EncryptionEngine,
    get_vault,
)

from .ledger import (
    Ledger,
    LedgerConfig,
    LedgerEntry,
    MerkleTree,
    get_ledger,
)

from .bridge import (
    Bridge,
    LocalBridge,
    NodeIdentity,
    NodeRegistry,
    VerificationRequest,
    VerificationResponse,
    ConsensusState,
    ConsensusRound,
)

from .robust import (
    RobustVerifier,
    RobustConfig,
    LockedBaseline,
    SourceTracker,
    TemporalDecay,
    mad,
    modified_zscore,
    is_anomaly,
)

from .grounding import (
    GroundingEngine,
    Evidence,
)

__all__ = [
    # CDL
    'CDLEvaluator', 'CDLParser', 'HaltChecker',
    'AtomicConstraint', 'CompositeConstraint', 'ConditionalConstraint', 'Constraint',
    'Domain', 'Operator', 'EvaluationResult', 'AggregationState',
    'verify', 'verify_all', 'verify_and', 'verify_or', 'newton',

    # Forge
    'Forge', 'ForgeConfig', 'ForgeMetrics', 'VerificationResult',
    'get_forge', 'verify_content', 'verify_signal', 'verify_full',
    'SAFETY_PATTERNS',

    # Vault
    'Vault', 'VaultConfig', 'VaultEntry',
    'KeyDerivation', 'EncryptionEngine', 'get_vault',

    # Ledger
    'Ledger', 'LedgerConfig', 'LedgerEntry', 'MerkleTree', 'get_ledger',

    # Bridge
    'Bridge', 'LocalBridge', 'NodeIdentity', 'NodeRegistry',
    'VerificationRequest', 'VerificationResponse',
    'ConsensusState', 'ConsensusRound',

    # Robust
    'RobustVerifier', 'RobustConfig', 'LockedBaseline',
    'SourceTracker', 'TemporalDecay',
    'mad', 'modified_zscore', 'is_anomaly',

    # Grounding
    'GroundingEngine', 'Evidence',
]

__version__ = "1.0.0"
