#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
parcStation TEST RUNNER
One command. Full verification. Before you look at the UI.

Usage:
    python test.py              # Full suite
    python test.py smoke        # Just smoke test (5 seconds)
    python test.py contract     # Just contract test
    python test.py acid         # ACID compliance test
    python test.py cartridges   # Cartridge system test
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import subprocess
import time
import os

G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
B = "\033[94m"
M = "\033[95m"
W = "\033[0m"

def banner():
    print(f"""
{B}╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   {M}parcStation Test Suite{B}                                                  ║
║   Trust the pipeline. Verify the artifact.                                ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝{W}
""")

def run_test(name: str, script: str) -> bool:
    """Run a test script, return True if passed."""
    print(f"{B}▶ Running {name}...{W}\n")
    start = time.time()
    
    result = subprocess.run(
        [sys.executable, script],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    elapsed = time.time() - start
    
    if result.returncode == 0:
        print(f"\n{G}✓ {name} PASSED{W} ({elapsed:.1f}s)\n")
        return True
    else:
        print(f"\n{R}✗ {name} FAILED{W} ({elapsed:.1f}s)\n")
        return False


def main():
    banner()
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    results = []
    start = time.time()
    
    if mode in ("smoke", "full"):
        results.append(("Smoke Test", run_test("Smoke Test", "smoke.py")))
    
    if mode in ("contract", "full"):
        results.append(("Contract Test", run_test("Contract Test", "contract_test.py")))
    
    if mode in ("acid", "full"):
        results.append(("ACID Test", run_test("ACID Test", "test_acid.py")))
    
    if mode in ("cartridges", "full"):
        results.append(("Cartridge Test", run_test("Cartridge Test", "test_cartridges.py")))
    
    # Summary
    elapsed = time.time() - start
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    print(f"{B}═══════════════════════════════════════════════════════════════════════════{W}")
    
    if passed == total:
        print(f"""
{G}  ███████╗ █████╗ ███████╗███████╗
  ██╔════╝██╔══██╗██╔════╝██╔════╝
  ███████╗███████║█████╗  █████╗  
  ╚════██║██╔══██║██╔══╝  ██╔══╝  
  ███████║██║  ██║██║     ███████╗
  ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝{W}
  
  All {total} test suites passed in {elapsed:.1f}s
  
  {Y}→ UI is safe to open{W}
""")
        return 0
    else:
        failed = total - passed
        print(f"""
{R}  ███████╗ █████╗ ██╗██╗     
  ██╔════╝██╔══██╗██║██║     
  █████╗  ███████║██║██║     
  ██╔══╝  ██╔══██║██║██║     
  ██║     ██║  ██║██║███████╗
  ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝{W}
  
  {failed}/{total} test suites failed
  
  {Y}→ Fix issues before opening UI{W}
""")
        for name, ok in results:
            icon = f"{G}✓{W}" if ok else f"{R}✗{W}"
            print(f"    {icon} {name}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
