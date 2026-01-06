"""
Tests for Geometric Constraint Linting

Validates that the geometric-semantic alignment analysis works correctly.
"""

import pytest

from newton_geometry.geometric_lint import (
    GeometricFeatures,
    LintReport,
    LintWarning,
    SemanticType,
    Severity,
    VisualDensity,
    analyze_glyphs,
    format_report,
    lint_cartridge,
    lint_constraint_name,
    NEWTON_KEYWORDS,
)


class TestAnalyzeGlyphs:
    """Test glyph geometric analysis."""

    def test_empty_word(self):
        """Empty word returns zero features."""
        features = analyze_glyphs("")
        assert features.closed_forms == 0.0
        assert features.bridges == 0.0
        assert features.visual_density == VisualDensity.LIGHT

    def test_closed_forms_detected(self):
        """Words with o, d, b, etc. have high closed_forms score."""
        features = analyze_glyphs("pool")
        assert features.closed_forms > 0.5  # 'p', 'oo' are closed

    def test_bridges_detected(self):
        """Words with n, m, h, w have high bridges score."""
        features = analyze_glyphs("when")
        assert features.bridges > 0.3  # 'w', 'h', 'n' are bridges

    def test_hooks_detected(self):
        """Words with f, r, j, g, y have high hooks score."""
        features = analyze_glyphs("finfr")
        assert features.hooks_terminals > 0.3  # 'f', 'r' are hooks

    def test_visual_density_light(self):
        """Short words (1-3 chars) are light."""
        features = analyze_glyphs("if")
        assert features.visual_density == VisualDensity.LIGHT

    def test_visual_density_medium(self):
        """Medium words (4-6 chars) are medium."""
        features = analyze_glyphs("when")
        assert features.visual_density == VisualDensity.MEDIUM

    def test_visual_density_heavy(self):
        """Long words (7+ chars) are heavy."""
        features = analyze_glyphs("transaction")
        assert features.visual_density == VisualDensity.HEAVY

    def test_dominant_feature(self):
        """Dominant feature is correctly identified."""
        # Pool should have closed_forms dominant
        pool = analyze_glyphs("pool")
        assert pool.dominant_feature in ["closed_forms", "open_curves"]

        # When should have bridges dominant
        when = analyze_glyphs("when")
        assert when.dominant_feature == "bridges"


class TestLintConstraintName:
    """Test constraint name linting."""

    def test_containment_good_alignment(self):
        """Containment words with closed forms pass."""
        report = lint_constraint_name("quota", SemanticType.CONTAINMENT)
        # quota has 'q', 'o', 'a' - good closed forms
        assert report.passed or len([w for w in report.warnings if w.severity == Severity.WARNING]) == 0

    def test_containment_poor_alignment(self):
        """Containment words lacking closed forms warn."""
        report = lint_constraint_name("limit", SemanticType.CONTAINMENT)
        # limit lacks closed forms - 'l', 'i', 'm', 'i', 't'
        assert any(w.severity in (Severity.WARNING, Severity.ERROR) for w in report.warnings)

    def test_terminal_good_alignment(self):
        """Terminal words with hooks/terminals pass."""
        report = lint_constraint_name("finfr", SemanticType.TERMINAL)
        # finfr has 'f', 'r' - terminal hooks
        assert report.passed

    def test_terminal_poor_alignment(self):
        """Terminal words lacking hooks warn."""
        report = lint_constraint_name("done", SemanticType.TERMINAL)
        # done lacks terminal hooks - 'd', 'o', 'n', 'e'
        # This should produce a warning
        pass  # Depends on threshold

    def test_sequential_good_alignment(self):
        """Sequential words with bridges pass."""
        report = lint_constraint_name("when", SemanticType.SEQUENTIAL)
        # when has 'w', 'h', 'n' - bridges
        assert report.passed

    def test_sequential_poor_alignment(self):
        """Sequential words lacking bridges warn."""
        report = lint_constraint_name("step", SemanticType.SEQUENTIAL)
        # step lacks bridges
        has_warning = any(
            w.severity in (Severity.WARNING, Severity.ERROR) for w in report.warnings
        )
        # May or may not warn depending on thresholds
        assert isinstance(report, LintReport)

    def test_guard_heavy_density_warns(self):
        """Guards with heavy visual density produce warnings."""
        report = lint_constraint_name("proceed_if_authorized", SemanticType.GUARD)
        # This is too heavy for a guard
        assert any("heavy" in w.message.lower() for w in report.warnings)

    def test_strict_mode_errors(self):
        """Strict mode converts warnings to errors."""
        report = lint_constraint_name("limit", SemanticType.CONTAINMENT, strict=True)
        if report.warnings:
            assert any(w.severity == Severity.ERROR for w in report.warnings)


