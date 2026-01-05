#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TLM - PHASES
Phase machine for deterministic state transitions.
═══════════════════════════════════════════════════════════════════════════════
"""

from enum import Enum
from typing import Optional


class Phase(Enum):
    """
    The 10 phases of Newton TLM computation cycle.
    
    Every cycle begins at IDLE (0) and returns to IDLE (0).
    No phase can be skipped. No state mutation occurs in IDLE.
    
    0. IDLE      - Rest state, ready for new input
    1. INGEST    - Accept new input/data
    2. PARSE     - Parse and structure the input
    3. CRYSTALLIZE - Form patterns and structures
    4. DIFFUSE   - Spread activation across graph
    5. CONVERGE  - Consolidate and stabilize
    6. VERIFY    - Check constraints and invariants
    7. COMMIT    - Apply changes to state
    8. REFLECT   - Analyze results and learn
    9. IDLE      - Return to rest (cycle complete)
    """
    IDLE = 0
    INGEST = 1
    PARSE = 2
    CRYSTALLIZE = 3
    DIFFUSE = 4
    CONVERGE = 5
    VERIFY = 6
    COMMIT = 7
    REFLECT = 8


class PhaseMachine:
    """
    Enforces the Newton phase cycle.
    
    Rules:
    - Every cycle returns to IDLE
    - No phase can be skipped
    - No state mutation in IDLE
    
    Attributes:
        current: Current phase
        cycle_count: Number of complete cycles (IDLE -> ... -> IDLE)
    """
    
    def __init__(self):
        self.current: Phase = Phase.IDLE
        self.cycle_count: int = 0
        self._previous: Optional[Phase] = None
    
    def transition(self, to_phase: Phase) -> None:
        """
        Transition to a new phase.
        
        Args:
            to_phase: Target phase
            
        Raises:
            RuntimeError: If transition violates phase rules
        """
        # Save previous for validation
        self._previous = self.current
        
        # Check for valid transitions
        if self.current == Phase.IDLE:
            # From IDLE can only go to INGEST or stay in IDLE
            if to_phase not in [Phase.IDLE, Phase.INGEST]:
                raise RuntimeError(
                    f"Invalid transition from IDLE to {to_phase.name}. "
                    "Must transition to INGEST to start cycle."
                )
        elif self.current == Phase.REFLECT:
            # From REFLECT must return to IDLE
            if to_phase != Phase.IDLE:
                raise RuntimeError(
                    f"Invalid transition from REFLECT to {to_phase.name}. "
                    "Must return to IDLE to complete cycle."
                )
            # Completed a full cycle
            self.cycle_count += 1
        else:
            # Normal forward progression
            expected_next = Phase(self.current.value + 1)
            if to_phase != expected_next:
                raise RuntimeError(
                    f"Invalid transition from {self.current.name} to {to_phase.name}. "
                    f"Expected {expected_next.name}. No phase skipping allowed."
                )
        
        self.current = to_phase
    
    def reset(self) -> None:
        """
        Reset to IDLE state.
        
        This is used for initialization or after errors.
        """
        self.current = Phase.IDLE
        self._previous = None
    
    def can_mutate_state(self) -> bool:
        """
        Check if state mutation is allowed in current phase.
        
        Returns:
            False if in IDLE (no mutation allowed), True otherwise
        """
        return self.current != Phase.IDLE
    
    def is_cycle_complete(self) -> bool:
        """
        Check if we've completed a full cycle.
        
        Returns:
            True if just transitioned back to IDLE from REFLECT
        """
        return self.current == Phase.IDLE and self._previous == Phase.REFLECT
    
    def get_phase_name(self) -> str:
        """
        Get the name of the current phase.
        
        Returns:
            Phase name as string
        """
        return self.current.name
    
    def get_phase_number(self) -> int:
        """
        Get the numeric value of the current phase.
        
        Returns:
            Phase number (0-8)
        """
        return self.current.value
