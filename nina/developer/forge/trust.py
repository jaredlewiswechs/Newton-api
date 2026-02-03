#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
TRUST LATTICE (Paper Section 7)

Trust as an Explicit Upgrade Lattice (Information Flow Control)

Define security labels:
    UNTRUSTED ⊏ TRUSTED

Policy:
    - No implicit cast UNTRUSTED → TRUSTED
    - The only cast is Verify/Upgrade:
        upgrade(y) allowed iff Verify(y) = true

From "Newton as a Verified Computation Substrate":
> This is the clean formalization of: "trust the kernel/ledger/constraints; 
> treat external output as untrusted until verified."

═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Generic, TypeVar
from enum import Enum, auto
from datetime import datetime
import hashlib


class TrustLabel(Enum):
    """
    Security labels in the trust lattice.
    
    Ordering: UNTRUSTED ⊏ VERIFIED ⊏ TRUSTED ⊏ KERNEL
    
    - UNTRUSTED: External/unverified data
    - VERIFIED: Passed verification but not from trusted source
    - TRUSTED: From trusted source or upgraded via verification
    - KERNEL: Core system invariants (cannot be demoted)
    """
    UNTRUSTED = 0
    VERIFIED = 1
    TRUSTED = 2
    KERNEL = 3
    
    def __lt__(self, other: 'TrustLabel') -> bool:
        return self.value < other.value
    
    def __le__(self, other: 'TrustLabel') -> bool:
        return self.value <= other.value
    
    def __gt__(self, other: 'TrustLabel') -> bool:
        return self.value > other.value
    
    def __ge__(self, other: 'TrustLabel') -> bool:
        return self.value >= other.value


T = TypeVar('T')


@dataclass
class Labeled(Generic[T]):
    """
    A value with an associated trust label.
    
    This is the fundamental unit of information flow control.
    Labels flow with data and constrain operations.
    """
    value: T
    label: TrustLabel
    source: str = "unknown"
    timestamp: datetime = field(default_factory=datetime.now)
    verification_trace: List[str] = field(default_factory=list)
    
    def __repr__(self):
        return f"Labeled({self.value!r}, {self.label.name})"
    
    def is_trusted(self) -> bool:
        """Check if this value is at least TRUSTED."""
        return self.label >= TrustLabel.TRUSTED
    
    def is_verified(self) -> bool:
        """Check if this value has been verified."""
        return self.label >= TrustLabel.VERIFIED


class UpgradeError(Exception):
    """Raised when an upgrade attempt fails."""
    pass


class DowngradeError(Exception):
    """Raised when an illegal downgrade is attempted."""
    pass


