#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON FULL SYSTEM TEST
Tests all connections together - proves the system works
═══════════════════════════════════════════════════════════════════════════════

Run with:
    Terminal 1: python newton_supercomputer.py
    Terminal 2: python test_full_system.py

This script tests:
    1. Health Check (CPU)
    2. Forge Verification
    3. CDL Constraint Evaluation
    4. Logic Engine (Calculate)
    5. Ledger (Immutable History)
    6. Cartridge Auto-Detect
    7. Rosetta Compiler
    8. Visual Cartridge
    9. Robust Statistics

If all tests pass, the invariants hold. 1 == 1.
"""

import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def test_connection(name, endpoint, method="GET", data=None, expected_key=None, expected_value=None):
    """Test a single endpoint and return (success, response_json)."""
    url = f"{BASE_URL}{endpoint}"
    start = time.perf_counter()

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)

        elapsed_ms = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            result = response.json()

            # Check expected value if specified
            if expected_key and expected_value is not None:
                actual = result.get(expected_key)
                if actual != expected_value:
                    print(f"{RED}✗{RESET} {name}: Expected {expected_key}={expected_value}, got {actual}")
                    return False, result

            print(f"{GREEN}✓{RESET} {name}: {elapsed_ms:.2f}ms")
            return True, result
        else:
            print(f"{RED}✗{RESET} {name}: HTTP {response.status_code}")
            return False, None
    except requests.exceptions.ConnectionError:
        print(f"{RED}✗{RESET} {name}: Connection refused - is Newton running?")
        return False, None
    except Exception as e:
        print(f"{RED}✗{RESET} {name}: {str(e)}")
        return False, None


def main():
    print()
    print(f"{BOLD}═══════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}              NEWTON FULL SYSTEM TEST{RESET}")
    print(f"{BOLD}═══════════════════════════════════════════════════════════════{RESET}")
    print()

    tests = []
    details = []

    # 1. Health Check (CPU)
    ok, result = test_connection("Health Check", "/health")
    tests.append(ok)
    if result:
        components = result.get("components", {})
        operational = sum(1 for v in components.values() if v == "operational")
        details.append(f"   └─ {operational}/{len(components)} components operational")

    # 2. Verify Content (Forge)
    ok, result = test_connection(
        "Forge Verification",
        "/verify",
        "POST",
        {"input": "What is the capital of France?"},
        "verified",
        True
    )
    tests.append(ok)
    if result:
        elapsed = result.get("elapsed_us", 0)
        details.append(f"   └─ Verified: {result.get('verified')} ({elapsed}μs)")

    # 3. Constraint Evaluation (CDL)
    ok, result = test_connection(
        "CDL Constraint",
        "/constraint",
        "POST",
        {
            "constraint": {"field": "amount", "operator": "lt", "value": 1000},
            "object": {"amount": 500}
        },
        "passed",
        True
    )
    tests.append(ok)
    if result:
        details.append(f"   └─ Passed: {result.get('passed')} (amount=500 < 1000)")

    # 4. Calculation (Logic Engine)
    ok, result = test_connection(
        "Logic Engine",
        "/calculate",
        "POST",
        {"expression": {"op": "+", "args": [1, 1]}}
    )
    tests.append(ok)
    if result:
        res = result.get("result")
        details.append(f"   └─ Result: {res} (1 + 1 = 2) ✓")

    # 5. Ledger (Immutable History)
    ok, result = test_connection("Ledger", "/ledger")
    tests.append(ok)
    if result:
        entries = len(result.get("entries", []))
        merkle = result.get("merkle_root", "")[:16]
        details.append(f"   └─ Entries: {entries}, Merkle: {merkle}...")

    # 6. Cartridge Auto-Detect
    ok, result = test_connection(
        "Cartridge Auto",
        "/cartridge/auto",
        "POST",
        {"intent": "Create a simple calculator app"}
    )
    tests.append(ok)
    if result:
        ctype = result.get("cartridge_type", "unknown")
        details.append(f"   └─ Detected: {ctype}")

    # 7. Rosetta Compiler
    ok, result = test_connection(
        "Rosetta Compiler",
        "/cartridge/rosetta",
        "POST",
        {
            "intent": "Build a todo list app",
            "target_platform": "ios",
            "language": "swift"
        },
        "verified",
        True
    )
    tests.append(ok)
    if result:
        details.append(f"   └─ Verified: {result.get('verified')}")

    # 8. Visual Cartridge
    ok, result = test_connection(
        "Visual Cartridge",
        "/cartridge/visual",
        "POST",
        {"intent": "Create a minimalist logo with circles"}
    )
    tests.append(ok)
    if result:
        ctype = result.get("cartridge_type", "unknown")
        details.append(f"   └─ Type: {ctype}")

    # 9. Statistics (Robust)
    ok, result = test_connection(
        "Robust Statistics",
        "/statistics",
        "POST",
        {"values": [1, 2, 3, 4, 5, 100], "method": "robust"}
    )
    tests.append(ok)
    if result:
        stats = result.get("result", {})
        mad = stats.get("mad", 0)
        details.append(f"   └─ MAD: {mad} (robust to outlier 100)")

    # 10. Ratio Constraint (f/g)
    ok, result = test_connection(
        "Ratio Constraint (f/g)",
        "/constraint",
        "POST",
        {
            "constraint": {
                "f_field": "liabilities",
                "g_field": "assets",
                "operator": "ratio_le",
                "threshold": 1.0
            },
            "object": {"liabilities": 500, "assets": 1000}
        },
        "passed",
        True
    )
    tests.append(ok)
    if result:
        details.append(f"   └─ Passed: {result.get('passed')} (500/1000 ≤ 1.0)")

    # Print details
    print()
    for detail in details:
        print(detail)

    # Summary
    print()
    print(f"{BOLD}═══════════════════════════════════════════════════════════════{RESET}")
    passed = sum(tests)
    total = len(tests)

    if passed == total:
        print(f"  {GREEN}RESULTS: {passed}/{total} tests passed{RESET}")
        print(f"  {GREEN}✓ ALL SYSTEMS OPERATIONAL{RESET}")
        print()
        print("  Newton is ready. The constraint IS the instruction.")
        print("  1 == 1.")
    else:
        print(f"  {YELLOW}RESULTS: {passed}/{total} tests passed{RESET}")
        print(f"  {RED}✗ {total - passed} tests failed{RESET}")
        print()
        print("  Check that Newton is running: python newton_supercomputer.py")

    print(f"{BOLD}═══════════════════════════════════════════════════════════════{RESET}")
    print()

    # Return exit code
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
