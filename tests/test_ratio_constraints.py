#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
TEST: f/g Ratio Constraints - Dimensional Analysis for Computation
═══════════════════════════════════════════════════════════════════════════════

Tests for Newton's f/g ratio constraint system:
- f = forge/fact/function (what you're trying to do)
- g = ground/goal/governance (what reality allows)

When f/g is undefined (g=0) or exceeds bounds → finfr (ontological death)

This is not just verification - it's physics.
"""

import sys
import os

# Add parent directory to path for imports
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent_dir)
sys.path.insert(0, os.path.join(_parent_dir, 'core'))
sys.path.insert(0, os.path.join(_parent_dir, 'tinytalk_py'))

# Import directly from cdl module to avoid core/__init__.py issues
from cdl import (
    RatioConstraint,
    AtomicConstraint,
    Operator,
    Domain,
    CDLEvaluator,
    CDLParser,
    verify,
    verify_ratio,
    ratio,
)

# Import from tinytalk_py core directly
from tinytalk_py.core import (
    Blueprint,
    Field as field_class,
    law,
    forge,
    when,
    finfr,
    ratio as tinytalk_ratio,
    finfr_if_undefined,
    RatioResult,
    LawViolation,
)

# Helper for field creation
def field(type_=None, default=None):
    return field_class(type_=type_, default=default)


class TestRatioResult:
    """Tests for the RatioResult class in tinytalk."""

    def test_basic_ratio(self):
        """Test basic ratio calculation."""
        r = RatioResult(500, 1000)
        assert r.value == 0.5
        assert not r.undefined

    def test_undefined_ratio(self):
        """Test undefined ratio when denominator is zero."""
        r = RatioResult(100, 0)
        assert r.undefined
        assert r.value == float('inf')

    def test_ratio_comparisons(self):
        """Test ratio comparison operators."""
        r1 = RatioResult(500, 1000)  # 0.5
        assert r1 < 1.0
        assert r1 <= 1.0
        assert r1 <= 0.5
        assert not r1 > 1.0
        assert not r1 >= 1.0

        r2 = RatioResult(1500, 1000)  # 1.5
        assert r2 > 1.0
        assert r2 >= 1.0
        assert not r2 < 1.0
        assert not r2 <= 1.0

    def test_undefined_ratio_comparisons(self):
        """Test that undefined ratios behave correctly in comparisons."""
        r = RatioResult(100, 0)  # Undefined
        # Undefined ratio is always "greater" than any finite value
        assert r > 1.0
        assert r > 1000.0
        assert r >= 1.0
        # Undefined ratio never satisfies less-than
        assert not r < 1.0
        assert not r <= 1.0
        # Undefined ratio is never equal to a finite value
        assert not r == 1.0


class TestCDLRatioConstraint:
    """Tests for CDL RatioConstraint class."""

    def test_ratio_constraint_creation(self):
        """Test creating a RatioConstraint."""
        rc = RatioConstraint(
            f_field="liabilities",
            g_field="assets",
            operator=Operator.RATIO_LE,
            threshold=1.0,
            domain=Domain.FINANCIAL
        )
        assert rc.f_field == "liabilities"
        assert rc.g_field == "assets"
        assert rc.operator == Operator.RATIO_LE
        assert rc.threshold == 1.0

    def test_ratio_constraint_evaluation_pass(self):
        """Test ratio constraint evaluation that passes."""
        rc = RatioConstraint(
            f_field="liabilities",
            g_field="assets",
            operator=Operator.RATIO_LE,
            threshold=1.0
        )
        evaluator = CDLEvaluator()
        result = evaluator.evaluate(rc, {"liabilities": 500, "assets": 1000})
        assert result.passed

    def test_ratio_constraint_evaluation_fail(self):
        """Test ratio constraint evaluation that fails."""
        rc = RatioConstraint(
            f_field="liabilities",
            g_field="assets",
            operator=Operator.RATIO_LE,
            threshold=1.0
        )
        evaluator = CDLEvaluator()
        result = evaluator.evaluate(rc, {"liabilities": 1500, "assets": 1000})
        assert not result.passed
        assert "finfr" in result.message

    def test_ratio_constraint_undefined(self):
        """Test ratio constraint with undefined ratio (g=0)."""
        rc = RatioConstraint(
            f_field="withdrawal",
            g_field="balance",
            operator=Operator.RATIO_LE,
            threshold=1.0
        )
        evaluator = CDLEvaluator()
        result = evaluator.evaluate(rc, {"withdrawal": 100, "balance": 0})
        assert not result.passed
        assert "undefined" in result.message.lower()


class TestVerifyRatio:
    """Tests for the verify_ratio convenience function."""

    def test_verify_ratio_pass(self):
        """Test verify_ratio that passes."""
        result = verify_ratio("debt", "equity", "ratio_le", 3.0,
                              {"debt": 2000, "equity": 1000})
        assert result.passed

    def test_verify_ratio_fail(self):
        """Test verify_ratio that fails."""
        result = verify_ratio("debt", "equity", "ratio_le", 1.0,
                              {"debt": 2000, "equity": 1000})
        assert not result.passed

    def test_verify_ratio_undefined(self):
        """Test verify_ratio with undefined ratio."""
        result = verify_ratio("amount", "limit", "ratio_le", 1.0,
                              {"amount": 100, "limit": 0})
        assert not result.passed


class TestRatioFunction:
    """Tests for the ratio() convenience function."""

    def test_ratio_function_creates_constraint(self):
        """Test that ratio() creates a RatioConstraint."""
        rc = ratio("debt", "equity", threshold=3.0)
        assert isinstance(rc, RatioConstraint)
        assert rc.f_field == "debt"
        assert rc.g_field == "equity"
        assert rc.threshold == 3.0

    def test_ratio_function_default_operator(self):
        """Test ratio() default operator is ratio_le."""
        rc = ratio("f", "g")
        assert rc.operator == Operator.RATIO_LE
        assert rc.threshold == 1.0


class TestCDLParserRatio:
    """Tests for parsing ratio constraints from dict/JSON."""

    def test_parse_ratio_constraint(self):
        """Test parsing a ratio constraint from dict."""
        parser = CDLParser()
        constraint = parser.parse({
            "f_field": "liabilities",
            "g_field": "assets",
            "operator": "ratio_le",
            "threshold": 1.0,
            "domain": "financial"
        })
        assert isinstance(constraint, RatioConstraint)
        assert constraint.f_field == "liabilities"
        assert constraint.g_field == "assets"

    def test_verify_parsed_ratio(self):
        """Test verifying a parsed ratio constraint."""
        result = verify(
            {
                "f_field": "flicker_rate",
                "g_field": "safe_threshold",
                "operator": "ratio_lt",
                "threshold": 1.0
            },
            {"flicker_rate": 2.5, "safe_threshold": 3.0}
        )
        assert result.passed


class TestAtomicConstraintRatio:
    """Tests for ratio operators in AtomicConstraint."""

    def test_atomic_constraint_with_denominator(self):
        """Test AtomicConstraint with denominator field."""
        ac = AtomicConstraint(
            domain=Domain.FINANCIAL,
            field="debt",
            operator=Operator.RATIO_LE,
            value=3.0,
            denominator="equity"
        )
        evaluator = CDLEvaluator()
        result = evaluator.evaluate(ac, {"debt": 2000, "equity": 1000})
        assert result.passed

    def test_atomic_constraint_ratio_fail(self):
        """Test AtomicConstraint ratio that fails."""
        ac = AtomicConstraint(
            domain=Domain.FINANCIAL,
            field="debt",
            operator=Operator.RATIO_LE,
            value=1.0,
            denominator="equity"
        )
        evaluator = CDLEvaluator()
        result = evaluator.evaluate(ac, {"debt": 2000, "equity": 1000})
        assert not result.passed


class TestBlueprintRatioLaws:
    """Tests for ratio constraints in Blueprint laws."""

    def test_blueprint_ratio_law_pass(self):
        """Test Blueprint with ratio law that passes."""

        class Account(Blueprint):
            balance = field(float, default=1000.0)
            liabilities = field(float, default=0.0)

            @law
            def no_insolvency(self):
                when(tinytalk_ratio(self.liabilities, self.balance) > 1.0, finfr)

            @forge
            def borrow(self, amount: float):
                self.liabilities += amount

        acc = Account()
        acc.borrow(500)  # Should work - ratio = 0.5
        assert acc.liabilities == 500

    def test_blueprint_ratio_law_fail(self):
        """Test Blueprint with ratio law that blocks operation."""

        class Account(Blueprint):
            balance = field(float, default=1000.0)
            liabilities = field(float, default=0.0)

            @law
            def no_insolvency(self):
                when(tinytalk_ratio(self.liabilities, self.balance) > 1.0, finfr)

            @forge
            def borrow(self, amount: float):
                self.liabilities += amount

        acc = Account()
        try:
            acc.borrow(1500)  # Should fail - ratio = 1.5
            assert False, "LawViolation should have been raised"
        except LawViolation:
            pass  # Expected

    def test_blueprint_finfr_if_undefined(self):
        """Test Blueprint with finfr_if_undefined."""

        class SafeCalculator(Blueprint):
            numerator = field(float, default=100.0)
            denominator = field(float, default=1.0)

            @law
            def valid_denominator(self):
                finfr_if_undefined(self.numerator, self.denominator)

            @forge
            def set_denominator(self, value: float):
                self.denominator = value

        calc = SafeCalculator()
        calc.set_denominator(5.0)  # Should work
        assert calc.denominator == 5.0

        try:
            calc.set_denominator(0.0)  # Should fail - undefined ratio
            assert False, "LawViolation should have been raised"
        except LawViolation:
            pass  # Expected


class TestRatioOperators:
    """Tests for all ratio operators."""

    def test_ratio_lt(self):
        """Test ratio_lt operator."""
        result = verify_ratio("f", "g", "ratio_lt", 1.0, {"f": 0.5, "g": 1.0})
        assert result.passed
        result = verify_ratio("f", "g", "ratio_lt", 1.0, {"f": 1.0, "g": 1.0})
        assert not result.passed  # Equal, not less than

    def test_ratio_le(self):
        """Test ratio_le operator."""
        result = verify_ratio("f", "g", "ratio_le", 1.0, {"f": 1.0, "g": 1.0})
        assert result.passed  # Equal
        result = verify_ratio("f", "g", "ratio_le", 1.0, {"f": 1.1, "g": 1.0})
        assert not result.passed

    def test_ratio_gt(self):
        """Test ratio_gt operator."""
        result = verify_ratio("f", "g", "ratio_gt", 1.0, {"f": 1.5, "g": 1.0})
        assert result.passed
        result = verify_ratio("f", "g", "ratio_gt", 1.0, {"f": 1.0, "g": 1.0})
        assert not result.passed  # Equal, not greater

    def test_ratio_ge(self):
        """Test ratio_ge operator."""
        result = verify_ratio("f", "g", "ratio_ge", 1.0, {"f": 1.0, "g": 1.0})
        assert result.passed  # Equal
        result = verify_ratio("f", "g", "ratio_ge", 1.0, {"f": 0.5, "g": 1.0})
        assert not result.passed

    def test_ratio_eq(self):
        """Test ratio_eq operator."""
        result = verify_ratio("f", "g", "ratio_eq", 1.0, {"f": 1.0, "g": 1.0})
        assert result.passed
        result = verify_ratio("f", "g", "ratio_eq", 1.0, {"f": 1.5, "g": 1.0})
        assert not result.passed

    def test_ratio_ne(self):
        """Test ratio_ne operator."""
        result = verify_ratio("f", "g", "ratio_ne", 1.0, {"f": 1.5, "g": 1.0})
        assert result.passed
        result = verify_ratio("f", "g", "ratio_ne", 1.0, {"f": 1.0, "g": 1.0})
        assert not result.passed


def run_tests():
    """Run all tests and print results."""
    import traceback

    test_classes = [
        TestRatioResult,
        TestCDLRatioConstraint,
        TestVerifyRatio,
        TestRatioFunction,
        TestCDLParserRatio,
        TestAtomicConstraintRatio,
        TestBlueprintRatioLaws,
        TestRatioOperators,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for test_class in test_classes:
        print(f"\n{test_class.__name__}")
        print("=" * len(test_class.__name__))
        instance = test_class()

        for method_name in dir(instance):
            if method_name.startswith("test_"):
                total_tests += 1
                try:
                    getattr(instance, method_name)()
                    print(f"  ✓ {method_name}")
                    passed_tests += 1
                except Exception as e:
                    print(f"  ✗ {method_name}: {e}")
                    failed_tests.append((test_class.__name__, method_name, traceback.format_exc()))

    print("\n" + "=" * 60)
    print(f"Results: {passed_tests}/{total_tests} tests passed")

    if failed_tests:
        print("\nFailed tests:")
        for class_name, method_name, tb in failed_tests:
            print(f"\n{class_name}.{method_name}:")
            print(tb)
        return 1

    print("\nAll tests passed! finfr = f/g. The ratio IS the constraint.")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
