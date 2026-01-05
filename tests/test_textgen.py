#!/usr/bin/env python3
"""
===========================================================================
NEWTON TEXT GENERATION TESTS
Test suite for the constraint-preserving text projection module.

This suite verifies:
1. Expand . Reduce = Identity (bijective text generation)
2. No hallucination by construction
3. Multiple style support (formal, technical, educational, minimal)
4. CDL integration
5. Document generation
6. Ledger fingerprinting

===========================================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from typing import List

from core.textgen import (
    TextStyle,
    TextConstraint,
    ProjectionResult,
    TextDocument,
    NewtonTextProjector,
    project,
    project_cdl,
    explain_constraints,
    generate_document,
    text_fingerprint,
    reduce_text,
    register_reduction,
    create_text_ledger_entry,
    TEMPLATES,
)


# ===========================================================================
# TEST FIXTURES
# ===========================================================================

@pytest.fixture
def projector_formal():
    """Provide a formal style projector."""
    return NewtonTextProjector(style="formal")


@pytest.fixture
def projector_technical():
    """Provide a technical style projector."""
    return NewtonTextProjector(style="technical")


@pytest.fixture
def projector_educational():
    """Provide an educational style projector."""
    return NewtonTextProjector(style="educational")


@pytest.fixture
def sample_constraints():
    """Provide sample constraints for testing."""
    return [
        TextConstraint("balance", "ge", 0),
        TextConstraint("withdrawal", "le", "balance"),
        TextConstraint("amount", "lt", 1000),
        TextConstraint("count", "gt", 5),
        TextConstraint("status", "eq", "active"),
    ]


@pytest.fixture
def ratio_constraints():
    """Provide ratio constraints for testing."""
    return [
        TextConstraint("debt", "ratio_le", 3.0, denominator="equity"),
        TextConstraint("liabilities", "ratio_lt", 1.0, denominator="assets"),
    ]


# ===========================================================================
# CORE FUNCTIONALITY TESTS
# ===========================================================================

class TestTextConstraint:
    """Tests for TextConstraint class."""

    def test_canonical_representation(self):
        """Test canonical string representation."""
        c = TextConstraint("balance", "ge", 0)
        assert c.canonical() == "balance ge 0"

    def test_canonical_with_denominator(self):
        """Test canonical representation for ratio constraints."""
        c = TextConstraint("debt", "ratio_le", 3.0, denominator="equity")
        assert c.canonical() == "debt/equity ratio_le 3.0"

    def test_equality(self):
        """Test constraint equality."""
        c1 = TextConstraint("balance", "ge", 0)
        c2 = TextConstraint("balance", "ge", 0)
        c3 = TextConstraint("balance", "le", 0)

        assert c1 == c2
        assert c1 != c3

    def test_hashing(self):
        """Test constraint hashing for set operations."""
        c1 = TextConstraint("balance", "ge", 0)
        c2 = TextConstraint("balance", "ge", 0)

        constraint_set = {c1, c2}
        assert len(constraint_set) == 1


# ===========================================================================
# EXPANSION TESTS
# ===========================================================================

class TestExpansion:
    """Tests for constraint expansion to text."""

    def test_expand_ge_formal(self, projector_formal):
        """Test expansion of 'greater than or equal' in formal style."""
        constraints = [TextConstraint("balance", "ge", 0)]
        candidates = projector_formal.expand(constraints)

        assert len(candidates) > 0
        texts = [t for t, c in candidates]
        assert any("greater than or equal" in t for t in texts)

    def test_expand_le_formal(self, projector_formal):
        """Test expansion of 'less than or equal' in formal style."""
        constraints = [TextConstraint("amount", "le", 1000)]
        candidates = projector_formal.expand(constraints)

        assert len(candidates) > 0
        texts = [t for t, c in candidates]
        assert any("less than or equal" in t or "exceed" in t for t in texts)

    def test_expand_ratio_formal(self, projector_formal):
        """Test expansion of ratio constraints in formal style."""
        constraints = [TextConstraint("debt", "ratio_le", 3.0, denominator="equity")]
        candidates = projector_formal.expand(constraints)

        assert len(candidates) > 0
        texts = [t for t, c in candidates]
        assert any("ratio" in t.lower() or "/" in t for t in texts)

    def test_expand_technical_style(self, projector_technical):
        """Test expansion in technical style."""
        constraints = [TextConstraint("balance", "ge", 0)]
        candidates = projector_technical.expand(constraints)

        assert len(candidates) > 0
        texts = [t for t, c in candidates]
        assert any(">=" in t for t in texts)

    def test_expand_educational_style(self, projector_educational):
        """Test expansion in educational style."""
        constraints = [TextConstraint("balance", "ge", 0)]
        candidates = projector_educational.expand(constraints)

        assert len(candidates) > 0
        texts = [t for t, c in candidates]
        assert any("at least" in t.lower() or "needs" in t.lower() for t in texts)


# ===========================================================================
# REDUCTION TESTS
# ===========================================================================

class TestReduction:
    """Tests for text reduction to constraints."""

    def test_reduce_ge(self):
        """Test reduction of 'greater than or equal' text."""
        text = "balance must be greater than or equal to 0."
        constraints = reduce_text(text)

        assert len(constraints) > 0
        assert any(c.op == "ge" and c.field == "balance" for c in constraints)

    def test_reduce_le(self):
        """Test reduction of 'less than or equal' text."""
        text = "amount must be less than or equal to 1000."
        constraints = reduce_text(text)

        assert len(constraints) > 0
        assert any(c.op == "le" and c.field == "amount" for c in constraints)

    def test_reduce_technical_style(self):
        """Test reduction of technical style text."""
        text = "balance >= 100"
        constraints = reduce_text(text)

        assert len(constraints) > 0
        assert any(c.op == "ge" for c in constraints)

    def test_reduce_ratio(self):
        """Test reduction of ratio constraint text."""
        text = "The ratio of debt to equity must not exceed 3.0."
        constraints = reduce_text(text)

        assert len(constraints) > 0
        assert any(c.op == "ratio_le" and c.denominator == "equity" for c in constraints)


# ===========================================================================
# BIJECTION TESTS (Expand . Reduce = Identity)
# ===========================================================================

class TestBijection:
    """Tests for the expand . reduce = identity property."""

    def test_bijection_ge(self, projector_formal):
        """Test bijection for 'greater than or equal' constraints."""
        original = TextConstraint("balance", "ge", 0)
        results = projector_formal.generate([original], verify=True)

        assert len(results) > 0
        for r in results:
            assert r.verified is True

    def test_bijection_le(self, projector_formal):
        """Test bijection for 'less than or equal' constraints."""
        original = TextConstraint("amount", "le", 1000)
        results = projector_formal.generate([original], verify=True)

        assert len(results) > 0
        for r in results:
            assert r.verified is True

    def test_bijection_eq(self, projector_formal):
        """Test bijection for 'equals' constraints."""
        original = TextConstraint("status", "eq", "active")
        results = projector_formal.generate([original], verify=True)

        assert len(results) > 0
        for r in results:
            assert r.verified is True

    def test_verified_expansion_rejects_invalid(self, projector_formal):
        """Test that verify_expansion rejects text that doesn't reduce correctly."""
        original = TextConstraint("balance", "ge", 100)

        # This text doesn't match the original constraint
        invalid_text = "something completely unrelated"
        verified = projector_formal.verify_expansion(original, invalid_text)

        assert verified is False

    def test_no_hallucination(self, projector_formal, sample_constraints):
        """Test that all generated text can be reduced back to original."""
        for constraint in sample_constraints:
            results = projector_formal.generate([constraint], verify=True)

            # All results should be verified
            for r in results:
                assert r.verified is True

                # Double-check: reduce the text and verify it matches
                reduced = reduce_text(r.text)
                assert any(rc.canonical() == constraint.canonical() for rc in reduced)


