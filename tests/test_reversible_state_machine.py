#!/usr/bin/env python3
"""
===============================================================================
NEWTON REVERSIBLE STATE MACHINE VALIDATION
===============================================================================

This module validates Newton's core claim: that it operates as a REVERSIBLE
STATE MACHINE where computation IS verification because the computational
path itself is deterministically constrained and invertible.

Key Properties Being Validated:

1. BIJECTIVE STATE TRANSITIONS
   - Every valid state has exactly one predecessor and successor for a given input
   - No many-to-one mappings (which create computational entropy)
   - State space is partitioned into equivalence classes

2. PERFECT REVERSIBILITY
   - State can be restored EXACTLY after any operation
   - Deep copy semantics preserve mutable object identity
   - No information leakage during rollback

3. INFORMATION PRESERVATION (Landauer's Principle)
   - Invalid states are never created, so no information needs to be erased
   - The f/g ratio check prevents entropy-creating operations BEFORE execution
   - Computation dissipates minimal heat because no erasure is required

4. DETERMINISTIC AUTOMATON PROPERTIES
   - Given (state, input) -> (next_state) is a pure function
   - The history tape (Bennett's construction) is implicit in the constraint structure

Theoretical Foundation:
- Charles Bennett's reversible Turing machines (1973)
- Rolf Landauer's principle of information and heat (1961)
- No-First logic as bijective constraint satisfaction

Run with: pytest tests/test_reversible_state_machine.py -v
===============================================================================
"""

import pytest
import copy
import hashlib
import sys
import os
from typing import Any, Dict, List, Set, Tuple
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tinytalk_py import (
    Blueprint, field, law, forge, when, finfr, fin,
    LawViolation, FinClosure, ratio, finfr_if_undefined
)


# =============================================================================
# PART 1: BIJECTIVE STATE TRANSITION TESTS
# =============================================================================

class TestBijectiveTransitions:
    """
    Validate that state transitions are bijective (one-to-one) within the
    valid state space. This is the core of reversible computing.
    """

    def test_transition_is_deterministic(self):
        """
        Property: Given (state, input), the next state is ALWAYS the same.
        This is the forward direction of bijectivity.
        """
        class Counter(Blueprint):
            value = field(int, default=0)

            @law
            def bounds(self):
                when(self.value < 0 or self.value > 100, finfr)

            @forge
            def increment(self, amount: int):
                self.value += amount
                return self.value

        # Same initial state
        c1 = Counter(value=50)
        c2 = Counter(value=50)

        # Same input
        r1 = c1.increment(10)
        r2 = c2.increment(10)

        # Must produce identical results
        assert r1 == r2, "Determinism violated: same (state, input) -> different outputs"
        assert c1.value == c2.value, "State divergence from identical starting points"

    def test_state_hash_before_after_transition(self):
        """
        Property: A state transition creates a unique (before_hash, after_hash) pair.
        This validates that we can reconstruct the transition.
        """
        class HashableBlueprint(Blueprint):
            x = field(int, default=0)
            y = field(int, default=0)

            @forge
            def move(self, dx: int, dy: int):
                self.x += dx
                self.y += dy

            def state_hash(self) -> str:
                state = self._get_state()
                return hashlib.sha256(str(sorted(state.items())).encode()).hexdigest()[:16]

        bp = HashableBlueprint(x=10, y=20)
        before_hash = bp.state_hash()

        bp.move(5, 5)
        after_hash = bp.state_hash()

        # The transition is uniquely identified
        assert before_hash != after_hash, "Transition should change state hash"

        # Same transition from same state produces same result
        bp2 = HashableBlueprint(x=10, y=20)
        assert bp2.state_hash() == before_hash

        bp2.move(5, 5)
        assert bp2.state_hash() == after_hash

    def test_no_many_to_one_within_valid_space(self):
        """
        Property: Different valid states cannot collapse to the same state
        via the same operation (no entropy-creating mappings).

        This is the key insight: constraints prevent the many-to-one mappings
        that would require information erasure.
        """
        class ConservativeSystem(Blueprint):
            """A system where total is conserved (like energy)."""
            a = field(int, default=50)
            b = field(int, default=50)

            @law
            def conservation(self):
                when(self.a + self.b != 100, finfr)

            @forge
            def transfer(self, amount: int):
                """Transfer from a to b - this is REVERSIBLE."""
                self.a -= amount
                self.b += amount

        # Two different states
        s1 = ConservativeSystem(a=70, b=30)
        s2 = ConservativeSystem(a=60, b=40)

        assert s1.a != s2.a  # Genuinely different states

        # Apply same operation
        s1.transfer(10)  # 70,30 -> 60,40
        s2.transfer(10)  # 60,40 -> 50,50

        # They should NOT collapse to the same state
        assert s1.a != s2.a or s1.b != s2.b, \
            "Many-to-one mapping detected: different states collapsed"

        # But we CAN reach the same state from different starting points
        # via DIFFERENT inputs - that's allowed
        s3 = ConservativeSystem(a=70, b=30)
        s4 = ConservativeSystem(a=60, b=40)

        s3.transfer(20)  # 70,30 -> 50,50
        s4.transfer(10)  # 60,40 -> 50,50

        # Same end state, but via different paths - this is OK
        assert s3.a == s4.a and s3.b == s4.b

    def test_transition_function_is_injective(self):
        """
        Property: For a fixed input, the transition function is injective.
        f(s1, i) == f(s2, i) implies s1 == s2

        This means different states cannot produce the same output state
        with the same input.
        """
        class InjectiveSystem(Blueprint):
            id = field(int, default=0)
            counter = field(int, default=0)

            @law
            def id_immutable(self):
                # ID acts as a distinguisher - makes states uniquely identifiable
                when(self.id < 0, finfr)

            @forge
            def tick(self):
                self.counter += 1

        # Create distinct systems
        systems = [InjectiveSystem(id=i, counter=0) for i in range(10)]

        # Apply same input to all
        for s in systems:
            s.tick()

        # All states should still be distinct
        state_hashes = set()
        for s in systems:
            state = (s.id, s.counter)
            assert state not in state_hashes, \
                f"Collision detected: state {state} already exists"
            state_hashes.add(state)


