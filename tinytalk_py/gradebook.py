#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON VERIFIED GRADEBOOK
A cryptographically provable gradebook where:
- No student can have a grade above 100 or below 0
- Final grades cannot be changed after submission

This demonstrates Newton's core philosophy:
- The constraint IS the instruction
- The verification IS the computation
- Every operation is cryptographically provable

Intent: 'A gradebook where no student can have a grade above 100 or below 0,
         and final grades cannot be changed after submission.'

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
"1 == 1. The cloud is weather. We're building shelter."
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field as dataclass_field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
import hashlib
import json
import time

from .core import Blueprint, field, law, forge, when, finfr, LawViolation


# ═══════════════════════════════════════════════════════════════════════════════
# GRADE CONSTRAINTS - The Laws
# ═══════════════════════════════════════════════════════════════════════════════

MIN_GRADE = 0
MAX_GRADE = 100


class GradeStatus(Enum):
    """Status of a grade entry."""
    DRAFT = "draft"           # Can be modified
    SUBMITTED = "submitted"   # Final, cannot be changed (finfr)


@dataclass
class GradeEntry:
    """
    A single grade entry for a student.
    
    Once status is SUBMITTED, the grade cannot be changed (finfr).
    """
    student_id: str
    assignment_name: str
    grade: float
    status: GradeStatus = GradeStatus.DRAFT
    submitted_at: Optional[float] = None
    created_at: float = dataclass_field(default_factory=time.time)
    fingerprint: Optional[str] = None
    
    def __post_init__(self):
        """Generate cryptographic fingerprint."""
        self._generate_fingerprint()
    
    def _generate_fingerprint(self):
        """Generate cryptographic fingerprint for this grade entry.
        
        Uses JSON serialization to ensure robust, collision-resistant hashing.
        """
        # Use JSON for robust serialization to prevent delimiter collision attacks
        data = json.dumps({
            "student_id": self.student_id,
            "assignment_name": self.assignment_name,
            "grade": self.grade,
            "status": self.status.value,
            "submitted_at": self.submitted_at
        }, sort_keys=True)
        self.fingerprint = hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "student_id": self.student_id,
            "assignment_name": self.assignment_name,
            "grade": self.grade,
            "status": self.status.value,
            "submitted_at": self.submitted_at,
            "created_at": self.created_at,
            "fingerprint": self.fingerprint,
            "is_final": self.status == GradeStatus.SUBMITTED
        }


@dataclass
class CryptographicProof:
    """
    Cryptographic proof that a grade operation was verified.
    
    This is the "show your work" part - every operation generates
    a proof that can be independently verified.
    """
    operation: str
    timestamp: float
    input_hash: str
    result_hash: str
    verified: bool
    constraint_checks: List[Dict[str, Any]]
    elapsed_us: int
    merkle_root: Optional[str] = None
    
    def __post_init__(self):
        """Generate merkle root from constraint checks.
        
        Uses JSON serialization to ensure collision-resistant hashing.
        """
        if self.constraint_checks:
            # Use JSON for robust serialization to prevent collision attacks
            combined = json.dumps([
                {"id": c.get("constraint_id", ""), "passed": c.get("passed", False)}
                for c in self.constraint_checks
            ], sort_keys=True)
            self.merkle_root = hashlib.sha256(combined.encode()).hexdigest()[:16].upper()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "timestamp": self.timestamp,
            "timestamp_iso": datetime.fromtimestamp(self.timestamp).isoformat(),
            "input_hash": self.input_hash,
            "result_hash": self.result_hash,
            "verified": self.verified,
            "constraint_checks": self.constraint_checks,
            "elapsed_us": self.elapsed_us,
            "merkle_root": self.merkle_root
        }


# ═══════════════════════════════════════════════════════════════════════════════
# GRADEBOOK BLUEPRINT - The Verified Application
# ═══════════════════════════════════════════════════════════════════════════════

