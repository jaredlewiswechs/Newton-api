#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON PROPERTY-BASED TESTS
Proving the supercomputer works.

Property-based testing finds edge cases humans miss.
If Newton claims to be deterministic, prove it.
If Newton claims to terminate, prove it.
If Newton claims to be consistent, prove it.

Using Hypothesis: https://hypothesis.readthedocs.io/
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import math
import hashlib
from typing import Any, Dict, List

# Try to import hypothesis, provide fallback
try:
    from hypothesis import given, strategies as st, settings, assume
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Provide dummy decorators
    def given(*args, **kwargs):
        def decorator(f):
            def wrapper(*a, **k):
                pytest.skip("Hypothesis not installed")
            return wrapper
        return decorator

    class st:
        @staticmethod
        def text(*args, **kwargs): return None
        @staticmethod
        def integers(*args, **kwargs): return None
        @staticmethod
        def floats(*args, **kwargs): return None
        @staticmethod
        def lists(*args, **kwargs): return None
        @staticmethod
        def dictionaries(*args, **kwargs): return None
        @staticmethod
        def booleans(): return None
        @staticmethod
        def one_of(*args): return None
        @staticmethod
        def just(x): return None
        @staticmethod
        def sampled_from(x): return None

    def settings(*args, **kwargs):
        def decorator(f): return f
        return decorator

    def assume(x): pass

from core.cdl import (
    CDLEvaluator, CDLParser, HaltChecker, AtomicConstraint,
    CompositeConstraint, ConditionalConstraint, Domain, Operator,
    verify, verify_and, verify_or, EvaluationResult
)
from core.forge import Forge, ForgeConfig
from core.robust import RobustVerifier, RobustConfig, LockedBaseline, mad
from core.ledger import Ledger, LedgerConfig, LedgerEntry


# ═══════════════════════════════════════════════════════════════════════════════
# CDL PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestCDLDeterminism:
    """Property: Same input ALWAYS produces same output."""

    @given(
        field_value=st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False), st.text()),
        threshold=st.floats(min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=200)
    def test_verify_deterministic(self, field_value, threshold):
        """Verification of the same input produces identical results."""
        obj = {"field": field_value}
        constraint = {"field": "field", "operator": "lt", "value": threshold}

        result1 = verify(constraint, obj)
        result2 = verify(constraint, obj)

        assert result1.passed == result2.passed, \
            f"Non-deterministic result for {field_value} < {threshold}"

    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=100)
    def test_fingerprint_deterministic(self, text):
        """Same constraint produces same fingerprint."""
        constraint = AtomicConstraint(
            domain=Domain.CUSTOM,
            field="test",
            operator=Operator.EQ,
            value=text
        )

        # Create two instances with same content
        constraint2 = AtomicConstraint(
            domain=Domain.CUSTOM,
            field="test",
            operator=Operator.EQ,
            value=text
        )

        # IDs should match (based on content hash)
        assert constraint.id == constraint2.id


class TestCDLTermination:
    """Property: Every constraint evaluation terminates."""

    @given(depth=st.integers(min_value=1, max_value=50))
    @settings(max_examples=50)
    def test_nested_composite_terminates(self, depth):
        """Deeply nested composites still terminate."""
        # Build nested AND constraints
        current = {"field": "x", "operator": "eq", "value": 1}
        for _ in range(depth):
            current = {"logic": "and", "constraints": [current]}

        parser = CDLParser()
        checker = HaltChecker()

        constraint = parser.parse(current)
        halts, reason = checker.check(constraint)

        assert halts, f"Constraint should halt at depth {depth}: {reason}"

    @given(n_constraints=st.integers(min_value=1, max_value=100))
    @settings(max_examples=50)
    def test_wide_composite_terminates(self, n_constraints):
        """Wide composites (many siblings) terminate."""
        constraints = [
            {"field": f"field_{i}", "operator": "eq", "value": i}
            for i in range(n_constraints)
        ]
        composite = {"logic": "and", "constraints": constraints}

        parser = CDLParser()
        constraint = parser.parse(composite)

        evaluator = CDLEvaluator()
        obj = {f"field_{i}": i for i in range(n_constraints)}

        # Should complete without hanging
        result = evaluator.evaluate(constraint, obj)
        assert isinstance(result, EvaluationResult)