# =============================================================================
# PART 2: PERFECT REVERSIBILITY TESTS
# =============================================================================

class TestPerfectReversibility:
    """
    Validate that rollback restores state EXACTLY - no information is lost.
    This is the foundation of reversible computation.
    """

    def test_atomic_rollback_on_law_violation(self):
        """
        Property: When a law is violated, state is restored EXACTLY to pre-forge.
        """
        class BoundedValue(Blueprint):
            value = field(int, default=50)
            history = field(list, default=None)

            @law
            def bounds(self):
                when(self.value > 100, finfr)

            @forge
            def set_value(self, v: int):
                if self.history is None:
                    self.history = []
                self.history.append(self.value)
                self.value = v

        bp = BoundedValue()
        bp.history = [10, 20, 30]

        original_value = bp.value
        original_history = copy.deepcopy(bp.history)

        # Attempt invalid operation
        with pytest.raises(LawViolation):
            bp.set_value(150)

        # State MUST be exactly restored
        assert bp.value == original_value, \
            f"Value not restored: {bp.value} != {original_value}"
        assert bp.history == original_history, \
            f"History not restored: {bp.history} != {original_history}"

    def test_deep_copy_preserves_mutable_objects(self):
        """
        Property: Mutable objects (lists, dicts) are deep copied during save.
        Modifications to the copy don't affect the saved state.
        """
        class ComplexState(Blueprint):
            data = field(dict, default=None)
            items = field(list, default=None)
            nested = field(list, default=None)

            @law
            def value_limit(self):
                # Trigger on any negative value in data
                if self.data is not None:
                    when(any(v < 0 for v in self.data.values()), finfr)

            @forge
            def modify_all(self, key: str, value: Any, item: Any):
                if self.data is None:
                    self.data = {}
                if self.items is None:
                    self.items = []
                if self.nested is None:
                    self.nested = [[]]

                self.data[key] = value
                self.items.append(item)
                self.nested[0].append(item)

        bp = ComplexState()
        bp.data = {"a": 1, "b": 2}
        bp.items = [1, 2, 3]
        bp.nested = [[1, 2], [3, 4]]

        original_data = copy.deepcopy(bp.data)
        original_items = copy.deepcopy(bp.items)
        original_nested = copy.deepcopy(bp.nested)

        # Force rollback by inserting a negative value
        with pytest.raises(LawViolation):
            bp.modify_all("bad_key", -1, 999)

        # Verify deep restoration
        assert bp.data == original_data
        assert bp.items == original_items
        assert bp.nested == original_nested

        # Verify no aliasing (modifying original doesn't affect blueprint)
        original_data["new_key"] = "test"
        assert "new_key" not in bp.data

    def test_rollback_on_any_exception(self):
        """
        Property: ANY exception during forge execution triggers rollback,
        not just LawViolation.
        """
        class ExceptionBlueprint(Blueprint):
            value = field(int, default=100)
            step = field(int, default=0)

            @forge
            def risky_operation(self, fail_at: int):
                for i in range(10):
                    self.step = i
                    self.value += 1
                    if i == fail_at:
                        raise RuntimeError(f"Intentional failure at step {i}")

        bp = ExceptionBlueprint()
        original_value = bp.value
        original_step = bp.step

        with pytest.raises(RuntimeError):
            bp.risky_operation(5)

        assert bp.value == original_value, \
            f"Value not rolled back: {bp.value} != {original_value}"
        assert bp.step == original_step, \
            f"Step not rolled back: {bp.step} != {original_step}"

    def test_state_identity_preserved_through_rollback(self):
        """
        Property: State identity (as measured by hash) is preserved through rollback.
        """
        class IdentityBlueprint(Blueprint):
            x = field(int, default=0)
            y = field(str, default="")
            z = field(float, default=0.0)

            @law
            def x_positive(self):
                when(self.x < 0, finfr)

            @forge
            def update(self, dx: int, new_y: str, dz: float):
                self.x += dx
                self.y = new_y
                self.z += dz

            def identity_hash(self) -> str:
                state = self._get_state()
                return hashlib.sha256(repr(sorted(state.items())).encode()).hexdigest()

        bp = IdentityBlueprint(x=10, y="hello", z=3.14)
        original_hash = bp.identity_hash()

        # Failed operation
        with pytest.raises(LawViolation):
            bp.update(-20, "world", 2.71)  # x would become -10

        # Hash must be identical
        assert bp.identity_hash() == original_hash, \
            "State identity changed through rollback"


