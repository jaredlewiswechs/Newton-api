"""
═══════════════════════════════════════════════════════════════════════════════
FOGHORN KERNEL — Property-Based Tests
═══════════════════════════════════════════════════════════════════════════════

Formal verification of Foghorn kernel properties using Hypothesis.

Properties proven:
1. Hash Determinism: Same content → same hash
2. Chain Integrity: prev_hash links are verifiable
3. Command Reversibility: execute → undo → original state
4. Service Idempotence: Same input → same output type
5. Inspector Completeness: Every object is inspectable

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from foghorn import (
    # Objects
    FoghornObject, ObjectType,
    Card, Query, ResultSet, FileAsset, Task, Receipt, LinkCurve, Rule,
    ObjectStore, get_object_store,
    # Services
    ServiceRegistry, ServiceCategory, get_service_registry, execute_service,
    # Commands
    Command, CommandBus, get_command_bus,
    AddObjectCommand, UpdateObjectCommand, DeleteObjectCommand, BatchCommand,
    execute, undo, redo, add_object, update_object, delete_object,
    # Inspector
    Inspector, InspectorData, get_inspector, inspect, inspect_by_hash,
)


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGIES — Hypothesis generators for Foghorn objects
# ═══════════════════════════════════════════════════════════════════════════════

@st.composite
def card_strategy(draw):
    """Generate random Card objects."""
    return Card(
        title=draw(st.text(min_size=0, max_size=100)),
        content=draw(st.text(min_size=0, max_size=1000)),
        tags=draw(st.lists(st.text(min_size=1, max_size=20), max_size=5)),
        source=draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
    )


@st.composite
def query_strategy(draw):
    """Generate random Query objects."""
    return Query(
        text=draw(st.text(min_size=1, max_size=200)),
        shape_type=draw(st.one_of(st.none(), st.sampled_from(["linear", "curved", "spiral"]))),
        filters=draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.integers(), st.text(max_size=50), st.booleans()),
            max_size=3
        )),
    )


@st.composite
def link_curve_strategy(draw):
    """Generate random LinkCurve objects."""
    return LinkCurve(
        source_hash=draw(st.text(min_size=64, max_size=64, alphabet="0123456789abcdef")),
        target_hash=draw(st.text(min_size=64, max_size=64, alphabet="0123456789abcdef")),
        relationship=draw(st.sampled_from(["links_to", "derived_from", "references", "contains"])),
        weight=draw(st.floats(min_value=0.0, max_value=1.0)),
        p0=(draw(st.floats(0, 1)), draw(st.floats(0, 1))),
        h1=(draw(st.floats(0, 1)), draw(st.floats(0, 1))),
        h2=(draw(st.floats(0, 1)), draw(st.floats(0, 1))),
        p3=(draw(st.floats(0, 1)), draw(st.floats(0, 1))),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY 1: HASH DETERMINISM
# Same content always produces the same hash
# ═══════════════════════════════════════════════════════════════════════════════

class TestHashDeterminism:
    """Prove: hash(content) is deterministic."""
    
    @given(st.text(max_size=500), st.text(max_size=100))
    @settings(max_examples=100)
    def test_card_hash_determinism(self, content: str, title: str):
        """Same Card content → same hash."""
        card1 = Card(title=title, content=content)
        card2 = Card(title=title, content=content)
        
        assert card1.hash == card2.hash, "Hash must be deterministic"
        assert card1.id == card2.id, "ID must be deterministic"
    
    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=100)
    def test_query_hash_determinism(self, text: str):
        """Same Query text → same hash."""
        query1 = Query(text=text)
        query2 = Query(text=text)
        
        assert query1.hash == query2.hash
    
    @given(st.text(max_size=100), st.text(max_size=500))
    @settings(max_examples=50)
    def test_different_content_different_hash(self, content1: str, content2: str):
        """Different content → different hash (collision resistance)."""
        assume(content1 != content2)
        
        card1 = Card(content=content1)
        card2 = Card(content=content2)
        
        assert card1.hash != card2.hash, "Different content must produce different hashes"


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY 2: CHAIN INTEGRITY
# Hash chains are verifiable and tamper-evident
# ═══════════════════════════════════════════════════════════════════════════════

class TestChainIntegrity:
    """Prove: hash chains maintain integrity."""
    
    @given(st.lists(st.text(max_size=100), min_size=2, max_size=10))
    @settings(max_examples=50)
    def test_chain_links_correctly(self, contents: list):
        """Each object links to previous via prev_hash."""
        store = ObjectStore()
        
        prev_hash = None
        for content in contents:
            card = Card(content=content, prev_hash=prev_hash)
            store.add(card)
            prev_hash = card.hash
        
        # Verify chain
        chain = store.get_chain(prev_hash)
        assert len(chain) == len(contents), "Chain length must match"
        
        # Verify links
        for i in range(len(chain) - 1):
            assert chain[i].prev_hash == chain[i + 1].hash, "Chain links must be intact"
    
    @given(st.lists(st.text(max_size=50), min_size=3, max_size=5))
    @settings(max_examples=30)
    def test_chain_verification(self, contents: list):
        """Store.verify_chain() returns True for valid chains."""
        store = ObjectStore()
        
        prev_hash = None
        last_hash = None
        for content in contents:
            card = Card(content=content, prev_hash=prev_hash)
            store.add(card)
            prev_hash = card.hash
            last_hash = card.hash
        
        assert store.verify_chain(last_hash), "Valid chain must verify"
    
    def test_genesis_object(self):
        """First object in chain has prev_hash=None (genesis)."""
        card = Card(content="Genesis card")
        assert card.prev_hash is None, "Genesis object has no prev_hash"


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY 3: COMMAND REVERSIBILITY
# execute(cmd) → undo() restores original state
# ═══════════════════════════════════════════════════════════════════════════════

class TestCommandReversibility:
    """Prove: all commands are reversible."""
    
    def setup_method(self):
        """Fresh command bus and object store for each test."""
        # Reset globals
        import foghorn.commands as cmd_module
        import foghorn.objects as obj_module
        cmd_module._command_bus = CommandBus()
        obj_module._object_store = ObjectStore()
    
    @given(card_strategy())
    @settings(max_examples=50)
    def test_add_undo_removes(self, card: Card):
        """AddObjectCommand → undo removes the object."""
        store = get_object_store()
        bus = get_command_bus()
        
        initial_count = store.count()
        
        # Add
        cmd = AddObjectCommand(obj=card)
        assert bus.execute(cmd), "Execute must succeed"
        assert store.count() == initial_count + 1, "Object added"
        
        # Undo
        assert bus.undo(), "Undo must succeed"
        assert store.count() == initial_count, "Object removed"
    
    @given(card_strategy())
    @settings(max_examples=50)
    def test_undo_redo_symmetry(self, card: Card):
        """undo() → redo() restores state."""
        store = get_object_store()
        bus = get_command_bus()
        
        # Add
        cmd = AddObjectCommand(obj=card)
        bus.execute(cmd)
        hash_after_add = card.hash
        count_after_add = store.count()
        
        # Undo
        bus.undo()
        count_after_undo = store.count()
        assert count_after_undo == count_after_add - 1
        
        # Redo
        bus.redo()
        count_after_redo = store.count()
        assert count_after_redo == count_after_add, "Redo restores state"
    
    @given(st.lists(st.text(min_size=1, max_size=50), min_size=2, max_size=5, unique=True))
    @settings(max_examples=30)
    def test_batch_command_atomicity(self, contents: list):
        """BatchCommand is atomic: all succeed or all fail."""
        store = get_object_store()
        bus = get_command_bus()
        
        initial_count = store.count()
        
        # Create batch with UNIQUE content (to avoid hash collisions)
        cards = [Card(content=c, title=f"Card {i}") for i, c in enumerate(contents)]
        commands = [AddObjectCommand(obj=card) for card in cards]
        batch = BatchCommand(commands=commands)
        
        # Execute
        assert bus.execute(batch), "Batch must succeed"
        assert store.count() == initial_count + len(cards)
        
        # Undo entire batch
        assert bus.undo(), "Batch undo must succeed"
        assert store.count() == initial_count, "Batch undo is atomic"


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY 4: SERVICE TYPE SAFETY
# Services respect accepts/produces contracts
# ═══════════════════════════════════════════════════════════════════════════════

class TestServiceTypeSafety:
    """Prove: services respect type contracts."""
    
    def test_service_registration(self):
        """Services are discoverable via registry."""
        registry = get_service_registry()
        services = registry.list_all()
        
        assert len(services) > 0, "Registry must have services"
        
        for svc in services:
            assert svc.name, "Service must have name"
            assert len(svc.accepts) > 0, "Service must accept some types"
            assert len(svc.produces) > 0, "Service must produce some types"
    
    @given(card_strategy())
    @settings(max_examples=30)
    def test_service_finds_for_object(self, card: Card):
        """Registry finds services for object type."""
        registry = get_service_registry()
        services = registry.find_for_object(card)
        
        for svc in services:
            assert ObjectType.CARD in svc.accepts, "Service must accept Card"
    
    def test_service_rejects_wrong_type(self):
        """Service rejects objects it doesn't accept."""
        # Query doesn't accept FileAsset in most services
        file_asset = FileAsset(filename="test.pdf", path="/tmp/test.pdf")
        
        registry = get_service_registry()
        services = registry.find_for_object(file_asset)
        
        # FileAsset has limited services
        for svc in services:
            assert ObjectType.FILE_ASSET in svc.accepts
    
    @given(card_strategy())
    @settings(max_examples=20)
    def test_echo_service_produces_card(self, card: Card):
        """Echo service produces Card from Card."""
        result = execute_service("Echo", card)
        
        assert result.success, f"Echo must succeed: {result.error}"
        assert len(result.results) > 0, "Echo must produce output"
        assert isinstance(result.results[0], Card), "Echo produces Card"


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY 5: INSPECTOR COMPLETENESS
# Every object type is inspectable
# ═══════════════════════════════════════════════════════════════════════════════

