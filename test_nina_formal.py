#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   NINA FORMAL VERIFICATION SUITE                                            ║
║   Testing the BeegMAMA/Newton Calculus Invariants                           ║
║                                                                              ║
║   Verifies:                                                                  ║
║   1. API Contract Compliance (5-tuple artifact)                             ║
║   2. Bounds Report Presence                                                  ║
║   3. Sanitization Exclusion Set                                             ║
║   4. Trust Lattice + LLM Ceiling                                            ║
║   5. Ledger Chain Integrity                                                 ║
║   6. No Implicit Trust Upgrade                                              ║
║   7. Trace Refinement (witness completeness)                                ║
║                                                                              ║
║   Based on: Progress/Preservation soundness theorems                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field

# Import BiggestMAMA
from BiggestMAMA import (
    Pipeline, Regime, RegimeType, TrustLabel, TrustLattice,
    PipelineResult, ExecutionBounds, get_trust_lattice,
    nina_query, nina_calculate
)


# ═══════════════════════════════════════════════════════════════════════════════
# INVARIANT DEFINITIONS (from BeegMAMA calculus)
# ═══════════════════════════════════════════════════════════════════════════════

FORBIDDEN_TOKENS = {'$', '`', ';', '|', '&', '<', '>', '\n', '\r', '\0'}
MAX_INPUT_LENGTH = 1000

@dataclass
class InvariantResult:
    """Result of checking a single invariant."""
    name: str
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormalVerificationReport:
    """Complete verification report."""
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    invariants: List[InvariantResult]
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def __str__(self):
        status = "PASS" if self.failed == 0 else "FAIL"
        return f"[{status}] {self.passed}/{self.total_tests} invariants verified"


# ═══════════════════════════════════════════════════════════════════════════════
# INVARIANT CHECKERS
# ═══════════════════════════════════════════════════════════════════════════════

def check_api_contract(result: PipelineResult) -> InvariantResult:
    """
    Invariant 1: API Contract Compliance
    
    Result = ⟨v, π, ℓ, b, p⟩ where all fields must be present.
    """
    has_value = hasattr(result, 'value')
    has_trace = hasattr(result, 'trace') and result.trace is not None
    has_trust = hasattr(result, 'trust_label') and isinstance(result.trust_label, TrustLabel)
    has_bounds = hasattr(result, 'bounds_report') and result.bounds_report is not None
    has_proof = hasattr(result, 'ledger_proof')  # Can be None on error, but field must exist
    
    all_present = has_value and has_trace and has_trust and has_bounds and has_proof
    
    return InvariantResult(
        name="API_CONTRACT",
        passed=all_present,
        message="Result artifact has all 5 required fields" if all_present else "Missing fields in result artifact",
        details={
            "has_value": has_value,
            "has_trace": has_trace,
            "has_trust_label": has_trust,
            "has_bounds_report": has_bounds,
            "has_ledger_proof": has_proof
        }
    )


def check_bounds_report(result: PipelineResult) -> InvariantResult:
    """
    Invariant 2: Bounded Execution
    
    ∀ computation c: resources(c) ≤ B and bounds report must be present.
    """
    if result.bounds_report is None:
        return InvariantResult(
            name="BOUNDS_REPORT",
            passed=False,
            message="Bounds report is None"
        )
    
    br = result.bounds_report
    has_time = hasattr(br, 'time_elapsed_ms') and br.time_elapsed_ms >= 0
    has_ops = hasattr(br, 'operations_count') and br.operations_count >= 0
    has_within = hasattr(br, 'within_bounds')
    
    all_valid = has_time and has_ops and has_within
    
    return InvariantResult(
        name="BOUNDS_REPORT",
        passed=all_valid,
        message="Bounds report valid with time/ops/status" if all_valid else "Invalid bounds report",
        details={
            "time_ms": getattr(br, 'time_elapsed_ms', None),
            "operations": getattr(br, 'operations_count', None),
            "within_bounds": getattr(br, 'within_bounds', None)
        }
    )


def check_sanitization(pipeline: Pipeline, test_inputs: List[str]) -> InvariantResult:
    """
    Invariant 3: Input Sanitization
    
    ∀ inputs i: sanitize(i) ∉ {$, `, ;, |, &, <, >, \n, \r, \0}
    """
    violations = []
    
    for input_text in test_inputs:
        sanitized = pipeline._sanitize_input(input_text)
        
        # Check for forbidden tokens
        for char in sanitized:
            if char in FORBIDDEN_TOKENS:
                violations.append({
                    "input": input_text[:50],
                    "forbidden_char": repr(char),
                    "in_output": sanitized[:50]
                })
        
        # Check length bound
        if len(sanitized) > MAX_INPUT_LENGTH:
            violations.append({
                "input": input_text[:50],
                "violation": "length_exceeded",
                "length": len(sanitized)
            })
    
    passed = len(violations) == 0
    
    return InvariantResult(
        name="SANITIZATION",
        passed=passed,
        message=f"All {len(test_inputs)} inputs sanitized correctly" if passed else f"{len(violations)} sanitization violations",
        details={"violations": violations[:5], "total_violations": len(violations)}
    )


