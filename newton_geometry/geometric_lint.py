"""
Geometric Constraint Linting

Human constraint verification happens geometrically before semantically.
This module analyzes constraint names for geometric-semantic alignment.

The shape of a word carries cognitive load before meaning is parsed.
Newton notation should leverage this by aligning glyph geometry with
semantic intent.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# Glyph classification based on geometric primitives
CLOSED_FORMS = set("oOQ0@abdegpq869")
OPEN_CURVES = set("cCsS35(){}[]<>")
STRAIGHT_LINES = set("lLiI1|_-=7/\\")
INTERSECTIONS = set("xX+*tTkKfF4#")
HOOKS_TERMINALS = set("fFrRjJgGyY")
BRIDGES = set("nNmMhHuUwW")
POINTS = set("iIjJ!?.:;")


class SemanticType(Enum):
    """Semantic categories for constraint names."""

    CONTAINMENT = "containment"  # Must stay within bounds (quota, bound, pool)
    SEQUENTIAL = "sequential"  # A then B then C (chain, when, flow)
    TERMINAL = "terminal"  # Hard stop (halt, finfr, end)
    IDENTITY = "identity"  # Equality check (is, same, id)
    CHOICE = "choice"  # Branching decision (or, pick, switch)
    GUARD = "guard"  # Lightweight check (if, when, has)
    ACTION = "action"  # Operation execution (run, exec, call)


class VisualDensity(Enum):
    """Visual weight classification."""

    LIGHT = "light"  # 1-3 chars, lots of whitespace (i, is, if)
    MEDIUM = "medium"  # 4-6 chars, standard weight (when, then, check)
    HEAVY = "heavy"  # 7+ chars or dense geometry (finfr, commit, transaction)


class Severity(Enum):
    """Lint warning severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class GeometricFeatures:
    """Geometric analysis of a word's glyph composition."""

    word: str
    closed_forms: float  # 0.0-1.0, ratio of closed shapes
    open_curves: float  # 0.0-1.0, ratio of open curves
    straight_lines: float  # 0.0-1.0, ratio of straight elements
    intersections: float  # 0.0-1.0, ratio of crossing shapes
    hooks_terminals: float  # 0.0-1.0, ratio of terminal forms
    bridges: float  # 0.0-1.0, ratio of bridge shapes
    points: float  # 0.0-1.0, ratio of point/dot forms
    visual_density: VisualDensity

    @property
    def dominant_feature(self) -> str:
        """Return the most prominent geometric feature."""
        features = {
            "closed_forms": self.closed_forms,
            "open_curves": self.open_curves,
            "straight_lines": self.straight_lines,
            "intersections": self.intersections,
            "hooks_terminals": self.hooks_terminals,
            "bridges": self.bridges,
            "points": self.points,
        }
        return max(features, key=features.get)


@dataclass
class LintWarning:
    """A single lint warning."""

    severity: Severity
    message: str
    suggestion: Optional[str] = None


@dataclass
class LintReport:
    """Complete lint report for a constraint name."""

    name: str
    semantic_type: SemanticType
    features: GeometricFeatures
    warnings: list[LintWarning]
    passed: bool

    @property
    def has_errors(self) -> bool:
        return any(w.severity == Severity.ERROR for w in self.warnings)

    @property
    def has_warnings(self) -> bool:
        return any(w.severity == Severity.WARNING for w in self.warnings)