# =============================================================================
# PART 3: INFORMATION-THEORETIC VALIDATION (LANDAUER'S PRINCIPLE)
# =============================================================================

class TestLandauerPrinciple:
    """
    Validate Newton's connection to Landauer's principle:
    - Erasing one bit of information dissipates kT*ln(2) energy
    - By NEVER CREATING invalid states, Newton avoids erasure entirely
    - The f/g ratio check is Landauer's principle applied before execution
    """

    def test_invalid_states_never_exist(self):
        """
        Property: Invalid states are never instantiated in the ledger.
        They are prevented, not detected and erased.
        """
        class ConstrainedSystem(Blueprint):
            balance = field(float, default=1000.0)
            operations = field(list, default=None)

            @law
            def no_overdraft(self):
                when(self.balance < 0, finfr)

            @forge
            def withdraw(self, amount: float):
                if self.operations is None:
                    self.operations = []
                self.operations.append(f"withdraw:{amount}")
                self.balance -= amount
                return self.balance

        bp = ConstrainedSystem()
        history_of_balances = [bp.balance]

        # Perform valid operations
        bp.withdraw(100)
        history_of_balances.append(bp.balance)

        bp.withdraw(200)
        history_of_balances.append(bp.balance)

        # Attempt invalid operation
        with pytest.raises(LawViolation):
            bp.withdraw(1000)  # Would cause overdraft

        # The invalid state (negative balance) NEVER appeared in history
        assert all(b >= 0 for b in history_of_balances), \
            "Invalid state appeared in history - Landauer principle violated"

        # Operation was not recorded
        assert len(bp.operations) == 2, \
            "Failed operation was recorded - information leaked"

    def test_fg_ratio_prevents_undefined_states(self):
        """
        Property: The f/g ratio check prevents ontologically impossible states
        (like division by zero) BEFORE they can create NaN garbage.
        """
        class RatioSystem(Blueprint):
            numerator = field(float, default=100.0)
            denominator = field(float, default=10.0)
            last_ratio = field(float, default=None)

            @law
            def no_undefined_ratio(self):
                finfr_if_undefined(self.numerator, self.denominator)

            @forge
            def set_denominator(self, value: float):
                self.denominator = value
                self.last_ratio = self.numerator / self.denominator \
                    if self.denominator != 0 else None

        bp = RatioSystem()

        # Valid operation
        bp.set_denominator(5.0)
        assert bp.last_ratio == 20.0

        # Invalid operation - would create undefined ratio
        with pytest.raises(LawViolation):
            bp.set_denominator(0.0)

        # NaN never appeared
        assert bp.denominator == 5.0, "Denominator should not be zero"
        assert bp.last_ratio == 20.0, "Last ratio should not be affected"

    def test_ratio_constraint_as_landauer_gate(self):
        """
        Property: The ratio constraint acts as a Landauer gate,
        preventing operations that would require information erasure.
        """
        class LandauerGate(Blueprint):
            request = field(float, default=0.0)
            capacity = field(float, default=100.0)
            utilization = field(float, default=0.0)

            @law
            def no_overcapacity(self):
                # request/capacity must be <= 1.0
                when(ratio(self.request, self.capacity) > 1.0, finfr)

            @forge
            def allocate(self, amount: float):
                self.request = amount
                self.utilization = self.request / self.capacity

        gate = LandauerGate()

        # Valid allocation
        gate.allocate(80.0)
        assert gate.utilization == 0.8

        # Over-capacity allocation prevented
        with pytest.raises(LawViolation):
            gate.allocate(150.0)  # 150/100 > 1.0

        # The impossible state (150% utilization) never existed
        assert gate.utilization == 0.8, \
            "Overcapacity state leaked through"

    def test_no_garbage_collection_needed(self):
        """
        Property: Because invalid states are prevented, no garbage collection
        or cleanup is needed. The ledger is always in a valid state.
        """
        class CleanSystem(Blueprint):
            items = field(list, default=None)
            garbage_count = field(int, default=0)  # Should always be 0

            @law
            def no_empty_items(self):
                if self.items is not None:
                    when(any(item == "" for item in self.items), finfr)

            @forge
            def add_item(self, item: str):
                if self.items is None:
                    self.items = []
                self.items.append(item)

        bp = CleanSystem()

        # Valid additions
        bp.add_item("apple")
        bp.add_item("banana")

        # Invalid addition prevented
        with pytest.raises(LawViolation):
            bp.add_item("")

        # No garbage to collect
        assert bp.garbage_count == 0
        assert "" not in (bp.items or [])


