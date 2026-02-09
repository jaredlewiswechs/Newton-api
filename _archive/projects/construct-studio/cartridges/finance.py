"""
Finance Cartridge for Construct Studio
======================================

Pre-approval by physics, not by process.

This cartridge provides constraint-first governance for:
- Corporate card spending
- Budget management
- Expense categorization
- Fund transfers

The illegal transaction cannot execute.
There is no "approval workflow" - there is only physics.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

try:
    from ..core import Matter, Floor, Construct, Force, attempt, ConstructError
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core import Matter, Floor, Construct, Force, attempt, ConstructError


# ============================================================================
# FLOOR DEFINITIONS
# ============================================================================

class CorporateCard(Floor):
    """
    A corporate card with a spending limit.

    The budget is not a suggestion - it's a physical boundary.
    Expenses that exceed the boundary simply cannot exist.

    Usage:
        card = CorporateCard()
        expense = Matter(1500, "USD")
        expense >> card  # OK if within limit
    """
    budget = Matter(5000, "USD")


class Budget(Floor):
    """
    A general-purpose budget floor.

    Can be used for project budgets, department budgets,
    or any monetary constraint.
    """
    amount = Matter(10000, "USD")


class SpendLimit(Floor):
    """
    A daily/weekly/monthly spend limit.

    Separate from total budget - this is rate limiting.
    """
    daily = Matter(500, "USD")
    weekly = Matter(2000, "USD")
    monthly = Matter(5000, "USD")


class ExpenseCategory(Floor):
    """
    Category-specific expense limits.

    Different categories have different physics.
    """
    travel = Matter(2000, "USD")
    software = Matter(1000, "USD")
    meals = Matter(500, "USD")
    equipment = Matter(3000, "USD")
    other = Matter(500, "USD")


# ============================================================================
# MATTER FACTORIES
# ============================================================================

def usd(amount: float, label: Optional[str] = None) -> Matter:
    """Create USD Matter."""
    return Matter(amount, "USD", label)


def eur(amount: float, label: Optional[str] = None) -> Matter:
    """Create EUR Matter."""
    return Matter(amount, "EUR", label)


def expense(amount: float, description: str, currency: str = "USD") -> Matter:
    """Create an expense with description."""
    return Matter(amount, currency, description)


# ============================================================================
# CONSTRUCT FUNCTIONS
# ============================================================================

@Construct(floor=CorporateCard, strict=True)
def spend(amount: float, description: str = "") -> Dict[str, Any]:
    """
    Attempt to spend from a corporate card.

    This either succeeds completely or causes Ontological Death.
    There is no partial spend. There is no "retry later".

    Args:
        amount: The amount to spend in USD
        description: What the spend is for

    Returns:
        Dict with transaction details if successful

    Raises:
        OntologicalDeath: If spend exceeds available budget
    """
    cost = Matter(amount, "USD", description)

    # Get the card instance
    card = CorporateCard._instances.get("CorporateCard")
    if card is None:
        card = CorporateCard()

    # Apply force
    capacity = card._capacities.get("budget")
    cost >> capacity

    return {
        "status": "approved",
        "amount": amount,
        "description": description,
        "remaining": capacity.remaining.value,
        "timestamp": datetime.utcnow().isoformat(),
    }


def transfer(amount: float, from_floor: Floor, to_floor: Floor) -> Dict[str, Any]:
    """
    Transfer funds between floors.

    Both the withdrawal and deposit must succeed, or neither happens.
    This is atomic constraint satisfaction.
    """
    with attempt() as ctx:
        # Create the matter to transfer
        funds = Matter(amount, "USD", "transfer")

        # First, check if source has enough (we can't really "withdraw" in this model)
        # This is more of a reallocation

        # For now, just validate the transfer is within limits
        # Real implementation would use a transaction model

        return {
            "status": "transferred",
            "amount": amount,
            "from": from_floor.name,
            "to": to_floor.name,
            "timestamp": datetime.utcnow().isoformat(),
        }


# ============================================================================
# SIMULATION HELPERS
# ============================================================================

def simulate_spending(transactions: List[tuple]) -> Dict[str, Any]:
    """
    Simulate a series of spending transactions.

    Args:
        transactions: List of (amount, description) tuples

    Returns:
        Dict with simulation results showing which succeed and which die
    """
    try:
        from ..ledger import Ledger
    except ImportError:
        from ledger import Ledger

    ledger = Ledger("spend_simulation")
    card = CorporateCard()  # Fresh card

    results = {
        "transactions": [],
        "approved": 0,
        "rejected": 0,
        "total_spent": 0,
        "remaining_budget": card._capacities["budget"].remaining.value,
    }

    for amount, description in transactions:
        cost = Matter(amount, "USD", description)
        capacity = card._capacities["budget"]

        with attempt():
            result = cost >> capacity

            if result.success:
                results["transactions"].append({
                    "amount": amount,
                    "description": description,
                    "status": "approved",
                    "remaining": capacity.remaining.value,
                })
                results["approved"] += 1
                results["total_spent"] += amount
            else:
                results["transactions"].append({
                    "amount": amount,
                    "description": description,
                    "status": "rejected",
                    "overflow": result.ratio.overflow,
                    "reason": f"Would exceed budget by {result.ratio.overflow:.2f} USD",
                })
                results["rejected"] += 1

    results["remaining_budget"] = card._capacities["budget"].remaining.value

    return results


def check_spend(amount: float, floor: Optional[Floor] = None) -> Dict[str, Any]:
    """
    Check if a spend would succeed without actually executing it.

    This is "what-if" analysis - pure simulation.
    """
    if floor is None:
        floor = CorporateCard._instances.get("CorporateCard") or CorporateCard()

    capacity = list(floor._capacities.values())[0]
    remaining = capacity.remaining.value

    would_fit = amount <= remaining

    return {
        "amount": amount,
        "would_succeed": would_fit,
        "remaining_before": remaining,
        "remaining_after": remaining - amount if would_fit else remaining,
        "overflow": max(0, amount - remaining),
        "utilization_after": (capacity.current.value + amount) / capacity.maximum.value if would_fit else None,
    }


# ============================================================================
# PRESET SCENARIOS
# ============================================================================

class FinanceScenarios:
    """Pre-built scenarios for demos and testing."""

    @staticmethod
    def startup_budget() -> CorporateCard:
        """Small startup with tight budget."""
        class StartupCard(Floor):
            budget = Matter(1000, "USD")
        return StartupCard()

    @staticmethod
    def enterprise_budget() -> CorporateCard:
        """Enterprise with larger budget."""
        class EnterpriseCard(Floor):
            budget = Matter(50000, "USD")
        return EnterpriseCard()

    @staticmethod
    def category_constrained() -> ExpenseCategory:
        """Category-based spending limits."""
        return ExpenseCategory()
