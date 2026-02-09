#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
ADAN - SELF-VERIFYING AUTONOMOUS AGENT
Every action is constrained. Every claim is grounded. Every step is logged.
═══════════════════════════════════════════════════════════════════════════════

Adan = Ada + Newton
The constraint IS the instruction.
The verification IS the computation.
The ledger IS the memory.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

from .agent import NewtonAgent, AgentConfig, AgentResponse
from .grounding_enhanced import EnhancedGroundingEngine, OfficialSource
from .memory import AgentMemory, ConversationTurn
from .llm_ollama import OllamaBackend, OllamaConfig, create_ollama_generator
from .knowledge_base import KnowledgeBase, get_knowledge_base, VerifiedFact
from .kinematic_linguistics import (
    KinematicAnalyzer,
    KinematicSignature,
    Trajectory,
    TrajectoryPoint,
    SymbolType,
    get_kinematic_analyzer,
)
from .trajectory_verifier import (
    TrajectoryVerifier,
    TrajectoryVerification,
    TrajectoryComposer,
    CompositionState,
    get_trajectory_verifier,
    get_trajectory_composer,
)
from .language_mechanics import (
    LanguageMechanics,
    get_language_mechanics,
    SYNONYM_GROUPS,
    ANTONYMS,
)

__all__ = [
    "NewtonAgent",
    "AgentConfig", 
    "AgentResponse",
    "EnhancedGroundingEngine",
    "OfficialSource",
    "AgentMemory",
    "ConversationTurn",
    "OllamaBackend",
    "OllamaConfig",
    "create_ollama_generator",
    "KnowledgeBase",
    "get_knowledge_base",
    "VerifiedFact",
    # Kinematic Linguistics
    "KinematicAnalyzer",
    "KinematicSignature",
    "Trajectory",
    "TrajectoryPoint",
    "SymbolType",
    "get_kinematic_analyzer",
    # Trajectory Verification
    "TrajectoryVerifier",
    "TrajectoryVerification",
    "TrajectoryComposer",
    "CompositionState",
    "get_trajectory_verifier",
    "get_trajectory_composer",
    # Language Mechanics
    "LanguageMechanics",
    "get_language_mechanics",
    "SYNONYM_GROUPS",
    "ANTONYMS",
]
