"""
═══════════════════════════════════════════════════════════════════════════════
PARCSTATION TEST BOT
Automated Testing for the Spatial Notebook

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8080"

# ═══════════════════════════════════════════════════════════════════════════════
# TEST UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_pass(self, name):
        self.passed += 1
        print(f"  ✓ {name}")

    def add_fail(self, name, error=""):
        self.failed += 1
        self.errors.append(f"{name}: {error}")
        print(f"  ✗ {name}: {error}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'═' * 60}")
        print(f"  RESULTS: {self.passed}/{total} passed")
        if self.errors:
            print(f"  ERRORS:")
            for e in self.errors:
                print(f"    - {e}")
        print(f"{'═' * 60}\n")
        return self.failed == 0


def print_section(title):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# ═══════════════════════════════════════════════════════════════════════════════
# API TESTS
# ═══════════════════════════════════════════════════════════════════════════════

async def test_api():
    """Test the parcStation API endpoints."""
    results = TestResult()
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        
        # ─────────────────────────────────────────────────────────────────
        print_section("BASIC ENDPOINTS")
        # ─────────────────────────────────────────────────────────────────
        
        # Test info endpoint
        try:
            resp = await client.get("/api/info")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("name") == "parcStation" and data.get("tagline") == "Built on proof":
                    results.add_pass("GET /api/info")
                else:
                    results.add_fail("GET /api/info", "Missing expected fields")
            else:
                results.add_fail("GET /api/info", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("GET /api/info", str(e))

        # Test available cartridges
        try:
            resp = await client.get("/api/cartridges/available")
            if resp.status_code == 200:
                data = resp.json()
                if len(data) >= 8:  # We have 8 cartridge types
                    cartridge_types = [c["type"] for c in data]
                    if "visual" in cartridge_types and "voicepath" in cartridge_types:
                        results.add_pass("GET /api/cartridges/available")
                    else:
                        results.add_fail("GET /api/cartridges/available", "Missing cartridge types")
                else:
                    results.add_fail("GET /api/cartridges/available", f"Only {len(data)} cartridges")
            else:
                results.add_fail("GET /api/cartridges/available", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("GET /api/cartridges/available", str(e))

        # ─────────────────────────────────────────────────────────────────
        print_section("NOTEBOOK CRUD")
        # ─────────────────────────────────────────────────────────────────

        notebook_id = None

        # Create notebook
        try:
            resp = await client.post("/api/notebook", json={
                "name": "Test Notebook",
                "stacks": [],
                "cartridges": [],
                "quickCards": []
            })
            if resp.status_code == 200:
                data = resp.json()
                notebook_id = data.get("id")
                if notebook_id:
                    results.add_pass("POST /api/notebook (create)")
                else:
                    results.add_fail("POST /api/notebook", "No ID returned")
            else:
                results.add_fail("POST /api/notebook", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("POST /api/notebook", str(e))

        if not notebook_id:
            print("  ⚠️  Skipping remaining tests - no notebook created")
            return results

        # Get notebook
        try:
            resp = await client.get(f"/api/notebook/{notebook_id}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("name") == "Test Notebook":
                    results.add_pass("GET /api/notebook/{id}")
                else:
                    results.add_fail("GET /api/notebook/{id}", "Wrong name")
            else:
                results.add_fail("GET /api/notebook/{id}", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("GET /api/notebook/{id}", str(e))

        # List notebooks
        try:
            resp = await client.get("/api/notebooks")
            if resp.status_code == 200:
                data = resp.json()
                if any(n["id"] == notebook_id for n in data):
                    results.add_pass("GET /api/notebooks (list)")
                else:
                    results.add_fail("GET /api/notebooks", "Created notebook not in list")
            else:
                results.add_fail("GET /api/notebooks", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("GET /api/notebooks", str(e))

        # ─────────────────────────────────────────────────────────────────
        print_section("STACK OPERATIONS")
        # ─────────────────────────────────────────────────────────────────

        stack_id = None

        # Add stack
        try:
            resp = await client.post(f"/api/notebook/{notebook_id}/stack", json={
                "name": "Lewis Family",
                "description": "Genealogy and land records",
                "position": {"x": 0, "y": 0, "z": 0},
                "color": 0x4a9eff,
                "cards": [],
                "constraints": []
            })
            if resp.status_code == 200:
                data = resp.json()
                stack_id = data.get("stack", {}).get("id")
                if stack_id:
                    results.add_pass("POST /api/notebook/{id}/stack")
                else:
                    results.add_fail("POST /api/notebook/{id}/stack", "No stack ID")
            else:
                results.add_fail("POST /api/notebook/{id}/stack", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("POST /api/notebook/{id}/stack", str(e))

        if not stack_id:
            print("  ⚠️  Skipping card tests - no stack created")
            return results

        # Get stack
        try:
            resp = await client.get(f"/api/notebook/{notebook_id}/stack/{stack_id}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("name") == "Lewis Family":
                    results.add_pass("GET /api/notebook/{id}/stack/{sid}")
                else:
                    results.add_fail("GET /api/notebook/{id}/stack/{sid}", "Wrong name")
            else:
                results.add_fail("GET /api/notebook/{id}/stack/{sid}", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("GET /api/notebook/{id}/stack/{sid}", str(e))

        # ─────────────────────────────────────────────────────────────────
        print_section("CARD OPERATIONS")
        # ─────────────────────────────────────────────────────────────────

        # Add card to stack
        try:
            resp = await client.post(f"/api/notebook/{notebook_id}/stack/{stack_id}/card", json={
                "claim": "Jasper Lewis owned 200 acres in Brazoria County in 1857",
                "sources": [
                    {"type": "document", "location": "Texas GLO Patent #4521", "verified": True}
                ],
                "verification": {"status": "draft", "confidence": 0.0}
            })
            if resp.status_code == 200:
                data = resp.json()
                card_id = data.get("card", {}).get("id")
                if card_id:
                    results.add_pass("POST /api/notebook/{id}/stack/{sid}/card")
                else:
                    results.add_fail("POST card to stack", "No card ID")
            else:
                results.add_fail("POST card to stack", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("POST card to stack", str(e))

        # Add quick card
        try:
            resp = await client.post(f"/api/notebook/{notebook_id}/quick-card", json={
                "claim": "Need to verify: Great-grandfather's military service",
                "sources": []
            })
            if resp.status_code == 200:
                results.add_pass("POST /api/notebook/{id}/quick-card")
            else:
                results.add_fail("POST quick-card", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("POST quick-card", str(e))

        # ─────────────────────────────────────────────────────────────────
        print_section("CARTRIDGE OPERATIONS")
        # ─────────────────────────────────────────────────────────────────

        # Add cartridge
        try:
            resp = await client.post(f"/api/notebook/{notebook_id}/cartridge", json={
                "type": "voicepath",
                "name": "VoicePath Player",
                "position": {"x": 10, "y": 0, "z": 5},
                "contract": {
                    "inputs": [{"name": "lyrics", "type": "string"}],
                    "outputs": [{"name": "trajectory", "type": "array"}],
                    "invariants": ["trajectory.length > 0"]
                }
            })
            if resp.status_code == 200:
                data = resp.json()
                if data.get("cartridge", {}).get("verified"):
                    results.add_pass("POST /api/notebook/{id}/cartridge (verified)")
                else:
                    results.add_pass("POST /api/notebook/{id}/cartridge")
            else:
                results.add_fail("POST cartridge", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("POST cartridge", str(e))

        # ─────────────────────────────────────────────────────────────────
        print_section("SEARCH")
        # ─────────────────────────────────────────────────────────────────

        # Search
        try:
            resp = await client.post("/api/search", json={"query": "Jasper Lewis"})
            if resp.status_code == 200:
                data = resp.json()
                if data.get("count", 0) >= 1:
                    results.add_pass("POST /api/search")
                else:
                    results.add_fail("POST /api/search", "No results found")
            else:
                results.add_fail("POST /api/search", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("POST /api/search", str(e))

        # ─────────────────────────────────────────────────────────────────
        print_section("VERIFICATION (requires Newton)")
        # ─────────────────────────────────────────────────────────────────

        # Verify card (this may fail if Newton isn't running)
        try:
            resp = await client.post("/api/card/test/verify", json={
                "claim": "Water boils at 100 degrees Celsius at sea level",
                "sources": [
                    {"type": "url", "location": "https://physics.nist.gov", "verified": True}
                ]
            })
            if resp.status_code == 200:
                data = resp.json()
                results.add_pass(f"POST /api/card/verify (confidence: {data.get('verification', {}).get('confidence', 0):.2f})")
            else:
                results.add_fail("POST /api/card/verify", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("POST /api/card/verify", f"Newton may not be running: {e}")

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# UI BOT TEST (Simulated)
# ═══════════════════════════════════════════════════════════════════════════════

async def test_ui_bot():
    """Simulate UI interactions via API calls."""
    results = TestResult()
    
    print_section("UI BOT SIMULATION")
    print("  Simulating user interactions...\n")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        
        # Step 1: User opens parcStation (GET /)
        try:
            resp = await client.get("/")
            if resp.status_code == 200 and "parcStation" in resp.text:
                results.add_pass("🤖 Bot opens parcStation homepage")
            else:
                results.add_fail("Open homepage", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("Open homepage", str(e))
        
        # Step 2: User creates a new notebook
        try:
            resp = await client.post("/api/notebook", json={
                "name": "Bot's Test Notebook"
            })
            data = resp.json()
            notebook_id = data.get("id")
            if notebook_id:
                results.add_pass("🤖 Bot creates new notebook")
            else:
                results.add_fail("Create notebook", "No ID")
                return results
        except Exception as e:
            results.add_fail("Create notebook", str(e))
            return results

        # Step 3: User clicks "New Stack"
        try:
            resp = await client.post(f"/api/notebook/{notebook_id}/stack", json={
                "name": "My Research",
                "description": "Testing verified knowledge",
                "color": 0xa855f7
            })
            data = resp.json()
            stack_id = data.get("stack", {}).get("id")
            if stack_id:
                results.add_pass("🤖 Bot clicks 'New Stack' → creates 'My Research'")
            else:
                results.add_fail("Create stack", "No ID")
                return results
        except Exception as e:
            results.add_fail("Create stack", str(e))
            return results

        # Step 4: User adds cards with claims
        cards_to_add = [
            {
                "claim": "The Earth orbits the Sun",
                "sources": [{"type": "url", "location": "NASA.gov", "verified": True}]
            },
            {
                "claim": "Water is H2O",
                "sources": [{"type": "document", "location": "Chemistry textbook", "verified": True}]
            },
            {
                "claim": "Houston was founded in 1836",
                "sources": []  # No source - should be draft
            }
        ]
        
        for card in cards_to_add:
            try:
                resp = await client.post(f"/api/notebook/{notebook_id}/stack/{stack_id}/card", json=card)
                if resp.status_code == 200:
                    results.add_pass(f"🤖 Bot adds card: '{card['claim'][:30]}...'")
                else:
                    results.add_fail(f"Add card", f"Status {resp.status_code}")
            except Exception as e:
                results.add_fail(f"Add card", str(e))

        # Step 5: User adds a VoicePath cartridge
        try:
            resp = await client.post(f"/api/notebook/{notebook_id}/cartridge", json={
                "type": "voicepath",
                "name": "Music Visualizer",
                "position": {"x": 20, "y": 0, "z": 0}
            })
            if resp.status_code == 200:
                results.add_pass("🤖 Bot adds VoicePath cartridge")
            else:
                results.add_fail("Add cartridge", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("Add cartridge", str(e))

        # Step 6: User searches for "Earth"
        try:
            resp = await client.post("/api/search", json={"query": "Earth"})
            data = resp.json()
            if data.get("count", 0) >= 1:
                results.add_pass(f"🤖 Bot searches 'Earth' → {data['count']} result(s)")
            else:
                results.add_fail("Search", "No results")
        except Exception as e:
            results.add_fail("Search", str(e))

        # Step 7: User adds a quick card (draft)
        try:
            resp = await client.post(f"/api/notebook/{notebook_id}/quick-card", json={
                "claim": "TODO: Research the Brazos River history"
            })
            if resp.status_code == 200:
                results.add_pass("🤖 Bot adds quick card to intake area")
            else:
                results.add_fail("Add quick card", f"Status {resp.status_code}")
        except Exception as e:
            results.add_fail("Add quick card", str(e))

        # Step 8: Check final notebook state
        try:
            resp = await client.get(f"/api/notebook/{notebook_id}")
            data = resp.json()
            stack_count = len(data.get("stacks", []))
            cartridge_count = len(data.get("cartridges", []))
            quick_card_count = len(data.get("quickCards", []))
            
            results.add_pass(f"🤖 Bot reviews notebook: {stack_count} stack(s), {cartridge_count} cartridge(s), {quick_card_count} draft(s)")
            
            # Check stack has cards
            if data.get("stacks"):
                card_count = len(data["stacks"][0].get("cards", []))
                results.add_pass(f"🤖 Bot verifies stack has {card_count} card(s)")
        except Exception as e:
            results.add_fail("Review notebook", str(e))

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    print("""
    ═══════════════════════════════════════════════════════════════════════════════
    
        ◈ parcStation Test Suite
        "Built on proof"
        
    ═══════════════════════════════════════════════════════════════════════════════
    """)
    
    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(f"{BASE_URL}/api/info")
    except:
        print("  ✗ parcStation server not running!")
        print(f"    Start it with: python server.py")
        print(f"    Expected at: {BASE_URL}")
        return
    
    print("  ✓ parcStation server is running\n")
    
    # Run API tests
    print("\n  ╔════════════════════════════════════════╗")
    print("  ║         API ENDPOINT TESTS             ║")
    print("  ╚════════════════════════════════════════╝")
    api_results = await test_api()
    
    # Run UI bot simulation
    print("\n  ╔════════════════════════════════════════╗")
    print("  ║         UI BOT SIMULATION              ║")
    print("  ╚════════════════════════════════════════╝")
    ui_results = await test_ui_bot()
    
    # Summary
    print("\n")
    print("  ╔════════════════════════════════════════╗")
    print("  ║             FINAL SUMMARY              ║")
    print("  ╚════════════════════════════════════════╝")
    
    total_passed = api_results.passed + ui_results.passed
    total_failed = api_results.failed + ui_results.failed
    
    print(f"\n  API Tests:  {api_results.passed} passed, {api_results.failed} failed")
    print(f"  UI Bot:     {ui_results.passed} passed, {ui_results.failed} failed")
    print(f"  ─────────────────────────────")
    print(f"  TOTAL:      {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("\n  ✓ ALL TESTS PASSED! parcStation is ready.")
    else:
        print(f"\n  ⚠️ {total_failed} test(s) failed. Check errors above.")
    
    print()


if __name__ == "__main__":
    asyncio.run(main())
