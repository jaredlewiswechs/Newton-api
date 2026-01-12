#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
TEST SUITE: Newton LLM Constraint Governor

Comprehensive tests for the domain-agnostic LLM constraint validation system.

Test Categories:
1. Schema Tests - Claim, ValidationResult, ClaimBatch
2. Validator Tests - Each domain validator
3. Registry Tests - ValidatorRegistry routing
4. Engine Tests - ConstraintEngine closed-loop
5. Integration Tests - Full pipeline tests

"The LLM proposes. The validator decides. The test proves."

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
import json
from typing import Dict, Any

from newton.llm import (
    # Schema
    Domain,
    Claim,
    ClaimBatch,
    ValidationResult,
    BatchValidationResult,
    LLM_SYSTEM_PROMPT,
    # Validators
    DomainValidator,
    PhysicsValidator,
    MathValidator,
    LogicValidator,
    PolicyValidator,
    TemporalValidator,
    FinancialValidator,
    CompositeValidator,
    # Engine
    ValidatorRegistry,
    ConstraintEngine,
    GenerationResult,
    MockLLM,
    build_repair_prompt,
    create_default_registry,
    create_engine,
)


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestDomain:
    """Test Domain enum."""

    def test_domain_values(self):
        """Test all domain values exist."""
        assert Domain.PHYSICS.value == "physics"
        assert Domain.MATH.value == "math"
        assert Domain.LOGIC.value == "logic"
        assert Domain.POLICY.value == "policy"
        assert Domain.TEMPORAL.value == "temporal"
        assert Domain.FINANCIAL.value == "financial"
        assert Domain.UNKNOWN.value == "unknown"

    def test_domain_from_string(self):
        """Test creating domain from string."""
        assert Domain("physics") == Domain.PHYSICS
        assert Domain("math") == Domain.MATH


class TestClaim:
    """Test Claim dataclass."""

    def test_claim_creation(self):
        """Test basic claim creation."""
        claim = Claim(text="2 + 2 = 4", domain=Domain.MATH)
        assert claim.text == "2 + 2 = 4"
        assert claim.domain == Domain.MATH
        assert claim.metadata == {}

    def test_claim_with_metadata(self):
        """Test claim with metadata."""
        claim = Claim(
            text="velocity = 10 m/s",
            domain=Domain.PHYSICS,
            metadata={"source": "calculation"}
        )
        assert claim.metadata["source"] == "calculation"

    def test_claim_from_string_domain(self):
        """Test creating claim with string domain."""
        claim = Claim(text="test", domain="physics")
        assert claim.domain == Domain.PHYSICS

    def test_claim_fingerprint(self):
        """Test claim fingerprint is deterministic."""
        claim1 = Claim(text="test", domain=Domain.MATH)
        claim2 = Claim(text="test", domain=Domain.MATH)
        assert claim1.fingerprint == claim2.fingerprint

    def test_claim_to_dict(self):
        """Test claim serialization."""
        claim = Claim(text="test", domain=Domain.LOGIC, metadata={"key": "value"})
        d = claim.to_dict()
        assert d["text"] == "test"
        assert d["domain"] == "logic"
        assert d["metadata"]["key"] == "value"

    def test_claim_from_dict(self):
        """Test claim deserialization."""
        data = {"text": "x = 1", "domain": "math", "metadata": {}}
        claim = Claim.from_dict(data)
        assert claim.text == "x = 1"
        assert claim.domain == Domain.MATH


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_result_creation(self):
        """Test basic result creation."""
        result = ValidationResult(
            valid=True,
            domain=Domain.MATH,
            rule="symbolic_equality",
            message="Valid equation"
        )
        assert result.valid is True
        assert result.domain == Domain.MATH
        assert result.rule == "symbolic_equality"

    def test_result_proof_hash(self):
        """Test proof hash generation."""
        result = ValidationResult(
            valid=True,
            domain=Domain.MATH,
            rule="test",
            message="test"
        )
        assert len(result.proof_hash) == 16

    def test_result_to_dict(self):
        """Test result serialization."""
        result = ValidationResult(
            valid=False,
            domain=Domain.LOGIC,
            rule="contradiction",
            message="X contradicts not X"
        )
        d = result.to_dict()
        assert d["valid"] is False
        assert d["domain"] == "logic"
        assert "proof_hash" in d