class TrustLattice:
    """
    The trust upgrade lattice implementing IFC (Information Flow Control).
    
    Core invariant: No implicit cast from lower to higher trust.
    The ONLY way to upgrade is through explicit verification.
    
    Usage:
        lattice = TrustLattice()
        
        # Create untrusted value from external source
        external_data = lattice.label("Paris", TrustLabel.UNTRUSTED, "user_input")
        
        # Cannot use directly in trusted context
        assert not external_data.is_trusted()
        
        # Must verify to upgrade
        def verify_capital(city):
            return city == "Paris"  # Check against knowledge base
        
        trusted_data = lattice.upgrade(external_data, verify_capital)
        assert trusted_data.is_trusted()
    """
    
    def __init__(self):
        self._verifiers: Dict[str, Callable[[Any], bool]] = {}
        self._upgrade_log: List[Dict[str, Any]] = []
    
    def label(
        self, 
        value: T, 
        trust: TrustLabel, 
        source: str = "unknown"
    ) -> Labeled[T]:
        """
        Attach a trust label to a value.
        
        This is the entry point for all data into the system.
        External data should ALWAYS enter as UNTRUSTED.
        """
        return Labeled(
            value=value,
            label=trust,
            source=source,
            timestamp=datetime.now(),
            verification_trace=[f"Labeled as {trust.name} from {source}"]
        )
    
    def untrusted(self, value: T, source: str = "external") -> Labeled[T]:
        """Convenience method for labeling untrusted data."""
        return self.label(value, TrustLabel.UNTRUSTED, source)
    
    def kernel(self, value: T, source: str = "kernel") -> Labeled[T]:
        """
        Label a value as KERNEL trust (highest).
        
        Use sparingly - only for core system invariants.
        KERNEL values cannot be demoted.
        """
        return self.label(value, TrustLabel.KERNEL, source)
    
    def upgrade(
        self,
        labeled: Labeled[T],
        verifier: Callable[[T], bool],
        target_trust: TrustLabel = TrustLabel.TRUSTED,
        verifier_name: str = "anonymous"
    ) -> Labeled[T]:
        """
        Attempt to upgrade a labeled value's trust level.
        
        This is the ONLY way to increase trust. The upgrade succeeds
        if and only if verifier(value) returns True.
        
        Args:
            labeled: The labeled value to upgrade
            verifier: Function that returns True if value is valid
            target_trust: The trust level to upgrade to
            verifier_name: Name of the verifier for audit trail
            
        Returns:
            New Labeled with upgraded trust if verification passes
            
        Raises:
            UpgradeError: If verification fails
        """
        # Cannot upgrade beyond KERNEL
        if target_trust > TrustLabel.KERNEL:
            raise UpgradeError("Cannot upgrade beyond KERNEL")
        
        # Cannot upgrade already higher-trusted values this way
        if labeled.label >= target_trust:
            # Already at or above target - return as-is
            return labeled
        
        # Run verification
        try:
            if verifier(labeled.value):
                # Verification passed - create upgraded value
                new_trace = labeled.verification_trace.copy()
                new_trace.append(
                    f"Upgraded {labeled.label.name} → {target_trust.name} "
                    f"via {verifier_name} at {datetime.now().isoformat()}"
                )
                
                upgraded = Labeled(
                    value=labeled.value,
                    label=target_trust,
                    source=labeled.source,
                    timestamp=datetime.now(),
                    verification_trace=new_trace
                )
                
                # Log the upgrade
                self._log_upgrade(labeled, upgraded, verifier_name, True)
                
                return upgraded
            else:
                # Verification failed
                self._log_upgrade(labeled, labeled, verifier_name, False)
                raise UpgradeError(
                    f"Verification failed: {verifier_name} rejected {labeled.value!r}"
                )
        except Exception as e:
            if isinstance(e, UpgradeError):
                raise
            self._log_upgrade(labeled, labeled, verifier_name, False, str(e))
            raise UpgradeError(f"Verification error: {e}")
    
    def _log_upgrade(
        self,
        before: Labeled,
        after: Labeled,
        verifier: str,
        success: bool,
        error: Optional[str] = None
    ):
        """Log an upgrade attempt for audit trail."""
        self._upgrade_log.append({
            "timestamp": datetime.now().isoformat(),
            "value_hash": hashlib.sha256(str(before.value).encode()).hexdigest()[:16],
            "before_trust": before.label.name,
            "after_trust": after.label.name,
            "verifier": verifier,
            "success": success,
            "error": error
        })
    
    def join(self, *labeled_values: Labeled) -> TrustLabel:
        """
        Compute the join (lowest common trust) of multiple labeled values.
        
        When combining data, the result's trust is the MINIMUM of inputs.
        This ensures information flow security - untrusted data contaminates
        trusted data.
        """
        if not labeled_values:
            return TrustLabel.KERNEL
        
        return min(lv.label for lv in labeled_values)
    
    def combine(
        self,
        *labeled_values: Labeled,
        combiner: Callable[..., T]
    ) -> Labeled[T]:
        """
        Combine multiple labeled values, computing result trust as join.
        
        Args:
            labeled_values: Values to combine
            combiner: Function to combine the raw values
            
        Returns:
            Labeled result with trust = min(input trusts)
        """
        # Compute result trust
        result_trust = self.join(*labeled_values)
        
        # Extract raw values and combine
        raw_values = [lv.value for lv in labeled_values]
        result_value = combiner(*raw_values)
        
        # Build trace
        sources = [f"{lv.source}({lv.label.name})" for lv in labeled_values]
        trace = [f"Combined from: {', '.join(sources)} → {result_trust.name}"]
        
        return Labeled(
            value=result_value,
            label=result_trust,
            source="combined",
            verification_trace=trace
        )
    
    def require_trust(
        self,
        labeled: Labeled[T],
        minimum_trust: TrustLabel
    ) -> T:
        """
        Extract value only if it meets minimum trust requirement.
        
        This is the secure way to consume labeled values.
        
        Raises:
            UpgradeError: If trust is insufficient
        """
        if labeled.label < minimum_trust:
            raise UpgradeError(
                f"Trust {labeled.label.name} < required {minimum_trust.name}"
            )
        return labeled.value
    
    def register_verifier(
        self,
        name: str,
        verifier: Callable[[Any], bool]
    ) -> None:
        """Register a named verifier for reuse."""
        self._verifiers[name] = verifier
    
    def verify_with(
        self,
        labeled: Labeled[T],
        verifier_name: str,
        target_trust: TrustLabel = TrustLabel.TRUSTED
    ) -> Labeled[T]:
        """Upgrade using a registered verifier."""
        if verifier_name not in self._verifiers:
            raise ValueError(f"Unknown verifier: {verifier_name}")
        
        return self.upgrade(
            labeled,
            self._verifiers[verifier_name],
            target_trust,
            verifier_name
        )
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get the upgrade audit log."""
        return self._upgrade_log.copy()
    
    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        self._upgrade_log.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# BUILT-IN VERIFIERS
# ═══════════════════════════════════════════════════════════════════════════════

def non_empty_verifier(value: Any) -> bool:
    """Verify value is non-empty."""
    return bool(value)


def type_verifier(expected_type: type) -> Callable[[Any], bool]:
    """Create a verifier that checks type."""
    def verify(value: Any) -> bool:
        return isinstance(value, expected_type)
    return verify


def range_verifier(min_val: float, max_val: float) -> Callable[[Any], bool]:
    """Create a verifier that checks numeric range."""
    def verify(value: Any) -> bool:
        try:
            return min_val <= float(value) <= max_val
        except (TypeError, ValueError):
            return False
    return verify


def pattern_verifier(pattern: str) -> Callable[[Any], bool]:
    """Create a verifier that checks regex pattern."""
    import re
    compiled = re.compile(pattern)
    def verify(value: Any) -> bool:
        return bool(compiled.match(str(value)))
    return verify


def always_true(_: Any) -> bool:
    """Verifier that always passes (use with caution!)."""
    return True


def always_false(_: Any) -> bool:
    """Verifier that always fails."""
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_lattice: Optional[TrustLattice] = None

def get_trust_lattice() -> TrustLattice:
    """Get the global trust lattice instance."""
    global _lattice
    if _lattice is None:
        _lattice = TrustLattice()
        # Register built-in verifiers
        _lattice.register_verifier("non_empty", non_empty_verifier)
        _lattice.register_verifier("is_string", type_verifier(str))
        _lattice.register_verifier("is_number", type_verifier((int, float)))
    return _lattice


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("TRUST LATTICE TEST")
    print("UNTRUSTED ⊏ VERIFIED ⊏ TRUSTED ⊏ KERNEL")
    print("=" * 70)
    
    lattice = TrustLattice()
    
    # Test 1: Basic labeling
    print("\n📋 Test 1: Basic labeling")
    external = lattice.untrusted("user input", "api")
    print(f"   {external}")
    print(f"   is_trusted: {external.is_trusted()}")
    
    # Test 2: Upgrade with passing verifier
    print("\n✓ Test 2: Successful upgrade")
    
    def is_valid_city(city):
        return city in ["Paris", "London", "Tokyo"]
    
    city_input = lattice.untrusted("Paris", "user")
    try:
        trusted_city = lattice.upgrade(city_input, is_valid_city, verifier_name="city_check")
        print(f"   Before: {city_input}")
        print(f"   After:  {trusted_city}")
        print(f"   Trace:  {trusted_city.verification_trace}")
    except UpgradeError as e:
        print(f"   Failed: {e}")
    
    # Test 3: Upgrade with failing verifier
    print("\n✗ Test 3: Failed upgrade")
    bad_city = lattice.untrusted("FakeCity", "user")
    try:
        lattice.upgrade(bad_city, is_valid_city, verifier_name="city_check")
        print("   Should not reach here!")
    except UpgradeError as e:
        print(f"   Expected failure: {e}")
    
    # Test 4: Trust join (contamination)
    print("\n🔀 Test 4: Trust join")
    trusted = lattice.label(10, TrustLabel.TRUSTED, "system")
    untrusted = lattice.label(5, TrustLabel.UNTRUSTED, "user")
    
    result = lattice.combine(trusted, untrusted, combiner=lambda a, b: a + b)
    print(f"   TRUSTED(10) + UNTRUSTED(5) = {result}")
    print(f"   Result trust: {result.label.name} (contaminated by UNTRUSTED)")
    
    # Test 5: Require trust
    print("\n🔒 Test 5: Require minimum trust")
    try:
        value = lattice.require_trust(trusted, TrustLabel.TRUSTED)
        print(f"   Extracted {value} from TRUSTED labeled value")
    except UpgradeError:
        print("   Failed to extract (should not happen)")
    
    try:
        value = lattice.require_trust(untrusted, TrustLabel.TRUSTED)
        print("   Should not reach here!")
    except UpgradeError as e:
        print(f"   Expected: {e}")
    
    # Test 6: Audit log
    print("\n📜 Test 6: Audit log")
    log = lattice.get_audit_log()
    for entry in log:
        print(f"   {entry['verifier']}: {entry['before_trust']} → {entry['after_trust']} "
              f"({'✓' if entry['success'] else '✗'})")
