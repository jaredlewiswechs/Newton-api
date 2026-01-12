"""
Comprehensive tests for Ada - The Better ChatGPT
=================================================

Tests all Ada capabilities:
- Chat with verification
- Deep research
- Memory system
- Agent execution
- Canvas building
- Code execution
- Task scheduling
- Connectors
"""

import json
import os
import pytest
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Import Ada components
from newton.ada.schema import (
    AdaConfig,
    AdaMode,
    AdaResponse,
    AgentAction,
    AgentPlan,
    AgentResult,
    AgentStatus,
    CanvasDocument,
    CanvasType,
    CodeLanguage,
    CodeResult,
    Connector,
    ConnectorType,
    Conversation,
    FactStatus,
    Memory,
    MemoryEntry,
    MemoryType,
    Message,
    MessageRole,
    ResearchReport,
    ResponseFormat,
    ScheduledTask,
    Source,
    SourceType,
    TaskFrequency,
    TaskResult,
    TaskStatus,
)
from newton.ada.engine import Ada, AdaEngine, IntelligenceMode, LLMClient
from newton.ada.research import DeepResearch, ClaimExtractor, SourceRanker, ClaimVerifier, ResearchConfig
from newton.ada.memory import MemoryStore, VerifiedFact
from newton.ada.agent import AdaAgent, Tool, ToolRegistry, ActionType, Planner, Executor
from newton.ada.canvas import Canvas, ContentGenerator, ContentVerifier, EditOperation
from newton.ada.sandbox import CodeSandbox, SecurityChecker, SandboxConfig
from newton.ada.tasks import TaskScheduler, CronParser, TaskRunner, TaskStore
from newton.ada.connectors import ConnectorRegistry, WebConnector, FileConnector, APIConnector, ConnectionStatus


# =============================================================================
# SCHEMA TESTS
# =============================================================================

class TestSchema:
    """Tests for schema data types."""

    def test_ada_config_defaults(self):
        """Test AdaConfig default values."""
        config = AdaConfig()
        assert config.default_mode == AdaMode.INSTANT
        assert config.verify_facts is True
        assert config.verify_math is True
        assert config.enable_memory is True
        assert config.max_verification_retries == 3

    def test_ada_config_custom(self):
        """Test AdaConfig with custom values."""
        config = AdaConfig(
            default_mode=AdaMode.THINKING,
            verify_facts=False,
            max_tokens=8192,
        )
        assert config.default_mode == AdaMode.THINKING
        assert config.verify_facts is False
        assert config.max_tokens == 8192

    def test_ada_config_to_dict(self):
        """Test AdaConfig serialization."""
        config = AdaConfig(default_mode=AdaMode.PRO)
        data = config.to_dict()
        assert data["default_mode"] == "pro"
        assert "verify_facts" in data

    def test_message_creation(self):
        """Test Message creation."""
        msg = Message(role=MessageRole.USER, content="Hello, Ada!")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello, Ada!"
        assert msg.id is not None
        assert msg.verified is False

    def test_message_hash(self):
        """Test Message verification hash."""
        msg = Message(role=MessageRole.USER, content="Test")
        hash1 = msg.compute_hash()
        assert hash1 is not None
        assert len(hash1) == 64  # SHA-256

    def test_message_serialization(self):
        """Test Message to_dict and from_dict."""
        msg = Message(role=MessageRole.ASSISTANT, content="Response")
        data = msg.to_dict()
        restored = Message.from_dict(data)
        assert restored.role == msg.role
        assert restored.content == msg.content

    def test_conversation_add_message(self):
        """Test Conversation message management."""
        conv = Conversation()
        conv.add_user_message("Hello")
        conv.add_assistant_message("Hi there!")

        assert len(conv.messages) == 2
        assert conv.messages[0].role == MessageRole.USER
        assert conv.messages[1].role == MessageRole.ASSISTANT

    def test_conversation_context_window(self):
        """Test Conversation context window."""
        conv = Conversation()
        for i in range(100):
            conv.add_user_message(f"Message {i}")

        context = conv.get_context_window(max_messages=10)
        assert len(context) == 10
        assert context[0].content == "Message 90"

    def test_ada_response(self):
        """Test AdaResponse creation."""
        response = AdaResponse(
            content="2 + 2 = 4",
            mode=AdaMode.INSTANT,
            format=ResponseFormat.MARKDOWN,
            verified=True,
            verification_status="verified",
        )
        assert response.verified is True
        assert response.content == "2 + 2 = 4"

    def test_research_report(self):
        """Test ResearchReport generation."""
        report = ResearchReport(
            query="quantum computing",
            summary="A summary of quantum computing",
            detailed_findings="Detailed findings...",
            key_findings=["Finding 1", "Finding 2"],
            confidence_score=0.85,
        )
        assert "quantum computing" in report.report
        assert "Finding 1" in report.report

    def test_memory_operations(self):
        """Test Memory data structure."""
        memory = Memory()
        entry = memory.add("user_name", "Alice", MemoryType.PREFERENCE)

        assert entry.key == "user_name"
        assert entry.value == "Alice"

        found = memory.get("user_name")
        assert found is not None
        assert found.access_count == 1

    def test_canvas_document(self):
        """Test CanvasDocument operations."""
        doc = CanvasDocument(
            title="Test Document",
            canvas_type=CanvasType.CODE,
        )
        doc.add_element("code", "print('hello')")

        assert len(doc.elements) == 1
        assert doc.version == 2  # Initial + add

    def test_scheduled_task(self):
        """Test ScheduledTask serialization."""
        task = ScheduledTask(
            name="Daily Summary",
            description="Summarize news",
            prompt="Summarize today's AI news",
            frequency=TaskFrequency.DAILY,
        )
        data = task.to_dict()
        assert data["name"] == "Daily Summary"
        assert data["frequency"] == "daily"


