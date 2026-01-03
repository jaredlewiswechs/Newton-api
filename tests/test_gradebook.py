#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON VERIFIED GRADEBOOK - Test Suite

Tests for the verified gradebook application that enforces:
1. Grade range constraint: 0 <= grade <= 100
2. Final grade immutability: submitted grades cannot be changed

Uses property-based testing with Hypothesis to prove constraints hold.

Run tests:
    pytest tests/test_gradebook.py -v
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import time
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tinytalk_py.gradebook import (
    Gradebook,
    get_gradebook,
    get_gradebook_constraints,
    GradeEntry,
    GradeStatus,
    CryptographicProof,
    MIN_GRADE,
    MAX_GRADE,
)
from tinytalk_py.core import LawViolation


# ═══════════════════════════════════════════════════════════════════════════════
# TEST FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def gradebook():
    """Provide a fresh Gradebook instance for testing."""
    return get_gradebook()


@pytest.fixture
def populated_gradebook():
    """Provide a Gradebook with some initial data."""
    gb = get_gradebook()
    gb.add_grade("student_001", "Math Quiz 1", 85)
    gb.add_grade("student_001", "Math Quiz 2", 90)
    gb.add_grade("student_002", "Math Quiz 1", 78)
    return gb


# ═══════════════════════════════════════════════════════════════════════════════
# INSTANTIATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInstantiation:
    """Tests for gradebook instantiation."""
    
    def test_instantiation_time(self):
        """Test that gradebook instantiates in under 60 seconds."""
        start_time = time.time()
        gradebook = get_gradebook()
        elapsed = time.time() - start_time
        
        assert elapsed < 60, f"Instantiation took {elapsed:.2f}s, expected < 60s"
        assert gradebook is not None
    
    def test_factory_function(self):
        """Test that factory function returns Gradebook instance."""
        gradebook = get_gradebook()
        assert isinstance(gradebook, Gradebook)
    
    def test_initial_state(self, gradebook):
        """Test initial state of empty gradebook."""
        assert len(gradebook.grades) == 0
        assert len(gradebook.audit_trail) == 0
        stats = gradebook.get_statistics()
        assert stats['total_entries'] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# GRADE RANGE CONSTRAINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestGradeRangeConstraint:
    """Tests for the grade range constraint (0 <= grade <= 100)."""
    
    def test_valid_grade_middle(self, gradebook):
        """Test that valid middle-range grades are accepted."""
        result = gradebook.add_grade("student_001", "Test", 50)
        assert result['success'] is True
        assert result['entry']['grade'] == 50
    
    def test_valid_grade_boundary_low(self, gradebook):
        """Test that grade 0 (boundary) is accepted."""
        result = gradebook.add_grade("student_001", "Test", 0)
        assert result['success'] is True
        assert result['entry']['grade'] == 0
    
    def test_valid_grade_boundary_high(self, gradebook):
        """Test that grade 100 (boundary) is accepted."""
        result = gradebook.add_grade("student_001", "Test", 100)
        assert result['success'] is True
        assert result['entry']['grade'] == 100
    
    def test_invalid_grade_above_100(self, gradebook):
        """Test that grades above 100 are rejected (finfr)."""
        with pytest.raises(LawViolation) as exc_info:
            gradebook.add_grade("student_001", "Test", 101)
        
        # Grade should not be stored
        assert len(gradebook.grades) == 0
    
    def test_invalid_grade_below_0(self, gradebook):
        """Test that grades below 0 are rejected (finfr)."""
        with pytest.raises(LawViolation) as exc_info:
            gradebook.add_grade("student_001", "Test", -1)
        
        # Grade should not be stored
        assert len(gradebook.grades) == 0
    
    def test_invalid_grade_extreme_high(self, gradebook):
        """Test rejection of extremely high grades."""
        with pytest.raises(LawViolation):
            gradebook.add_grade("student_001", "Test", 150)
    
    def test_invalid_grade_extreme_low(self, gradebook):
        """Test rejection of extremely low grades."""
        with pytest.raises(LawViolation):
            gradebook.add_grade("student_001", "Test", -50)
    
    @given(st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False))
    @settings(max_examples=50)
    def test_property_valid_grades_accepted(self, grade):
        """Property: Any grade in [0, 100] should be accepted."""
        gradebook = get_gradebook()
        result = gradebook.add_grade("student", "test", grade)
        assert result['success'] is True
        assert result['entry']['grade'] == grade
    
    @given(st.floats(min_value=100.01, max_value=1000, allow_nan=False, allow_infinity=False))
    @settings(max_examples=50)
    def test_property_high_grades_rejected(self, grade):
        """Property: Any grade > 100 should be rejected."""
        gradebook = get_gradebook()
        with pytest.raises(LawViolation):
            gradebook.add_grade("student", "test", grade)
    
    @given(st.floats(min_value=-1000, max_value=-0.01, allow_nan=False, allow_infinity=False))
    @settings(max_examples=50)
    def test_property_low_grades_rejected(self, grade):
        """Property: Any grade < 0 should be rejected."""
        gradebook = get_gradebook()
        with pytest.raises(LawViolation):
            gradebook.add_grade("student", "test", grade)


