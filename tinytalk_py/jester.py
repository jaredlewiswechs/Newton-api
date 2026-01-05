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
class UnreachableState:
    """An unreachable state detected via control flow analysis."""
    description: str
    line_number: int
    reason: str
    category: str  # "dead_code", "impossible_condition", "contradictory_guards"

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "line_number": self.line_number,
            "reason": self.reason,
            "category": self.category
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
    unreachable_states: list = field(default_factory=list)  # list[UnreachableState]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "source_language": self.source_language,
            "source_snippet": self.source_snippet[:500] + ("..." if len(self.source_snippet) > 500 else ""),
            "constraints": [c.to_dict() for c in self.constraints],
            "functions_analyzed": self.functions_analyzed,
            "forbidden_states": self.forbidden_states,
            "required_invariants": self.required_invariants,
            "unreachable_states": [u.to_dict() if hasattr(u, 'to_dict') else u for u in self.unreachable_states],
            "warnings": self.warnings,
            "summary": {
                "total_constraints": len(self.constraints),
                "unreachable_count": len(self.unreachable_states),
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
            lines.append("")

        # Add unreachable states (CFG analysis)
        if self.unreachable_states:
            lines.append("  // Unreachable states (CFG analysis)")
            for u in self.unreachable_states:
                if hasattr(u, 'description'):
                    lines.append(f"  unreachable @{u.line_number}: {u.description};")
                else:
                    lines.append(f"  unreachable: {u};")

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


class ControlFlowAnalyzer:
    """
    Simple CFG-based unreachable state detection.

    Detects:
    - Dead code after unconditional returns/raises
    - Tautological conditions (always true/false)
    - Contradictory guard sequences
    - Impossible branches
    """

    # Patterns for unconditional exits
    EXIT_PATTERNS = {
        SourceLanguage.PYTHON: [
            r"^\s*return\b",
            r"^\s*raise\b",
            r"^\s*sys\.exit\s*\(",
            r"^\s*exit\s*\(",
        ],
        SourceLanguage.JAVASCRIPT: [
            r"^\s*return\b",
            r"^\s*throw\b",
            r"^\s*process\.exit\s*\(",
        ],
        SourceLanguage.SWIFT: [
            r"^\s*return\b",
            r"^\s*fatalError\s*\(",
            r"^\s*preconditionFailure\s*\(",
        ],
        SourceLanguage.C: [
            r"^\s*return\b",
            r"^\s*exit\s*\(",
            r"^\s*abort\s*\(",
        ],
    }

    # Patterns for always-true/false conditions
    TAUTOLOGY_PATTERNS = [
        (r"\btrue\b", True),
        (r"\bTrue\b", True),
        (r"\bfalse\b", False),
        (r"\bFalse\b", False),
        (r"\b1\s*==\s*1\b", True),
        (r"\b0\s*==\s*0\b", True),
        (r"\b1\s*!=\s*1\b", False),
        (r"\b0\s*!=\s*0\b", False),
        (r"\bnil\s*==\s*nil\b", True),
        (r"\bnull\s*===\s*null\b", True),
    ]

    @classmethod
    def analyze(cls, code: str, language: SourceLanguage) -> list:
        """Analyze code for unreachable states."""
        unreachable = []
        lines = code.split('\n')

        # Track state
        in_unconditional_exit = False
        exit_line = -1
        guard_stack = []  # Track nested guards for contradiction detection

        for i, line in enumerate(lines):
            line_num = i + 1

            # Skip empty lines and comments
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue

            # Check for dead code after unconditional exit
            if in_unconditional_exit:
                # Check if we're still at same or deeper indentation
                if cls._is_dead_code(line, lines, i):
                    unreachable.append(UnreachableState(
                        description=f"Code after unconditional exit",
                        line_number=line_num,
                        reason=f"Unreachable: follows return/raise at line {exit_line}",
                        category="dead_code"
                    ))
                else:
                    in_unconditional_exit = False

            # Check for unconditional exits
            if cls._is_unconditional_exit(stripped, language):
                in_unconditional_exit = True
                exit_line = line_num

            # Check for tautological conditions
            tautology = cls._check_tautology(stripped)
            if tautology is not None:
                if tautology:
                    unreachable.append(UnreachableState(
                        description=f"Condition is always true",
                        line_number=line_num,
                        reason="Tautological condition - else branch unreachable",
                        category="impossible_condition"
                    ))
                else:
                    unreachable.append(UnreachableState(
                        description=f"Condition is always false",
                        line_number=line_num,
                        reason="Contradictory condition - then branch unreachable",
                        category="impossible_condition"
                    ))

            # Track guards for contradiction detection
            guard = cls._extract_guard(stripped, language)
            if guard:
                contradiction = cls._check_contradiction(guard, guard_stack)
                if contradiction:
                    unreachable.append(UnreachableState(
                        description=f"Guard contradicts earlier guard",
                        line_number=line_num,
                        reason=f"Contradicts: {contradiction}",
                        category="contradictory_guards"
                    ))
                guard_stack.append((guard, line_num))

        return unreachable

    @classmethod
    def _is_unconditional_exit(cls, line: str, language: SourceLanguage) -> bool:
        """Check if line is an unconditional exit statement."""
        patterns = cls.EXIT_PATTERNS.get(language, cls.EXIT_PATTERNS[SourceLanguage.PYTHON])
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    @classmethod
    def _is_dead_code(cls, line: str, all_lines: list[str], current_idx: int) -> bool:
        """Check if current line is dead code based on indentation."""
        if not line.strip():
            return False

        # Get indentation of current line
        current_indent = len(line) - len(line.lstrip())

        # Look back for the exit statement
        for j in range(current_idx - 1, -1, -1):
            prev_line = all_lines[j]
            if not prev_line.strip():
                continue
            prev_indent = len(prev_line) - len(prev_line.lstrip())

            # If we found a line at same or less indentation, we're in a new block
            if prev_indent <= current_indent:
                # Check if it's the exit line or after it
                if 'return' in prev_line or 'raise' in prev_line or 'throw' in prev_line:
                    return True
                break

        return False

    @classmethod
    def _check_tautology(cls, line: str) -> Optional[bool]:
        """Check if a condition is tautological. Returns True/False/None."""
        # Look for if/while/guard conditions
        cond_match = re.search(r'(?:if|while|guard)\s*[(\s](.+?)(?:[):\{]|$)', line)
        if not cond_match:
            return None

        condition = cond_match.group(1).strip()

        for pattern, value in cls.TAUTOLOGY_PATTERNS:
            if re.search(pattern, condition, re.IGNORECASE):
                return value

        return None

    @classmethod
    def _extract_guard(cls, line: str, language: SourceLanguage) -> Optional[str]:
        """Extract guard condition from line."""
        patterns = [
            r'if\s*\((.+?)\)',
            r'if\s+(.+?):',
            r'guard\s+(.+?)\s+else',
            r'while\s*\((.+?)\)',
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1).strip()

        return None

    @classmethod
    def _check_contradiction(cls, new_guard: str, existing_guards: list) -> Optional[str]:
        """Check if new guard contradicts existing guards."""
        # Simple contradiction detection based on negation
        for existing, line_num in existing_guards:
            # Check for direct negation patterns
            if cls._is_negation(new_guard, existing):
                return f"{existing} (line {line_num})"

        return None

    @classmethod
    def _is_negation(cls, a: str, b: str) -> bool:
        """Check if a is the negation of b."""
        # Normalize both
        a = a.strip().lower()
        b = b.strip().lower()

        # Simple negation patterns - check if the operators are negations of each other
        negation_ops = [
            ('>', '<='),
            ('<', '>='),
            ('==', '!='),
        ]

        for op1, op2 in negation_ops:
            # Check if a has op1 and b has op2 (or vice versa) with same operands
            for pattern_op in [op1, op2]:
                other_op = op2 if pattern_op == op1 else op1
                pattern = rf"(\w+)\s*{re.escape(pattern_op)}\s*(\w+)"
                other_pattern = rf"(\w+)\s*{re.escape(other_op)}\s*(\w+)"
                
                match_a = re.match(pattern, a)
                match_b = re.match(other_pattern, b)
                
                if match_a and match_b:
                    # Check if the operands are the same
                    if match_a.groups() == match_b.groups():
                        return True

        # Check for explicit not
        if a == f"not {b}" or b == f"not {a}":
            return True
        if a == f"!{b}" or b == f"!{a}":
            return True

        return False


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

        # Handle comparison operators using regex to avoid partial replacements
        # Build a regex pattern that matches all operators (longest first)
        ops_sorted = sorted(cls.COMPARISON_OPS.keys(), key=len, reverse=True)
        ops_pattern = '|'.join(re.escape(op) for op in ops_sorted)
        
        def replace_op(match):
            code_op = match.group(0)
            newton_op = cls.COMPARISON_OPS[code_op]
            return f" {newton_op} "
        
        normalized = re.sub(ops_pattern, replace_op, normalized)

        # Handle logical operators with proper precedence
        # Wrap NOT targets in parentheses for precedence clarity (Python 'not' keyword only)
        # Note: C-style '!x' is already handled above as 'IS FALSY' for truthiness checks
        normalized = re.sub(r"\bnot\s+(\w+)", r"NOT(\1)", normalized, flags=re.IGNORECASE)

        # Then handle binary logical operators
        for code_op, newton_op in [("&&", "AND"), ("||", "OR"), ("and", "AND"), ("or", "OR")]:
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

            # Only convert to ratio form when RHS is a variable (not a numeric literal)
            # This prevents division by zero (e.g., "balance >= 0" should NOT become "balance / 0 >= 1.0")
            is_variable = right.isidentifier() and not right.isdigit() and not right.replace('.', '').isdigit()

            if is_variable:
                # Convert to ratio form when appropriate
                if op == "<=":
                    return f"{left} / {right} <= 1.0"
                elif op == ">=":
                    return f"{left} / {right} >= 1.0"
                elif op == "<":
                    return f"{left} / {right} < 1.0"
                elif op == ">":
                    return f"{left} / {right} > 1.0"
            else:
                # Keep as direct comparison for numeric literals
                return f"{left} {op} {right}"

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
        self._unreachable: list[UnreachableState] = []
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

        # Run CFG analysis for unreachable state detection
        self._unreachable = ControlFlowAnalyzer.analyze(self.code, self.language)

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

    def get_unreachable(self) -> list[UnreachableState]:
        """Get unreachable states detected via CFG analysis."""
        if not self._analyzed:
            self.analyze()
        return self._unreachable

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
        if self._unreachable:
            warnings.append(f"Detected {len(self._unreachable)} unreachable state(s)")

        return NewtonCartridge(
            source_language=self.language.value,
            source_snippet=self.code,
            constraints=self._constraints,
            functions_analyzed=self._functions,
            forbidden_states=forbidden_states[:10],  # Limit to top 10
            required_invariants=invariants[:10],
            unreachable_states=self._unreachable,
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
    "version": "1.1.0",
    "description": "Newton Code Constraint Compiler - extracts guards, invariants, constraints, and unreachable states from source code",
    "supported_languages": [lang.value for lang in SourceLanguage if lang != SourceLanguage.UNKNOWN],
    "constraint_kinds": [kind.value for kind in ConstraintKind],
    "features": [
        "Guard condition extraction",
        "Assertion analysis",
        "Early exit detection",
        "Null/nil check recognition",
        "Exception/error path analysis",
        "CFG-based unreachable state detection",
        "Dead code detection",
        "Contradictory guard detection",
        "Tautological condition detection",
        "Newton cartridge generation",
        "CDL output format",
        "Multi-language support"
    ],
    "tree_sitter_available": TREE_SITTER_AVAILABLE
}