# =============================================================================
# ENGINE TESTS
# =============================================================================

class TestEngine:
    """Tests for Ada engine."""

    def test_llm_client(self):
        """Test LLM client mock responses."""
        client = LLMClient()

        # Math question
        response = client.generate("What is 2 + 2?")
        assert "4" in response

        # Greeting
        response = client.generate("Hello!")
        assert "Hello" in response

    def test_ada_engine_creation(self):
        """Test AdaEngine initialization."""
        engine = AdaEngine()
        assert engine.config is not None
        assert engine.llm is not None

    def test_ada_engine_generate(self):
        """Test AdaEngine response generation."""
        engine = AdaEngine()
        response = engine.generate("Hello, Ada!")

        assert response is not None
        assert response.content is not None
        assert response.mode == AdaMode.INSTANT

    def test_ada_engine_with_verification(self):
        """Test AdaEngine with verification enabled."""
        config = AdaConfig(verify_facts=True, verify_math=True)
        engine = AdaEngine(config)
        response = engine.generate("What is 2 + 2?", verify=True)

        assert response is not None

    def test_ada_class_chat(self):
        """Test Ada class chat method."""
        ada = Ada()
        response = ada.chat("Hello!")

        assert response is not None
        assert response.content is not None

    def test_ada_conversation_management(self):
        """Test Ada conversation handling."""
        ada = Ada()

        # First message creates conversation
        ada.chat("Hello")
        assert ada.conversation is not None

        # Second message uses same conversation
        conv_id = ada.conversation.id
        ada.chat("How are you?")
        assert ada.conversation.id == conv_id
        assert len(ada.conversation.messages) == 4  # 2 user + 2 assistant

    def test_ada_new_conversation(self):
        """Test starting new conversation."""
        ada = Ada()
        ada.chat("Hello")

        old_id = ada.conversation.id
        ada.new_conversation("New Chat")

        assert ada.conversation.id != old_id
        assert ada.conversation.title == "New Chat"
        assert len(ada.conversation.messages) == 0

    def test_ada_mode_switching(self):
        """Test mode switching."""
        ada = Ada()

        ada.set_mode(AdaMode.THINKING)
        assert ada.config.default_mode == AdaMode.THINKING

        ada.set_mode("pro")  # String mode
        assert ada.config.default_mode == AdaMode.PRO

    def test_ada_stats(self):
        """Test usage statistics."""
        ada = Ada()
        ada.chat("Test message")

        stats = ada.get_stats()
        assert stats["total_requests"] == 1