def analyze_glyphs(word: str) -> GeometricFeatures:
    """
    Analyze the geometric composition of a word.

    Each character is classified by its dominant geometric primitive.
    Returns ratios of each primitive type present in the word.
    """
    if not word:
        return GeometricFeatures(
            word="",
            closed_forms=0.0,
            open_curves=0.0,
            straight_lines=0.0,
            intersections=0.0,
            hooks_terminals=0.0,
            bridges=0.0,
            points=0.0,
            visual_density=VisualDensity.LIGHT,
        )

    # Strip non-alphabetic for analysis but keep for density
    alpha_word = "".join(c for c in word if c.isalpha())
    total = len(alpha_word) if alpha_word else 1

    counts = {
        "closed": sum(1 for c in alpha_word if c in CLOSED_FORMS),
        "open": sum(1 for c in alpha_word if c in OPEN_CURVES),
        "straight": sum(1 for c in alpha_word if c in STRAIGHT_LINES),
        "intersect": sum(1 for c in alpha_word if c in INTERSECTIONS),
        "hooks": sum(1 for c in alpha_word if c in HOOKS_TERMINALS),
        "bridges": sum(1 for c in alpha_word if c in BRIDGES),
        "points": sum(1 for c in alpha_word if c in POINTS),
    }

    # Determine visual density
    if len(word) <= 3:
        density = VisualDensity.LIGHT
    elif len(word) <= 6:
        density = VisualDensity.MEDIUM
    else:
        density = VisualDensity.HEAVY

    return GeometricFeatures(
        word=word,
        closed_forms=counts["closed"] / total,
        open_curves=counts["open"] / total,
        straight_lines=counts["straight"] / total,
        intersections=counts["intersect"] / total,
        hooks_terminals=counts["hooks"] / total,
        bridges=counts["bridges"] / total,
        points=counts["points"] / total,
        visual_density=density,
    )


# Recommended alternatives for each semantic type
RECOMMENDATIONS = {
    SemanticType.CONTAINMENT: ["quota", "bound", "pool", "scope", "dome", "orbit"],
    SemanticType.SEQUENTIAL: ["chain", "then", "when", "flow", "next", "through"],
    SemanticType.TERMINAL: ["halt", "stop", "finfr", "end", "freeze", "fail"],
    SemanticType.IDENTITY: ["is", "same", "id", "one", "equals", "this"],
    SemanticType.CHOICE: ["or", "xor", "pick", "switch", "fork", "select"],
    SemanticType.GUARD: ["if", "when", "has", "can", "may", "ok"],
    SemanticType.ACTION: ["run", "exec", "call", "do", "fire", "emit"],
}


def lint_constraint_name(
    name: str,
    semantic_type: SemanticType,
    strict: bool = False,
) -> LintReport:
    """
    Analyze a constraint name for geometric-semantic alignment.

    Args:
        name: The constraint name to analyze
        semantic_type: The intended semantic category
        strict: If True, warnings become errors

    Returns:
        LintReport with geometric features and any alignment warnings
    """
    features = analyze_glyphs(name)
    warnings: list[LintWarning] = []

    severity = Severity.ERROR if strict else Severity.WARNING
    suggestions = RECOMMENDATIONS.get(semantic_type, [])

    # Check alignment based on semantic type
    if semantic_type == SemanticType.CONTAINMENT:
        if features.closed_forms < 0.25:
            warnings.append(
                LintWarning(
                    severity=severity,
                    message=f"'{name}' suggests containment but lacks closed shapes (closed={features.closed_forms:.2f})",
                    suggestion=f"Consider: {', '.join(suggestions[:3])}",
                )
            )

    elif semantic_type == SemanticType.TERMINAL:
        if features.hooks_terminals < 0.15:
            warnings.append(
                LintWarning(
                    severity=severity,
                    message=f"'{name}' suggests termination but lacks terminal forms (hooks={features.hooks_terminals:.2f})",
                    suggestion=f"Consider: {', '.join(suggestions[:3])}",
                )
            )

    elif semantic_type == SemanticType.SEQUENTIAL:
        if features.bridges < 0.25:
            warnings.append(
                LintWarning(
                    severity=severity,
                    message=f"'{name}' suggests sequence but lacks bridges (bridges={features.bridges:.2f})",
                    suggestion=f"Consider: {', '.join(suggestions[:3])}",
                )
            )

    elif semantic_type == SemanticType.IDENTITY:
        if features.straight_lines < 0.15 and features.points < 0.15:
            warnings.append(
                LintWarning(
                    severity=severity,
                    message=f"'{name}' suggests identity but lacks linear/point forms",
                    suggestion=f"Consider: {', '.join(suggestions[:3])}",
                )
            )

    elif semantic_type == SemanticType.CHOICE:
        if features.intersections < 0.15:
            warnings.append(
                LintWarning(
                    severity=severity,
                    message=f"'{name}' suggests choice but lacks intersections (intersect={features.intersections:.2f})",
                    suggestion=f"Consider: {', '.join(suggestions[:3])}",
                )
            )

    elif semantic_type == SemanticType.GUARD:
        if features.visual_density == VisualDensity.HEAVY:
            warnings.append(
                LintWarning(
                    severity=Severity.INFO,
                    message=f"'{name}' is visually heavy for a simple guard",
                    suggestion=f"Consider: {', '.join(suggestions[:3])}",
                )
            )

    elif semantic_type == SemanticType.ACTION:
        if features.hooks_terminals < 0.1 and features.intersections < 0.1:
            warnings.append(
                LintWarning(
                    severity=Severity.INFO,
                    message=f"'{name}' suggests action but lacks active forms",
                    suggestion=f"Consider: {', '.join(suggestions[:3])}",
                )
            )

    # Check visual density alignment
    density_warnings = _check_density_alignment(name, semantic_type, features)
    warnings.extend(density_warnings)

    # Check for known contradictions
    contradiction_warnings = _check_contradictions(name, semantic_type, features)
    warnings.extend(contradiction_warnings)

    passed = not any(w.severity in (Severity.WARNING, Severity.ERROR) for w in warnings)

    return LintReport(
        name=name,
        semantic_type=semantic_type,
        features=features,
        warnings=warnings,
        passed=passed,
    )


