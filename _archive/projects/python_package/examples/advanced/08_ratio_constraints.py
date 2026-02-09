#!/usr/bin/env python3
"""
08_ratio_constraints.py - Advanced Ratio Constraints

Use the f/g ratio system for dimensional analysis and proportional limits.
This is Newton's core insight: finfr = f/g
"""

from newton import (
    Blueprint, field, law, forge, when, finfr,
    ratio, finfr_if_undefined, LawViolation
)


class LeveragedFund(Blueprint):
    """
    A fund with leverage constraints.

    Leverage = debt / equity
    When equity approaches zero, leverage becomes undefined (finfr).
    """

    debt = field(float, default=0.0)
    equity = field(float, default=1000000.0)
    max_leverage = field(float, default=3.0)

    @law
    def no_excessive_leverage(self):
        """Debt/Equity ratio cannot exceed max leverage."""
        when(ratio(self.debt, self.equity) > self.max_leverage, finfr)

    @law
    def no_negative_equity(self):
        """Equity must stay positive."""
        when(self.equity <= 0, finfr)

    @law
    def no_undefined_leverage(self):
        """Prevent division by zero in leverage calculation."""
        finfr_if_undefined(self.debt, self.equity)

    @forge
    def borrow(self, amount: float):
        """Increase debt."""
        self.debt += amount
        leverage = self.debt / self.equity if self.equity > 0 else float('inf')
        return f"Borrowed ${amount:,.0f}. Debt: ${self.debt:,.0f}, Leverage: {leverage:.2f}x"

    @forge
    def repay(self, amount: float):
        """Decrease debt."""
        self.debt -= amount
        leverage = self.debt / self.equity if self.equity > 0 else float('inf')
        return f"Repaid ${amount:,.0f}. Debt: ${self.debt:,.0f}, Leverage: {leverage:.2f}x"

    @forge
    def add_equity(self, amount: float):
        """Increase equity (investment)."""
        self.equity += amount
        return f"Added ${amount:,.0f} equity. Total equity: ${self.equity:,.0f}"

    @forge
    def withdraw_equity(self, amount: float):
        """Decrease equity (distribution)."""
        self.equity -= amount
        return f"Withdrew ${amount:,.0f} equity. Total equity: ${self.equity:,.0f}"

    def status(self):
        leverage = self.debt / self.equity if self.equity > 0 else float('inf')
        return f"Equity: ${self.equity:,.0f}, Debt: ${self.debt:,.0f}, Leverage: {leverage:.2f}x"


class SafetySystem(Blueprint):
    """
    A safety system using ratio constraints.

    Examples: Flash rate for seizure safety, speed limits, etc.
    """

    current_rate = field(float, default=0.0)
    safe_threshold = field(float, default=1.0)

    @law
    def within_safe_ratio(self):
        """Current rate must not exceed safe threshold."""
        when(ratio(self.current_rate, self.safe_threshold) >= 1.0, finfr)

    @forge
    def set_rate(self, rate: float):
        """Set the current rate."""
        self.current_rate = rate
        r = self.current_rate / self.safe_threshold
        return f"Rate: {self.current_rate} (ratio: {r:.2%} of threshold)"


def main():
    print("=" * 60)
    print("  RATIO CONSTRAINTS - f/g Dimensional Analysis")
    print("=" * 60)
    print()

    # Leveraged Fund Demo
    print("--- Leveraged Fund (debt/equity) ---")
    fund = LeveragedFund()
    print(f"Initial: {fund.status()}")
    print(f"Max leverage: {fund.max_leverage}x")
    print()

    # Normal borrowing
    print(fund.borrow(1000000))   # 1:1 leverage
    print(fund.borrow(1000000))   # 2:1 leverage
    print(fund.borrow(500000))    # 2.5:1 leverage
    print()

    # Try to exceed leverage limit
    print("Trying to borrow $1M more (would exceed 3x leverage)...")
    try:
        fund.borrow(1000000)
    except LawViolation as e:
        print(f"BLOCKED: {e}")
    print()

    # Pay down some debt
    print(fund.repay(500000))
    print()

    # Try to withdraw equity (would increase leverage)
    print("Trying to withdraw $500K equity...")
    try:
        fund.withdraw_equity(500000)
    except LawViolation as e:
        print(f"BLOCKED: {e}")
    print()

    # Add equity to allow more borrowing
    print(fund.add_equity(500000))
    print(f"Now: {fund.status()}")
    print()

    # Safety System Demo
    print("--- Safety System (rate/threshold) ---")
    safety = SafetySystem(safe_threshold=10.0)
    print(f"Safe threshold: {safety.safe_threshold}")
    print()

    print(safety.set_rate(3.0))   # 30% of threshold
    print(safety.set_rate(7.0))   # 70% of threshold
    print(safety.set_rate(9.5))   # 95% of threshold
    print()

    # Try to exceed threshold
    print("Trying to set rate to 10.0 (equals threshold)...")
    try:
        safety.set_rate(10.0)
    except LawViolation as e:
        print(f"BLOCKED: {e}")

    print()
    print("Trying to set rate to 15.0 (exceeds threshold)...")
    try:
        safety.set_rate(15.0)
    except LawViolation as e:
        print(f"BLOCKED: {e}")

    print()
    print("=" * 60)
    print("Ratio constraints enable dimensional analysis.")
    print("f/g ratios prevent proportional violations.")
    print("=" * 60)


if __name__ == "__main__":
    main()