# ═══════════════════════════════════════════════════════════════════════════════
# FINAL GRADE IMMUTABILITY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestFinalGradeImmutability:
    """Tests for the final grade immutability constraint."""
    
    def test_draft_grade_can_be_updated(self, gradebook):
        """Test that draft grades can be updated."""
        gradebook.add_grade("student_001", "Test", 80)
        result = gradebook.update_grade("student_001", "Test", 85)
        
        assert result['success'] is True
        assert result['old_grade'] == 80
        assert result['new_grade'] == 85
    
    def test_submitted_grade_cannot_be_updated(self, gradebook):
        """Test that submitted grades cannot be updated (finfr)."""
        gradebook.add_grade("student_001", "Test", 80)
        gradebook.submit_grade("student_001", "Test")
        
        with pytest.raises(LawViolation) as exc_info:
            gradebook.update_grade("student_001", "Test", 85)
        
        # Grade should remain unchanged
        grade = gradebook.get_grade("student_001", "Test")
        assert grade['grade'] == 80
    
    def test_submit_changes_status(self, gradebook):
        """Test that submitting changes status to SUBMITTED."""
        gradebook.add_grade("student_001", "Test", 80)
        
        # Before submit
        grade = gradebook.get_grade("student_001", "Test")
        assert grade['status'] == GradeStatus.DRAFT.value
        
        # Submit
        result = gradebook.submit_grade("student_001", "Test")
        
        # After submit
        grade = gradebook.get_grade("student_001", "Test")
        assert grade['status'] == GradeStatus.SUBMITTED.value
        assert grade['is_final'] is True
    
    def test_submit_sets_timestamp(self, gradebook):
        """Test that submitting sets the submitted_at timestamp."""
        gradebook.add_grade("student_001", "Test", 80)
        result = gradebook.submit_grade("student_001", "Test")
        
        assert result['entry']['submitted_at'] is not None
        assert result['entry']['submitted_at'] > 0
    
    def test_cannot_submit_already_submitted(self, gradebook):
        """Test that you cannot submit an already submitted grade."""
        gradebook.add_grade("student_001", "Test", 80)
        gradebook.submit_grade("student_001", "Test")
        
        with pytest.raises(ValueError, match="already submitted"):
            gradebook.submit_grade("student_001", "Test")
    
    def test_cannot_add_grade_over_submitted(self, gradebook):
        """Test that you cannot add a grade to overwrite a submitted one."""
        gradebook.add_grade("student_001", "Test", 80)
        gradebook.submit_grade("student_001", "Test")
        
        with pytest.raises(LawViolation):
            gradebook.add_grade("student_001", "Test", 85)


