#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON STRESS TEST
Tests all components: KB, Calculator, Logic Engine, Trajectory, Grounding, etc.
═══════════════════════════════════════════════════════════════════════════════
"""
import requests
import time

def run_stress_test():
    print("═" * 60)
    print("NEWTON STRESS TEST")
    print("═" * 60)
    
    passed = 0
    failed = 0
    
    # 1. KB Lookup
    start = time.time()
    try:
        r = requests.post('http://localhost:8090/chat', json={'message': 'Capital of France?'}, timeout=10)
        ms = int((time.time() - start) * 1000)
        data = r.json()
        verified = data.get('verified', False)
        content = data.get('content', '')[:40]
        if verified:
            passed += 1
            print(f"✓ 1. KB Lookup:     PASS ({ms}ms) - {content}...")
        else:
            failed += 1
            print(f"✗ 1. KB Lookup:     FAIL ({ms}ms)")
    except Exception as e:
        failed += 1
        print(f"✗ 1. KB Lookup:     ERROR - {e}")
    
    # 2. TI Calculator
    start = time.time()
    try:
        r = requests.post('http://localhost:8090/calculate', json={'expression': '2^10 + sqrt(100)'}, timeout=10)
        ms = int((time.time() - start) * 1000)
        data = r.json()
        result = data.get('result')
        if result == 1034:
            passed += 1
            print(f"✓ 2. TI Calc:       PASS ({ms}ms) - 2^10+sqrt(100) = {result}")
        else:
            failed += 1
            print(f"✗ 2. TI Calc:       FAIL ({ms}ms) - got {result}, expected 1034")
    except Exception as e:
        failed += 1
        print(f"✗ 2. TI Calc:       ERROR - {e}")
    
    # 3. Logic Engine
    start = time.time()
    try:
        r = requests.post('http://localhost:8000/calculate', json={'expression': {'op': '*', 'args': [7, 8]}}, timeout=10)
        ms = int((time.time() - start) * 1000)
        data = r.json()
        result = data.get('result')
        # Result could be int or float
        if result is not None and int(result) == 56:
            passed += 1
            print(f"✓ 3. Logic Engine:  PASS ({ms}ms) - 7*8 = {result}")
        else:
            failed += 1
            print(f"✗ 3. Logic Engine:  FAIL ({ms}ms) - got {result}")
    except Exception as e:
        failed += 1
        print(f"✗ 3. Logic Engine:  ERROR - {e}")
    
    # 4. Trajectory Analysis
    start = time.time()
    try:
        r = requests.post('http://localhost:8090/trajectory/analyze', json={'text': 'Newton verifies truth'}, timeout=10)
        ms = int((time.time() - start) * 1000)
        data = r.json()
        word_count = data.get('word_count', 0)
        if word_count == 3:
            passed += 1
            print(f"✓ 4. Trajectory:    PASS ({ms}ms) - {word_count} words analyzed")
        else:
            failed += 1
            print(f"✗ 4. Trajectory:    FAIL ({ms}ms) - got {word_count} words")
    except Exception as e:
        failed += 1
        print(f"✗ 4. Trajectory:    ERROR - {e}")
    
    # 5. Verify Endpoint (constraints is list of strings)
    start = time.time()
    try:
        r = requests.post('http://localhost:8000/verify', json={
            'input': 'test',
            'constraints': ['test']
        }, timeout=10)
        ms = int((time.time() - start) * 1000)
        data = r.json()
        # Check 'verified' key
        if data.get('verified'):
            passed += 1
            print(f"✓ 5. Verify:        PASS ({ms}ms)")
        else:
            failed += 1
            print(f"✗ 5. Verify:        FAIL ({ms}ms) - {data}")
    except Exception as e:
        failed += 1
        print(f"✗ 5. Verify:        ERROR - {e}")
    
    # 6. Grounding (may be slow due to external APIs)
    start = time.time()
    try:
        r = requests.post('http://localhost:8090/ground', json={'claim': 'Paris is in France'}, timeout=30)
        ms = int((time.time() - start) * 1000)
        data = r.json()
        evidence_count = len(data.get('evidence', []))
        if evidence_count > 0:
            passed += 1
            print(f"✓ 6. Grounding:     PASS ({ms}ms) - {evidence_count} sources")
        else:
            print(f"⚠ 6. Grounding:     WARN ({ms}ms) - no evidence (external APIs)")
    except Exception as e:
        print(f"⚠ 6. Grounding:     SKIP - {e}")
    
    # 7. Wikipedia Cartridge
    start = time.time()
    try:
        r = requests.post('http://localhost:8093/cartridge/wikipedia/search', json={'query': 'Python'}, timeout=15)
        ms = int((time.time() - start) * 1000)
        data = r.json()
        results = len(data.get('results', []))
        if results > 0:
            passed += 1
            print(f"✓ 7. Wikipedia:     PASS ({ms}ms) - {results} results")
        else:
            failed += 1
            print(f"✗ 7. Wikipedia:     FAIL ({ms}ms)")
    except Exception as e:
        failed += 1
        print(f"✗ 7. Wikipedia:     ERROR - {e}")
    
    # 8. Dictionary Cartridge
    start = time.time()
    try:
        r = requests.post('http://localhost:8093/cartridge/dictionary/define', json={'word': 'verify'}, timeout=10)
        ms = int((time.time() - start) * 1000)
        data = r.json()
        if data.get('found'):
            passed += 1
            print(f"✓ 8. Dictionary:    PASS ({ms}ms)")
        else:
            failed += 1
            print(f"✗ 8. Dictionary:    FAIL ({ms}ms)")
    except Exception as e:
        failed += 1
        print(f"✗ 8. Dictionary:    ERROR - {e}")
    
    # 9. Calendar Cartridge
    start = time.time()
    try:
        r = requests.get('http://localhost:8093/cartridge/calendar/now', timeout=10)
        ms = int((time.time() - start) * 1000)
        data = r.json()
        if data.get('datetime'):
            passed += 1
            print(f"✓ 9. Calendar:      PASS ({ms}ms) - {data.get('datetime')}")
        else:
            failed += 1
            print(f"✗ 9. Calendar:      FAIL ({ms}ms)")
    except Exception as e:
        failed += 1
        print(f"✗ 9. Calendar:      ERROR - {e}")
    
    # 10. Batch Verify
    start = time.time()
    try:
        r = requests.post('http://localhost:8000/verify/batch', json={'items': [
            {'input': 1, 'constraints': {'gt': 0}},
            {'input': 'abc', 'constraints': {'contains': 'b'}},
            {'input': 10, 'constraints': {'le': 10}},
        ]}, timeout=10)
        ms = int((time.time() - start) * 1000)
        data = r.json()
        results = data.get('results', [])
        all_pass = all(item.get('verified') for item in results)
        if all_pass:
            passed += 1
            print(f"✓ 10. Batch Verify: PASS ({ms}ms) - 3/3 items verified")
        else:
            failed += 1
            print(f"✗ 10. Batch Verify: FAIL ({ms}ms)")
    except Exception as e:
        failed += 1
        print(f"✗ 10. Batch Verify: ERROR - {e}")
    
    # Summary
    print("═" * 60)
    total = passed + failed
    pct = (passed / total * 100) if total > 0 else 0
    print(f"RESULTS: {passed}/{total} passed ({pct:.0f}%)")
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠ {failed} test(s) failed")
    print("═" * 60)

if __name__ == "__main__":
    run_stress_test()