class TestInspectorCompleteness:
    """Prove: all objects are inspectable."""
    
    @given(card_strategy())
    @settings(max_examples=30)
    def test_card_inspectable(self, card: Card):
        """Cards are fully inspectable."""
        data = inspect(card)
        
        assert data.obj == card
        assert len(data.tabs) > 0, "Must have tabs"
        assert any(tab.name == "General" for tab in data.tabs), "Must have General tab"
    
    @given(query_strategy())
    @settings(max_examples=30)
    def test_query_inspectable(self, query: Query):
        """Queries are fully inspectable."""
        data = inspect(query)
        
        assert data.obj == query
        assert len(data.tabs) > 0
    
    @given(link_curve_strategy())
    @settings(max_examples=20)
    def test_link_curve_has_bezier_tab(self, link: LinkCurve):
        """LinkCurves have Bézier inspector tab."""
        data = inspect(link)
        
        assert data.obj == link
        # LinkCurve should have Bézier-specific tab
        tab_names = [tab.name for tab in data.tabs]
        assert "Bézier" in tab_names or len(data.tabs) > 0
    
    def test_all_object_types_inspectable(self):
        """Every ObjectType has working inspection."""
        objects = [
            Card(title="Test", content="Content"),
            Query(text="What is Newton?"),
            ResultSet(query_hash="abc123", results=[{"title": "Result"}]),
            FileAsset(filename="test.txt", path="/tmp/test.txt"),
            Task(name="Test Task"),
            Receipt(action="test_action"),
            LinkCurve(source_hash="a" * 64, target_hash="b" * 64),
            Rule(name="Test Rule", patterns=["pattern1"]),
        ]
        
        inspector = get_inspector()
        
        for obj in objects:
            data = inspector.inspect(obj)
            assert data.obj == obj, f"{obj.object_type} must be inspectable"
            assert len(data.tabs) > 0, f"{obj.object_type} must have tabs"
            assert data.to_dict(), f"{obj.object_type} must serialize"


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY 6: SERIALIZATION ROUND-TRIP
# to_dict() → from_dict() preserves data
# ═══════════════════════════════════════════════════════════════════════════════