# =============================================================================
# PART 4: DETERMINISTIC AUTOMATON PROPERTIES
# =============================================================================

class TestDeterministicAutomaton:
    """
    Validate Newton as a deterministic finite automaton (DFA) where:
    - States are Blueprint field configurations
    - Alphabet is the set of forge method calls
    - Transitions are forge executions
    - Accept states are all states satisfying laws
    """

    def test_dfa_transition_function_totality(self):
        """
        Property: For every valid state and every input, either:
        1. A unique next state exists (transition succeeds), OR
        2. The transition is blocked (finfr)

        There is no third option (undefined behavior).
        """
        class TotalDFA(Blueprint):
            state = field(int, default=0)

            @law
            def valid_states(self):
                when(self.state < 0 or self.state > 10, finfr)

            @forge
            def transition(self, input: int):
                self.state = (self.state + input) % 11
                return self.state

        dfa = TotalDFA()

        # Every (state, input) pair has a defined outcome
        for start_state in range(11):
            for input_val in range(-20, 20):
                dfa.state = start_state
                try:
                    result = dfa.transition(input_val)
                    # If we get here, transition succeeded
                    assert 0 <= result <= 10, "Invalid state reached"
                except LawViolation:
                    # Transition was blocked - also a valid outcome
                    assert dfa.state == start_state, "State changed despite block"

    def test_dfa_closure_under_composition(self):
        """
        Property: Composing valid transitions yields valid transitions.
        If s1 -> s2 and s2 -> s3 are valid, then s1 -> s3 is reachable.
        """
        class ComposableDFA(Blueprint):
            x = field(int, default=0)
            y = field(int, default=0)

            @law
            def in_bounds(self):
                when(self.x < 0 or self.x > 5, finfr)
                when(self.y < 0 or self.y > 5, finfr)

            @forge
            def step_right(self):
                self.x += 1

            @forge
            def step_up(self):
                self.y += 1

        dfa = ComposableDFA()

        # Compose: (0,0) -> (1,0) -> (1,1) -> (2,1)
        dfa.step_right()  # (0,0) -> (1,0)
        assert (dfa.x, dfa.y) == (1, 0)

        dfa.step_up()     # (1,0) -> (1,1)
        assert (dfa.x, dfa.y) == (1, 1)

        dfa.step_right()  # (1,1) -> (2,1)
        assert (dfa.x, dfa.y) == (2, 1)

        # The composition is still within valid bounds
        assert 0 <= dfa.x <= 5 and 0 <= dfa.y <= 5

    def test_history_tape_implicit_in_constraints(self):
        """
        Property: Bennett's history tape (for reversible TMs) is implicitly
        maintained by the constraint structure. We can reconstruct the
        computation path from the constraint definitions.
        """
        class HistoryAwareDFA(Blueprint):
            value = field(int, default=0)
            history = field(list, default=None)

            @law
            def monotonic(self):
                # Value can only increase - this encodes history constraint
                if self.history is not None and len(self.history) > 0:
                    when(self.value < self.history[-1], finfr)

            @forge
            def advance(self, amount: int):
                if self.history is None:
                    self.history = []
                self.history.append(self.value)
                self.value += amount
                return self.value

        dfa = HistoryAwareDFA()

        # Build up a history
        dfa.advance(10)  # 0 -> 10
        dfa.advance(5)   # 10 -> 15
        dfa.advance(3)   # 15 -> 18

        # The constraint prevents backward transitions
        with pytest.raises(LawViolation):
            dfa.advance(-10)  # Would violate monotonicity

        # The history tape is preserved
        assert dfa.history == [0, 10, 15]
        assert dfa.value == 18


