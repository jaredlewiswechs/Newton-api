#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
TRUST LATTICE TESTS
Test coverage for Paper Section 7
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from developer.forge.trust import (
    TrustLabel, TrustLattice, Labeled, UpgradeError,
    non_empty_verifier, type_verifier, range_verifier, pattern_verifier,
    always_true, always_false, get_trust_lattice
)


class TestTrustLabel:
    """Test TrustLabel enum and ordering."""
    
    def test_label_ordering(self):
        """Test that labels are properly ordered."""
        assert TrustLabel.UNTRUSTED < TrustLabel.VERIFIED
        assert TrustLabel.VERIFIED < TrustLabel.TRUSTED
        assert TrustLabel.TRUSTED < TrustLabel.KERNEL
    
    def test_label_comparison(self):
        """Test label comparison operators."""
        assert TrustLabel.UNTRUSTED <= TrustLabel.UNTRUSTED
        assert TrustLabel.UNTRUSTED <= TrustLabel.VERIFIED
        assert not (TrustLabel.TRUSTED <= TrustLabel.UNTRUSTED)
        
        assert TrustLabel.KERNEL >= TrustLabel.TRUSTED
        assert TrustLabel.KERNEL > TrustLabel.TRUSTED


class TestLabeled:
    """Test Labeled wrapper."""
    
    def test_create_labeled(self):
        """Test creating a labeled value."""
        labeled = Labeled(value="test", label=TrustLabel.UNTRUSTED, source="user")
        
        assert labeled.value == "test"
        assert labeled.label == TrustLabel.UNTRUSTED
        assert labeled.source == "user"
    
    def test_is_trusted(self):
        """Test is_trusted check."""
        untrusted = Labeled(value=1, label=TrustLabel.UNTRUSTED)
        verified = Labeled(value=2, label=TrustLabel.VERIFIED)
        trusted = Labeled(value=3, label=TrustLabel.TRUSTED)
        kernel = Labeled(value=4, label=TrustLabel.KERNEL)
        
        assert not untrusted.is_trusted()
        assert not verified.is_trusted()
        assert trusted.is_trusted()
        assert kernel.is_trusted()
    
    def test_is_verified(self):
        """Test is_verified check."""
        untrusted = Labeled(value=1, label=TrustLabel.UNTRUSTED)
        verified = Labeled(value=2, label=TrustLabel.VERIFIED)
        
        assert not untrusted.is_verified()
        assert verified.is_verified()


class TestTrustLattice:
    """Test the TrustLattice upgrade mechanism."""
    
    def test_label_untrusted(self):
        """Test labeling data as untrusted."""
        lattice = TrustLattice()
        
        labeled = lattice.untrusted("user data", "api")
        assert labeled.label == TrustLabel.UNTRUSTED
        assert labeled.source == "api"
    
    def test_label_kernel(self):
        """Test labeling data as kernel trust."""
        lattice = TrustLattice()
        
        labeled = lattice.kernel("invariant", "system")
        assert labeled.label == TrustLabel.KERNEL
    
    def test_upgrade_success(self):
        """Test successful upgrade via verification."""
        lattice = TrustLattice()
        
        # Start untrusted
        value = lattice.untrusted(42, "input")
        assert value.label == TrustLabel.UNTRUSTED
        
        # Upgrade with verifier that passes
        upgraded = lattice.upgrade(
            value,
            verifier=lambda x: x > 0,
            target_trust=TrustLabel.TRUSTED,
            verifier_name="positive_check"
        )
        
        assert upgraded.label == TrustLabel.TRUSTED
        assert upgraded.value == 42
        assert "positive_check" in str(upgraded.verification_trace)
    
    def test_upgrade_failure(self):
        """Test failed upgrade when verification fails."""
        lattice = TrustLattice()
        
        value = lattice.untrusted(-5, "input")
        
        with pytest.raises(UpgradeError) as exc_info:
            lattice.upgrade(
                value,
                verifier=lambda x: x > 0,  # Will fail for -5
                verifier_name="positive_check"
            )
        
        assert "positive_check" in str(exc_info.value)
    
    def test_no_implicit_upgrade(self):
        """Test that there's no implicit trust upgrade."""
        lattice = TrustLattice()
        
        untrusted = lattice.untrusted("data")
        
        # Cannot directly access as trusted
        with pytest.raises(UpgradeError):
            lattice.require_trust(untrusted, TrustLabel.TRUSTED)
    
    def test_already_trusted_no_change(self):
        """Test that upgrading already-trusted value returns same."""
        lattice = TrustLattice()
        
        trusted = lattice.label("data", TrustLabel.TRUSTED, "system")
        
        # Upgrading to same level should return as-is
        result = lattice.upgrade(trusted, always_true, TrustLabel.TRUSTED)
        assert result.label == TrustLabel.TRUSTED