# ═══════════════════════════════════════════════════════════════════════════════
# CRYPTOGRAPHIC PROOF TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCryptographicProofs:
    """Tests for cryptographic proof generation."""
    
    def test_add_grade_generates_proof(self, gradebook):
        """Test that add_grade generates a proof."""
        result = gradebook.add_grade("student_001", "Test", 80)
        
        assert 'proof' in result
        assert result['proof']['operation'] == 'add_grade'
        assert result['proof']['verified'] is True
    
    def test_update_grade_generates_proof(self, gradebook):
        """Test that update_grade generates a proof."""
        gradebook.add_grade("student_001", "Test", 80)
        result = gradebook.update_grade("student_001", "Test", 85)
        
        assert 'proof' in result
        assert result['proof']['operation'] == 'update_grade'
        assert result['proof']['verified'] is True
    
    def test_submit_grade_generates_proof(self, gradebook):
        """Test that submit_grade generates a proof."""
        gradebook.add_grade("student_001", "Test", 80)
        result = gradebook.submit_grade("student_001", "Test")
        
        assert 'proof' in result
        assert result['proof']['operation'] == 'submit_grade'
        assert result['proof']['verified'] is True
    
    def test_proof_has_hashes(self, gradebook):
        """Test that proofs include input and result hashes."""
        result = gradebook.add_grade("student_001", "Test", 80)
        proof = result['proof']
        
        assert 'input_hash' in proof
        assert 'result_hash' in proof
        assert len(proof['input_hash']) == 16  # SHA256 truncated to 16 chars
        assert len(proof['result_hash']) == 16
    
    def test_proof_has_merkle_root(self, gradebook):
        """Test that proofs include Merkle root."""
        result = gradebook.add_grade("student_001", "Test", 80)
        proof = result['proof']
        
        assert 'merkle_root' in proof
        assert proof['merkle_root'] is not None
    
    def test_proof_has_timestamp(self, gradebook):
        """Test that proofs include timestamp."""
        before = time.time()
        result = gradebook.add_grade("student_001", "Test", 80)
        after = time.time()
        
        proof = result['proof']
        assert before <= proof['timestamp'] <= after
        assert 'timestamp_iso' in proof
    
    def test_proof_has_constraint_checks(self, gradebook):
        """Test that proofs include constraint check results."""
        result = gradebook.add_grade("student_001", "Test", 80)
        proof = result['proof']
        
        assert 'constraint_checks' in proof
        assert len(proof['constraint_checks']) > 0
        
        for check in proof['constraint_checks']:
            assert 'constraint_id' in check
            assert 'passed' in check
            assert check['passed'] is True


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT TRAIL TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAuditTrail:
    """Tests for the audit trail."""
    
    def test_empty_audit_trail_initially(self, gradebook):
        """Test that audit trail starts empty."""
        trail = gradebook.get_audit_trail()
        assert len(trail) == 0
    
    def test_operations_recorded_in_audit_trail(self, gradebook):
        """Test that operations are recorded in audit trail."""
        gradebook.add_grade("student_001", "Test 1", 80)
        gradebook.add_grade("student_002", "Test 1", 85)
        gradebook.update_grade("student_001", "Test 1", 82)
        
        trail = gradebook.get_audit_trail()
        assert len(trail) == 3
    
    def test_audit_trail_order(self, gradebook):
        """Test that audit trail is in chronological order."""
        gradebook.add_grade("student_001", "Test 1", 80)
        time.sleep(0.01)  # Small delay to ensure different timestamps
        gradebook.add_grade("student_002", "Test 1", 85)
        
        trail = gradebook.get_audit_trail()
        assert trail[0]['timestamp'] <= trail[1]['timestamp']
    
    def test_audit_trail_immutable_on_failure(self, gradebook):
        """Test that failed operations don't appear in audit trail."""
        gradebook.add_grade("student_001", "Test", 80)
        
        try:
            gradebook.add_grade("student_002", "Test", 150)  # Invalid, will fail
        except LawViolation:
            pass
        
        trail = gradebook.get_audit_trail()
        assert len(trail) == 1  # Only the valid operation


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRITY VERIFICATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegrityVerification:
    """Tests for integrity verification."""
    
    def test_verify_empty_gradebook(self, gradebook):
        """Test verification of empty gradebook."""
        result = gradebook.verify_integrity()
        assert result['verified'] is True
        assert result['total_entries'] == 0
        assert result['violations'] == []
    
    def test_verify_valid_gradebook(self, populated_gradebook):
        """Test verification of valid populated gradebook."""
        result = populated_gradebook.verify_integrity()
        assert result['verified'] is True
        assert result['total_entries'] == 3
        assert result['violations'] == []
    
    def test_verify_grade_method(self, gradebook):
        """Test the verify_grade method."""
        # Valid grades
        result = gradebook.verify_grade(50)
        assert result['verified'] is True
        
        result = gradebook.verify_grade(0)
        assert result['verified'] is True
        
        result = gradebook.verify_grade(100)
        assert result['verified'] is True
        
        # Invalid grades
        result = gradebook.verify_grade(101)
        assert result['verified'] is False
        
        result = gradebook.verify_grade(-1)
        assert result['verified'] is False


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestQueries:
    """Tests for query methods."""
    
    def test_get_grade(self, populated_gradebook):
        """Test getting a specific grade."""
        grade = populated_gradebook.get_grade("student_001", "Math Quiz 1")
        assert grade is not None
        assert grade['grade'] == 85
    
    def test_get_nonexistent_grade(self, populated_gradebook):
        """Test getting a nonexistent grade."""
        grade = populated_gradebook.get_grade("student_999", "Unknown")
        assert grade is None
    
    def test_get_student_grades(self, populated_gradebook):
        """Test getting all grades for a student."""
        grades = populated_gradebook.get_student_grades("student_001")
        assert len(grades) == 2
    
    def test_get_assignment_grades(self, populated_gradebook):
        """Test getting all grades for an assignment."""
        grades = populated_gradebook.get_assignment_grades("Math Quiz 1")
        assert len(grades) == 2
    
    def test_get_all_grades(self, populated_gradebook):
        """Test getting all grades."""
        grades = populated_gradebook.get_all_grades()
        assert len(grades) == 3
    
    def test_calculate_average(self, populated_gradebook):
        """Test calculating student average."""
        avg = populated_gradebook.calculate_average("student_001")
        assert avg == 87.5  # (85 + 90) / 2
    
    def test_calculate_average_nonexistent_student(self, populated_gradebook):
        """Test calculating average for nonexistent student."""
        avg = populated_gradebook.calculate_average("student_999")
        assert avg is None


