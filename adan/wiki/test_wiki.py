#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
ADANPEDIA STRESS TEST
Test the Wikipedia-style Knowledge Base interface
═══════════════════════════════════════════════════════════════════════════════
"""

import httpx
import time
import asyncio

BASE_URL = "http://localhost:8085"

def test_health():
    """Test health endpoint."""
    print("\n1. HEALTH CHECK")
    print("-" * 50)
    try:
        r = httpx.get(f"{BASE_URL}/health", timeout=5)
        data = r.json()
        print(f"   Status: {data['status']}")
        print(f"   Facts: {data['facts_count']}")
        print(f"   Categories: {data['categories_count']}")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_get_facts():
    """Test getting all facts."""
    print("\n2. GET ALL FACTS")
    print("-" * 50)
    try:
        start = time.time()
        r = httpx.get(f"{BASE_URL}/api/facts", timeout=10)
        elapsed = (time.time() - start) * 1000
        data = r.json()
        print(f"   Total facts: {data['total']}")
        print(f"   Categories: {list(data['categories'].keys())[:5]}...")
        print(f"   Time: {elapsed:.0f}ms")
        
        # Sample a few
        if data['facts']:
            print(f"\n   Sample facts:")
            for fact in data['facts'][:3]:
                print(f"   • {fact['key']}: {fact['fact'][:60]}...")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_wikipedia_import():
    """Test importing from Wikipedia."""
    print("\n3. WIKIPEDIA IMPORT")
    print("-" * 50)
    
    test_articles = [
        "Albert Einstein",
        "Python (programming language)",
        "Tokyo",
        "Isaac Newton",
        "NASA"
    ]
    
    success = 0
    for article in test_articles:
        try:
            start = time.time()
            r = httpx.post(
                f"{BASE_URL}/api/import/wikipedia",
                json={"query": article},
                timeout=15
            )
            elapsed = (time.time() - start) * 1000
            data = r.json()
            
            if data.get('success'):
                print(f"   ✓ '{article}' → {data.get('facts_added', 0)} facts ({elapsed:.0f}ms)")
                success += 1
            else:
                print(f"   ✗ '{article}' → {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ✗ '{article}' → Error: {e}")
    
    print(f"\n   Result: {success}/{len(test_articles)} imports successful")
    return success == len(test_articles)

def test_add_fact():
    """Test adding a manual fact."""
    print("\n4. ADD MANUAL FACT")
    print("-" * 50)
    try:
        r = httpx.post(
            f"{BASE_URL}/api/facts",
            json={
                "key": "Test Fact",
                "fact": "This is a test fact added by the stress test.",
                "category": "Testing",
                "source": "Stress Test",
                "source_url": "http://localhost"
            },
            timeout=5
        )
        data = r.json()
        if data.get('success'):
            print(f"   ✓ Fact added successfully")
            return True
        else:
            print(f"   ✗ Failed: {data}")
            return False
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_concurrent_requests():
    """Test concurrent requests."""
    print("\n5. CONCURRENT LOAD TEST")
    print("-" * 50)
    
    async def fetch_facts():
        async with httpx.AsyncClient() as client:
            return await client.get(f"{BASE_URL}/api/facts", timeout=10)
    
    async def run_concurrent():
        tasks = [fetch_facts() for _ in range(20)]
        start = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = (time.time() - start) * 1000
        
        success = sum(1 for r in results if not isinstance(r, Exception) and r.status_code == 200)
        print(f"   20 concurrent requests: {success}/20 succeeded")
        print(f"   Total time: {elapsed:.0f}ms ({elapsed/20:.1f}ms avg)")
        return success == 20
    
    try:
        return asyncio.run(run_concurrent())
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_verify_imported():
    """Verify imported facts are queryable."""
    print("\n6. VERIFY IMPORTED DATA")
    print("-" * 50)
    try:
        r = httpx.get(f"{BASE_URL}/api/facts", timeout=10)
        data = r.json()
        
        # Check for Wikipedia-sourced facts
        wiki_facts = [f for f in data['facts'] if f.get('source') == 'Wikipedia']
        print(f"   Wikipedia facts: {len(wiki_facts)}")
        
        if wiki_facts:
            print(f"   Sample Wikipedia import:")
            for wf in wiki_facts[:3]:
                print(f"   • {wf['key']}")
        
        # Check total growth
        print(f"\n   Total KB size: {data['total']} facts")
        return len(wiki_facts) > 0
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def main():
    print("=" * 60)
    print("ADANPEDIA STRESS TEST")
    print("=" * 60)
    
    results = []
    
    results.append(("Health", test_health()))
    results.append(("Get Facts", test_get_facts()))
    results.append(("Wikipedia Import", test_wikipedia_import()))
    results.append(("Add Fact", test_add_fact()))
    results.append(("Concurrent Load", test_concurrent_requests()))
    results.append(("Verify Imported", test_verify_imported()))
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n   {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n   🎉 ALL TESTS PASSED!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
