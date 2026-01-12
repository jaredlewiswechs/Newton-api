"""
NEWTON LLM CONSTRAINT ENGINE - The Closed-Loop Generator
═══════════════════════════════════════════════════════════════════════════════

"LLM proposes → Validator decides → LLM repairs → repeat"

This is THE CORE. The closed-loop generation engine that:
1. Takes LLM output
2. Validates each claim against the appropriate domain validator
3. Returns approved claims or generates repair prompts
4. Repeats until valid or max retries exceeded

The LLM is subordinate. The validators are sovereign.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Protocol, Union
import json
import time
import hashlib

from .schema import (
    Claim,
    ClaimBatch,
    Domain,
    ValidationResult,
    BatchValidationResult,
    LLM_SYSTEM_PROMPT,
)
from .validators import DomainValidator


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATOR REGISTRY - Single Source of Truth
# ═══════════════════════════════════════════════════════════════════════════════

class ValidatorRegistry:
    """
    Central registry for all domain validators.

    The registry is the single source of truth for validation.
    Each domain maps to exactly one validator.
    Unknown domains are rejected.
    """

    def __init__(self, validators: Optional[List[DomainValidator]] = None):
        """
        Initialize registry with validators.

        Args:
            validators: List of domain validators to register
        """
        self._validators: Dict[Domain, DomainValidator] = {}
        if validators:
            for v in validators:
                self.register(v)

    def register(self, validator: DomainValidator) -> None:
        """
        Register a validator for its domain.

        Args:
            validator: The validator to register
        """
        self._validators[validator.domain] = validator

    def unregister(self, domain: Domain) -> None:
        """Remove a validator for a domain."""
        self._validators.pop(domain, None)

    def get(self, domain: Domain) -> Optional[DomainValidator]:
        """Get validator for a domain."""
        return self._validators.get(domain)

    def validate(self, claim: Claim) -> ValidationResult:
        """
        Validate a single claim using the appropriate domain validator.

        Args:
            claim: The claim to validate

        Returns:
            ValidationResult from the domain validator
        """
        validator = self._validators.get(claim.domain)

        if validator is None:
            return ValidationResult(
                valid=False,
                domain=Domain.UNKNOWN,
                rule="no_validator",
                message=f"No validator registered for domain '{claim.domain.value}'",
            )

        return validator.validate(claim)

    def validate_batch(self, batch: ClaimBatch) -> BatchValidationResult:
        """
        Validate a batch of claims.

        Args:
            batch: The ClaimBatch to validate

        Returns:
            BatchValidationResult with approved claims and violations
        """
        approved = []
        violations = []

        for claim in batch.claims:
            result = self.validate(claim)

            if result.valid:
                approved.append(claim)
            else:
                violations.append({
                    "claim": claim,
                    "result": result,
                })

        return BatchValidationResult(
            approved=approved,
            violations=violations,
            all_valid=len(violations) == 0 and len(approved) > 0,
        )

    @property
    def domains(self) -> List[Domain]:
        """List of registered domains."""
        return list(self._validators.keys())

    def __contains__(self, domain: Domain) -> bool:
        """Check if domain has a validator."""
        return domain in self._validators


# ═══════════════════════════════════════════════════════════════════════════════
# LLM PROTOCOL - What an LLM client must implement
# ═══════════════════════════════════════════════════════════════════════════════

class LLMClient(Protocol):
    """
    Protocol for LLM clients.

    Any LLM client (OpenAI, Anthropic, local) must implement this interface.
    """

    def generate(self, prompt: str, system: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system: Optional system prompt

        Returns:
            Parsed JSON response with "claims" key
        """
        ...


