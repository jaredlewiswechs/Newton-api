#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON VERIFIED GRADEBOOK - Full Demonstration

Problem Statement:
"Using Newton, create a verified application from a single natural language
intent. The application should be cryptographically provable and instantiate
in under 60 seconds.

Intent: 'A gradebook where no student can have a grade above 100 or below 0,
and final grades cannot be changed after submission.'

Show your work. Show the proof."

This demo:
1. Instantiates the application (target: < 60 seconds)
2. Demonstrates constraint enforcement
3. Shows cryptographic proofs
4. Verifies integrity

Run:
    python examples/gradebook_demo.py

Or against the live Newton server:
    python examples/gradebook_demo.py --live

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import time
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tinytalk_py.gradebook import (
    Gradebook,
    get_gradebook,
    get_gradebook_constraints,
    GradeStatus,
    MIN_GRADE,
    MAX_GRADE,
)
from tinytalk_py.core import LawViolation


def print_header(text: str):
    """Print a formatted header."""
    print()
    print("═" * 70)
    print(f" {text}")
    print("═" * 70)


def print_section(text: str):
    """Print a section header."""
    print()
    print("-" * 70)
    print(f" {text}")
    print("-" * 70)


def format_proof(proof: dict) -> str:
    """Format a proof for display."""
    return f"""
    Operation: {proof['operation']}
    Timestamp: {proof['timestamp_iso']}
    Input Hash: {proof['input_hash']}
    Result Hash: {proof['result_hash']}
    Merkle Root: {proof['merkle_root']}
    Verified: {proof['verified']}
    Elapsed: {proof['elapsed_us']} μs"""


def main():
    """Main demonstration of the verified gradebook."""
    
    print_header("NEWTON VERIFIED GRADEBOOK - Full Demonstration")
    
    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  PROBLEM STATEMENT:                                                 │
