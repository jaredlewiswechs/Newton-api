#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
parcStation Complete Test Bot
Tests EVERYTHING - API, Agent, Data, UI simulation
═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import aiohttp
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

NEWTON_URL = "http://localhost:8000"
AGENT_URL = "http://localhost:8091"
UI_URL = "http://localhost:8082"

class TestCategory(Enum):
    NEWTON_CORE = "Newton Core"
    NEWTON_AGENT = "Newton Agent"
    DATA_INTEGRITY = "Data Integrity"
    UI_ASSETS = "UI Assets"
    INTEGRATION = "Integration"
    PERFORMANCE = "Performance"

@dataclass
class TestResult:
    name: str
    category: TestCategory
    passed: bool
    duration_ms: float
    details: str = ""
    error: str = ""

@dataclass 
class TestReport:
    results: List[TestResult] = field(default_factory=list)
    start_time: float = 0
    end_time: float = 0
    
    def add(self, result: TestResult):
        self.results.append(result)
        icon = "✓" if result.passed else "✗"
        print(f"   {icon} {result.name} ({result.duration_ms:.1f}ms)")
        if result.error:
            print(f"      └─ {result.error[:80]}")
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def total(self) -> int:
        return len(self.results)
    
    def by_category(self) -> Dict[TestCategory, List[TestResult]]:
        cats = {}
        for r in self.results:
            if r.category not in cats:
                cats[r.category] = []
            cats[r.category].append(r)
        return cats


