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
- Logic: Verified Computation Engine (Turing complete, bounded)
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

    # Cohen-Sutherland Constraint Clipping
    ClipState,
    ClipResult,
    ConstraintClipper,
    CLIP_PATTERNS,
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

from .logic import (
    LogicEngine,
    ExecutionBounds,
    ExecutionContext,
    ExecutionResult,
    Value,
    ValueType,
    Expr,
    ExprType,
    calculate,
    calc,
)

from .vault_client import (
    VaultClient,
    ProvenanceRecord,
    get_vault_client,
)

from .policy_engine import (
    PolicyEngine,
    Policy,
    PolicyType,
    PolicyAction,
    PolicyEvaluationResult,
    get_policy_engine,
)

from .negotiator import (
    Negotiator,
    ApprovalRequest,
    ApprovalStatus,
    RequestPriority,
    get_negotiator,
)

from .merkle_anchor import (
    MerkleAnchorScheduler,
    MerkleAnchor,
    MerkleProof,
    verify_merkle_proof,
)

from .cartridges import (
    # Types
    CartridgeType,
    OutputFormat,

    # Results
    ConstraintResult,
    CartridgeResult,

    # Checker
    ConstraintChecker,

    # Cartridges
    VisualCartridge,
    SoundCartridge,
    SequenceCartridge,
    DataCartridge,
    RosettaCompiler,

    # Manager
    CartridgeManager,
    get_cartridge_manager,

    # Constraints
    VISUAL_CONSTRAINTS,
    SOUND_CONSTRAINTS,
    SEQUENCE_CONSTRAINTS,
    DATA_CONSTRAINTS,
    ROSETTA_CONSTRAINTS,
)

from .gumroad import (
    GumroadService,
    GumroadConfig,
    Customer,
    Feedback,
    LicenseVerification,
    get_gumroad_service,
)

from .voice_interface import (
    # Core Interface
    NewtonVoiceInterface,
    StreamingVoiceInterface,
    VoiceResponse,
    get_voice_interface,
    get_streaming_interface,
    ask_newton,

    # Intent System
    IntentParser,
    ParsedIntent,
    IntentType,
    DomainCategory,

    # Pattern Library
    PatternLibrary,
    AppPattern,
    find_pattern,

    # CDL Generator
    CDLGenerator,

    # Memory System
    ConversationMemory,
    MemoryObject,
    MemoryType,

    # Session Management
    SessionManager,
    Session,
    ConversationTurn,

    # Convenience
    parse_intent,
)

from .constraint_extractor import (
    # Core Extraction
    ConstraintExtractor,
    extract_constraints,
    get_extractor,

    # Verification
    PlanVerifier,
    verify_plan,
    VerifiedPlan,
    VerificationCertificate,

    # Extraction Results
    ExtractionResult,
    ExtractedConstraint,

    # Categories and Types
    ConstraintCategory,
    ConstraintStrength,
    ConstraintPolarity,

    # Patterns
    ExtractionPatterns,
)

from .chatbot_compiler import (
    # Core Compiler
    ChatbotCompiler,
    get_chatbot_compiler,
    compile_request,
    classify_only,

    # Governance
    ChatbotGovernor,
    get_chatbot_governor,

    # Type System
    RequestType,
    RiskLevel,
    CompilerDecision,

    # Data Classes
    RequestClassification,
    ResponseConstraint,
    CompiledResponse,

    # Constraint Rules
    RESPONSE_CONSTRAINTS,
    CLASSIFICATION_PATTERNS,
)

from .textgen import (
    # Core Classes
    TextStyle,
    TextConstraint,
    ProjectionResult,
    TextDocument,
    NewtonTextProjector,

    # Convenience Functions
    project,
    project_cdl,
    explain_constraints,
    generate_document,
    text_fingerprint,
    reduce_text,
    register_reduction,

    # JESTER Integration
    project_jester_constraints,

    # Ledger Integration
    create_text_ledger_entry,

    # Templates
    TEMPLATES,
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
    # Cohen-Sutherland Constraint Clipping
    'ClipState', 'ClipResult', 'ConstraintClipper', 'CLIP_PATTERNS',

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

    # Logic (Verified Computation)
    'LogicEngine', 'ExecutionBounds', 'ExecutionContext', 'ExecutionResult',
    'Value', 'ValueType', 'Expr', 'ExprType',
    'calculate', 'calc',
    
    # Glass Box Components
    'VaultClient', 'ProvenanceRecord', 'get_vault_client',
    'PolicyEngine', 'Policy', 'PolicyType', 'PolicyAction', 'PolicyEvaluationResult', 'get_policy_engine',
    'Negotiator', 'ApprovalRequest', 'ApprovalStatus', 'RequestPriority', 'get_negotiator',
    'MerkleAnchorScheduler', 'MerkleAnchor', 'MerkleProof', 'verify_merkle_proof',

    # Cartridges
    'CartridgeType', 'OutputFormat',
    'ConstraintResult', 'CartridgeResult',
    'ConstraintChecker',
    'VisualCartridge', 'SoundCartridge', 'SequenceCartridge', 'DataCartridge', 'RosettaCompiler',
    'CartridgeManager', 'get_cartridge_manager',
    'VISUAL_CONSTRAINTS', 'SOUND_CONSTRAINTS', 'SEQUENCE_CONSTRAINTS', 'DATA_CONSTRAINTS', 'ROSETTA_CONSTRAINTS',

    # Gumroad Integration
    'GumroadService', 'GumroadConfig', 'Customer', 'Feedback', 'LicenseVerification', 'get_gumroad_service',

    # Voice Interface (MOAD - Mother Of All Demos)
    'NewtonVoiceInterface', 'StreamingVoiceInterface', 'VoiceResponse',
    'get_voice_interface', 'get_streaming_interface', 'ask_newton',
    'IntentParser', 'ParsedIntent', 'IntentType', 'DomainCategory',
    'PatternLibrary', 'AppPattern', 'find_pattern',
    'CDLGenerator',
    'ConversationMemory', 'MemoryObject', 'MemoryType',
    'SessionManager', 'Session', 'ConversationTurn',
    'parse_intent',

    # Constraint Extraction - From Fuzzy to Formal
    'ConstraintExtractor', 'extract_constraints', 'get_extractor',
    'PlanVerifier', 'verify_plan', 'VerifiedPlan', 'VerificationCertificate',
    'ExtractionResult', 'ExtractedConstraint',
    'ConstraintCategory', 'ConstraintStrength', 'ConstraintPolarity',
    'ExtractionPatterns',

    # Chatbot Compiler - The Better ChatGPT
    'ChatbotCompiler', 'get_chatbot_compiler', 'compile_request', 'classify_only',
    'ChatbotGovernor', 'get_chatbot_governor',
    'RequestType', 'RiskLevel', 'CompilerDecision',
    'RequestClassification', 'ResponseConstraint', 'CompiledResponse',
    'RESPONSE_CONSTRAINTS', 'CLASSIFICATION_PATTERNS',

    # Text Generation - Constraint-Preserving Text Projection
    'TextStyle', 'TextConstraint', 'ProjectionResult', 'TextDocument', 'NewtonTextProjector',
    'project', 'project_cdl', 'explain_constraints', 'generate_document',
    'text_fingerprint', 'reduce_text', 'register_reduction',
    'project_jester_constraints', 'create_text_ledger_entry', 'TEMPLATES',
]

__version__ = "1.0.0"
