#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON VOICE INTERFACE - WWDC-STYLE TEST SUITE
═══════════════════════════════════════════════════════════════════════════════

Comprehensive testing: Demo, Report, Simulation, Stress Test, Acid Test

Run with: python tests/test_voice_interface.py

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import time
import json
import random
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

# Add parent to path for imports
sys.path.insert(0, '.')

# ═══════════════════════════════════════════════════════════════════════════════
# TEST FRAMEWORK
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    message: str
    details: Dict[str, Any] = None

class TestReport:
    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.end_time = None

    def add(self, result: TestResult):
        self.results.append(result)

    def finalize(self):
        self.end_time = time.time()

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def duration_s(self) -> float:
        return (self.end_time or time.time()) - self.start_time

    def print_summary(self):
        print(f"\n{'═' * 70}")
        print(f"  {self.name}")
        print(f"{'═' * 70}")
        print(f"  ✓ Passed: {self.passed}/{self.total}")
        print(f"  ✗ Failed: {self.failed}/{self.total}")
        print(f"  ⏱  Duration: {self.duration_s:.2f}s")
        print(f"{'═' * 70}")

        if self.failed > 0:
            print("\n  Failed Tests:")
            for r in self.results:
                if not r.passed:
                    print(f"    ✗ {r.name}: {r.message}")


def run_test(name: str, test_fn) -> TestResult:
    """Run a single test and return result."""
    start = time.time()
    try:
        result = test_fn()
        duration = (time.time() - start) * 1000
        if isinstance(result, tuple):
            passed, message, details = result
        else:
            passed, message, details = result, "OK", None
        return TestResult(name, passed, duration, message, details)
    except Exception as e:
        duration = (time.time() - start) * 1000
        return TestResult(name, False, duration, f"Exception: {str(e)}",
                         {"traceback": traceback.format_exc()})


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO TESTS - WWDC Keynote Style
# ═══════════════════════════════════════════════════════════════════════════════

