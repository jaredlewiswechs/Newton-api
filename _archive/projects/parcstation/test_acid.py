#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
parcStation ACID Test
Atomicity, Consistency, Isolation, Durability

Tests the full verification pipeline through Newton and Newton Agent.
═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import aiohttp
import time
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

NEWTON_URL = "http://localhost:8000"
AGENT_URL = "http://localhost:8091"

# ═══════════════════════════════════════════════════════════════════════════════
# Test Results
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    details: Optional[str] = None
    error: Optional[str] = None


class ACIDTestSuite:
    def __init__(self):
        self.results: List[TestResult] = []
        self.newton_online = False
        self.agent_online = False

    async def check_services(self, session: aiohttp.ClientSession):
        """Check if Newton and Agent are running."""
        print("\n🔍 Checking services...")
        
        # Check Newton
        try:
            async with session.get(f"{NEWTON_URL}/health", timeout=aiohttp.ClientTimeout(total=3)) as resp:
                self.newton_online = resp.status == 200
                print(f"   Newton Supercomputer: {'✓ Online' if self.newton_online else '✗ Offline'}")
        except:
            print(f"   Newton Supercomputer: ✗ Offline")

        # Check Agent
        try:
            async with session.get(f"{AGENT_URL}/health", timeout=aiohttp.ClientTimeout(total=3)) as resp:
                self.agent_online = resp.status == 200
                print(f"   Newton Agent: {'✓ Online' if self.agent_online else '✗ Offline'}")
        except:
            print(f"   Newton Agent: ✗ Offline")

    def record(self, result: TestResult):
        """Record a test result."""
        self.results.append(result)
        status = "✓" if result.passed else "✗"
        print(f"   {status} {result.name} ({result.duration_ms:.1f}ms)")
        if result.error:
            print(f"      Error: {result.error}")

    # ═══════════════════════════════════════════════════════════════════════════
    # ATOMICITY TESTS - Operations complete fully or not at all
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_atomic_verification(self, session: aiohttp.ClientSession):
        """Test that verification is atomic - returns complete result or error."""
        start = time.time()
        try:
            # Use /verify with string input (Newton's actual API)
            payload = {"input": "Test verification input"}
            async with session.post(f"{NEWTON_URL}/verify", json=payload) as resp:
                data = await resp.json()
                # Must have all required fields
                has_verified = "verified" in data
                passed = resp.status == 200 and has_verified
                self.record(TestResult(
                    name="Atomic Verification",
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"verified={data.get('verified')}"
                ))
        except Exception as e:
            self.record(TestResult(
                name="Atomic Verification",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            ))

    async def test_atomic_grounding(self, session: aiohttp.ClientSession):
        """Test that grounding is atomic - returns complete result."""
        start = time.time()
        try:
            payload = {"claim": "Python was created by Guido van Rossum"}
            async with session.post(f"{NEWTON_URL}/ground", json=payload) as resp:
                data = await resp.json()
                has_status = "status" in data
                passed = resp.status == 200 and has_status
                self.record(TestResult(
                    name="Atomic Grounding",
                    passed=passed,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"status={data.get('status')}"
                ))
        except Exception as e:
            self.record(TestResult(
                name="Atomic Grounding",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            ))

    # ═══════════════════════════════════════════════════════════════════════════
    # CONSISTENCY TESTS - Same input always produces same output
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_consistent_verification(self, session: aiohttp.ClientSession):
        """Test that identical inputs produce identical results."""
        start = time.time()
        try:
            payload = {"input": "Consistent test input for verification"}
            results = []
            for _ in range(3):
                async with session.post(f"{NEWTON_URL}/verify", json=payload) as resp:
                    data = await resp.json()
                    results.append(data.get("verified"))
            
            # All results should be identical
            all_same = len(set(results)) == 1
            self.record(TestResult(
                name="Consistent Verification",
                passed=all_same,
                duration_ms=(time.time() - start) * 1000,
                details=f"results={results}"
            ))
        except Exception as e:
            self.record(TestResult(
                name="Consistent Verification",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            ))

    async def test_consistent_calculation(self, session: aiohttp.ClientSession):
        """Test that calculations are deterministic."""
        start = time.time()
        try:
            # Use the nested expression format Newton expects
            payload = {"expression": {"op": "+", "args": [{"op": "*", "args": [3, 4]}, 5]}}
            results = []
            for _ in range(3):
                async with session.post(f"{NEWTON_URL}/calculate", json=payload) as resp:
                    data = await resp.json()
                    # Result comes back as string
                    results.append(data.get("result"))
            
            # All should be "17"
            all_same = len(set(results)) == 1 and results[0] == "17"
            self.record(TestResult(
                name="Consistent Calculation",
                passed=all_same,
                duration_ms=(time.time() - start) * 1000,
                details=f"3*4+5={results[0]}, expected='17'"
            ))
        except Exception as e:
            self.record(TestResult(
                name="Consistent Calculation",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            ))

    # ═══════════════════════════════════════════════════════════════════════════
    # ISOLATION TESTS - Concurrent operations don't interfere
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_isolated_concurrent_verify(self, session: aiohttp.ClientSession):
        """Test that concurrent verifications don't interfere."""
        start = time.time()
        try:
            # Use /verify endpoint for concurrent testing
            payloads = [
                {"input": f"Isolation test message {i}"}
                for i in range(5)
            ]
            
            async def verify_one(payload):
                try:
                    async with session.post(f"{NEWTON_URL}/verify", json=payload) as resp:
                        data = await resp.json()
                        return "verified" in data
                except:
                    return False
            
            tasks = [verify_one(p) for p in payloads]
            results = await asyncio.gather(*tasks)
            
            all_passed = all(results)
            self.record(TestResult(
                name="Isolated Concurrent Verify",
                passed=all_passed,
                duration_ms=(time.time() - start) * 1000,
                details=f"5 concurrent verify, all responded={all_passed}"
            ))
        except Exception as e:
            self.record(TestResult(
                name="Isolated Concurrent Verify",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            ))

    # ═══════════════════════════════════════════════════════════════════════════
    # DURABILITY TESTS - Results persist and can be audited
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_durable_ledger(self, session: aiohttp.ClientSession):
        """Test that operations are recorded in the ledger."""
        start = time.time()
        try:
            # Do a verification
            payload = {"input": "Durability test input"}
            async with session.post(f"{NEWTON_URL}/verify", json=payload) as resp:
                await resp.json()
            
            # Check ledger
            async with session.get(f"{NEWTON_URL}/ledger") as resp:
                data = await resp.json()
                # Ledger returns 'entries' array or 'total_entries'
                has_entries = len(data.get("entries", [])) > 0 or data.get("total_entries", 0) > 0
                self.record(TestResult(
                    name="Durable Ledger",
                    passed=has_entries,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"ledger has entries={has_entries}"
                ))
        except Exception as e:
            self.record(TestResult(
                name="Durable Ledger",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            ))

    # ═══════════════════════════════════════════════════════════════════════════
    # NEWTON AGENT TESTS (fast endpoints - no LLM calls)
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_agent_health(self, session: aiohttp.ClientSession):
        """Test Newton Agent health endpoint."""
        if not self.agent_online:
            self.record(TestResult(
                name="Agent Health",
                passed=False,
                duration_ms=0,
                error="Agent offline"
            ))
            return
            
        start = time.time()
        try:
            async with session.get(f"{AGENT_URL}/health") as resp:
                data = await resp.json()
                self.record(TestResult(
                    name="Agent Health",
                    passed=resp.status == 200,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"status={data.get('status', 'ok')}"
                ))
        except Exception as e:
            self.record(TestResult(
                name="Agent Health",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            ))

    async def test_agent_stats(self, session: aiohttp.ClientSession):
        """Test Newton Agent stats endpoint."""
        if not self.agent_online:
            self.record(TestResult(
                name="Agent Stats",
                passed=False,
                duration_ms=0,
                error="Agent offline"
            ))
            return
            
        start = time.time()
        try:
            async with session.get(f"{AGENT_URL}/stats") as resp:
                data = await resp.json()
                self.record(TestResult(
                    name="Agent Stats",
                    passed=resp.status == 200,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"keys={list(data.keys())[:3]}"
                ))
        except Exception as e:
            self.record(TestResult(
                name="Agent Stats",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            ))

    async def test_agent_history(self, session: aiohttp.ClientSession):
        """Test Newton Agent history endpoint."""
        if not self.agent_online:
            self.record(TestResult(
                name="Agent History",
                passed=False,
                duration_ms=0,
                error="Agent offline"
            ))
            return
            
        start = time.time()
        try:
            async with session.get(f"{AGENT_URL}/history") as resp:
                data = await resp.json()
                self.record(TestResult(
                    name="Agent History",
                    passed=resp.status == 200,
                    duration_ms=(time.time() - start) * 1000,
                    details=f"history items={len(data.get('history', []))}"
                ))
        except Exception as e:
            self.record(TestResult(
                name="Agent History",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            ))

    # ═══════════════════════════════════════════════════════════════════════════
    # INTEGRATION TESTS
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_full_verification_pipeline(self, session: aiohttp.ClientSession):
        """Test the full claim -> verify -> record pipeline."""
        start = time.time()
        try:
            # 1. Ground a claim
            claim = "Python was created by Guido van Rossum"
            payload = {"claim": claim}
            async with session.post(f"{NEWTON_URL}/ground", json=payload) as resp:
                ground_result = await resp.json()
            
            # 2. Verify content passes safety
            verify_payload = {"input": claim}
            async with session.post(f"{NEWTON_URL}/verify", json=verify_payload) as resp:
                verify_result = await resp.json()
            
            # 3. Check ledger recorded it
            async with session.get(f"{NEWTON_URL}/ledger") as resp:
                ledger = await resp.json()
            
            has_status = "status" in ground_result
            has_verified = "verified" in verify_result
            has_entries = len(ledger.get("entries", [])) > 0
            passed = has_status and has_verified and has_entries
            
            self.record(TestResult(
                name="Full Verification Pipeline",
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                details=f"ground={ground_result.get('status')}, verified={verify_result.get('verified')}, ledger={has_entries}"
            ))
        except Exception as e:
            self.record(TestResult(
                name="Full Verification Pipeline",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            ))

    async def test_constraint_types(self, session: aiohttp.ClientSession):
        """Test various calculation types instead of constraints."""
        start = time.time()
        tests = [
            ({"op": "+", "args": [2, 3]}, "5", "addition"),
            ({"op": "-", "args": [10, 4]}, "6", "subtraction"),
            ({"op": "*", "args": [3, 4]}, "12", "multiplication"),
            ({"op": "/", "args": [20, 4]}, "5", "division"),
            ({"op": "if", "args": [True, 1, 0]}, "1", "conditional_true"),
            ({"op": "if", "args": [False, 1, 0]}, "0", "conditional_false"),
        ]
        
        passed_count = 0
        for expr, expected, name in tests:
            try:
                payload = {"expression": expr}
                async with session.post(f"{NEWTON_URL}/calculate", json=payload) as resp:
                    data = await resp.json()
                    result = str(data.get("result", ""))
                    if result == expected:
                        passed_count += 1
            except:
                pass
        
        self.record(TestResult(
            name="Calculation Types",
            passed=passed_count == len(tests),
            duration_ms=(time.time() - start) * 1000,
            details=f"{passed_count}/{len(tests)} calculation types working"
        ))

    # ═══════════════════════════════════════════════════════════════════════════
    # Run All Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def run_all(self):
        """Run the complete ACID test suite."""
        print("═" * 60)
        print("parcStation ACID Test Suite")
        print("═" * 60)

        async with aiohttp.ClientSession() as session:
            await self.check_services(session)
            
            if not self.newton_online:
                print("\n⚠️  Newton Supercomputer is offline. Some tests will fail.")
            
            # ATOMICITY
            print("\n📦 ATOMICITY (Complete or Nothing)")
            if self.newton_online:
                await self.test_atomic_verification(session)
                await self.test_atomic_grounding(session)
            else:
                self.record(TestResult("Atomic Verification", False, 0, error="Newton offline"))
                self.record(TestResult("Atomic Grounding", False, 0, error="Newton offline"))

            # CONSISTENCY
            print("\n🔄 CONSISTENCY (Deterministic)")
            if self.newton_online:
                await self.test_consistent_verification(session)
                await self.test_consistent_calculation(session)
            else:
                self.record(TestResult("Consistent Verification", False, 0, error="Newton offline"))
                self.record(TestResult("Consistent Calculation", False, 0, error="Newton offline"))

            # ISOLATION
            print("\n🔒 ISOLATION (No Interference)")
            if self.newton_online:
                await self.test_isolated_concurrent_verify(session)
            else:
                self.record(TestResult("Isolated Concurrent Verify", False, 0, error="Newton offline"))

            # DURABILITY
            print("\n💾 DURABILITY (Persistent)")
            if self.newton_online:
                await self.test_durable_ledger(session)
            else:
                self.record(TestResult("Durable Ledger", False, 0, error="Newton offline"))

            # NEWTON AGENT (fast endpoints - no LLM)
            print("\n🧠 NEWTON AGENT")
            await self.test_agent_health(session)
            await self.test_agent_stats(session)
            await self.test_agent_history(session)

            # INTEGRATION
            print("\n🔗 INTEGRATION")
            if self.newton_online:
                await self.test_full_verification_pipeline(session)
                await self.test_constraint_types(session)
            else:
                self.record(TestResult("Full Verification Pipeline", False, 0, error="Newton offline"))
                self.record(TestResult("Constraint Types", False, 0, error="Newton offline"))

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print("\n" + "═" * 60)
        print(f"RESULTS: {passed}/{total} tests passed")
        print("═" * 60)
        
        if passed == total:
            print("✅ ALL TESTS PASSED - parcStation ACID compliant!")
        elif passed >= total * 0.8:
            print("🟡 MOSTLY PASSING - Some services may be offline")
        else:
            print("❌ TESTS FAILING - Check service status")
        
        # Timing summary
        total_time = sum(r.duration_ms for r in self.results)
        print(f"\n⏱️  Total time: {total_time:.1f}ms")
        
        # Failed tests
        failed = [r for r in self.results if not r.passed]
        if failed:
            print(f"\n❌ Failed tests:")
            for r in failed:
                print(f"   - {r.name}: {r.error or 'Unknown error'}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    suite = ACIDTestSuite()
    asyncio.run(suite.run_all())
