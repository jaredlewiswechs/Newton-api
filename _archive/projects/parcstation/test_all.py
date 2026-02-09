#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
PARCSTATION TEST RUNNER
Complete Test Suite

Test Suites:
1. SMOKE     - Basic connectivity (8 checks)
2. CONTRACT  - API contracts (45 checks) 
3. ACID      - Transaction integrity (11 checks)
4. CARTRIDGE - External integrations (36 checks)
5. UI        - User interface structure (20+ checks)
6. LOGIC     - JavaScript logic validation (40+ checks)

Usage:
    python test_all.py              # Run all tests
    python test_all.py smoke        # Run smoke tests only
    python test_all.py ui logic     # Run UI and logic tests
    python test_all.py --fast       # Skip slow network tests

Based on:
- Nielsen's 10 Usability Heuristics
- Testing Library principles ("test how users use it")
- ACID transaction guarantees
- Contract-first API design
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import time
import subprocess
from pathlib import Path

PARCSTATION_DIR = Path(__file__).parent

# Test modules
TEST_MODULES = {
    'smoke': 'test.py smoke',
    'contract': 'test.py contract', 
    'acid': 'test_acid.py',
    'cartridge': 'test.py cartridge',
    'ui': 'test_ui.py',
    'logic': 'test_logic.py'
}

def run_test(name, command):
    """Run a test module and return success status."""
    print(f"\n{'─' * 60}")
    print(f"Running: {name.upper()}")
    print('─' * 60)
    
    try:
        result = subprocess.run(
            ['python', *command.split()],
            cwd=PARCSTATION_DIR,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {name}: {e}")
        return False

def main():
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " PARCSTATION COMPLETE TEST SUITE ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    # Parse arguments
    args = sys.argv[1:]
    fast_mode = '--fast' in args
    args = [a for a in args if not a.startswith('--')]
    
    # Determine which tests to run
    if not args:
        # Run all tests
        tests_to_run = list(TEST_MODULES.keys())
    else:
        tests_to_run = [t for t in args if t in TEST_MODULES]
    
    if fast_mode:
        # Skip network-dependent tests
        tests_to_run = [t for t in tests_to_run if t not in ['cartridge']]
        print("\n⚡ Fast mode: skipping network tests")
    
    if not tests_to_run:
        print(f"\nUnknown test suite. Available: {', '.join(TEST_MODULES.keys())}")
        return 1
    
    print(f"\nTests to run: {', '.join(tests_to_run)}")
    
    # Run tests
    start_time = time.time()
    results = {}
    
    for test_name in tests_to_run:
        command = TEST_MODULES[test_name]
        results[test_name] = run_test(test_name, command)
    
    elapsed = time.time() - start_time
    
    # Summary
    print("\n" + "═" * 60)
    print(" TEST SUMMARY ".center(60))
    print("═" * 60)
    
    passed = sum(1 for r in results.values() if r)
    failed = sum(1 for r in results.values() if not r)
    
    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}  {name.upper()}")
    
    print(f"\n  Suites: {passed}/{passed + failed} passed")
    print(f"  Time: {elapsed:.2f}s")
    print("═" * 60)
    
    if failed == 0:
        print("\n✅ All test suites passed!")
        return 0
    else:
        print(f"\n❌ {failed} test suite(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