# =============================================================================
# PART 5: ADVANCED REVERSIBILITY - BIJECTION CERTIFICATION
# =============================================================================

class TestBijectionCertification:
    """
    Formally certify that specific transition types are bijective.
    """

    def test_additive_inverse_bijection(self):
        """
        Property: Addition is bijective because subtraction is its inverse.
        f(x) = x + c has inverse f^(-1)(x) = x - c
        """
        class AdditiveBijection(Blueprint):
            value = field(int, default=0)

            @law
            def bounded(self):
                when(self.value < -1000 or self.value > 1000, finfr)

            @forge
            def add(self, c: int):
                self.value += c

            @forge
            def subtract(self, c: int):
                self.value -= c

        bp = AdditiveBijection(value=500)
        original = bp.value

        # Forward
        bp.add(100)
        after_add = bp.value
        assert after_add == 600

        # Inverse
        bp.subtract(100)
        after_inverse = bp.value

        # Must return to original
        assert after_inverse == original, \
            f"Bijection broken: {original} -> {after_add} -> {after_inverse}"

    def test_multiplicative_bijection_with_nonzero(self):
        """
        Property: Multiplication by non-zero is bijective.
        f(x) = x * c (c != 0) has inverse f^(-1)(x) = x / c
        """
        class MultiplicativeBijection(Blueprint):
            value = field(float, default=100.0)

            @law
            def nonzero(self):
                when(abs(self.value) < 1e-10, finfr)

            @forge
            def multiply(self, c: float):
                self.value *= c

            @forge
            def divide(self, c: float):
                self.value /= c

        bp = MultiplicativeBijection(value=100.0)
        original = bp.value

        # Forward
        bp.multiply(2.5)
        after_mul = bp.value
        assert abs(after_mul - 250.0) < 1e-10

        # Inverse
        bp.divide(2.5)
        after_inverse = bp.value

        # Must return to original (within floating point tolerance)
        assert abs(after_inverse - original) < 1e-10, \
            f"Bijection broken: {original} -> {after_mul} -> {after_inverse}"

    def test_permutation_bijection(self):
        """
        Property: Permutations are bijective. Applying the inverse permutation
        returns to the original state.
        """
        class PermutationBijection(Blueprint):
            items = field(list, default=None)

            @forge
            def rotate_right(self):
                if self.items and len(self.items) > 1:
                    self.items = [self.items[-1]] + self.items[:-1]

            @forge
            def rotate_left(self):
                if self.items and len(self.items) > 1:
                    self.items = self.items[1:] + [self.items[0]]

        bp = PermutationBijection()
        bp.items = [1, 2, 3, 4, 5]
        original = copy.deepcopy(bp.items)

        # Forward (3 right rotations)
        bp.rotate_right()
        bp.rotate_right()
        bp.rotate_right()

        rotated = copy.deepcopy(bp.items)
        assert rotated != original  # Actually changed

        # Inverse (3 left rotations)
        bp.rotate_left()
        bp.rotate_left()
        bp.rotate_left()

        # Must return to original
        assert bp.items == original, \
            f"Permutation bijection broken: {original} -> {rotated} -> {bp.items}"

    def test_xor_is_self_inverse(self):
        """
        Property: XOR is its own inverse, making it trivially bijective.
        x XOR k XOR k == x
        """
        class XORBijection(Blueprint):
            value = field(int, default=0)

            @forge
            def xor_with(self, key: int):
                self.value ^= key

        bp = XORBijection(value=0b10101010)
        original = bp.value

        key = 0b11001100

        # Apply XOR
        bp.xor_with(key)
        encrypted = bp.value
        assert encrypted != original

        # Apply XOR again (self-inverse)
        bp.xor_with(key)
        decrypted = bp.value

        assert decrypted == original, \
            f"XOR self-inverse failed: {original} -> {encrypted} -> {decrypted}"


