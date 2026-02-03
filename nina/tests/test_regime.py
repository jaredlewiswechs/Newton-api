#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
REGIME SYSTEM TESTS
Test coverage for Paper Section 10.1
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from developer.forge.regime import (
    Regime, RegimeType, DomainRule,
    non_empty_rule, numeric_rule, positive_rule, bounded_string_rule, pattern_rule,
    RegimeRegistry, get_regime_registry
)


class TestRegimeCreation:
    """Test regime creation and configuration."""
    
    def test_create_default_regime(self):
        """Test creating a regime with defaults."""
        regime = Regime()
        assert regime.regime_type == RegimeType.FACTUAL
        assert regime.ambiguity_tolerance == 0.1
        assert regime.distortion_threshold == 0.3
    
    def test_create_from_type(self):
        """Test creating regimes from preset types."""
        factual = Regime.from_type(RegimeType.FACTUAL)
        assert factual.regime_type == RegimeType.FACTUAL
        assert factual.ambiguity_tolerance == 0.1
        
        math = Regime.from_type(RegimeType.MATHEMATICAL)
        assert math.regime_type == RegimeType.MATHEMATICAL
        assert math.ambiguity_tolerance == 0.0  # No ambiguity in math
        assert math.distortion_threshold == 0.0
        
        conversational = Regime.from_type(RegimeType.CONVERSATIONAL)
        assert conversational.ambiguity_tolerance == 0.8  # High tolerance
    
    def test_custom_regime(self):
        """Test creating a custom regime."""
        regime = Regime(
            regime_type=RegimeType.CUSTOM,
            name="my_regime",
            ambiguity_tolerance=0.5,
            distortion_threshold=0.4
        )
        assert regime.name == "my_regime"
        assert regime.ambiguity_tolerance == 0.5


class TestDomainRules:
    """Test domain rule validation."""
    
    def test_non_empty_rule(self):
        """Test non-empty rule."""
        rule = non_empty_rule()
        
        valid, _ = rule.validate("hello")
        assert valid
        
        valid, error = rule.validate("")
        assert not valid
        assert "empty" in error.lower()
        
        valid, _ = rule.validate([1, 2, 3])
        assert valid
        
        valid, _ = rule.validate([])
        assert not valid
    
    def test_numeric_rule(self):
        """Test numeric rule."""
        rule = numeric_rule()
        
        valid, _ = rule.validate(42)
        assert valid
        
        valid, _ = rule.validate(3.14)
        assert valid
        
        valid, _ = rule.validate("123")
        assert valid
        
        valid, _ = rule.validate("hello")
        assert not valid
    
    def test_positive_rule(self):
        """Test positive rule."""
        rule = positive_rule()
        
        valid, _ = rule.validate(5)
        assert valid
        
        valid, _ = rule.validate(-5)
        assert not valid
        
        valid, _ = rule.validate(0)
        assert not valid
    
    def test_bounded_string_rule(self):
        """Test bounded string rule."""
        rule = bounded_string_rule(max_length=10)
        
        valid, _ = rule.validate("hello")
        assert valid
        
        valid, _ = rule.validate("this is too long")
        assert not valid
    
    def test_pattern_rule(self):
        """Test pattern rule."""
        rule = pattern_rule(r"^\d{3}-\d{4}$", name="phone")
        
        valid, _ = rule.validate("123-4567")
        assert valid
        
        valid, _ = rule.validate("invalid")
        assert not valid


class TestRegimeValidation:
    """Test regime-level validation."""
    
    def test_validate_with_rules(self):
        """Test validating values against regime rules."""
        regime = Regime(
            regime_type=RegimeType.CUSTOM,
            domain_rules=[
                non_empty_rule(),
                numeric_rule(),
                positive_rule()
            ]
        )
        
        # All rules pass
        valid, errors = regime.validate(42)
        assert valid
        assert len(errors) == 0
        
        # Fails positive
        valid, errors = regime.validate(-5)
        assert not valid
        assert len(errors) == 1
        
        # Fails numeric and positive
        valid, errors = regime.validate("hello")
        assert not valid
        assert len(errors) >= 1


class TestTrustedSources:
    """Test trusted source handling."""
    
    def test_default_trusted_sources(self):
        """Test that regimes have appropriate default trusted sources."""
        factual = Regime.from_type(RegimeType.FACTUAL)
        assert "knowledge_base" in factual.trusted_sources
        assert "ledger" in factual.trusted_sources
        
        math = Regime.from_type(RegimeType.MATHEMATICAL)
        assert "logic_engine" in math.trusted_sources
    
    def test_is_source_trusted(self):
        """Test source trust checking."""
        regime = Regime(
            regime_type=RegimeType.CUSTOM,
            trusted_sources={"database", "api"}
        )
        
        assert regime.is_source_trusted("database")
        assert regime.is_source_trusted("api")
        assert not regime.is_source_trusted("user_input")
    
    def test_any_source_trusted(self):
        """Test 'any' trusted source."""
        conversational = Regime.from_type(RegimeType.CONVERSATIONAL)
        assert "any" in conversational.trusted_sources
        assert conversational.is_source_trusted("anything")


class TestTolerances:
    """Test ambiguity and distortion tolerances."""
    
    def test_allows_ambiguity(self):
        """Test ambiguity tolerance checking."""
        regime = Regime(ambiguity_tolerance=0.3)
        
        assert regime.allows_ambiguity(0.1)
        assert regime.allows_ambiguity(0.3)
        assert not regime.allows_ambiguity(0.5)
    
    def test_allows_distortion(self):
        """Test distortion threshold checking."""
        regime = Regime(distortion_threshold=0.2)
        
        assert regime.allows_distortion(0.1)
        assert regime.allows_distortion(0.2)
        assert not regime.allows_distortion(0.3)


class TestRegimeRegistry:
    """Test the regime registry."""
    
    def test_global_registry(self):
        """Test global registry has default regimes."""
        registry = get_regime_registry()
        
        names = registry.list_regimes()
        assert "factual" in names
        assert "mathematical" in names
        assert "conversational" in names
    
    def test_register_and_get(self):
        """Test registering and retrieving regimes."""
        registry = RegimeRegistry()
        
        custom = Regime(
            regime_type=RegimeType.CUSTOM,
            name="test_regime"
        )
        registry.register(custom)
        
        retrieved = registry.get("test_regime")
        assert retrieved is not None
        assert retrieved.name == "test_regime"
    
    def test_activate_regime(self):
        """Test activating a regime."""
        registry = get_regime_registry()
        
        regime = registry.activate("mathematical")
        assert regime.regime_type == RegimeType.MATHEMATICAL
        assert registry.active == regime


class TestSerialization:
    """Test regime serialization."""
    
    def test_to_dict(self):
        """Test converting regime to dictionary."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        d = regime.to_dict()
        
        assert d["type"] == "factual"
        assert "ambiguity_tolerance" in d
        assert "distortion_threshold" in d
        assert isinstance(d["trusted_sources"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