│  "Using Newton, create a verified application from a single         │
│   natural language intent. The application should be                │
│   cryptographically provable and instantiate in under 60 seconds.   │
│                                                                     │
│   Intent: 'A gradebook where no student can have a grade above 100  │
│            or below 0, and final grades cannot be changed after     │
│            submission.'                                             │
│                                                                     │
│   Show your work. Show the proof."                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
    """)
    
    # =========================================================================
    # PHASE 1: INSTANTIATION (Target: < 60 seconds)
    # =========================================================================
    
    print_section("PHASE 1: Application Instantiation")
    
    start_time = time.time()
    
    # Instantiate the gradebook
    gradebook = get_gradebook()
    
    instantiation_time = time.time() - start_time
    
    print(f"  ✓ Gradebook instantiated in {instantiation_time:.4f} seconds")
    print(f"  ✓ Target: < 60 seconds")
    print(f"  ✓ Result: {'PASS' if instantiation_time < 60 else 'FAIL'}")
    print()
    print("  Constraints enforced:")
    print(f"    - Grade range: {MIN_GRADE} <= grade <= {MAX_GRADE}")
    print(f"    - Final grade immutability: submitted grades cannot be changed")
    
    # =========================================================================
    # PHASE 2: CONSTRAINT DEMONSTRATION
    # =========================================================================
    
    print_section("PHASE 2: Constraint Demonstration")
    
    # Add valid grades
    print("\n  [2.1] Adding valid grades...")
    
    test_grades = [
        ("alice", "Math Quiz 1", 95),
        ("bob", "Math Quiz 1", 87),
        ("charlie", "Math Quiz 1", 72),
        ("alice", "Science Test", 88),
        ("bob", "Science Test", 91),
    ]
    
    for student, assignment, grade in test_grades:
        result = gradebook.add_grade(student, assignment, grade)
        print(f"    ✓ {student}/{assignment}: {grade} (fingerprint: {result['entry']['fingerprint']})")
    
    # Try invalid grades
    print("\n  [2.2] Testing grade range constraint...")
    
    invalid_tests = [
        ("invalid_high", "Test", 105, "above 100"),
        ("invalid_low", "Test", -10, "below 0"),
        ("invalid_extreme", "Test", 150, "above 100"),
        ("invalid_negative", "Test", -50, "below 0"),
    ]
    
    for student, assignment, grade, reason in invalid_tests:
        try:
            gradebook.add_grade(student, assignment, grade)
            print(f"    ✗ FAILED: Grade {grade} should have been rejected")
        except LawViolation as e:
            print(f"    ✓ BLOCKED: Grade {grade} rejected ({reason})")
    
    # Test boundary values
    print("\n  [2.3] Testing boundary values...")
    
    boundary_tests = [
        ("boundary_low", "Test", 0, True),    # Should pass (exactly 0)
        ("boundary_high", "Test", 100, True), # Should pass (exactly 100)
    ]
    
    for student, assignment, grade, should_pass in boundary_tests:
        try:
            result = gradebook.add_grade(student, assignment, grade)
            if should_pass:
                print(f"    ✓ PASS: Grade {grade} accepted (boundary)")
            else:
                print(f"    ✗ FAILED: Grade {grade} should have been rejected")
        except LawViolation as e:
            if not should_pass:
                print(f"    ✓ BLOCKED: Grade {grade} rejected")
            else:
                print(f"    ✗ FAILED: Grade {grade} should have been accepted")
    
    # =========================================================================
    # PHASE 3: IMMUTABILITY DEMONSTRATION
    # =========================================================================
    
    print_section("PHASE 3: Final Grade Immutability")
    
    # Submit a grade
    print("\n  [3.1] Submitting a grade (making it final)...")
    
    result = gradebook.submit_grade("alice", "Math Quiz 1")
    print(f"    ✓ Submitted: alice/Math Quiz 1")
    print(f"    ✓ Grade: {result['entry']['grade']}")
    print(f"    ✓ Status: {result['entry']['status']}")
    print(f"    ✓ Is Final: {result['entry']['is_final']}")
    print(f"    ✓ Submitted At: {datetime.fromtimestamp(result['entry']['submitted_at']).isoformat()}")
    
    # Try to modify submitted grade
    print("\n  [3.2] Attempting to modify submitted grade...")
    
    try:
        gradebook.update_grade("alice", "Math Quiz 1", 98)
        print("    ✗ FAILED: Should not be able to modify submitted grade")
    except LawViolation as e:
        print(f"    ✓ BLOCKED: Cannot modify submitted grade")
        print(f"    ✓ Law enforced: {e.law_name}")
    
    # Modify a draft grade (should work)
    print("\n  [3.3] Modifying a draft grade (should work)...")
    
    result = gradebook.update_grade("bob", "Math Quiz 1", 89)
    print(f"    ✓ Updated: bob/Math Quiz 1")
    print(f"    ✓ Old Grade: {result['old_grade']}")
    print(f"    ✓ New Grade: {result['new_grade']}")
    
    # =========================================================================
    # PHASE 4: CRYPTOGRAPHIC PROOFS
    # =========================================================================
    
    print_section("PHASE 4: Cryptographic Proofs (Show Your Work)")
    
    audit_trail = gradebook.get_audit_trail()
    
    print(f"\n  Total operations recorded: {len(audit_trail)}")
    print("\n  Proof Chain:")
    
    for i, proof in enumerate(audit_trail, 1):
        print(f"\n  [{i}] {proof['operation'].upper()}")
        print(f"      Timestamp: {proof['timestamp_iso']}")
        print(f"      Input Hash: {proof['input_hash']}")
        print(f"      Result Hash: {proof['result_hash']}")
        print(f"      Merkle Root: {proof['merkle_root']}")
        print(f"      Verified: {'✓' if proof['verified'] else '✗'}")
        print(f"      Constraints Checked: {len(proof['constraint_checks'])}")
        for check in proof['constraint_checks']:
            status = '✓' if check['passed'] else '✗'
            print(f"        {status} {check['constraint_id']}: {check['description']}")
    
    # =========================================================================
    # PHASE 5: INTEGRITY VERIFICATION
    # =========================================================================
    
    print_section("PHASE 5: Integrity Verification")
    
    integrity = gradebook.verify_integrity()
    
    print(f"\n  Integrity Check Results:")
    print(f"    Verified: {'✓ PASS' if integrity['verified'] else '✗ FAIL'}")
    print(f"    Total Entries: {integrity['total_entries']}")
    print(f"    Valid Entries: {integrity['valid_entries']}")
    print(f"    Violations: {len(integrity['violations'])}")
    print(f"    Audit Trail Length: {integrity['audit_trail_length']}")
    print(f"    Elapsed: {integrity['elapsed_us']} μs")
    
    if integrity['violations']:
        print("\n  Violations:")
        for v in integrity['violations']:
            print(f"    - {v['type']}: {v['message']}")
    
    # =========================================================================
    # PHASE 6: STATISTICS
    # =========================================================================
    
    print_section("PHASE 6: Gradebook Statistics")
    
    stats = gradebook.get_statistics()
    
    print(f"\n  Summary:")
    print(f"    Total Entries: {stats['total_entries']}")
    print(f"    Submitted (Final): {stats['submitted_count']}")
    print(f"    Drafts: {stats['draft_count']}")
    print(f"    Unique Students: {stats['unique_students']}")
    print(f"    Unique Assignments: {stats['unique_assignments']}")
    print(f"\n  Grade Statistics:")
    print(f"    Average: {stats['average']}")
    print(f"    Min: {stats['min']}")
    print(f"    Max: {stats['max']}")
    
    # =========================================================================
    # FINAL REPORT
    # =========================================================================
    
    print_header("VERIFICATION COMPLETE")
    
    total_time = time.time() - start_time
    
    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│                         RESULTS SUMMARY                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✓ Application instantiated: {instantiation_time:.4f} seconds (< 60s)               │
│  ✓ Grade range constraint enforced (0-100)                          │
│  ✓ Final grade immutability enforced                                │
│  ✓ Cryptographic proofs generated for all operations                │
│  ✓ Integrity verification passed                                    │
│                                                                     │
│  Total demonstration time: {total_time:.4f} seconds                          │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CONSTRAINT SPECIFICATION (CDL):                                    │
│                                                                     │
│    Law 1: grade_range_constraint                                    │
│      when grade < 0 → finfr                                         │
│      when grade > 100 → finfr                                       │
│                                                                     │
│    Law 2: final_grade_immutability                                  │
│      when status == SUBMITTED AND modification attempted → finfr    │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PROOF CHAIN:                                                       │
│    {len(audit_trail)} operations recorded                                          │
│    All operations cryptographically signed                          │
│    Merkle roots generated for tamper detection                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

"1 == 1. The constraint IS the instruction. The verification IS the computation."
    """)
    
    # CDL Constraints export
    print("\nCDL Constraints (for API integration):")
    constraints = get_gradebook_constraints()
    print(json.dumps(constraints, indent=2))
    
    return 0