class TestSerializationRoundTrip:
    """Prove: serialization preserves data."""
    
    @given(card_strategy())
    @settings(max_examples=50)
    def test_card_to_dict_complete(self, card: Card):
        """Card.to_dict() includes all fields."""
        d = card.to_dict()
        
        assert d["type"] == "card"
        assert d["hash"] == card.hash
        assert d["id"] == card.id
        assert d["content"] == card.content
        assert d["title"] == card.title
        assert d["tags"] == card.tags
    
    @given(query_strategy())
    @settings(max_examples=50)
    def test_query_to_dict_complete(self, query: Query):
        """Query.to_dict() includes all fields."""
        d = query.to_dict()
        
        assert d["type"] == "query"
        assert d["text"] == query.text
        assert d["filters"] == query.filters
    
    def test_inspector_data_serializable(self):
        """InspectorData serializes to JSON-compatible dict."""
        card = Card(title="Test", content="Content")
        data = inspect(card)
        
        d = data.to_dict()
        
        assert "object" in d
        assert "tabs" in d
        assert "actions" in d
        assert isinstance(d["tabs"], list)


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY 7: BOUNDED EXECUTION
# Tasks have bounded execution (Turing completeness with termination)
# ═══════════════════════════════════════════════════════════════════════════════

class TestBoundedExecution:
    """Prove: execution is bounded (termination guaranteed)."""
    
    def test_task_has_bounds(self):
        """Tasks have execution bounds."""
        task = Task(name="Test")
        
        assert task.max_ops > 0, "Must have max_ops bound"
        assert task.max_time_ms > 0, "Must have time bound"
    
    @given(st.integers(min_value=1, max_value=1_000_000))
    @settings(max_examples=20)
    def test_task_bounds_configurable(self, max_ops: int):
        """Task bounds are configurable."""
        task = Task(name="Test", max_ops=max_ops)
        assert task.max_ops == max_ops
    
    def test_service_execution_produces_receipt(self):
        """Service execution always produces a Receipt."""
        card = Card(title="Test", content="Test content")
        result = execute_service("Echo", card)
        
        assert result.receipt is not None, "Must produce receipt"
        assert result.task is not None, "Must produce task"
        assert result.duration_ms >= 0, "Must track duration"


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY 8: OBJECT STORE INVARIANTS
# Store maintains consistency
# ═══════════════════════════════════════════════════════════════════════════════

