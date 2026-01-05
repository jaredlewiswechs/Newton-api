"""
JESTER - Newton Code Constraint Translator
==========================================

A deterministic code analyzer that extracts:
- Inferred constraints
- Guard conditions / early exits
- Unreachable states
- Forbidden inputs
- Requirements implied by checks

And produces Newton cartridge blueprints representing the structural meaning of code.

This is NOT a neural guesser - it's rule-based extraction using AST parsing.
"""

import re
import json
from typing import Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

# Try to import tree-sitter for real parsing
try:
    from tree_sitter_languages import get_parser, get_language
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


class ConstraintKind(str, Enum):
    """Types of constraints that can be extracted from code."""
    GUARD = "guard"
    ASSERTION = "assertion"
    PRECONDITION = "precondition"
    POSTCONDITION = "postcondition"
    INVARIANT = "invariant"
    RANGE_CHECK = "range_check"
    NULL_CHECK = "null_check"
    TYPE_CHECK = "type_check"
    EARLY_EXIT = "early_exit"
    EXCEPTION = "exception"
    FORBIDDEN_STATE = "forbidden_state"


class SourceLanguage(str, Enum):
    """Supported source languages for analysis."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    C = "c"
    CPP = "cpp"
    SWIFT = "swift"
    OBJECTIVE_C = "objc"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    UNKNOWN = "unknown"


@dataclass
class ExtractedConstraint:
    """A single constraint extracted from source code."""
    kind: ConstraintKind
    raw_condition: str
    normalized_form: str
    newton_constraint: str
    line_number: Optional[int] = None
    context: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> dict:
        return {
            "kind": self.kind.value,
            "raw_condition": self.raw_condition,
            "normalized_form": self.normalized_form,
            "newton_constraint": self.newton_constraint,
            "line_number": self.line_number,
            "context": self.context,
            "confidence": self.confidence
        }


@dataclass
class NewtonCartridge:
    """A Newton cartridge representation of extracted code constraints."""
    source_language: str
    source_snippet: str
    constraints: list[ExtractedConstraint] = field(default_factory=list)
    functions_analyzed: list[str] = field(default_factory=list)
    forbidden_states: list[str] = field(default_factory=list)
    required_invariants: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "source_language": self.source_language,
            "source_snippet": self.source_snippet[:500] + ("..." if len(self.source_snippet) > 500 else ""),
            "constraints": [c.to_dict() for c in self.constraints],
            "functions_analyzed": self.functions_analyzed,
            "forbidden_states": self.forbidden_states,
            "required_invariants": self.required_invariants,
            "warnings": self.warnings,
            "summary": {
                "total_constraints": len(self.constraints),
                "by_kind": self._count_by_kind()
            }
        }

    def _count_by_kind(self) -> dict:
        counts = {}
        for c in self.constraints:
            kind = c.kind.value
            counts[kind] = counts.get(kind, 0) + 1
        return counts

    def to_cdl(self) -> str:
        """Convert to Newton CDL format."""
        lines = [
            f"// Newton Cartridge - Generated from {self.source_language}",
            f"// Extracted {len(self.constraints)} constraints",
            "",
            "cartridge JesterAnalysis {",
        ]

        # Add constraints
        for i, constraint in enumerate(self.constraints):
            lines.append(f"  // {constraint.kind.value}: {constraint.raw_condition}")
            lines.append(f"  constraint c{i}: {constraint.newton_constraint};")
            lines.append("")

        # Add forbidden states
        if self.forbidden_states:
            lines.append("  // Forbidden states")
            for state in self.forbidden_states:
                lines.append(f"  forbidden: {state};")
            lines.append("")

        # Add invariants
        if self.required_invariants:
            lines.append("  // Required invariants")
            for inv in self.required_invariants:
                lines.append(f"  invariant: {inv};")

        lines.append("}")
        return "\n".join(lines)


class LanguageDetector:
    """Detects programming language from source code."""

    PATTERNS = {
        SourceLanguage.PYTHON: [
            (r"^def\s+\w+\s*\(", 10),
            (r"^class\s+\w+\s*[:\(]", 10),
            (r"^\s*import\s+\w+", 5),
            (r"^\s*from\s+\w+\s+import", 5),
            (r":\s*$", 3),
            (r"self\.", 5),
            (r"__init__", 8),
        ],
        SourceLanguage.JAVASCRIPT: [
            (r"function\s+\w+\s*\(", 8),
            (r"const\s+\w+\s*=", 5),
            (r"let\s+\w+\s*=", 5),
            (r"=>\s*{", 8),
            (r"require\s*\(", 6),
            (r"module\.exports", 8),
            (r"console\.(log|error|warn)", 5),
        ],
        SourceLanguage.TYPESCRIPT: [
            (r":\s*(string|number|boolean|any)\b", 10),
            (r"interface\s+\w+", 10),
            (r"type\s+\w+\s*=", 10),
            (r"<\w+>", 5),
            (r"as\s+\w+", 5),
        ],
        SourceLanguage.SWIFT: [
            (r"\bfunc\s+\w+", 10),
            (r"\bvar\s+\w+\s*:", 8),
            (r"\blet\s+\w+\s*:", 8),
            (r"\bguard\s+", 10),
            (r"\bif\s+let\s+", 8),
            (r"import\s+(UIKit|Foundation|SwiftUI)", 10),
            (r"@\w+\b", 5),
        ],
        SourceLanguage.OBJECTIVE_C: [
            (r"@interface\s+\w+", 15),
            (r"@implementation\s+\w+", 15),
            (r"@property", 10),
            (r"\[\w+\s+\w+\]", 8),
            (r"#import\s*[<\"]", 8),
            (r"NS\w+", 5),
            (r"- \(\w+\)", 8),
        ],
        SourceLanguage.C: [
            (r"#include\s*[<\"]", 10),
            (r"\bint\s+main\s*\(", 10),
            (r"\b(void|int|char|float|double)\s+\w+\s*\(", 8),
            (r"printf\s*\(", 5),
            (r"malloc\s*\(", 5),
            (r"->\w+", 5),
        ],
        SourceLanguage.CPP: [
            (r"#include\s*<\w+>", 8),
            (r"\bclass\s+\w+\s*{", 10),
            (r"std::", 10),
            (r"cout\s*<<", 8),
            (r"cin\s*>>", 8),
            (r"namespace\s+\w+", 8),
            (r"template\s*<", 10),
        ],
        SourceLanguage.JAVA: [
            (r"public\s+(class|interface)\s+\w+", 15),
            (r"public\s+static\s+void\s+main", 15),
            (r"System\.out\.print", 10),
            (r"@Override", 10),
            (r"import\s+java\.", 10),
            (r"throws\s+\w+Exception", 8),
        ],
        SourceLanguage.GO: [
            (r"^package\s+\w+", 15),
            (r"func\s+\w+\s*\(", 10),
            (r"import\s+\(", 8),
            (r"fmt\.(Print|Sprintf)", 8),
            (r":=", 5),
            (r"go\s+\w+\(", 8),
        ],
        SourceLanguage.RUST: [
            (r"\bfn\s+\w+", 10),
            (r"\blet\s+mut\s+", 10),
            (r"impl\s+\w+", 10),
            (r"pub\s+(fn|struct|enum)", 10),
            (r"->.*{", 5),
            (r"println!\s*\(", 8),
            (r"Option<|Result<", 10),
        ],
        SourceLanguage.RUBY: [
            (r"^def\s+\w+", 8),
            (r"^class\s+\w+", 8),
            (r"\bend\s*$", 5),
            (r"require\s+['\"]", 8),
            (r"attr_(reader|writer|accessor)", 10),
            (r"puts\s+", 5),
        ],
    }

    @classmethod
    def detect(cls, code: str) -> SourceLanguage:
        """Detect the programming language of the given code."""
        scores = {lang: 0 for lang in SourceLanguage}

        for lang, patterns in cls.PATTERNS.items():
            for pattern, weight in patterns:
                if re.search(pattern, code, re.MULTILINE):
                    scores[lang] += weight

        # Find the best match
        best_lang = max(scores, key=scores.get)
        if scores[best_lang] > 0:
            return best_lang
        return SourceLanguage.UNKNOWN


class ConstraintNormalizer:
    """Normalizes code conditions into Newton constraint format."""

    # Operator mappings
    COMPARISON_OPS = {
        "==": "=",
        "!=": "!=",
        "<=": "<=",
        ">=": ">=",
        "<": "<",
        ">": ">",
        "===": "=",
        "!==": "!=",
    }

    LOGICAL_OPS = {
        "&&": "AND",
        "||": "OR",
        "and": "AND",
        "or": "OR",
        "!": "NOT",
        "not": "NOT",
    }

    @classmethod
    def normalize(cls, condition: str, language: SourceLanguage) -> tuple[str, str]:
        """
        Normalize a condition into standard form and Newton constraint.
        Returns (normalized_form, newton_constraint).
        """
        # Clean up the condition
        clean = condition.strip()

        # Handle null/nil checks
        null_patterns = [
            (r"(\w+)\s*(?:==|===)\s*(?:None|null|nil|NULL)", r"\1 IS NULL"),
            (r"(\w+)\s*(?:!=|!==)\s*(?:None|null|nil|NULL)", r"\1 IS NOT NULL"),
            (r"(\w+)\s+is\s+None", r"\1 IS NULL"),
            (r"(\w+)\s+is\s+not\s+None", r"\1 IS NOT NULL"),
            (r"!\s*(\w+)", r"\1 IS FALSY"),
            (r"(\w+)\s*\?\?", r"\1 IS NOT NULL"),
        ]

        normalized = clean
        for pattern, replacement in null_patterns:
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

        # Handle comparison operators
        for code_op, newton_op in cls.COMPARISON_OPS.items():
            normalized = normalized.replace(code_op, f" {newton_op} ")

        # Handle logical operators
        for code_op, newton_op in cls.LOGICAL_OPS.items():
            normalized = re.sub(rf"\b{re.escape(code_op)}\b", f" {newton_op} ", normalized, flags=re.IGNORECASE)

        # Clean up whitespace
        normalized = " ".join(normalized.split())

        # Generate Newton constraint
        newton = cls._to_newton_constraint(normalized, condition)

        return normalized, newton

    @classmethod
    def _to_newton_constraint(cls, normalized: str, original: str) -> str:
        """Convert normalized form to Newton constraint format."""
        # Try to convert to ratio form for comparisons
        ratio_match = re.match(r"(\w+)\s*([<>]=?)\s*(\w+)", normalized)
        if ratio_match:
            left, op, right = ratio_match.groups()

            # Convert to ratio form when appropriate
            if op == "<=" and right.isalnum():
                return f"{left} / {right} <= 1.0"
            elif op == ">=" and right.isalnum():
                return f"{left} / {right} >= 1.0"
            elif op == "<" and right.isalnum():
                return f"{left} / {right} < 1.0"
            elif op == ">" and right.isalnum():
                return f"{left} / {right} > 1.0"

        # Handle null checks
        if "IS NULL" in normalized:
            var = re.search(r"(\w+)\s+IS", normalized)
            if var:
                return f"defined({var.group(1)}) = false"

        if "IS NOT NULL" in normalized:
            var = re.search(r"(\w+)\s+IS", normalized)
            if var:
                return f"defined({var.group(1)}) = true"

        # Handle equality
        eq_match = re.match(r"(\w+)\s*=\s*(\w+)", normalized)
        if eq_match:
            left, right = eq_match.groups()
            return f"{left} = {right}"

        # Handle inequality
        neq_match = re.match(r"(\w+)\s*!=\s*(\w+)", normalized)
        if neq_match:
            left, right = neq_match.groups()
            return f"{left} != {right}"

        # Fall back to original
        return normalized


class RegexExtractor:
    """Extracts constraints using regex patterns when tree-sitter is unavailable."""

    # Language-specific patterns
    PATTERNS = {
        SourceLanguage.PYTHON: {
            "if_condition": r"if\s+(.+?):",
            "assert": r"assert\s+(.+?)(?:,|$)",
            "raise": r"raise\s+(\w+(?:Error|Exception))\s*\(([^)]*)\)",
            "return_early": r"if\s+(.+?):\s*\n\s*return",
            "function_def": r"def\s+(\w+)\s*\([^)]*\)",
        },
        SourceLanguage.JAVASCRIPT: {
            "if_condition": r"if\s*\((.+?)\)\s*{",
            "throw": r"throw\s+new\s+(\w+)\s*\(([^)]*)\)",
            "return_early": r"if\s*\((.+?)\)\s*{\s*return",
            "function_def": r"function\s+(\w+)\s*\([^)]*\)",
            "arrow_guard": r"if\s*\((.+?)\)\s*return",
        },
        SourceLanguage.SWIFT: {
            "guard": r"guard\s+(.+?)\s+else\s*{",
            "if_let": r"if\s+let\s+(\w+)\s*=\s*(.+?)\s*{",
            "precondition": r"precondition\s*\((.+?)\)",
            "assert": r"assert\s*\((.+?)\)",
            "fatalError": r"fatalError\s*\(([^)]*)\)",
            "function_def": r"func\s+(\w+)\s*\([^)]*\)",
        },
        SourceLanguage.OBJECTIVE_C: {
            "nsassert": r"NSAssert\s*\((.+?),",
            "nsparameterassert": r"NSParameterAssert\s*\((.+?)\)",
            "if_condition": r"if\s*\((.+?)\)\s*{",
            "return_early": r"if\s*\((.+?)\)\s*{\s*return",
            "method_def": r"-\s*\([^)]+\)\s*(\w+)",
        },
        SourceLanguage.C: {
            "assert": r"assert\s*\((.+?)\)",
            "if_condition": r"if\s*\((.+?)\)\s*{",
            "return_early": r"if\s*\((.+?)\)\s*{\s*return",
            "function_def": r"\b\w+\s+(\w+)\s*\([^)]*\)\s*{",
        },
        SourceLanguage.JAVA: {
            "if_condition": r"if\s*\((.+?)\)\s*{",
            "assert": r"assert\s+(.+?)(?::|;)",
            "throw": r"throw\s+new\s+(\w+)\s*\(([^)]*)\)",
            "function_def": r"(?:public|private|protected)\s+\w+\s+(\w+)\s*\(",
        },
        SourceLanguage.GO: {
            "if_condition": r"if\s+(.+?)\s*{",
            "panic": r"panic\s*\(([^)]+)\)",
            "function_def": r"func\s+(\w+)\s*\(",
        },
        SourceLanguage.RUST: {
            "if_condition": r"if\s+(.+?)\s*{",
            "assert": r"assert!\s*\((.+?)\)",
            "panic": r"panic!\s*\(([^)]+)\)",
            "unwrap": r"\.unwrap\(\)",
            "expect": r"\.expect\s*\(([^)]+)\)",
            "function_def": r"fn\s+(\w+)\s*\(",
        },
    }

    @classmethod
    def extract(cls, code: str, language: SourceLanguage) -> list[ExtractedConstraint]:
        """Extract constraints using regex patterns."""
        constraints = []
        patterns = cls.PATTERNS.get(language, {})

        # Add common patterns
        common_patterns = cls.PATTERNS.get(SourceLanguage.PYTHON, {})

        for pattern_name, pattern in patterns.items():
            for match in re.finditer(pattern, code, re.MULTILINE | re.DOTALL):
                line_num = code[:match.start()].count('\n') + 1

                if pattern_name == "guard":
                    constraint = cls._create_constraint(
                        ConstraintKind.GUARD,
                        match.group(1),
                        language,
                        line_num,
                        "Swift guard statement"
                    )
                elif pattern_name in ("if_condition", "if_let"):
                    constraint = cls._create_constraint(
                        ConstraintKind.GUARD,
                        match.group(1),
                        language,
                        line_num,
                        "Conditional check"
                    )
                elif pattern_name in ("assert", "nsassert", "nsparameterassert", "precondition"):
                    constraint = cls._create_constraint(
                        ConstraintKind.ASSERTION,
                        match.group(1),
                        language,
                        line_num,
                        "Assertion"
                    )
                elif pattern_name in ("raise", "throw", "fatalError", "panic"):
                    exc_type = match.group(1) if match.lastindex >= 1 else "Error"
                    msg = match.group(2) if match.lastindex >= 2 else ""
                    constraint = cls._create_constraint(
                        ConstraintKind.EXCEPTION,
                        f"{exc_type}: {msg}",
                        language,
                        line_num,
                        "Exception/Error thrown"
                    )
                elif pattern_name in ("return_early", "arrow_guard"):
                    constraint = cls._create_constraint(
                        ConstraintKind.EARLY_EXIT,
                        match.group(1),
                        language,
                        line_num,
                        "Early return guard"
                    )
                elif pattern_name in ("unwrap", "expect"):
                    constraint = cls._create_constraint(
                        ConstraintKind.PRECONDITION,
                        "value IS NOT NULL",
                        language,
                        line_num,
                        "Unwrap requires non-null"
                    )
                else:
                    continue

                if constraint:
                    constraints.append(constraint)

        return constraints

    @classmethod
    def _create_constraint(
        cls,
        kind: ConstraintKind,
        raw: str,
        language: SourceLanguage,
        line_num: int,
        context: str
    ) -> ExtractedConstraint:
        """Create an ExtractedConstraint from raw condition."""
        normalized, newton = ConstraintNormalizer.normalize(raw, language)
        return ExtractedConstraint(
            kind=kind,
            raw_condition=raw.strip(),
            normalized_form=normalized,
            newton_constraint=newton,
            line_number=line_num,
            context=context,
            confidence=0.8  # Regex extraction is less confident than AST
        )

    @classmethod
    def extract_functions(cls, code: str, language: SourceLanguage) -> list[str]:
        """Extract function/method names from code."""
        patterns = cls.PATTERNS.get(language, {})
        functions = []

        for pattern_name in ("function_def", "method_def"):
            pattern = patterns.get(pattern_name)
            if pattern:
                for match in re.finditer(pattern, code, re.MULTILINE):
                    functions.append(match.group(1))

        return functions


class TreeSitterExtractor:
    """Extracts constraints using tree-sitter AST parsing."""

    # Language mappings for tree-sitter
    LANG_MAP = {
        SourceLanguage.PYTHON: "python",
        SourceLanguage.JAVASCRIPT: "javascript",
        SourceLanguage.TYPESCRIPT: "typescript",
        SourceLanguage.C: "c",
        SourceLanguage.CPP: "cpp",
        SourceLanguage.SWIFT: "swift",
        SourceLanguage.JAVA: "java",
        SourceLanguage.GO: "go",
        SourceLanguage.RUST: "rust",
        SourceLanguage.RUBY: "ruby",
    }

    @classmethod
    def extract(cls, code: str, language: SourceLanguage) -> list[ExtractedConstraint]:
        """Extract constraints using tree-sitter AST."""
        if not TREE_SITTER_AVAILABLE:
            return []

        lang_name = cls.LANG_MAP.get(language)
        if not lang_name:
            return []

        try:
            parser = get_parser(lang_name)
            tree = parser.parse(bytes(code, "utf-8"))

            constraints = []
            constraints.extend(cls._extract_if_conditions(tree, code, language))
            constraints.extend(cls._extract_assertions(tree, code, language))
            constraints.extend(cls._extract_early_returns(tree, code, language))

            return constraints
        except Exception as e:
            # Fall back to regex if tree-sitter fails
            return []

    @classmethod
    def _extract_if_conditions(cls, tree, code: str, language: SourceLanguage) -> list[ExtractedConstraint]:
        """Extract conditions from if statements."""
        constraints = []

        def visit(node):
            if node.type == "if_statement":
                # Find the condition child
                for child in node.children:
                    if child.type in ("condition", "comparison_operator", "binary_expression", "parenthesized_expression"):
                        cond_text = code[child.start_byte:child.end_byte]
                        line_num = code[:child.start_byte].count('\n') + 1

                        normalized, newton = ConstraintNormalizer.normalize(cond_text, language)
                        constraints.append(ExtractedConstraint(
                            kind=ConstraintKind.GUARD,
                            raw_condition=cond_text,
                            normalized_form=normalized,
                            newton_constraint=newton,
                            line_number=line_num,
                            context="If statement condition",
                            confidence=1.0
                        ))
                        break

            for child in node.children:
                visit(child)

        visit(tree.root_node)
        return constraints

    @classmethod
    def _extract_assertions(cls, tree, code: str, language: SourceLanguage) -> list[ExtractedConstraint]:
        """Extract assertions from code."""
        constraints = []

        def visit(node):
            if node.type in ("assert_statement", "call_expression"):
                text = code[node.start_byte:node.end_byte]
                if "assert" in text.lower():
                    # Extract the condition
                    cond_match = re.search(r"assert\s*\(?(.+?)(?:\)|,|$)", text, re.IGNORECASE)
                    if cond_match:
                        cond = cond_match.group(1)
                        line_num = code[:node.start_byte].count('\n') + 1

                        normalized, newton = ConstraintNormalizer.normalize(cond, language)
                        constraints.append(ExtractedConstraint(
                            kind=ConstraintKind.ASSERTION,
                            raw_condition=cond,
                            normalized_form=normalized,
                            newton_constraint=newton,
                            line_number=line_num,
                            context="Assertion",
                            confidence=1.0
                        ))

            for child in node.children:
                visit(child)

        visit(tree.root_node)
        return constraints

    @classmethod
    def _extract_early_returns(cls, tree, code: str, language: SourceLanguage) -> list[ExtractedConstraint]:
        """Extract early return patterns."""
        constraints = []

        def visit(node, parent_condition=None):
            if node.type == "if_statement":
                # Check if this if contains a return
                has_return = False
                condition = None

                for child in node.children:
                    if child.type in ("condition", "comparison_operator", "binary_expression"):
                        condition = code[child.start_byte:child.end_byte]
                    if child.type == "block" or child.type == "statement_block":
                        block_text = code[child.start_byte:child.end_byte]
                        if "return" in block_text and len(block_text) < 100:
                            has_return = True

                if has_return and condition:
                    line_num = code[:node.start_byte].count('\n') + 1
                    normalized, newton = ConstraintNormalizer.normalize(condition, language)
                    constraints.append(ExtractedConstraint(
                        kind=ConstraintKind.EARLY_EXIT,
                        raw_condition=condition,
                        normalized_form=normalized,
                        newton_constraint=newton,
                        line_number=line_num,
                        context="Early return guard",
                        confidence=1.0
                    ))

            for child in node.children:
                visit(child)

        visit(tree.root_node)
        return constraints


class Jester:
    """
    Main Jester analyzer class.

    Parses source code and extracts constraints to produce Newton cartridges.
    """

    def __init__(self, code: str, language: Optional[SourceLanguage] = None):
        """
        Initialize Jester with source code.

        Args:
            code: The source code to analyze
            language: Optional language hint (auto-detected if not provided)
        """
        self.code = code
        self.language = language or LanguageDetector.detect(code)
        self._constraints: list[ExtractedConstraint] = []
        self._functions: list[str] = []
        self._analyzed = False

    def analyze(self) -> "Jester":
        """
        Perform the analysis. Returns self for chaining.
        """
        if self._analyzed:
            return self

        # Try tree-sitter first, fall back to regex
        if TREE_SITTER_AVAILABLE:
            self._constraints = TreeSitterExtractor.extract(self.code, self.language)

        # If tree-sitter didn't find anything, use regex
        if not self._constraints:
            self._constraints = RegexExtractor.extract(self.code, self.language)

        # Extract function names
        self._functions = RegexExtractor.extract_functions(self.code, self.language)

        self._analyzed = True
        return self

    def get_constraints(self) -> list[ExtractedConstraint]:
        """Get all extracted constraints."""
        if not self._analyzed:
            self.analyze()
        return self._constraints

    def get_guards(self) -> list[ExtractedConstraint]:
        """Get only guard constraints."""
        return [c for c in self.get_constraints() if c.kind == ConstraintKind.GUARD]

    def get_assertions(self) -> list[ExtractedConstraint]:
        """Get only assertion constraints."""
        return [c for c in self.get_constraints() if c.kind == ConstraintKind.ASSERTION]

    def get_early_exits(self) -> list[ExtractedConstraint]:
        """Get only early exit constraints."""
        return [c for c in self.get_constraints() if c.kind == ConstraintKind.EARLY_EXIT]

    def to_cartridge(self) -> NewtonCartridge:
        """
        Generate a Newton cartridge from the analyzed code.
        """
        if not self._analyzed:
            self.analyze()

        # Build forbidden states from guards
        forbidden_states = []
        for c in self._constraints:
            if c.kind in (ConstraintKind.GUARD, ConstraintKind.EARLY_EXIT):
                # The negation of a guard condition is a forbidden state
                forbidden_states.append(f"NOT ({c.normalized_form})")

        # Build invariants from assertions
        invariants = []
        for c in self._constraints:
            if c.kind == ConstraintKind.ASSERTION:
                invariants.append(c.normalized_form)

        # Build warnings
        warnings = []
        if not self._constraints:
            warnings.append("No constraints could be extracted from this code")
        if self.language == SourceLanguage.UNKNOWN:
            warnings.append("Language could not be detected; analysis may be incomplete")

        return NewtonCartridge(
            source_language=self.language.value,
            source_snippet=self.code,
            constraints=self._constraints,
            functions_analyzed=self._functions,
            forbidden_states=forbidden_states[:10],  # Limit to top 10
            required_invariants=invariants[:10],
            warnings=warnings
        )

    def to_dict(self) -> dict:
        """Convert analysis to dictionary."""
        return self.to_cartridge().to_dict()

    def to_json(self, indent: int = 2) -> str:
        """Convert analysis to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_cdl(self) -> str:
        """Convert analysis to Newton CDL format."""
        return self.to_cartridge().to_cdl()


