#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
POLICY ENGINE - POLICY-AS-CODE MIDDLEWARE
Enforce policies on verification operations.

Part of Glass Box activation - provides declarative policy enforcement
before and after verification operations.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import time
import re


class PolicyAction(Enum):
    """Actions that can be taken when a policy is violated."""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    REQUIRE_APPROVAL = "require_approval"


class PolicyType(Enum):
    """Types of policies."""
    INPUT_VALIDATION = "input_validation"
    OUTPUT_VALIDATION = "output_validation"
    RATE_LIMIT = "rate_limit"
    CONTENT_FILTER = "content_filter"
    SIZE_LIMIT = "size_limit"


@dataclass
class Policy:
    """A single policy rule."""
    id: str
    name: str
    type: PolicyType
    action: PolicyAction
    condition: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "action": self.action.value,
            "condition": self.condition,
            "metadata": self.metadata,
            "enabled": self.enabled
        }


@dataclass
class PolicyEvaluationResult:
    """Result of evaluating a policy."""
    policy_id: str
    passed: bool
    action: PolicyAction
    message: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "passed": self.passed,
            "action": self.action.value,
            "message": self.message,
            "timestamp": self.timestamp
        }


class PolicyEngine:
    """
    Policy engine for enforcing policies on verification operations.
    
    Policies are evaluated before and after operations to ensure
    compliance with organizational rules.
    """
    
    def __init__(self):
        """Initialize PolicyEngine."""
        self.policies: Dict[str, Policy] = {}
        self._evaluation_count = 0
        self._violation_count = 0
    
    def add_policy(self, policy: Policy) -> None:
        """
        Add a policy to the engine.
        
        Args:
            policy: The policy to add
        """
        self.policies[policy.id] = policy
    
    def remove_policy(self, policy_id: str) -> bool:
        """
        Remove a policy from the engine.
        
        Args:
            policy_id: ID of the policy to remove
        
        Returns:
            True if removed, False if not found
        """
        if policy_id in self.policies:
            del self.policies[policy_id]
            return True
        return False
    
    def evaluate_input(self, input_data: Any, operation: str) -> List[PolicyEvaluationResult]:
        """
        Evaluate input against all applicable policies.
        
        Args:
            input_data: Input data to evaluate
            operation: Operation being performed
        
        Returns:
            List of policy evaluation results
        """
        results = []
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            
            if policy.type in [PolicyType.INPUT_VALIDATION, PolicyType.CONTENT_FILTER, 
                              PolicyType.SIZE_LIMIT]:
                result = self._evaluate_policy(policy, input_data, operation)
                results.append(result)
                
                if not result.passed:
                    self._violation_count += 1
        
        self._evaluation_count += len(results)
        return results
    
    def evaluate_output(self, output_data: Any, operation: str) -> List[PolicyEvaluationResult]:
        """
        Evaluate output against all applicable policies.
        
        Args:
            output_data: Output data to evaluate
            operation: Operation being performed
        
        Returns:
            List of policy evaluation results
        """
        results = []
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            
            if policy.type == PolicyType.OUTPUT_VALIDATION:
                result = self._evaluate_policy(policy, output_data, operation)
                results.append(result)
                
                if not result.passed:
                    self._violation_count += 1
        
        self._evaluation_count += len(results)
        return results
    
    def _evaluate_policy(self, policy: Policy, data: Any, operation: str) -> PolicyEvaluationResult:
        """
        Evaluate a single policy against data.
        
        Args:
            policy: The policy to evaluate
            data: The data to check
            operation: The operation context
        
        Returns:
            PolicyEvaluationResult
        """
        condition = policy.condition
        passed = True
        message = f"Policy {policy.name} passed"
        
        try:
            if policy.type == PolicyType.SIZE_LIMIT:
                passed = self._check_size_limit(data, condition)
                if not passed:
                    message = f"Size limit exceeded: {condition.get('max_size', 'unknown')}"
            
            elif policy.type == PolicyType.CONTENT_FILTER:
                passed = self._check_content_filter(data, condition)
                if not passed:
                    message = f"Content filter triggered: {condition.get('pattern', 'unknown')}"
            
            elif policy.type == PolicyType.INPUT_VALIDATION:
                passed = self._check_input_validation(data, condition)
                if not passed:
                    message = f"Input validation failed: {condition.get('message', 'unknown')}"
            
            elif policy.type == PolicyType.OUTPUT_VALIDATION:
                passed = self._check_output_validation(data, condition)
                if not passed:
                    message = f"Output validation failed: {condition.get('message', 'unknown')}"
            
            elif policy.type == PolicyType.RATE_LIMIT:
                # Rate limiting would require state management
                passed = True
                message = "Rate limit check passed"
        
        except Exception as e:
            passed = False
            message = f"Policy evaluation error: {str(e)}"
        
        return PolicyEvaluationResult(
            policy_id=policy.id,
            passed=passed,
            action=policy.action,
            message=message
        )
    
    def _check_size_limit(self, data: Any, condition: Dict[str, Any]) -> bool:
        """Check if data size is within limits."""
        max_size = condition.get("max_size", float('inf'))
        
        if isinstance(data, str):
            return len(data) <= max_size
        elif isinstance(data, (list, dict)):
            return len(str(data)) <= max_size
        
        return True
    
    def _check_content_filter(self, data: Any, condition: Dict[str, Any]) -> bool:
        """Check if data matches content filter."""
        pattern = condition.get("pattern")
        if not pattern:
            return True
        
        text = str(data)
        blacklist = condition.get("blacklist", [])
        
        # Check blacklist
        for term in blacklist:
            if term.lower() in text.lower():
                return False
        
        # Check regex pattern if provided
        if pattern and isinstance(pattern, str):
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    return False
            except re.error:
                pass
        
        return True
    
    def _check_input_validation(self, data: Any, condition: Dict[str, Any]) -> bool:
        """Check if input meets validation requirements."""
        required_fields = condition.get("required_fields", [])
        
        if isinstance(data, dict):
            for field in required_fields:
                if field not in data:
                    return False
        
        return True
    
    def _check_output_validation(self, data: Any, condition: Dict[str, Any]) -> bool:
        """Check if output meets validation requirements."""
        expected_type = condition.get("type")
        
        if expected_type:
            type_map = {
                "string": str,
                "number": (int, float),
                "boolean": bool,
                "object": dict,
                "array": list
            }
            
            expected_python_type = type_map.get(expected_type)
            if expected_python_type and not isinstance(data, expected_python_type):
                return False
        
        return True
    
    def check_enforcement_needed(self, results: List[PolicyEvaluationResult]) -> bool:
        """
        Check if any policy results require enforcement (deny or require approval).
        
        Args:
            results: List of policy evaluation results
        
        Returns:
            True if enforcement is needed (operation should be blocked)
        """
        for result in results:
            if not result.passed and result.action in [PolicyAction.DENY, PolicyAction.REQUIRE_APPROVAL]:
                return True
        return False
    
    def get_policies(self) -> List[Dict[str, Any]]:
        """Get all policies."""
        return [p.to_dict() for p in self.policies.values()]
    
    def stats(self) -> Dict[str, Any]:
        """Get policy engine statistics."""
        return {
            "total_policies": len(self.policies),
            "enabled_policies": sum(1 for p in self.policies.values() if p.enabled),
            "total_evaluations": self._evaluation_count,
            "total_violations": self._violation_count,
            "violation_rate": round(self._violation_count / self._evaluation_count * 100, 2) 
                if self._evaluation_count > 0 else 0
        }


# Global policy engine instance
_policy_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get the global PolicyEngine instance."""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
        _initialize_default_policies(_policy_engine)
    return _policy_engine


def _initialize_default_policies(engine: PolicyEngine) -> None:
    """Initialize default policies."""
    
    # Size limit policy
    engine.add_policy(Policy(
        id="size_limit_default",
        name="Default Size Limit",
        type=PolicyType.SIZE_LIMIT,
        action=PolicyAction.DENY,
        condition={"max_size": 1000000},  # 1MB
        metadata={"description": "Prevent processing of oversized inputs"}
    ))
    
    # Content filter for sensitive patterns
    engine.add_policy(Policy(
        id="content_filter_sensitive",
        name="Sensitive Content Filter",
        type=PolicyType.CONTENT_FILTER,
        action=PolicyAction.WARN,
        condition={
            "blacklist": ["api_key", "secret_key", "password", "private_key"],
            "pattern": r"sk-[a-zA-Z0-9]{32,}"  # Common secret pattern
        },
        metadata={"description": "Warn on potential secrets in input"}
    ))