# ===========================================================================
# PROJECTION RESULT TESTS
# ===========================================================================

class TestProjectionResult:
    """Tests for ProjectionResult class."""

    def test_fingerprint_generation(self, projector_formal):
        """Test that fingerprints are generated."""
        constraints = [TextConstraint("balance", "ge", 0)]
        results = projector_formal.generate(constraints)

        assert len(results) > 0
        for r in results:
            assert r.fingerprint is not None
            assert len(r.fingerprint) == 16  # SHA-256 truncated to 16 chars

    def test_to_dict(self, projector_formal):
        """Test dictionary serialization."""
        constraints = [TextConstraint("balance", "ge", 0)]
        results = projector_formal.generate(constraints)

        assert len(results) > 0
        d = results[0].to_dict()

        assert "text" in d
        assert "constraint" in d
        assert "fingerprint" in d
        assert "verified" in d
        assert "style" in d
        assert "timestamp" in d

    def test_fingerprint_uniqueness(self, projector_formal):
        """Test that different texts have different fingerprints."""
        c1 = TextConstraint("balance", "ge", 0)
        c2 = TextConstraint("amount", "le", 1000)

        r1 = projector_formal.generate([c1])[0]
        r2 = projector_formal.generate([c2])[0]

        assert r1.fingerprint != r2.fingerprint