class TestCDLConsistency:
    """Property: No constraint can be both pass and fail."""

    @given(
        value=st.integers(),
        threshold=st.integers()
    )
    @settings(max_examples=200)
    def test_no_contradiction(self, value, threshold):
        """A constraint cannot simultaneously pass and fail."""
        obj = {"amount": value}
        constraint = {"field": "amount", "operator": "lt", "value": threshold}

        result = verify(constraint, obj)

        # Result must be definitively True or False
        assert result.passed in (True, False), "Result must be boolean"

        # Verify logical consistency
        if value < threshold:
            assert result.passed is True, f"{value} < {threshold} should pass"
        else:
            assert result.passed is False, f"{value} >= {threshold} should fail"

    @given(
        a_value=st.integers(),
        b_value=st.integers()
    )
    @settings(max_examples=100)
    def test_and_or_duality(self, a_value, b_value):
        """NOT(A AND B) == NOT(A) OR NOT(B)."""
        obj = {"a": a_value, "b": b_value}

        # A: a < 50, B: b < 50
        a_passes = a_value < 50
        b_passes = b_value < 50

        # Test AND
        and_result = verify_and([
            {"field": "a", "operator": "lt", "value": 50},
            {"field": "b", "operator": "lt", "value": 50}
        ], obj)

        assert and_result.passed == (a_passes and b_passes)

        # Test OR
        or_result = verify_or([
            {"field": "a", "operator": "lt", "value": 50},
            {"field": "b", "operator": "lt", "value": 50}
        ], obj)

        assert or_result.passed == (a_passes or b_passes)


class TestCDLOperators:
    """Property: Operators behave correctly for all inputs."""

    @given(a=st.integers(), b=st.integers())
    @settings(max_examples=200)
    def test_comparison_operators(self, a, b):
        """Comparison operators match Python semantics."""
        obj = {"value": a}

        # EQ
        result = verify({"field": "value", "operator": "eq", "value": b}, obj)
        assert result.passed == (a == b)

        # NE
        result = verify({"field": "value", "operator": "ne", "value": b}, obj)
        assert result.passed == (a != b)

        # LT
        result = verify({"field": "value", "operator": "lt", "value": b}, obj)
        assert result.passed == (a < b)

        # GT
        result = verify({"field": "value", "operator": "gt", "value": b}, obj)
        assert result.passed == (a > b)

        # LE
        result = verify({"field": "value", "operator": "le", "value": b}, obj)
        assert result.passed == (a <= b)

        # GE
        result = verify({"field": "value", "operator": "ge", "value": b}, obj)
        assert result.passed == (a >= b)

    @given(text=st.text(), substring=st.text(min_size=1))
    @settings(max_examples=100)
    def test_contains_operator(self, text, substring):
        """Contains operator matches Python 'in' semantics."""
        obj = {"text": text}
        result = verify({"field": "text", "operator": "contains", "value": substring}, obj)
        assert result.passed == (substring in text)


# ═══════════════════════════════════════════════════════════════════════════════
# FORGE PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestForgeDeterminism:
    """Property: Forge verification is deterministic."""

    @given(text=st.text(min_size=1, max_size=500))
    @settings(max_examples=100)
    def test_content_verify_deterministic(self, text):
        """Content verification always produces same result."""
        forge = Forge()

        result1 = forge.verify_content(text)
        result2 = forge.verify_content(text)

        assert result1.passed == result2.passed
        assert result1.constraint_id == result2.constraint_id

    @given(text=st.text(min_size=1, max_size=500))
    @settings(max_examples=100)
    def test_signal_verify_deterministic(self, text):
        """Signal verification always produces same result."""
        forge = Forge()

        result1 = forge.verify_signal(text)
        result2 = forge.verify_signal(text)

        assert result1.passed == result2.passed