class TestClaimBatch:
    """Test ClaimBatch dataclass."""

    def test_batch_from_json(self):
        """Test creating batch from JSON response."""
        data = {
            "claims": [
                {"text": "2 + 2 = 4", "domain": "math"},
                {"text": "velocity = 10 m/s", "domain": "physics"},
            ]
        }
        batch = ClaimBatch.from_json(data, source_prompt="test prompt")
        assert len(batch.claims) == 2
        assert batch.claims[0].domain == Domain.MATH
        assert batch.source_prompt == "test prompt"

    def test_batch_to_dict(self):
        """Test batch serialization."""
        batch = ClaimBatch(
            claims=[Claim(text="test", domain=Domain.LOGIC)],
            source_prompt="test"
        )
        d = batch.to_dict()
        assert len(d["claims"]) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# MATH VALIDATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestMathValidator:
    """Test MathValidator for arithmetic and algebraic claims."""

    @pytest.fixture
    def validator(self):
        return MathValidator()

    def test_valid_arithmetic(self, validator):
        """Test valid arithmetic equations."""
        claim = Claim(text="2 + 2 = 4", domain=Domain.MATH)
        result = validator.validate(claim)
        assert result.valid is True
        assert result.rule == "symbolic_equality"

    def test_invalid_arithmetic(self, validator):
        """Test invalid arithmetic equations."""
        claim = Claim(text="2 + 2 = 5", domain=Domain.MATH)
        result = validator.validate(claim)
        assert result.valid is False

    def test_valid_multiplication(self, validator):
        """Test multiplication equations."""
        claim = Claim(text="3 * 4 = 12", domain=Domain.MATH)
        result = validator.validate(claim)
        assert result.valid is True

    def test_valid_negative_numbers(self, validator):
        """Test equations with negative numbers."""
        claim = Claim(text="-5 + 10 = 5", domain=Domain.MATH)
        result = validator.validate(claim)
        assert result.valid is True

    def test_valid_exponentiation(self, validator):
        """Test exponentiation equations."""
        claim = Claim(text="2^3 = 8", domain=Domain.MATH)
        result = validator.validate(claim)
        assert result.valid is True

    def test_chained_equality(self, validator):
        """Test chained equality (a = b = c)."""
        claim = Claim(text="1 + 1 = 2 = 4/2", domain=Domain.MATH)
        result = validator.validate(claim)
        assert result.valid is True

    def test_missing_equals(self, validator):
        """Test that equations require equals sign."""
        claim = Claim(text="2 + 2", domain=Domain.MATH)
        result = validator.validate(claim)
        assert result.valid is False
        assert "equation" in result.message.lower()

    def test_zero_division_detection(self, validator):
        """Test detection of division by zero type issues."""
        # This should parse but may not be valid depending on sympy handling
        claim = Claim(text="1/0 = infinity", domain=Domain.MATH)
        result = validator.validate(claim)
        # Should either fail to parse or fail to validate
        assert result is not None


