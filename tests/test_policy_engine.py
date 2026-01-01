#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
POLICY ENGINE TESTS
Tests for the policy-as-code middleware.
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.policy_engine import (
    PolicyEngine, Policy, PolicyType, PolicyAction,
    PolicyEvaluationResult
)


class TestPolicyEngine:
    """Test suite for PolicyEngine."""
    
    def test_create_engine(self):
        """Test creating a policy engine."""
        engine = PolicyEngine()
        assert engine is not None
        assert len(engine.policies) >= 0
    
    def test_add_policy(self):
        """Test adding a policy."""
        engine = PolicyEngine()
        
        policy = Policy(
            id="test_policy_1",
            name="Test Size Limit",
            type=PolicyType.SIZE_LIMIT,
            action=PolicyAction.DENY,
            condition={"max_size": 100}
        )
        
        engine.add_policy(policy)
        assert "test_policy_1" in engine.policies
        assert engine.policies["test_policy_1"].name == "Test Size Limit"
    
    def test_remove_policy(self):
        """Test removing a policy."""
        engine = PolicyEngine()
        
        policy = Policy(
            id="test_policy_2",
            name="Test Policy",
            type=PolicyType.SIZE_LIMIT,
            action=PolicyAction.DENY,
            condition={"max_size": 100}
        )
        
        engine.add_policy(policy)
        assert "test_policy_2" in engine.policies
        
        removed = engine.remove_policy("test_policy_2")
        assert removed is True
        assert "test_policy_2" not in engine.policies
        
        # Try removing non-existent policy
        removed = engine.remove_policy("non_existent")
        assert removed is False
    
    def test_size_limit_policy(self):
        """Test size limit policy enforcement."""
        engine = PolicyEngine()
        
        policy = Policy(
            id="size_limit",
            name="Size Limit",
            type=PolicyType.SIZE_LIMIT,
            action=PolicyAction.DENY,
            condition={"max_size": 50}
        )
        
        engine.add_policy(policy)
        
        # Test with small input (should pass)
        results = engine.evaluate_input("short text", "test")
        assert len(results) > 0
        size_result = next((r for r in results if r.policy_id == "size_limit"), None)
        assert size_result is not None
        assert size_result.passed is True
        
        # Test with large input (should fail)
        long_text = "x" * 100
        results = engine.evaluate_input(long_text, "test")
        size_result = next((r for r in results if r.policy_id == "size_limit"), None)
        assert size_result is not None
        assert size_result.passed is False
    
    def test_content_filter_policy(self):
        """Test content filter policy."""
        # Create a fresh engine without default policies
        engine = PolicyEngine()
        # Remove default policies that might interfere
        for policy_id in list(engine.policies.keys()):
            engine.remove_policy(policy_id)
        
        policy = Policy(
            id="test_content_filter",
            name="Test Content Filter",
            type=PolicyType.CONTENT_FILTER,
            action=PolicyAction.WARN,
            condition={
                "blacklist": ["forbidden", "blocked"]
            }
        )
        
        engine.add_policy(policy)
        
        # Test with safe content
        results = engine.evaluate_input("This is safe content", "test")
        content_result = next((r for r in results if r.policy_id == "test_content_filter"), None)
        assert content_result is not None
        assert content_result.passed is True
        
        # Test with blacklisted term
        results = engine.evaluate_input("This contains a forbidden word", "test")
        content_result = next((r for r in results if r.policy_id == "test_content_filter"), None)
        assert content_result is not None
        assert content_result.passed is False
    
    def test_input_validation_policy(self):
        """Test input validation policy."""
        engine = PolicyEngine()
        
        policy = Policy(
            id="input_validation",
            name="Required Fields",
            type=PolicyType.INPUT_VALIDATION,
            action=PolicyAction.DENY,
            condition={
                "required_fields": ["name", "email"]
            }
        )
        
        engine.add_policy(policy)
        
        # Test with missing fields
        results = engine.evaluate_input({"name": "John"}, "test")
        validation_result = next((r for r in results if r.policy_id == "input_validation"), None)
        assert validation_result is not None
        assert validation_result.passed is False
        
        # Test with all fields
        results = engine.evaluate_input({"name": "John", "email": "john@example.com"}, "test")
        validation_result = next((r for r in results if r.policy_id == "input_validation"), None)
        assert validation_result is not None
        assert validation_result.passed is True
    
    def test_output_validation_policy(self):
        """Test output validation policy."""
        engine = PolicyEngine()
        
        policy = Policy(
            id="output_validation",
            name="Output Type Check",
            type=PolicyType.OUTPUT_VALIDATION,
            action=PolicyAction.DENY,
            condition={
                "type": "number"
            }
        )
        
        engine.add_policy(policy)
        
        # Test with correct type
        results = engine.evaluate_output(42, "test")
        output_result = next((r for r in results if r.policy_id == "output_validation"), None)
        assert output_result is not None
        assert output_result.passed is True
        
        # Test with incorrect type
        results = engine.evaluate_output("string", "test")
        output_result = next((r for r in results if r.policy_id == "output_validation"), None)
        assert output_result is not None
        assert output_result.passed is False
    
    def test_check_enforcement_needed(self):
        """Test enforcement check."""
        engine = PolicyEngine()
        
        # Create results with different actions
        results = [
            PolicyEvaluationResult(
                policy_id="policy1",
                passed=False,
                action=PolicyAction.WARN,
                message="Warning"
            ),
            PolicyEvaluationResult(
                policy_id="policy2",
                passed=True,
                action=PolicyAction.ALLOW,
                message="Allowed"
            )
        ]
        
        # No enforcement needed for WARN
        assert engine.check_enforcement_needed(results) is False
        
        # Add DENY action
        results.append(
            PolicyEvaluationResult(
                policy_id="policy3",
                passed=False,
                action=PolicyAction.DENY,
                message="Denied"
            )
        )
        
        # Enforcement needed for DENY
        assert engine.check_enforcement_needed(results) is True
    
    def test_disabled_policy(self):
        """Test that disabled policies are not evaluated."""
        engine = PolicyEngine()
        
        policy = Policy(
            id="disabled_policy",
            name="Disabled Policy",
            type=PolicyType.SIZE_LIMIT,
            action=PolicyAction.DENY,
            condition={"max_size": 1},
            enabled=False
        )
        
        engine.add_policy(policy)
        
        # Even with large input, disabled policy should not be evaluated
        results = engine.evaluate_input("x" * 100, "test")
        disabled_result = next((r for r in results if r.policy_id == "disabled_policy"), None)
        assert disabled_result is None
    
    def test_policy_stats(self):
        """Test policy engine statistics."""
        engine = PolicyEngine()
        
        policy = Policy(
            id="test_policy",
            name="Test Policy",
            type=PolicyType.SIZE_LIMIT,
            action=PolicyAction.DENY,
            condition={"max_size": 50}
        )
        
        engine.add_policy(policy)
        
        # Run some evaluations
        engine.evaluate_input("short", "test")
        engine.evaluate_input("x" * 100, "test")
        
        stats = engine.stats()
        assert stats["total_policies"] >= 1
        assert stats["enabled_policies"] >= 1
        assert stats["total_evaluations"] >= 2
        assert "violation_rate" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
