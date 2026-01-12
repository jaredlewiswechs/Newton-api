"""
Ada - The Newton Intelligence Engine
=====================================

A comprehensive AI assistant that does everything ChatGPT does, but BETTER.
Built on Newton's constraint verification system for guaranteed reliability.

Features:
---------
- Multi-tier intelligence (Instant, Thinking, Pro modes)
- Deep Research with source verification
- Persistent Memory with fact verification
- Agent Mode for autonomous task completion
- Canvas Mode for document/code/app building
- Tasks & Scheduling
- Connectors for external integrations
- Code Execution sandbox
- Math verification with SymPy
- Physics validation with KineticForge
- Policy enforcement

Why Ada is BETTER than ChatGPT:
-------------------------------
1. Verified Outputs - All claims are validated before returning
2. Reduced Hallucinations - Constraint-based fact checking
3. Transparent Reasoning - Full audit trail of decisions
4. Customizable Policies - Define your own safety rules
5. Domain Expertise - Specialized validators for different domains

Quick Start:
------------
    from newton.ada import Ada, AdaConfig

    # Create Ada instance
    ada = Ada()

    # Simple chat
    response = ada.chat("What is 2 + 2?")
    print(response.content)  # "2 + 2 = 4" (verified!)

    # Deep research
    research = ada.research("Latest advances in quantum computing")
    print(research.report)  # Comprehensive, verified report

    # Agent mode
    result = ada.agent("Find all Python files and count lines of code")
    print(result.summary)  # Task completed autonomously

Philosophy:
-----------
Ada subordinates language model outputs to formal constraint verification.
"The LLM proposes. Ada verifies. Only truth survives."

Named after Ada Lovelace, the first computer programmer.
"""

__version__ = "1.0.0"
__author__ = "Newton Team"

# Core Schema
from .schema import (
    # Configuration
    AdaConfig,
    AdaMode,
    ResponseFormat,
    # Messages
    Message,
    MessageRole,
    Conversation,
    # Responses
    AdaResponse,
    ResearchReport,
    AgentResult,
    CanvasDocument,
    TaskResult,
    # Memory
    Memory,
    MemoryEntry,
    MemoryType,
    # Connectors
    Connector,
    ConnectorType,
    # Code execution
    CodeResult,
    CodeLanguage,
)

# Intelligence Engine
from .engine import (
    Ada,
    AdaEngine,
    IntelligenceMode,
)

# Research System
from .research import (
    DeepResearch,
    Source,
    SourceType,
    ResearchConfig,
)

# Memory System
from .memory import (
    MemoryStore,
    VerifiedFact,
    FactStatus,
)

# Agent System
from .agent import (
    AdaAgent,
    AgentAction,
    AgentPlan,
    AgentStatus,
)

# Canvas System
from .canvas import (
    Canvas,
    CanvasType,
    CanvasElement,
)

# Tasks & Scheduling
from .tasks import (
    TaskScheduler,
    ScheduledTask,
    TaskFrequency,
    TaskStatus,
)

# Connectors
from .connectors import (
    ConnectorRegistry,
    WebConnector,
    FileConnector,
    APIConnector,
)

# Code Execution
from .sandbox import (
    CodeSandbox,
    ExecutionResult,
    SandboxConfig,
)

# Web Interface
from .web import (
    create_ada_app,
    AdaWebConfig,
)

# CLI
from .cli import (
    ada_cli,
    AdaCLI,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "Ada",
    "AdaConfig",
    "AdaMode",
    "AdaEngine",
    "IntelligenceMode",
    # Messages
    "Message",
    "MessageRole",
    "Conversation",
    "ResponseFormat",
    # Responses
    "AdaResponse",
    "ResearchReport",
    "AgentResult",
    "CanvasDocument",
    "TaskResult",
    # Research
    "DeepResearch",
    "Source",
    "SourceType",
    "ResearchConfig",
    # Memory
    "Memory",
    "MemoryEntry",
    "MemoryType",
    "MemoryStore",
    "VerifiedFact",
    "FactStatus",
    # Agent
    "AdaAgent",
    "AgentAction",
    "AgentPlan",
    "AgentStatus",
    # Canvas
    "Canvas",
    "CanvasType",
    "CanvasElement",
    # Tasks
    "TaskScheduler",
    "ScheduledTask",
    "TaskFrequency",
    "TaskStatus",
    # Connectors
    "Connector",
    "ConnectorType",
    "ConnectorRegistry",
    "WebConnector",
    "FileConnector",
    "APIConnector",
    # Code
    "CodeSandbox",
    "CodeResult",
    "CodeLanguage",
    "ExecutionResult",
    "SandboxConfig",
    # Web
    "create_ada_app",
    "AdaWebConfig",
    # CLI
    "ada_cli",
    "AdaCLI",
]
