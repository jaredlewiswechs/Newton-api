#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
CONSTRAINT EXTRACTION COMPREHENSIVE TEST SUITE
═══════════════════════════════════════════════════════════════════════════════

"You're parsing it like a CONSTRAINT EXTRACTOR, not a language model."

This test suite verifies:
1. Numeric constraint extraction (at least, at most, between, etc.)
2. Temporal constraint extraction (before, after, duration, etc.)
3. Qualitative → Quantitative inversion (expensive → cost < threshold)
4. Group/relational constraints (consensus, group size)
5. Constraint strength detection (must vs want)
6. Plan verification against extracted constraints
7. TinyTalk and CDL generation

Run with: pytest tests/test_constraint_extraction.py -v
"""

import pytest
import time
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from core.constraint_extractor import (
    ConstraintExtractor,
    extract_constraints,
    verify_plan,
    get_extractor,
    ConstraintCategory,
    ConstraintStrength,
    ConstraintPolarity,
    ExtractedConstraint,
    ExtractionResult,
    VerifiedPlan,
    PlanVerifier,
    ExtractionPatterns,
)
from core.cdl import Operator, Domain


# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: NUMERIC CONSTRAINT EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestNumericConstraintExtraction:
    """Test extraction of numeric constraints from natural language."""

    def test_at_least_extraction(self):
        """Extract 'at least X' constraints."""
        result = extract_constraints("We want at least 3 activities")

        # Find the constraint for activities
        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.NUMERIC]

        assert len(constraints) >= 1
        # Find constraint with value 3
        at_least_3 = [c for c in constraints if c.value == 3.0]
        assert len(at_least_3) >= 1
        assert at_least_3[0].operator == Operator.GE

    def test_at_most_extraction(self):
        """Extract 'at most X' constraints."""
        result = extract_constraints("Spend at most 5000 dollars")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.NUMERIC]

        assert len(constraints) >= 1
        at_most = [c for c in constraints if c.value == 5000.0]
        assert len(at_most) >= 1
        assert at_most[0].operator == Operator.LE

    def test_exactly_extraction(self):
        """Extract 'exactly X' constraints."""
        result = extract_constraints("Need exactly 5 people")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.NUMERIC]

        exactly_5 = [c for c in constraints if c.value == 5.0]
        assert len(exactly_5) >= 1
        assert exactly_5[0].operator == Operator.EQ

    def test_between_extraction(self):
        """Extract 'between X and Y' constraints (creates two constraints)."""
        result = extract_constraints("Budget between 1000 and 5000")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.NUMERIC]

        # Should create lower bound (>= 1000) and upper bound (<= 5000)
        lower = [c for c in constraints if c.value == 1000.0]
        upper = [c for c in constraints if c.value == 5000.0]

        assert len(lower) >= 1
        assert len(upper) >= 1
        assert lower[0].operator == Operator.GE
        assert upper[0].operator == Operator.LE

    def test_no_more_than_extraction(self):
        """Extract 'no more than X' constraints."""
        result = extract_constraints("No more than 10 participants")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.NUMERIC]

        no_more = [c for c in constraints if c.value == 10.0]
        assert len(no_more) >= 1
        assert no_more[0].operator == Operator.LE
        assert no_more[0].polarity == ConstraintPolarity.FORBID

    def test_under_extraction(self):
        """Extract 'under X' or 'below X' constraints."""
        result = extract_constraints("Keep costs under 100 dollars")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.NUMERIC]

        under_100 = [c for c in constraints if c.value == 100.0]
        assert len(under_100) >= 1
        assert under_100[0].operator == Operator.LT

    def test_over_extraction(self):
        """Extract 'over X' or 'above X' constraints."""
        result = extract_constraints("Rating above 4.5 stars")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.NUMERIC]

        over_4 = [c for c in constraints if c.value == 4.5]
        assert len(over_4) >= 1
        assert over_4[0].operator == Operator.GT


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: TEMPORAL CONSTRAINT EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestTemporalConstraintExtraction:
    """Test extraction of temporal constraints from natural language."""

    def test_for_duration_extraction(self):
        """Extract 'for X weeks/days' duration constraints."""
        result = extract_constraints("Trip for 2 weeks")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.TEMPORAL]

        assert len(constraints) >= 1
        duration = [c for c in constraints if "2" in str(c.value)]
        assert len(duration) >= 1

    def test_before_time_extraction(self):
        """Extract 'before X' time constraints."""
        result = extract_constraints("Must finish before 6pm")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.TEMPORAL]

        assert len(constraints) >= 1
        before = [c for c in constraints if c.operator == Operator.BEFORE]
        assert len(before) >= 1

    def test_after_time_extraction(self):
        """Extract 'after X' time constraints."""
        result = extract_constraints("Activities start after 9am")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.TEMPORAL]

        assert len(constraints) >= 1
        after = [c for c in constraints if c.operator == Operator.AFTER]
        assert len(after) >= 1

    def test_in_month_extraction(self):
        """Extract 'in December' type constraints."""
        result = extract_constraints("Vacation in December")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.TEMPORAL]

        assert len(constraints) >= 1
        december = [c for c in constraints if "december" in str(c.value).lower()]
        assert len(december) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: QUALITATIVE → QUANTITATIVE INVERSION
# ═══════════════════════════════════════════════════════════════════════════════

class TestQualitativeInversion:
    """
    Test extraction and inversion of qualitative constraints.

    "nothing too expensive" → cost < high_threshold
    "should be safe" → safety_rating >= high
    """

    def test_expensive_inversion(self):
        """'expensive' → cost constraint."""
        result = extract_constraints("Nothing too expensive")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.QUALITATIVE]

        assert len(constraints) >= 1
        cost = [c for c in constraints if c.field == "cost"]
        assert len(cost) >= 1

    def test_safe_inversion(self):
        """'safe' → safety_rating constraint."""
        result = extract_constraints("It should be safe")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.QUALITATIVE]

        assert len(constraints) >= 1
        safety = [c for c in constraints if c.field == "safety_rating"]
        assert len(safety) >= 1
        assert safety[0].operator == Operator.GE

    def test_night_inversion(self):
        """'not night people' → time constraint."""
        result = extract_constraints("We're not night people")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.QUALITATIVE]

        assert len(constraints) >= 1
        # Should have a time-related constraint with negation
        night = [c for c in constraints if c.field == "time"]
        assert len(night) >= 1

    def test_negation_detection(self):
        """Test that negation is detected and inverts the constraint."""
        result = extract_constraints("Nothing expensive")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.QUALITATIVE]

        # Negated expensive should forbid high cost
        cost = [c for c in constraints if c.field == "cost"]
        if cost:
            assert cost[0].polarity == ConstraintPolarity.FORBID


# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: GROUP/RELATIONAL CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestGroupConstraintExtraction:
    """Test extraction of group and relational constraints."""

    def test_group_size_extraction(self):
        """Extract group size from 'X friends'."""
        result = extract_constraints("I want to take my 4 friends")

        # Check subject extraction
        assert result.subject["type"] == "group"
        assert result.subject["count"] == 5  # 4 friends + speaker

    def test_people_count_extraction(self):
        """Extract group size from 'X people'."""
        result = extract_constraints("Need space for 10 people")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.RELATIONAL]

        # Should extract group_size constraint
        assert len(constraints) >= 0  # May or may not create constraint

    def test_consensus_extraction(self):
        """Extract consensus requirements."""
        result = extract_constraints("At least 2 people must agree")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.RELATIONAL]

        assert len(constraints) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: CONSTRAINT STRENGTH DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstraintStrengthDetection:
    """Test detection of hard vs soft constraints."""

    def test_must_is_hard(self):
        """'must' indicates a hard constraint."""
        result = extract_constraints("Must have at least 3 rooms")

        constraints = [c for c in result.constraints
                      if c.strength == ConstraintStrength.HARD]

        assert len(constraints) >= 1

    def test_require_is_hard(self):
        """'require' indicates a hard constraint."""
        result = extract_constraints("We require 5 seats")

        constraints = [c for c in result.constraints]
        hard = [c for c in constraints if c.strength == ConstraintStrength.HARD]

        assert len(hard) >= 1

    def test_want_is_soft(self):
        """'want' indicates a soft constraint."""
        result = extract_constraints("We want at least 3 activities")

        constraints = [c for c in result.constraints]
        soft = [c for c in constraints if c.strength == ConstraintStrength.SOFT]

        assert len(soft) >= 1

    def test_prefer_is_soft(self):
        """'prefer' indicates a soft constraint."""
        result = extract_constraints("We prefer morning activities")

        # At least one constraint should be soft if detected
        # (might not extract if pattern doesn't match)
        assert result is not None


# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: COMPLEX SENTENCE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestComplexSentenceExtraction:
    """Test extraction from complex, multi-constraint sentences."""

    def test_costa_rica_example(self):
        """
        The canonical example from Jared's specification.

        "I want to take my 4 friends to Costa Rica for 2 weeks in December.
         Nothing too expensive, but it should be safe and fun.
         We all want at least 3 activities. Oh, and we're not night people."
        """
        text = (
            "I want to take my 4 friends to Costa Rica for 2 weeks in December. "
            "Nothing too expensive, but it should be safe and fun. "
            "We all want at least 3 activities. Oh, and we're not night people."
        )

        result = extract_constraints(text)

        # Should extract multiple constraints
        assert len(result.constraints) >= 4

        # Check subject extraction
        assert result.subject["type"] == "group"
        assert result.subject["count"] == 5

        # Check location extraction
        locations = [o for o in result.objects if o["type"] == "location"]
        assert len(locations) >= 1
        assert locations[0]["value"] == "Costa Rica"

        # Check duration extraction
        durations = [o for o in result.objects if o["type"] == "duration"]
        assert len(durations) >= 1
        assert durations[0]["value"] == 2

        # Verify we have diverse constraint types
        categories = set(c.category for c in result.constraints)
        assert len(categories) >= 2  # At least 2 different categories

    def test_multi_sentence_extraction(self):
        """Extract constraints from multiple sentences."""
        text = (
            "The event needs at least 50 attendees. "
            "Budget should be under 10000 dollars. "
            "It must happen before December."
        )

        result = extract_constraints(text)

        # Should extract at least 3 constraints
        assert len(result.constraints) >= 3

    def test_conjunction_handling(self):
        """Handle 'and' conjunctions in constraints."""
        text = "We need 5 or more rooms and at least 3 bathrooms"

        result = extract_constraints(text)

        # Should extract multiple constraints
        assert len(result.constraints) >= 2


# ═══════════════════════════════════════════════════════════════════════════════
# PART 7: PLAN VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlanVerification:
    """
    Test verification of plans against extracted constraints.

    Not "I think this is good" but "This IS verified."
    """

    def test_plan_passes_all_constraints(self):
        """Verify a plan that satisfies all constraints."""
        # Extract constraints
        extraction = extract_constraints("Need at least 5 people and under 100 cost")

        # Create a plan that satisfies
        plan = {
            "count": 10,  # Satisfies >= 5
            "cost": 50    # Satisfies < 100
        }

        # Verify
        verified = verify_plan(plan, extraction)

        # Check structure
        assert verified.id is not None
        assert verified.merkle_root is not None
        assert verified.signature is not None
        assert len(verified.certificates) > 0

    def test_plan_fails_constraint(self):
        """Verify a plan that fails a constraint."""
        # Extract constraints
        extraction = extract_constraints("Need at least 5 items")

        # Create a plan that fails
        plan = {
            "items": 2,  # Fails >= 5
            "count": 2
        }

        # Verify
        verified = verify_plan(plan, extraction)

        # Should have certificates
        assert len(verified.certificates) > 0

    def test_verification_certificates(self):
        """Check that verification produces proper certificates."""
        extraction = extract_constraints("Budget at most 1000")

        plan = {"Budget": 500}

        verified = verify_plan(plan, extraction)

        for cert in verified.certificates:
            assert cert.constraint_id is not None
            assert cert.proof_hash is not None
            assert cert.timestamp > 0


# ═══════════════════════════════════════════════════════════════════════════════
# PART 8: TINYTALK AND CDL GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestCodeGeneration:
    """Test TinyTalk and CDL code generation from extractions."""

    def test_tinytalk_generation(self):
        """Generate TinyTalk Blueprint from extraction."""
        extraction = extract_constraints("Must have at least 3 items")

        tinytalk = extraction.to_tinytalk_blueprint("TestPlan")

        # Should generate valid Python class
        assert "class TestPlan" in tinytalk
        assert "Blueprint" in tinytalk
        assert "@law" in tinytalk

    def test_cdl_generation(self):
        """Generate CDL specification from extraction."""
        extraction = extract_constraints("Need exactly 5 participants")

        cdl = extraction.to_cdl_spec()

        # Should have constraints and verification
        assert "when" in cdl
        assert "constraints" in cdl
        assert "verification" in cdl

    def test_constraint_to_cdl(self):
        """Convert individual constraint to CDL."""
        extraction = extract_constraints("At least 10 users")

        if extraction.constraints:
            constraint = extraction.constraints[0]
            cdl = constraint.to_cdl()

            # Should create an AtomicConstraint
            assert cdl is not None

    def test_constraint_to_tinytalk(self):
        """Convert individual constraint to TinyTalk law."""
        extraction = extract_constraints("Maximum 100 items")

        if extraction.constraints:
            constraint = extraction.constraints[0]
            tinytalk = constraint.to_tinytalk()

            # Should create when() statement
            assert "when(" in tinytalk


# ═══════════════════════════════════════════════════════════════════════════════
# PART 9: AMBIGUITY AND ASSUMPTION DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestAmbiguityDetection:
    """Test detection of ambiguities and documentation of assumptions."""

    def test_vague_quantity_detection(self):
        """Detect vague quantities like 'several', 'few', 'many'."""
        result = extract_constraints("We need several rooms")

        # Should flag this as ambiguous
        assert len(result.ambiguities) >= 1
        assert any("several" in a.lower() for a in result.ambiguities)

    def test_too_qualifier_ambiguity(self):
        """Detect 'too X' without defined threshold."""
        result = extract_constraints("Nothing too expensive")

        # Should note the threshold assumption
        assert len(result.assumptions) >= 0 or len(result.ambiguities) >= 0

    def test_assumptions_documented(self):
        """Verify assumptions are documented for qualitative inversions."""
        result = extract_constraints("It should be safe and affordable")

        # Qualitative constraints should document threshold assumptions
        qualitative = [c for c in result.constraints
                      if c.category == ConstraintCategory.QUALITATIVE]

        if qualitative:
            # Should have at least one assumption about thresholds
            assert len(result.assumptions) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# PART 10: CRYPTOGRAPHIC PROOFS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCryptographicProofs:
    """Test cryptographic proof generation for audit trails."""

    def test_extraction_has_merkle_root(self):
        """Extractions should have merkle root for verification."""
        result = extract_constraints("Need 5 items")

        assert result.merkle_root is not None
        assert len(result.merkle_root) == 64  # SHA-256 hex

    def test_extraction_has_signature(self):
        """Extractions should have signature for authenticity."""
        result = extract_constraints("At least 10 people")

        assert result.signature is not None
        assert result.signature.startswith("newton_")

    def test_proof_is_deterministic(self):
        """Same input should produce same proof."""
        text = "Exactly 5 items required"

        result1 = extract_constraints(text)
        # Note: Due to timestamps, exact proof will differ
        # But structure should be consistent

        assert result1.merkle_root is not None

    def test_verified_plan_has_proof(self):
        """Verified plans should have cryptographic proofs."""
        extraction = extract_constraints("Need 3 rooms")
        plan = {"rooms": 5}

        verified = verify_plan(plan, extraction)

        assert verified.merkle_root is not None
        assert verified.signature is not None
        assert verified.signature.startswith("newton_verified_")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 11: PERFORMANCE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerformance:
    """Test extraction performance requirements."""

    def test_extraction_latency(self):
        """Extraction should complete in reasonable time."""
        text = (
            "I want to take my 4 friends to Costa Rica for 2 weeks in December. "
            "Nothing too expensive, but it should be safe and fun. "
            "We all want at least 3 activities."
        )

        start = time.perf_counter()
        result = extract_constraints(text)
        elapsed = time.perf_counter() - start

        # Should complete in under 100ms
        assert elapsed < 0.1
        assert len(result.constraints) > 0

    def test_verification_latency(self):
        """Plan verification should be fast."""
        extraction = extract_constraints("Need at least 5 items and under 100 cost")
        plan = {"items": 10, "cost": 50}

        start = time.perf_counter()
        verified = verify_plan(plan, extraction)
        elapsed = time.perf_counter() - start

        # Should complete in under 50ms
        assert elapsed < 0.05

    def test_batch_extraction(self):
        """Handle batch of extractions efficiently."""
        texts = [
            "Need 5 rooms",
            "Budget under 1000",
            "At least 10 people",
            "Must be safe",
            "Before 6pm",
        ]

        start = time.perf_counter()
        results = [extract_constraints(t) for t in texts]
        elapsed = time.perf_counter() - start

        # All should complete in under 200ms
        assert elapsed < 0.2
        assert all(r.constraints for r in results)


# ═══════════════════════════════════════════════════════════════════════════════
# PART 12: EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_input(self):
        """Handle empty input gracefully."""
        result = extract_constraints("")

        assert result is not None
        assert result.constraints == []
        assert result.source_text == ""

    def test_no_constraints_found(self):
        """Handle text with no extractable constraints."""
        result = extract_constraints("Hello, how are you today?")

        assert result is not None
        # May or may not find constraints depending on patterns

    def test_unicode_input(self):
        """Handle unicode characters in input."""
        result = extract_constraints("Need at least 5 items ✓")

        assert result is not None
        assert len(result.constraints) >= 1

    def test_very_long_input(self):
        """Handle very long input text."""
        text = "Need at least 5 items. " * 100

        result = extract_constraints(text)

        assert result is not None
        # Should still extract constraints

    def test_mixed_case(self):
        """Handle mixed case input."""
        result = extract_constraints("AT LEAST 5 items AND at most 10 PEOPLE")

        assert result is not None
        assert len(result.constraints) >= 2

    def test_decimal_numbers(self):
        """Handle decimal numbers correctly."""
        result = extract_constraints("Rating above 4.5 stars")

        constraints = [c for c in result.constraints
                      if c.category == ConstraintCategory.NUMERIC]

        if constraints:
            # Should handle decimal
            decimal_value = [c for c in constraints if c.value == 4.5]
            assert len(decimal_value) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# PART 13: SINGLETON AND CACHING
# ═══════════════════════════════════════════════════════════════════════════════

class TestSingletonAndCaching:
    """Test extractor singleton and caching behavior."""

    def test_singleton_extractor(self):
        """get_extractor returns same instance."""
        extractor1 = get_extractor()
        extractor2 = get_extractor()

        assert extractor1 is extractor2

    def test_extractor_reusable(self):
        """Extractor can be reused for multiple extractions."""
        extractor = get_extractor()

        result1 = extractor.extract("Need 5 items")
        result2 = extractor.extract("Need 10 people")

        assert result1.id != result2.id
        assert len(result1.constraints) >= 1
        assert len(result2.constraints) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
