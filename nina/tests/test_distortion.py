#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
DISTORTION METRIC TESTS
Test coverage for Paper Section 10.2
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from developer.forge.distortion import (
    DistortionMetric, 
    GeometryMismatchError,
    KinematicSignature,
    PhysicsVector,
    get_distortion_metric
)


class TestKinematicSignature:
    """Test kinematic signature creation and properties."""
    
    def test_create_signature(self):
        """Test creating a kinematic signature."""
        sig = KinematicSignature(
            word="jump",
            weight=0.7,
            curvature=0.5,
            commit_strength=0.7,
            is_action=True,
            force_vector=(0.0, 0.5, 0.3)
        )
        
        assert sig.word == "jump"
        assert sig.weight == 0.7
        assert sig.is_action
    
    def test_magnitude(self):
        """Test force vector magnitude calculation."""
        sig = KinematicSignature(
            word="test",
            force_vector=(3.0, 4.0, 0.0)
        )
        assert sig.magnitude() == 5.0
    
    def test_as_vector(self):
        """Test converting signature to vector."""
        sig = KinematicSignature(
            word="test",
            weight=0.5,
            curvature=0.1,
            commit_strength=0.6,
            is_action=True,
            force_vector=(0.1, 0.2, 0.3)
        )
        
        vec = sig.as_vector()
        assert len(vec) == 7
        assert vec[0] == 0.5  # weight
        assert vec[3] == 1.0  # is_action as float


class TestPhysicsVector:
    """Test physics vector creation and properties."""
    
    def test_create_physics(self):
        """Test creating a physics vector."""
        phys = PhysicsVector(
            action="drop",
            force=100.0,
            direction=(0.0, 0.0, -1.0),
            reversibility=0.1,
            locality=0.5,
            time_scale=0.5
        )
        
        assert phys.action == "drop"
        assert phys.force == 100.0
        assert phys.reversibility == 0.1
    
    def test_as_vector(self):
        """Test converting physics to vector."""
        phys = PhysicsVector(action="test")
        vec = phys.as_vector()
        assert len(vec) == 7


class TestDistortionMetric:
    """Test the distortion metric computation."""
    
    def test_get_builtin_signature(self):
        """Test retrieving built-in word signatures."""
        metric = DistortionMetric()
        
        trim_sig = metric.get_signature("trim")
        assert trim_sig.word == "trim"
        assert trim_sig.is_action
        assert trim_sig.weight < 0.5  # Gentle action
        
        dive_sig = metric.get_signature("dive")
        assert dive_sig.word == "dive"
        assert dive_sig.weight > 0.7  # Forceful action
    
    def test_get_unknown_signature(self):
        """Test generating signature for unknown word."""
        metric = DistortionMetric()
        
        sig = metric.get_signature("xyzabc")
        assert sig.word == "xyzabc"
        # Should have computed some default values
        assert 0.0 <= sig.weight <= 1.0
    
    def test_compute_distortion_match(self):
        """Test distortion computation for matching word/action."""
        metric = DistortionMetric()
        
        # "trim" + precise cutting should have low distortion
        distortion = metric.compute_distortion("trim", "cut_precise")
        assert distortion < 0.5  # Should be relatively low
    
    def test_compute_distortion_mismatch(self):
        """Test distortion computation for mismatched word/action."""
        metric = DistortionMetric()
        
        # "trim" + forceful water entry should have high distortion
        distortion = metric.compute_distortion("trim", "enter_water_forceful")
        # Should be higher than matching case
        match_distortion = metric.compute_distortion("dive", "enter_water_forceful")
        assert distortion > match_distortion
    
    def test_different_metrics(self):
        """Test different distance metrics."""
        metric = DistortionMetric()
        
        d_euclidean = metric.compute_distortion("walk", "cut_precise", metric="euclidean")
        d_cosine = metric.compute_distortion("walk", "cut_precise", metric="cosine")
        d_manhattan = metric.compute_distortion("walk", "cut_precise", metric="manhattan")
        
        # All should be positive
        assert d_euclidean >= 0
        assert d_cosine >= 0
        assert d_manhattan >= 0


