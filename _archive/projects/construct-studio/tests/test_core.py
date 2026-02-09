"""
Tests for Construct Studio Core
===============================

These tests verify the fundamental physics of constraint satisfaction.
"""

import pytest
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    Matter, Floor, Capacity, Force, Ratio,
    Construct, ConstructError, OntologicalDeath,
    attempt, MatterState
)
from ledger import Ledger, LedgerEntry, EntryType, global_ledger


class TestMatter:
    """Tests for Matter - typed values with units."""

    def test_creation(self):
        """Matter can be created with value and unit."""
        m = Matter(100, "USD")
        assert m.value == 100
        assert m.unit == "USD"
        assert m.state == MatterState.POTENTIAL

    def test_with_label(self):
        """Matter can have an optional label."""
        m = Matter(50, "USD", "lunch expense")
        assert m.label == "lunch expense"

    def test_string_representation(self):
        """Matter has readable string representation."""
        m = Matter(1500, "USD")
        assert str(m) == "1500 USD"

    def test_arithmetic_same_units(self):
        """Matter with same units can be added/subtracted."""
        a = Matter(100, "USD")
        b = Matter(50, "USD")

        result = a + b
        assert result.value == 150
        assert result.unit == "USD"

        result = a - b
        assert result.value == 50

    def test_arithmetic_different_units_fails(self):
        """Matter with different units cannot be combined."""
        a = Matter(100, "USD")
        b = Matter(50, "EUR")

        with pytest.raises(ConstructError):
            a + b

    def test_scalar_multiplication(self):
        """Matter can be multiplied by scalars."""
        m = Matter(100, "USD")

        result = m * 2
        assert result.value == 200
        assert result.unit == "USD"

        result = 3 * m
        assert result.value == 300

    def test_comparison_same_units(self):
        """Matter with same units can be compared."""
        a = Matter(100, "USD")
        b = Matter(50, "USD")
        c = Matter(100, "USD")

        assert a > b
        assert b < a
        assert a >= c
        assert a <= c
        assert a == c

    def test_comparison_different_units_fails(self):
        """Matter with different units cannot be compared."""
        a = Matter(100, "USD")
        b = Matter(100, "EUR")

        with pytest.raises(ConstructError):
            a < b


class TestCapacity:
    """Tests for Capacity - container limits."""

    def test_creation(self):
        """Capacity tracks current vs maximum."""
        cap = Capacity(
            current=Matter(0, "USD"),
            maximum=Matter(1000, "USD"),
            name="budget"
        )
        assert cap.current.value == 0
        assert cap.maximum.value == 1000

    def test_remaining(self):
        """Capacity knows remaining headroom."""
        cap = Capacity(
            current=Matter(300, "USD"),
            maximum=Matter(1000, "USD"),
            name="budget"
        )
        assert cap.remaining.value == 700

    def test_utilization(self):
        """Capacity calculates utilization percentage."""
        cap = Capacity(
            current=Matter(500, "USD"),
            maximum=Matter(1000, "USD"),
            name="budget"
        )
        assert cap.utilization == 0.5

    def test_can_accept_fitting_matter(self):
        """Capacity accepts matter that fits."""
        cap = Capacity(
            current=Matter(0, "USD"),
            maximum=Matter(1000, "USD"),
            name="budget"
        )
        m = Matter(500, "USD")
        assert cap.can_accept(m) is True

    def test_cannot_accept_overflow(self):
        """Capacity rejects matter that doesn't fit."""
        cap = Capacity(
            current=Matter(800, "USD"),
            maximum=Matter(1000, "USD"),
            name="budget"
        )
        m = Matter(500, "USD")
        assert cap.can_accept(m) is False

    def test_cannot_accept_wrong_unit(self):
        """Capacity rejects matter with wrong unit."""
        cap = Capacity(
            current=Matter(0, "USD"),
            maximum=Matter(1000, "USD"),
            name="budget"
        )
        m = Matter(100, "EUR")
        assert cap.can_accept(m) is False


