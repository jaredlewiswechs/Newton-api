#!/usr/bin/env python3
"""
Test examples from TINYTALK_PROGRAMMING_GUIDE.md
Ensures all code examples in the guide actually work.

Run with: python tests/test_programming_guide_examples.py
Or with pytest: pytest tests/test_programming_guide_examples.py -v
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

try:
    import pytest
except ImportError:
    # Create mock pytest for standalone execution
    class MockPytest:
        @staticmethod
        def raises(exc):
            class RaisesContext:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc_val, exc_tb):
                    if exc_type is None:
                        raise AssertionError(f"Expected {exc.__name__} but no exception raised")
                    if not issubclass(exc_type, exc):
                        return False
                    return True
            return RaisesContext()
        @staticmethod
        def main(args):
            print("Run with: python -m pytest tests/test_programming_guide_examples.py -v")
    pytest = MockPytest()

from tinytalk_py import (
    Blueprint, field, law, forge, when, finfr, fin,
    LawViolation, FinClosure,
    KineticEngine, Presence, Delta, motion,
    Money, Mass, Distance, Temperature, Pressure,
    Celsius, Fahrenheit, PSI, Meters,
    ratio, finfr_if_undefined, RatioResult
)


# =============================================================================
# YOUR FIRST PROGRAM - Bank Account
# =============================================================================

class BankAccount(Blueprint):
    """A bank account that cannot overdraft."""
    balance = field(float, default=100.0)

    @law
    def no_overdraft(self):
        when(self.balance < 0, finfr)

    @forge
    def withdraw(self, amount):
        self.balance -= amount
        return f"Withdrew ${amount}. Balance: ${self.balance}"


class TestBankAccount:
    def test_valid_withdrawal(self):
        account = BankAccount()
        result = account.withdraw(30)
        assert account.balance == 70.0
        assert "Withdrew" in result

    def test_overdraft_blocked(self):
        account = BankAccount()
        account.withdraw(30)  # balance = 70

        with pytest.raises(LawViolation):
            account.withdraw(100)  # Would make balance -30

        assert account.balance == 70.0  # Unchanged


# =============================================================================
# BASIC EXAMPLES
# =============================================================================

class Thermostat(Blueprint):
    """A thermostat with safety limits."""
    current_temp = field(float, default=20.0)
    target_temp = field(float, default=22.0)
    min_temp = field(float, default=10.0)
    max_temp = field(float, default=30.0)

    @law
    def within_safe_range(self):
        when(self.target_temp < self.min_temp, finfr)
        when(self.target_temp > self.max_temp, finfr)

    @forge
    def set_target(self, temp):
        self.target_temp = temp
        return f"Target set to {temp}°C"

    @forge
    def adjust(self, delta):
        self.target_temp += delta
        return f"Adjusted to {self.target_temp}°C"


class TestThermostat:
    def test_valid_temperature(self):
        thermo = Thermostat()
        thermo.set_target(25)
        assert thermo.target_temp == 25

    def test_exceeds_max_blocked(self):
        thermo = Thermostat()
        thermo.set_target(28)  # OK

        with pytest.raises(LawViolation):
            thermo.adjust(5)  # Would be 33 > 30

        assert thermo.target_temp == 28


class Inventory(Blueprint):
    """Track inventory with minimum stock."""
    stock = field(int, default=100)
    reserved = field(int, default=0)
    min_stock = field(int, default=10)

    @law
    def stock_non_negative(self):
        when(self.stock < 0, finfr)

    @law
    def reserved_within_stock(self):
        when(self.reserved > self.stock, finfr)

    @law
    def maintain_minimum(self):
        available = self.stock - self.reserved
        when(available < self.min_stock, finfr)

    @forge
    def reserve(self, quantity):
        self.reserved += quantity
        return f"Reserved {quantity}"


class TestInventory:
    def test_valid_reservation(self):
        inv = Inventory(stock=50)
        inv.reserve(30)  # available = 20
        assert inv.reserved == 30

    def test_minimum_maintained(self):
        inv = Inventory(stock=50)
        inv.reserve(30)  # available = 20

        with pytest.raises(LawViolation):
            inv.reserve(15)  # Would leave available = 5 < 10


class TrafficLight(Blueprint):
    """Traffic light with valid state transitions."""
    state = field(str, default="red")

    @law
    def valid_state(self):
        valid_states = ["red", "yellow", "green"]
        when(self.state not in valid_states, finfr)

    @forge
    def next(self):
        transitions = {"red": "green", "green": "yellow", "yellow": "red"}
        self.state = transitions[self.state]
        return self.state


class TestTrafficLight:
    def test_state_cycle(self):
        light = TrafficLight()
        assert light.next() == "green"
        assert light.next() == "yellow"
        assert light.next() == "red"


# =============================================================================
# MATTER TYPES
# =============================================================================

class TestMatterTypes:
    def test_money_arithmetic(self):
        m1 = Money(100)
        m2 = Money(50)

        assert (m1 + m2).value == 150
        assert (m1 - m2).value == 50
        assert (m1 * 2).value == 200
        assert (m1 / 2).value == 50

    def test_money_comparisons(self):
        assert Money(100) > Money(50)
        assert Money(50) < Money(100)
        assert Money(100) == Money(100)

    def test_type_safety(self):
        money = Money(100)
        mass = Mass(50)

        with pytest.raises(TypeError):
            money + mass

    def test_temperature_conversion(self):
        c = Celsius(100)
        f = c.to_fahrenheit()
        assert abs(f.value - 212) < 0.01


# =============================================================================
# KINETIC ENGINE
# =============================================================================

class TestKineticEngine:
    def test_basic_motion(self):
        engine = KineticEngine()
        start = Presence({'x': 0, 'y': 0})
        end = Presence({'x': 100, 'y': 50})

        result = engine.resolve_motion(start, end)

        assert result['status'] == 'synchronized'
        assert result['delta']['x']['delta'] == 100
        assert result['delta']['y']['delta'] == 50

    def test_boundary_violation(self):
        engine = KineticEngine()
        engine.add_boundary(
            lambda d: d.changes.get('x', {}).get('to', 0) > 80,
            name="MaxX"
        )

        start = Presence({'x': 0})
        end = Presence({'x': 100})  # Exceeds 80

        result = engine.resolve_motion(start, end)

        assert result['status'] == 'finfr'
        assert 'MaxX' in result['reason']

    def test_interpolation(self):
        engine = KineticEngine()
        start = Presence({'x': 0, 'y': 0})
        end = Presence({'x': 100, 'y': 100})

        frames = engine.interpolate(start, end, steps=5)

        assert len(frames) == 5
        assert frames[0].state['x'] == 0
        assert frames[-1].state['x'] == 100


# =============================================================================
# RATIO CONSTRAINTS
# =============================================================================

class LeverageGovernor(Blueprint):
    debt = field(float, default=0.0)
    equity = field(float, default=1000.0)

    @law
    def max_leverage(self):
        when(ratio(self.debt, self.equity) > 3.0, finfr)

    @forge
    def borrow(self, amount):
        self.debt += amount


class TestRatioConstraints:
    def test_valid_ratio(self):
        gov = LeverageGovernor()
        gov.borrow(2000)  # ratio = 2.0
        assert gov.debt == 2000

    def test_ratio_exceeded(self):
        gov = LeverageGovernor()
        gov.borrow(2000)  # ratio = 2.0

        with pytest.raises(LawViolation):
            gov.borrow(1500)  # Would be 3.5 > 3.0

    def test_ratio_result_class(self):
        r = RatioResult(500, 1000)
        assert r.value == 0.5
        assert not r.undefined
        assert r < 1.0

        r_undef = RatioResult(100, 0)
        assert r_undef.undefined
        assert r_undef > 1.0


# =============================================================================
# INTERMEDIATE EXAMPLES
# =============================================================================

class GameCharacter(Blueprint):
    health = field(int, default=100)
    max_health = field(int, default=100)
    mana = field(int, default=50)
    max_mana = field(int, default=50)

    @law
    def health_bounds(self):
        when(self.health < 0, finfr)
        when(self.health > self.max_health, finfr)

    @law
    def mana_bounds(self):
        when(self.mana < 0, finfr)

    @forge
    def take_damage(self, amount):
        self.health -= amount
        return self.health

    @forge
    def cast_spell(self, mana_cost):
        self.mana -= mana_cost
        return self.mana


class TestGameCharacter:
    def test_take_damage(self):
        hero = GameCharacter()
        hero.take_damage(30)
        assert hero.health == 70

    def test_death_prevented(self):
        hero = GameCharacter(health=10)

        with pytest.raises(LawViolation):
            hero.take_damage(20)  # Would be -10

    def test_mana_exhaustion(self):
        hero = GameCharacter()
        hero.cast_spell(30)  # mana = 20

        with pytest.raises(LawViolation):
            hero.cast_spell(30)  # Would be -10


# =============================================================================
# NES LESSON PLAN
# =============================================================================

class NESLessonPlan(Blueprint):
    title = field(str, default="")
    teks_codes = field(list, default=None)
    opening = field(int, default=5)
    instruction = field(int, default=15)
    guided = field(int, default=15)
    independent = field(int, default=10)
    closing = field(int, default=5)

    @law
    def total_50_minutes(self):
        total = self.opening + self.instruction + self.guided + self.independent + self.closing
        when(total != 50, finfr)

    @law
    def valid_phase_durations(self):
        when(self.opening < 3, finfr)
        when(self.instruction < 10, finfr)
        when(self.guided < 10, finfr)
        when(self.independent < 5, finfr)
        when(self.closing < 3, finfr)

    @law
    def has_teks(self):
        when(self.teks_codes is None or len(self.teks_codes) == 0, finfr)

    @forge
    def set_phases(self, opening, instruction, guided, independent, closing):
        self.opening = opening
        self.instruction = instruction
        self.guided = guided
        self.independent = independent
        self.closing = closing

    @forge
    def add_teks(self, code):
        if self.teks_codes is None:
            self.teks_codes = []
        self.teks_codes.append(code)


class TestNESLessonPlan:
    def test_valid_lesson(self):
        lesson = NESLessonPlan(title="Test")
        lesson.add_teks("5.3A")
        lesson.set_phases(5, 15, 15, 10, 5)  # = 50
        assert lesson.opening == 5

    def test_invalid_duration(self):
        lesson = NESLessonPlan(title="Test")
        lesson.add_teks("5.3A")

        with pytest.raises(LawViolation):
            lesson.set_phases(5, 20, 20, 10, 10)  # = 65 != 50


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
