#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NINA DESKTOP — Interactive Test Suite
═══════════════════════════════════════════════════════════════════════════════

Tests the claimed user interactions:
1. Search → results
2. Create card
3. View in inspector
4. Run service
5. Drop into window

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

import sys
import json
import requests
from time import sleep

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/foghorn"

def test_get_cards():
    """Test: Can list all cards."""
    print("TEST 1: Get all cards...")
    r = requests.get(f"{API_URL}/cards")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "cards" in data, "Response missing 'cards'"
    print(f"   ✓ Found {len(data['cards'])} cards")
    return data["cards"]


def test_create_card():
    """Test: Can create a new card."""
    print("TEST 2: Create new card...")
    payload = {
        "title": "Test Card from API",
        "content": "This card was created by the test suite.",
        "tags": ["test", "automated"]
    }
    r = requests.post(f"{API_URL}/cards", json=payload)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data.get("success"), "Create card failed"
    assert "card" in data, "Response missing 'card'"
    card = data["card"]
    print(f"   ✓ Created card: {card['title']} (ID: {card['id']})")
    return card


def test_get_all_objects():
    """Test: Can list all objects (cards, queries, map places)."""
    print("TEST 3: Get all objects...")
    r = requests.get(f"{API_URL}/objects")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "objects" in data, "Response missing 'objects'"
    
    # Count by type
    type_counts = {}
    for obj in data["objects"]:
        t = obj.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"   ✓ Found {len(data['objects'])} objects:")
    for t, count in sorted(type_counts.items()):
        print(f"      - {t}: {count}")
    return data["objects"]


def test_get_single_object(obj_id: str):
    """Test: Can fetch a single object by ID."""
    print(f"TEST 4: Get object by ID ({obj_id[:8]}...)...")
    r = requests.get(f"{API_URL}/object/{obj_id}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "object" in data, "Response missing 'object'"
    obj = data["object"]
    print(f"   ✓ Retrieved: {obj.get('title', obj.get('name', obj_id))}")
    return obj


def test_create_query():
    """Test: Can create a query."""
    print("TEST 5: Create query...")
    payload = {"text": "What is the capital of Texas?"}
    r = requests.post(f"{API_URL}/query", json=payload)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data.get("success"), "Create query failed"
    assert "query" in data, "Response missing 'query'"
    print(f"   ✓ Created query: \"{data['query']['text']}\"")
    return data["query"]


def test_verify_service(obj_id: str):
    """Test: Can run verify service on an object."""
    print(f"TEST 6: Run verify service on {obj_id[:8]}...")
    payload = {"object_id": obj_id}
    r = requests.post(f"{API_URL}/services/verify", json=payload)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data.get("success"), "Verify service failed"
    assert "receipt" in data, "Response missing 'receipt'"
    receipt = data["receipt"]
    print(f"   ✓ Verified! Receipt: {receipt['id'][:8]}...")
    return receipt


def test_static_files():
    """Test: Static files are served correctly."""
    print("TEST 7: Static file serving...")
    
    # HTML
    r = requests.get(f"{BASE_URL}/index.html")
    assert r.status_code == 200, f"index.html: Expected 200, got {r.status_code}"
    assert "Nina Desktop" in r.text, "index.html missing title"
    print("   ✓ index.html served")
    
    # CSS
    r = requests.get(f"{BASE_URL}/desktop.css")
    assert r.status_code == 200, f"desktop.css: Expected 200, got {r.status_code}"
    assert "--bg-desktop" in r.text, "CSS missing variables"
    print("   ✓ desktop.css served")
    
    # JS
    r = requests.get(f"{BASE_URL}/desktop.js")
    assert r.status_code == 200, f"desktop.js: Expected 200, got {r.status_code}"
    assert "initClock" in r.text, "JS missing functions"
    print("   ✓ desktop.js served")


def main():
    """Run all tests."""
    print("\n" + "═" * 60)
    print("NINA DESKTOP — Test Suite")
    print("═" * 60 + "\n")
    
    try:
        # Check server is running
        requests.get(BASE_URL, timeout=1)
    except requests.exceptions.ConnectionError:
        print("❌ Server not running! Start with: python foghorn/shell/server.py")
        sys.exit(1)
    
    try:
        # Run tests
        test_static_files()
        print()
        
        cards = test_get_cards()
        print()
        
        new_card = test_create_card()
        print()
        
        objects = test_get_all_objects()
        print()
        
        if objects:
            test_get_single_object(objects[0]["id"])
        print()
        
        query = test_create_query()
        print()
        
        if cards:
            test_verify_service(cards[0]["id"])
        print()
        
        print("═" * 60)
        print("✅ ALL TESTS PASSED")
        print("═" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
