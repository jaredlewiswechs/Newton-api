"""
Risk Cartridge for Construct Studio
===================================

Risk is not a feeling. Risk is geometry.

This cartridge provides constraint-first governance for:
- Probability budgets
- Exposure limits
- Risk accumulation
- Correlation constraints

The unacceptable risk cannot be taken.
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

class RiskBudget(Floor):
    """
    A probability budget.

    Risk is measured in probability units (0.0 to 1.0).
    The total accepted risk cannot exceed the budget.

    Usage:
        budget = RiskBudget()
        new_risk = Matter(0.15, "probability")
        new_risk >> budget  # OK if within budget
    """
    total = Matter(0.20, "probability")  # 20% total risk tolerance


class ExposureLimit(Floor):
    """
    Financial exposure limits.

    Measured in currency units - how much could be lost.
    """
    max_loss = Matter(100000, "USD")
    concentration = Matter(0.10, "ratio")  # No more than 10% in one asset


class ProbabilityPool(Floor):
    """
    A pool of probability for different risk categories.
    """
    market_risk = Matter(0.10, "probability")
    credit_risk = Matter(0.05, "probability")
    operational_risk = Matter(0.05, "probability")
    liquidity_risk = Matter(0.03, "probability")


class VaRLimit(Floor):
    """
    Value at Risk limits.
    """
    daily_var_95 = Matter(50000, "USD")
    daily_var_99 = Matter(100000, "USD")
    weekly_var_95 = Matter(150000, "USD")


# ============================================================================
# MATTER FACTORIES
# ============================================================================

def probability(p: float, label: Optional[str] = None) -> Matter:
    """Create probability Matter (0.0 to 1.0)."""
    if not 0 <= p <= 1:
        raise ConstructError(f"Probability must be between 0 and 1, got {p}")
    return Matter(p, "probability", label)


def percent_risk(p: float, label: Optional[str] = None) -> Matter:
    """Create probability Matter from percentage (0 to 100)."""
    return probability(p / 100, label)


def exposure(amount: float, currency: str = "USD", label: Optional[str] = None) -> Matter:
    """Create exposure Matter."""
    return Matter(amount, currency, label)


def ratio(r: float, label: Optional[str] = None) -> Matter:
    """Create ratio Matter (e.g., concentration ratio)."""
    return Matter(r, "ratio", label)


# ============================================================================
# RISK MODELS
# ============================================================================

@dataclass
class RiskPosition:
    """A position with associated risk."""
    name: str
    value: float
    currency: str = "USD"
    probability_of_loss: float = 0.0
    max_loss_percent: float = 1.0  # Could lose 100% by default

    @property
    def expected_loss(self) -> float:
        return self.value * self.probability_of_loss * self.max_loss_percent

    @property
    def max_loss(self) -> float:
        return self.value * self.max_loss_percent


class RiskCategory(Enum):
    """Categories of risk."""
    MARKET = "market_risk"
    CREDIT = "credit_risk"
    OPERATIONAL = "operational_risk"
    LIQUIDITY = "liquidity_risk"
    OTHER = "other"


# ============================================================================
# CONSTRUCT FUNCTIONS
# ============================================================================

@Construct(floor=RiskBudget, strict=True)
def accept_risk(
    probability: float,
    description: str = "",
    category: RiskCategory = RiskCategory.OTHER
) -> Dict[str, Any]:
    """
    Accept a risk into the portfolio.

    The risk either fits within budget or causes Ontological Death.
    There is no "we'll monitor it" - either it fits or it doesn't.

    Args:
        probability: The probability of the adverse event (0.0 to 1.0)
        description: What this risk is for
        category: The risk category

    Returns:
        Dict with risk acceptance details if successful

    Raises:
        OntologicalDeath: If risk exceeds budget
    """
    budget = RiskBudget._instances.get("RiskBudget")
    if budget is None:
        budget = RiskBudget()

    risk = Matter(probability, "probability", description)
    risk >> budget._capacities["total"]

    return {
        "status": "accepted",
        "probability": probability,
        "description": description,
        "category": category.value,
        "remaining_budget": budget._capacities["total"].remaining.value,
        "utilization": 1 - (budget._capacities["total"].remaining.value / budget._capacities["total"].maximum.value),
        "timestamp": datetime.utcnow().isoformat(),
    }


def check_risk(probability: float, floor: Optional[Floor] = None) -> Dict[str, Any]:
    """
    Check if a risk would fit without actually accepting it.
    """
    if floor is None:
        floor = RiskBudget._instances.get("RiskBudget") or RiskBudget()

    capacity = list(floor._capacities.values())[0]
    remaining = capacity.remaining.value

    would_fit = probability <= remaining

    return {
        "probability": probability,
        "would_accept": would_fit,
        "remaining_before": remaining,
        "remaining_after": remaining - probability if would_fit else remaining,
        "overflow": max(0, probability - remaining),
        "utilization_after": (capacity.current.value + probability) / capacity.maximum.value if would_fit else None,
    }


def categorized_risk(
    amount: float,
    category: RiskCategory,
    floor: Optional[ProbabilityPool] = None
) -> Dict[str, Any]:
    """
    Accept risk into a specific category.
    """
    if floor is None:
        floor = ProbabilityPool._instances.get("ProbabilityPool") or ProbabilityPool()

    capacity_name = category.value
    if capacity_name not in floor._capacities:
        raise ConstructError(f"Unknown risk category: {category}")

    capacity = floor._capacities[capacity_name]
    risk = Matter(amount, "probability", category.value)

    with attempt():
        result = risk >> capacity

        if result.success:
            return {
                "status": "accepted",
                "category": category.value,
                "amount": amount,
                "remaining": capacity.remaining.value,
            }
        else:
            return {
                "status": "rejected",
                "category": category.value,
                "amount": amount,
                "overflow": result.ratio.overflow,
                "reason": f"Exceeds {category.value} budget by {result.ratio.overflow:.4f}",
            }


# ============================================================================
# SIMULATION HELPERS
# ============================================================================

def simulate_portfolio(positions: List[RiskPosition]) -> Dict[str, Any]:
    """
    Simulate a portfolio of risk positions.

    Returns aggregate risk metrics and which positions would fit.
    """
    budget = RiskBudget()  # Fresh budget

    results = {
        "positions": [],
        "accepted": 0,
        "rejected": 0,
        "total_probability": 0,
        "total_exposure": 0,
        "remaining_budget": budget._capacities["total"].remaining.value,
    }

    for pos in positions:
        with attempt():
            risk = Matter(pos.probability_of_loss, "probability", pos.name)
            result = risk >> budget._capacities["total"]

            if result.success:
                results["positions"].append({
                    "name": pos.name,
                    "status": "accepted",
                    "probability": pos.probability_of_loss,
                    "exposure": pos.max_loss,
                })
                results["accepted"] += 1
                results["total_probability"] += pos.probability_of_loss
                results["total_exposure"] += pos.max_loss
            else:
                results["positions"].append({
                    "name": pos.name,
                    "status": "rejected",
                    "probability": pos.probability_of_loss,
                    "overflow": result.ratio.overflow,
                    "reason": f"Would exceed budget by {result.ratio.overflow:.4f}",
                })
                results["rejected"] += 1

    results["remaining_budget"] = budget._capacities["total"].remaining.value

    return results


def var_check(
    amount: float,
    confidence: float = 0.95,
    floor: Optional[VaRLimit] = None
) -> Dict[str, Any]:
    """
    Check Value at Risk against limits.
    """
    if floor is None:
        floor = VaRLimit._instances.get("VaRLimit") or VaRLimit()

    # Select appropriate limit based on confidence
    if confidence >= 0.99:
        capacity_name = "daily_var_99"
    else:
        capacity_name = "daily_var_95"

    capacity = floor._capacities.get(capacity_name)
    if capacity is None:
        return {"error": f"No VaR limit for confidence {confidence}"}

    remaining = capacity.remaining.value
    would_fit = amount <= remaining

    return {
        "var": amount,
        "confidence": confidence,
        "limit_type": capacity_name,
        "would_fit": would_fit,
        "limit": capacity.maximum.value,
        "remaining": remaining,
        "utilization": amount / capacity.maximum.value,
    }


# ============================================================================
# PRESET SCENARIOS
# ============================================================================

class RiskScenarios:
    """Pre-built scenarios for demos and testing."""

    @staticmethod
    def conservative() -> RiskBudget:
        """Conservative risk profile."""
        class ConservativeBudget(Floor):
            total = Matter(0.05, "probability")  # 5% max
        return ConservativeBudget()

    @staticmethod
    def aggressive() -> RiskBudget:
        """Aggressive risk profile."""
        class AggressiveBudget(Floor):
            total = Matter(0.35, "probability")  # 35% max
        return AggressiveBudget()

    @staticmethod
    def sample_positions() -> List[RiskPosition]:
        """Sample risk positions for testing."""
        return [
            RiskPosition("Stock Portfolio", 50000, probability_of_loss=0.05, max_loss_percent=0.30),
            RiskPosition("Bond Holdings", 30000, probability_of_loss=0.02, max_loss_percent=0.10),
            RiskPosition("Crypto", 10000, probability_of_loss=0.15, max_loss_percent=0.80),
            RiskPosition("Real Estate", 100000, probability_of_loss=0.02, max_loss_percent=0.20),
            RiskPosition("Venture Investment", 20000, probability_of_loss=0.30, max_loss_percent=1.0),
        ]