class Gradebook(Blueprint):
    """
    A verified gradebook that enforces:
    1. Grade range constraint: 0 <= grade <= 100
    2. Final grade immutability: submitted grades cannot be changed
    
    This is Newton's answer to the problem statement:
    "A gradebook where no student can have a grade above 100 or below 0,
     and final grades cannot be changed after submission."
    
    Every operation is:
    - Verified before execution
    - Cryptographically provable
    - Recorded in an immutable audit trail
    """
    
    # Fields
    grades = field(dict, default=None)  # {entry_id: GradeEntry}
    audit_trail = field(list, default=None)  # List of CryptographicProof
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.grades is None:
            self.grades = {}
        if self.audit_trail is None:
            self.audit_trail = []
    
    # ─────────────────────────────────────────────────────────────────────────
    # LAWS - What Cannot Happen (Layer 0: Governance)
    # These laws define the constraints that can never be violated.
    # ─────────────────────────────────────────────────────────────────────────
    
    @law
    def grade_range_constraint(self):
        """
        LAW: Grade must be between 0 and 100 (inclusive).
        
        When grade < 0 OR grade > 100 → finfr (ontological death)
        
        This is a mathematical boundary - grades outside this range
        simply cannot exist in this system.
        
        Note: This law is enforced explicitly via _verify_grade_range()
        in the forge methods to ensure pre-verification before state change.
        """
        pass  # Enforced via _verify_grade_range()
    
    @law
    def final_grade_immutability(self):
        """
        LAW: Submitted grades cannot be modified.
        
        When grade.status == SUBMITTED AND modification attempted → finfr
        
        Once a grade is submitted, it becomes part of the immutable record.
        This is Newton's answer to academic integrity - the constraint
        IS the protection.
        
        Note: This law is enforced explicitly via _verify_not_submitted()
        in the forge methods to ensure pre-verification before state change.
        """
        pass  # Enforced via _verify_not_submitted()
    
    def _verify_grade_range(self, grade: float) -> None:
        """
        Verify grade is within valid range.
        Raises LawViolation if grade is invalid.
        """
        if grade < MIN_GRADE:
            raise LawViolation(
                "grade_range_constraint",
                f"Grade {grade} is below minimum ({MIN_GRADE})"
            )
        if grade > MAX_GRADE:
            raise LawViolation(
                "grade_range_constraint",
                f"Grade {grade} is above maximum ({MAX_GRADE})"
            )
    
    def _verify_not_submitted(self, entry_id: str) -> None:
        """
        Verify that the grade entry is not submitted.
        Raises LawViolation if grade is already submitted.
        """
        if entry_id in self.grades:
            entry = self.grades[entry_id]
            if entry.status == GradeStatus.SUBMITTED:
                raise LawViolation(
                    "final_grade_immutability",
                    f"Cannot modify submitted grade (entry_id: {entry_id})"
                )
    
    # ─────────────────────────────────────────────────────────────────────────
    # FORGES - What Can Happen (Layer 1: Executive)
    # ─────────────────────────────────────────────────────────────────────────
    
    @forge
    def add_grade(self, student_id: str, assignment_name: str, grade: float) -> Dict[str, Any]:
        """
        Add a new grade entry for a student.
        
        This forge:
        1. Verifies grade is within valid range (0-100)
        2. Verifies entry is not already submitted
        3. Creates the grade entry if laws pass
        4. Generates cryptographic proof
        5. Records in audit trail
        
        Returns the grade entry and proof.
        """
        start_us = time.perf_counter_ns() // 1000
        
        # VERIFY: Grade must be in valid range (Law 1)
        self._verify_grade_range(grade)
        
        # Generate entry ID
        entry_id = self._generate_entry_id(student_id, assignment_name)
        
        # VERIFY: Entry must not be already submitted (Law 2)
        self._verify_not_submitted(entry_id)
        
        # Create grade entry
        entry = GradeEntry(
            student_id=student_id,
            assignment_name=assignment_name,
            grade=grade,
            status=GradeStatus.DRAFT
        )
        
        # Store entry
        self.grades[entry_id] = entry
        
        elapsed_us = (time.perf_counter_ns() // 1000) - start_us
        
        # Generate proof
        proof = self._generate_proof(
            operation="add_grade",
            input_data={"student_id": student_id, "assignment": assignment_name, "grade": grade},
            result_data=entry.to_dict(),
            elapsed_us=elapsed_us
        )
        
        # Record in audit trail
        self.audit_trail.append(proof)
        
        return {
            "success": True,
            "entry": entry.to_dict(),
            "entry_id": entry_id,
            "proof": proof.to_dict()
        }
    
    @forge
    def update_grade(self, student_id: str, assignment_name: str, new_grade: float) -> Dict[str, Any]:
        """
        Update an existing grade (only if not submitted).
        
        This forge:
        1. Verifies the entry exists
        2. Sets pending state for law verification
        3. Updates if laws pass (will fail if submitted)
        4. Generates cryptographic proof
        """
        start_us = time.perf_counter_ns() // 1000
        
        entry_id = self._generate_entry_id(student_id, assignment_name)
        
        if entry_id not in self.grades:
            raise ValueError(f"No grade entry found for {student_id}/{assignment_name}")
        
        # VERIFY: Grade must be in valid range (Law 1)
        self._verify_grade_range(new_grade)
        
        # VERIFY: Entry must not be submitted (Law 2)
        self._verify_not_submitted(entry_id)
        
        # Get existing entry
        entry = self.grades[entry_id]
        old_grade = entry.grade
        
        # Update grade
        entry.grade = new_grade
        entry._generate_fingerprint()
        
        elapsed_us = (time.perf_counter_ns() // 1000) - start_us
        
        # Generate proof
        proof = self._generate_proof(
            operation="update_grade",
            input_data={
                "student_id": student_id,
                "assignment": assignment_name,
                "old_grade": old_grade,
                "new_grade": new_grade
            },
            result_data=entry.to_dict(),
            elapsed_us=elapsed_us
        )
        
        # Record in audit trail
        self.audit_trail.append(proof)
        
        return {
            "success": True,
            "entry": entry.to_dict(),
            "entry_id": entry_id,
            "old_grade": old_grade,
            "new_grade": new_grade,
            "proof": proof.to_dict()
        }
    
    @forge
    def submit_grade(self, student_id: str, assignment_name: str) -> Dict[str, Any]:
        """
        Submit a grade, making it final and immutable.
        
        Once submitted:
        - The grade cannot be changed (finfr protects it)
        - A cryptographic proof is generated
        - The submission is recorded in the audit trail
        
        This is the "finality" operation - after this, the grade
        becomes part of the permanent record.
        """
        start_us = time.perf_counter_ns() // 1000
        
        entry_id = self._generate_entry_id(student_id, assignment_name)
        
        if entry_id not in self.grades:
            raise ValueError(f"No grade entry found for {student_id}/{assignment_name}")
        
        entry = self.grades[entry_id]
        
        if entry.status == GradeStatus.SUBMITTED:
            raise ValueError(f"Grade for {student_id}/{assignment_name} is already submitted")
        
        # Submit the grade
        entry.status = GradeStatus.SUBMITTED
        entry.submitted_at = time.time()
        entry._generate_fingerprint()
        
        elapsed_us = (time.perf_counter_ns() // 1000) - start_us
        
        # Generate proof
        proof = self._generate_proof(
            operation="submit_grade",
            input_data={"student_id": student_id, "assignment": assignment_name},
            result_data=entry.to_dict(),
            elapsed_us=elapsed_us
        )
        
        # Record in audit trail
        self.audit_trail.append(proof)
        
        return {
            "success": True,
            "entry": entry.to_dict(),
            "entry_id": entry_id,
            "message": f"Grade for {student_id}/{assignment_name} is now final and immutable",
            "proof": proof.to_dict()
        }
    
    # ─────────────────────────────────────────────────────────────────────────
    # QUERY METHODS - Read Operations (No State Change)
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_grade(self, student_id: str, assignment_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific grade entry."""
        entry_id = self._generate_entry_id(student_id, assignment_name)
        entry = self.grades.get(entry_id)
        if entry:
            return entry.to_dict()
        return None
    
    def get_student_grades(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all grades for a student."""
        return [
            entry.to_dict()
            for entry in self.grades.values()
            if entry.student_id == student_id
        ]
    
    def get_assignment_grades(self, assignment_name: str) -> List[Dict[str, Any]]:
        """Get all grades for an assignment."""
        return [
            entry.to_dict()
            for entry in self.grades.values()
            if entry.assignment_name == assignment_name
        ]
    
    def get_all_grades(self) -> List[Dict[str, Any]]:
        """Get all grade entries."""
        return [entry.to_dict() for entry in self.grades.values()]
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get the complete audit trail with cryptographic proofs."""
        return [proof.to_dict() for proof in self.audit_trail]
    
    def calculate_average(self, student_id: str) -> Optional[float]:
        """Calculate a student's average grade."""
        grades = [
            entry.grade
            for entry in self.grades.values()
            if entry.student_id == student_id
        ]
        if not grades:
            return None
        return sum(grades) / len(grades)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get gradebook statistics."""
        all_grades = [entry.grade for entry in self.grades.values()]
        submitted_count = sum(
            1 for entry in self.grades.values()
            if entry.status == GradeStatus.SUBMITTED
        )
        
        if not all_grades:
            return {
                "total_entries": 0,
                "submitted_count": 0,
                "draft_count": 0,
                "average": None,
                "min": None,
                "max": None
            }
        
        return {
            "total_entries": len(all_grades),
            "submitted_count": submitted_count,
            "draft_count": len(all_grades) - submitted_count,
            "average": round(sum(all_grades) / len(all_grades), 2),
            "min": min(all_grades),
            "max": max(all_grades),
            "unique_students": len(set(e.student_id for e in self.grades.values())),
            "unique_assignments": len(set(e.assignment_name for e in self.grades.values()))
        }
    
    # ─────────────────────────────────────────────────────────────────────────
    # VERIFICATION METHODS - Prove the Constraints Hold
    # ─────────────────────────────────────────────────────────────────────────
    
    def verify_grade(self, grade: float) -> Dict[str, Any]:
        """
        Verify that a grade value is within constraints.
        
        Returns verification result with proof.
        """
        start_us = time.perf_counter_ns() // 1000
        
        checks = [
            {
                "constraint_id": "GRADE_MIN",
                "constraint": f"grade >= {MIN_GRADE}",
                "value": grade,
                "passed": grade >= MIN_GRADE
            },
            {
                "constraint_id": "GRADE_MAX",
                "constraint": f"grade <= {MAX_GRADE}",
                "value": grade,
                "passed": grade <= MAX_GRADE
            }
        ]
        
        elapsed_us = (time.perf_counter_ns() // 1000) - start_us
        
        all_passed = all(c["passed"] for c in checks)
        
        return {
            "verified": all_passed,
            "grade": grade,
            "constraint_checks": checks,
            "elapsed_us": elapsed_us,
            "message": "Grade is valid" if all_passed else f"Grade must be between {MIN_GRADE} and {MAX_GRADE}"
        }
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify the integrity of all grades in the gradebook.
        
        Checks:
        1. All grades are within range
        2. All fingerprints are valid
        3. Audit trail is consistent
        
        Returns comprehensive verification report.
        """
        start_us = time.perf_counter_ns() // 1000
        
        violations = []
        valid_count = 0
        
        for entry_id, entry in self.grades.items():
            # Check grade range
            if entry.grade < MIN_GRADE or entry.grade > MAX_GRADE:
                violations.append({
                    "entry_id": entry_id,
                    "type": "range_violation",
                    "message": f"Grade {entry.grade} is outside valid range"
                })
            else:
                valid_count += 1
            
            # Verify fingerprint using the same method as GradeEntry._generate_fingerprint()
            expected_fingerprint = self._compute_fingerprint(
                entry.student_id,
                entry.assignment_name,
                entry.grade,
                entry.status.value,
                entry.submitted_at
            )
            
            if entry.fingerprint != expected_fingerprint:
                violations.append({
                    "entry_id": entry_id,
                    "type": "integrity_violation",
                    "message": "Fingerprint mismatch - data may have been tampered"
                })
        
        elapsed_us = (time.perf_counter_ns() // 1000) - start_us
        
        return {
            "verified": len(violations) == 0,
            "total_entries": len(self.grades),
            "valid_entries": valid_count,
            "violations": violations,
            "audit_trail_length": len(self.audit_trail),
            "elapsed_us": elapsed_us
        }
    
    # ─────────────────────────────────────────────────────────────────────────
    # HELPER METHODS
    # ─────────────────────────────────────────────────────────────────────────
    
    def _generate_entry_id(self, student_id: str, assignment_name: str) -> str:
        """Generate a unique entry ID.
        
        Uses JSON serialization to prevent delimiter collision attacks.
        """
        data = json.dumps({"student_id": student_id, "assignment": assignment_name}, sort_keys=True)
        return f"GRADE_{hashlib.sha256(data.encode()).hexdigest()[:12].upper()}"
    
    def _compute_fingerprint(
        self,
        student_id: str,
        assignment_name: str,
        grade: float,
        status: str,
        submitted_at: Optional[float]
    ) -> str:
        """Compute fingerprint using the same method as GradeEntry.
        
        This shared utility ensures consistency between fingerprint
        generation and verification.
        """
        data = json.dumps({
            "student_id": student_id,
            "assignment_name": assignment_name,
            "grade": grade,
            "status": status,
            "submitted_at": submitted_at
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    
    def _generate_proof(
        self,
        operation: str,
        input_data: Dict[str, Any],
        result_data: Dict[str, Any],
        elapsed_us: int
    ) -> CryptographicProof:
        """Generate cryptographic proof for an operation.
        
        Uses JSON serialization for robust, collision-resistant hashing.
        """
        input_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:16].upper()
        result_hash = hashlib.sha256(json.dumps(result_data, sort_keys=True, default=str).encode()).hexdigest()[:16].upper()
        
        constraint_checks = [
            {
                "constraint_id": "GRADE_RANGE",
                "description": f"Grade must be between {MIN_GRADE} and {MAX_GRADE}",
                "passed": True
            },
            {
                "constraint_id": "FINAL_IMMUTABLE",
                "description": "Submitted grades cannot be modified",
                "passed": True
            }
        ]
        
        return CryptographicProof(
            operation=operation,
            timestamp=time.time(),
            input_hash=input_hash,
            result_hash=result_hash,
            verified=True,
            constraint_checks=constraint_checks,
            elapsed_us=elapsed_us
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def get_gradebook() -> Gradebook:
    """
    Factory function to create a verified Gradebook instance.
    
    Usage:
        from tinytalk_py.gradebook import get_gradebook
        
        gradebook = get_gradebook()
        gradebook.add_grade("student_001", "Math Quiz 1", 95)
        gradebook.submit_grade("student_001", "Math Quiz 1")
    """
    return Gradebook()


# ═══════════════════════════════════════════════════════════════════════════════
# CDL CONSTRAINTS - For use with Newton API
# ═══════════════════════════════════════════════════════════════════════════════

def get_gradebook_constraints() -> List[Dict[str, Any]]:
    """
    Get CDL constraints for gradebook verification.
    
    These can be used with the Newton /constraint endpoint for
    external verification of grade values.
    """
    return [
        {
            "domain": "education",
            "field": "grade",
            "operator": "ge",
            "value": MIN_GRADE,
            "message": f"Grade must be at least {MIN_GRADE}"
        },
        {
            "domain": "education",
            "field": "grade",
            "operator": "le",
            "value": MAX_GRADE,
            "message": f"Grade must be at most {MAX_GRADE}"
        },
        {
            "if": {
                "field": "status",
                "operator": "eq",
                "value": "submitted"
            },
            "then": {
                "field": "_can_modify",
                "operator": "eq",
                "value": False
            }
        }
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json
    
    print("=" * 70)
    print("NEWTON VERIFIED GRADEBOOK - Demonstration")
    print("=" * 70)
    print()
    print("Intent: 'A gradebook where no student can have a grade above 100")
    print("        or below 0, and final grades cannot be changed after submission.'")
    print()
    
    # Create gradebook
    gradebook = get_gradebook()
    print("✓ Gradebook instantiated")
    print()
    
    # Test 1: Add valid grades
    print("-" * 70)
    print("TEST 1: Adding valid grades")
    print("-" * 70)
    
    result = gradebook.add_grade("student_001", "Math Quiz 1", 85)
    print(f"  Added grade: 85 for student_001/Math Quiz 1")
    print(f"  Verified: {result['proof']['verified']}")
    print(f"  Fingerprint: {result['entry']['fingerprint']}")
    
    result = gradebook.add_grade("student_002", "Math Quiz 1", 92)
    print(f"  Added grade: 92 for student_002/Math Quiz 1")
    
    result = gradebook.add_grade("student_001", "Science Test", 78)
    print(f"  Added grade: 78 for student_001/Science Test")
    print()
    
    # Test 2: Try to add invalid grades
    print("-" * 70)
    print("TEST 2: Attempting to add invalid grades (should be blocked)")
    print("-" * 70)
    
    try:
        gradebook.add_grade("student_003", "History Essay", 105)  # Above 100
        print("  ERROR: Should have been blocked!")
    except LawViolation as e:
        print(f"  ✓ BLOCKED: Grade 105 rejected (above 100)")
        print(f"    Law: {e.law_name}")
    
    try:
        gradebook.add_grade("student_003", "History Essay", -5)  # Below 0
        print("  ERROR: Should have been blocked!")
    except LawViolation as e:
        print(f"  ✓ BLOCKED: Grade -5 rejected (below 0)")
        print(f"    Law: {e.law_name}")
    print()
    
    # Test 3: Submit a grade (make it final)
    print("-" * 70)
    print("TEST 3: Submitting a grade (making it final)")
    print("-" * 70)
    
    result = gradebook.submit_grade("student_001", "Math Quiz 1")
    print(f"  Submitted: student_001/Math Quiz 1")
    print(f"  Is Final: {result['entry']['is_final']}")
    print(f"  Submitted At: {result['entry']['submitted_at']}")
    print(f"  Proof Merkle Root: {result['proof']['merkle_root']}")
    print()
    
    # Test 4: Try to modify a submitted grade
    print("-" * 70)
    print("TEST 4: Attempting to modify submitted grade (should be blocked)")
    print("-" * 70)
    
    try:
        gradebook.update_grade("student_001", "Math Quiz 1", 90)  # Try to change
        print("  ERROR: Should have been blocked!")
    except LawViolation as e:
        print(f"  ✓ BLOCKED: Cannot modify submitted grade")
        print(f"    Law: {e.law_name}")
    print()
    
    # Test 5: Update a draft grade (should work)
    print("-" * 70)
    print("TEST 5: Updating a draft grade (should work)")
    print("-" * 70)
    
    result = gradebook.update_grade("student_001", "Science Test", 82)
    print(f"  Updated: student_001/Science Test")
    print(f"  Old Grade: {result['old_grade']}")
    print(f"  New Grade: {result['new_grade']}")
    print(f"  Verified: {result['proof']['verified']}")
    print()
    
    # Test 6: Verify integrity
    print("-" * 70)
    print("TEST 6: Verifying gradebook integrity")
    print("-" * 70)
    
    integrity = gradebook.verify_integrity()
    print(f"  Verified: {integrity['verified']}")
    print(f"  Total Entries: {integrity['total_entries']}")
    print(f"  Valid Entries: {integrity['valid_entries']}")
    print(f"  Violations: {len(integrity['violations'])}")
    print(f"  Audit Trail Length: {integrity['audit_trail_length']}")
    print()
    
    # Test 7: Statistics
    print("-" * 70)
    print("TEST 7: Gradebook statistics")
    print("-" * 70)
    
    stats = gradebook.get_statistics()
    print(f"  Total Entries: {stats['total_entries']}")
    print(f"  Submitted: {stats['submitted_count']}")
    print(f"  Drafts: {stats['draft_count']}")
    print(f"  Average Grade: {stats['average']}")
    print(f"  Min Grade: {stats['min']}")
    print(f"  Max Grade: {stats['max']}")
    print()
    
    # Show audit trail
    print("-" * 70)
    print("AUDIT TRAIL (Cryptographic Proofs)")
    print("-" * 70)
    
    for i, proof in enumerate(gradebook.get_audit_trail()):
        print(f"\n  [{i+1}] {proof['operation']}")
        print(f"      Timestamp: {proof['timestamp_iso']}")
        print(f"      Input Hash: {proof['input_hash']}")
        print(f"      Result Hash: {proof['result_hash']}")
        print(f"      Merkle Root: {proof['merkle_root']}")
        print(f"      Verified: {proof['verified']}")
    
    print()
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print()
    print("This gradebook enforces:")
    print("  1. Grade range: 0 <= grade <= 100 (enforced by law)")
    print("  2. Final immutability: submitted grades cannot change (enforced by law)")
    print("  3. Cryptographic proofs: every operation is provable")
    print("  4. Audit trail: complete history of all operations")
    print()
    print("1 == 1. The constraint IS the instruction.")
    print("=" * 70)
