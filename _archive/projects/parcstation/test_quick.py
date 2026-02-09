"""
Quick test for parcStation - runs server inline
"""

import os
import sys
import asyncio
import threading
import time

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))

from server import app, notebooks, Notebook, Stack, Card, Cartridge
from fastapi.testclient import TestClient

def test_parcstation():
    """Test parcStation with TestClient (no server needed)"""
    
    print("""
    ═══════════════════════════════════════════════════════════════════════════════
    
        ◈ parcStation Test Suite
        "Built on proof"
        
    ═══════════════════════════════════════════════════════════════════════════════
    """)
    
    client = TestClient(app)
    passed = 0
    failed = 0
    
    def test(name, condition):
        nonlocal passed, failed
        if condition:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")
            failed += 1
    
    # ─────────────────────────────────────────────────────────────────
    print("\n  ─────────────────────────────────────────────────────────────")
    print("  BASIC ENDPOINTS")
    print("  ─────────────────────────────────────────────────────────────")
    
    # Test index
    resp = client.get("/")
    test("GET / (homepage)", resp.status_code == 200 and "parcStation" in resp.text)
    
    # Test info
    resp = client.get("/api/info")
    test("GET /api/info", resp.status_code == 200 and resp.json().get("name") == "parcStation")
    
    # Test cartridges list
    resp = client.get("/api/cartridges/available")
    data = resp.json()
    test("GET /api/cartridges/available", resp.status_code == 200 and len(data) >= 8)
    
    # ─────────────────────────────────────────────────────────────────
    print("\n  ─────────────────────────────────────────────────────────────")
    print("  NOTEBOOK CRUD")
    print("  ─────────────────────────────────────────────────────────────")
    
    # Create notebook
    resp = client.post("/api/notebook", json={"name": "Test Notebook"})
    data = resp.json()
    notebook_id = data.get("id")
    test("POST /api/notebook (create)", resp.status_code == 200 and notebook_id)
    
    # Get notebook
    resp = client.get(f"/api/notebook/{notebook_id}")
    test("GET /api/notebook/{id}", resp.status_code == 200 and resp.json().get("name") == "Test Notebook")
    
    # List notebooks
    resp = client.get("/api/notebooks")
    test("GET /api/notebooks", resp.status_code == 200 and any(n["id"] == notebook_id for n in resp.json()))
    
    # ─────────────────────────────────────────────────────────────────
    print("\n  ─────────────────────────────────────────────────────────────")
    print("  STACK OPERATIONS")
    print("  ─────────────────────────────────────────────────────────────")
    
    # Add stack
    resp = client.post(f"/api/notebook/{notebook_id}/stack", json={
        "name": "Lewis Family",
        "description": "Genealogy and land records",
        "color": 0x4a9eff
    })
    data = resp.json()
    stack_id = data.get("stack", {}).get("id")
    test("POST /api/notebook/{id}/stack", resp.status_code == 200 and stack_id)
    
    # Get stack
    resp = client.get(f"/api/notebook/{notebook_id}/stack/{stack_id}")
    test("GET /api/notebook/{id}/stack/{sid}", resp.status_code == 200 and resp.json().get("name") == "Lewis Family")
    
    # ─────────────────────────────────────────────────────────────────
    print("\n  ─────────────────────────────────────────────────────────────")
    print("  CARD OPERATIONS")
    print("  ─────────────────────────────────────────────────────────────")
    
    # Add card
    resp = client.post(f"/api/notebook/{notebook_id}/stack/{stack_id}/card", json={
        "claim": "Jasper Lewis owned 200 acres in Brazoria County in 1857",
        "sources": [{"type": "document", "location": "Texas GLO Patent #4521", "verified": True}]
    })
    test("POST /api/notebook/{id}/stack/{sid}/card", resp.status_code == 200)
    
    # Add quick card
    resp = client.post(f"/api/notebook/{notebook_id}/quick-card", json={
        "claim": "Need to verify: Great-grandfather's military service"
    })
    test("POST /api/notebook/{id}/quick-card", resp.status_code == 200)
    
    # ─────────────────────────────────────────────────────────────────
    print("\n  ─────────────────────────────────────────────────────────────")
    print("  CARTRIDGE OPERATIONS")
    print("  ─────────────────────────────────────────────────────────────")
    
    # Add cartridge
    resp = client.post(f"/api/notebook/{notebook_id}/cartridge", json={
        "type": "voicepath",
        "name": "VoicePath Player",
        "position": {"x": 10, "y": 0, "z": 5}
    })
    data = resp.json()
    test("POST /api/notebook/{id}/cartridge", resp.status_code == 200 and data.get("cartridge", {}).get("verified"))
    
    # ─────────────────────────────────────────────────────────────────
    print("\n  ─────────────────────────────────────────────────────────────")
    print("  SEARCH")
    print("  ─────────────────────────────────────────────────────────────")
    
    # Search
    resp = client.post("/api/search", json={"query": "Jasper Lewis"})
    data = resp.json()
    test("POST /api/search", resp.status_code == 200 and data.get("count", 0) >= 1)
    
    # ─────────────────────────────────────────────────────────────────
    print("\n  ─────────────────────────────────────────────────────────────")
    print("  🤖 UI BOT SIMULATION")
    print("  ─────────────────────────────────────────────────────────────")
    
    # Simulate user creating a full workflow
    
    # Bot creates notebook
    resp = client.post("/api/notebook", json={"name": "Bot's Research"})
    bot_notebook_id = resp.json().get("id")
    test("🤖 Bot creates notebook", bot_notebook_id is not None)
    
    # Bot creates stack
    resp = client.post(f"/api/notebook/{bot_notebook_id}/stack", json={
        "name": "Facts to Verify",
        "description": "Bot's test data",
        "color": 0xa855f7
    })
    bot_stack_id = resp.json().get("stack", {}).get("id")
    test("🤖 Bot creates stack", bot_stack_id is not None)
    
    # Bot adds multiple cards
    cards = [
        "The Earth orbits the Sun",
        "Water is H2O",
        "Houston was founded in 1836"
    ]
    for claim in cards:
        resp = client.post(f"/api/notebook/{bot_notebook_id}/stack/{bot_stack_id}/card", json={
            "claim": claim
        })
        test(f"🤖 Bot adds: '{claim[:25]}...'", resp.status_code == 200)
    
    # Bot adds VoicePath cartridge
    resp = client.post(f"/api/notebook/{bot_notebook_id}/cartridge", json={
        "type": "voicepath",
        "name": "Music Viz"
    })
    test("🤖 Bot adds VoicePath cartridge", resp.status_code == 200)
    
    # Bot adds Data cartridge
    resp = client.post(f"/api/notebook/{bot_notebook_id}/cartridge", json={
        "type": "data",
        "name": "Analytics"
    })
    test("🤖 Bot adds Data cartridge", resp.status_code == 200)
    
    # Bot searches
    resp = client.post("/api/search", json={"query": "Earth"})
    test("🤖 Bot searches for 'Earth'", resp.json().get("count", 0) >= 1)
    
    # Bot checks final state
    resp = client.get(f"/api/notebook/{bot_notebook_id}")
    data = resp.json()
    stack_count = len(data.get("stacks", []))
    cartridge_count = len(data.get("cartridges", []))
    card_count = len(data.get("stacks", [{}])[0].get("cards", []))
    test(f"🤖 Bot verifies: {stack_count} stack, {cartridge_count} cartridges, {card_count} cards", 
         stack_count == 1 and cartridge_count == 2 and card_count == 3)
    
    # ─────────────────────────────────────────────────────────────────
    print("\n  ═══════════════════════════════════════════════════════════")
    print(f"  RESULTS: {passed} passed, {failed} failed")
    print("  ═══════════════════════════════════════════════════════════\n")
    
    if failed == 0:
        print("  ✓ ALL TESTS PASSED! parcStation is ready.")
    else:
        print(f"  ⚠️ {failed} test(s) failed.")
    
    return failed == 0


if __name__ == "__main__":
    success = test_parcstation()
    sys.exit(0 if success else 1)
