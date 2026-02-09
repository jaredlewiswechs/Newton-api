"""
Construct Studio Cartridges
===========================

Domain-specific constraint modules that plug into the Construct kernel.

A cartridge is a pre-built Floor with domain semantics.
Same physics. Different vocabulary.

Available Cartridges:
- finance: Corporate cards, budgets, spend limits
- infrastructure: Deployment quotas, resource limits
- risk: Probability budgets, exposure limits
- time: Scheduling constraints, deadline budgets
"""

from .finance import (
    CorporateCard,
    Budget,
    SpendLimit,
    ExpenseCategory,
    spend,
    transfer,
)

from .infrastructure import (
    DeploymentQuota,
    ResourcePool,
    ClusterLimits,
    deploy,
    allocate,
)

from .risk import (
    RiskBudget,
    ExposureLimit,
    ProbabilityPool,
    accept_risk,
)

__all__ = [
    # Finance
    "CorporateCard",
    "Budget",
    "SpendLimit",
    "ExpenseCategory",
    "spend",
    "transfer",
    # Infrastructure
    "DeploymentQuota",
    "ResourcePool",
    "ClusterLimits",
    "deploy",
    "allocate",
    # Risk
    "RiskBudget",
    "ExposureLimit",
    "ProbabilityPool",
    "accept_risk",
]