def _check_density_alignment(
    name: str,
    semantic_type: SemanticType,
    features: GeometricFeatures,
) -> list[LintWarning]:
    """Check if visual density matches semantic complexity."""
    warnings = []

    # Guards should be light
    if semantic_type == SemanticType.GUARD and features.visual_density == VisualDensity.HEAVY:
        warnings.append(
            LintWarning(
                severity=Severity.WARNING,
                message=f"'{name}' is visually heavy ({len(name)} chars) for a guard constraint",
                suggestion="Guards should be light (1-3 chars): if, has, ok, can",
            )
        )

    # Terminals can be medium or heavy
    if semantic_type == SemanticType.TERMINAL and features.visual_density == VisualDensity.LIGHT:
        warnings.append(
            LintWarning(
                severity=Severity.INFO,
                message=f"'{name}' is visually light for a terminal condition",
                suggestion="Terminal conditions often benefit from more visual weight",
            )
        )

    return warnings


def _check_contradictions(
    name: str,
    semantic_type: SemanticType,
    features: GeometricFeatures,
) -> list[LintWarning]:
    """Check for known geometric-semantic contradictions."""
    warnings = []
    lower_name = name.lower()

    # Known contradictions
    contradictions = {
        # Word claims one thing but shape suggests another
        "open": ("CONTAINMENT", "has closed loop in 'o'"),
        "stop": ("TERMINAL", "'p' has continuation bridge"),
        "flow": ("SEQUENTIAL", "'f' has terminal hook"),
        "close": ("TERMINAL", "'o' suggests openness"),
    }

    for word, (expected_type, reason) in contradictions.items():
        if word in lower_name:
            if semantic_type.value.upper() != expected_type:
                continue  # Only warn if type matches expected use
            warnings.append(
                LintWarning(
                    severity=Severity.INFO,
                    message=f"Potential geometric contradiction in '{name}': {reason}",
                    suggestion=None,
                )
            )

    return warnings


def lint_cartridge(
    constraints: list[tuple[str, SemanticType]],
    strict: bool = False,
) -> dict:
    """
    Lint all constraints in a cartridge.

    Args:
        constraints: List of (name, semantic_type) tuples
        strict: If True, warnings become errors

    Returns:
        Summary dict with all reports and statistics
    """
    reports = []
    for name, sem_type in constraints:
        report = lint_constraint_name(name, sem_type, strict=strict)
        reports.append(report)

    passed = sum(1 for r in reports if r.passed)
    warnings = sum(1 for r in reports if r.has_warnings and not r.has_errors)
    errors = sum(1 for r in reports if r.has_errors)

    return {
        "reports": reports,
        "summary": {
            "total": len(reports),
            "passed": passed,
            "warnings": warnings,
            "errors": errors,
        },
    }


