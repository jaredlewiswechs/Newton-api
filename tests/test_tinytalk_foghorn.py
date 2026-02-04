"""
═══════════════════════════════════════════════════════════════════════════════
TINYTALK + FOGHORN INTEGRATION TESTS
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from realTinyTalk.runtime import Runtime, TinyFunction
from realTinyTalk.parser import Parser
from realTinyTalk.lexer import Lexer
from realTinyTalk.types import Value, ValueType
from realTinyTalk.foghorn_stdlib import register_foghorn_stdlib, FOGHORN_BUILTINS

from foghorn import get_object_store, Card


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def runtime():
    """Create a TinyTalk runtime with Foghorn stdlib."""
    rt = Runtime()
    register_foghorn_stdlib(rt)
    return rt


@pytest.fixture(autouse=True)
def clear_store():
    """Clear object store between tests."""
    from foghorn.objects import ObjectType
    store = get_object_store()
    store._objects.clear()
    # Reset _by_type to empty lists
    store._by_type = {t: [] for t in ObjectType}
    yield


def run_tinytalk(runtime, code: str) -> Value:
    """Parse and run TinyTalk code."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    return runtime.execute(ast)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestFoghornRegistration:
    """Test that Foghorn builtins are registered correctly."""
    
    def test_all_builtins_defined(self):
        """All expected builtins exist."""
        expected = [
            'Card.new', 'Card.get', 'Card.all',
            'Query.new',
            'Services.list', 'Services.run', 'Services.find_for',
            'inspect',
            'undo', 'redo', 'history',
            'Workspace.count', 'Workspace.all', 'Workspace.delete',
            'Link.new',
        ]
        
        for name in expected:
            assert name in FOGHORN_BUILTINS, f"Missing builtin: {name}"
    
    def test_register_with_runtime(self, runtime):
        """Foghorn builtins register with runtime."""
        # Check namespaces exist
        card_ns = runtime.global_scope.get('Card')
        assert card_ns is not None
        assert card_ns.type == ValueType.MAP
        
        # Check simple functions
        undo_fn = runtime.global_scope.get('undo')
        assert undo_fn is not None
        assert undo_fn.type == ValueType.FUNCTION


# ═══════════════════════════════════════════════════════════════════════════════
# CARD TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCardOperations:
    """Test Card operations from TinyTalk."""
    
    def test_card_new_basic(self, runtime):
        """Create a card with title and content."""
        result = run_tinytalk(runtime, '''
            let card = Card.new("My Note", "This is the content")
            card
        ''')
        
        assert result.type == ValueType.MAP
        assert "title" in result.data
        assert result.data["title"].data == "My Note"
        assert result.data["content"].data == "This is the content"
    
    def test_card_new_with_tags(self, runtime):
        """Create a card with tags."""
        result = run_tinytalk(runtime, '''
            let card = Card.new("Tagged Note", "Content", ["work", "urgent"])
            card
        ''')
        
        assert result.type == ValueType.MAP
        assert "tags" in result.data
        tags = result.data["tags"]
        assert tags.type == ValueType.LIST
        assert len(tags.data) == 2
    
    def test_card_get_by_hash(self, runtime):
        """Get a card by its hash."""
        result = run_tinytalk(runtime, '''
            let card = Card.new("Test", "Content")
            let h = card["hash"]
            let retrieved = Card.get(h)
            retrieved
        ''')
        
        assert result.type == ValueType.MAP
        assert result.data["title"].data == "Test"
    
    def test_card_all(self, runtime):
        """Get all cards."""
        result = run_tinytalk(runtime, '''
            Card.new("Card 1", "Content 1")
            Card.new("Card 2", "Content 2")
            let cards = Card.all()
            cards
        ''')
        
        assert result.type == ValueType.LIST
        assert len(result.data) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestQueryOperations:
    """Test Query operations from TinyTalk."""
    
    def test_query_new_basic(self, runtime):
        """Create a simple query."""
        result = run_tinytalk(runtime, '''
            let q = Query.new("What is Newton?")
            q
        ''')
        
        assert result.type == ValueType.MAP
        assert "text" in result.data
        assert result.data["text"].data == "What is Newton?"
    
    def test_query_new_with_filters(self, runtime):
        """Create a query with filters."""
        result = run_tinytalk(runtime, '''
            let q = Query.new("search term", {"type": "card", "limit": 10})
            q
        ''')
        
        assert result.type == ValueType.MAP
        assert "filters" in result.data


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestServiceOperations:
    """Test Service operations from TinyTalk."""
    
    def test_services_list(self, runtime):
        """List all services."""
        result = run_tinytalk(runtime, '''
            let services = Services.list()
            services
        ''')
        
        assert result.type == ValueType.LIST
        assert len(result.data) > 0
        
        # Each service should have name, description, category
        service = result.data[0]
        assert "name" in service.data
        assert "description" in service.data
    
    def test_services_find_for_card(self, runtime):
        """Find services for card type."""
        result = run_tinytalk(runtime, '''
            let services = Services.find_for("card")
            services
        ''')
        
        assert result.type == ValueType.LIST
    
    def test_services_run_echo(self, runtime):
        """Run echo service on a card."""
        result = run_tinytalk(runtime, '''
            let card = Card.new("Test", "Hello World")
            let result = Services.run("Echo", card)
            result
        ''')
        
        assert result.type == ValueType.MAP
        assert "success" in result.data
        assert result.data["success"].data == True


