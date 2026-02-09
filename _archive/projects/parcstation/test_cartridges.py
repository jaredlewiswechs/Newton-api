#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
CARTRIDGE TEST SUITE
Tests all cartridge endpoints
═══════════════════════════════════════════════════════════════════════════════
"""

import requests
import sys
import time
import re
import os

G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
B = "\033[94m"
W = "\033[0m"

CARTRIDGE_URL = "http://localhost:8093"

class CartridgeTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        
    def check(self, name: str, condition: bool, detail: str = ""):
        if condition:
            print(f"  {G}✓{W} {name}")
            self.passed += 1
        else:
            print(f"  {R}✗{W} {name} {Y}({detail}){W}")
            self.failed += 1
        return condition
    
    def check_frontend_config(self):
        """Verify app2.js uses correct CONFIG property names and endpoints"""
        print(f"{Y}Frontend Config Consistency:{W}")
        
        app2_path = os.path.join(os.path.dirname(__file__), "app2.js")
        if not os.path.exists(app2_path):
            self.check("app2.js exists", False, "File not found")
            return
            
        with open(app2_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for typos in CONFIG property names
        # Valid: CONFIG.CARTRIDGE_URL (singular)
        # Invalid: CONFIG.CARTRIDGES_URL (plural - typo)
        typo_matches = re.findall(r'CONFIG\.CARTRIDGES_URL', content)
        self.check("No CONFIG.CARTRIDGES_URL typos", len(typo_matches) == 0, 
                   f"Found {len(typo_matches)} instances of typo")
        
        # Verify CONFIG.CARTRIDGE_URL is defined
        config_def = re.search(r"CARTRIDGE_URL:\s*['\"]", content)
        self.check("CONFIG.CARTRIDGE_URL defined", config_def is not None)
        
        # Verify it's used correctly
        correct_uses = re.findall(r'CONFIG\.CARTRIDGE_URL', content)
        self.check("CONFIG.CARTRIDGE_URL used", len(correct_uses) >= 1, 
                   f"Found {len(correct_uses)} uses")
        
        # Verify calculator uses cartridge endpoint (not Newton directly)
        calc_uses_cartridge = re.search(r'calculate\(.*?\{[^}]*CARTRIDGE_URL.*?/cartridge/code', content, re.DOTALL)
        self.check("Calculator uses cartridge endpoint", calc_uses_cartridge is not None,
                   "Should use /cartridge/code/evaluate not /calculate")
    
    def run(self):
        print(f"\n{B}═══ CARTRIDGE TEST SUITE ═══{W}\n")
        
        # Check frontend config consistency first
        self.check_frontend_config()
        
        # Check service health
        print(f"\n{Y}Service Health:{W}")
        try:
            r = requests.get(f"{CARTRIDGE_URL}/health", timeout=3)
            self.check("Service running", r.status_code == 200)
        except:
            print(f"  {R}✗ Cartridge service not running on port 8093{W}")
            print(f"  {Y}Start with: python cartridges.py{W}")
            return 1
        
        # List cartridges
        print(f"\n{Y}Cartridge Registry:{W}")
        r = requests.get(f"{CARTRIDGE_URL}/cartridges", timeout=3)
        data = r.json()
        self.check("Cartridges endpoint", "cartridges" in data)
        self.check("Has cartridges", len(data.get("cartridges", [])) >= 5)
        
        # ═══════════════════════════════════════════════════════════════════
        # WIKIPEDIA
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{Y}📚 Wikipedia Cartridge:{W}")
        
        # Summary
        r = requests.post(f"{CARTRIDGE_URL}/cartridge/wikipedia/summary",
                         json={"query": "Python programming language"}, timeout=15)
        data = r.json()
        self.check("Summary endpoint", r.status_code == 200)
        self.check("Summary found", data.get("found") == True)
        self.check("Has title", "title" in data)
        self.check("Has summary", len(data.get("summary", "")) > 50)
        self.check("Has URL", "wikipedia.org" in data.get("url", ""))
        
        # Search
        r = requests.post(f"{CARTRIDGE_URL}/cartridge/wikipedia/search",
                         json={"query": "machine learning"}, timeout=15)
        data = r.json()
        self.check("Search endpoint", r.status_code == 200)
        self.check("Has results", len(data.get("results", [])) > 0)
        
        # ═══════════════════════════════════════════════════════════════════
        # ARXIV
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{Y}📄 arXiv Cartridge:{W}")
        
        r = requests.post(f"{CARTRIDGE_URL}/cartridge/arxiv/search",
                         json={"query": "neural networks", "max_results": 3}, timeout=20)
        data = r.json()
        self.check("arXiv search", r.status_code == 200)
        self.check("Has results", len(data.get("results", [])) > 0)
        if data.get("results"):
            paper = data["results"][0]
            self.check("Paper has title", "title" in paper)
            self.check("Paper has authors", len(paper.get("authors", [])) > 0)
            self.check("Paper has URL", "arxiv.org" in paper.get("url", ""))
        
        # ═══════════════════════════════════════════════════════════════════
        # CALENDAR
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{Y}📅 Calendar Cartridge:{W}")
        
        # Now
        r = requests.get(f"{CARTRIDGE_URL}/cartridge/calendar/now", timeout=3)
        data = r.json()
        self.check("Now endpoint", r.status_code == 200)
        self.check("Has datetime", "datetime" in data)
        self.check("Has day_of_week", "day_of_week" in data)
        
        # Parse dates
        test_queries = [
            ("today", True),
            ("tomorrow", True),
            ("next friday", True),
            ("in 3 days", True),
            ("end of month", True),
        ]
        
        for query, should_parse in test_queries:
            r = requests.post(f"{CARTRIDGE_URL}/cartridge/calendar/parse",
                            json={"query": query}, timeout=3)
            data = r.json()
            self.check(f"Parse '{query}'", data.get("parsed") == should_parse)
        
        # ═══════════════════════════════════════════════════════════════════
        # EXPORT
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{Y}📤 Export Cartridge:{W}")
        
        test_stacks = [{
            "id": "test_stack",
            "title": "Test Stack",
            "cards": [
                {"id": "card1", "content": "Test content", "trust": "verified", "sources": []},
                {"id": "card2", "content": "More content", "trust": "draft", "sources": []}
            ]
        }]
        
        # JSON export
        r = requests.post(f"{CARTRIDGE_URL}/cartridge/export/json",
                         json={"stacks": test_stacks}, timeout=5)
        data = r.json()
        self.check("JSON export", r.status_code == 200)
        self.check("JSON has content", len(data.get("content", "")) > 0)
        self.check("JSON has filename", data.get("filename", "").endswith(".json"))
        
        # Markdown export
        r = requests.post(f"{CARTRIDGE_URL}/cartridge/export/markdown",
                         json={"stacks": test_stacks}, timeout=5)
        data = r.json()
        self.check("Markdown export", r.status_code == 200)
        self.check("Markdown has content", "# parcStation Export" in data.get("content", ""))
        self.check("Markdown has filename", data.get("filename", "").endswith(".md"))
        
        # ═══════════════════════════════════════════════════════════════════
        # CODE
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{Y}💻 Code Cartridge:{W}")
        
        r = requests.post(f"{CARTRIDGE_URL}/cartridge/code/evaluate",
                         json={"code": "2 + 2"}, timeout=5)
        data = r.json()
        self.check("Code evaluate", r.status_code == 200)
        self.check("Code result", data.get("result") == "4")
        self.check("Code verified", data.get("verified") == True)
        
        # Complex math
        r = requests.post(f"{CARTRIDGE_URL}/cartridge/code/evaluate",
                         json={"code": "(3 * 4) + 5"}, timeout=5)
        data = r.json()
        self.check("Complex math", data.get("result") == "17")
        
        # ═══════════════════════════════════════════════════════════════════
        # DICTIONARY
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{Y}📖 Dictionary Cartridge:{W}")
        
        r = requests.post(f"{CARTRIDGE_URL}/cartridge/dictionary/define",
                         json={"word": "algorithm"}, timeout=10)
        data = r.json()
        self.check("Dictionary endpoint", r.status_code == 200)
        self.check("Word found", data.get("found") == True)
        self.check("Has definitions", len(data.get("definitions", [])) > 0)
        
        # ═══════════════════════════════════════════════════════════════════
        # SUMMARY
        # ═══════════════════════════════════════════════════════════════════
        print(f"\n{B}═══════════════════════════════{W}")
        total = self.passed + self.failed
        
        if self.failed == 0:
            print(f"  {G}✓ ALL CARTRIDGES WORKING{W}")
            print(f"  {self.passed}/{total} checks passed")
        else:
            print(f"  {R}✗ SOME CARTRIDGES FAILING{W}")
            print(f"  {self.passed}/{total} checks passed")
        
        print(f"{B}═══════════════════════════════{W}\n")
        
        return 0 if self.failed == 0 else 1


if __name__ == "__main__":
    test = CartridgeTest()
    sys.exit(test.run())