# Convenience functions
def analyze_code(code: str, language: Optional[str] = None) -> dict:
    """
    Analyze source code and return constraints as a dictionary.

    Args:
        code: Source code to analyze
        language: Optional language hint (python, javascript, swift, etc.)

    Returns:
        Dictionary containing extracted constraints and Newton cartridge
    """
    lang = None
    if language:
        try:
            lang = SourceLanguage(language.lower())
        except ValueError:
            pass

    jester = Jester(code, lang)
    return jester.to_dict()


def analyze_file(filepath: str) -> dict:
    """
    Analyze a source file and return constraints.

    Args:
        filepath: Path to the source file

    Returns:
        Dictionary containing extracted constraints
    """
    with open(filepath, 'r') as f:
        code = f.read()

    # Try to detect language from extension
    ext_map = {
        '.py': SourceLanguage.PYTHON,
        '.js': SourceLanguage.JAVASCRIPT,
        '.ts': SourceLanguage.TYPESCRIPT,
        '.swift': SourceLanguage.SWIFT,
        '.m': SourceLanguage.OBJECTIVE_C,
        '.c': SourceLanguage.C,
        '.cpp': SourceLanguage.CPP,
        '.cc': SourceLanguage.CPP,
        '.java': SourceLanguage.JAVA,
        '.go': SourceLanguage.GO,
        '.rs': SourceLanguage.RUST,
        '.rb': SourceLanguage.RUBY,
    }

    import os
    ext = os.path.splitext(filepath)[1].lower()
    lang = ext_map.get(ext)

    jester = Jester(code, lang)
    return jester.to_dict()


# Module info
JESTER_INFO = {
    "name": "Jester",
    "version": "1.0.0",
    "description": "Newton Code Constraint Translator - extracts guards, invariants, and constraints from source code",
    "supported_languages": [lang.value for lang in SourceLanguage if lang != SourceLanguage.UNKNOWN],
    "constraint_kinds": [kind.value for kind in ConstraintKind],
    "features": [
        "Guard condition extraction",
        "Assertion analysis",
        "Early exit detection",
        "Null/nil check recognition",
        "Exception/error path analysis",
        "Newton cartridge generation",
        "CDL output format",
        "Multi-language support"
    ],
    "tree_sitter_available": TREE_SITTER_AVAILABLE
}
