#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
REGIME SYSTEM (Paper Section 10.1)

A regime R parameterizes admissibility:
    R = (domain_rules, authority, ambiguity_tolerance, ...)

This is effectively a mode-dependent type/effect environment.

From "Newton as a Verified Computation Substrate":
> A regime R parameterizes admissibility... This is effectively a 
> mode-dependent type/effect environment.

═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import re


class RegimeType(Enum):
    """Built-in regime types."""
    FACTUAL = "factual"           # Requires verified facts
    MATHEMATICAL = "mathematical"  # Requires provable computation
    CONVERSATIONAL = "conversational"  # Relaxed verification
    NAVIGATIONAL = "navigational"  # Physical/action commands
    FINANCIAL = "financial"        # Monetary constraints
    TEMPORAL = "temporal"          # Time-based constraints
    CUSTOM = "custom"             # User-defined


@dataclass
class DomainRule:
    """A single domain rule within a regime."""
    name: str
    description: str
    validator: Callable[[Any], bool]
    error_message: str = "Domain rule violated"
    
    def validate(self, value: Any) -> tuple[bool, str]:
        """Check if value satisfies this rule."""
        try:
            if self.validator(value):
                return True, ""
            return False, self.error_message
        except Exception as e:
            return False, f"Validation error: {e}"