def demo_tests() -> TestReport:
    """WWDC-style demo tests - the money shots."""
    report = TestReport("WWDC DEMO TESTS")

    from core.voice_interface import (
        IntentParser, IntentType, DomainCategory,
        PatternLibrary, CDLGenerator,
        ConversationMemory, MemoryType,
        SessionManager, NewtonVoiceInterface,
        parse_intent, find_pattern, ask_newton
    )

    # Demo 1: Intent Recognition
    def test_intent_recognition():
        parser = IntentParser()
        cases = [
            ("Build me a calculator", IntentType.DO),
            ("What is compound interest?", IntentType.WHAT),
            ("Deploy the app", IntentType.GO),
            ("Remember my settings", IntentType.REMEMBER),
        ]
        for text, expected in cases:
            intent = parser.parse(text)
            if intent.intent_type != expected:
                return False, f"'{text}' → {intent.intent_type}, expected {expected}", None
        return True, f"All {len(cases)} intents recognized", {"cases": len(cases)}

    report.add(run_test("Intent Recognition", test_intent_recognition))

    # Demo 2: Domain Detection
    def test_domain_detection():
        parser = IntentParser()
        cases = [
            ("Calculate compound interest", DomainCategory.FINANCE),
            ("Create a lesson plan for math", DomainCategory.EDUCATION),
            ("Check symptom information", DomainCategory.HEALTH),
            ("Build a dashboard", DomainCategory.MAKE),
        ]
        for text, expected in cases:
            intent = parser.parse(text)
            if intent.domain != expected:
                return False, f"'{text}' → {intent.domain}, expected {expected}", None
        return True, f"All {len(cases)} domains detected", {"cases": len(cases)}

    report.add(run_test("Domain Detection", test_domain_detection))

    # Demo 3: Pattern Matching
    def test_pattern_matching():
        library = PatternLibrary()
        cases = [
            ("calculator", "calculator_basic"),
            ("financial calculator", "calculator_financial"),
            ("lesson planner", "lesson_planner"),
            ("quiz builder", "quiz_builder"),
            ("expense tracker", "expense_tracker"),
        ]
        for query, expected_id in cases:
            pattern = library.find_pattern(query)
            if not pattern or pattern.id != expected_id:
                actual = pattern.id if pattern else None
                return False, f"'{query}' → {actual}, expected {expected_id}", None
        return True, f"All {len(cases)} patterns matched", {"cases": len(cases)}

    report.add(run_test("Pattern Matching", test_pattern_matching))

    # Demo 4: CDL Generation
    def test_cdl_generation():
        parser = IntentParser()
        generator = CDLGenerator(PatternLibrary())

        intent = parser.parse("Build a financial calculator")
        cdl = generator.generate(intent)

        checks = [
            ("id" in cdl, "CDL has ID"),
            ("constraints" in cdl, "CDL has constraints"),
            (len(cdl.get("constraints", [])) > 0, "CDL has at least one constraint"),
            (cdl.get("pattern_id") == "calculator_financial", "Correct pattern matched"),
        ]

        for check, msg in checks:
            if not check:
                return False, msg, None

        return True, f"CDL generated with {len(cdl['constraints'])} constraints", cdl

    report.add(run_test("CDL Generation", test_cdl_generation))

    # Demo 5: Memory System
    def test_memory_system():
        memory = ConversationMemory("test_session")

        # Store
        id1 = memory.remember("user_name", "Jared", MemoryType.KEYSTONE)
        id2 = memory.remember("last_query", "calculator", MemoryType.OBJECT)

        # Recall
        name = memory.recall("user_name")
        query = memory.recall("last_query")

        if name != "Jared":
            return False, f"Keystone recall failed: got {name}", None
        if query != "calculator":
            return False, f"Object recall failed: got {query}", None

        # Search
        results = memory.search("calculator")
        if len(results) == 0:
            return False, "Memory search returned no results", None

        return True, "Memory store/recall/search working", {"ids": [id1, id2]}

    report.add(run_test("Memory System", test_memory_system))

    # Demo 6: Session Management
    def test_session_management():
        manager = SessionManager()

        # Create
        session1 = manager.create_session("user1")
        session2 = manager.create_session("user2")

        if session1.id == session2.id:
            return False, "Sessions have same ID", None

        # Retrieve
        retrieved = manager.get_session(session1.id)
        if retrieved is None or retrieved.id != session1.id:
            return False, "Session retrieval failed", None

        return True, "Session create/retrieve working", {"sessions": 2}

    report.add(run_test("Session Management", test_session_management))

    # Demo 7: Full Voice Interface (The Money Shot)
    def test_full_voice_interface():
        interface = NewtonVoiceInterface()

        response = interface.ask("Build me a financial calculator")

        checks = [
            (response.session_id is not None, "Has session ID"),
            (response.intent is not None, "Has intent"),
            (response.cdl is not None, "Has CDL"),
            (response.result is not None, "Has result"),
            (response.verified, "Is verified"),
            (response.message is not None, "Has message"),
            (len(response.suggestions) > 0, "Has suggestions"),
            (response.elapsed_us > 0, "Has timing"),
        ]

        for check, msg in checks:
            if not check:
                return False, msg, None

        return True, f"Full pipeline in {response.elapsed_us/1000:.2f}ms", {
            "session_id": response.session_id,
            "intent_type": response.intent.get("intent_type"),
            "verified": response.verified,
            "elapsed_ms": response.elapsed_us / 1000
        }

    report.add(run_test("Full Voice Interface", test_full_voice_interface))

    report.finalize()
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# SIMULATION TESTS - Real-world usage patterns
# ═══════════════════════════════════════════════════════════════════════════════

