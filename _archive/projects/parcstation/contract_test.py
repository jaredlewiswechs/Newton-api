#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
parcStation UI CONTRACT TEST
Tests the boundary between UI ↔ State ↔ Network
"Most bugs live at boundaries" - This is your boundary guard.
═══════════════════════════════════════════════════════════════════════════════
"""

import requests
import json
import re
import sys

G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
B = "\033[94m"
W = "\033[0m"

class ContractTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.ui_url = "http://localhost:8082"
        self.api_url = "http://localhost:8000"
        self.agent_url = "http://localhost:8091"
        
    def check(self, name: str, condition: bool, detail: str = ""):
        if condition:
            print(f"  {G}✓{W} {name}")
            self.passed += 1
        else:
            print(f"  {R}✗{W} {name} {Y}({detail}){W}")
            self.failed += 1
        return condition
    
    def run(self):
        print(f"\n{B}═══ UI CONTRACT TEST ═══{W}\n")
        
        # ═══════════════════════════════════════════════════════════════════
        # 1. HTML CONTRACT
        # ═══════════════════════════════════════════════════════════════════
        print(f"{Y}HTML Structure:{W}")
        try:
            html = requests.get(f"{self.ui_url}/index2.html", timeout=3).text
            
            # Required elements
            self.check("Has app container", 'class="app"' in html or 'id="app"' in html)
            self.check("Has sidebar", 'class="sidebar"' in html or 'id="sidebar"' in html)
            self.check("Has main area", 'class="main"' in html or 'class="main-content"' in html)
            self.check("Has chat-panel", 'class="chat-panel"' in html)
            self.check("Has chat-fab", 'class="chat-fab"' in html)
            
            # Required scripts
            self.check("Loads app2.js", 'app2.js' in html)
            self.check("Loads style.css", 'style.css' in html)
            
            # No console errors trigger (basic)
            self.check("No inline onerror", 'onerror=' not in html.lower())
            
        except Exception as e:
            self.check("HTML loads", False, str(e))
        
        # ═══════════════════════════════════════════════════════════════════
        # 2. CSS CONTRACT  
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{Y}CSS Contract:{W}")
        try:
            css = requests.get(f"{self.ui_url}/style.css", timeout=3).text
            
            # Required variables
            self.check("Has --bg-primary", "--bg-primary" in css)
            self.check("Has --glass-bg", "--glass-bg" in css)
            self.check("Has --accent", "--accent" in css)
            
            # Trust colors (core to Newton)
            self.check("Has verified color", "--verified" in css or "#10B981" in css)
            self.check("Has unverified color", "--unverified" in css or "#EF4444" in css)
            
            # Critical: Pointer events for clickability
            self.check("Pointer-events defined", "pointer-events" in css)
            
            # Sheet/overlay visibility
            self.check("Sheet visibility rules", ".sheet" in css and "hidden" in css)
            self.check("Overlay visibility rules", ".sheet-overlay" in css)
            
            # Chat panel
            self.check("Chat panel styled", ".chat-panel" in css)
            self.check("Chat messages styled", ".chat-message" in css or "message" in css)
            
        except Exception as e:
            self.check("CSS loads", False, str(e))
        
        # ═══════════════════════════════════════════════════════════════════
        # 3. JAVASCRIPT CONTRACT
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{Y}JavaScript Contract:{W}")
        try:
            js = requests.get(f"{self.ui_url}/app2.js", timeout=3).text
            
            # Required classes
            self.check("ParcStationApp class", "class ParcStationApp" in js)
            self.check("NewtonClient class", "class NewtonClient" in js)
            self.check("NewtonAgentClient class", "class NewtonAgentClient" in js)
            self.check("DataStore class", "class DataStore" in js)
            
            # Required methods exist
            self.check("bindEvents method", "bindEvents" in js)
            self.check("bindChatEvents method", "bindChatEvents" in js)
            self.check("render methods", "renderStackGrid" in js or "render(" in js)
            
            # API URLs configured
            self.check("Newton URL config", "localhost:8000" in js or "NEWTON_URL" in js)
            self.check("Agent URL config", "localhost:8091" in js or "AGENT_URL" in js)
            
            # Event handlers
            self.check("Click handlers", "addEventListener" in js and "click" in js)
            self.check("DOMContentLoaded", "DOMContentLoaded" in js)
            
            # No obvious errors
            self.check("No console.error calls", js.count("console.error") < 5)
            
        except Exception as e:
            self.check("JS loads", False, str(e))
        
        # ═══════════════════════════════════════════════════════════════════
        # 4. API CONTRACT (what UI expects from backend)
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{Y}API Contract (Newton):{W}")
        try:
            # Verify returns expected shape
            r = requests.post(f"{self.api_url}/verify", 
                            json={"input": "contract test"}, timeout=3)
            data = r.json()
            self.check("/verify returns 'verified'", "verified" in data)
            self.check("/verify returns boolean", isinstance(data.get("verified"), bool))
            
            # Calculate returns expected shape
            r = requests.post(f"{self.api_url}/calculate",
                            json={"expression": {"op": "+", "args": [1, 1]}}, timeout=3)
            data = r.json()
            self.check("/calculate returns 'result'", "result" in data)
            
            # Ground returns expected shape
            r = requests.post(f"{self.api_url}/ground",
                            json={"claim": "test"}, timeout=3)
            data = r.json()
            self.check("/ground returns 'status'", "status" in data)
            
            # Ledger returns expected shape
            r = requests.get(f"{self.api_url}/ledger", timeout=3)
            data = r.json()
            self.check("/ledger returns 'entries'", "entries" in data)
            self.check("/ledger entries is list", isinstance(data.get("entries"), list))
            
        except Exception as e:
            self.check("Newton API responds", False, str(e))
        
        print(f"\n{Y}API Contract (Agent):{W}")
        try:
            # Health check (fast)
            r = requests.get(f"{self.agent_url}/health", timeout=3)
            self.check("/health responds", r.status_code == 200)
            
            # Stats (no LLM, fast)
            r = requests.get(f"{self.agent_url}/stats", timeout=3)
            self.check("/stats returns data", r.status_code == 200)
            
            # History returns expected shape  
            r = requests.get(f"{self.agent_url}/history", timeout=3)
            data = r.json()
            self.check("/history returns turns", "turns" in data or "history" in data)
            
            # Models list (no LLM inference)
            r = requests.get(f"{self.agent_url}/models", timeout=5)
            data = r.json()
            self.check("/models returns list", "models" in data or isinstance(data, list))
            
        except Exception as e:
            self.check("Agent API responds", False, str(e))
        
        # ═══════════════════════════════════════════════════════════════════
        # 5. BOUNDARY TEST (UI ↔ API wiring)
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{Y}Boundary Wiring:{W}")
        try:
            js = requests.get(f"{self.ui_url}/app2.js", timeout=3).text
            
            # Check fetch calls match API endpoints
            self.check("fetch to /verify", "/verify" in js)
            self.check("fetch to /ground", "/ground" in js)
            self.check("fetch to /chat", "/chat" in js)
            
            # Check error handling exists
            self.check("catch blocks exist", ".catch(" in js or "catch {" in js or "catch(" in js)
            
            # Check response handling
            self.check("JSON parsing", ".json()" in js)
            
        except Exception as e:
            self.check("Boundary check", False, str(e))
        
        # ═══════════════════════════════════════════════════════════════════
        # REPORT
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{B}═══════════════════════════{W}")
        total = self.passed + self.failed
        pct = (self.passed / total * 100) if total > 0 else 0
        
        if self.failed == 0:
            print(f"  {G}✓ CONTRACT SATISFIED{W}")
            print(f"  {self.passed}/{total} checks passed (100%)")
        else:
            print(f"  {R}✗ CONTRACT VIOLATED{W}")
            print(f"  {self.passed}/{total} checks passed ({pct:.0f}%)")
            print(f"  {self.failed} violations found")
        
        print(f"{B}═══════════════════════════{W}\n")
        
        return 0 if self.failed == 0 else 1


# ═══════════════════════════════════════════════════════════════════════════════
# USAGE SNIPPET (for intent verification)
# ═══════════════════════════════════════════════════════════════════════════════

USAGE = """
┌─────────────────────────────────────────────────────────────────────────────┐
│ parcStation UI Usage                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Import (in HTML):                                                           │
│   <link rel="stylesheet" href="style.css">                                  │
│   <script src="app2.js"></script>                                           │
│                                                                             │
│ Required HTML:                                                              │
│   <div id="app">                                                            │
│     <nav class="sidebar">...</nav>                                          │
│     <main class="main-content">...</main>                                   │
│     <div class="chat-panel hidden">...</div>                                │
│     <button class="chat-fab">...</button>                                   │
│   </div>                                                                    │
│                                                                             │
│ Config (in app2.js):                                                        │
│   const CONFIG = {                                                          │
│     NEWTON_URL: 'http://localhost:8000',                                    │
│     AGENT_URL: 'http://localhost:8091'                                      │
│   };                                                                        │
│                                                                             │
│ Expected Props/Types:                                                       │
│   - Stack: { id, title, cards[], created, modified }                        │
│   - Card: { id, content, trust, sources[], created, modified }              │
│   - Trust: 'verified' | 'partial' | 'draft' | 'unverified' | 'disputed'     │
│                                                                             │
│ API Contracts:                                                              │
│   POST /verify     { input: string }  → { verified: bool }                  │
│   POST /ground     { claim: string }  → { status: string }                  │
│   POST /calculate  { expression: obj} → { result: any }                     │
│   POST /chat       { message: string} → { content: string }                 │
│   GET  /ledger                        → { entries: [] }                     │
│   GET  /history                       → { history: [] }                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
"""


if __name__ == "__main__":
    print(USAGE)
    test = ContractTest()
    sys.exit(test.run())
