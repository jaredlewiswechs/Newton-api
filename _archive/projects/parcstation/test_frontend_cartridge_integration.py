#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
FRONTEND CARTRIDGE INTEGRATION TEST
End-to-end tests that verify the frontend JS calls work correctly

This test:
1. Parses app2.js to extract actual endpoint URLs and payload formats
2. Makes real HTTP requests exactly as the frontend would
3. Validates responses match what renderCartridgeResults() expects
4. Catches mismatches between frontend code and backend API

NO CHEATING - extracts real URLs from JS, makes real requests
═══════════════════════════════════════════════════════════════════════════════
"""

import requests
import sys
import os
import re
import json

G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
B = "\033[94m"
C = "\033[96m"
W = "\033[0m"


class FrontendCartridgeIntegrationTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.app2_content = None
        self.config = {}
        
    def check(self, name: str, condition: bool, detail: str = ""):
        if condition:
            print(f"  {G}✓{W} {name}")
            self.passed += 1
        else:
            print(f"  {R}✗{W} {name} {Y}({detail}){W}")
            self.failed += 1
        return condition
    
    def load_app2_js(self):
        """Load and parse app2.js to extract real configuration"""
        app2_path = os.path.join(os.path.dirname(__file__), "app2.js")
        with open(app2_path, "r", encoding="utf-8") as f:
            self.app2_content = f.read()
        
        # Extract CONFIG object values
        # Look for CONFIG = { ... CARTRIDGE_URL: 'http://...' ... }
        cartridge_match = re.search(r"CARTRIDGE_URL:\s*['\"]([^'\"]+)['\"]", self.app2_content)
        newton_match = re.search(r"NEWTON_URL:\s*['\"]([^'\"]+)['\"]", self.app2_content)
        
        self.config['CARTRIDGE_URL'] = cartridge_match.group(1) if cartridge_match else None
        self.config['NEWTON_URL'] = newton_match.group(1) if newton_match else None
        
        return bool(cartridge_match)
    
    def extract_method_endpoint(self, method_name: str):
        """Extract the actual endpoint URL and payload format from a JS method"""
        # Find fetch calls with CONFIG.CARTRIDGE_URL for this method pattern
        # Look for the actual API call, not UI handling methods
        
        # Pattern: find fetch with CONFIG.CARTRIDGE_URL or CONFIG.NEWTON_URL and method name nearby
        fetch_patterns = [
            # Pattern 1: async method(param) { ... fetch(`${CONFIG.URL}/path`
            rf"async\s+{method_name}\s*\(\w+\)\s*\{{[^{{}}]*?fetch\(`\$\{{([^}}]+)\}}/([^`]+)`",
            # Pattern 2: Look for the specific URL pattern with the method name
            rf"{method_name}[^{{}}]*\{{[^{{}}]*fetch\(`\$\{{(CONFIG\.[A-Z_]+)\}}/([^`]+)`",
        ]
        
        for pattern in fetch_patterns:
            match = re.search(pattern, self.app2_content, re.DOTALL)
            if match:
                config_key = match.group(1)
                endpoint_path = match.group(2)
                
                # Resolve the config key
                if "CARTRIDGE_URL" in config_key:
                    base_url = self.config['CARTRIDGE_URL']
                elif "NEWTON_URL" in config_key:
                    base_url = self.config['NEWTON_URL']
                else:
                    base_url = None
                
                if base_url:
                    return {
                        'base_url': base_url,
                        'path': endpoint_path,
                        'full_url': f"{base_url}/{endpoint_path}",
                        'config_key': config_key
                    }
        
        return None
    
    def test_wikipedia_integration(self):
        """Test Wikipedia cartridge exactly as frontend calls it"""
        print(f"\n{C}📚 Wikipedia Frontend Integration:{W}")
        
        # Extract how frontend calls it
        endpoint_info = self.extract_method_endpoint("searchWikipedia")
        self.check("searchWikipedia endpoint extracted", endpoint_info is not None)
        
        if not endpoint_info:
            return
        
        self.check("Uses CARTRIDGE_URL", "localhost:8093" in endpoint_info['full_url'])
        self.check("Correct path", endpoint_info['path'] == "cartridge/wikipedia/search")
        
        # Make request exactly as frontend would
        # Frontend: body: JSON.stringify({ query })
        user_input = "Python programming"
        payload = {"query": user_input}
        
        try:
            resp = requests.post(endpoint_info['full_url'], json=payload, timeout=15)
            data = resp.json()
            
            self.check("Request succeeds", resp.status_code == 200)
            self.check("Has 'results' array", isinstance(data.get("results"), list))
            
            # Verify response matches what renderCartridgeResults expects:
            # data.results.map(r => ... r.url, r.title, r.snippet ...)
            if data.get("results"):
                r = data["results"][0]
                self.check("Result has 'url'", "url" in r, f"keys: {list(r.keys())}")
                self.check("Result has 'title'", "title" in r, f"keys: {list(r.keys())}")
                self.check("Result has 'snippet'", "snippet" in r, f"keys: {list(r.keys())}")
        except Exception as e:
            self.check("Request completed", False, str(e))
    
    def test_arxiv_integration(self):
        """Test arXiv cartridge exactly as frontend calls it"""
        print(f"\n{C}📄 arXiv Frontend Integration:{W}")
        
        endpoint_info = self.extract_method_endpoint("searchArxiv")
        self.check("searchArxiv endpoint extracted", endpoint_info is not None)
        
        if not endpoint_info:
            return
        
        self.check("Uses CARTRIDGE_URL", "localhost:8093" in endpoint_info['full_url'])
        self.check("Correct path", endpoint_info['path'] == "cartridge/arxiv/search")
        
        # Frontend: body: JSON.stringify({ query })
        user_input = "neural networks"
        payload = {"query": user_input}
        
        try:
            resp = requests.post(endpoint_info['full_url'], json=payload, timeout=20)
            data = resp.json()
            
            self.check("Request succeeds", resp.status_code == 200)
            self.check("Has 'results' array", isinstance(data.get("results"), list))
            
            # renderCartridgeResults expects: r.url, r.title, r.authors, r.summary, r.pdf_url
            if data.get("results"):
                r = data["results"][0]
                self.check("Result has 'url'", "url" in r, f"keys: {list(r.keys())}")
                self.check("Result has 'title'", "title" in r, f"keys: {list(r.keys())}")
                self.check("Result has 'authors'", "authors" in r, f"keys: {list(r.keys())}")
                self.check("Result has 'summary'", "summary" in r, f"keys: {list(r.keys())}")
        except Exception as e:
            self.check("Request completed", False, str(e))
    
    def test_calculator_integration(self):
        """Test Calculator cartridge exactly as frontend calls it"""
        print(f"\n{C}🧮 Calculator Frontend Integration:{W}")
        
        endpoint_info = self.extract_method_endpoint("calculate")
        self.check("calculate endpoint extracted", endpoint_info is not None)
        
        if not endpoint_info:
            return
        
        self.check("Uses CARTRIDGE_URL", "localhost:8093" in endpoint_info['full_url'])
        self.check("Correct path", endpoint_info['path'] == "cartridge/code/evaluate")
        
        # Frontend: body: JSON.stringify({ code: expression })
        # User types "2+2" in the cartridge search box
        user_input = "2+2"
        payload = {"code": user_input}
        
        try:
            resp = requests.post(endpoint_info['full_url'], json=payload, timeout=10)
            data = resp.json()
            
            self.check("Request succeeds", resp.status_code == 200)
            
            # renderCartridgeResults expects: data.result, data.input, data.verified
            self.check("Has 'result'", "result" in data, f"keys: {list(data.keys())}")
            self.check("Result is correct", str(data.get("result")) == "4", f"got: {data.get('result')}")
            self.check("Has 'input' for display", "input" in data, f"keys: {list(data.keys())}")
            self.check("Has 'verified' flag", "verified" in data, f"keys: {list(data.keys())}")
            
            # Test complex expressions users might type
            complex_tests = [
                ("(3 * 4) + 5", "17"),
                ("100 / 4", "25.0"),
                ("2 ** 8", "256"),
            ]
            for expr, expected in complex_tests:
                resp2 = requests.post(endpoint_info['full_url'], json={"code": expr}, timeout=10)
                data2 = resp2.json()
                self.check(f"'{expr}' = {expected}", str(data2.get("result")) == expected, 
                          f"got: {data2.get('result')}")
                
        except Exception as e:
            self.check("Request completed", False, str(e))
    
    def test_calendar_integration(self):
        """Test Calendar cartridge exactly as frontend calls it"""
        print(f"\n{C}📅 Calendar Frontend Integration:{W}")
        
        endpoint_info = self.extract_method_endpoint("parseDate")
        self.check("parseDate endpoint extracted", endpoint_info is not None)
        
        if not endpoint_info:
            return
        
        self.check("Uses CARTRIDGE_URL", "localhost:8093" in endpoint_info['full_url'])
        self.check("Correct path", endpoint_info['path'] == "cartridge/calendar/parse")
        
        # Frontend: body: JSON.stringify({ query })
        user_input = "tomorrow"
        payload = {"query": user_input}
        
        try:
            resp = requests.post(endpoint_info['full_url'], json=payload, timeout=10)
            data = resp.json()
            
            self.check("Request succeeds", resp.status_code == 200)
            
            # renderCartridgeResults expects: data.datetime OR data.date, data.formatted, data.iso
            self.check("Has 'datetime' or 'date'", "datetime" in data or "date" in data, f"keys: {list(data.keys())}")
            self.check("Has 'formatted' for display", "formatted" in data, f"keys: {list(data.keys())}")
            
            # Test various user inputs
            date_tests = ["today", "next friday", "in 3 days", "end of month"]
            for query in date_tests:
                resp2 = requests.post(endpoint_info['full_url'], json={"query": query}, timeout=10)
                data2 = resp2.json()
                self.check(f"Parse '{query}'", data2.get("parsed") == True, f"got: {data2}")
                
        except Exception as e:
            self.check("Request completed", False, str(e))
    
    def test_dictionary_integration(self):
        """Test Dictionary - uses external API, verify frontend code pattern"""
        print(f"\n{C}📖 Dictionary Frontend Integration:{W}")
        
        # Dictionary uses external API: https://api.dictionaryapi.dev/api/v2/entries/en/{word}
        # Frontend wraps response as: { results: [...], type: 'dictionary' }
        
        # Verify the pattern exists in app2.js
        dict_pattern = re.search(r"defineWord.*dictionaryapi\.dev", self.app2_content, re.DOTALL)
        self.check("defineWord uses dictionaryapi.dev", dict_pattern is not None)
        
        # Verify it wraps with type: 'dictionary'
        wrap_pattern = re.search(r"return\s*\{\s*results:.*type:\s*['\"]dictionary['\"]", self.app2_content, re.DOTALL)
        self.check("Wraps response with type='dictionary'", wrap_pattern is not None)
        
        # Test the actual API
        user_input = "algorithm"
        try:
            resp = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{user_input}", timeout=10)
            
            if resp.status_code == 200:
                raw_data = resp.json()
                # Frontend wraps as { results: raw_data, type: 'dictionary' }
                data = {"results": raw_data, "type": "dictionary"}
                
                self.check("External API works", True)
                
                # renderCartridgeResults expects: data.results[0].word, .phonetic, .meanings
                word = data["results"][0]
                self.check("Has 'word'", "word" in word, f"keys: {list(word.keys())}")
                self.check("Has 'meanings'", "meanings" in word, f"keys: {list(word.keys())}")
                
                if word.get("meanings"):
                    m = word["meanings"][0]
                    self.check("Meaning has 'partOfSpeech'", "partOfSpeech" in m)
                    self.check("Meaning has 'definitions'", "definitions" in m)
            else:
                self.check("External API works", False, f"status: {resp.status_code}")
                
        except Exception as e:
            self.check("External API reachable", False, str(e))
    
    def test_no_results_fallback(self):
        """Test that 'No results found' only shows for actual empty results"""
        print(f"\n{C}🔍 No Results Fallback Logic:{W}")
        
        # The renderCartridgeResults has this fallback:
        # else { resultsEl.innerHTML = '<div class="cartridge-empty">No results found</div>'; }
        
        # This should ONLY trigger if none of these match:
        # 1. data.results && currentCartridge === 'wikipedia'
        # 2. data.results && currentCartridge === 'arxiv'
        # 3. data.result !== undefined && (currentCartridge === 'calculator' || data.verified !== undefined)
        # 4. data.date
        # 5. data.type === 'dictionary' && data.results
        
        # Test: Calculator response should have 'result' field
        calc_url = f"{self.config['CARTRIDGE_URL']}/cartridge/code/evaluate"
        resp = requests.post(calc_url, json={"code": "1+1"}, timeout=5)
        data = resp.json()
        
        # Verify calculator won't hit fallback
        has_result = data.get("result") is not None
        has_verified = data.get("verified") is not None
        self.check("Calculator: has 'result' (avoids fallback)", has_result)
        self.check("Calculator: has 'verified' (extra safety)", has_verified)
        
        # Test: Calendar response should have 'datetime' or 'date' field (frontend checks both)
        cal_url = f"{self.config['CARTRIDGE_URL']}/cartridge/calendar/parse"
        resp = requests.post(cal_url, json={"query": "today"}, timeout=5)
        data = resp.json()
        
        has_datetime_or_date = "datetime" in data or "date" in data
        self.check("Calendar: has 'datetime' or 'date'", has_datetime_or_date, f"keys: {list(data.keys())}")
        
        # Test: Wikipedia should have 'results' array
        wiki_url = f"{self.config['CARTRIDGE_URL']}/cartridge/wikipedia/search"
        resp = requests.post(wiki_url, json={"query": "test"}, timeout=15)
        data = resp.json()
        
        has_results = isinstance(data.get("results"), list)
        self.check("Wikipedia: has 'results' array (avoids fallback)", has_results)
    
    def test_error_handling(self):
        """Test that error responses are handled correctly"""
        print(f"\n{C}⚠️ Error Handling:{W}")
        
        # renderCartridgeResults checks: if (data.error) { show error }
        
        # Test invalid calculator expression
        calc_url = f"{self.config['CARTRIDGE_URL']}/cartridge/code/evaluate"
        resp = requests.post(calc_url, json={"code": "import os; os.system('bad')"}, timeout=5)
        data = resp.json()
        
        # Should either have error or be safely handled
        is_safe = data.get("error") or data.get("result") is not None
        self.check("Invalid code handled safely", is_safe)
    
    def run(self):
        print(f"\n{B}═══ FRONTEND CARTRIDGE INTEGRATION TEST ═══{W}")
        print(f"{Y}Testing exactly what happens when user uses cartridges{W}\n")
        
        # Load and parse app2.js
        print(f"{Y}Loading Frontend Code:{W}")
        if not self.load_app2_js():
            print(f"  {R}✗ Could not load app2.js{W}")
            return 1
        
        self.check("app2.js loaded", self.app2_content is not None)
        self.check("CARTRIDGE_URL extracted", self.config.get('CARTRIDGE_URL') is not None,
                   f"got: {self.config.get('CARTRIDGE_URL')}")
        
        # Check service is running
        print(f"\n{Y}Service Check:{W}")
        try:
            r = requests.get(f"{self.config['CARTRIDGE_URL']}/health", timeout=3)
            self.check("Cartridge service running", r.status_code == 200)
        except:
            print(f"  {R}✗ Cartridge service not running{W}")
            print(f"  {Y}Start with: python cartridges.py{W}")
            return 1
        
        # Run all integration tests
        self.test_wikipedia_integration()
        self.test_arxiv_integration()
        self.test_calculator_integration()
        self.test_calendar_integration()
        self.test_dictionary_integration()
        self.test_no_results_fallback()
        self.test_error_handling()
        
        # Summary
        print(f"\n{B}═══════════════════════════════════════════{W}")
        total = self.passed + self.failed
        
        if self.failed == 0:
            print(f"  {G}✓ ALL FRONTEND INTEGRATIONS WORKING{W}")
            print(f"  {self.passed}/{total} checks passed")
        else:
            print(f"  {R}✗ SOME INTEGRATIONS FAILING{W}")
            print(f"  {G}{self.passed}{W}/{total} passed, {R}{self.failed}{W} failed")
        
        print(f"{B}═══════════════════════════════════════════{W}\n")
        
        return 0 if self.failed == 0 else 1


if __name__ == "__main__":
    test = FrontendCartridgeIntegrationTest()
    sys.exit(test.run())