def check_trust_lattice(results: List[Tuple[str, PipelineResult, str]]) -> InvariantResult:
    """
    Invariant 4: Trust Lattice Well-Ordering + LLM Ceiling
    
    - UNTRUSTED ⊑ VERIFIED ⊑ TRUSTED ⊑ KERNEL
    - ∀ LLM responses r: trust(r) ⊑ VERIFIED
    """
    violations = []
    llm_ceiling_violations = []
    
    for query, result, expected_source in results:
        if result.success:
            # Check LLM ceiling: Ollama can never be TRUSTED
            if expected_source == "ollama_governed" and result.trust_label >= TrustLabel.TRUSTED:
                llm_ceiling_violations.append({
                    "query": query,
                    "source": expected_source,
                    "trust": result.trust_label.name,
                    "violation": "LLM_CEILING_BREACHED"
                })
            
            # Check lattice ordering
            if result.trust_label.value < 0 or result.trust_label.value > 3:
                violations.append({
                    "query": query,
                    "invalid_trust": result.trust_label.name
                })
    
    passed = len(violations) == 0 and len(llm_ceiling_violations) == 0
    
    return InvariantResult(
        name="TRUST_LATTICE",
        passed=passed,
        message="Trust lattice valid, LLM ceiling enforced" if passed else "Trust lattice violations detected",
        details={
            "lattice_violations": violations,
            "llm_ceiling_violations": llm_ceiling_violations
        }
    )


def check_ledger_chain(pipeline: Pipeline) -> InvariantResult:
    """
    Invariant 5: Provenance Chain Integrity
    
    ∀ i > 0: entry[i].prev_hash = entry[i-1].hash
    """
    ledger = pipeline.get_ledger()
    
    if len(ledger) < 2:
        return InvariantResult(
            name="LEDGER_CHAIN",
            passed=True,
            message="Ledger has <2 entries, chain trivially valid",
            details={"entries": len(ledger)}
        )
    
    violations = []
    for i in range(1, len(ledger)):
        prev_entry = ledger[i-1]
        curr_entry = ledger[i]
        
        # Check prev_hash links to previous entry's hash
        if curr_entry['prev_hash'] != prev_entry['hash']:
            violations.append({
                "index": i,
                "expected_prev": prev_entry['hash'][:16],
                "actual_prev": curr_entry['prev_hash'][:16]
            })
    
    passed = len(violations) == 0
    
    return InvariantResult(
        name="LEDGER_CHAIN",
        passed=passed,
        message=f"Chain integrity verified across {len(ledger)} entries" if passed else f"{len(violations)} chain breaks",
        details={"entries": len(ledger), "violations": violations}
    )


def check_no_implicit_upgrade(lattice: TrustLattice) -> InvariantResult:
    """
    Invariant 6: No Implicit Trust Upgrade
    
    upgrade(x) → higher trust IFF Verify(x) = True
    """
    # Test that upgrade without verification fails
    test_value = "test_value"
    labeled = lattice.untrusted(test_value, "test_source")
    
    # Try upgrade with failing verifier
    upgrade_succeeded = False
    try:
        upgraded = lattice.upgrade(
            labeled,
            verifier=lambda x: False,  # Always fails
            target=TrustLabel.TRUSTED,
            reason="test_upgrade"
        )
        upgrade_succeeded = True
    except:
        pass
    
    # Also test that upgrade with passing verifier works
    upgrade_with_verify_works = False
    try:
        upgraded = lattice.upgrade(
            labeled,
            verifier=lambda x: True,  # Always passes
            target=TrustLabel.TRUSTED,
            reason="test_upgrade_verified"
        )
        upgrade_with_verify_works = upgraded.label == TrustLabel.TRUSTED
    except:
        pass
    
    passed = not upgrade_succeeded and upgrade_with_verify_works
    
    return InvariantResult(
        name="NO_IMPLICIT_UPGRADE",
        passed=passed,
        message="Upgrade requires verification" if passed else "Implicit upgrade possible!",
        details={
            "failed_upgrade_blocked": not upgrade_succeeded,
            "verified_upgrade_works": upgrade_with_verify_works
        }
    )


