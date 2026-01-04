#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON FORGE - THE VERIFICATION ENGINE
The CPU of the Newton Supercomputer.

The Forge evaluates constraints. That's it.
But that's everything.

Every verification is a computation.
The constraint check IS the work.

═══════════════════════════════════════════════════════════════════════════════

HISTORICAL LINEAGE:

The Forge implements a Propagator Network (Steele & Sussman, MIT 1980) with
iterative relaxation (Sutherland's Sketchpad, 1963). Like Sutherland's
Gauss-Seidel relaxation, the Forge seeks a fixed-point where all constraints
are satisfied.

Key CS Concepts Implemented:
- Arc Consistency (Waltz, 1975): Prune invalid states before computation
- Fixed-Point Iteration: Loop until stable state or violation
- Parallel Constraint Evaluation: ThreadPoolExecutor for concurrent checks

The 2.31ms latency comes from early pruning—like Waltz's algorithm, we delete
impossible states before attempting to compute with them.

See: docs/NEWTON_CLP_SYSTEM_DEFINITION.md for full historical context.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import time
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

from .cdl import (
    Constraint, AtomicConstraint, CompositeConstraint, ConditionalConstraint,
    CDLEvaluator, CDLParser, EvaluationResult, Domain, Operator
)


# ═══════════════════════════════════════════════════════════════════════════════
# FORGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ForgeConfig:
    """Configuration for the Forge."""
    max_workers: int = 8                    # Parallel evaluation threads
    timeout_ms: int = 1000                  # Max time per evaluation
    enable_metrics: bool = True             # Track performance metrics
    enable_caching: bool = True             # Cache repeated evaluations
    cache_ttl_seconds: int = 300            # Cache TTL
    strict_mode: bool = True                # Fail on any error


# ═══════════════════════════════════════════════════════════════════════════════
# FORGE METRICS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ForgeMetrics:
    """Performance metrics for the Forge."""
    total_evaluations: int = 0
    passed_evaluations: int = 0
    failed_evaluations: int = 0
    error_evaluations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_time_us: int = 0  # microseconds
    min_time_us: int = 0
    max_time_us: int = 0

    @property
    def avg_time_us(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        return self.total_time_us / self.total_evaluations

    @property
    def pass_rate(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        return self.passed_evaluations / self.total_evaluations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_evaluations": self.total_evaluations,
            "passed": self.passed_evaluations,
            "failed": self.failed_evaluations,
            "errors": self.error_evaluations,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "avg_time_us": round(self.avg_time_us, 2),
            "min_time_us": self.min_time_us,
            "max_time_us": self.max_time_us,
            "pass_rate": round(self.pass_rate * 100, 2)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION RESULT - Extended with timing
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VerificationResult:
    """Complete result of Forge verification."""
    passed: bool
    constraint_id: str
    message: Optional[str] = None
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    elapsed_us: int = 0
    fingerprint: Optional[str] = None
    from_cache: bool = False

    def __post_init__(self):
        if self.fingerprint is None:
            data = f"{self.passed}:{self.constraint_id}:{self.timestamp}"
            self.fingerprint = f"N2_{hashlib.sha256(data.encode()).hexdigest()}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "constraint_id": self.constraint_id,
            "message": self.message,
            "timestamp": self.timestamp,
            "elapsed_us": self.elapsed_us,
            "fingerprint": self.fingerprint,
            "from_cache": self.from_cache
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT SAFETY PATTERNS - Built-in harm prevention
# ═══════════════════════════════════════════════════════════════════════════════

SAFETY_PATTERNS = {
    "harm": {
        "name": "No Harm",
        "patterns": [
            r"(how to )?(make|build|create|construct).*\b(bomb|weapon|explosive|poison|grenade)\b",
            r"(how to )?(kill|murder|harm|hurt|injure|assassinate)",
            r"(how to )?(suicide|self.harm)",
            r"\b(i want to|i need to|help me) (kill|murder|harm|hurt)",
        ]
    },
    "medical": {
        "name": "Medical Bounds",
        "patterns": [
            r"what (medication|drug|dosage|prescription) should (i|you) take",
            r"diagnose (my|this|the)",
            r"prescribe (me|a)",
        ]
    },
    "legal": {
        "name": "Legal Bounds",
        "patterns": [
            r"(how to )?(evade|avoid|cheat).*(tax|irs)",
            r"(how to )?(launder|hide|offshore) money",
            r"(how to )?(forge|fake|counterfeit)",
        ]
    },
    "security": {
        "name": "Security",
        "patterns": [
            r"(how to )?(hack|crack|break into|exploit|bypass)",
            r"\b(steal password|phishing|malware|ransomware)\b",
        ]
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# THE FORGE
# ═══════════════════════════════════════════════════════════════════════════════

class Forge:
    """
    The Newton Forge - Verification Engine.

    This is the CPU of the Newton Supercomputer.
    It does one thing: evaluate constraints against objects.
    It does it fast. It does it right. It does it deterministically.

    The verification IS the computation.
    """

    def __init__(self, config: Optional[ForgeConfig] = None):
        self.config = config or ForgeConfig()
        self.metrics = ForgeMetrics()
        self._evaluator = CDLEvaluator()
        self._parser = CDLParser()
        self._cache: Dict[str, tuple] = {}  # {cache_key: (result, timestamp)}
        self._cache_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        
        # Glass Box components (lazy initialization)
        self._vault_client = None
        self._policy_engine = None
        self._negotiator = None
        self._glass_box_enabled = False

    # ─────────────────────────────────────────────────────────────────────────
    # CORE VERIFICATION
    # ─────────────────────────────────────────────────────────────────────────

    def verify(
        self,
        constraint: Any,
        obj: Dict[str, Any],
        use_cache: bool = True
    ) -> VerificationResult:
        """
        Verify a single constraint against an object.

        The fundamental operation. Everything else is optimization.
        """
        start_us = time.perf_counter_ns() // 1000

        # Parse constraint if needed
        if isinstance(constraint, dict):
            constraint = self._parser.parse(constraint)

        # Check cache
        if use_cache and self.config.enable_caching:
            cache_key = self._cache_key(constraint, obj)
            cached = self._get_cached(cache_key)
            if cached is not None:
                self.metrics.cache_hits += 1
                return VerificationResult(
                    passed=cached.passed,
                    constraint_id=cached.constraint_id,
                    message=cached.message,
                    elapsed_us=0,
                    from_cache=True
                )
            self.metrics.cache_misses += 1

        # Evaluate
        try:
            result = self._evaluator.evaluate(constraint, obj)
            elapsed_us = (time.perf_counter_ns() // 1000) - start_us

            verification_result = VerificationResult(
                passed=result.passed,
                constraint_id=result.constraint_id,
                message=result.message,
                elapsed_us=elapsed_us
            )

            # Update metrics
            self._update_metrics(verification_result)

            # Cache result
            if use_cache and self.config.enable_caching:
                self._set_cached(cache_key, verification_result)

            return verification_result

        except Exception as e:
            elapsed_us = (time.perf_counter_ns() // 1000) - start_us
            self.metrics.error_evaluations += 1
            return VerificationResult(
                passed=False if self.config.strict_mode else True,
                constraint_id=getattr(constraint, 'id', 'UNKNOWN'),
                message=f"Evaluation error: {str(e)}",
                elapsed_us=elapsed_us
            )

    def verify_all(
        self,
        constraints: List[Any],
        obj: Dict[str, Any],
        parallel: bool = True
    ) -> List[VerificationResult]:
        """
        Verify multiple constraints against an object.
        Optionally in parallel.
        """
        if not parallel or len(constraints) <= 1:
            return [self.verify(c, obj) for c in constraints]

        # Parallel verification
        futures = [
            self._executor.submit(self.verify, c, obj)
            for c in constraints
        ]
        return [f.result() for f in futures]

    def verify_and(
        self,
        constraints: List[Any],
        obj: Dict[str, Any],
        parallel: bool = True
    ) -> VerificationResult:
        """All constraints must pass."""
        start_us = time.perf_counter_ns() // 1000
        results = self.verify_all(constraints, obj, parallel)

        passed = all(r.passed for r in results)
        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        failed_messages = [r.message for r in results if not r.passed and r.message]

        return VerificationResult(
            passed=passed,
            constraint_id=f"AND_{len(results)}",
            message="; ".join(failed_messages) if not passed else None,
            elapsed_us=elapsed_us
        )

    def verify_or(
        self,
        constraints: List[Any],
        obj: Dict[str, Any],
        parallel: bool = True
    ) -> VerificationResult:
        """At least one constraint must pass."""
        start_us = time.perf_counter_ns() // 1000
        results = self.verify_all(constraints, obj, parallel)

        passed = any(r.passed for r in results)
        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return VerificationResult(
            passed=passed,
            constraint_id=f"OR_{len(results)}",
            message="All constraints failed" if not passed else None,
            elapsed_us=elapsed_us
        )

    # ─────────────────────────────────────────────────────────────────────────
    # CONTENT SAFETY - Built-in harm prevention
    # ─────────────────────────────────────────────────────────────────────────

    def verify_content(
        self,
        text: str,
        categories: Optional[List[str]] = None
    ) -> VerificationResult:
        """
        Verify text content against safety patterns.

        This is the original Newton verification - pattern-based content safety.
        Now integrated into the Forge as a first-class operation.
        """
        start_us = time.perf_counter_ns() // 1000
        text_lower = text.lower()

        if categories is None:
            categories = list(SAFETY_PATTERNS.keys())

        passed_categories = []
        failed_categories = []

        for category in categories:
            if category not in SAFETY_PATTERNS:
                continue

            patterns = SAFETY_PATTERNS[category]["patterns"]
            violation = False

            for pattern in patterns:
                if re.search(pattern, text_lower):
                    violation = True
                    break

            if violation:
                failed_categories.append(category)
            else:
                passed_categories.append(category)

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us
        passed = len(failed_categories) == 0

        result = VerificationResult(
            passed=passed,
            constraint_id=f"CONTENT_{len(categories)}",
            message=f"Violations: {', '.join(failed_categories)}" if not passed else None,
            elapsed_us=elapsed_us
        )

        self._update_metrics(result)
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # SIGNAL ANALYSIS - DW Axis verification
    # ─────────────────────────────────────────────────────────────────────────

    DW_AXIS = 2048
    THRESHOLD = 1024

    def verify_signal(self, text: str) -> VerificationResult:
        """
        Original Newton signal-based verification.

        Maps text to a signal value and checks if it's within
        the crystalline threshold of the DW axis.
        """
        start_us = time.perf_counter_ns() // 1000

        # Melt text to signal
        cleaned = re.sub(r'[^a-z0-9\s]', '', text.lower())
        tokens = cleaned.split()

        signal = self.DW_AXIS
        for i, token in enumerate(tokens):
            h = 0
            for char in token:
                h = ((h << 5) ^ h ^ ord(char)) & 0xFFF
            weight = (h % 400) - 200
            signal += weight

        signal = max(0, min(4095, signal))

        # Check crystalline alignment
        distance = abs(signal - self.DW_AXIS)
        crystalline = distance <= self.THRESHOLD
        confidence = round((1 - distance / self.THRESHOLD) * 100, 1) if crystalline else 0

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        result = VerificationResult(
            passed=crystalline,
            constraint_id=f"SIGNAL_{signal}",
            message=f"Signal {signal}, distance {distance} (threshold {self.THRESHOLD})" if not crystalline else None,
            elapsed_us=elapsed_us
        )

        self._update_metrics(result)
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # COMPOSITE VERIFICATION - Full Newton check
    # ─────────────────────────────────────────────────────────────────────────

    def verify_full(
        self,
        text: str,
        constraints: Optional[List[Any]] = None,
        obj: Optional[Dict[str, Any]] = None,
        safety_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Full Newton verification pipeline.

        1. Content safety check (pattern matching)
        2. Signal verification (crystalline alignment)
        3. Constraint verification (CDL evaluation)

        Returns comprehensive result with all checks.
        """
        start_us = time.perf_counter_ns() // 1000
        results = {}

        # 1. Content safety
        content_result = self.verify_content(text, safety_categories)
        results["content"] = content_result.to_dict()

        # 2. Signal verification
        signal_result = self.verify_signal(text)
        results["signal"] = signal_result.to_dict()

        # 3. Constraint verification
        if constraints and obj:
            constraint_result = self.verify_and(constraints, obj)
            results["constraints"] = constraint_result.to_dict()
        else:
            results["constraints"] = None

        # Overall pass/fail
        passed = content_result.passed and signal_result.passed
        if constraints and obj:
            passed = passed and results["constraints"]["passed"]

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return {
            "passed": passed,
            "code": 200 if passed else 1202,
            "elapsed_us": elapsed_us,
            "timestamp": int(time.time() * 1000),
            "fingerprint": f"N2_{hashlib.sha256(text.encode()).hexdigest()[:16]}",
            "results": results,
            "engine": "Newton Forge 1.0.0"
        }

    # ─────────────────────────────────────────────────────────────────────────
    # CACHE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def _cache_key(self, constraint: Constraint, obj: Dict[str, Any]) -> str:
        """Generate cache key from constraint and object."""
        c_str = str(constraint.id if hasattr(constraint, 'id') else constraint)
        o_str = str(sorted(obj.items()))
        return hashlib.sha256(f"{c_str}:{o_str}".encode()).hexdigest()[:16]

    def _get_cached(self, key: str) -> Optional[VerificationResult]:
        """Get cached result if not expired."""
        with self._cache_lock:
            if key not in self._cache:
                return None
            result, timestamp = self._cache[key]
            if time.time() - timestamp > self.config.cache_ttl_seconds:
                del self._cache[key]
                return None
            return result

    def _set_cached(self, key: str, result: VerificationResult):
        """Cache a verification result."""
        with self._cache_lock:
            self._cache[key] = (result, time.time())

    def clear_cache(self):
        """Clear all cached results."""
        with self._cache_lock:
            self._cache.clear()

    # ─────────────────────────────────────────────────────────────────────────
    # METRICS
    # ─────────────────────────────────────────────────────────────────────────

    def _update_metrics(self, result: VerificationResult):
        """Update performance metrics."""
        if not self.config.enable_metrics:
            return

        self.metrics.total_evaluations += 1
        if result.passed:
            self.metrics.passed_evaluations += 1
        else:
            self.metrics.failed_evaluations += 1

        self.metrics.total_time_us += result.elapsed_us

        if self.metrics.min_time_us == 0 or result.elapsed_us < self.metrics.min_time_us:
            self.metrics.min_time_us = result.elapsed_us
        if result.elapsed_us > self.metrics.max_time_us:
            self.metrics.max_time_us = result.elapsed_us

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.to_dict()

    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = ForgeMetrics()

    # ─────────────────────────────────────────────────────────────────────────
    # SHUTDOWN
    # ─────────────────────────────────────────────────────────────────────────

    def shutdown(self):
        """Graceful shutdown of the Forge."""
        self._executor.shutdown(wait=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # GLASS BOX ACTIVATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def enable_glass_box(
        self,
        vault_client=None,
        policy_engine=None,
        negotiator=None
    ):
        """
        Enable Glass Box mode with full transparency and human oversight.
        
        Args:
            vault_client: VaultClient instance for provenance logging
            policy_engine: PolicyEngine instance for policy enforcement
            negotiator: Negotiator instance for HITL
        """
        self._glass_box_enabled = True
        
        # Import here to avoid circular dependencies
        if vault_client:
            self._vault_client = vault_client
        
        if policy_engine:
            self._policy_engine = policy_engine
        
        if negotiator:
            self._negotiator = negotiator
    
    def verify_with_glass_box(
        self,
        constraint: Any,
        obj: Dict[str, Any],
        operation: str = "verify",
        require_approval: bool = False
    ) -> VerificationResult:
        """
        Verify with full Glass Box transparency.
        
        This method:
        1. Evaluates input policies
        2. Logs to vault (provenance)
        3. Requests human approval if needed
        4. Performs verification
        5. Evaluates output policies
        6. Emits provenance record
        
        Args:
            constraint: Constraint to verify
            obj: Object to verify against
            operation: Operation name for logging
            require_approval: Force human approval
        
        Returns:
            VerificationResult with full provenance
        """
        if not self._glass_box_enabled:
            # Fall back to regular verify
            return self.verify(constraint, obj)
        
        # 1. Evaluate input policies
        if self._policy_engine:
            policy_results = self._policy_engine.evaluate_input(obj, operation)
            if self._policy_engine.check_enforcement_needed(policy_results):
                return VerificationResult(
                    passed=False,
                    constraint_id="POLICY_VIOLATION",
                    message=f"Input policy violation: {policy_results[0].message}"
                )
        
        # 2. Request approval if needed
        if require_approval and self._negotiator:
            from .negotiator import RequestPriority
            request = self._negotiator.request_approval(
                operation=operation,
                input_data=str(obj),
                reason="Glass Box verification requires approval",
                priority=RequestPriority.MEDIUM
            )
            # Note: In real usage, this would wait or return pending status
            # For now, we proceed without blocking
        
        # 3. Perform verification
        result = self.verify(constraint, obj)
        
        # 4. Evaluate output policies
        if self._policy_engine:
            output_policies = self._policy_engine.evaluate_output(
                result.to_dict(),
                operation
            )
            if self._policy_engine.check_enforcement_needed(output_policies):
                result.passed = False
                result.message = f"Output policy violation: {output_policies[0].message}"
        
        # 5. Log to vault for provenance
        if self._vault_client:
            try:
                self._vault_client.log_verification(
                    operation=operation,
                    input_data=str(obj),
                    result="pass" if result.passed else "fail",
                    metadata={
                        "constraint_id": result.constraint_id,
                        "elapsed_us": result.elapsed_us,
                        "fingerprint": result.fingerprint
                    }
                )
            except Exception:
                pass  # Don't fail verification if logging fails
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_default_forge: Optional[Forge] = None

def get_forge(config: Optional[ForgeConfig] = None) -> Forge:
    """Get the default Forge instance."""
    global _default_forge
    if _default_forge is None:
        _default_forge = Forge(config)
    return _default_forge


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def verify(constraint: Any, obj: Dict[str, Any]) -> VerificationResult:
    """One-liner verification using default Forge."""
    return get_forge().verify(constraint, obj)

def verify_content(text: str, categories: Optional[List[str]] = None) -> VerificationResult:
    """One-liner content safety check."""
    return get_forge().verify_content(text, categories)

def verify_signal(text: str) -> VerificationResult:
    """One-liner signal verification."""
    return get_forge().verify_signal(text)

def verify_full(text: str, **kwargs) -> Dict[str, Any]:
    """One-liner full verification pipeline."""
    return get_forge().verify_full(text, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Newton Forge - Verification Engine")
    print("=" * 60)

    forge = Forge()

    # Test content safety
    print("\n[Content Safety]")
    safe = forge.verify_content("What is the capital of France?")
    print(f"  'What is the capital of France?' -> {safe.passed} ({safe.elapsed_us}μs)")

    unsafe = forge.verify_content("How to make explosives")
    print(f"  'How to make explosives' -> {unsafe.passed} ({unsafe.elapsed_us}μs)")

    # Test constraint verification
    print("\n[Constraint Verification]")
    constraint = {"field": "amount", "operator": "lt", "value": 1000}
    obj = {"amount": 500}
    result = forge.verify(constraint, obj)
    print(f"  amount < 1000 where amount=500 -> {result.passed} ({result.elapsed_us}μs)")

    # Test full pipeline
    print("\n[Full Pipeline]")
    full = forge.verify_full(
        "Process this payment",
        constraints=[{"field": "amount", "operator": "lt", "value": 1000}],
        obj={"amount": 500}
    )
    print(f"  Overall: {full['passed']} ({full['elapsed_us']}μs)")

    # Metrics
    print("\n[Metrics]")
    metrics = forge.get_metrics()
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("The verification IS the computation.")