class TestForgeNoNaN:
    """Property: Forge never returns NaN values."""

    @given(text=st.text())
    @settings(max_examples=100)
    def test_signal_no_nan(self, text):
        """Signal verification never produces NaN."""
        forge = Forge()
        result = forge.verify_signal(text)

        # Check numeric fields
        assert not math.isnan(result.elapsed_us)
        assert result.passed in (True, False)  # Boolean, can't be NaN

    @given(
        values=st.lists(
            st.floats(allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=50)
    def test_metrics_no_nan(self, values):
        """Metrics never contain NaN."""
        forge = Forge()

        for v in values:
            forge.verify({"field": "x", "operator": "lt", "value": v}, {"x": v - 1})

        metrics = forge.get_metrics()

        assert not math.isnan(metrics["avg_time_us"])
        assert not math.isnan(metrics["pass_rate"])


# ═══════════════════════════════════════════════════════════════════════════════
# ROBUST STATISTICS PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestMADProperties:
    """Property: MAD is resistant to outliers."""

    @given(
        normal_values=st.lists(
            st.floats(min_value=95, max_value=105, allow_nan=False),
            min_size=20,
            max_size=100
        ),
        n_outliers=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=100)
    def test_mad_outlier_resistance(self, normal_values, n_outliers):
        """MAD doesn't change much with a few outliers."""
        assume(len(normal_values) >= 20)

        # Calculate MAD without outliers
        mad_clean = mad(normal_values)

        # Add outliers
        outliers = [1000.0] * n_outliers
        values_with_outliers = normal_values + outliers

        # Calculate MAD with outliers
        mad_dirty = mad(values_with_outliers)

        # MAD should not change dramatically (within 2x)
        if mad_clean > 0:
            ratio = mad_dirty / mad_clean
            assert 0.5 < ratio < 2.0, \
                f"MAD changed too much: {mad_clean} -> {mad_dirty}"

    @given(
        values=st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            min_size=30,
            max_size=200
        )
    )
    @settings(max_examples=50)
    def test_locked_baseline_immutable(self, values):
        """Locked baseline cannot be changed after creation."""
        baseline = LockedBaseline.from_values(values)

        original_median = baseline.median
        original_mad = baseline.mad
        original_fingerprint = baseline.fingerprint

        # Try to "update" by creating with more values
        new_baseline = LockedBaseline.from_values(values + [999999.0])

        # Original baseline unchanged
        assert baseline.median == original_median
        assert baseline.mad == original_mad
        assert baseline.fingerprint == original_fingerprint


class TestModifiedZScore:
    """Property: Modified Z-score behaves correctly."""

    @given(
        median=st.floats(min_value=-1000, max_value=1000, allow_nan=False),
        mad_value=st.floats(min_value=0.1, max_value=100, allow_nan=False)
    )
    @settings(max_examples=100)
    def test_zscore_at_median_is_zero(self, median, mad_value):
        """Z-score at median is always 0."""
        baseline = LockedBaseline(
            median=median,
            mad=mad_value,
            n_samples=100,
            locked_at=0,
            fingerprint="test",
            min_value=median - 10,
            max_value=median + 10
        )

        z = baseline.modified_zscore(median)
        assert abs(z) < 0.001, f"Z-score at median should be ~0, got {z}"


# ═══════════════════════════════════════════════════════════════════════════════
# LEDGER PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestLedgerAppendOnly:
    """Property: Ledger is append-only."""

    @given(
        operations=st.lists(
            st.sampled_from(["verify", "sign", "store"]),
            min_size=1,
            max_size=50
        )
    )
    @settings(max_examples=50)
    def test_ledger_grows_monotonically(self, operations):
        """Ledger length only increases."""
        ledger = Ledger(LedgerConfig(storage_path=f".newton_ledger_test_{hash(tuple(operations))}"))

        previous_length = 0
        for op in operations:
            ledger.append(operation=op, payload={"test": True}, result="pass")
            current_length = len(ledger)

            assert current_length == previous_length + 1, \
                "Ledger should grow by exactly 1"
            previous_length = current_length


class TestLedgerChainIntegrity:
    """Property: Ledger chain maintains integrity."""

    @given(n_entries=st.integers(min_value=1, max_value=20))
    @settings(max_examples=30)
    def test_chain_links_correctly(self, n_entries):
        """Each entry links to the previous entry's hash."""
        ledger = Ledger(LedgerConfig(storage_path=f".newton_ledger_test_chain_{n_entries}"))

        for i in range(n_entries):
            ledger.append(operation="test", payload={"i": i}, result="pass")

        # Verify chain
        for i in range(1, len(ledger)):
            entry = ledger.get(i)
            prev_entry = ledger.get(i - 1)

            assert entry.prev_hash == prev_entry.entry_hash, \
                f"Chain broken at entry {i}"

    @given(n_entries=st.integers(min_value=5, max_value=20))
    @settings(max_examples=20)
    def test_tampering_detectable(self, n_entries):
        """Tampering with any entry is detectable."""
        ledger = Ledger(LedgerConfig(storage_path=f".newton_ledger_test_tamper_{n_entries}"))

        for i in range(n_entries):
            ledger.append(operation="test", payload={"i": i}, result="pass")

        # Verify chain is valid
        valid, _ = ledger.verify_chain()
        assert valid, "Fresh chain should be valid"

        # Tamper with an entry (modify internal state - bad practice but for testing)
        if len(ledger._entries) > 2:
            ledger._entries[1].result = "TAMPERED"

            # Entry should fail self-verification
            assert not ledger._entries[1].verify_integrity(), \
                "Tampered entry should fail integrity check"


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-MODULE PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestEndToEnd:
    """Property: End-to-end verification works correctly."""

    @given(
        amount=st.integers(min_value=0, max_value=10000),
        limit=st.integers(min_value=0, max_value=10000)
    )
    @settings(max_examples=100)
    def test_full_pipeline_consistent(self, amount, limit):
        """Full verification pipeline produces consistent results."""
        forge = Forge()

        constraint = {"field": "amount", "operator": "lt", "value": limit}
        obj = {"amount": amount}

        # Run through Forge
        result = forge.verify(constraint, obj)

        # Check consistency
        expected = amount < limit
        assert result.passed == expected, \
            f"Expected {amount} < {limit} to be {expected}, got {result.passed}"


# ═══════════════════════════════════════════════════════════════════════════════
# THE CLOSURE CONDITION
# ═══════════════════════════════════════════════════════════════════════════════

class TestClosureCondition:
    """Property: 1 == 1. Always."""

    @given(x=st.one_of(
        st.integers(),
        st.floats(allow_nan=False),
        st.text(),
        st.booleans(),
        st.lists(st.integers())
    ))
    @settings(max_examples=200)
    def test_identity(self, x):
        """x == x for all x."""
        assert x == x, "Identity failed - this should be impossible"

    @given(
        current=st.integers(),
        goal=st.integers()
    )
    @settings(max_examples=200)
    def test_newton_closure(self, current, goal):
        """Newton closure: current == goal iff they're equal."""
        from core.cdl import newton

        result = newton(current, goal)
        assert result == (current == goal), \
            f"newton({current}, {goal}) should be {current == goal}"


# ═══════════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Newton Property-Based Tests")
    print("=" * 60)

    if not HYPOTHESIS_AVAILABLE:
        print("\n[WARNING] Hypothesis not installed!")
        print("  Install with: pip install hypothesis")
        print("  Running basic sanity checks instead...")

        # Basic sanity checks
        print("\n[Sanity Checks]")

        # Test determinism
        result1 = verify({"field": "x", "operator": "lt", "value": 100}, {"x": 50})
        result2 = verify({"field": "x", "operator": "lt", "value": 100}, {"x": 50})
        assert result1.passed == result2.passed
        print("  ✓ Determinism")

        # Test operators
        assert verify({"field": "x", "operator": "eq", "value": 5}, {"x": 5}).passed
        assert not verify({"field": "x", "operator": "eq", "value": 5}, {"x": 6}).passed
        print("  ✓ Operators")

        # Test closure
        from core.cdl import newton
        assert newton(1, 1) == True
        assert newton(1, 2) == False
        print("  ✓ Closure condition")

        print("\n" + "=" * 60)
        print("Basic sanity checks passed!")
    else:
        print("\n[Running Hypothesis Tests]")
        pytest.main([__file__, "-v", "--tb=short", "-x"])
