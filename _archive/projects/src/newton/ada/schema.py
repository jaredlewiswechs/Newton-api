"""
Ada Schema - Core data types and structures
============================================

Defines all the fundamental types used throughout Ada.
Built with verification-first design principles.
"""

from dataclasses import dataclass, field as dataclass_field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Union
import hashlib
import json
import uuid


# =============================================================================
# ENUMS - Mode and Type Definitions
# =============================================================================

class AdaMode(Enum):
    """Intelligence mode - similar to GPT-5.2 tiers but with verification."""

    INSTANT = "instant"      # Fast, everyday tasks
    THINKING = "thinking"    # Deep reasoning, step-by-step
    PRO = "pro"              # Maximum capability, complex tasks
    RESEARCH = "research"    # Deep web research mode
    AGENT = "agent"          # Autonomous task execution
    CANVAS = "canvas"        # Document/code building mode


class ResponseFormat(Enum):
    """Output format for Ada responses."""

    TEXT = "text"            # Plain text
    MARKDOWN = "markdown"    # GitHub-flavored markdown
    JSON = "json"            # Structured JSON
    HTML = "html"            # HTML formatted
    CODE = "code"            # Code block
    TABLE = "table"          # Tabular data


class MessageRole(Enum):
    """Role in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MemoryType(Enum):
    """Type of memory entry."""

    FACT = "fact"            # Verified factual information
    PREFERENCE = "preference" # User preferences
    CONTEXT = "context"      # Conversation context
    SKILL = "skill"          # Learned capability
    RELATIONSHIP = "relationship"  # Entity relationships


class ConnectorType(Enum):
    """Type of external connector."""

    WEB = "web"              # Web/URL fetching
    FILE = "file"            # Local file system
    API = "api"              # External APIs
    DATABASE = "database"    # Database connections
    EMAIL = "email"          # Email services
    CALENDAR = "calendar"    # Calendar services
    GITHUB = "github"        # GitHub integration
    SLACK = "slack"          # Slack integration
    NOTION = "notion"        # Notion integration


class SourceType(Enum):
    """Type of research source."""

    WEB = "web"              # Web page
    PAPER = "paper"          # Academic paper
    NEWS = "news"            # News article
    DOCUMENTATION = "documentation"  # Technical docs
    BOOK = "book"            # Book/publication
    DATABASE = "database"    # Database query result
    USER = "user"            # User-provided


class CodeLanguage(Enum):
    """Supported programming languages for code execution."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    BASH = "bash"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"


class CanvasType(Enum):
    """Type of canvas document."""

    DOCUMENT = "document"    # Text document
    CODE = "code"            # Code file
    DIAGRAM = "diagram"      # Visual diagram
    SPREADSHEET = "spreadsheet"  # Tabular data
    PRESENTATION = "presentation"  # Slides
    APP = "app"              # Interactive application


class TaskFrequency(Enum):
    """Frequency for scheduled tasks."""

    ONCE = "once"            # Run once
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"        # Custom cron expression


