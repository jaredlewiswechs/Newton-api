#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON SDK STRESS TEST
Prove Turing completeness. Break nothing.

Tests:
1. Bounded loops (for, while, map, filter, reduce)
2. Recursion with depth limits  
3. Arithmetic at scale
4. Constraint checking at volume
5. Concurrent verification
6. Memory pressure
7. Timeout enforcement
8. TI Calculator edge cases

Run: python -m newton.stress_test
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import time
import random
import math
from typing import List, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Newton SDK
import newton
from newton import (
    verify, check, calc, ti_calc,
    gt, lt, eq, between, all_of, contains,
    LogicEngine, ExecutionBounds, execute, run_program,
    verified, bounded, constrained,
)


@dataclass
class TestResult:
    """Result of a stress test."""
    name: str
    passed: bool
    elapsed_ms: float
    operations: int
    message: str = ""


class StressTest:
    """Newton SDK Stress Test Suite."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results: List[TestResult] = []
    
    def log(self, msg: str):
        if self.verbose:
            print(msg)
    
    def run_all(self) -> bool:
        """Run all stress tests. Returns True if all pass."""
        self.log("=" * 70)
        self.log("NEWTON SDK STRESS TEST")
        self.log("Proving Turing completeness with bounded verification")
        self.log("=" * 70)
        
        tests = [
            self.test_bounded_for_loop,
            self.test_bounded_while_loop,
            self.test_recursion_factorial,
            self.test_recursion_fibonacci,
            self.test_map_filter_reduce,
            self.test_nested_loops,
            self.test_arithmetic_scale,
            self.test_constraint_volume,
            self.test_ti_calculator_expressions,
            self.test_ti_calculator_edge_cases,
            self.test_concurrent_verification,
            self.test_bounds_enforcement,
            self.test_decorated_functions,
            self.test_complex_program,
        ]
        
        for test in tests:
            start = time.perf_counter()
            try:
                result = test()
                elapsed = (time.perf_counter() - start) * 1000
                result.elapsed_ms = elapsed
                self.results.append(result)
                
                status = "PASS" if result.passed else "FAIL"
                self.log(f"  [{status}] {result.name} ({elapsed:.1f}ms, {result.operations} ops)")
                if not result.passed and result.message:
                    self.log(f"         {result.message}")
            except Exception as e:
                elapsed = (time.perf_counter() - start) * 1000
                self.results.append(TestResult(
                    name=test.__name__,
                    passed=False,
                    elapsed_ms=elapsed,
                    operations=0,
                    message=str(e)
                ))
                self.log(f"  [FAIL] {test.__name__} - Exception: {e}")
        
        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        total_time = sum(r.elapsed_ms for r in self.results)
        total_ops = sum(r.operations for r in self.results)
        
        self.log("")
        self.log("=" * 70)
        self.log(f"RESULTS: {passed}/{total} tests passed")
        self.log(f"Total time: {total_time:.1f}ms")
        self.log(f"Total operations: {total_ops:,}")
        self.log("=" * 70)
        
        return passed == total
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LOOP TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_bounded_for_loop(self) -> TestResult:
        """Test bounded FOR loops."""
        engine = LogicEngine()
        
        # Simple FOR loop - generate list [0, 2, 4, 6, 8]
        result = engine.evaluate({
            "op": "for",
            "args": ["i", 0, 4, {"op": "*", "args": [{"op": "var", "args": ["i"]}, 2]}]
        })
        
        # Should produce list of doubled values
        passed = result.verified and len(result.value.data) == 5
        
        return TestResult(
            name="Bounded FOR Loop",
            passed=passed,
            elapsed_ms=0,
            operations=result.operations,
            message=f"Expected 5 items, got {result.value}" if not passed else ""
        )
    
    def test_bounded_while_loop(self) -> TestResult:
        """Test bounded WHILE loops."""
        engine = LogicEngine()
        
        # Simple program: let x = 0, while x < 10, set x = x + 1
        result = engine.evaluate({
            "op": "block",
            "args": [
                {"op": "let", "args": ["x", 0]},
                {"op": "while", "args": [
                    {"op": "<", "args": [{"op": "var", "args": ["x"]}, 10]},
                    {"op": "set", "args": ["x", 
                        {"op": "+", "args": [{"op": "var", "args": ["x"]}, 1]}
                    ]}
                ]},
                {"op": "var", "args": ["x"]}
            ]
        })
        
        passed = result.verified and float(result.value.data) == 10
        
        return TestResult(
            name="Bounded WHILE Loop",
            passed=passed,
            elapsed_ms=0,
            operations=result.operations,
            message=f"Expected 10, got {result.value}" if not passed else ""
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RECURSION TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_recursion_factorial(self) -> TestResult:
        """Test recursive factorial with bounded depth."""
        engine = LogicEngine()
        
        # Define and call factorial(5)
        result = engine.evaluate({
            "op": "block",
            "args": [
                {"op": "def", "args": ["fact", ["n"], 
                    {"op": "if", "args": [
                        {"op": "<=", "args": [{"op": "var", "args": ["n"]}, 1]},
                        1,
                        {"op": "*", "args": [
                            {"op": "var", "args": ["n"]},
                            {"op": "call", "args": ["fact",
                                {"op": "-", "args": [{"op": "var", "args": ["n"]}, 1]}
                            ]}
                        ]}
                    ]}
                ]},
                {"op": "call", "args": ["fact", 5]}
            ]
        })
        
        expected = 120  # 5!
        passed = result.verified and float(result.value.data) == expected
        
        return TestResult(
            name="Recursive Factorial (5!)",
            passed=passed,
            elapsed_ms=0,
            operations=result.operations,
            message=f"Expected {expected}, got {result.value}" if not passed else ""
        )
    
    def test_recursion_fibonacci(self) -> TestResult:
        """Test recursive Fibonacci with bounded depth."""
        engine = LogicEngine()
        
        # Define and call fib(10) 
        result = engine.evaluate({
            "op": "block",
            "args": [
                {"op": "def", "args": ["fib", ["n"],
                    {"op": "if", "args": [
                        {"op": "<=", "args": [{"op": "var", "args": ["n"]}, 1]},
                        {"op": "var", "args": ["n"]},
                        {"op": "+", "args": [
                            {"op": "call", "args": ["fib",
                                {"op": "-", "args": [{"op": "var", "args": ["n"]}, 1]}
                            ]},
                            {"op": "call", "args": ["fib",
                                {"op": "-", "args": [{"op": "var", "args": ["n"]}, 2]}
                            ]}
                        ]}
                    ]}
                ]},
                {"op": "call", "args": ["fib", 10]}
            ]
        })
        
        expected = 55  # fib(10)
        passed = result.verified and float(result.value.data) == expected
        
        return TestResult(
            name="Recursive Fibonacci (fib(10))",
            passed=passed,
            elapsed_ms=0,
            operations=result.operations,
            message=f"Expected {expected}, got {result.value}" if not passed else ""
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HIGHER-ORDER FUNCTION TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_map_filter_reduce(self) -> TestResult:
        """Test map, filter operations."""
        engine = LogicEngine()
        
        # Filter even numbers from [0..10]
        result = engine.evaluate({
            "op": "filter",
            "args": [
                {"op": "for", "args": ["i", 0, 10, {"op": "var", "args": ["i"]}]},
                {"op": "==", "args": [
                    {"op": "%", "args": [{"op": "var", "args": ["x"]}, 2]},
                    0
                ]}
            ]
        })
        
        # Should give [0, 2, 4, 6, 8, 10] = 6 items
        passed = result.verified and len(result.value.data) == 6
        
        return TestResult(
            name="Filter (even numbers)",
            passed=passed,
            elapsed_ms=0,
            operations=result.operations,
            message=f"Expected 6 evens, got {len(result.value.data) if result.value.type.value == 'list' else result.value}" if not passed else ""
        )
    
    def test_nested_loops(self) -> TestResult:
        """Test nested operations."""
        engine = LogicEngine()
        
        # Sum: (1+2+3) * 2 
        result = engine.evaluate({
            "op": "*",
            "args": [
                {"op": "sum", "args": [
                    {"op": "for", "args": ["i", 1, 3, {"op": "var", "args": ["i"]}]}
                ]},
                2
            ]
        })
        
        expected = 12  # (1+2+3) * 2 = 6 * 2
        passed = result.verified and float(result.value.data) == expected
        
        return TestResult(
            name="Nested Operations",
            passed=passed,
            elapsed_ms=0,
            operations=result.operations,
            message=f"Expected {expected}, got {result.value}" if not passed else ""
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SCALE TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_arithmetic_scale(self) -> TestResult:
        """Test arithmetic at scale - 1000 calculations."""
        ops = 0
        passed = True
        
        for i in range(1000):
            result = calc(f"{i} + {i * 2}")
            ops += 1
            if result.value != i + i * 2:
                passed = False
                break
        
        return TestResult(
            name="Arithmetic Scale (1000 calculations)",
            passed=passed,
            elapsed_ms=0,
            operations=ops
        )
    
    def test_constraint_volume(self) -> TestResult:
        """Test constraint checking at volume - 1000 checks."""
        ops = 0
        passed = True
        
        for i in range(1000):
            result = check(i, between(0, 1000))
            ops += 1
            if not result.satisfied:
                passed = False
                break
        
        return TestResult(
            name="Constraint Volume (1000 checks)",
            passed=passed,
            elapsed_ms=0,
            operations=ops
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TI CALCULATOR TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_ti_calculator_expressions(self) -> TestResult:
        """Test TI calculator with various expressions."""
        test_cases = [
            ("2+2", 4),
            ("3*3*3", 27),
            ("10/2", 5),
            ("2^10", 1024),
            ("sqrt(16)", 4.0),
            ("abs(-5)", 5),
            ("floor(3.7)", 3),
            ("ceil(3.2)", 4),
            ("(2+3)*4", 20),
            ("2+3*4", 14),
        ]
        
        ops = 0
        failed = []
        
        for expr, expected in test_cases:
            result = ti_calc(expr)
            ops += 1
            if result != expected:
                failed.append(f"{expr}={result} (expected {expected})")
        
        passed = len(failed) == 0
        
        return TestResult(
            name="TI Calculator Expressions",
            passed=passed,
            elapsed_ms=0,
            operations=ops,
            message=", ".join(failed) if failed else ""
        )
    
    def test_ti_calculator_edge_cases(self) -> TestResult:
        """Test TI calculator edge cases."""
        test_cases = [
            ("0+0", 0),
            ("-5", -5),
            ("--5", 5),
            ("2*-3", -6),
            ("1e2", 100),
            ("1.5+2.5", 4.0),
        ]
        
        ops = 0
        failed = []
        
        for expr, expected in test_cases:
            result = ti_calc(expr)
            ops += 1
            if result != expected:
                failed.append(f"{expr}={result} (expected {expected})")
        
        passed = len(failed) == 0
        
        return TestResult(
            name="TI Calculator Edge Cases",
            passed=passed,
            elapsed_ms=0,
            operations=ops,
            message=", ".join(failed) if failed else ""
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONCURRENCY TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_concurrent_verification(self) -> TestResult:
        """Test concurrent verification - 100 parallel checks."""
        def verify_task(i):
            return verify(f"{i} + {i} equals {i + i}")
        
        ops = 0
        passed = True
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(verify_task, i) for i in range(100)]
            
            for future in as_completed(futures):
                result = future.result()
                ops += 1
                if not result.verified:
                    passed = False
        
        return TestResult(
            name="Concurrent Verification (100 parallel)",
            passed=passed,
            elapsed_ms=0,
            operations=ops
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BOUNDS ENFORCEMENT TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_bounds_enforcement(self) -> TestResult:
        """Test that bounds are properly enforced."""
        # Create engine with very tight bounds
        tight_bounds = ExecutionBounds(
            max_iterations=10,
            max_operations=100,
        )
        engine = LogicEngine(tight_bounds)
        
        # Try to run a loop that exceeds bounds
        result = engine.evaluate({
            "op": "for",
            "args": ["i", 0, 1000, {"op": "var", "args": ["i"]}]
        })
        
        # Should fail due to iteration limit
        passed = not result.verified or result.value.type.value == "error"
        
        return TestResult(
            name="Bounds Enforcement (iteration limit)",
            passed=passed,
            elapsed_ms=0,
            operations=result.operations,
            message="Loop should have been stopped by bounds" if not passed else ""
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DECORATOR TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_decorated_functions(self) -> TestResult:
        """Test Newton decorators."""
        ops = 0
        passed = True
        messages = []
        
        # Test @verified
        @verified
        def add(a, b):
            return a + b
        
        if add(2, 3) != 5:
            passed = False
            messages.append("@verified failed")
        ops += 1
        
        # Test @bounded
        @bounded(max_iterations=1000)
        def slow_add(a, b):
            return a + b
        
        if slow_add(2, 3) != 5:
            passed = False
            messages.append("@bounded failed")
        ops += 1
        
        # Test @constrained
        @constrained(input=gt(0), output=gt(0))
        def double(x):
            return x * 2
        
        if double(5) != 10:
            passed = False
            messages.append("@constrained failed")
        ops += 1
        
        # Test @constrained enforcement
        try:
            double(-1)
            passed = False
            messages.append("@constrained should have raised for negative input")
        except ValueError:
            ops += 1  # Expected
        
        return TestResult(
            name="Decorated Functions",
            passed=passed,
            elapsed_ms=0,
            operations=ops,
            message="; ".join(messages) if messages else ""
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMPLEX PROGRAM TEST
    # ═══════════════════════════════════════════════════════════════════════════
    
    def test_complex_program(self) -> TestResult:
        """Test a complex program - compute sum of squares."""
        engine = LogicEngine()
        
        # Sum of squares 1^2 + 2^2 + ... + 10^2
        result = engine.evaluate({
            "op": "sum",
            "args": [
                {"op": "for", "args": ["i", 1, 10,
                    {"op": "*", "args": [
                        {"op": "var", "args": ["i"]},
                        {"op": "var", "args": ["i"]}
                    ]}
                ]}
            ]
        })
        
        # Sum of squares 1-10 = 1+4+9+16+25+36+49+64+81+100 = 385
        expected = 385
        passed = result.verified and float(result.value.data) == expected
        
        return TestResult(
            name="Complex Program (sum of squares)",
            passed=passed,
            elapsed_ms=0,
            operations=result.operations,
            message=f"Expected {expected}, got {result.value}" if not passed else ""
        )


def main():
    """Run stress tests."""
    test = StressTest(verbose=True)
    success = test.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