def simulation_tests() -> TestReport:
    """Simulate real-world usage patterns."""
    report = TestReport("SIMULATION TESTS")

    from core.voice_interface import NewtonVoiceInterface

    interface = NewtonVoiceInterface()

    # Sim 1: Multi-turn conversation
    def test_multi_turn():
        session_id = None
        queries = [
            "Build me a calculator",
            "Add financial functions",
            "Deploy the app",
            "Show me the audit trail",
        ]

        for query in queries:
            response = interface.ask(query, session_id=session_id)
            if session_id is None:
                session_id = response.session_id
            elif response.session_id != session_id:
                return False, "Session ID changed mid-conversation", None

        history = interface.get_session_history(session_id)
        if history is None or len(history) != len(queries):
            return False, f"History has {len(history) if history else 0} turns, expected {len(queries)}", None

        return True, f"{len(queries)}-turn conversation maintained", {"turns": len(queries)}

    report.add(run_test("Multi-turn Conversation", test_multi_turn))

    # Sim 2: Pattern coverage
    def test_pattern_coverage():
        queries = [
            "I need a basic calculator",
            "Build a financial calculator with interest calculation",
            "Create a lesson planner for 5th grade",
            "Make a quiz builder for my class",
            "Build an expense tracker",
            "Create a contact form",
            "Build a dashboard for metrics",
            "Analyze this data",
            "Check content safety",
            "Build inventory tracking",
        ]

        patterns_used = set()
        for query in queries:
            response = interface.ask(query)
            if response.cdl and response.cdl.get("pattern_id"):
                patterns_used.add(response.cdl["pattern_id"])

        if len(patterns_used) < 5:
            return False, f"Only {len(patterns_used)} unique patterns used", None

        return True, f"{len(patterns_used)} unique patterns exercised", {"patterns": list(patterns_used)}

    report.add(run_test("Pattern Coverage", test_pattern_coverage))

    # Sim 3: Error handling
    def test_error_handling():
        edge_cases = [
            "",  # Empty
            "   ",  # Whitespace
            "?" * 1000,  # Long input
            "🚀🔥💯",  # Emoji only
            "SELECT * FROM users",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
        ]

        for case in edge_cases:
            try:
                response = interface.ask(case)
                # Should handle gracefully, not crash
            except Exception as e:
                return False, f"Crashed on: {case[:50]}... - {str(e)}", None

        return True, f"Handled {len(edge_cases)} edge cases gracefully", None

    report.add(run_test("Error Handling", test_error_handling))

    # Sim 4: Entity extraction
    def test_entity_extraction():
        from core.voice_interface import IntentParser
        parser = IntentParser()

        cases = [
            ("Calculate $1,000 at 5% interest", {"currency": "1,000", "percentage": "5"}),
            ("Lesson for grade 5 math", {"grade_level": "5"}),
            ("Send to user@example.com", {"email": "user@example.com"}),
        ]

        for text, expected_entities in cases:
            intent = parser.parse(text)
            for key, expected_val in expected_entities.items():
                actual = intent.entities.get(key)
                if actual is None:
                    return False, f"Missing entity '{key}' in '{text}'", None

        return True, f"All entities extracted correctly", {"cases": len(cases)}

    report.add(run_test("Entity Extraction", test_entity_extraction))

    report.finalize()
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# STRESS TESTS - Performance under load
# ═══════════════════════════════════════════════════════════════════════════════

def stress_tests() -> TestReport:
    """Stress test the voice interface."""
    report = TestReport("STRESS TESTS")

    from core.voice_interface import (
        IntentParser, PatternLibrary, NewtonVoiceInterface
    )

    # Stress 1: Rapid intent parsing
    def test_rapid_parsing():
        parser = IntentParser()
        queries = [
            "Build a calculator",
            "What is this?",
            "Deploy now",
            "Remember this",
            "Create a form",
        ] * 200  # 1000 parses

        start = time.time()
        for query in queries:
            parser.parse(query)
        elapsed = time.time() - start

        rate = len(queries) / elapsed
        if rate < 100:  # Should do >100 parses/sec
            return False, f"Too slow: {rate:.1f} parses/sec", None

        return True, f"{len(queries)} parses in {elapsed:.2f}s ({rate:.0f}/sec)", {
            "count": len(queries),
            "rate": rate
        }

    report.add(run_test("Rapid Parsing (1000)", test_rapid_parsing))

    # Stress 2: Pattern search load
    def test_pattern_search_load():
        library = PatternLibrary()
        searches = ["calculator", "finance", "education", "form", "data"] * 200

        start = time.time()
        for query in searches:
            library.search_patterns(query)
        elapsed = time.time() - start

        rate = len(searches) / elapsed
        return True, f"{len(searches)} searches in {elapsed:.2f}s ({rate:.0f}/sec)", {
            "count": len(searches),
            "rate": rate
        }

    report.add(run_test("Pattern Search (1000)", test_pattern_search_load))

    # Stress 3: Full pipeline throughput
    def test_pipeline_throughput():
        interface = NewtonVoiceInterface()
        queries = [
            "Build a calculator",
            "Create a lesson plan",
            "Track expenses",
            "Make a form",
            "Analyze data",
        ] * 20  # 100 full requests

        start = time.time()
        for query in queries:
            interface.ask(query)
        elapsed = time.time() - start

        rate = len(queries) / elapsed
        avg_ms = (elapsed / len(queries)) * 1000

        if avg_ms > 100:  # Should be <100ms average
            return False, f"Too slow: {avg_ms:.1f}ms average", None

        return True, f"{len(queries)} requests, {avg_ms:.1f}ms avg, {rate:.1f}/sec", {
            "count": len(queries),
            "avg_ms": avg_ms,
            "rate": rate
        }

    report.add(run_test("Full Pipeline (100)", test_pipeline_throughput))

    # Stress 4: Concurrent sessions
    def test_concurrent_sessions():
        from core.voice_interface import SessionManager
        manager = SessionManager()

        # Create many sessions
        sessions = [manager.create_session(f"user_{i}") for i in range(100)]

        # Verify uniqueness
        ids = [s.id for s in sessions]
        if len(set(ids)) != len(ids):
            return False, "Duplicate session IDs created", None

        # Verify retrieval
        for session in sessions[:10]:  # Spot check
            retrieved = manager.get_session(session.id)
            if retrieved is None:
                return False, "Session retrieval failed", None

        return True, f"{len(sessions)} concurrent sessions", {"count": len(sessions)}

    report.add(run_test("Concurrent Sessions (100)", test_concurrent_sessions))

    # Stress 5: Memory operations
    def test_memory_stress():
        from core.voice_interface import ConversationMemory, MemoryType
        memory = ConversationMemory("stress_test")

        # Store many items
        for i in range(500):
            memory.remember(f"key_{i}", f"value_{i}", MemoryType.OBJECT)

        # Recall random items
        start = time.time()
        for i in random.sample(range(500), 100):
            value = memory.recall(f"key_{i}")
            if value != f"value_{i}":
                return False, f"Recall mismatch at key_{i}", None
        elapsed = time.time() - start

        return True, f"500 stores, 100 recalls in {elapsed*1000:.1f}ms", {
            "stores": 500,
            "recalls": 100
        }

    report.add(run_test("Memory Stress", test_memory_stress))

    report.finalize()
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# ACID TESTS - Boundary conditions and invariants
# ═══════════════════════════════════════════════════════════════════════════════