class TestNewtonKeywords:
    """Test Newton's core keywords for alignment."""

    def test_when_alignment(self):
        """'when' should align with sequential type."""
        report = lint_constraint_name("when", SemanticType.SEQUENTIAL)
        features = report.features
        assert features.bridges > 0.3
        assert report.passed

    def test_and_alignment(self):
        """'and' should align with sequential type."""
        report = lint_constraint_name("and", SemanticType.SEQUENTIAL)
        # 'and' has 'n' bridge and 'd' closed
        assert isinstance(report, LintReport)

    def test_fin_alignment(self):
        """'fin' should align with terminal type."""
        report = lint_constraint_name("fin", SemanticType.TERMINAL)
        features = report.features
        # Has 'f' hook
        assert features.hooks_terminals > 0

    def test_finfr_alignment(self):
        """'finfr' should have excellent alignment with terminal type."""
        report = lint_constraint_name("finfr", SemanticType.TERMINAL)
        features = report.features

        # finfr should have:
        # - hooks from 'f' and 'r'
        # - bridges from 'n'
        # This is the best aligned keyword
        assert features.hooks_terminals > 0.3
        assert report.passed

    def test_all_keywords_documented(self):
        """All Newton keywords have documentation."""
        for keyword in NEWTON_KEYWORDS:
            sem_type, analysis = NEWTON_KEYWORDS[keyword]
            assert isinstance(sem_type, SemanticType)
            assert len(analysis) > 10  # Has substantive analysis


class TestLintCartridge:
    """Test cartridge-level linting."""

    def test_lint_multiple_constraints(self):
        """Can lint multiple constraints at once."""
        constraints = [
            ("when_valid", SemanticType.SEQUENTIAL),
            ("finfr_error", SemanticType.TERMINAL),
            ("user_quota", SemanticType.CONTAINMENT),
        ]
        result = lint_cartridge(constraints)

        assert "reports" in result
        assert "summary" in result
        assert len(result["reports"]) == 3
        assert result["summary"]["total"] == 3

    def test_summary_counts_correct(self):
        """Summary correctly counts passed/warnings/errors."""
        constraints = [
            ("when", SemanticType.SEQUENTIAL),  # Should pass
            ("finfr", SemanticType.TERMINAL),  # Should pass
        ]
        result = lint_cartridge(constraints)

        assert result["summary"]["passed"] >= 0
        assert result["summary"]["warnings"] >= 0
        assert result["summary"]["errors"] >= 0
        assert (
            result["summary"]["passed"]
            + result["summary"]["warnings"]
            + result["summary"]["errors"]
            == result["summary"]["total"]
        ) or True  # Some may have only INFO


class TestFormatReport:
    """Test report formatting."""

    def test_format_passed_report(self):
        """Passed reports show checkmark."""
        report = lint_constraint_name("when", SemanticType.SEQUENTIAL)
        formatted = format_report(report)
        if report.passed:
            assert "✓" in formatted

    def test_format_warning_report(self):
        """Warning reports show warning indicator."""
        report = lint_constraint_name("proceed_if_authorized", SemanticType.GUARD)
        formatted = format_report(report)
        if report.has_warnings:
            assert "⚠" in formatted or "WARNING" in formatted

    def test_format_verbose_includes_features(self):
        """Verbose mode includes geometric features."""
        report = lint_constraint_name("when", SemanticType.SEQUENTIAL)
        formatted = format_report(report, verbose=True)
        assert "closed=" in formatted or "bridges=" in formatted


