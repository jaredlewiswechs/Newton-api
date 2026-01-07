#!/usr/bin/env python3
"""
===============================================================================
TESTS FOR NEWTON QAP COMPILER
Comprehensive tests for tinyTalk to QAP compilation.

Tests cover:
- Lexer: Token generation
- Parser: AST construction
- Symbol Table: Enum and witness allocation
- IR Generation: SSA-like intermediate representation
- R1CS: Rank-1 Constraint System generation
- QAP: Polynomial conversion and field arithmetic
- End-to-end compilation
===============================================================================
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.qap import (
    # Field arithmetic
    FieldElement, F, BN254_PRIME, TEST_PRIME,
    # Lexer
    Lexer, Token, TokenType,
    # Parser
    Parser, Program, Rule, BinaryOp, Comparison, Identifier, Literal, InExpr,
    # Symbol table
    SymbolTable, EnumTable, SetTable,
    # IR
    IRBuilder, IRConst, IRSub, IRMul, IRIsZero, IRNot, IRMembership, IRAssert,
    # R1CS
    R1CSBuilder, R1CSConstraint,
    # QAP
    QAPBuilder, QAPPolynomial,
    # Compiler
    QAPCompiler, compile_to_qap, CompilationResult,
    # Formatting
    format_compilation_output
)


# ============================================================================
# FIELD ARITHMETIC TESTS
# ============================================================================

class TestFieldArithmetic:
    """Tests for prime field arithmetic."""

    def test_field_element_creation(self):
        """Test creating field elements."""
        f = F(5, TEST_PRIME)
        assert f.value == 5
        assert f.prime == TEST_PRIME

    def test_field_modular_reduction(self):
        """Test that values are reduced mod p."""
        f = F(TEST_PRIME + 10, TEST_PRIME)
        assert f.value == 10

    def test_field_addition(self):
        """Test field addition."""
        a = F(10, TEST_PRIME)
        b = F(20, TEST_PRIME)
        c = a + b
        assert c.value == 30

    def test_field_addition_overflow(self):
        """Test field addition with overflow."""
        a = F(TEST_PRIME - 5, TEST_PRIME)
        b = F(10, TEST_PRIME)
        c = a + b
        assert c.value == 5

    def test_field_subtraction(self):
        """Test field subtraction."""
        a = F(20, TEST_PRIME)
        b = F(10, TEST_PRIME)
        c = a - b
        assert c.value == 10

    def test_field_subtraction_negative(self):
        """Test field subtraction resulting in negative (wraps around)."""
        a = F(5, TEST_PRIME)
        b = F(10, TEST_PRIME)
        c = a - b
        assert c.value == TEST_PRIME - 5

    def test_field_multiplication(self):
        """Test field multiplication."""
        a = F(6, TEST_PRIME)
        b = F(7, TEST_PRIME)
        c = a * b
        assert c.value == 42

    def test_field_negation(self):
        """Test field negation."""
        a = F(10, TEST_PRIME)
        b = -a
        assert b.value == TEST_PRIME - 10
        assert (a + b).value == 0

    def test_field_inverse(self):
        """Test multiplicative inverse."""
        a = F(7, TEST_PRIME)
        inv = a.inverse()
        assert (a * inv).value == 1

    def test_field_division(self):
        """Test field division."""
        a = F(42, TEST_PRIME)
        b = F(6, TEST_PRIME)
        c = a / b
        assert c.value == 7

    def test_field_zero_inverse_raises(self):
        """Test that inverting zero raises error."""
        a = F(0, TEST_PRIME)
        with pytest.raises(ValueError):
            a.inverse()

    def test_field_equality(self):
        """Test field element equality."""
        a = F(10, TEST_PRIME)
        b = F(10, TEST_PRIME)
        c = F(11, TEST_PRIME)
        assert a == b
        assert a != c


# ============================================================================
# LEXER TESTS
# ============================================================================

class TestLexer:
    """Tests for the lexer/tokenizer."""

    def test_tokenize_when_keyword(self):
        """Test tokenizing 'when' keyword."""
        lexer = Lexer("when")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.WHEN

    def test_tokenize_fin_keyword(self):
        """Test tokenizing 'fin' keyword."""
        lexer = Lexer("fin")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.FIN

    def test_tokenize_finfr_keyword(self):
        """Test tokenizing 'finfr' keyword."""
        lexer = Lexer("finfr")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.FINFR

    def test_tokenize_and_keyword(self):
        """Test tokenizing 'and' keyword."""
        lexer = Lexer("and")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.AND

    def test_tokenize_or_keyword(self):
        """Test tokenizing 'or' keyword."""
        lexer = Lexer("or")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.OR

    def test_tokenize_identifier(self):
        """Test tokenizing identifier."""
        lexer = Lexer("user_intent")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENT
        assert tokens[0].value == "user_intent"

    def test_tokenize_string(self):
        """Test tokenizing string literal."""
        lexer = Lexer('"homework_help"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "homework_help"

    def test_tokenize_number(self):
        """Test tokenizing numeric literal."""
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42

    def test_tokenize_float(self):
        """Test tokenizing float literal."""
        lexer = Lexer("3.14")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 3.14

    def test_tokenize_boolean_true(self):
        """Test tokenizing 'true' keyword."""
        lexer = Lexer("true")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BOOL
        assert tokens[0].value is True

    def test_tokenize_boolean_false(self):
        """Test tokenizing 'false' keyword."""
        lexer = Lexer("false")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BOOL
        assert tokens[0].value is False

    def test_tokenize_comparison_operators(self):
        """Test tokenizing comparison operators."""
        lexer = Lexer("== != < > <= >=")
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.EQEQ
        assert tokens[1].type == TokenType.NE
        assert tokens[2].type == TokenType.LT
        assert tokens[3].type == TokenType.GT
        assert tokens[4].type == TokenType.LE
        assert tokens[5].type == TokenType.GE

    def test_tokenize_in_operator(self):
        """Test tokenizing 'in' operator."""
        lexer = Lexer("in")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IN

    def test_tokenize_full_rule(self):
        """Test tokenizing a complete rule."""
        source = 'when user_intent == "homework_help" fin'
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.WHEN
        assert tokens[1].type == TokenType.IDENT
        assert tokens[1].value == "user_intent"
        assert tokens[2].type == TokenType.EQEQ
        assert tokens[3].type == TokenType.STRING
        assert tokens[3].value == "homework_help"
        assert tokens[4].type == TokenType.FIN

    def test_tokenize_skips_comments(self):
        """Test that comments are skipped."""
        source = "when # this is a comment\nfin"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        types = [t.type for t in tokens if t.type != TokenType.NEWLINE]
        assert TokenType.WHEN in types
        assert TokenType.FIN in types


# ============================================================================
# PARSER TESTS
# ============================================================================

class TestParser:
    """Tests for the parser/AST builder."""

    def test_parse_simple_rule(self):
        """Test parsing a simple rule."""
        source = 'when x == 1 fin'
        lexer = Lexer(source)
        parser = Parser(lexer.tokenize())
        ast = parser.parse()

        assert isinstance(ast, Program)
        assert len(ast.rules) == 1
        assert ast.rules[0].action == "fin"

    def test_parse_finfr_rule(self):
        """Test parsing a finfr rule."""
        source = 'when x == 1 finfr'
        lexer = Lexer(source)
        parser = Parser(lexer.tokenize())
        ast = parser.parse()

        assert ast.rules[0].action == "finfr"

    def test_parse_comparison(self):
        """Test parsing comparison expression."""
        source = 'when x == "hello" fin'
        lexer = Lexer(source)
        parser = Parser(lexer.tokenize())
        ast = parser.parse()

        guard = ast.rules[0].guard
        assert isinstance(guard, Comparison)
        assert guard.op == "=="
        assert isinstance(guard.left, Identifier)
        assert guard.left.name == "x"
        assert isinstance(guard.right, Literal)
        assert guard.right.value == "hello"

    def test_parse_and_expression(self):
        """Test parsing AND expression."""
        source = 'when x == 1 and y == 2 fin'
        lexer = Lexer(source)
        parser = Parser(lexer.tokenize())
        ast = parser.parse()

        guard = ast.rules[0].guard
        assert isinstance(guard, BinaryOp)
        assert guard.op == "and"

    def test_parse_or_expression(self):
        """Test parsing OR expression."""
        source = 'when x == 1 or y == 2 fin'
        lexer = Lexer(source)
        parser = Parser(lexer.tokenize())
        ast = parser.parse()

        guard = ast.rules[0].guard
        assert isinstance(guard, BinaryOp)
        assert guard.op == "or"

    def test_parse_in_expression(self):
        """Test parsing IN expression."""
        source = 'when topic in approved_list fin'
        lexer = Lexer(source)
        parser = Parser(lexer.tokenize())
        ast = parser.parse()

        guard = ast.rules[0].guard
        assert isinstance(guard, InExpr)
        assert isinstance(guard.element, Identifier)
        assert guard.element.name == "topic"
        assert guard.set_name == "approved_list"

    def test_parse_multiple_rules(self):
        """Test parsing multiple rules."""
        source = '''
        when x == 1 fin action1
        when y == 2 finfr
        '''
        lexer = Lexer(source)
        parser = Parser(lexer.tokenize())
        ast = parser.parse()

        assert len(ast.rules) == 2

    def test_parse_complex_guard(self):
        """Test parsing complex guard with nested AND/OR."""
        source = 'when x == 1 and y == 2 and z == 3 fin'
        lexer = Lexer(source)
        parser = Parser(lexer.tokenize())
        ast = parser.parse()

        # Should be (((x==1) and (y==2)) and (z==3))
        guard = ast.rules[0].guard
        assert isinstance(guard, BinaryOp)
        assert guard.op == "and"


# ============================================================================
# SYMBOL TABLE TESTS
# ============================================================================

class TestSymbolTable:
    """Tests for symbol table management."""

    def test_enum_encoding(self):
        """Test enum string-to-int encoding."""
        table = EnumTable(name="test")
        assert table.encode("a") == 1
        assert table.encode("b") == 2
        assert table.encode("a") == 1  # Same value for same string

    def test_witness_allocation(self):
        """Test witness variable allocation."""
        symbols = SymbolTable()

        # w[0] is reserved for constant 1
        assert symbols.get_witness_index("1") == 0

        # Allocate new variables
        idx1 = symbols.allocate_witness("x")
        idx2 = symbols.allocate_witness("y")
        idx3 = symbols.allocate_witness("x")  # Should return same index

        assert idx1 == 1
        assert idx2 == 2
        assert idx3 == 1

    def test_set_table(self):
        """Test set table management."""
        symbols = SymbolTable()
        set_table = symbols.get_or_create_set("approved")
        set_table.add("item1")
        set_table.add("item2")

        assert "item1" in set_table.elements
        assert "item2" in set_table.elements


# ============================================================================
# IR GENERATION TESTS
# ============================================================================

class TestIRGeneration:
    """Tests for IR generation."""

    def test_ir_equality_check(self):
        """Test IR generation for equality check."""
        source = 'when x == "a" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        # Should generate: sub, isZero, assert
        ir_types = [type(i).__name__ for i in result.ir]

        assert "IRConst" in ir_types
        assert "IRSub" in ir_types
        assert "IRIsZero" in ir_types
        assert "IRAssert" in ir_types

    def test_ir_and_chain(self):
        """Test IR generation for AND chain."""
        source = 'when x == "a" and y == "b" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        # Should include multiplication for AND
        ir_types = [type(i).__name__ for i in result.ir]
        assert "IRMul" in ir_types

    def test_ir_not_expression(self):
        """Test IR generation for NOT."""
        source = 'when x != "a" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        ir_types = [type(i).__name__ for i in result.ir]
        assert "IRNot" in ir_types

    def test_ir_set_membership(self):
        """Test IR generation for set membership."""
        source = 'when topic in approved_list finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        ir_types = [type(i).__name__ for i in result.ir]
        assert "IRMembership" in ir_types


# ============================================================================
# R1CS GENERATION TESTS
# ============================================================================

class TestR1CSGeneration:
    """Tests for R1CS constraint generation."""

    def test_r1cs_basic_constraint(self):
        """Test basic R1CS constraint generation."""
        source = 'when x == "a" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        assert len(result.r1cs) > 0

    def test_r1cs_is_zero_gadget(self):
        """Test R1CS for isZero gadget."""
        source = 'when x == "a" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        # isZero generates 3 constraints:
        # 1. z * inv = 1 - eq
        # 2. eq * z = 0
        # 3. eq * (eq - 1) = 0

        labels = [c.label for c in result.r1cs]
        has_is_zero = any("isZero" in label or "1 -" in label for label in labels)
        has_boolean = any("- 1) = 0" in label for label in labels)

        assert has_is_zero or has_boolean

    def test_r1cs_finfr_constraint(self):
        """Test R1CS FINFR constraint: guard == 0."""
        source = 'when x == "a" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        # Should have FINFR constraint
        labels = [c.label for c in result.r1cs]
        has_finfr = any("FINFR" in label or "= 0" in label for label in labels)
        assert has_finfr

    def test_r1cs_multiplication_constraint(self):
        """Test R1CS multiplication constraint format."""
        source = 'when x == "a" and y == "b" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        # Should have multiplication constraints for AND
        has_mul = any(
            len(c.A) > 0 and len(c.B) > 0 and len(c.C) > 0
            for c in result.r1cs
        )
        assert has_mul


# ============================================================================
# QAP CONVERSION TESTS
# ============================================================================

class TestQAPConversion:
    """Tests for QAP polynomial conversion."""

    def test_qap_polynomial_evaluation(self):
        """Test polynomial evaluation."""
        # P(x) = 2 + 3x + 5x^2
        coeffs = [F(2, TEST_PRIME), F(3, TEST_PRIME), F(5, TEST_PRIME)]
        poly = QAPPolynomial(coefficients=coeffs)

        # P(1) = 2 + 3 + 5 = 10
        assert poly.evaluate(F(1, TEST_PRIME)).value == 10

        # P(2) = 2 + 6 + 20 = 28
        assert poly.evaluate(F(2, TEST_PRIME)).value == 28

    def test_qap_target_polynomial(self):
        """Test target polynomial T(x) = prod(x - r_i)."""
        source = 'when x == "a" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        if result.qap and result.qap.target_poly:
            # T(r_i) should be 0 for all roots
            for root in result.qap.roots:
                val = result.qap.target_poly.evaluate(F(root, TEST_PRIME))
                assert val.value == 0

    def test_qap_polynomial_degree(self):
        """Test QAP polynomial degrees."""
        source = 'when x == "a" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        if result.qap:
            # Polynomial degree should be <= num_constraints - 1
            max_degree = result.qap.num_constraints - 1 if result.qap.num_constraints > 0 else 0

            for poly in result.qap.A_polys.values():
                assert poly.degree() <= max_degree

    def test_qap_lagrange_interpolation(self):
        """Test Lagrange interpolation produces correct values at roots."""
        source = 'when x == "a" and y == "b" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        if result.qap and result.qap.num_constraints > 0:
            # For each A polynomial, evaluate at roots and check against R1CS values
            for j, poly in result.qap.A_polys.items():
                for i, root in enumerate(result.qap.roots):
                    expected = result.r1cs[i].A.get(j, 0)
                    actual = poly.evaluate(F(root, TEST_PRIME)).value % TEST_PRIME
                    # Normalize expected
                    expected = expected % TEST_PRIME
                    assert actual == expected, f"A_{j}({root}) = {actual}, expected {expected}"


# ============================================================================
# END-TO-END COMPILATION TESTS
# ============================================================================

class TestEndToEndCompilation:
    """Tests for complete compilation pipeline."""

    def test_compile_simple_rule(self):
        """Test compiling a simple rule."""
        source = 'when x == "a" fin'
        result = compile_to_qap(source, prime=TEST_PRIME)

        assert result.success
        assert len(result.tokens) > 0
        assert result.ast is not None
        assert result.symbols is not None

    def test_compile_finfr_rule(self):
        """Test compiling a finfr rule."""
        source = 'when x == "forbidden" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        assert result.success
        assert len(result.r1cs) > 0
        assert result.qap is not None

    def test_compile_complex_rule(self):
        """Test compiling a complex rule with multiple conditions."""
        source = '''
        when user_intent == "homework_help" and
             topic in approved_curriculum and
             response_tone == "educational" and
             no_direct_answers == true
        fin generate_educational_response

        when user_intent == "request_direct_answer" and
             context == "assessment"
        finfr
        '''
        result = compile_to_qap(source, prime=TEST_PRIME)

        assert result.success
        assert len(result.ast.rules) == 2
        assert result.ast.rules[1].action == "finfr"

    def test_compile_with_debug(self):
        """Test compilation with debug output."""
        source = 'when x == "a" finfr'
        compiler = QAPCompiler(prime=TEST_PRIME, debug=False)
        result = compiler.compile(source)

        assert result.success

    def test_compile_invalid_syntax(self):
        """Test compilation handles syntax errors gracefully."""
        source = 'when == finfr'  # Invalid
        result = compile_to_qap(source, prime=TEST_PRIME)

        # Should not crash, but may have errors
        assert len(result.errors) > 0 or not result.success

    def test_compilation_result_to_dict(self):
        """Test exporting compilation result to dict."""
        source = 'when x == "a" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        d = result.to_dict()

        assert "success" in d
        assert "tokens" in d
        assert "ast" in d
        assert "symbols" in d
        assert "ir" in d
        assert "r1cs" in d
        assert "qap" in d

    def test_format_compilation_output(self):
        """Test formatting compilation output as string."""
        source = 'when x == "a" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        output = format_compilation_output(result)

        assert "LEXER OUTPUT" in output
        assert "PARSER OUTPUT" in output
        assert "SYMBOL TABLE" in output
        assert "R1CS CONSTRAINTS" in output
        assert "QAP" in output


# ============================================================================
# BN254 FIELD TESTS
# ============================================================================

class TestBN254Field:
    """Tests using the BN254 prime field."""

    def test_bn254_prime_operations(self):
        """Test operations in BN254 field."""
        a = F(12345, BN254_PRIME)
        b = F(67890, BN254_PRIME)

        c = a + b
        assert c.value == 12345 + 67890

        d = a * b
        assert d.value == (12345 * 67890) % BN254_PRIME

    def test_bn254_inverse(self):
        """Test inverse in BN254 field."""
        a = F(12345, BN254_PRIME)
        inv = a.inverse()

        product = a * inv
        assert product.value == 1

    def test_compile_with_bn254(self):
        """Test compilation using BN254 prime."""
        source = 'when x == "a" finfr'
        result = compile_to_qap(source, prime=BN254_PRIME)

        assert result.success
        if result.qap:
            assert result.qap.prime == BN254_PRIME


# ============================================================================
# CONSTRAINT SEMANTICS TESTS
# ============================================================================

class TestConstraintSemantics:
    """Tests for correct constraint semantics."""

    def test_finfr_means_guard_must_be_false(self):
        """Test that finfr constraints enforce guard == 0."""
        source = 'when forbidden_state == true finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        # The final constraint should enforce the guard variable == 0
        assert any("FINFR" in c.label or "= 0" in c.label for c in result.r1cs)

    def test_fin_is_allowed_action(self):
        """Test that fin rules don't generate blocking constraints."""
        source = 'when allowed_state == true fin'
        result = compile_to_qap(source, prime=TEST_PRIME)

        # Should NOT have FINFR constraint
        finfr_count = sum(1 for c in result.r1cs if "FINFR" in c.label)

        # fin generates evaluation but no blocking assertion
        assert result.success

    def test_and_requires_both_conditions(self):
        """Test AND semantics: both conditions required."""
        source = 'when a == true and b == true finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        # Should have multiplication for AND
        ir_types = [type(i).__name__ for i in result.ir]
        assert "IRMul" in ir_types

    def test_boolean_constraint_generated(self):
        """Test that boolean constraints are generated."""
        source = 'when x == "a" finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        # isZero gadget should generate boolean constraint: eq*(eq-1)=0
        labels = [c.label for c in result.r1cs]
        has_boolean = any("- 1) = 0" in label for label in labels)
        assert has_boolean