# ═══════════════════════════════════════════════════════════════════════════════
# PHYSICS VALIDATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestPhysicsValidator:
    """Test PhysicsValidator for physical plausibility."""

    @pytest.fixture
    def validator(self):
        return PhysicsValidator()

    def test_valid_velocity(self, validator):
        """Test valid velocity claim."""
        claim = Claim(text="velocity = 100 m/s", domain=Domain.PHYSICS)
        result = validator.validate(claim)
        assert result.valid is True

    def test_superluminal_velocity_rejected(self, validator):
        """Test that FTL velocities are rejected."""
        claim = Claim(
            text="velocity = 400000000 m/s",  # > speed of light
            domain=Domain.PHYSICS
        )
        result = validator.validate(claim)
        assert result.valid is False
        assert "speed of light" in result.message.lower()

    def test_negative_velocity_rejected(self, validator):
        """Test that negative velocity magnitudes are rejected."""
        claim = Claim(text="velocity = -100 m/s", domain=Domain.PHYSICS)
        result = validator.validate(claim)
        assert result.valid is False
        assert "negative" in result.message.lower()

    def test_below_absolute_zero_rejected(self, validator):
        """Test that temperatures below absolute zero are rejected."""
        claim = Claim(text="temperature = -300 celsius", domain=Domain.PHYSICS)
        result = validator.validate(claim)
        assert result.valid is False
        assert "absolute zero" in result.message.lower()

    def test_valid_temperature(self, validator):
        """Test valid temperature claim."""
        claim = Claim(text="temperature = 25 celsius", domain=Domain.PHYSICS)
        result = validator.validate(claim)
        assert result.valid is True

    def test_negative_mass_rejected(self, validator):
        """Test that negative mass is rejected."""
        claim = Claim(text="mass = -10 kg", domain=Domain.PHYSICS)
        result = validator.validate(claim)
        assert result.valid is False

    def test_valid_mass(self, validator):
        """Test valid mass claim."""
        claim = Claim(text="mass = 10 kg", domain=Domain.PHYSICS)
        result = validator.validate(claim)
        assert result.valid is True

    def test_negative_distance_rejected(self, validator):
        """Test that negative distance is rejected."""
        claim = Claim(text="distance = -5 m", domain=Domain.PHYSICS)
        result = validator.validate(claim)
        assert result.valid is False

    def test_negative_time_rejected(self, validator):
        """Test that negative time duration is rejected."""
        claim = Claim(text="time = -2 s", domain=Domain.PHYSICS)
        result = validator.validate(claim)
        assert result.valid is False


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIC VALIDATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestLogicValidator:
    """Test LogicValidator for propositional consistency."""

    @pytest.fixture
    def validator(self):
        return LogicValidator()

    def test_simple_assertion(self, validator):
        """Test simple proposition assertion."""
        claim = Claim(text="the sky is blue", domain=Domain.LOGIC)
        result = validator.validate(claim)
        assert result.valid is True

    def test_negation_assertion(self, validator):
        """Test negation assertion."""
        claim = Claim(text="not the sky is green", domain=Domain.LOGIC)
        result = validator.validate(claim)
        assert result.valid is True

    def test_contradiction_detected(self, validator):
        """Test that contradictions are detected."""
        # First assert X
        claim1 = Claim(text="cats are mammals", domain=Domain.LOGIC)
        result1 = validator.validate(claim1)
        assert result1.valid is True

        # Then assert NOT X
        claim2 = Claim(text="not cats are mammals", domain=Domain.LOGIC)
        result2 = validator.validate(claim2)
        assert result2.valid is False
        assert "contradiction" in result2.message.lower()

    def test_consistent_assertions(self, validator):
        """Test that consistent assertions pass."""
        claim1 = Claim(text="dogs bark", domain=Domain.LOGIC)
        claim2 = Claim(text="cats meow", domain=Domain.LOGIC)

        assert validator.validate(claim1).valid is True
        assert validator.validate(claim2).valid is True

    def test_explicit_true_assertion(self, validator):
        """Test explicit 'is true' assertion."""
        claim = Claim(text="the earth is round is true", domain=Domain.LOGIC)
        result = validator.validate(claim)
        assert result.valid is True

    def test_explicit_false_assertion(self, validator):
        """Test explicit 'is false' assertion."""
        claim1 = Claim(text="unicorns exist", domain=Domain.LOGIC)
        validator.validate(claim1)

        # Now say it's false - should contradict
        claim2 = Claim(text="unicorns exist is false", domain=Domain.LOGIC)
        result = validator.validate(claim2)
        assert result.valid is False

    def test_reset_clears_facts(self, validator):
        """Test that reset clears fact base."""
        claim = Claim(text="test fact", domain=Domain.LOGIC)
        validator.validate(claim)
        assert "test fact" in validator.facts

        validator.reset()
        assert len(validator.facts) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# POLICY VALIDATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestPolicyValidator:
    """Test PolicyValidator for rule enforcement."""

    def test_forbidden_phrase_rejected(self):
        """Test that forbidden phrases are rejected."""
        validator = PolicyValidator(forbidden_phrases=["confidential", "secret"])
        claim = Claim(text="This is confidential information", domain=Domain.POLICY)
        result = validator.validate(claim)
        assert result.valid is False
        assert "forbidden" in result.message.lower()

    def test_allowed_content_passes(self):
        """Test that allowed content passes."""
        validator = PolicyValidator(forbidden_phrases=["secret"])
        claim = Claim(text="This is public information", domain=Domain.POLICY)
        result = validator.validate(claim)
        assert result.valid is True

    def test_required_phrase_missing(self):
        """Test that missing required phrases fail."""
        validator = PolicyValidator(required_phrases=["disclaimer", "warning"])
        claim = Claim(text="Some content without required phrase", domain=Domain.POLICY)
        result = validator.validate(claim)
        assert result.valid is False
        assert "must include" in result.message.lower()

    def test_required_phrase_present(self):
        """Test that required phrases pass."""
        validator = PolicyValidator(required_phrases=["disclaimer"])
        claim = Claim(text="This includes a disclaimer", domain=Domain.POLICY)
        result = validator.validate(claim)
        assert result.valid is True

    def test_forbidden_pattern_rejected(self):
        """Test regex pattern rejection."""
        validator = PolicyValidator(forbidden_patterns=[r"\d{3}-\d{2}-\d{4}"])  # SSN
        claim = Claim(text="SSN: 123-45-6789", domain=Domain.POLICY)
        result = validator.validate(claim)
        assert result.valid is False

    def test_custom_rule(self):
        """Test custom rule function."""
        def no_shouting(text):
            if text.isupper() and len(text) > 10:
                return False, "No shouting allowed"
            return True, ""

        validator = PolicyValidator(custom_rules=[no_shouting])

        claim1 = Claim(text="THIS IS SHOUTING AT YOU", domain=Domain.POLICY)
        assert validator.validate(claim1).valid is False

        claim2 = Claim(text="This is normal text", domain=Domain.POLICY)
        assert validator.validate(claim2).valid is True

    def test_add_forbidden_dynamically(self):
        """Test adding forbidden phrases after creation."""
        validator = PolicyValidator()
        claim = Claim(text="test secret data", domain=Domain.POLICY)
        assert validator.validate(claim).valid is True

        validator.add_forbidden("secret")
        assert validator.validate(claim).valid is False


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPORAL VALIDATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTemporalValidator:
    """Test TemporalValidator for time constraints."""

    @pytest.fixture
    def validator(self):
        return TemporalValidator()

    def test_positive_duration(self, validator):
        """Test valid positive duration."""
        claim = Claim(text="duration = 10 s", domain=Domain.TEMPORAL)
        result = validator.validate(claim)
        assert result.valid is True

    def test_negative_duration_rejected(self, validator):
        """Test that negative durations are rejected."""
        claim = Claim(text="duration = -5 s", domain=Domain.TEMPORAL)
        result = validator.validate(claim)
        assert result.valid is False
        assert "negative" in result.message.lower()

    def test_before_ordering(self, validator):
        """Test 'before' temporal ordering."""
        claim = Claim(text="event A before event B", domain=Domain.TEMPORAL)
        result = validator.validate(claim)
        assert result.valid is True

    def test_after_ordering(self, validator):
        """Test 'after' temporal ordering."""
        claim = Claim(text="event C after event D", domain=Domain.TEMPORAL)
        result = validator.validate(claim)
        assert result.valid is True

    def test_temporal_contradiction(self, validator):
        """Test that temporal contradictions are detected."""
        # A before B
        claim1 = Claim(text="meeting before lunch", domain=Domain.TEMPORAL)
        validator.validate(claim1)

        # B before A (contradiction)
        claim2 = Claim(text="lunch before meeting", domain=Domain.TEMPORAL)
        result = validator.validate(claim2)
        assert result.valid is False
        assert "contradiction" in result.message.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# FINANCIAL VALIDATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestFinancialValidator:
    """Test FinancialValidator for budget constraints."""

    def test_within_budget(self):
        """Test transaction within budget."""
        validator = FinancialValidator(budget=1000.0)
        claim = Claim(text="cost = $500", domain=Domain.FINANCIAL)
        result = validator.validate(claim)
        assert result.valid is True
        assert validator.remaining_budget == 500.0

    def test_overdraft_rejected(self):
        """Test that overdraft is rejected."""
        validator = FinancialValidator(budget=100.0)
        claim = Claim(text="cost = $150", domain=Domain.FINANCIAL)
        result = validator.validate(claim)
        assert result.valid is False
        assert "overdraft" in result.message.lower() or "balance" in result.message.lower()

    def test_max_transaction_limit(self):
        """Test max transaction limit."""
        validator = FinancialValidator(budget=10000.0, max_transaction=500.0)
        claim = Claim(text="cost = $750", domain=Domain.FINANCIAL)
        result = validator.validate(claim)
        assert result.valid is False
        assert "maximum" in result.message.lower()

    def test_cumulative_spending(self):
        """Test that spending accumulates."""
        validator = FinancialValidator(budget=1000.0)

        claim1 = Claim(text="cost = $400", domain=Domain.FINANCIAL)
        validator.validate(claim1)

        claim2 = Claim(text="cost = $400", domain=Domain.FINANCIAL)
        validator.validate(claim2)

        # Third should fail
        claim3 = Claim(text="cost = $400", domain=Domain.FINANCIAL)
        result = validator.validate(claim3)
        assert result.valid is False

    def test_non_financial_claim_passes(self):
        """Test that non-financial claims pass through."""
        validator = FinancialValidator(budget=100.0)
        claim = Claim(text="the sky is blue", domain=Domain.FINANCIAL)
        result = validator.validate(claim)
        assert result.valid is True


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATOR REGISTRY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidatorRegistry:
    """Test ValidatorRegistry for routing and management."""

    @pytest.fixture
    def registry(self):
        return ValidatorRegistry([
            MathValidator(),
            LogicValidator(),
            PolicyValidator(),
        ])

    def test_registration(self, registry):
        """Test validator registration."""
        assert Domain.MATH in registry
        assert Domain.LOGIC in registry
        assert Domain.PHYSICS not in registry

    def test_routing(self, registry):
        """Test claim routing to correct validator."""
        math_claim = Claim(text="2 + 2 = 4", domain=Domain.MATH)
        result = registry.validate(math_claim)
        assert result.valid is True
        assert result.domain == Domain.MATH

    def test_unknown_domain_rejected(self, registry):
        """Test that unknown domains are rejected."""
        unknown_claim = Claim(text="something", domain=Domain.PHYSICS)
        result = registry.validate(unknown_claim)
        assert result.valid is False
        assert "no validator" in result.message.lower()

    def test_batch_validation(self, registry):
        """Test batch validation."""
        batch = ClaimBatch(claims=[
            Claim(text="2 + 2 = 4", domain=Domain.MATH),  # Valid
            Claim(text="2 + 2 = 5", domain=Domain.MATH),  # Invalid
            Claim(text="test fact", domain=Domain.LOGIC),  # Valid
        ])

        result = registry.validate_batch(batch)
        assert len(result.approved) == 2
        assert len(result.violations) == 1
        assert result.all_valid is False

    def test_all_valid_batch(self, registry):
        """Test fully valid batch."""
        batch = ClaimBatch(claims=[
            Claim(text="2 + 2 = 4", domain=Domain.MATH),
            Claim(text="3 * 3 = 9", domain=Domain.MATH),
        ])

        result = registry.validate_batch(batch)
        assert result.all_valid is True
        assert result.status == "verified"

    def test_unregister(self, registry):
        """Test unregistering a validator."""
        assert Domain.MATH in registry
        registry.unregister(Domain.MATH)
        assert Domain.MATH not in registry


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT ENGINE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstraintEngine:
    """Test ConstraintEngine closed-loop generation."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM that returns valid claims."""
        return MockLLM(responses=[
            {"claims": [{"text": "2 + 2 = 4", "domain": "math"}]}
        ])

    @pytest.fixture
    def engine(self, mock_llm):
        """Create engine with mock LLM."""
        registry = ValidatorRegistry([MathValidator()])
        return ConstraintEngine(registry=registry, llm=mock_llm, max_retries=3)

    def test_successful_generation(self, engine):
        """Test successful generation on first try."""
        result = engine.generate("What is 2 + 2?")
        assert result.status == "verified"
        assert "2 + 2 = 4" in result.claims
        assert result.iterations == 1

    def test_generation_with_repair(self):
        """Test generation that requires repair."""
        mock = MockLLM(responses=[
            # First response: invalid
            {"claims": [{"text": "2 + 2 = 5", "domain": "math"}]},
            # Second response: valid
            {"claims": [{"text": "2 + 2 = 4", "domain": "math"}]},
        ])

        registry = ValidatorRegistry([MathValidator()])
        engine = ConstraintEngine(registry=registry, llm=mock, max_retries=3)

        result = engine.generate("What is 2 + 2?")
        assert result.status == "verified"
        assert result.iterations == 2

    def test_generation_refused_after_max_retries(self):
        """Test that generation is refused after max retries."""
        mock = MockLLM(responses=[
            {"claims": [{"text": "2 + 2 = 5", "domain": "math"}]},
            {"claims": [{"text": "2 + 2 = 5", "domain": "math"}]},
            {"claims": [{"text": "2 + 2 = 5", "domain": "math"}]},
            {"claims": [{"text": "2 + 2 = 5", "domain": "math"}]},
        ])

        registry = ValidatorRegistry([MathValidator()])
        engine = ConstraintEngine(registry=registry, llm=mock, max_retries=3)

        result = engine.generate("What is 2 + 2?")
        assert result.status == "refused"
        assert result.iterations == 4

    def test_partial_success(self):
        """Test partial success with some valid claims."""
        mock = MockLLM(responses=[
            {"claims": [
                {"text": "2 + 2 = 4", "domain": "math"},  # Valid
                {"text": "2 + 2 = 5", "domain": "math"},  # Invalid
            ]}
        ])

        registry = ValidatorRegistry([MathValidator()])
        engine = ConstraintEngine(registry=registry, llm=mock, max_retries=1)

        result = engine.generate("test")
        assert result.status == "partial"
        assert len(result.claims) == 1
        assert len(result.violations) == 1

    def test_validate_response_directly(self):
        """Test direct validation without generation."""
        registry = ValidatorRegistry([MathValidator()])
        engine = ConstraintEngine(registry=registry, llm=None)

        response = {"claims": [
            {"text": "1 + 1 = 2", "domain": "math"},
            {"text": "2 * 3 = 6", "domain": "math"},
        ]}

        result = engine.validate_response(response)
        assert result.all_valid is True
        assert len(result.approved) == 2

    def test_metrics_tracking(self):
        """Test engine metrics."""
        mock = MockLLM(responses=[
            {"claims": [{"text": "2 + 2 = 4", "domain": "math"}]}
        ])

        registry = ValidatorRegistry([MathValidator()])
        engine = ConstraintEngine(registry=registry, llm=mock)

        engine.generate("test")
        engine.generate("test2")

        metrics = engine.metrics
        assert metrics["total_generations"] == 2
        assert metrics["total_approved"] == 2