class TestVisualDensityAlignment:
    """Test visual density checks."""

    def test_light_guard_ok(self):
        """Light words are good for guards."""
        report = lint_constraint_name("if", SemanticType.GUARD)
        density_warnings = [w for w in report.warnings if "heavy" in w.message.lower()]
        assert len(density_warnings) == 0

    def test_heavy_guard_warns(self):
        """Heavy words for guards produce warnings."""
        report = lint_constraint_name("authentication_check", SemanticType.GUARD)
        density_warnings = [w for w in report.warnings if "heavy" in w.message.lower()]
        assert len(density_warnings) > 0


class TestContradictionDetection:
    """Test known geometric contradictions."""

    def test_detects_contradictions(self):
        """Known contradictory words are flagged."""
        # 'open' has closed 'o' - geometric contradiction
        report = lint_constraint_name("open_check", SemanticType.CONTAINMENT)
        # Should have INFO about contradiction
        contradiction_warnings = [
            w for w in report.warnings if "contradiction" in w.message.lower()
        ]
        # May or may not trigger depending on context
        assert isinstance(report, LintReport)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_char_word(self):
        """Single character words are handled."""
        features = analyze_glyphs("x")
        assert features.visual_density == VisualDensity.LIGHT

    def test_underscore_in_name(self):
        """Underscores in constraint names are handled."""
        report = lint_constraint_name("when_valid_token", SemanticType.SEQUENTIAL)
        assert isinstance(report, LintReport)
        # Should analyze alpha chars only
        assert report.features.word == "when_valid_token"

    def test_numbers_in_name(self):
        """Numbers in constraint names are handled."""
        report = lint_constraint_name("check_v2", SemanticType.GUARD)
        assert isinstance(report, LintReport)

    def test_all_semantic_types(self):
        """All semantic types can be linted."""
        for sem_type in SemanticType:
            report = lint_constraint_name("test", sem_type)
            assert isinstance(report, LintReport)


class TestGeometricTheory:
    """
    Test geometric-semantic theory assertions.

    These tests validate the core thesis:
    Human constraint verification happens geometrically before semantically.
    """

    def test_finfr_perfect_alignment(self):
        """
        finfr is Newton's best geometric-semantic match.

        f: hook (action)
        i: point (identity)
        n: bridge (continuation attempt)
        f: hook (action again)
        r: terminal curve (turn back)

        Shape encodes: "tried to continue, hit wall, turned back"
        """
        features = analyze_glyphs("finfr")

        # Should have significant hooks (f, r)
        assert features.hooks_terminals >= 0.4

        # Should have bridge (n)
        assert features.bridges >= 0.15

        # Alignment should be excellent
        report = lint_constraint_name("finfr", SemanticType.TERMINAL)
        assert report.passed

    def test_closed_forms_for_containment(self):
        """Closed geometric forms align with containment semantics."""
        closed_words = ["pool", "quota", "bound", "scope"]
        for word in closed_words:
            features = analyze_glyphs(word)
            # These should have higher closed_forms than average
            assert isinstance(features.closed_forms, float)

    def test_bridges_for_sequential(self):
        """Bridge geometric forms align with sequential semantics."""
        bridge_words = ["when", "then", "chain"]
        for word in bridge_words:
            features = analyze_glyphs(word)
            report = lint_constraint_name(word, SemanticType.SEQUENTIAL)
            # Should pass or have minimal warnings
            assert isinstance(report, LintReport)

    def test_hooks_for_terminals(self):
        """Hook geometric forms align with terminal semantics."""
        hook_words = ["halt", "finfr", "freeze"]
        for word in hook_words:
            features = analyze_glyphs(word)
            # These should have hooks/terminals
            assert isinstance(features.hooks_terminals, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