class TestFloor:
    """Tests for Floor - constraint containers."""

    def test_floor_definition(self):
        """Floors can be defined with Matter capacities."""
        class TestBudget(Floor):
            limit = Matter(5000, "USD")

        floor = TestBudget()
        assert "limit" in floor._capacities
        assert floor._capacities["limit"].maximum.value == 5000

    def test_floor_starts_empty(self):
        """Floor capacities start at zero."""
        class TestBudget(Floor):
            limit = Matter(5000, "USD")

        floor = TestBudget()
        assert floor._capacities["limit"].current.value == 0

    def test_floor_reset(self):
        """Floors can be reset to initial state."""
        class TestBudget(Floor):
            limit = Matter(5000, "USD")

        floor = TestBudget()
        floor._capacities["limit"].accept(Matter(1000, "USD"))
        assert floor._capacities["limit"].current.value == 1000

        floor._initialize_capacities()
        assert floor._capacities["limit"].current.value == 0


class TestForce:
    """Tests for Force - the >> operator."""

    def setup_method(self):
        """Reset global state before each test."""
        global_ledger.clear()
        Floor._instances.clear()

    def test_force_success(self):
        """Force succeeds when matter fits."""
        class TestBudget(Floor):
            limit = Matter(1000, "USD")

        floor = TestBudget()
        cap = floor._capacities["limit"]

        m = Matter(500, "USD")
        result = m >> cap

        assert result.success is True
        assert result.ratio.fits is True
        assert cap.current.value == 500

    def test_force_death_strict(self):
        """Force causes death when matter doesn't fit."""
        class TestBudget(Floor):
            limit = Matter(1000, "USD")

        floor = TestBudget()
        cap = floor._capacities["limit"]

        m = Matter(1500, "USD")

        with pytest.raises(OntologicalDeath):
            m >> cap

    def test_force_soft_mode(self):
        """Force in attempt() returns False instead of raising."""
        class TestBudget(Floor):
            limit = Matter(1000, "USD")

        floor = TestBudget()
        cap = floor._capacities["limit"]

        m = Matter(1500, "USD")

        with attempt():
            result = m >> cap
            assert result.success is False
            assert result.ratio.fits is False
            assert result.ratio.overflow == 500

    def test_force_records_to_ledger(self):
        """Force application is recorded in ledger."""
        class TestBudget(Floor):
            limit = Matter(1000, "USD")

        floor = TestBudget()
        cap = floor._capacities["limit"]

        m = Matter(500, "USD")
        m >> cap

        assert len(global_ledger) >= 1
        entry = global_ledger.get_recent(1)[0]
        assert entry.success is True


class TestRatio:
    """Tests for Ratio - collision test results."""

    def test_ratio_fits(self):
        """Ratio calculates when matter fits."""
        ratio = Ratio(
            numerator=500,
            denominator=1000,
            unit="USD",
            fits=True
        )
        assert ratio.fits is True
        assert ratio.value == 0.5
        assert ratio.percentage == 50.0

    def test_ratio_overflow(self):
        """Ratio calculates overflow when matter doesn't fit."""
        ratio = Ratio(
            numerator=1500,
            denominator=1000,
            unit="USD",
            fits=False,
            overflow=500
        )
        assert ratio.fits is False
        assert ratio.overflow == 500

    def test_ratio_truthiness(self):
        """Ratio is truthy when it fits."""
        fits = Ratio(100, 1000, "USD", True)
        doesnt = Ratio(1500, 1000, "USD", False)

        assert bool(fits) is True
        assert bool(doesnt) is False