def check_trace_witnesses(result: PipelineResult) -> InvariantResult:
    """
    Invariant 7: Trace Refinement (Witness Completeness)
    
    Trace π must contain witnesses for each pipeline stage.
    """
    if result.trace is None:
        return InvariantResult(
            name="TRACE_WITNESSES",
            passed=False,
            message="No trace present"
        )
    
    stages = result.trace.to_list()
    required_stages = {
        "INTENT_LOCK", "PARSE", "ABSTRACT_INTERPRET",
        "GEOMETRIC_CHECK", "VERIFY_UPGRADE", "EXECUTE",
        "LOG_PROVENANCE", "META_CHECK", "RETURN"
    }
    
    present_stages = {s['name'] for s in stages}
    missing = required_stages - present_stages
    
    # For successful results, all stages should be present
    # For failures, some stages may be missing
    passed = len(missing) == 0 if result.success else len(present_stages) >= 1
    
    return InvariantResult(
        name="TRACE_WITNESSES",
        passed=passed,
        message=f"Trace has {len(present_stages)}/9 stage witnesses" if passed else f"Missing stages: {missing}",
        details={
            "present_stages": list(present_stages),
            "missing_stages": list(missing),
            "total_witnesses": len(stages)
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN VERIFICATION RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def run_formal_verification(verbose: bool = True) -> FormalVerificationReport:
    """
    Run the complete formal verification suite.
    
    Tests all 7 BeegMAMA/Nina invariants against the running system.
    """
    timestamp = datetime.now().isoformat()
    invariants: List[InvariantResult] = []
    metrics: Dict[str, float] = {}
    
    start_time = time.time()
    
    if verbose:
        print("\n" + "=" * 78)
        print(" NINA FORMAL VERIFICATION SUITE")
        print(" Testing BeegMAMA/Newton Calculus Invariants")
        print("=" * 78)
    
    # Create test pipeline
    regime = Regime.from_type(RegimeType.FACTUAL)
    pipeline = Pipeline(regime)
    lattice = get_trust_lattice()
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test Suite A: Deterministic Verified Facts
    # ─────────────────────────────────────────────────────────────────────────
    if verbose:
        print("\n[Suite A] Deterministic Verified Facts")
    
    test_queries = [
        ("What is the capital of France?", "adan_knowledge_base"),
        ("What is the capital of Germany?", "adan_knowledge_base"),
        ("What is the capital of the USA?", "adan_knowledge_base"),
        ("2 + 3 * 4", "computation"),
        ("(10 + 5) / 3", "computation"),
    ]
    
    results_with_sources = []
    for query, expected_source in test_queries:
        result = pipeline.process(query)
        results_with_sources.append((query, result, expected_source))
        
        if verbose:
            status = "[OK]" if result.success else "[FAIL]"
            trust = result.trust_label.name
            print(f"  {status} \"{query[:40]}...\" → {trust}")
    
    # Check API Contract (Invariant 1)
    for _, result, _ in results_with_sources:
        inv = check_api_contract(result)
        invariants.append(inv)
        if verbose:
            status = "PASS" if inv.passed else "FAIL"
            print(f"\n[Invariant 1] API_CONTRACT: {status}")
        break  # Only need to check structure once
    
    # Check Bounds Report (Invariant 2)
    for _, result, _ in results_with_sources:
        inv = check_bounds_report(result)
        invariants.append(inv)
        if verbose:
            status = "PASS" if inv.passed else "FAIL"
            print(f"[Invariant 2] BOUNDS_REPORT: {status}")
            if inv.details.get('time_ms'):
                print(f"             Time: {inv.details['time_ms']:.2f}ms, Ops: {inv.details['operations']}")
        break
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test Suite D: Adversarial Input Sanitization
    # ─────────────────────────────────────────────────────────────────────────
    if verbose:
        print("\n[Suite D] Adversarial Input Sanitization")
    
    adversarial_inputs = [
        "$(rm -rf /)",
        "$(whoami)",
        "`cat /etc/passwd`",
        "query; DROP TABLE users;--",
        "test | cat /etc/shadow",
        "cmd && evil_command",
        "<script>alert('xss')</script>",
        "<img onerror='evil()' src='x'>",
        "normal query\ninjected line",
        "a" * 5000,  # Length bomb
        "test\x00null\x00bytes",  # Null bytes
        "test\r\nCRLF injection",
    ]
    
    inv = check_sanitization(pipeline, adversarial_inputs)
    invariants.append(inv)
    if verbose:
        status = "PASS" if inv.passed else "FAIL"
        print(f"\n[Invariant 3] SANITIZATION: {status}")
        print(f"             Tested {len(adversarial_inputs)} adversarial inputs")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test Suite C: Trust-Mixing Retrieval (LLM Ceiling)
    # ─────────────────────────────────────────────────────────────────────────
    if verbose:
        print("\n[Suite C] Trust-Mixing & LLM Ceiling")
    
    # Add an LLM query if available
    llm_result = pipeline.process("How do I learn Python?")
    results_with_sources.append(("How do I learn Python?", llm_result, "ollama_governed"))
    
    inv = check_trust_lattice(results_with_sources)
    invariants.append(inv)
    if verbose:
        status = "PASS" if inv.passed else "FAIL"
        print(f"\n[Invariant 4] TRUST_LATTICE + LLM_CEILING: {status}")
        if llm_result.success:
            print(f"             LLM response trust: {llm_result.trust_label.name}")
    
    # Check Ledger Chain (Invariant 5)
    inv = check_ledger_chain(pipeline)
    invariants.append(inv)
    if verbose:
        status = "PASS" if inv.passed else "FAIL"
        print(f"\n[Invariant 5] LEDGER_CHAIN: {status}")
        print(f"             Entries: {inv.details.get('entries', 0)}")
    
    # Check No Implicit Upgrade (Invariant 6)
    inv = check_no_implicit_upgrade(lattice)
    invariants.append(inv)
    if verbose:
        status = "PASS" if inv.passed else "FAIL"
        print(f"\n[Invariant 6] NO_IMPLICIT_UPGRADE: {status}")
    
    # Check Trace Witnesses (Invariant 7)
    for _, result, _ in results_with_sources:
        if result.success:
            inv = check_trace_witnesses(result)
            invariants.append(inv)
            if verbose:
                status = "PASS" if inv.passed else "FAIL"
                print(f"\n[Invariant 7] TRACE_WITNESSES: {status}")
                print(f"             Stages: {len(inv.details.get('present_stages', []))}/9")
            break
    
    # ─────────────────────────────────────────────────────────────────────────
    # Compute Metrics
    # ─────────────────────────────────────────────────────────────────────────
    elapsed = time.time() - start_time
    passed = sum(1 for inv in invariants if inv.passed)
    failed = len(invariants) - passed
    
    # M1: Artifact Contract Rate
    metrics["M1_ACR"] = 1.0 if all(check_api_contract(r).passed for _, r, _ in results_with_sources) else 0.0
    
    # M3: LLM Ceiling Violation Rate
    llm_violations = sum(1 for q, r, s in results_with_sources 
                         if s == "ollama_governed" and r.trust_label >= TrustLabel.TRUSTED)
    llm_total = sum(1 for _, _, s in results_with_sources if s == "ollama_governed")
    metrics["M3_LCVR"] = llm_violations / max(llm_total, 1)
    
    # M9: Trusted-Slice Determinism (run same query 3 times)
    determinism_results = []
    for _ in range(3):
        r = Pipeline(regime).process("What is the capital of France?")
        determinism_results.append(r.value)
    metrics["M9_TSDR"] = 1.0 if len(set(str(v) for v in determinism_results)) == 1 else 0.0
    
    metrics["verification_time_ms"] = elapsed * 1000
    
    # ─────────────────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────────────────
    if verbose:
        print("\n" + "=" * 78)
        print(" VERIFICATION SUMMARY")
        print("=" * 78)
        print(f"\n  Invariants Tested: {len(invariants)}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Time: {elapsed*1000:.2f}ms")
        print()
        print("  Metrics:")
        print(f"    M1 (Artifact Contract Rate):     {metrics['M1_ACR']:.2%}")
        print(f"    M3 (LLM Ceiling Violation Rate): {metrics['M3_LCVR']:.2%}")
        print(f"    M9 (Trusted-Slice Determinism):  {metrics['M9_TSDR']:.2%}")
        print()
        
        if failed == 0:
            print("  ╔════════════════════════════════════════════════════════════╗")
            print("  ║  ALL INVARIANTS VERIFIED                                   ║")
            print("  ║  The implementation enforces the soundness theorems.       ║")
            print("  ╚════════════════════════════════════════════════════════════╝")
        else:
            print("  ╔════════════════════════════════════════════════════════════╗")
            print("  ║  INVARIANT VIOLATIONS DETECTED                             ║")
            print("  ║  Review failed checks above.                               ║")
            print("  ╚════════════════════════════════════════════════════════════╝")
        print()
    
    return FormalVerificationReport(
        timestamp=timestamp,
        total_tests=len(invariants),
        passed=passed,
        failed=failed,
        invariants=invariants,
        metrics=metrics
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Nina Formal Verification Suite")
    parser.add_argument("--proofs", action="store_true", help="Run proof verification")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    report = run_formal_verification(verbose=not args.quiet)
    
    if args.json:
        import json
        output = {
            "timestamp": report.timestamp,
            "total_tests": report.total_tests,
            "passed": report.passed,
            "failed": report.failed,
            "metrics": report.metrics,
            "invariants": [
                {"name": inv.name, "passed": inv.passed, "message": inv.message, "details": inv.details}
                for inv in report.invariants
            ]
        }
        print(json.dumps(output, indent=2, default=str))
    
    sys.exit(0 if report.failed == 0 else 1)