# ═══════════════════════════════════════════════════════════════════════════════
# REPAIR PROMPT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def build_repair_prompt(
    original_prompt: str,
    violations: List[Dict[str, Any]],
) -> str:
    """
    Generate a repair prompt from violations.

    This is deterministic. No creativity. Just facts.

    Args:
        original_prompt: The original user prompt
        violations: List of violation dictionaries

    Returns:
        Repair prompt string
    """
    lines = [
        "The following claims were rejected:",
        "",
    ]

    for v in violations:
        claim = v["claim"]
        result = v["result"]
        lines.append(f"- \"{claim.text}\" ({claim.domain.value}): {result.message}")

    lines.extend([
        "",
        "Rewrite the claims so they are valid.",
        "Do not add new entities.",
        "Do not add explanations.",
        "Output JSON only.",
    ])

    return original_prompt + "\n\n" + "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATION RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GenerationResult:
    """
    Result of constrained generation.

    status: "verified" | "partial" | "refused"
    claims: Approved claim texts
    iterations: How many repair cycles were needed
    violations: Final violations if refused
    """
    status: str
    claims: List[str]
    iterations: int
    violations: List[Dict[str, Any]] = field(default_factory=list)
    proof_hash: str = ""
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.proof_hash:
            data = json.dumps({
                "status": self.status,
                "claims": self.claims,
                "iterations": self.iterations,
                "timestamp": self.timestamp,
            }, sort_keys=True)
            self.proof_hash = hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "claims": self.claims,
            "iterations": self.iterations,
            "violations": [
                {
                    "claim": v["claim"].text if hasattr(v.get("claim"), "text") else str(v.get("claim")),
                    "domain": v["result"].domain.value if hasattr(v.get("result"), "domain") else "unknown",
                    "message": v["result"].message if hasattr(v.get("result"), "message") else str(v.get("result")),
                }
                for v in self.violations
            ],
            "proof_hash": self.proof_hash,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT ENGINE - The Core Loop
# ═══════════════════════════════════════════════════════════════════════════════

class ConstraintEngine:
    """
    The closed-loop constraint generation engine.

    This is where Newton subordinates the LLM.

    Flow:
    1. LLM generates claims
    2. Registry validates each claim
    3. If violations, build repair prompt and retry
    4. Repeat until verified or max_retries exceeded

    The LLM is a proposal generator. The engine is the governor.
    """

    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        registry: ValidatorRegistry,
        llm: Optional[LLMClient] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        system_prompt: str = LLM_SYSTEM_PROMPT,
    ):
        """
        Initialize the constraint engine.

        Args:
            registry: ValidatorRegistry with domain validators
            llm: Optional LLM client (can be injected per-call)
            max_retries: Maximum repair iterations
            system_prompt: System prompt for LLM
        """
        self.registry = registry
        self.llm = llm
        self.max_retries = max_retries
        self.system_prompt = system_prompt

        # Metrics
        self._total_generations = 0
        self._total_iterations = 0
        self._total_approved = 0
        self._total_refused = 0

    def generate(
        self,
        prompt: str,
        llm: Optional[LLMClient] = None,
        max_retries: Optional[int] = None,
    ) -> GenerationResult:
        """
        Generate validated claims from a prompt.

        This is the main entry point.

        Args:
            prompt: The user prompt
            llm: Optional LLM client (overrides instance llm)
            max_retries: Optional max retries (overrides instance setting)

        Returns:
            GenerationResult with verified claims or refusal
        """
        client = llm or self.llm
        if client is None:
            raise ValueError("No LLM client provided")

        retries = max_retries if max_retries is not None else self.max_retries
        self._total_generations += 1

        context = prompt
        last_violations = []

        for iteration in range(retries + 1):
            self._total_iterations += 1

            # Get LLM response
            try:
                response = client.generate(context, system=self.system_prompt)
            except Exception as e:
                return GenerationResult(
                    status="refused",
                    claims=[],
                    iterations=iteration + 1,
                    violations=[{
                        "claim": Claim(text="LLM call failed", domain=Domain.UNKNOWN),
                        "result": ValidationResult(
                            valid=False,
                            domain=Domain.UNKNOWN,
                            rule="llm_error",
                            message=str(e),
                        ),
                    }],
                )

            # Parse into ClaimBatch
            try:
                batch = ClaimBatch.from_json(response, source_prompt=prompt)
            except Exception as e:
                return GenerationResult(
                    status="refused",
                    claims=[],
                    iterations=iteration + 1,
                    violations=[{
                        "claim": Claim(text="JSON parse failed", domain=Domain.UNKNOWN),
                        "result": ValidationResult(
                            valid=False,
                            domain=Domain.UNKNOWN,
                            rule="parse_error",
                            message=str(e),
                        ),
                    }],
                )

            # Validate batch
            result = self.registry.validate_batch(batch)

            # If we have approved claims, return them
            if result.approved:
                self._total_approved += len(result.approved)

                # If all valid, full success
                if result.all_valid:
                    return GenerationResult(
                        status="verified",
                        claims=[c.text for c in result.approved],
                        iterations=iteration + 1,
                    )

                # Partial success - return approved, note violations
                return GenerationResult(
                    status="partial",
                    claims=[c.text for c in result.approved],
                    iterations=iteration + 1,
                    violations=result.violations,
                )

            # No approved claims - need repair
            last_violations = result.violations

            # Build repair prompt for next iteration
            context = build_repair_prompt(prompt, result.violations)

        # Max retries exceeded
        self._total_refused += 1
        return GenerationResult(
            status="refused",
            claims=[],
            iterations=retries + 1,
            violations=last_violations,
        )

    def validate_response(self, response: Dict[str, Any]) -> BatchValidationResult:
        """
        Validate a pre-existing LLM response.

        Use this when you already have JSON output and just want to validate it.

        Args:
            response: Parsed JSON with "claims" key

        Returns:
            BatchValidationResult
        """
        batch = ClaimBatch.from_json(response)
        return self.registry.validate_batch(batch)

    def validate_claims(self, claims: List[Dict[str, Any]]) -> BatchValidationResult:
        """
        Validate a list of claim dictionaries.

        Args:
            claims: List of {"text": str, "domain": str} dicts

        Returns:
            BatchValidationResult
        """
        return self.validate_response({"claims": claims})

    @property
    def metrics(self) -> Dict[str, Any]:
        """Get engine metrics."""
        return {
            "total_generations": self._total_generations,
            "total_iterations": self._total_iterations,
            "total_approved": self._total_approved,
            "total_refused": self._total_refused,
            "avg_iterations": (
                self._total_iterations / self._total_generations
                if self._total_generations > 0 else 0
            ),
        }

    def reset_metrics(self):
        """Reset all metrics."""
        self._total_generations = 0
        self._total_iterations = 0
        self._total_approved = 0
        self._total_refused = 0