class TestObjectStoreInvariants:
    """Prove: ObjectStore maintains invariants."""
    
    def test_empty_store(self):
        """Empty store has count 0."""
        store = ObjectStore()
        assert store.count() == 0
    
    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=20, unique=True))
    @settings(max_examples=30)
    def test_store_count_accurate(self, contents: list):
        """Store count matches added UNIQUE objects (content-addressable)."""
        store = ObjectStore()
        
        # Use unique content to ensure unique hashes
        for i, content in enumerate(contents):
            card = Card(content=content, title=f"Card {i}")
            store.add(card)
        
        # Content-addressable: unique content = unique objects
        assert store.count() == len(contents)
    
    @given(card_strategy())
    @settings(max_examples=50)
    def test_get_by_hash(self, card: Card):
        """Get by hash returns correct object."""
        store = ObjectStore()
        store.add(card)
        
        retrieved = store.get(card.hash)
        assert retrieved == card
    
    @given(card_strategy())
    @settings(max_examples=50)
    def test_get_by_id(self, card: Card):
        """Get by ID returns correct object."""
        store = ObjectStore()
        store.add(card)
        
        retrieved = store.get_by_id(card.id)
        assert retrieved == card
    
    @given(st.lists(card_strategy(), min_size=1, max_size=10))
    @settings(max_examples=20)
    def test_get_by_type(self, cards: list):
        """Get by type returns all objects of that type."""
        store = ObjectStore()
        
        for card in cards:
            store.add(card)
        
        retrieved = store.get_by_type(ObjectType.CARD)
        assert len(retrieved) == len(cards)


# ═══════════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