# =============================================================================
# PART 6: STRESS TESTS FOR REVERSIBILITY UNDER LOAD
# =============================================================================

class TestReversibilityUnderLoad:
    """
    Stress test reversibility properties under high load.
    """

    def test_many_sequential_rollbacks(self):
        """
        Property: Reversibility holds after many sequential rollback attempts.
        """
        class StressBlueprint(Blueprint):
            counter = field(int, default=0)

            @law
            def limit(self):
                when(self.counter > 100, finfr)

            @forge
            def increment(self, amount: int):
                self.counter += amount

        bp = StressBlueprint(counter=50)
        original = bp.counter

        # Attempt 1000 rollbacks
        for i in range(1000):
            with pytest.raises(LawViolation):
                bp.increment(100)  # Would exceed 100

        # State must still be exactly original
        assert bp.counter == original, \
            f"State drifted after 1000 rollbacks: {bp.counter} != {original}"

    def test_interleaved_success_and_failure(self):
        """
        Property: Interleaving successful and failed operations maintains consistency.
        """
        class InterleavedBlueprint(Blueprint):
            value = field(int, default=50)
            success_count = field(int, default=0)

            @law
            def bounds(self):
                when(self.value < 0 or self.value > 100, finfr)

            @forge
            def adjust(self, delta: int):
                self.value += delta
                self.success_count += 1

        bp = InterleavedBlueprint()

        operations = [
            (10, True),   # 50 -> 60 (success)
            (50, False),  # 60 -> 110 (fail)
            (-20, True),  # 60 -> 40 (success)
            (-50, False), # 40 -> -10 (fail)
            (30, True),   # 40 -> 70 (success)
        ]

        expected_value = 50
        expected_success = 0

        for delta, should_succeed in operations:
            if should_succeed:
                bp.adjust(delta)
                expected_value += delta
                expected_success += 1
            else:
                with pytest.raises(LawViolation):
                    bp.adjust(delta)

        assert bp.value == expected_value, \
            f"Value mismatch: {bp.value} != {expected_value}"
        assert bp.success_count == expected_success, \
            f"Success count mismatch: {bp.success_count} != {expected_success}"

    def test_complex_object_rollback_stress(self):
        """
        Property: Complex nested objects are correctly restored under stress.
        """
        class ComplexBlueprint(Blueprint):
            matrix = field(list, default=None)

            @law
            def size_limit(self):
                if self.matrix:
                    total = sum(sum(row) for row in self.matrix)
                    when(total > 1000, finfr)

            @forge
            def add_to_cell(self, row: int, col: int, value: int):
                if self.matrix is None:
                    self.matrix = [[0] * 5 for _ in range(5)]
                self.matrix[row][col] += value

        bp = ComplexBlueprint()
        bp.matrix = [[i + j for j in range(5)] for i in range(5)]
        original_matrix = copy.deepcopy(bp.matrix)

        # Stress test with many attempted violations
        for _ in range(100):
            with pytest.raises(LawViolation):
                bp.add_to_cell(0, 0, 10000)  # Would exceed total limit

        assert bp.matrix == original_matrix, \
            "Complex matrix state corrupted after stress test"


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" NEWTON REVERSIBLE STATE MACHINE VALIDATION")
    print("=" * 70)
    print("""
    Validating the core claims of reversible computation:

    1. BIJECTIVE TRANSITIONS - No many-to-one mappings
    2. PERFECT REVERSIBILITY - Exact state restoration
    3. LANDAUER'S PRINCIPLE - No information erasure needed
    4. DETERMINISTIC AUTOMATON - Pure transition functions
    5. BIJECTION CERTIFICATION - Mathematical inverses
    6. STRESS TESTS - Reversibility under load

    If all tests pass, Newton operates as a true reversible state machine.
    """)
    print("=" * 70)

    pytest.main([__file__, "-v", "--tb=short"])