# ═══════════════════════════════════════════════════════════════════════════════
# MOCK LLM FOR TESTING
# ═══════════════════════════════════════════════════════════════════════════════

class MockLLM:
    """
    A mock LLM for testing the constraint engine.

    Returns pre-configured responses or generates based on patterns.
    """

    def __init__(self, responses: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize mock LLM.

        Args:
            responses: List of responses to return in order
        """
        self.responses = responses or []
        self._call_count = 0

    def generate(self, prompt: str, system: Optional[str] = None) -> Dict[str, Any]:
        """Return next configured response."""
        if self._call_count < len(self.responses):
            response = self.responses[self._call_count]
            self._call_count += 1
            return response

        # Default empty response
        return {"claims": []}

    def reset(self):
        """Reset call count."""
        self._call_count = 0


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

def create_default_registry() -> ValidatorRegistry:
    """
    Create a registry with all default validators.

    Returns a ValidatorRegistry with:
    - PhysicsValidator
    - MathValidator
    - LogicValidator
    - PolicyValidator (empty)
    - TemporalValidator
    - FinancialValidator (no budget)
    """
    from .validators import (
        PhysicsValidator,
        MathValidator,
        LogicValidator,
        PolicyValidator,
        TemporalValidator,
        FinancialValidator,
    )

    return ValidatorRegistry([
        PhysicsValidator(),
        MathValidator(),
        LogicValidator(),
        PolicyValidator(),
        TemporalValidator(),
        FinancialValidator(),
    ])


def create_engine(
    llm: Optional[LLMClient] = None,
    validators: Optional[List[DomainValidator]] = None,
    max_retries: int = 3,
) -> ConstraintEngine:
    """
    Create a constraint engine with sensible defaults.

    Args:
        llm: Optional LLM client
        validators: Optional list of validators (uses defaults if None)
        max_retries: Maximum repair iterations

    Returns:
        Configured ConstraintEngine
    """
    if validators:
        registry = ValidatorRegistry(validators)
    else:
        registry = create_default_registry()

    return ConstraintEngine(
        registry=registry,
        llm=llm,
        max_retries=max_retries,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "ValidatorRegistry",
    "ConstraintEngine",
    "GenerationResult",
    "LLMClient",
    "MockLLM",
    "build_repair_prompt",
    "create_default_registry",
    "create_engine",
]