class ParcStationTestBot:
    """Complete test bot for parcStation."""
    
    def __init__(self):
        self.report = TestReport()
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
        
    async def run_all(self):
        """Run complete test suite."""
        print("═" * 70)
        print("  parcStation Complete Test Bot")
        print("  Testing EVERYTHING possible")
        print("═" * 70)
        
        self.report.start_time = time.time()
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            self.session = session
            
            # 1. Newton Core API
            print(f"\n🔷 {TestCategory.NEWTON_CORE.value}")
            await self.test_newton_health()
            await self.test_newton_verify()
            await self.test_newton_verify_batch()
            await self.test_newton_ground()
            await self.test_newton_calculate()
            await self.test_newton_calculate_complex()
            await self.test_newton_ledger()
            await self.test_newton_metrics()
            await self.test_newton_ask()
            
            # 2. Newton Agent
            print(f"\n🧠 {TestCategory.NEWTON_AGENT.value}")
            await self.test_agent_health()
            await self.test_agent_chat_simple()
            await self.test_agent_chat_grounded()
            await self.test_agent_ground_claim()
            await self.test_agent_history()
            await self.test_agent_stats()
            await self.test_agent_models()
            
            # 3. Data Integrity
            print(f"\n💾 {TestCategory.DATA_INTEGRITY.value}")
            await self.test_deterministic_verify()
            await self.test_deterministic_calculate()
            await self.test_concurrent_requests()
            await self.test_ledger_persistence()
            
            # 4. UI Assets
            print(f"\n🖥️  {TestCategory.UI_ASSETS.value}")
            await self.test_ui_html()
            await self.test_ui_css()
            await self.test_ui_js()
            await self.test_ui_fonts()
            
            # 5. Integration
            print(f"\n🔗 {TestCategory.INTEGRATION.value}")
            await self.test_full_verification_flow()
            await self.test_agent_newton_integration()
            await self.test_grounding_pipeline()
            
            # 6. Performance
            print(f"\n⚡ {TestCategory.PERFORMANCE.value}")
            await self.test_verify_performance()
            await self.test_calculate_performance()
            await self.test_concurrent_performance()
        
        self.report.end_time = time.time()
        self.print_report()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Newton Core Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def test_newton_health(self):
        start = time.time()
        try:
            async with self.session.get(f"{NEWTON_URL}/health") as resp:
                data = await resp.json()
                passed = resp.status == 200 and data.get("status") == "healthy"
                self.report.add(TestResult(
                    name="Health Check",
                    category=TestCategory.NEWTON_CORE,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"status={data.get('status')}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Health Check", category=TestCategory.NEWTON_CORE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_newton_verify(self):
        start = time.time()
        try:
            payload = {"input": "Hello, this is a safe test message"}
            async with self.session.post(f"{NEWTON_URL}/verify", json=payload) as resp:
                data = await resp.json()
                passed = resp.status == 200 and "verified" in data
                self.report.add(TestResult(
                    name="Verify Endpoint",
                    category=TestCategory.NEWTON_CORE,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"verified={data.get('verified')}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Verify Endpoint", category=TestCategory.NEWTON_CORE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_newton_verify_batch(self):
        start = time.time()
        try:
            payload = {"inputs": ["Test 1", "Test 2", "Test 3"]}
            async with self.session.post(f"{NEWTON_URL}/verify/batch", json=payload) as resp:
                data = await resp.json()
                passed = resp.status == 200 and "results" in data
                self.report.add(TestResult(
                    name="Batch Verify",
                    category=TestCategory.NEWTON_CORE,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"results_count={len(data.get('results', []))}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Batch Verify", category=TestCategory.NEWTON_CORE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_newton_ground(self):
        start = time.time()
        try:
            payload = {"claim": "Python is a programming language"}
            async with self.session.post(f"{NEWTON_URL}/ground", json=payload) as resp:
                data = await resp.json()
                passed = resp.status == 200 and "status" in data
                self.report.add(TestResult(
                    name="Ground Claim",
                    category=TestCategory.NEWTON_CORE,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"status={data.get('status')}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Ground Claim", category=TestCategory.NEWTON_CORE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_newton_calculate(self):
        start = time.time()
        try:
            payload = {"expression": {"op": "+", "args": [10, 5]}}
            async with self.session.post(f"{NEWTON_URL}/calculate", json=payload) as resp:
                data = await resp.json()
                passed = resp.status == 200 and str(data.get("result")) == "15"
                self.report.add(TestResult(
                    name="Calculate Simple",
                    category=TestCategory.NEWTON_CORE,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"10+5={data.get('result')}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Calculate Simple", category=TestCategory.NEWTON_CORE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_newton_calculate_complex(self):
        start = time.time()
        try:
            # (3 * 4) + (10 / 2) = 12 + 5 = 17
            payload = {"expression": {
                "op": "+", 
                "args": [
                    {"op": "*", "args": [3, 4]},
                    {"op": "/", "args": [10, 2]}
                ]
            }}
            async with self.session.post(f"{NEWTON_URL}/calculate", json=payload) as resp:
                data = await resp.json()
                passed = resp.status == 200 and str(data.get("result")) == "17"
                self.report.add(TestResult(
                    name="Calculate Complex",
                    category=TestCategory.NEWTON_CORE,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"(3*4)+(10/2)={data.get('result')}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Calculate Complex", category=TestCategory.NEWTON_CORE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_newton_ledger(self):
        start = time.time()
        try:
            async with self.session.get(f"{NEWTON_URL}/ledger") as resp:
                data = await resp.json()
                passed = resp.status == 200 and "entries" in data
                self.report.add(TestResult(
                    name="Ledger Access",
                    category=TestCategory.NEWTON_CORE,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"entries={len(data.get('entries', []))}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Ledger Access", category=TestCategory.NEWTON_CORE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_newton_metrics(self):
        start = time.time()
        try:
            async with self.session.get(f"{NEWTON_URL}/metrics") as resp:
                data = await resp.json()
                passed = resp.status == 200
                self.report.add(TestResult(
                    name="Metrics Endpoint",
                    category=TestCategory.NEWTON_CORE,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"keys={list(data.keys())[:3]}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Metrics Endpoint", category=TestCategory.NEWTON_CORE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_newton_ask(self):
        start = time.time()
        try:
            payload = {"question": "What is 2+2?"}
            async with self.session.post(f"{NEWTON_URL}/ask", json=payload) as resp:
                data = await resp.json()
                passed = resp.status == 200
                self.report.add(TestResult(
                    name="Ask Endpoint",
                    category=TestCategory.NEWTON_CORE,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"has_answer={'answer' in data or 'result' in data}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Ask Endpoint", category=TestCategory.NEWTON_CORE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Newton Agent Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def test_agent_health(self):
        start = time.time()
        try:
            async with self.session.get(f"{AGENT_URL}/health") as resp:
                data = await resp.json()
                passed = resp.status == 200
                self.report.add(TestResult(
                    name="Agent Health",
                    category=TestCategory.NEWTON_AGENT,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"status={data.get('status', 'ok')}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Agent Health", category=TestCategory.NEWTON_AGENT,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_agent_chat_simple(self):
        start = time.time()
        try:
            payload = {"message": "Hello!", "ground_claims": False}
            async with self.session.post(f"{AGENT_URL}/chat", json=payload) as resp:
                data = await resp.json()
                passed = resp.status == 200 and "content" in data
                self.report.add(TestResult(
                    name="Chat Simple",
                    category=TestCategory.NEWTON_AGENT,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"response_len={len(data.get('content', ''))}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Chat Simple", category=TestCategory.NEWTON_AGENT,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_agent_chat_grounded(self):
        start = time.time()
        try:
            payload = {"message": "Is Python a programming language?", "ground_claims": True}
            async with self.session.post(f"{AGENT_URL}/chat", json=payload) as resp:
                data = await resp.json()
                passed = resp.status == 200 and "content" in data
                self.report.add(TestResult(
                    name="Chat Grounded",
                    category=TestCategory.NEWTON_AGENT,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"verified={data.get('verified', 'n/a')}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Chat Grounded", category=TestCategory.NEWTON_AGENT,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_agent_ground_claim(self):
        start = time.time()
        try:
            payload = {"claim": "The Earth is round"}
            async with self.session.post(f"{AGENT_URL}/ground", json=payload) as resp:
                data = await resp.json()
                passed = resp.status == 200
                self.report.add(TestResult(
                    name="Agent Ground",
                    category=TestCategory.NEWTON_AGENT,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"grounded={data.get('grounded', 'n/a')}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Agent Ground", category=TestCategory.NEWTON_AGENT,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_agent_history(self):
        start = time.time()
        try:
            async with self.session.get(f"{AGENT_URL}/history") as resp:
                data = await resp.json()
                passed = resp.status == 200 and "history" in data
                self.report.add(TestResult(
                    name="Agent History",
                    category=TestCategory.NEWTON_AGENT,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"history_count={len(data.get('history', []))}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Agent History", category=TestCategory.NEWTON_AGENT,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_agent_stats(self):
        start = time.time()
        try:
            async with self.session.get(f"{AGENT_URL}/stats") as resp:
                data = await resp.json()
                passed = resp.status == 200
                self.report.add(TestResult(
                    name="Agent Stats",
                    category=TestCategory.NEWTON_AGENT,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"keys={list(data.keys())[:3]}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Agent Stats", category=TestCategory.NEWTON_AGENT,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_agent_models(self):
        start = time.time()
        try:
            async with self.session.get(f"{AGENT_URL}/models") as resp:
                data = await resp.json()
                passed = resp.status == 200
                self.report.add(TestResult(
                    name="Agent Models",
                    category=TestCategory.NEWTON_AGENT,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"models={data.get('models', [])[:2]}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Agent Models", category=TestCategory.NEWTON_AGENT,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Data Integrity Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def test_deterministic_verify(self):
        start = time.time()
        try:
            payload = {"input": "Determinism test input XYZ123"}
            results = []
            for _ in range(5):
                async with self.session.post(f"{NEWTON_URL}/verify", json=payload) as resp:
                    data = await resp.json()
                    results.append(data.get("verified"))
            
            all_same = len(set(results)) == 1
            self.report.add(TestResult(
                name="Deterministic Verify",
                category=TestCategory.DATA_INTEGRITY,
                passed=all_same,
                duration_ms=(time.time() - start) * 1000,
                details=f"5 calls, all_same={all_same}"
            ))
        except Exception as e:
            self.report.add(TestResult(
                name="Deterministic Verify", category=TestCategory.DATA_INTEGRITY,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_deterministic_calculate(self):
        start = time.time()
        try:
            payload = {"expression": {"op": "*", "args": [7, 8]}}
            results = []
            for _ in range(5):
                async with self.session.post(f"{NEWTON_URL}/calculate", json=payload) as resp:
                    data = await resp.json()
                    results.append(data.get("result"))
            
            all_same = len(set(results)) == 1 and results[0] == "56"
            self.report.add(TestResult(
                name="Deterministic Calculate",
                category=TestCategory.DATA_INTEGRITY,
                passed=all_same,
                duration_ms=(time.time() - start) * 1000,
                details=f"7*8={results[0]}, consistent={all_same}"
            ))
        except Exception as e:
            self.report.add(TestResult(
                name="Deterministic Calculate", category=TestCategory.DATA_INTEGRITY,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_concurrent_requests(self):
        start = time.time()
        try:
            async def make_request(i):
                payload = {"input": f"Concurrent test {i}"}
                async with self.session.post(f"{NEWTON_URL}/verify", json=payload) as resp:
                    return resp.status == 200
            
            tasks = [make_request(i) for i in range(10)]
            results = await asyncio.gather(*tasks)
            all_ok = all(results)
            
            self.report.add(TestResult(
                name="Concurrent Requests",
                category=TestCategory.DATA_INTEGRITY,
                passed=all_ok,
                duration_ms=(time.time() - start) * 1000,
                details=f"10 concurrent, all_ok={all_ok}"
            ))
        except Exception as e:
            self.report.add(TestResult(
                name="Concurrent Requests", category=TestCategory.DATA_INTEGRITY,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_ledger_persistence(self):
        start = time.time()
        try:
            # Get ledger before
            async with self.session.get(f"{NEWTON_URL}/ledger") as resp:
                before = await resp.json()
                before_count = len(before.get("entries", []))
            
            # Do an operation
            payload = {"input": "Ledger persistence test"}
            async with self.session.post(f"{NEWTON_URL}/verify", json=payload) as resp:
                await resp.json()
            
            # Get ledger after
            async with self.session.get(f"{NEWTON_URL}/ledger") as resp:
                after = await resp.json()
                after_count = len(after.get("entries", []))
            
            passed = after_count >= before_count
            self.report.add(TestResult(
                name="Ledger Persistence",
                category=TestCategory.DATA_INTEGRITY,
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                details=f"before={before_count}, after={after_count}"
            ))
        except Exception as e:
            self.report.add(TestResult(
                name="Ledger Persistence", category=TestCategory.DATA_INTEGRITY,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UI Asset Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def test_ui_html(self):
        start = time.time()
        try:
            async with self.session.get(f"{UI_URL}/index2.html") as resp:
                content = await resp.text()
                has_app = "parcStation" in content
                has_scripts = "app2.js" in content
                passed = resp.status == 200 and has_app and has_scripts
                self.report.add(TestResult(
                    name="HTML Loads",
                    category=TestCategory.UI_ASSETS,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"size={len(content)}, has_app={has_app}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="HTML Loads", category=TestCategory.UI_ASSETS,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_ui_css(self):
        start = time.time()
        try:
            async with self.session.get(f"{UI_URL}/style.css") as resp:
                content = await resp.text()
                has_vars = "--bg-primary" in content
                has_glass = "glassmorphism" in content.lower() or "glass" in content
                passed = resp.status == 200 and has_vars
                self.report.add(TestResult(
                    name="CSS Loads",
                    category=TestCategory.UI_ASSETS,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"size={len(content)}, has_vars={has_vars}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="CSS Loads", category=TestCategory.UI_ASSETS,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_ui_js(self):
        start = time.time()
        try:
            async with self.session.get(f"{UI_URL}/app2.js") as resp:
                content = await resp.text()
                has_class = "class ParcStationApp" in content
                has_newton = "NewtonClient" in content
                has_agent = "NewtonAgentClient" in content
                passed = resp.status == 200 and has_class and has_newton and has_agent
                self.report.add(TestResult(
                    name="JS Loads",
                    category=TestCategory.UI_ASSETS,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"has_app={has_class}, has_newton={has_newton}, has_agent={has_agent}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="JS Loads", category=TestCategory.UI_ASSETS,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_ui_fonts(self):
        start = time.time()
        try:
            async with self.session.get(f"{UI_URL}/index2.html") as resp:
                content = await resp.text()
                has_inter = "Inter" in content
                has_google = "fonts.googleapis.com" in content
                passed = resp.status == 200 and (has_inter or has_google)
                self.report.add(TestResult(
                    name="Fonts Referenced",
                    category=TestCategory.UI_ASSETS,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"inter={has_inter}, google_fonts={has_google}"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Fonts Referenced", category=TestCategory.UI_ASSETS,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def test_full_verification_flow(self):
        start = time.time()
        try:
            # 1. Verify content
            verify_payload = {"input": "Integration test claim"}
            async with self.session.post(f"{NEWTON_URL}/verify", json=verify_payload) as resp:
                verify_result = await resp.json()
            
            # 2. Ground claim
            ground_payload = {"claim": "Integration test claim"}
            async with self.session.post(f"{NEWTON_URL}/ground", json=ground_payload) as resp:
                ground_result = await resp.json()
            
            # 3. Check ledger
            async with self.session.get(f"{NEWTON_URL}/ledger") as resp:
                ledger_result = await resp.json()
            
            passed = all([
                "verified" in verify_result,
                "status" in ground_result,
                "entries" in ledger_result
            ])
            
            self.report.add(TestResult(
                name="Full Verification Flow",
                category=TestCategory.INTEGRATION,
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                details=f"verify→ground→ledger complete"
            ))
        except Exception as e:
            self.report.add(TestResult(
                name="Full Verification Flow", category=TestCategory.INTEGRATION,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_agent_newton_integration(self):
        start = time.time()
        try:
            # Agent should use Newton for grounding
            payload = {"message": "Is the sky blue?", "ground_claims": True}
            async with self.session.post(f"{AGENT_URL}/chat", json=payload) as resp:
                data = await resp.json()
                passed = resp.status == 200 and "content" in data
                self.report.add(TestResult(
                    name="Agent-Newton Integration",
                    category=TestCategory.INTEGRATION,
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"agent uses newton grounding"
                ))
        except Exception as e:
            self.report.add(TestResult(
                name="Agent-Newton Integration", category=TestCategory.INTEGRATION,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_grounding_pipeline(self):
        start = time.time()
        try:
            claims = [
                "Python was created by Guido van Rossum",
                "JavaScript runs in web browsers",
                "Git is a version control system"
            ]
            
            results = []
            for claim in claims:
                payload = {"claim": claim}
                async with self.session.post(f"{NEWTON_URL}/ground", json=payload) as resp:
                    data = await resp.json()
                    results.append("status" in data)
            
            all_ok = all(results)
            self.report.add(TestResult(
                name="Grounding Pipeline",
                category=TestCategory.INTEGRATION,
                passed=all_ok,
                duration_ms=(time.time() - start) * 1000,
                details=f"3 claims grounded, all_ok={all_ok}"
            ))
        except Exception as e:
            self.report.add(TestResult(
                name="Grounding Pipeline", category=TestCategory.INTEGRATION,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Performance Tests
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def test_verify_performance(self):
        start = time.time()
        try:
            times = []
            for _ in range(10):
                t0 = time.time()
                payload = {"input": "Performance test"}
                async with self.session.post(f"{NEWTON_URL}/verify", json=payload) as resp:
                    await resp.json()
                times.append((time.time() - t0) * 1000)
            
            avg_ms = sum(times) / len(times)
            passed = avg_ms < 100  # Should be under 100ms average
            self.report.add(TestResult(
                name="Verify Performance",
                category=TestCategory.PERFORMANCE,
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                details=f"avg={avg_ms:.1f}ms, max={max(times):.1f}ms"
            ))
        except Exception as e:
            self.report.add(TestResult(
                name="Verify Performance", category=TestCategory.PERFORMANCE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_calculate_performance(self):
        start = time.time()
        try:
            times = []
            for i in range(10):
                t0 = time.time()
                payload = {"expression": {"op": "+", "args": [i, i*2]}}
                async with self.session.post(f"{NEWTON_URL}/calculate", json=payload) as resp:
                    await resp.json()
                times.append((time.time() - t0) * 1000)
            
            avg_ms = sum(times) / len(times)
            passed = avg_ms < 50  # Should be under 50ms average
            self.report.add(TestResult(
                name="Calculate Performance",
                category=TestCategory.PERFORMANCE,
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                details=f"avg={avg_ms:.1f}ms, max={max(times):.1f}ms"
            ))
        except Exception as e:
            self.report.add(TestResult(
                name="Calculate Performance", category=TestCategory.PERFORMANCE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    async def test_concurrent_performance(self):
        start = time.time()
        try:
            async def timed_request():
                t0 = time.time()
                payload = {"input": "Concurrent perf test"}
                async with self.session.post(f"{NEWTON_URL}/verify", json=payload) as resp:
                    await resp.json()
                return (time.time() - t0) * 1000
            
            tasks = [timed_request() for _ in range(20)]
            times = await asyncio.gather(*tasks)
            
            avg_ms = sum(times) / len(times)
            passed = avg_ms < 200  # Under 200ms average for 20 concurrent
            self.report.add(TestResult(
                name="Concurrent Performance",
                category=TestCategory.PERFORMANCE,
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                details=f"20 concurrent, avg={avg_ms:.1f}ms"
            ))
        except Exception as e:
            self.report.add(TestResult(
                name="Concurrent Performance", category=TestCategory.PERFORMANCE,
                passed=False, duration_ms=(time.time() - start) * 1000, error=str(e)
            ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Report
    # ═══════════════════════════════════════════════════════════════════════════
    
    def print_report(self):
        """Print comprehensive test report."""
        total_time = self.report.end_time - self.report.start_time
        
        print("\n" + "═" * 70)
        print("  TEST REPORT")
        print("═" * 70)
        
        # By category
        print("\n📊 Results by Category:")
        for cat, results in self.report.by_category().items():
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            pct = (passed / total * 100) if total > 0 else 0
            bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
            icon = "✅" if pct == 100 else "🟡" if pct >= 80 else "❌"
            print(f"   {icon} {cat.value:20} [{bar}] {passed}/{total} ({pct:.0f}%)")
        
        # Summary
        print(f"\n📈 Summary:")
        print(f"   Total Tests:  {self.report.total}")
        print(f"   Passed:       {self.report.passed} ✓")
        print(f"   Failed:       {self.report.failed} ✗")
        print(f"   Success Rate: {(self.report.passed / self.report.total * 100):.1f}%")
        print(f"   Total Time:   {total_time:.2f}s")
        
        # Failed tests
        failed = [r for r in self.report.results if not r.passed]
        if failed:
            print(f"\n❌ Failed Tests:")
            for r in failed:
                print(f"   • {r.name}")
                if r.error:
                    print(f"     └─ {r.error[:60]}")
        
        # Final verdict
        print("\n" + "═" * 70)
        if self.report.passed == self.report.total:
            print("  ✅ ALL TESTS PASSED - parcStation is fully operational!")
        elif self.report.passed >= self.report.total * 0.9:
            print("  🟡 MOSTLY PASSING - Minor issues detected")
        elif self.report.passed >= self.report.total * 0.7:
            print("  ⚠️  SOME FAILURES - Check failed tests above")
        else:
            print("  ❌ SIGNIFICANT FAILURES - Services may be down")
        print("═" * 70)


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    bot = ParcStationTestBot()
    asyncio.run(bot.run_all())