class TestTrustJoin:
    """Test trust join (contamination) semantics."""
    
    def test_join_same_trust(self):
        """Test joining values with same trust level."""
        lattice = TrustLattice()
        
        a = lattice.label(1, TrustLabel.TRUSTED)
        b = lattice.label(2, TrustLabel.TRUSTED)
        
        result_trust = lattice.join(a, b)
        assert result_trust == TrustLabel.TRUSTED
    
    def test_join_different_trust(self):
        """Test that join returns minimum trust (contamination)."""
        lattice = TrustLattice()
        
        trusted = lattice.label(1, TrustLabel.TRUSTED)
        untrusted = lattice.label(2, TrustLabel.UNTRUSTED)
        
        result_trust = lattice.join(trusted, untrusted)
        assert result_trust == TrustLabel.UNTRUSTED  # Contaminated!
    
    def test_combine_values(self):
        """Test combining values with trust propagation."""
        lattice = TrustLattice()
        
        a = lattice.label(10, TrustLabel.TRUSTED)
        b = lattice.label(5, TrustLabel.UNTRUSTED)
        
        result = lattice.combine(a, b, combiner=lambda x, y: x + y)
        
        assert result.value == 15
        assert result.label == TrustLabel.UNTRUSTED  # Contaminated by b


class TestRequireTrust:
    """Test require_trust extraction."""
    
    def test_require_trust_success(self):
        """Test extracting value when trust is sufficient."""
        lattice = TrustLattice()
        
        trusted = lattice.label("secret", TrustLabel.TRUSTED)
        
        value = lattice.require_trust(trusted, TrustLabel.TRUSTED)
        assert value == "secret"
    
    def test_require_trust_failure(self):
        """Test that extraction fails when trust is insufficient."""
        lattice = TrustLattice()
        
        untrusted = lattice.untrusted("data")
        
        with pytest.raises(UpgradeError):
            lattice.require_trust(untrusted, TrustLabel.TRUSTED)
    
    def test_require_lower_trust(self):
        """Test that higher trust satisfies lower requirement."""
        lattice = TrustLattice()
        
        kernel = lattice.kernel("system_data")
        
        # KERNEL should satisfy TRUSTED requirement
        value = lattice.require_trust(kernel, TrustLabel.TRUSTED)
        assert value == "system_data"


class TestBuiltinVerifiers:
    """Test built-in verifier functions."""
    
    def test_non_empty_verifier(self):
        """Test non_empty_verifier."""
        assert non_empty_verifier("hello")
        assert non_empty_verifier([1, 2, 3])
        assert not non_empty_verifier("")
        assert not non_empty_verifier([])
    
    def test_type_verifier(self):
        """Test type_verifier."""
        is_str = type_verifier(str)
        assert is_str("hello")
        assert not is_str(42)
        
        is_num = type_verifier((int, float))
        assert is_num(42)
        assert is_num(3.14)
        assert not is_num("42")
    
    def test_range_verifier(self):
        """Test range_verifier."""
        in_range = range_verifier(0, 100)
        assert in_range(50)
        assert in_range(0)
        assert in_range(100)
        assert not in_range(-1)
        assert not in_range(101)
    
    def test_pattern_verifier(self):
        """Test pattern_verifier."""
        is_email_like = pattern_verifier(r".+@.+\..+")
        assert is_email_like("test@example.com")
        assert not is_email_like("invalid")


class TestRegisteredVerifiers:
    """Test registered verifier workflow."""
    
    def test_register_and_use_verifier(self):
        """Test registering and using a named verifier."""
        lattice = TrustLattice()
        
        lattice.register_verifier("is_positive", lambda x: x > 0)
        
        value = lattice.untrusted(42)
        upgraded = lattice.verify_with(value, "is_positive")
        
        assert upgraded.label == TrustLabel.TRUSTED
    
    def test_unknown_verifier_raises(self):
        """Test that unknown verifier raises error."""
        lattice = TrustLattice()
        
        value = lattice.untrusted(42)
        
        with pytest.raises(ValueError):
            lattice.verify_with(value, "nonexistent_verifier")


class TestAuditLog:
    """Test upgrade audit logging."""
    
    def test_audit_log_records_upgrades(self):
        """Test that upgrades are logged."""
        lattice = TrustLattice()
        lattice.clear_audit_log()
        
        value = lattice.untrusted(42)
        lattice.upgrade(value, always_true, verifier_name="test_verifier")
        
        log = lattice.get_audit_log()
        assert len(log) == 1
        assert log[0]["verifier"] == "test_verifier"
        assert log[0]["success"] == True
    
    def test_audit_log_records_failures(self):
        """Test that failed upgrades are also logged."""
        lattice = TrustLattice()
        lattice.clear_audit_log()
        
        value = lattice.untrusted(42)
        
        with pytest.raises(UpgradeError):
            lattice.upgrade(value, always_false, verifier_name="failing_verifier")
        
        log = lattice.get_audit_log()
        assert len(log) == 1
        assert log[0]["verifier"] == "failing_verifier"
        assert log[0]["success"] == False


class TestGlobalInstance:
    """Test global trust lattice instance."""
    
    def test_get_global_instance(self):
        """Test getting the global instance."""
        lattice1 = get_trust_lattice()
        lattice2 = get_trust_lattice()
        assert lattice1 is lattice2
    
    def test_global_has_builtin_verifiers(self):
        """Test that global instance has built-in verifiers."""
        lattice = get_trust_lattice()
        
        # Should have non_empty registered
        value = lattice.untrusted("hello")
        upgraded = lattice.verify_with(value, "non_empty")
        assert upgraded.is_trusted()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