class TaskStatus(Enum):
    """Status of a scheduled task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStatus(Enum):
    """Status of an agent task."""

    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class FactStatus(Enum):
    """Verification status of a fact."""

    VERIFIED = "verified"    # Confirmed true
    REFUTED = "refuted"      # Confirmed false
    UNCERTAIN = "uncertain"  # Unable to verify
    PENDING = "pending"      # Not yet checked


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class AdaConfig:
    """
    Configuration for Ada instance.

    Controls behavior, capabilities, and policies.
    """

    # Mode settings
    default_mode: AdaMode = AdaMode.INSTANT
    default_format: ResponseFormat = ResponseFormat.MARKDOWN

    # Capability toggles
    enable_research: bool = True
    enable_memory: bool = True
    enable_agent: bool = True
    enable_canvas: bool = True
    enable_tasks: bool = True
    enable_code_execution: bool = True
    enable_connectors: bool = True

    # Verification settings
    verify_facts: bool = True
    verify_math: bool = True
    verify_logic: bool = True
    verify_physics: bool = True
    max_verification_retries: int = 3

    # Research settings
    max_research_sources: int = 20
    research_depth: int = 3  # Levels of link following

    # Memory settings
    memory_capacity: int = 10000
    memory_persistence: bool = True
    memory_file: str = ".ada_memory.json"

    # Agent settings
    agent_max_steps: int = 50
    agent_timeout_seconds: int = 300
    agent_require_approval: bool = False

    # Code execution settings
    sandbox_timeout_seconds: int = 30
    sandbox_memory_limit_mb: int = 512
    allowed_languages: List[CodeLanguage] = dataclass_field(
        default_factory=lambda: [
            CodeLanguage.PYTHON,
            CodeLanguage.JAVASCRIPT,
            CodeLanguage.BASH,
        ]
    )

    # Policy settings
    forbidden_topics: List[str] = dataclass_field(default_factory=list)
    required_disclaimers: List[str] = dataclass_field(default_factory=list)
    max_response_length: int = 100000

    # Model settings (for LLM backend)
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096

    # API settings
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, list):
                result[key] = [
                    v.value if isinstance(v, Enum) else v for v in value
                ]
            else:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdaConfig":
        """Create config from dictionary."""
        # Convert enum strings back to enums
        if "default_mode" in data:
            data["default_mode"] = AdaMode(data["default_mode"])
        if "default_format" in data:
            data["default_format"] = ResponseFormat(data["default_format"])
        if "allowed_languages" in data:
            data["allowed_languages"] = [
                CodeLanguage(lang) for lang in data["allowed_languages"]
            ]
        return cls(**data)


# =============================================================================
# MESSAGES AND CONVERSATIONS
# =============================================================================

@dataclass
class Message:
    """
    A single message in a conversation.

    Includes verification metadata.
    """

    role: MessageRole
    content: str
    timestamp: datetime = dataclass_field(default_factory=datetime.now)

    # Metadata
    id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None
    tool_call_id: Optional[str] = None

    # Verification
    verified: bool = False
    verification_hash: Optional[str] = None
    verification_details: Dict[str, Any] = dataclass_field(default_factory=dict)

    # Attachments
    attachments: List[Dict[str, Any]] = dataclass_field(default_factory=list)

    def compute_hash(self) -> str:
        """Compute verification hash for this message."""
        content_hash = hashlib.sha256(
            f"{self.role.value}:{self.content}:{self.timestamp.isoformat()}".encode()
        ).hexdigest()
        self.verification_hash = content_hash
        return content_hash

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "name": self.name,
            "tool_call_id": self.tool_call_id,
            "verified": self.verified,
            "verification_hash": self.verification_hash,
            "verification_details": self.verification_details,
            "attachments": self.attachments,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            name=data.get("name"),
            tool_call_id=data.get("tool_call_id"),
            verified=data.get("verified", False),
            verification_hash=data.get("verification_hash"),
            verification_details=data.get("verification_details", {}),
            attachments=data.get("attachments", []),
        )


@dataclass
class Conversation:
    """
    A conversation session with Ada.

    Maintains history and context.
    """

    id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = None
    messages: List[Message] = dataclass_field(default_factory=list)
    created_at: datetime = dataclass_field(default_factory=datetime.now)
    updated_at: datetime = dataclass_field(default_factory=datetime.now)

    # Context
    system_prompt: Optional[str] = None
    mode: AdaMode = AdaMode.INSTANT

    # Metadata
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)
    tags: List[str] = dataclass_field(default_factory=list)

    def add_message(self, role: MessageRole, content: str, **kwargs) -> Message:
        """Add a message to the conversation."""
        message = Message(role=role, content=content, **kwargs)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message

    def add_user_message(self, content: str, **kwargs) -> Message:
        """Add a user message."""
        return self.add_message(MessageRole.USER, content, **kwargs)

    def add_assistant_message(self, content: str, **kwargs) -> Message:
        """Add an assistant message."""
        return self.add_message(MessageRole.ASSISTANT, content, **kwargs)

    def get_context_window(self, max_messages: int = 50) -> List[Message]:
        """Get the most recent messages for context."""
        return self.messages[-max_messages:]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "system_prompt": self.system_prompt,
            "mode": self.mode.value,
            "metadata": self.metadata,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title"),
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            system_prompt=data.get("system_prompt"),
            mode=AdaMode(data["mode"]) if "mode" in data else AdaMode.INSTANT,
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
        )


# =============================================================================
# RESPONSES
# =============================================================================

@dataclass
class AdaResponse:
    """
    Response from Ada.

    Includes the content plus verification metadata.
    """

    content: str
    mode: AdaMode
    format: ResponseFormat

    # Verification results
    verified: bool = False
    verification_status: str = "pending"  # "verified", "partial", "refused"
    verification_iterations: int = 0
    verification_details: Dict[str, Any] = dataclass_field(default_factory=dict)

    # Claims extracted and validated
    claims: List[Dict[str, Any]] = dataclass_field(default_factory=list)

    # Metadata
    id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = dataclass_field(default_factory=datetime.now)
    processing_time_ms: int = 0
    tokens_used: int = 0

    # Sources (for research mode)
    sources: List[Dict[str, Any]] = dataclass_field(default_factory=list)

    # Tool calls (for agent mode)
    tool_calls: List[Dict[str, Any]] = dataclass_field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "mode": self.mode.value,
            "format": self.format.value,
            "verified": self.verified,
            "verification_status": self.verification_status,
            "verification_iterations": self.verification_iterations,
            "verification_details": self.verification_details,
            "claims": self.claims,
            "created_at": self.created_at.isoformat(),
            "processing_time_ms": self.processing_time_ms,
            "tokens_used": self.tokens_used,
            "sources": self.sources,
            "tool_calls": self.tool_calls,
        }


@dataclass
class Source:
    """A research source."""

    url: str
    title: str
    source_type: SourceType
    content: str = ""
    excerpt: str = ""

    # Credibility
    credibility_score: float = 0.5  # 0-1
    verified: bool = False

    # Metadata
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    accessed_at: datetime = dataclass_field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "source_type": self.source_type.value,
            "content": self.content,
            "excerpt": self.excerpt,
            "credibility_score": self.credibility_score,
            "verified": self.verified,
            "author": self.author,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "accessed_at": self.accessed_at.isoformat(),
        }


@dataclass
class ResearchReport:
    """
    Deep research report.

    Comprehensive, verified research output.
    """

    query: str
    summary: str
    detailed_findings: str

    # Sources used
    sources: List[Source] = dataclass_field(default_factory=list)

    # Key findings (verified)
    key_findings: List[str] = dataclass_field(default_factory=list)
    verified_claims: List[Dict[str, Any]] = dataclass_field(default_factory=list)

    # Confidence
    confidence_score: float = 0.0  # 0-1
    completeness_score: float = 0.0  # 0-1

    # Metadata
    id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = dataclass_field(default_factory=datetime.now)
    research_time_seconds: float = 0.0

    @property
    def report(self) -> str:
        """Get the full formatted report."""
        sections = [
            f"# Research Report: {self.query}",
            "",
            "## Summary",
            self.summary,
            "",
            "## Key Findings",
        ]

        for i, finding in enumerate(self.key_findings, 1):
            sections.append(f"{i}. {finding}")

        sections.extend([
            "",
            "## Detailed Analysis",
            self.detailed_findings,
            "",
            "## Sources",
        ])

        for source in self.sources:
            sections.append(f"- [{source.title}]({source.url})")

        sections.extend([
            "",
            "---",
            f"*Confidence: {self.confidence_score:.0%} | Completeness: {self.completeness_score:.0%}*",
        ])

        return "\n".join(sections)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "query": self.query,
            "summary": self.summary,
            "detailed_findings": self.detailed_findings,
            "sources": [s.to_dict() for s in self.sources],
            "key_findings": self.key_findings,
            "verified_claims": self.verified_claims,
            "confidence_score": self.confidence_score,
            "completeness_score": self.completeness_score,
            "created_at": self.created_at.isoformat(),
            "research_time_seconds": self.research_time_seconds,
        }


# =============================================================================
# AGENT TYPES
# =============================================================================

@dataclass
class AgentAction:
    """A single action taken by the agent."""

    action_type: str  # "tool_call", "code", "web", "file", etc.
    description: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None

    status: AgentStatus = AgentStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_type": self.action_type,
            "description": self.description,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


@dataclass
class AgentPlan:
    """Plan for agent task execution."""

    goal: str
    steps: List[str]
    estimated_actions: int = 0
    requires_approval: List[str] = dataclass_field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "goal": self.goal,
            "steps": self.steps,
            "estimated_actions": self.estimated_actions,
            "requires_approval": self.requires_approval,
        }


@dataclass
class AgentResult:
    """Result of agent task execution."""

    goal: str
    status: AgentStatus
    summary: str

    # Execution details
    plan: Optional[AgentPlan] = None
    actions: List[AgentAction] = dataclass_field(default_factory=list)

    # Output
    output: Any = None
    artifacts: List[Dict[str, Any]] = dataclass_field(default_factory=list)

    # Metadata
    id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = dataclass_field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_time_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "goal": self.goal,
            "status": self.status.value,
            "summary": self.summary,
            "plan": self.plan.to_dict() if self.plan else None,
            "actions": [a.to_dict() for a in self.actions],
            "output": self.output,
            "artifacts": self.artifacts,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_time_seconds": self.total_time_seconds,
        }


# =============================================================================
# CANVAS TYPES
# =============================================================================

@dataclass
class CanvasElement:
    """An element within a canvas document."""

    element_type: str  # "text", "code", "image", "table", etc.
    content: Any
    position: int = 0
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class CanvasDocument:
    """A canvas document for building content."""

    title: str
    canvas_type: CanvasType
    elements: List[CanvasElement] = dataclass_field(default_factory=list)

    # State
    content: str = ""
    version: int = 1
    history: List[Dict[str, Any]] = dataclass_field(default_factory=list)

    # Metadata
    id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = dataclass_field(default_factory=datetime.now)
    updated_at: datetime = dataclass_field(default_factory=datetime.now)

    def add_element(self, element_type: str, content: Any, **kwargs) -> CanvasElement:
        """Add an element to the canvas."""
        element = CanvasElement(
            element_type=element_type,
            content=content,
            position=len(self.elements),
            **kwargs
        )
        self.elements.append(element)
        self._update()
        return element

    def _update(self):
        """Update modification time and version."""
        self.version += 1
        self.updated_at = datetime.now()

    def render(self) -> str:
        """Render the canvas to a string."""
        return self.content

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "canvas_type": self.canvas_type.value,
            "elements": [
                {
                    "id": e.id,
                    "element_type": e.element_type,
                    "content": e.content,
                    "position": e.position,
                    "metadata": e.metadata,
                }
                for e in self.elements
            ],
            "content": self.content,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# =============================================================================
# TASK TYPES
# =============================================================================

@dataclass
class ScheduledTask:
    """A scheduled task."""

    name: str
    description: str
    prompt: str
    frequency: TaskFrequency

    # Schedule details
    cron_expression: Optional[str] = None
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None

    # Status
    status: TaskStatus = TaskStatus.PENDING
    run_count: int = 0

    # Configuration
    enabled: bool = True
    notify_on_complete: bool = True
    notify_email: Optional[str] = None

    # Metadata
    id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = dataclass_field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "prompt": self.prompt,
            "frequency": self.frequency.value,
            "cron_expression": self.cron_expression,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "status": self.status.value,
            "run_count": self.run_count,
            "enabled": self.enabled,
            "notify_on_complete": self.notify_on_complete,
            "notify_email": self.notify_email,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class TaskResult:
    """Result of a task execution."""

    task_id: str
    task_name: str
    status: TaskStatus
    output: str

    # Timing
    started_at: datetime = dataclass_field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0

    # Error handling
    error: Optional[str] = None
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "status": self.status.value,
            "output": self.output,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
            "retry_count": self.retry_count,
        }


# =============================================================================
# MEMORY TYPES
# =============================================================================

@dataclass
class MemoryEntry:
    """A single memory entry."""

    key: str
    value: Any
    memory_type: MemoryType

    # Verification
    verified: bool = False
    confidence: float = 0.5

    # Metadata
    id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = dataclass_field(default_factory=datetime.now)
    updated_at: datetime = dataclass_field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    # Source
    source: Optional[str] = None
    conversation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "memory_type": self.memory_type.value,
            "verified": self.verified,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "source": self.source,
            "conversation_id": self.conversation_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            key=data["key"],
            value=data["value"],
            memory_type=MemoryType(data["memory_type"]),
            verified=data.get("verified", False),
            confidence=data.get("confidence", 0.5),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            access_count=data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None,
            source=data.get("source"),
            conversation_id=data.get("conversation_id"),
        )


@dataclass
class Memory:
    """User memory container."""

    entries: List[MemoryEntry] = dataclass_field(default_factory=list)

    def add(self, key: str, value: Any, memory_type: MemoryType = MemoryType.FACT, **kwargs) -> MemoryEntry:
        """Add a memory entry."""
        entry = MemoryEntry(key=key, value=value, memory_type=memory_type, **kwargs)
        self.entries.append(entry)
        return entry

    def get(self, key: str) -> Optional[MemoryEntry]:
        """Get a memory entry by key."""
        for entry in self.entries:
            if entry.key == key:
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                return entry
        return None

    def search(self, query: str) -> List[MemoryEntry]:
        """Search memory entries."""
        results = []
        query_lower = query.lower()
        for entry in self.entries:
            if query_lower in entry.key.lower() or query_lower in str(entry.value).lower():
                results.append(entry)
        return results

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entries": [e.to_dict() for e in self.entries]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create from dictionary."""
        return cls(
            entries=[MemoryEntry.from_dict(e) for e in data.get("entries", [])]
        )


# =============================================================================
# CONNECTOR TYPES
# =============================================================================

@dataclass
class Connector:
    """Base connector for external services."""

    name: str
    connector_type: ConnectorType
    enabled: bool = True

    # Authentication
    api_key: Optional[str] = None
    auth_token: Optional[str] = None

    # Configuration
    config: Dict[str, Any] = dataclass_field(default_factory=dict)

    # Status
    connected: bool = False
    last_used: Optional[datetime] = None
    error: Optional[str] = None

    # Metadata
    id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = dataclass_field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "name": self.name,
            "connector_type": self.connector_type.value,
            "enabled": self.enabled,
            "config": self.config,
            "connected": self.connected,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# CODE EXECUTION TYPES
# =============================================================================

@dataclass
class CodeResult:
    """Result of code execution."""

    code: str
    language: CodeLanguage
    success: bool

    # Output
    stdout: str = ""
    stderr: str = ""
    return_value: Any = None

    # Timing
    execution_time_ms: int = 0

    # Error
    error: Optional[str] = None
    error_line: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "language": self.language.value,
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "return_value": self.return_value,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
            "error_line": self.error_line,
        }