class TestAdmissibilityCheck:
    """Test admissibility checking."""
    
    def test_check_admissible(self):
        """Test checking an admissible word/action pair."""
        metric = DistortionMetric()
        
        admissible, distortion, suggestions = metric.check_admissibility(
            "trim", "cut_precise", threshold=1.0
        )
        assert admissible
        assert distortion < 1.0
    
    def test_check_inadmissible(self):
        """Test checking an inadmissible word/action pair."""
        metric = DistortionMetric()
        
        admissible, distortion, suggestions = metric.check_admissibility(
            "trim", "enter_water_forceful", threshold=0.2
        )
        # Likely inadmissible with low threshold
        if not admissible:
            assert len(suggestions) > 0  # Should suggest alternatives
    
    def test_suggest_alternatives(self):
        """Test suggestion of alternative words."""
        metric = DistortionMetric()
        
        suggestions = metric.suggest_alternatives("enter_water_forceful", max_distortion=1.0)
        assert len(suggestions) > 0
        # "dive" or "plunge" should be good suggestions
        forceful_words = {"dive", "plunge", "crash"}
        assert any(s in forceful_words for s in suggestions)


class TestGeometryMismatchError:
    """Test the GeometryMismatchError exception."""
    
    def test_verify_or_raise_pass(self):
        """Test verify_or_raise when verification passes."""
        metric = DistortionMetric()
        
        # Should not raise for matching pair with high threshold
        distortion = metric.verify_or_raise("dive", "enter_water_forceful", threshold=2.0)
        assert distortion >= 0
    
    def test_verify_or_raise_fail(self):
        """Test verify_or_raise when verification fails."""
        metric = DistortionMetric()
        
        with pytest.raises(GeometryMismatchError) as exc_info:
            metric.verify_or_raise("trim", "enter_water_forceful", threshold=0.1)
        
        error = exc_info.value
        assert error.word == "trim"
        assert error.action == "enter_water_forceful"
        assert error.distortion > error.threshold
    
    def test_error_has_suggestions(self):
        """Test that GeometryMismatchError includes suggestions."""
        metric = DistortionMetric()
        
        with pytest.raises(GeometryMismatchError) as exc_info:
            metric.verify_or_raise("nudge", "enter_water_forceful", threshold=0.1)
        
        error = exc_info.value
        # Should have suggestions for better words
        assert isinstance(error.suggestions, list)


class TestCustomRegistration:
    """Test registering custom signatures and physics."""
    
    def test_register_signature(self):
        """Test registering a custom word signature."""
        metric = DistortionMetric()
        
        custom_sig = KinematicSignature(
            word="quantum_leap",
            weight=0.95,
            curvature=1.0,
            commit_strength=0.99,
            is_action=True,
            force_vector=(0.0, 1.0, 0.0)
        )
        metric.register_signature("quantum_leap", custom_sig)
        
        retrieved = metric.get_signature("quantum_leap")
        assert retrieved.weight == 0.95
    
    def test_register_physics(self):
        """Test registering custom action physics."""
        metric = DistortionMetric()
        
        custom_phys = PhysicsVector(
            action="teleport",
            force=0.0,
            direction=(0.0, 0.0, 0.0),
            reversibility=1.0,
            locality=0.0,  # Non-local!
            time_scale=0.001
        )
        metric.register_physics("teleport", custom_phys)
        
        retrieved = metric.get_physics("teleport")
        assert retrieved.locality == 0.0


class TestGlobalInstance:
    """Test global distortion metric instance."""
    
    def test_get_global_instance(self):
        """Test getting the global instance."""
        metric1 = get_distortion_metric()
        metric2 = get_distortion_metric()
        assert metric1 is metric2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