# ═══════════════════════════════════════════════════════════════════════════════
# STATISTICS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestStatistics:
    """Tests for statistics calculation."""
    
    def test_statistics_populated(self, populated_gradebook):
        """Test statistics on populated gradebook."""
        stats = populated_gradebook.get_statistics()
        
        assert stats['total_entries'] == 3
        assert stats['submitted_count'] == 0
        assert stats['draft_count'] == 3
        assert stats['min'] == 78
        assert stats['max'] == 90
    
    def test_statistics_with_submitted(self, populated_gradebook):
        """Test statistics with submitted grades."""
        populated_gradebook.submit_grade("student_001", "Math Quiz 1")
        
        stats = populated_gradebook.get_statistics()
        assert stats['submitted_count'] == 1
        assert stats['draft_count'] == 2


# ═══════════════════════════════════════════════════════════════════════════════
# CDL CONSTRAINTS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCDLConstraints:
    """Tests for CDL constraint export."""
    
    def test_get_constraints(self):
        """Test that get_gradebook_constraints returns valid constraints."""
        constraints = get_gradebook_constraints()
        
        assert isinstance(constraints, list)
        assert len(constraints) >= 2
    
    def test_constraint_structure(self):
        """Test that constraints have correct structure."""
        constraints = get_gradebook_constraints()
        
        # Check grade min constraint
        min_constraint = constraints[0]
        assert min_constraint['field'] == 'grade'
        assert min_constraint['operator'] == 'ge'
        assert min_constraint['value'] == MIN_GRADE
        
        # Check grade max constraint
        max_constraint = constraints[1]
        assert max_constraint['field'] == 'grade'
        assert max_constraint['operator'] == 'le'
        assert max_constraint['value'] == MAX_GRADE


# ═══════════════════════════════════════════════════════════════════════════════
# FINGERPRINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestFingerprints:
    """Tests for cryptographic fingerprints."""
    
    def test_entry_has_fingerprint(self, gradebook):
        """Test that grade entries have fingerprints."""
        result = gradebook.add_grade("student_001", "Test", 80)
        assert result['entry']['fingerprint'] is not None
        assert len(result['entry']['fingerprint']) == 16
    
    def test_fingerprint_changes_on_update(self, gradebook):
        """Test that fingerprint changes when grade is updated."""
        result1 = gradebook.add_grade("student_001", "Test", 80)
        fingerprint1 = result1['entry']['fingerprint']
        
        result2 = gradebook.update_grade("student_001", "Test", 85)
        fingerprint2 = result2['entry']['fingerprint']
        
        assert fingerprint1 != fingerprint2
    
    def test_fingerprint_changes_on_submit(self, gradebook):
        """Test that fingerprint changes when grade is submitted."""
        result1 = gradebook.add_grade("student_001", "Test", 80)
        fingerprint1 = result1['entry']['fingerprint']
        
        result2 = gradebook.submit_grade("student_001", "Test")
        fingerprint2 = result2['entry']['fingerprint']
        
        assert fingerprint1 != fingerprint2


# ═══════════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