@dataclass 
class Regime:
    """
    A regime parameterizes admissibility for verification.
    
    From the paper (Section 10.1):
        R = (domain_rules, authority, ambiguity_tolerance, ...)
    
    This is effectively a mode-dependent type/effect environment.
    
    Usage:
        regime = Regime(
            regime_type=RegimeType.FACTUAL,
            domain_rules=[...],
            authority="knowledge_base",
            ambiguity_tolerance=0.1,
            distortion_threshold=0.3
        )
    """
    
    # Core identity
    regime_type: RegimeType = RegimeType.FACTUAL
    name: str = ""
    description: str = ""
    
    # Domain rules - the constraints that define this regime
    domain_rules: List[DomainRule] = field(default_factory=list)
    
    # Authority - what sources are trusted in this regime
    authority: str = "default"
    trusted_sources: Set[str] = field(default_factory=set)
    
    # Tolerance parameters
    ambiguity_tolerance: float = 0.1  # 0.0 = no ambiguity, 1.0 = anything goes
    distortion_threshold: float = 0.3  # Max D(w,a) before GeometryMismatchError
    
    # Execution parameters
    max_iterations: int = 10000
    max_recursion: int = 100
    timeout_seconds: float = 30.0
    
    # Upgrade requirements - what's needed to upgrade trust in this regime
    upgrade_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.name:
            self.name = self.regime_type.value
        if not self.trusted_sources:
            self.trusted_sources = self._default_trusted_sources()
    
    def _default_trusted_sources(self) -> Set[str]:
        """Default trusted sources based on regime type."""
        defaults = {
            RegimeType.FACTUAL: {"knowledge_base", "verified_facts", "ledger"},
            RegimeType.MATHEMATICAL: {"logic_engine", "proof_system"},
            RegimeType.CONVERSATIONAL: {"any"},
            RegimeType.NAVIGATIONAL: {"physics_engine", "map_data"},
            RegimeType.FINANCIAL: {"ledger", "bank_api"},
            RegimeType.TEMPORAL: {"system_clock", "calendar"},
            RegimeType.CUSTOM: set()
        }
        return defaults.get(self.regime_type, set())
    
    def validate(self, value: Any) -> tuple[bool, List[str]]:
        """
        Validate a value against all domain rules.
        
        Returns:
            (is_valid, list_of_error_messages)
        """
        errors = []
        for rule in self.domain_rules:
            valid, error = rule.validate(value)
            if not valid:
                errors.append(f"{rule.name}: {error}")
        
        return len(errors) == 0, errors
    
    def is_source_trusted(self, source: str) -> bool:
        """Check if a source is trusted in this regime."""
        if "any" in self.trusted_sources:
            return True
        return source in self.trusted_sources
    
    def allows_ambiguity(self, ambiguity_score: float) -> bool:
        """Check if the given ambiguity level is acceptable."""
        return ambiguity_score <= self.ambiguity_tolerance
    
    def allows_distortion(self, distortion: float) -> bool:
        """Check if the given distortion is within threshold."""
        return distortion <= self.distortion_threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize regime to dictionary."""
        return {
            "type": self.regime_type.value,
            "name": self.name,
            "description": self.description,
            "authority": self.authority,
            "trusted_sources": list(self.trusted_sources),
            "ambiguity_tolerance": self.ambiguity_tolerance,
            "distortion_threshold": self.distortion_threshold,
            "max_iterations": self.max_iterations,
            "max_recursion": self.max_recursion,
            "timeout_seconds": self.timeout_seconds,
            "domain_rules": [r.name for r in self.domain_rules]
        }
    
    @classmethod
    def from_type(cls, regime_type: RegimeType) -> 'Regime':
        """Create a regime with default settings for the given type."""
        presets = {
            RegimeType.FACTUAL: {
                "description": "Requires verified facts from trusted sources",
                "ambiguity_tolerance": 0.1,
                "distortion_threshold": 0.2
            },
            RegimeType.MATHEMATICAL: {
                "description": "Requires provable mathematical computation",
                "ambiguity_tolerance": 0.0,
                "distortion_threshold": 0.0
            },
            RegimeType.CONVERSATIONAL: {
                "description": "Relaxed verification for casual interaction",
                "ambiguity_tolerance": 0.8,
                "distortion_threshold": 0.7
            },
            RegimeType.NAVIGATIONAL: {
                "description": "Physical/action commands with physics constraints",
                "ambiguity_tolerance": 0.1,
                "distortion_threshold": 0.1
            },
            RegimeType.FINANCIAL: {
                "description": "Monetary constraints with ledger verification",
                "ambiguity_tolerance": 0.0,
                "distortion_threshold": 0.0
            },
            RegimeType.TEMPORAL: {
                "description": "Time-based constraints",
                "ambiguity_tolerance": 0.2,
                "distortion_threshold": 0.2
            }
        }
        
        preset = presets.get(regime_type, {})
        return cls(
            regime_type=regime_type,
            description=preset.get("description", ""),
            ambiguity_tolerance=preset.get("ambiguity_tolerance", 0.5),
            distortion_threshold=preset.get("distortion_threshold", 0.5)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# BUILT-IN DOMAIN RULES
# ═══════════════════════════════════════════════════════════════════════════════

def non_empty_rule() -> DomainRule:
    """Value must be non-empty."""
    return DomainRule(
        name="non_empty",
        description="Value must be non-empty",
        validator=lambda x: bool(x),
        error_message="Value is empty"
    )

def numeric_rule() -> DomainRule:
    """Value must be numeric."""
    return DomainRule(
        name="numeric",
        description="Value must be numeric",
        validator=lambda x: isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.','').replace('-','').isdigit()),
        error_message="Value is not numeric"
    )

def positive_rule() -> DomainRule:
    """Value must be positive."""
    return DomainRule(
        name="positive",
        description="Value must be positive",
        validator=lambda x: float(x) > 0,
        error_message="Value is not positive"
    )

def bounded_string_rule(max_length: int = 1000) -> DomainRule:
    """String must not exceed max length."""
    return DomainRule(
        name=f"bounded_string_{max_length}",
        description=f"String must not exceed {max_length} characters",
        validator=lambda x: isinstance(x, str) and len(x) <= max_length,
        error_message=f"String exceeds {max_length} characters"
    )

def pattern_rule(pattern: str, name: str = "pattern") -> DomainRule:
    """Value must match regex pattern."""
    compiled = re.compile(pattern)
    return DomainRule(
        name=name,
        description=f"Value must match pattern: {pattern}",
        validator=lambda x: bool(compiled.match(str(x))),
        error_message=f"Value does not match pattern {pattern}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# REGIME REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

class RegimeRegistry:
    """Registry for managing multiple regimes."""
    
    def __init__(self):
        self._regimes: Dict[str, Regime] = {}
        self._active: Optional[str] = None
        
        # Register default regimes
        for rt in RegimeType:
            if rt != RegimeType.CUSTOM:
                regime = Regime.from_type(rt)
                self.register(regime)
    
    def register(self, regime: Regime) -> None:
        """Register a regime."""
        self._regimes[regime.name] = regime
    
    def get(self, name: str) -> Optional[Regime]:
        """Get a regime by name."""
        return self._regimes.get(name)
    
    def activate(self, name: str) -> Regime:
        """Set the active regime."""
        if name not in self._regimes:
            raise ValueError(f"Unknown regime: {name}")
        self._active = name
        return self._regimes[name]
    
    @property
    def active(self) -> Optional[Regime]:
        """Get the currently active regime."""
        if self._active:
            return self._regimes.get(self._active)
        return None
    
    def list_regimes(self) -> List[str]:
        """List all registered regime names."""
        return list(self._regimes.keys())


# Global registry instance
_registry: Optional[RegimeRegistry] = None

def get_regime_registry() -> RegimeRegistry:
    """Get the global regime registry."""
    global _registry
    if _registry is None:
        _registry = RegimeRegistry()
    return _registry


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("REGIME SYSTEM TEST")
    print("=" * 70)
    
    # Create regimes
    factual = Regime.from_type(RegimeType.FACTUAL)
    math = Regime.from_type(RegimeType.MATHEMATICAL)
    
    print(f"\n📋 Factual Regime:")
    print(f"   Ambiguity tolerance: {factual.ambiguity_tolerance}")
    print(f"   Distortion threshold: {factual.distortion_threshold}")
    print(f"   Trusted sources: {factual.trusted_sources}")
    
    print(f"\n🔢 Mathematical Regime:")
    print(f"   Ambiguity tolerance: {math.ambiguity_tolerance}")
    print(f"   Distortion threshold: {math.distortion_threshold}")
    print(f"   Trusted sources: {math.trusted_sources}")
    
    # Test domain rules
    custom = Regime(
        regime_type=RegimeType.CUSTOM,
        name="bounded_positive",
        domain_rules=[
            non_empty_rule(),
            numeric_rule(),
            positive_rule()
        ]
    )
    
    print(f"\n🔧 Custom Regime Tests:")
    test_values = [42, -5, "hello", "", 3.14]
    for val in test_values:
        valid, errors = custom.validate(val)
        status = "✓" if valid else "✗"
        print(f"   {status} validate({val!r}): {errors if errors else 'OK'}")
    
    # Registry
    registry = get_regime_registry()
    print(f"\n📚 Registered regimes: {registry.list_regimes()}")