class TestLedger:
    """Tests for Ledger - audit trail."""

    def test_ledger_creation(self):
        """Ledger can be created with a name."""
        ledger = Ledger("test")
        assert ledger.name == "test"
        assert len(ledger) == 0

    def test_ledger_append_only(self):
        """Ledger entries are append-only."""
        ledger = Ledger("test")

        # Can't directly modify _entries from outside
        initial_len = len(ledger._entries)
        ledger._entries.append("fake")  # Direct modification (shouldn't do this)

        # The .entries property returns a copy
        entries_copy = ledger.entries
        entries_copy.append("another fake")
        assert len(ledger._entries) == initial_len + 1  # Only the first append worked

    def test_ledger_serialization(self):
        """Ledger can be serialized to JSON."""
        ledger = Ledger("test")
        ledger.checkpoint("test checkpoint")

        json_str = ledger.to_json()
        restored = Ledger.from_json(json_str)

        assert restored.name == "test"
        assert len(restored) == 1

    def test_ledger_stats(self):
        """Ledger provides statistics."""
        ledger = Ledger("test")

        stats = ledger.stats
        assert stats["total_entries"] == 0
        assert stats["successes"] == 0
        assert stats["deaths"] == 0


class TestConstruct:
    """Tests for @Construct decorator."""

    def setup_method(self):
        """Reset global state before each test."""
        global_ledger.clear()
        Floor._instances.clear()

    def test_construct_decorator(self):
        """@Construct wraps functions with floor context."""
        class TestBudget(Floor):
            limit = Matter(1000, "USD")

        @Construct(floor=TestBudget)
        def spend(amount):
            m = Matter(amount, "USD")
            floor = TestBudget._instances.get("TestBudget") or TestBudget()
            m >> floor._capacities["limit"]
            return "OK"

        result = spend(500)
        assert result == "OK"

    def test_construct_strict_raises(self):
        """@Construct with strict=True raises on death."""
        class TestBudget(Floor):
            limit = Matter(1000, "USD")

        @Construct(floor=TestBudget, strict=True)
        def spend(amount):
            m = Matter(amount, "USD")
            floor = TestBudget._instances.get("TestBudget") or TestBudget()
            m >> floor._capacities["limit"]
            return "OK"

        with pytest.raises(OntologicalDeath):
            spend(1500)


class TestOntologicalDeath:
    """Tests for OntologicalDeath exception."""

    def test_death_message(self):
        """Death has informative message."""
        death = OntologicalDeath("Test failure")
        assert "ONTOLOGICAL DEATH" in str(death)
        assert "Test failure" in str(death)

    def test_death_captures_context(self):
        """Death captures matter, floor, ratio context."""
        m = Matter(1500, "USD")
        ratio = Ratio(1500, 1000, "USD", False, 500)

        death = OntologicalDeath(
            "Overflow",
            matter=m,
            ratio=ratio
        )

        assert death.matter == m
        assert death.ratio == ratio


class TestIntegration:
    """Integration tests for complete workflows."""

    def setup_method(self):
        """Reset global state before each test."""
        global_ledger.clear()
        Floor._instances.clear()

    def test_corporate_card_scenario(self):
        """Complete corporate card spending scenario."""
        class CorporateCard(Floor):
            budget = Matter(5000, "USD")

        card = CorporateCard()
        cap = card._capacities["budget"]

        # First expense - should succeed
        expense1 = Matter(1500, "USD", "Office supplies")
        result1 = expense1 >> cap
        assert result1.success is True
        assert cap.remaining.value == 3500

        # Second expense - should succeed
        expense2 = Matter(2000, "USD", "Software")
        result2 = expense2 >> cap
        assert result2.success is True
        assert cap.remaining.value == 1500

        # Third expense - should fail (overflow)
        expense3 = Matter(2000, "USD", "Conference")
        with attempt():
            result3 = expense3 >> cap
            assert result3.success is False
            assert result3.ratio.overflow == 500

    def test_multiple_capacities(self):
        """Floor with multiple capacities."""
        class DeploymentQuota(Floor):
            cpu = Matter(64, "vCPU")
            memory = Matter(256, "GB")

        quota = DeploymentQuota()

        # Allocate CPU
        cpu_req = Matter(32, "vCPU")
        result = cpu_req >> quota._capacities["cpu"]
        assert result.success is True

        # Allocate memory
        mem_req = Matter(128, "GB")
        result = mem_req >> quota._capacities["memory"]
        assert result.success is True

        # Check remaining
        assert quota._capacities["cpu"].remaining.value == 32
        assert quota._capacities["memory"].remaining.value == 128


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