# ===========================================================================
# CONVENIENCE FUNCTION TESTS
# ===========================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_project_one_liner(self):
        """Test one-liner projection."""
        text = project("balance", "ge", 0)

        assert text is not None
        assert "balance" in text.lower()

    def test_project_ratio(self):
        """Test ratio projection."""
        text = project("debt", "ratio_le", 3.0, denominator="equity")

        assert text is not None
        assert "debt" in text.lower() or "ratio" in text.lower()

    def test_explain_constraints(self):
        """Test educational explanation generation."""
        constraints = [
            TextConstraint("balance", "ge", 0),
            TextConstraint("withdrawal", "le", "balance"),
        ]
        explanations = explain_constraints(constraints)

        assert len(explanations) > 0


# ===========================================================================
# DOCUMENT GENERATION TESTS
# ===========================================================================

class TestDocumentGeneration:
    """Tests for document generation."""

    def test_generate_document(self):
        """Test document generation from constraints."""
        constraints = [
            TextConstraint("balance", "ge", 0),
            TextConstraint("withdrawal", "le", "balance"),
        ]
        doc = generate_document("Account Rules", constraints)

        assert isinstance(doc, TextDocument)
        assert doc.title == "Account Rules"
        assert len(doc.sections) > 0
        assert doc.fingerprint is not None

    def test_document_to_markdown(self):
        """Test markdown export."""
        constraints = [TextConstraint("balance", "ge", 0)]
        doc = generate_document("Test Rules", constraints)

        markdown = doc.to_markdown()

        assert "# Test Rules" in markdown
        assert doc.fingerprint in markdown

    def test_document_to_dict(self):
        """Test dictionary export."""
        constraints = [TextConstraint("balance", "ge", 0)]
        doc = generate_document("Test Rules", constraints)

        d = doc.to_dict()

        assert "title" in d
        assert "sections" in d
        assert "fingerprint" in d
        assert "timestamp" in d


# ===========================================================================
# FINGERPRINT TESTS
# ===========================================================================

class TestFingerprinting:
    """Tests for text fingerprinting."""

    def test_fingerprint_consistency(self):
        """Test that same text always produces same fingerprint."""
        text = "This is a test sentence."
        fp1 = text_fingerprint(text)
        fp2 = text_fingerprint(text)

        assert fp1 == fp2

    def test_fingerprint_format(self):
        """Test fingerprint format (16 uppercase hex chars)."""
        text = "Test text"
        fp = text_fingerprint(text)

        assert len(fp) == 16
        assert fp.isupper()
        assert all(c in "0123456789ABCDEF" for c in fp)

    def test_fingerprint_different_texts(self):
        """Test that different texts produce different fingerprints."""
        fp1 = text_fingerprint("Text one")
        fp2 = text_fingerprint("Text two")

        assert fp1 != fp2


