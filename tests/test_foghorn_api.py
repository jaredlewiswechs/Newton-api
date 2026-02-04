"""
═══════════════════════════════════════════════════════════════════════════════
FOGHORN API TESTS
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from foghorn import mount_foghorn_api, get_object_store
from foghorn.objects import ObjectType


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def app():
    """Create FastAPI app with Foghorn routes."""
    _app = FastAPI()
    mount_foghorn_api(_app)
    return _app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_store():
    """Clear object store between tests."""
    store = get_object_store()
    store._objects.clear()
    store._by_type = {t: [] for t in ObjectType}
    yield


# ═══════════════════════════════════════════════════════════════════════════════
# CARD API TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCardAPI:
    """Test Card endpoints."""
    
    def test_list_cards_empty(self, client):
        """List cards when empty."""
        response = client.get("/foghorn/cards")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["data"] == []
        assert data["elapsed_us"] > 0
    
    def test_create_card(self, client):
        """Create a card."""
        response = client.post("/foghorn/cards", json={
            "title": "Test Card",
            "content": "This is test content",
            "tags": ["test", "api"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["title"] == "Test Card"
        assert data["data"]["content"] == "This is test content"
        assert data["data"]["tags"] == ["test", "api"]
        assert "hash" in data["data"]
    
    def test_get_card(self, client):
        """Get a card by ID."""
        # Create first
        create_resp = client.post("/foghorn/cards", json={
            "title": "Retrievable",
            "content": "Find me"
        })
        card_id = create_resp.json()["data"]["id"]
        
        # Get by ID
        response = client.get(f"/foghorn/cards/{card_id}")
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Retrievable"
    
    def test_get_card_by_hash(self, client):
        """Get a card by full hash."""
        # Create first
        create_resp = client.post("/foghorn/cards", json={
            "title": "By Hash",
            "content": "Find me"
        })
        card_hash = create_resp.json()["data"]["hash"]
        
        # Get by hash
        response = client.get(f"/foghorn/cards/{card_hash}")
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "By Hash"
    
    def test_get_card_not_found(self, client):
        """404 for non-existent card."""
        response = client.get("/foghorn/cards/nonexistent")
        assert response.status_code == 404
    
    def test_update_card(self, client):
        """Update a card."""
        # Create
        create_resp = client.post("/foghorn/cards", json={
            "title": "Original",
            "content": "Original content"
        })
        card_id = create_resp.json()["data"]["id"]
        
        # Update
        response = client.put(f"/foghorn/cards/{card_id}", json={
            "title": "Updated",
            "content": "New content"
        })
        
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated"
        assert response.json()["data"]["content"] == "New content"
    
    def test_delete_card(self, client):
        """Delete a card."""
        # Create
        create_resp = client.post("/foghorn/cards", json={
            "title": "To Delete",
            "content": "Gone soon"
        })
        card_id = create_resp.json()["data"]["id"]
        
        # Delete
        response = client.delete(f"/foghorn/cards/{card_id}")
        assert response.status_code == 200
        assert response.json()["success"] == True
        
        # Verify gone
        get_resp = client.get(f"/foghorn/cards/{card_id}")
        assert get_resp.status_code == 404
    
    def test_list_cards_with_filter(self, client):
        """List cards filtered by tag."""
        # Create some cards
        client.post("/foghorn/cards", json={
            "title": "Tagged",
            "content": "Has the tag",
            "tags": ["special"]
        })
        client.post("/foghorn/cards", json={
            "title": "Not Tagged",
            "content": "No special tag"
        })
        
        # Filter by tag
        response = client.get("/foghorn/cards?tag=special")
        assert response.status_code == 200
        
        cards = response.json()["data"]
        assert len(cards) == 1
        assert cards[0]["title"] == "Tagged"


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE API TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestServiceAPI:
    """Test Service endpoints."""
    
    def test_list_services(self, client):
        """List available services."""
        response = client.get("/foghorn/services")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert len(data["data"]) > 0
        
        # Check structure
        service = data["data"][0]
        assert "name" in service
        assert "description" in service
        assert "category" in service
    
    def test_run_echo_service(self, client):
        """Run Echo service on a card."""
        # Create card
        create_resp = client.post("/foghorn/cards", json={
            "title": "Echo Me",
            "content": "Echo this content"
        })
        card_hash = create_resp.json()["data"]["hash"]
        
        # Run service
        response = client.post("/foghorn/services/run", json={
            "service_name": "Echo",
            "object_hash": card_hash
        })
        
        assert response.status_code == 200
        assert response.json()["success"] == True
    
    def test_run_service_not_found_object(self, client):
        """Service fails for non-existent object."""
        response = client.post("/foghorn/services/run", json={
            "service_name": "Echo",
            "object_hash": "nonexistent"
        })
        
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY API TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestQueryAPI:
    """Test Query endpoint."""
    
    def test_execute_query(self, client):
        """Execute a query creates a query object."""
        response = client.post("/foghorn/query", json={
            "text": "What is Newton?"
        })
        
        assert response.status_code == 200
        data = response.json()
        # Query itself is created successfully even if service fails
        assert "query" in data["data"]
        assert data["data"]["query"]["text"] == "What is Newton?"


# ═══════════════════════════════════════════════════════════════════════════════
# INSPECTOR API TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInspectorAPI:
    """Test Inspector endpoint."""
    
    def test_inspect_card(self, client):
        """Inspect a card."""
        # Create card
        create_resp = client.post("/foghorn/cards", json={
            "title": "Inspect Me",
            "content": "Content here"
        })
        card_id = create_resp.json()["data"]["id"]
        
        # Inspect
        response = client.get(f"/foghorn/inspect/{card_id}")
        assert response.status_code == 200
        
        data = response.json()["data"]
        assert "object" in data
        assert "tabs" in data
    
    def test_inspect_not_found(self, client):
        """404 for non-existent object."""
        response = client.get("/foghorn/inspect/nonexistent")
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# WORKSPACE API TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestWorkspaceAPI:
    """Test Workspace endpoints."""
    
    def test_workspace_stats_empty(self, client):
        """Get stats for empty workspace."""
        response = client.get("/foghorn/workspace")
        assert response.status_code == 200
        
        data = response.json()["data"]
        assert data["total_objects"] == 0
        assert "by_type" in data
    
    def test_workspace_stats_with_objects(self, client):
        """Get stats after adding objects."""
        # Add some cards
        client.post("/foghorn/cards", json={"title": "A", "content": "1"})
        client.post("/foghorn/cards", json={"title": "B", "content": "2"})
        
        response = client.get("/foghorn/workspace")
        data = response.json()["data"]
        
        assert data["total_objects"] == 2
        assert data["by_type"]["card"] == 2
    
    def test_undo_redo(self, client):
        """Test undo/redo endpoints."""
        # These just need to return without error
        undo_resp = client.post("/foghorn/undo")
        assert undo_resp.status_code == 200
        
        redo_resp = client.post("/foghorn/redo")
        assert redo_resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# LINK API TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestLinkAPI:
    """Test Link endpoints."""
    
    def test_create_link(self, client):
        """Create a link between cards."""
        # Create two cards
        card1 = client.post("/foghorn/cards", json={
            "title": "Source",
            "content": "From here"
        }).json()["data"]
        
        card2 = client.post("/foghorn/cards", json={
            "title": "Target",
            "content": "To here"
        }).json()["data"]
        
        # Create link
        response = client.post("/foghorn/links", json={
            "source_hash": card1["hash"],
            "target_hash": card2["hash"],
            "relationship": "references"
        })
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["source_hash"] == card1["hash"]
        assert data["target_hash"] == card2["hash"]
        assert data["relationship"] == "references"
    
    def test_list_links(self, client):
        """List links."""
        # Create cards and link
        card1 = client.post("/foghorn/cards", json={
            "title": "A", "content": "1"
        }).json()["data"]
        card2 = client.post("/foghorn/cards", json={
            "title": "B", "content": "2"
        }).json()["data"]
        
        client.post("/foghorn/links", json={
            "source_hash": card1["hash"],
            "target_hash": card2["hash"]
        })
        
        # List
        response = client.get("/foghorn/links")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1
    
    def test_list_links_filtered(self, client):
        """List links with filter."""
        # Create cards
        card1 = client.post("/foghorn/cards", json={
            "title": "A", "content": "1"
        }).json()["data"]
        card2 = client.post("/foghorn/cards", json={
            "title": "B", "content": "2"
        }).json()["data"]
        card3 = client.post("/foghorn/cards", json={
            "title": "C", "content": "3"
        }).json()["data"]
        
        # Create links
        client.post("/foghorn/links", json={
            "source_hash": card1["hash"],
            "target_hash": card2["hash"]
        })
        client.post("/foghorn/links", json={
            "source_hash": card2["hash"],
            "target_hash": card3["hash"]
        })
        
        # Filter by source
        response = client.get(f"/foghorn/links?source={card1['hash']}")
        assert len(response.json()["data"]) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TINYTALK API TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTinyTalkAPI:
    """Test TinyTalk endpoint."""
    
    def test_run_simple_code(self, client):
        """Run simple TinyTalk code."""
        response = client.post("/foghorn/tinytalk", json={
            "code": "2 + 3"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["result"] == 5
    
    def test_run_foghorn_code(self, client):
        """Run TinyTalk code using Foghorn builtins."""
        response = client.post("/foghorn/tinytalk", json={
            "code": '''
                let card = Card.new("API Test", "Created via API")
                card["title"]
            '''
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["result"] == "API Test"
    
    def test_run_invalid_code(self, client):
        """Handle invalid TinyTalk code."""
        response = client.post("/foghorn/tinytalk", json={
            "code": "this is not valid code !!!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert data["error"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