# =============================================================================
# RESEARCH TESTS
# =============================================================================

class TestResearch:
    """Tests for deep research system."""

    def test_claim_extractor(self):
        """Test claim extraction from text."""
        extractor = ClaimExtractor()
        text = """
        According to studies, AI is advancing rapidly.
        In 2024, researchers found significant improvements.
        Over 50% of companies now use AI.
        """
        claims = extractor.extract(text)
        assert len(claims) > 0

    def test_source_ranker(self):
        """Test source credibility ranking."""
        config = ResearchConfig()
        ranker = SourceRanker(config)

        # Government sites should rank high
        gov_score = ranker.get_credibility("https://www.nasa.gov/article")
        assert gov_score >= 0.9

        # Education sites should rank high
        edu_score = ranker.get_credibility("https://mit.edu/research")
        assert edu_score >= 0.85

        # Unknown sites get default score
        unknown_score = ranker.get_credibility("https://random-site.com/page")
        assert unknown_score == 0.5

    def test_claim_verifier(self):
        """Test claim verification."""
        verifier = ClaimVerifier(threshold=2)

        sources = [
            Source(url="https://example1.com", title="Source 1", source_type=SourceType.WEB, content="AI is advancing rapidly"),
            Source(url="https://example2.com", title="Source 2", source_type=SourceType.WEB, content="AI advancement is rapid"),
        ]

        claim = {"text": "AI is advancing rapidly"}
        result = verifier.verify_claim(claim, sources)

        assert "verified" in result
        assert "confidence" in result

    def test_deep_research(self):
        """Test deep research investigation."""
        research = DeepResearch(max_sources=5)
        report = research.investigate("artificial intelligence")

        assert report is not None
        assert report.query == "artificial intelligence"
        assert len(report.sources) > 0

    def test_research_quick_search(self):
        """Test quick search."""
        research = DeepResearch()
        sources = research.quick_search("machine learning", max_results=3)

        assert len(sources) <= 3

    def test_research_fact_check(self):
        """Test single claim fact-checking."""
        research = DeepResearch()
        result = research.fact_check("The sky is blue")

        assert "claim" in result
        assert "verdict" in result


# =============================================================================
# MEMORY TESTS
# =============================================================================

