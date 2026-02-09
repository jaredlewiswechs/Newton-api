#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
parcStation SMOKE TEST
"Does it boot?" - 5 second answer
═══════════════════════════════════════════════════════════════════════════════

Run before looking at the UI. Trust the pipeline, verify the artifact.
"""

import requests
import sys
import time

# Colors
G = "\033[92m"  # Green
R = "\033[91m"  # Red
Y = "\033[93m"  # Yellow
B = "\033[94m"  # Blue
W = "\033[0m"   # White/Reset

def smoke():
    print(f"\n{B}═══ SMOKE TEST ═══{W}\n")
    
    checks = []
    start = time.time()
    
    # 1. Newton Supercomputer
    try:
        r = requests.get("http://localhost:8000/health", timeout=2)
        ok = r.status_code == 200
        checks.append(("Newton API", ok, f"{r.elapsed.total_seconds()*1000:.0f}ms"))
    except:
        checks.append(("Newton API", False, "DOWN"))
    
    # 2. Newton Agent
    try:
        r = requests.get("http://localhost:8091/health", timeout=2)
        ok = r.status_code == 200
        checks.append(("Newton Agent", ok, f"{r.elapsed.total_seconds()*1000:.0f}ms"))
    except:
        checks.append(("Newton Agent", False, "DOWN"))
    
    # 3. Cartridges
    try:
        r = requests.get("http://localhost:8093/health", timeout=2)
        ok = r.status_code == 200
        checks.append(("Cartridges", ok, f"{r.elapsed.total_seconds()*1000:.0f}ms"))
    except:
        checks.append(("Cartridges", False, "DOWN (optional)"))
    
    # 4. UI Server
    try:
        r = requests.get("http://localhost:8082/index2.html", timeout=2)
        ok = r.status_code == 200 and "parcStation" in r.text
        checks.append(("UI Server", ok, f"{len(r.text)} bytes"))
    except:
        checks.append(("UI Server", False, "DOWN"))
    
    # 5. Critical API: Verify
    try:
        r = requests.post("http://localhost:8000/verify", 
                         json={"input": "smoke"}, timeout=2)
        ok = r.status_code == 200 and "verified" in r.json()
        checks.append(("API /verify", ok, f"{r.elapsed.total_seconds()*1000:.0f}ms"))
    except:
        checks.append(("API /verify", False, "FAIL"))
    
    # 6. Critical API: Calculate
    try:
        r = requests.post("http://localhost:8000/calculate",
                         json={"expression": {"op": "+", "args": [1, 1]}}, timeout=2)
        ok = r.status_code == 200 and str(r.json().get("result")) == "2"
        checks.append(("API /calculate", ok, "1+1=2"))
    except:
        checks.append(("API /calculate", False, "FAIL"))
    
    # 7. UI Contract: JS loads
    try:
        r = requests.get("http://localhost:8082/app2.js", timeout=2)
        has_app = "ParcStationApp" in r.text
        has_newton = "NewtonClient" in r.text
        has_agent = "NewtonAgentClient" in r.text
        ok = all([has_app, has_newton, has_agent])
        checks.append(("JS Contract", ok, f"App:{has_app} Newton:{has_newton} Agent:{has_agent}"))
    except:
        checks.append(("JS Contract", False, "FAIL"))
    
    # 7. UI Contract: CSS loads
    try:
        r = requests.get("http://localhost:8082/style.css", timeout=2)
        has_vars = "--bg-primary" in r.text
        has_pointer = "pointer-events" in r.text
        ok = has_vars and has_pointer
        checks.append(("CSS Contract", ok, f"vars:{has_vars} pointer:{has_pointer}"))
    except:
        checks.append(("CSS Contract", False, "FAIL"))
    
    # Print results
    all_pass = True
    for name, ok, detail in checks:
        icon = f"{G}✓{W}" if ok else f"{R}✗{W}"
        status = f"{G}PASS{W}" if ok else f"{R}FAIL{W}"
        print(f"  {icon} {name:15} {status:12} {Y}{detail}{W}")
        if not ok:
            all_pass = False
    
    elapsed = time.time() - start
    
    print(f"\n{B}═══════════════════{W}")
    if all_pass:
        print(f"  {G}✓ ALL SYSTEMS GO{W} ({elapsed:.1f}s)")
        print(f"{B}═══════════════════{W}\n")
        return 0
    else:
        failed = sum(1 for _, ok, _ in checks if not ok)
        print(f"  {R}✗ {failed} SYSTEMS DOWN{W} ({elapsed:.1f}s)")
        print(f"{B}═══════════════════{W}\n")
        return 1


if __name__ == "__main__":
    sys.exit(smoke())
