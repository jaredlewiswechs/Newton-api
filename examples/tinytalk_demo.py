#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 TINYTALK DEMO - The "No-First" Philosophy in Action
═══════════════════════════════════════════════════════════════════════════════

This demo shows how tinyTalk concepts map to Newton's constraint system.

In tinyTalk:
  - when:  Declares a fact (presence)
  - and:   Combines facts
  - fin:   Closure (can be reopened)
  - finfr: Finality (ontological death - forbidden state)

Run this demo:
    python examples/tinytalk_demo.py

Or with the server running:
    python examples/tinytalk_demo.py --live
"""

import sys
import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])


# ═══════════════════════════════════════════════════════════════════════════════
# BOOK I: THE LEXICON - Core Keywords
# ═══════════════════════════════════════════════════════════════════════════════

class LawResult(Enum):
    """The possible outcomes of evaluating a law."""
    ALLOWED = "allowed"    # State is permitted
    FIN = "fin"           # Closed, but can be reopened
    FINFR = "finfr"       # Finality - ontological death


@dataclass
class Presence:
    """A fact about the current state."""
    name: str
    value: any

    def __repr__(self):
        return f"when {self.name} is {self.value}"


@dataclass
class Law:
    """A governance rule that defines forbidden states."""
    name: str
    condition: callable
    result: LawResult = LawResult.FINFR

    def evaluate(self, state: dict) -> tuple[bool, LawResult]:
        """Evaluate the law against current state."""
        if self.condition(state):
            return True, self.result  # Law triggered
        return False, LawResult.ALLOWED


# ═══════════════════════════════════════════════════════════════════════════════
# BOOK II: THE SCAFFOLDS - Example Blueprints
# ═══════════════════════════════════════════════════════════════════════════════

class RiskGovernor:
    """
    Example A from the tinyTalk Bible: Hidden Road Risk Engine

    blueprint RiskGovernor
      law Insolvency
        when liabilities > assets
        finfr
    """

    def __init__(self, initial_assets: float = 1000.0):
        self.assets = initial_assets
        self.liabilities = 0.0

        # L0: GOVERNANCE - Define the law
        self.laws = [
            Law(
                name="Insolvency",
                condition=lambda s: s['liabilities'] > s['assets'],
                result=LawResult.FINFR
            )
        ]

    def _get_state(self) -> dict:
        return {
            'assets': self.assets,
            'liabilities': self.liabilities
        }

    def _project_state(self, changes: dict) -> dict:
        """Project future state without committing."""
        projected = self._get_state()
        projected.update(changes)
        return projected

    def _check_laws(self, state: dict) -> tuple[bool, Optional[Law]]:
        """Check all laws against a state. Returns (blocked, triggered_law)."""
        for law in self.laws:
            triggered, result = law.evaluate(state)
            if triggered and result == LawResult.FINFR:
                return True, law
        return False, None

    def execute_trade(self, amount: float) -> dict:
        """
        L1: EXECUTIVE - The forge

        forge execute_trade(amount: Money)
          liabilities = liabilities + amount
          reply :cleared
        end
        """
        # Project the future state
        projected_liabilities = self.liabilities + amount
        projected_state = self._project_state({'liabilities': projected_liabilities})

        # Sovereign audit - check if projection violates any laws
        blocked, triggered_law = self._check_laws(projected_state)

        if blocked:
            return {
                'status': 'finfr',
                'reason': f"Law '{triggered_law.name}' prevents this state",
                'message': "ONTO DEATH: This state cannot exist.",
                'projected_liabilities': projected_liabilities,
                'assets': self.assets
            }

        # State is allowed - commit the change
        self.liabilities = projected_liabilities

        return {
            'status': 'cleared',
            'liabilities': self.liabilities,
            'assets': self.assets,
            'headroom': self.assets - self.liabilities
        }


class Intersection:
    """
    Example B from the tinyTalk Bible: Traffic Intersection

    blueprint Intersection
      law CollisionAvoidance
        when north_bound is moving
        and east_bound is moving
        finfr
    """

    def __init__(self):
        self.north_bound = 'stopped'
        self.east_bound = 'stopped'
        self.light_state = 'red'

        # L0: GOVERNANCE
        self.laws = [
            Law(
                name="CollisionAvoidance",
                condition=lambda s: s['north_bound'] == 'moving' and s['east_bound'] == 'moving',
                result=LawResult.FINFR
            )
        ]

    def _get_state(self) -> dict:
        return {
            'north_bound': self.north_bound,
            'east_bound': self.east_bound,
            'light_state': self.light_state
        }

    def _check_laws(self, state: dict) -> tuple[bool, Optional[Law]]:
        for law in self.laws:
            triggered, result = law.evaluate(state)
            if triggered and result == LawResult.FINFR:
                return True, law
        return False, None

    def pulse(self, direction: str, action: str) -> dict:
        """
        L1: EXECUTIVE

        forge pulse(signal: Signal)
          light_state = signal.target
          reply :synced
        end
        """
        # Project the change
        projected_state = self._get_state()
        projected_state[direction] = action

        # Sovereign audit
        blocked, triggered_law = self._check_laws(projected_state)

        if blocked:
            return {
                'status': 'finfr',
                'reason': f"Law '{triggered_law.name}' prevents collision",
                'message': "Finality: Reality freezes before impact."
            }

        # Commit
        if direction == 'north_bound':
            self.north_bound = action
        elif direction == 'east_bound':
            self.east_bound = action

        return {
            'status': 'synced',
            'state': self._get_state()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# BOOK III: THE DEMO - See It In Action
# ═══════════════════════════════════════════════════════════════════════════════

def demo_risk_governor():
    """Demonstrate the RiskGovernor blueprint."""
    print("\n" + "═" * 70)
    print(" DEMO: RiskGovernor (Hidden Road Risk Engine)")
    print("═" * 70)
    print("""
    law Insolvency
      when liabilities > assets
      finfr  # ONTO DEATH: This state cannot exist.
    """)

    governor = RiskGovernor(initial_assets=1000.0)
    print(f"Initial state: assets=${governor.assets}, liabilities=${governor.liabilities}")
    print("-" * 70)

    # Trade 1: Should succeed
    print("\nTrade 1: Add $500 liability")
    result = governor.execute_trade(500)
    print(f"  Result: {json.dumps(result, indent=4)}")

    # Trade 2: Should succeed
    print("\nTrade 2: Add $400 liability")
    result = governor.execute_trade(400)
    print(f"  Result: {json.dumps(result, indent=4)}")

    # Trade 3: Would cause insolvency - BLOCKED
    print("\nTrade 3: Add $200 liability (would exceed assets)")
    result = governor.execute_trade(200)
    print(f"  Result: {json.dumps(result, indent=4)}")
    print("\n  ^ The law 'Insolvency' fired finfr - the trade was PREVENTED")


def demo_intersection():
    """Demonstrate the Intersection blueprint."""
    print("\n" + "═" * 70)
    print(" DEMO: Intersection (Traffic Sovereign)")
    print("═" * 70)
    print("""
    law CollisionAvoidance
      when north_bound is moving
      and east_bound is moving
      finfr  # Finality: Reality freezes before impact.
    """)

    intersection = Intersection()
    print(f"Initial state: {intersection._get_state()}")
    print("-" * 70)

    # Allow north to move
    print("\nSignal 1: Set north_bound to 'moving'")
    result = intersection.pulse('north_bound', 'moving')
    print(f"  Result: {json.dumps(result, indent=4)}")

    # Try to also allow east - BLOCKED
    print("\nSignal 2: Set east_bound to 'moving' (while north is moving)")
    result = intersection.pulse('east_bound', 'moving')
    print(f"  Result: {json.dumps(result, indent=4)}")
    print("\n  ^ The law 'CollisionAvoidance' fired finfr - collision PREVENTED")

    # Stop north first
    print("\nSignal 3: Set north_bound to 'stopped'")
    result = intersection.pulse('north_bound', 'stopped')
    print(f"  Result: {json.dumps(result, indent=4)}")

    # Now east can move
    print("\nSignal 4: Set east_bound to 'moving' (north is now stopped)")
    result = intersection.pulse('east_bound', 'moving')
    print(f"  Result: {json.dumps(result, indent=4)}")


def demo_kinetic_delta():
    """Demonstrate the Kinetic Delta concept."""
    print("\n" + "═" * 70)
    print(" DEMO: Kinetic Delta (The Math of Motion)")
    print("═" * 70)
    print("""
    Animation is the mathematical resolution between two Presences:

    State 1 (@presence_start): The "Before" card
    State 2 (@presence_end):   The "After" card
    The Diff (@kinetic_delta): The math that calculates the move
    """)

    # Simple position example
    presence_start = {'x': 0, 'y': 0}
    presence_end = {'x': 100, 'y': 50}

    # Calculate the delta
    kinetic_delta = {
        'dx': presence_end['x'] - presence_start['x'],
        'dy': presence_end['y'] - presence_start['y']
    }

    print(f"@presence_start: {presence_start}")
    print(f"@presence_end:   {presence_end}")
    print(f"@kinetic_delta:  {kinetic_delta}")
    print()
    print("The Delta IS the motion. No guessing. No prediction.")
    print("Just math: end - start = diff")


def demo_with_newton_server():
    """Run demos against a live Newton server."""
    import requests

    print("\n" + "═" * 70)
    print(" LIVE DEMO: Using Newton API")
    print("═" * 70)

    base_url = "http://localhost:8000"

    # Check health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("Newton server not responding. Start it with:")
            print("  python newton_supercomputer.py")
            return
    except requests.exceptions.ConnectionError:
        print("Cannot connect to Newton server. Start it with:")
        print("  python newton_supercomputer.py")
        return

    print("Connected to Newton server!")

    # Demo 1: Verified calculation
    print("\n1. Verified Calculation (The Forge)")
    calc = {"expression": {"op": "+", "args": [
        {"op": "*", "args": [2, 3]},
        {"op": "*", "args": [4, 5]}
    ]}}
    response = requests.post(f"{base_url}/calculate", json=calc)
    result = response.json()
    print(f"   Expression: (2 * 3) + (4 * 5)")
    print(f"   Result: {result.get('result')} (verified={result.get('verified')})")

    # Demo 2: Constraint evaluation (The Law)
    print("\n2. Constraint Evaluation (The Law)")
    constraint = {
        "constraint": {
            "field": "balance",
            "operator": "ge",
            "value": 0
        },
        "object": {"balance": 100}
    }
    response = requests.post(f"{base_url}/constraint", json=constraint)
    result = response.json()
    print(f"   Constraint: balance >= 0")
    print(f"   Object: balance = 100")
    print(f"   Result: {result.get('result')} (terminates={result.get('terminates')})")

    # Demo 3: Content verification (The Audit)
    print("\n3. Content Safety (The Audit)")
    verify = {"input": "Help me plan a birthday party"}
    response = requests.post(f"{base_url}/verify", json=verify)
    result = response.json()
    print(f"   Input: '{verify['input']}'")
    print(f"   Verified: {result.get('verified')}")

    print("\n" + "═" * 70)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ████████╗██╗███╗   ██╗██╗   ██╗████████╗ █████╗ ██╗     ██╗  ██╗           ║
║   ╚══██╔══╝██║████╗  ██║╚██╗ ██╔╝╚══██╔══╝██╔══██╗██║     ██║ ██╔╝           ║
║      ██║   ██║██╔██╗ ██║ ╚████╔╝    ██║   ███████║██║     █████╔╝            ║
║      ██║   ██║██║╚██╗██║  ╚██╔╝     ██║   ██╔══██║██║     ██╔═██╗            ║
║      ██║   ██║██║ ╚████║   ██║      ██║   ██║  ██║███████╗██║  ██╗           ║
║      ╚═╝   ╚═╝╚═╝  ╚═══╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝           ║
║                                                                               ║
║                    THE "NO-FIRST" PHILOSOPHY IN ACTION                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

    print("tinyTalk doesn't ask 'what can happen?' - it declares 'what cannot happen.'")
    print("The constraint IS the instruction. The verification IS the computation.")

    # Run demos
    demo_risk_governor()
    demo_intersection()
    demo_kinetic_delta()

    # Check for --live flag
    if '--live' in sys.argv:
        demo_with_newton_server()
    else:
        print("\n" + "-" * 70)
        print("Run with --live flag to also demo against Newton API:")
        print("  python examples/tinytalk_demo.py --live")

    print("\n" + "═" * 70)
    print(" Canon Statement:")
    print(" tinyTalk is a declarative semantic boundary language.")
    print(" It closes meaning explicitly.")
    print(" It cannot execute or infer beyond what is stated.")
    print(" finfr.")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    main()