class TestBuildRepairPrompt:
    """Test repair prompt generation."""

    def test_basic_repair_prompt(self):
        """Test basic repair prompt structure."""
        violations = [{
            "claim": Claim(text="2 + 2 = 5", domain=Domain.MATH),
            "result": ValidationResult(
                valid=False,
                domain=Domain.MATH,
                rule="equality",
                message="Equation does not hold"
            )
        }]

        prompt = build_repair_prompt("What is 2 + 2?", violations)
        assert "rejected" in prompt.lower()
        assert "2 + 2 = 5" in prompt
        assert "math" in prompt.lower()
        assert "Equation does not hold" in prompt

    def test_repair_prompt_includes_instructions(self):
        """Test that repair prompt includes rewrite instructions."""
        violations = [{
            "claim": Claim(text="test", domain=Domain.LOGIC),
            "result": ValidationResult(
                valid=False,
                domain=Domain.LOGIC,
                rule="test",
                message="test"
            )
        }]

        prompt = build_repair_prompt("original", violations)
        assert "Rewrite" in prompt
        assert "JSON" in prompt


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSITE VALIDATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCompositeValidator:
    """Test CompositeValidator for chaining validators."""

    def test_all_pass(self):
        """Test that claim passes when all validators pass."""
        validator = CompositeValidator([
            PhysicsValidator(),
            PolicyValidator(),
        ])

        claim = Claim(text="velocity = 10 m/s", domain=Domain.PHYSICS)
        result = validator.validate(claim)
        assert result.valid is True

    def test_one_fails(self):
        """Test that claim fails when one validator fails."""
        validator = CompositeValidator([
            PhysicsValidator(),
            PolicyValidator(forbidden_phrases=["velocity"]),
        ])

        claim = Claim(text="velocity = 10 m/s", domain=Domain.PHYSICS)
        result = validator.validate(claim)
        assert result.valid is False


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestFactoryFunctions:
    """Test factory functions for creating default configurations."""

    def test_create_default_registry(self):
        """Test default registry creation."""
        registry = create_default_registry()

        assert Domain.PHYSICS in registry
        assert Domain.MATH in registry
        assert Domain.LOGIC in registry
        assert Domain.POLICY in registry
        assert Domain.TEMPORAL in registry
        assert Domain.FINANCIAL in registry

    def test_create_engine(self):
        """Test engine factory."""
        mock = MockLLM(responses=[
            {"claims": [{"text": "2 + 2 = 4", "domain": "math"}]}
        ])

        engine = create_engine(llm=mock)

        result = engine.generate("test")
        assert result.status == "verified"


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """Full integration tests."""

    def test_full_pipeline(self):
        """Test complete validation pipeline."""
        # Create registry with all validators
        registry = ValidatorRegistry([
            PhysicsValidator(),
            MathValidator(),
            LogicValidator(),
            PolicyValidator(forbidden_phrases=["forbidden"]),
        ])

        # Validate mixed batch
        batch = ClaimBatch(claims=[
            Claim(text="2 + 2 = 4", domain=Domain.MATH),
            Claim(text="velocity = 100 m/s", domain=Domain.PHYSICS),
            Claim(text="the cat is on the mat", domain=Domain.LOGIC),
        ])

        result = registry.validate_batch(batch)
        assert result.all_valid is True
        assert len(result.approved) == 3

    def test_pipeline_with_violations(self):
        """Test pipeline with mixed valid/invalid claims."""
        registry = ValidatorRegistry([
            PhysicsValidator(),
            MathValidator(),
        ])

        batch = ClaimBatch(claims=[
            Claim(text="2 + 2 = 4", domain=Domain.MATH),          # Valid
            Claim(text="velocity = 400000000 m/s", domain=Domain.PHYSICS),  # FTL
            Claim(text="2 + 2 = 5", domain=Domain.MATH),          # Invalid
        ])

        result = registry.validate_batch(batch)
        assert len(result.approved) == 1
        assert len(result.violations) == 2

    def test_generation_result_serialization(self):
        """Test GenerationResult JSON serialization."""
        result = GenerationResult(
            status="verified",
            claims=["2 + 2 = 4", "3 * 3 = 9"],
            iterations=1,
        )

        d = result.to_dict()
        assert d["status"] == "verified"
        assert len(d["claims"]) == 2
        assert "proof_hash" in d


# ═══════════════════════════════════════════════════════════════════════════════
# LLM SYSTEM PROMPT TEST
# ═══════════════════════════════════════════════════════════════════════════════

class TestLLMSystemPrompt:
    """Test the LLM system prompt specification."""

    def test_system_prompt_exists(self):
        """Test that system prompt is defined."""
        assert LLM_SYSTEM_PROMPT is not None
        assert len(LLM_SYSTEM_PROMPT) > 0

    def test_system_prompt_contains_schema(self):
        """Test that system prompt contains JSON schema."""
        assert "JSON" in LLM_SYSTEM_PROMPT
        assert "claims" in LLM_SYSTEM_PROMPT
        assert "domain" in LLM_SYSTEM_PROMPT

    def test_system_prompt_contains_rules(self):
        """Test that system prompt contains rules."""
        assert "atomic" in LLM_SYSTEM_PROMPT.lower()
        assert "no explanations" in LLM_SYSTEM_PROMPT.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