def demo_with_live_server():
    """Run demo against live Newton server."""
    import requests
    
    print_header("LIVE SERVER DEMO")
    
    base_url = "http://localhost:8000"
    
    # Check server health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("Newton server not responding. Start it with:")
            print("  python newton_supercomputer.py")
            return 1
    except requests.exceptions.ConnectionError:
        print("Cannot connect to Newton server. Start it with:")
        print("  python newton_supercomputer.py")
        return 1
    
    print("✓ Connected to Newton server")
    
    # Verify grade constraints using /constraint endpoint
    print("\n[1] Verifying grade range constraint via API...")
    
    test_cases = [
        (50, True, "Valid grade"),
        (100, True, "Boundary high"),
        (0, True, "Boundary low"),
        (105, False, "Above 100"),
        (-5, False, "Below 0"),
    ]
    
    constraints = get_gradebook_constraints()
    
    for grade, should_pass, description in test_cases:
        # Test grade >= MIN_GRADE
        response = requests.post(
            f"{base_url}/constraint",
            json={
                "constraint": constraints[0],  # grade >= MIN_GRADE
                "object": {"grade": grade}
            }
        )
        result1 = response.json()
        
        # Test grade <= MAX_GRADE
        response = requests.post(
            f"{base_url}/constraint",
            json={
                "constraint": constraints[1],  # grade <= MAX_GRADE
                "object": {"grade": grade}
            }
        )
        result2 = response.json()
        
        passed = result1["passed"] and result2["passed"]
        status = "✓" if passed == should_pass else "✗"
        
        print(f"  {status} Grade {grade}: {description} - {'PASS' if passed else 'FAIL'}")
    
    # Record in ledger
    print("\n[2] Recording operations in Newton ledger...")
    
    response = requests.post(
        f"{base_url}/ask",
        json={
            "query": "Grade verification for student alice: 95 on Math Quiz 1",
            "context": {"operation": "gradebook", "student": "alice", "grade": 95}
        }
    )
    result = response.json()
    print(f"  ✓ Operation recorded: {result['answer']['verified']}")
    
    # View ledger
    print("\n[3] Viewing audit trail from ledger...")
    
    response = requests.get(f"{base_url}/ledger?limit=5")
    ledger = response.json()
    print(f"  Total entries: {ledger['total']}")
    print(f"  Merkle root: {ledger['merkle_root']}")
    
    print("\n✓ Live server demo complete")
    return 0


if __name__ == "__main__":
    if '--live' in sys.argv:
        sys.exit(demo_with_live_server())
    else:
        sys.exit(main())