# ═══════════════════════════════════════════════════════════════════════════════
# WORKSPACE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestWorkspaceOperations:
    """Test Workspace operations from TinyTalk."""
    
    def test_workspace_count(self, runtime):
        """Get workspace object count."""
        result = run_tinytalk(runtime, '''
            Workspace.count()
        ''')
        
        assert result.type == ValueType.INT
        assert result.data == 0
    
    def test_workspace_count_after_add(self, runtime):
        """Count increases when adding objects."""
        result = run_tinytalk(runtime, '''
            Card.new("Test", "Content")
            Workspace.count()
        ''')
        
        assert result.data == 1
    
    def test_workspace_all(self, runtime):
        """Get all workspace objects."""
        result = run_tinytalk(runtime, '''
            Card.new("A", "1")
            Card.new("B", "2")
            Workspace.all()
        ''')
        
        assert result.type == ValueType.LIST
        assert len(result.data) == 2
    
    def test_workspace_delete(self, runtime):
        """Delete an object from workspace."""
        result = run_tinytalk(runtime, '''
            let card = Card.new("To Delete", "Content")
            let h = card["hash"]
            Workspace.delete(h)
            Workspace.count()
        ''')
        
        assert result.data == 0


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND BUS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCommandBus:
    """Test undo/redo from TinyTalk."""
    
    def test_undo_returns_bool(self, runtime):
        """Undo returns boolean."""
        result = run_tinytalk(runtime, '''
            undo()
        ''')
        
        assert result.type == ValueType.BOOLEAN
    
    def test_redo_returns_bool(self, runtime):
        """Redo returns boolean."""
        result = run_tinytalk(runtime, '''
            redo()
        ''')
        
        assert result.type == ValueType.BOOLEAN
    
    def test_history(self, runtime):
        """Get command history."""
        result = run_tinytalk(runtime, '''
            history()
        ''')
        
        assert result.type == ValueType.LIST


# ═══════════════════════════════════════════════════════════════════════════════
# INSPECTOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInspector:
    """Test object inspection from TinyTalk."""
    
    def test_inspect_card(self, runtime):
        """Inspect a card object."""
        result = run_tinytalk(runtime, '''
            let card = Card.new("Inspectable", "Inspect me")
            inspect(card)
        ''')
        
        assert result.type == ValueType.MAP
        assert "object" in result.data


# ═══════════════════════════════════════════════════════════════════════════════
# LINK TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestLinkOperations:
    """Test Link operations from TinyTalk."""
    
    def test_link_new(self, runtime):
        """Create a link between cards."""
        result = run_tinytalk(runtime, '''
            let card1 = Card.new("Source", "From here")
            let card2 = Card.new("Target", "To here")
            let link = Link.new(card1["hash"], card2["hash"])
            link
        ''')
        
        assert result.type == ValueType.MAP
        assert "source_hash" in result.data
        assert "target_hash" in result.data
    
    def test_link_with_relationship(self, runtime):
        """Create a link with custom relationship."""
        result = run_tinytalk(runtime, '''
            let card1 = Card.new("Paper", "Research")
            let card2 = Card.new("Reference", "Citation")
            let link = Link.new(card1["hash"], card2["hash"], "cites")
            link
        ''')
        
        assert result.data["relationship"].data == "cites"


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """End-to-end integration tests."""
    
    def test_full_workflow(self, runtime):
        """Complete workflow: create, link, inspect, query."""
        result = run_tinytalk(runtime, '''
            // Create some cards
            let note1 = Card.new("Newton Laws", "F=ma and friends", ["physics"])
            let note2 = Card.new("Calculus", "Derivatives and integrals", ["math"])
            
            // Link them
            Link.new(note1["hash"], note2["hash"], "relates_to")
            
            // Check workspace
            let count = Workspace.count()
            
            // Get all cards
            let cards = Card.all()
            let num_cards = len(cards)
            
            // Return count
            count
        ''')
        
        # 2 cards + 1 link = 3 objects
        assert result.type == ValueType.INT
        assert result.data == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
