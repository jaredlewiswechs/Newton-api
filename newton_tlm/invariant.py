#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TLM - INVARIANT
1==1 invariant checks and goal equivalence verification.
═══════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import json
from typing import Any, Dict, Set
from dataclasses import dataclass, field


def canonical_hash(obj: Any) -> str:
    """
    Compute deterministic hash of any object.
    
    Uses JSON serialization with sorted keys to ensure
    identical objects always produce identical hashes.
    
    Args:
        obj: Object to hash
        
    Returns:
        SHA256 hash as hex string
    """
    # Convert to JSON with sorted keys for determinism
    json_str = json.dumps(obj, sort_keys=True, default=str)
    # Hash the JSON string
    return hashlib.sha256(json_str.encode()).hexdigest()


def one_equals_one(current: Any, goal: Any) -> bool:
    """
    The fundamental Newton invariant: 1 == 1
    
    Check if current state equals goal state using deterministic hashing.
    This is the basis of verified computation:
    - If current == goal: execute
    - If current != goal: halt
    
    Args:
        current: Current state
        goal: Goal/target state
        
    Returns:
        True if states are equivalent
    """
    return canonical_hash(current) == canonical_hash(goal)


@dataclass
class GoalRegistry:
    """
    Registry of pattern crystallization goals.
    
    Tracks goals that have been established and whether
    they have been achieved.
    
    Attributes:
        goals: Mapping of goal names to target values
        achieved: Set of achieved goal names
    """
    goals: Dict[str, Any] = field(default_factory=dict)
    achieved: Set[str] = field(default_factory=set)
    
    def register_goal(self, name: str, target: Any) -> None:
        """
        Register a new goal.
        
        Args:
            name: Goal identifier
            target: Target state/value for this goal
        """
        self.goals[name] = target
    
    def check_goal(self, name: str, current: Any) -> bool:
        """
        Check if a goal has been achieved.
        
        Uses 1==1 equivalence check.
        
        Args:
            name: Goal identifier
            current: Current state to check
            
        Returns:
            True if goal achieved
            
        Raises:
            KeyError: If goal not registered
        """
        if name not in self.goals:
            raise KeyError(f"Goal '{name}' not registered")
        
        target = self.goals[name]
        is_achieved = one_equals_one(current, target)
        
        if is_achieved:
            self.achieved.add(name)
        
        return is_achieved
    
    def is_achieved(self, name: str) -> bool:
        """
        Check if a goal has been marked as achieved.
        
        Args:
            name: Goal identifier
            
        Returns:
            True if goal in achieved set
        """
        return name in self.achieved
    
    def progress(self) -> Dict[str, bool]:
        """
        Get progress report for all goals.
        
        Returns:
            Dictionary mapping goal names to achievement status
        """
        return {
            name: name in self.achieved
            for name in self.goals.keys()
        }
    
    def all_achieved(self) -> bool:
        """
        Check if all registered goals have been achieved.
        
        Returns:
            True if all goals achieved
        """
        return len(self.achieved) == len(self.goals)
    
    def clear(self) -> None:
        """
        Clear all goals and achievements.
        """
        self.goals.clear()
        self.achieved.clear()