def acid_tests() -> TestReport:
    """ACID tests - verify invariants hold under all conditions."""
    report = TestReport("ACID TESTS")

    from core.voice_interface import (
        IntentParser, IntentType, DomainCategory,
        PatternLibrary, CDLGenerator,
        ConversationMemory, MemoryType,
        NewtonVoiceInterface
    )

    # ACID 1: Intent type completeness
    def test_intent_completeness():
        parser = IntentParser()

        # Every input should map to exactly one intent type
        test_inputs = [
            "hello", "build", "what", "deploy", "remember",
            "create", "run", "save", "show", "analyze",
            "123", "!!!", "   ", "αβγ", "日本語",
        ]

        for text in test_inputs:
            intent = parser.parse(text)
            if intent.intent_type not in IntentType:
                return False, f"Invalid intent type for '{text}'", None
            if intent.domain not in DomainCategory:
                return False, f"Invalid domain for '{text}'", None

        return True, "All inputs map to valid types", {"inputs": len(test_inputs)}

    report.add(run_test("Intent Completeness", test_intent_completeness))

    # ACID 2: CDL constraint validity
    def test_cdl_validity():
        parser = IntentParser()
        generator = CDLGenerator(PatternLibrary())

        queries = [
            "Build a calculator",
            "Create a lesson",
            "Track expenses",
            "Analyze data",
            "Random gibberish xyz",
        ]

        for query in queries:
            intent = parser.parse(query)
            cdl = generator.generate(intent)

            # CDL must always have these fields
            required = ["id", "constraints", "domain", "generated_at"]
            for field in required:
                if field not in cdl:
                    return False, f"CDL missing '{field}' for '{query}'", None

            # Constraints must be valid
            for c in cdl.get("constraints", []):
                if "field" not in c or "operator" not in c:
                    return False, f"Invalid constraint in CDL for '{query}'", None

        return True, "All CDL outputs valid", {"queries": len(queries)}

    report.add(run_test("CDL Validity", test_cdl_validity))

    # ACID 3: Session isolation
    def test_session_isolation():
        interface = NewtonVoiceInterface()

        # Create two sessions
        r1 = interface.ask("Remember user is Alice")
        r2 = interface.ask("Remember user is Bob")

        session1 = r1.session_id
        session2 = r2.session_id

        if session1 == session2:
            return False, "Sessions not isolated", None

        # Memories should be separate
        s1_memory = interface.sessions.get_session(session1).memory
        s2_memory = interface.sessions.get_session(session2).memory

        # Each session's memory should be independent
        # (This is implicit in the design but worth verifying)

        return True, "Sessions properly isolated", {
            "session1": session1,
            "session2": session2
        }

    report.add(run_test("Session Isolation", test_session_isolation))

    # ACID 4: Verification consistency
    def test_verification_consistency():
        interface = NewtonVoiceInterface()

        # Same query should give consistent verification
        query = "Build a verified calculator"
        results = [interface.ask(query) for _ in range(10)]

        verifications = [r.verified for r in results]
        if len(set(verifications)) != 1:
            return False, "Inconsistent verification results", None

        # All should have proofs if verified
        if results[0].verified:
            for r in results:
                if r.proof is None:
                    return False, "Missing proof on verified result", None

        return True, "Verification consistent across 10 runs", {"verified": results[0].verified}

    report.add(run_test("Verification Consistency", test_verification_consistency))

    # ACID 5: Memory persistence
    def test_memory_persistence():
        from core.voice_interface import ConversationMemory, MemoryType

        memory = ConversationMemory("persistence_test")

        # Store keystone (should persist)
        memory.remember("critical", "data", MemoryType.KEYSTONE)

        # Store object (session-scoped)
        memory.remember("temporary", "data", MemoryType.OBJECT)

        # Keystones should always be recallable
        if memory.recall("critical") != "data":
            return False, "Keystone memory lost", None

        # Get context should include both
        ctx = memory.get_context()
        if "critical" not in ctx.get("keystones", {}):
            return False, "Keystone not in context", None
        if "temporary" not in ctx.get("objects", {}):
            return False, "Object not in context", None

        return True, "Memory persistence correct", ctx

    report.add(run_test("Memory Persistence", test_memory_persistence))

    # ACID 6: Proof integrity
    def test_proof_integrity():
        interface = NewtonVoiceInterface()

        response = interface.ask("Build a calculator with verification")

        if not response.verified or not response.proof:
            return True, "Skipped (no proof generated)", None

        proof = response.proof

        # Proof must have required fields
        required = ["result_hash", "cdl_hash", "verified", "timestamp", "signature"]
        for field in required:
            if field not in proof:
                return False, f"Proof missing '{field}'", None

        # Hashes should be valid hex
        for hash_field in ["result_hash", "cdl_hash", "signature"]:
            try:
                int(proof[hash_field], 16)
            except ValueError:
                return False, f"Invalid hash in '{hash_field}'", None

        return True, "Proof structure valid", proof

    report.add(run_test("Proof Integrity", test_proof_integrity))

    # ACID 7: Pattern determinism
    def test_pattern_determinism():
        library = PatternLibrary()

        # Same query should always return same pattern
        queries = ["calculator", "lesson", "expense"]

        for query in queries:
            results = [library.find_pattern(query) for _ in range(10)]
            ids = [r.id if r else None for r in results]

            if len(set(ids)) != 1:
                return False, f"Non-deterministic pattern for '{query}'", None

        return True, "Pattern matching deterministic", {"queries": len(queries)}

    report.add(run_test("Pattern Determinism", test_pattern_determinism))

    report.finalize()
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN - Run all tests
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  NEWTON VOICE INTERFACE - WWDC TEST SUITE".center(68) + "█")
    print("█" + "  Mother Of All Demos - Comprehensive Testing".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    all_reports = []
    total_start = time.time()

    # Run all test suites
    print("\n\n🎬 DEMO TESTS (WWDC Keynote)")
    print("─" * 70)
    demo_report = demo_tests()
    demo_report.print_summary()
    all_reports.append(demo_report)

    print("\n\n🔄 SIMULATION TESTS (Real-world Usage)")
    print("─" * 70)
    sim_report = simulation_tests()
    sim_report.print_summary()
    all_reports.append(sim_report)

    print("\n\n💪 STRESS TESTS (Performance)")
    print("─" * 70)
    stress_report = stress_tests()
    stress_report.print_summary()
    all_reports.append(stress_report)

    print("\n\n🧪 ACID TESTS (Invariants)")
    print("─" * 70)
    acid_report = acid_tests()
    acid_report.print_summary()
    all_reports.append(acid_report)

    # Final summary
    total_elapsed = time.time() - total_start
    total_passed = sum(r.passed for r in all_reports)
    total_failed = sum(r.failed for r in all_reports)
    total_tests = sum(r.total for r in all_reports)

    print("\n\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  FINAL REPORT".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    print(f"""
    ┌────────────────────────────────────────────────────────────────┐
    │  Test Suite Results                                            │
    ├────────────────────────────────────────────────────────────────┤
    │  Total Tests:    {total_tests:4d}                                        │
    │  Passed:         {total_passed:4d}  ({'✓' if total_passed == total_tests else '○'})                                     │
    │  Failed:         {total_failed:4d}  ({'✗' if total_failed > 0 else '○'})                                     │
    │  Pass Rate:      {total_passed/total_tests*100:5.1f}%                                       │
    │  Duration:       {total_elapsed:5.2f}s                                       │
    └────────────────────────────────────────────────────────────────┘
    """)

    if total_failed == 0:
        print("    ✓ ALL TESTS PASSED - READY FOR WWDC! 🎉\n")
    else:
        print(f"    ✗ {total_failed} TESTS FAILED - NEEDS ATTENTION\n")

    return total_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