class TestMemory:
    """Tests for memory system."""

    def test_memory_store_add(self):
        """Test adding memory entries."""
        store = MemoryStore(persistence=False)
        entry = store.add("test_key", "test_value")

        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert len(store.entries) == 1

    def test_memory_store_get(self):
        """Test retrieving memory entries."""
        store = MemoryStore(persistence=False)
        store.add("key1", "value1")

        entry = store.get("key1")
        assert entry is not None
        assert entry.value == "value1"
        assert entry.access_count == 1

    def test_memory_store_search(self):
        """Test searching memory."""
        store = MemoryStore(persistence=False)
        store.add("python_version", "3.11")
        store.add("java_version", "17")
        store.add("favorite_color", "blue")

        results = store.search("version")
        assert len(results) == 2

    def test_memory_store_remove(self):
        """Test removing memory entries."""
        store = MemoryStore(persistence=False)
        store.add("to_remove", "value")
        assert store.remove("to_remove") is True
        assert store.get("to_remove") is None

    def test_verified_fact(self):
        """Test verified fact creation."""
        fact = VerifiedFact(
            statement="2 + 2 = 4",
            status=FactStatus.VERIFIED,
            confidence=1.0,
            source="math",
        )
        assert fact.hash is not None
        assert len(fact.hash) == 16

    def test_contradiction_detection(self):
        """Test contradiction detection."""
        store = MemoryStore(persistence=False)
        store.add("fact1", "The sky is blue", verified=True)

        contradictions = store.check_contradiction("The sky is not blue")
        # Should detect potential contradiction
        assert isinstance(contradictions, list)

    def test_memory_persistence(self):
        """Test memory persistence to file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            # Create and populate store
            store1 = MemoryStore(persistence=True, storage_file=filepath)
            store1.add("persistent_key", "persistent_value")

            # Create new store from same file
            store2 = MemoryStore(persistence=True, storage_file=filepath)

            entry = store2.get("persistent_key")
            assert entry is not None
            assert entry.value == "persistent_value"
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_memory_capacity(self):
        """Test memory capacity limits."""
        store = MemoryStore(capacity=5, persistence=False)

        for i in range(10):
            store.add(f"key{i}", f"value{i}")

        # Should not exceed capacity
        assert len(store.entries) <= 5


# =============================================================================
# AGENT TESTS
# =============================================================================

class TestAgent:
    """Tests for agent system."""

    def test_tool_registry(self):
        """Test tool registry."""
        registry = ToolRegistry()
        tools = registry.list_tools()

        assert len(tools) > 0
        assert registry.get("search") is not None

    def test_tool_execution(self):
        """Test tool execution."""
        registry = ToolRegistry()
        search_tool = registry.get("search")

        result = search_tool.execute({"query": "test"})
        assert result is not None
        assert "results" in result

    def test_planner(self):
        """Test task planning."""
        planner = Planner()
        tools = ToolRegistry().list_tools()

        plan = planner.create_plan("Find all Python files", tools)
        assert plan is not None
        assert len(plan.steps) > 0
        assert plan.goal == "Find all Python files"

    def test_executor(self):
        """Test step execution."""
        registry = ToolRegistry()
        executor = Executor(registry)

        action, context = executor.execute_step("Search for files", {})
        assert action is not None
        assert action.status in (AgentStatus.COMPLETED, AgentStatus.PENDING)

    def test_ada_agent_execute(self):
        """Test agent task execution."""
        agent = AdaAgent(max_steps=5)
        result = agent.execute("Find Python files")

        assert result is not None
        assert result.status in (AgentStatus.COMPLETED, AgentStatus.FAILED)
        assert result.summary != ""

    def test_agent_capabilities(self):
        """Test listing agent capabilities."""
        agent = AdaAgent()
        capabilities = agent.list_capabilities()

        assert len(capabilities) > 0
        assert any("search" in cap.lower() for cap in capabilities)

    def test_custom_tool_registration(self):
        """Test registering custom tools."""
        agent = AdaAgent()

        custom_tool = Tool(
            name="custom",
            description="Custom tool",
            action_type=ActionType.ANALYZE,
            handler=lambda params: {"result": "custom"},
        )
        agent.register_tool(custom_tool)

        assert agent.tools.get("custom") is not None


# =============================================================================
# CANVAS TESTS
# =============================================================================

class TestCanvas:
    """Tests for canvas system."""

    def test_content_generator_code(self):
        """Test code generation."""
        generator = ContentGenerator()
        code = generator.generate_code(
            "Calculate fibonacci",
            CodeLanguage.PYTHON,
        )
        assert code is not None
        assert "def" in code or "fibonacci" in code.lower()

    def test_content_generator_document(self):
        """Test document generation."""
        generator = ContentGenerator()
        doc = generator.generate_document("API documentation")

        assert doc is not None
        assert len(doc) > 0

    def test_content_verifier_python(self):
        """Test Python code verification."""
        verifier = ContentVerifier()

        # Valid code
        valid, issues = verifier.verify(
            "def test(): pass",
            CanvasType.CODE,
            CodeLanguage.PYTHON,
        )
        assert valid is True
        assert len(issues) == 0

        # Invalid code
        valid, issues = verifier.verify(
            "def test( pass",
            CanvasType.CODE,
            CodeLanguage.PYTHON,
        )
        assert valid is False
        assert len(issues) > 0

    def test_canvas_create(self):
        """Test canvas creation."""
        canvas = Canvas()
        doc = canvas.create("Test Canvas", CanvasType.DOCUMENT, "Initial content")

        assert doc is not None
        assert doc.title == "Test Canvas"
        assert doc.content == "Initial content"

    def test_canvas_process(self):
        """Test canvas processing."""
        canvas = Canvas()
        doc = canvas.process("Create a Python hello world function")

        assert doc is not None
        assert doc.canvas_type == CanvasType.CODE
        assert doc.content is not None

    def test_canvas_edit(self):
        """Test canvas editing."""
        canvas = Canvas()
        doc = canvas.create("Test", CanvasType.DOCUMENT, "Original content")

        edited = canvas.edit(doc, "Make it better")
        assert edited.version > 1

    def test_canvas_undo(self):
        """Test canvas undo."""
        canvas = Canvas()
        doc = canvas.create("Test", CanvasType.DOCUMENT, "Original")
        canvas.edit(doc, "Change it")

        original_content = doc.content
        success = canvas.undo(doc)
        assert success is True
        assert doc.content != original_content or doc.version < 3

    def test_canvas_export_html(self):
        """Test HTML export."""
        canvas = Canvas()
        doc = canvas.create("Test", CanvasType.DOCUMENT, "# Hello World")

        html = canvas.export(doc, "html")
        assert "<html>" in html
        assert "Hello World" in html


# =============================================================================
# SANDBOX TESTS
# =============================================================================

class TestSandbox:
    """Tests for code sandbox."""

    def test_security_checker_safe(self):
        """Test security checker with safe code."""
        config = SandboxConfig()
        checker = SecurityChecker(config)

        is_safe, issues = checker.check(
            "x = 1 + 2\nprint(x)",
            CodeLanguage.PYTHON,
        )
        assert is_safe is True
        assert len(issues) == 0

    def test_security_checker_dangerous(self):
        """Test security checker with dangerous code."""
        config = SandboxConfig()
        checker = SecurityChecker(config)

        # Import dangerous module
        is_safe, issues = checker.check(
            "import subprocess",
            CodeLanguage.PYTHON,
        )
        assert is_safe is False

        # Exec call
        is_safe, issues = checker.check(
            "exec('print(1)')",
            CodeLanguage.PYTHON,
        )
        assert is_safe is False

    def test_sandbox_execute_python(self):
        """Test Python code execution."""
        sandbox = CodeSandbox()
        result = sandbox.execute(
            "print(2 + 2)",
            CodeLanguage.PYTHON,
        )

        assert result.success is True
        assert "4" in result.stdout

    def test_sandbox_execute_with_return(self):
        """Test execution with return value."""
        sandbox = CodeSandbox()
        result = sandbox.execute(
            "_result = [1, 2, 3]",
            CodeLanguage.PYTHON,
        )

        assert result.success is True
        assert result.return_value == [1, 2, 3]

    def test_sandbox_execute_error(self):
        """Test execution with error."""
        sandbox = CodeSandbox()
        result = sandbox.execute(
            "raise ValueError('test error')",
            CodeLanguage.PYTHON,
        )

        assert result.success is False
        assert "ValueError" in result.error

    def test_sandbox_blocked_language(self):
        """Test blocked language."""
        sandbox = CodeSandbox(allowed_languages=[CodeLanguage.PYTHON])
        result = sandbox.execute(
            "console.log('test')",
            CodeLanguage.JAVASCRIPT,
        )

        assert result.success is False
        assert "not allowed" in result.error.lower()

    def test_sandbox_check_without_execute(self):
        """Test code checking without execution."""
        sandbox = CodeSandbox()
        is_safe, issues = sandbox.check_code(
            "import os; os.system('rm -rf /')",
            CodeLanguage.PYTHON,
        )

        assert is_safe is False


# =============================================================================
# TASKS TESTS
# =============================================================================

class TestTasks:
    """Tests for task scheduling."""

    def test_cron_parser(self):
        """Test cron expression parsing."""
        parsed = CronParser.parse("0 9 * * 1")  # 9 AM Monday

        assert 0 in parsed["minute"]
        assert 9 in parsed["hour"]
        assert 1 in parsed["weekday"]

    def test_cron_matches(self):
        """Test cron matching."""
        parsed = CronParser.parse("0 * * * *")  # Every hour
        dt = datetime(2024, 1, 15, 10, 0, 0)

        assert CronParser.matches(parsed, dt) is True

        dt_wrong = datetime(2024, 1, 15, 10, 30, 0)
        assert CronParser.matches(parsed, dt_wrong) is False

    def test_cron_next_run(self):
        """Test next run calculation."""
        parsed = CronParser.parse("0 9 * * *")  # 9 AM daily
        now = datetime(2024, 1, 15, 8, 0, 0)

        next_run = CronParser.next_run(parsed, now)
        assert next_run.hour == 9
        assert next_run.minute == 0

    def test_task_store(self):
        """Test task storage."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            store = TaskStore(storage_file=filepath)

            task = ScheduledTask(
                name="Test Task",
                description="A test task",
                prompt="Do something",
                frequency=TaskFrequency.DAILY,
            )
            store.add(task)

            retrieved = store.get(task.id)
            assert retrieved is not None
            assert retrieved.name == "Test Task"
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_task_scheduler_schedule(self):
        """Test scheduling a task."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            scheduler = TaskScheduler(storage_file=filepath)
            task = scheduler.schedule(
                prompt="Summarize AI news",
                name="AI Summary",
                frequency="daily",
            )

            assert task is not None
            assert task.name == "AI Summary"
            assert task.next_run is not None
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_task_scheduler_run_now(self):
        """Test immediate task execution."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            scheduler = TaskScheduler(storage_file=filepath)
            task = scheduler.schedule(
                prompt="Say hello",
                name="Hello Task",
                frequency="once",
            )

            result = scheduler.run_now(task.id)
            assert result is not None
            assert result.task_name == "Hello Task"
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_task_scheduler_pause_resume(self):
        """Test pausing and resuming tasks."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            scheduler = TaskScheduler(storage_file=filepath)
            task = scheduler.schedule(
                prompt="Test",
                name="Test Task",
                frequency="daily",
            )

            scheduler.pause(task.id)
            task = scheduler.store.get(task.id)
            assert task.enabled is False

            scheduler.resume(task.id)
            task = scheduler.store.get(task.id)
            assert task.enabled is True
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


# =============================================================================
# CONNECTORS TESTS
# =============================================================================

class TestConnectors:
    """Tests for connector system."""

    def test_web_connector(self):
        """Test web connector."""
        connector = WebConnector({"base_url": "https://example.com"})

        assert connector.connect() is True
        assert connector.status == ConnectionStatus.CONNECTED

        result = connector.query("fetch", {"url": "https://example.com/page"})
        assert result.success is True

    def test_file_connector(self):
        """Test file connector."""
        connector = FileConnector({"root_path": "."})

        assert connector.connect() is True

        result = connector.query("list", {"path": "."})
        assert result.success is True
        assert "files" in result.data

    def test_api_connector(self):
        """Test API connector."""
        connector = APIConnector({
            "base_url": "https://api.example.com",
            "api_key": "test_key",
        })

        connector.connect()

        result = connector.query("get", {"endpoint": "users"})
        assert result.success is True

    def test_connector_registry(self):
        """Test connector registry."""
        registry = ConnectorRegistry()

        # Register connectors
        web = registry.register("web1", ConnectorType.WEB, {"base_url": "https://example.com"})
        file = registry.register("file1", ConnectorType.FILE, {"root_path": "."})

        assert registry.get("web1") is not None
        assert registry.get("file1") is not None

        # List connectors
        connectors = registry.list_connectors()
        assert len(connectors) == 2

    def test_connector_registry_connect_all(self):
        """Test connecting all connectors."""
        registry = ConnectorRegistry()
        registry.register("web", ConnectorType.WEB)
        registry.register("file", ConnectorType.FILE, {"root_path": "."})

        results = registry.connect_all()
        assert all(results.values())

    def test_connector_query_through_registry(self):
        """Test querying through registry."""
        registry = ConnectorRegistry()
        registry.register("web", ConnectorType.WEB)

        web = registry.get("web")
        web.connect()

        result = registry.query("web", "search", {"query": "test"})
        assert result.success is True


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for Ada."""

    def test_full_chat_flow(self):
        """Test complete chat interaction flow."""
        ada = Ada()

        # Start conversation
        response1 = ada.chat("Hello, my name is Alice")
        assert response1 is not None

        # Continue conversation
        response2 = ada.chat("What did I just tell you?")
        assert response2 is not None

        # Check conversation maintained
        assert len(ada.conversation.messages) == 4

    def test_ada_with_memory(self):
        """Test Ada with memory operations."""
        config = AdaConfig(enable_memory=True)
        ada = Ada(config)

        # Remember something
        ada.remember("user_preference", "dark_mode", verified=True)

        # Recall it
        results = ada.recall("preference")
        assert len(results) > 0
        assert results[0].value == "dark_mode"

    def test_ada_research_to_memory(self):
        """Test research results stored in memory."""
        config = AdaConfig(enable_memory=True, enable_research=True)
        ada = Ada(config)

        # Research should populate memory with verified facts
        report = ada.research("test topic")
        assert report is not None

    def test_ada_agent_with_tools(self):
        """Test agent using available tools."""
        config = AdaConfig(enable_agent=True)
        ada = Ada(config)

        result = ada.agent("Search for information about Python")
        assert result is not None
        assert len(result.actions) > 0

    def test_ada_canvas_code_generation(self):
        """Test canvas code generation and verification."""
        config = AdaConfig(enable_canvas=True)
        ada = Ada(config)

        doc = ada.canvas("Create a Python function to add two numbers")
        assert doc is not None
        assert doc.canvas_type == CanvasType.CODE

    def test_ada_code_execution(self):
        """Test code execution through Ada."""
        config = AdaConfig(enable_code_execution=True)
        ada = Ada(config)

        result = ada.execute("print('Hello from Ada!')")
        assert result.success is True
        assert "Hello from Ada!" in result.stdout

    def test_ada_disabled_features(self):
        """Test that disabled features raise errors."""
        config = AdaConfig(
            enable_research=False,
            enable_agent=False,
            enable_canvas=False,
        )
        ada = Ada(config)

        with pytest.raises(RuntimeError):
            ada.research("test")

        with pytest.raises(RuntimeError):
            ada.agent("test")

        with pytest.raises(RuntimeError):
            ada.canvas("test")

    def test_ada_export_import_conversation(self):
        """Test conversation export and import."""
        ada = Ada()
        ada.chat("Test message 1")
        ada.chat("Test message 2")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            ada.export_conversation(filepath)

            # Create new Ada and import
            ada2 = Ada()
            ada2.import_conversation(filepath)

            assert len(ada2.conversation.messages) == len(ada.conversation.messages)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