def format_report(report: LintReport, verbose: bool = False) -> str:
    """Format a lint report for display."""
    lines = []

    # Status indicator
    if report.passed:
        status = "✓"
    elif report.has_errors:
        status = "✗"
    else:
        status = "⚠"

    lines.append(f"{status} {report.name}")
    lines.append(f"  Type: {report.semantic_type.value}")

    if verbose:
        f = report.features
        lines.append(
            f"  Features: closed={f.closed_forms:.2f}, bridges={f.bridges:.2f}, "
            f"hooks={f.hooks_terminals:.2f}, intersect={f.intersections:.2f}"
        )
        lines.append(f"  Density: {f.visual_density.value}")
        lines.append(f"  Dominant: {f.dominant_feature}")

    for warning in report.warnings:
        prefix = "  " + warning.severity.value.upper() + ": "
        lines.append(prefix + warning.message)
        if warning.suggestion:
            lines.append("    → " + warning.suggestion)

    if report.passed and not verbose:
        lines.append("  Good: geometric features align with semantic type")

    return "\n".join(lines)


def format_summary(result: dict) -> str:
    """Format lint summary for display."""
    s = result["summary"]
    lines = [
        "",
        f"Summary: {s['passed']} passed, {s['warnings']} warnings, {s['errors']} errors",
    ]
    return "\n".join(lines)


# Analysis of Newton's core keywords
NEWTON_KEYWORDS = {
    "when": (
        SemanticType.SEQUENTIAL,
        "Multiple bridges with entry point. "
        "Suggests conditional flow—bridges that only activate if entry permits.",
    ),
    "and": (
        SemanticType.SEQUENTIAL,
        "Containment + continuation + closure. "
        "Bridges link multiple conditions; closure suggests completeness requirement.",
    ),
    "fin": (
        SemanticType.TERMINAL,
        "Action → identity → continuation. "
        "Valid states flow forward. Terminal but suggests continuation.",
    ),
    "finfr": (
        SemanticType.TERMINAL,
        "Action → identity → bridge → action → STOP/TURN. "
        "PERFECT ALIGNMENT: Double hook with terminal turn encodes "
        "'attempted action that cannot continue.' The shape IS the meaning.",
    ),
}


def analyze_newton_keywords() -> str:
    """Analyze Newton's core keywords for geometric-semantic alignment."""
    lines = ["Newton Keyword Geometric Analysis", "=" * 40, ""]

    for keyword, (sem_type, analysis) in NEWTON_KEYWORDS.items():
        features = analyze_glyphs(keyword)
        report = lint_constraint_name(keyword, sem_type)

        lines.append(f"### {keyword}")
        lines.append(f"Semantic Type: {sem_type.value}")
        lines.append(f"Geometric Analysis: {analysis}")
        lines.append("")

        # Show glyph breakdown
        lines.append("Glyph breakdown:")
        for char in keyword:
            for category, char_set in [
                ("closed", CLOSED_FORMS),
                ("open", OPEN_CURVES),
                ("straight", STRAIGHT_LINES),
                ("intersect", INTERSECTIONS),
                ("hook", HOOKS_TERMINALS),
                ("bridge", BRIDGES),
                ("point", POINTS),
            ]:
                if char in char_set:
                    lines.append(f"  {char}: {category}")
                    break
            else:
                lines.append(f"  {char}: other")

        lines.append("")
        lines.append(f"Alignment: {'✓ EXCELLENT' if report.passed else '⚠ NEEDS REVIEW'}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo: Analyze Newton keywords
    print(analyze_newton_keywords())

    print("\n" + "=" * 60 + "\n")

    # Demo: Lint a sample cartridge
    sample_constraints = [
        ("when_valid_token", SemanticType.SEQUENTIAL),
        ("token_expired", SemanticType.TERMINAL),
        ("proceed_if_authorized", SemanticType.GUARD),  # Should warn
        ("finfr_invalid_session", SemanticType.TERMINAL),
        ("user_quota", SemanticType.CONTAINMENT),
        ("select_handler", SemanticType.CHOICE),
    ]

    print("Cartridge Lint: user_authentication.cdl")
    print("-" * 40)

    result = lint_cartridge(sample_constraints)
    for report in result["reports"]:
        print(format_report(report, verbose=True))
        print()

    print(format_summary(result))
