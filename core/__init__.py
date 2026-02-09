"""Core package init for local imports in the workspace."""

# Centralized imports for shared logic
from .cdl import CDLEvaluator as CDL
from .logic import LogicEngine
from .forge import Forge as VerificationEngine
from .vault import Vault as EncryptedStorage
from .ledger import Ledger as ImmutableLedger
from .bridge import Bridge as DistributedProtocol
from .robust import RobustVerifier as AdversarialStatistics

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

__all__ = [
    "CDL",
    "LogicEngine",
    "VerificationEngine",
    "EncryptedStorage",
    "ImmutableLedger",
    "DistributedProtocol",
    "AdversarialStatistics",
]

__version__ = "1.0.0"