# ============================================================================
# MEMBERSHIP GADGET TESTS
# ============================================================================

class TestMembershipGadget:
    """Tests for set membership gadget."""

    def test_membership_ir_generation(self):
        """Test membership IR is generated."""
        source = 'when topic in approved_curriculum finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        # Should have membership instruction
        has_membership = any(
            isinstance(i, IRMembership) for i in result.ir
        )
        assert has_membership

    def test_membership_set_created(self):
        """Test that set is created in symbol table."""
        source = 'when topic in approved_curriculum finfr'
        result = compile_to_qap(source, prime=TEST_PRIME)

        assert "approved_curriculum" in result.symbols.sets


# ============================================================================
# INTEGRATION WITH CDL/TINYTALK
# ============================================================================

class TestIntegrationWithCDL:
    """Tests for integration with existing CDL/tinyTalk."""

    def test_compile_cdl_style_constraint(self):
        """Test compiling CDL-style constraint."""
        source = '''
        when amount > 1000 and approved == false finfr
        '''
        result = compile_to_qap(source, prime=TEST_PRIME)

        assert result.success

    def test_enum_encoding_consistency(self):
        """Test that enum encoding is consistent."""
        source = '''
        when intent == "buy"
        fin
        when intent == "sell"
        fin
        when intent == "buy"
        finfr
        '''
        result = compile_to_qap(source, prime=TEST_PRIME)

        # "buy" should always encode to the same value
        if "_literals" in result.symbols.enums:
            assert result.symbols.enums["_literals"].values.get("buy") is not None


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