# ===========================================================================
# LEDGER INTEGRATION TESTS
# ===========================================================================

class TestLedgerIntegration:
    """Tests for ledger integration."""

    def test_create_ledger_entry(self, projector_formal):
        """Test creating a ledger entry from projection result."""
        constraints = [TextConstraint("balance", "ge", 0)]
        results = projector_formal.generate(constraints)

        assert len(results) > 0
        entry = create_text_ledger_entry(results[0])

        assert entry["operation"] == "textgen"
        assert entry["result"] == "pass"
        assert "metadata" in entry
        assert "constraint" in entry["metadata"]

    def test_ledger_entry_unverified(self, projector_formal):
        """Test ledger entry for unverified projection."""
        constraints = [TextConstraint("balance", "ge", 0)]
        results = projector_formal.generate(constraints, verify=False)

        assert len(results) > 0
        entry = create_text_ledger_entry(results[0])

        assert entry["result"] == "unverified"


# ===========================================================================
# STYLE TESTS
# ===========================================================================

class TestStyles:
    """Tests for different text styles."""

    def test_all_styles_have_ge_template(self):
        """Test that all styles have 'ge' templates."""
        for style in ["formal", "technical", "educational", "minimal"]:
            assert "ge" in TEMPLATES[style]

    def test_all_styles_have_le_template(self):
        """Test that all styles have 'le' templates."""
        for style in ["formal", "technical", "educational", "minimal"]:
            assert "le" in TEMPLATES[style]

    def test_all_styles_have_ratio_templates(self):
        """Test that all styles have ratio templates."""
        for style in ["formal", "technical", "educational", "minimal"]:
            assert "ratio_le" in TEMPLATES[style]
            assert "ratio_lt" in TEMPLATES[style]

    def test_minimal_style_is_terse(self):
        """Test that minimal style produces short output."""
        projector = NewtonTextProjector(style="minimal")
        constraints = [TextConstraint("balance", "ge", 0)]
        results = projector.generate(constraints)

        assert len(results) > 0
        # Minimal style should be very short
        for r in results:
            assert len(r.text) < 30


# ===========================================================================
# STATISTICS TESTS
# ===========================================================================

class TestStatistics:
    """Tests for projector statistics."""

    def test_stats_tracking(self, projector_formal):
        """Test that statistics are tracked."""
        constraints = [TextConstraint("balance", "ge", 0)]
        projector_formal.generate(constraints)

        stats = projector_formal.stats

        assert "projections" in stats
        assert "rejections" in stats
        assert "acceptance_rate" in stats
        assert stats["projections"] > 0


# ===========================================================================
# EDGE CASE TESTS
# ===========================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_constraint_list(self, projector_formal):
        """Test handling of empty constraint list."""
        results = projector_formal.generate([])
        assert results == []

    def test_unknown_operator(self, projector_formal):
        """Test handling of unknown operator."""
        constraints = [TextConstraint("field", "unknown_op", "value")]
        results = projector_formal.generate(constraints, verify=False)

        # Should produce empty results (no matching template)
        assert len(results) == 0

    def test_special_characters_in_field(self, projector_formal):
        """Test handling of special characters in field names."""
        constraints = [TextConstraint("user_balance", "ge", 0)]
        results = projector_formal.generate(constraints, verify=False)

        assert len(results) > 0
        for r in results:
            assert "user_balance" in r.text


# ===========================================================================
# CUSTOM REDUCTION RULE TESTS
# ===========================================================================

class TestCustomReduction:
    """Tests for custom reduction rules."""

    def test_register_custom_reduction(self):
        """Test registering a custom reduction rule."""
        # Register a custom reduction
        @register_reduction
        def reduce_custom(text):
            if "CUSTOM_PATTERN" in text:
                return TextConstraint("custom_field", "eq", "custom_value")
            return None

        # Test it works
        constraints = reduce_text("This has CUSTOM_PATTERN in it")
        assert any(c.field == "custom_field" for c in constraints)


# ===========================================================================
# CLI TEST
# ===========================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
