#!/usr/bin/env python3
"""
04_trading_system.py - Financial Risk Management

A trading desk with position limits and risk controls.
Demonstrates real-world financial constraints.
"""

from newton import (
    Blueprint, field, law, forge, when, finfr,
    Money, ratio, LawViolation
)


class TradingDesk(Blueprint):
    """A trading desk with strict risk controls."""

    # Current positions
    long_position = field(float, default=0.0)   # Positive = bought
    short_position = field(float, default=0.0)  # Positive = sold short
    cash = field(float, default=1000000.0)      # Available cash

    # Risk limits
    max_position = field(float, default=500000.0)    # Max single position
    max_gross = field(float, default=800000.0)       # Max total exposure
    max_leverage = field(float, default=3.0)         # Max leverage ratio

    @law
    def long_position_limit(self):
        """Long position cannot exceed maximum."""
        when(self.long_position > self.max_position, finfr)

    @law
    def short_position_limit(self):
        """Short position cannot exceed maximum."""
        when(self.short_position > self.max_position, finfr)

    @law
    def gross_exposure_limit(self):
        """Total exposure cannot exceed maximum."""
        gross = self.long_position + self.short_position
        when(gross > self.max_gross, finfr)

    @law
    def leverage_limit(self):
        """Leverage ratio must stay within limits."""
        gross = self.long_position + self.short_position
        when(ratio(gross, self.cash) > self.max_leverage, finfr)

    @law
    def no_negative_cash(self):
        """Cash cannot go negative."""
        when(self.cash < 0, finfr)

    @forge
    def buy(self, amount: float, price: float):
        """Open or add to long position."""
        cost = amount * price
        self.long_position += amount
        self.cash -= cost
        return f"Bought {amount} @ ${price:.2f}. Long: {self.long_position}, Cash: ${self.cash:.2f}"

    @forge
    def sell(self, amount: float, price: float):
        """Close long position or open short."""
        proceeds = amount * price
        if amount <= self.long_position:
            # Closing long
            self.long_position -= amount
        else:
            # Opening/adding to short
            self.short_position += (amount - self.long_position)
            self.long_position = 0
        self.cash += proceeds
        return f"Sold {amount} @ ${price:.2f}. Long: {self.long_position}, Short: {self.short_position}"

    @forge
    def cover(self, amount: float, price: float):
        """Close short position."""
        cost = amount * price
        self.short_position -= amount
        self.cash -= cost
        return f"Covered {amount} @ ${price:.2f}. Short: {self.short_position}"

    def status(self):
        """Print current status."""
        gross = self.long_position + self.short_position
        leverage = gross / self.cash if self.cash > 0 else 0
        return f"""
Position Summary:
  Long:  ${self.long_position:,.2f}
  Short: ${self.short_position:,.2f}
  Gross: ${gross:,.2f}
  Cash:  ${self.cash:,.2f}
  Leverage: {leverage:.2f}x
"""


def main():
    print("=" * 60)
    print("  TRADING DESK - Risk Management Demo")
    print("=" * 60)

    desk = TradingDesk()
    print(desk.status())

    # Normal trading
    print("--- Normal Trading ---")
    print(desk.buy(1000, 100))     # Buy 1000 shares @ $100
    print(desk.buy(2000, 100))     # Buy 2000 more
    print(desk.status())

    # Try to exceed position limit
    print("--- Testing Position Limit ---")
    print("Trying to buy 3000 more shares (would exceed $500k limit)...")
    try:
        desk.buy(3000, 100)
    except LawViolation as e:
        print(f"BLOCKED: {e}")
    print(desk.status())

    # Sell to reduce position
    print("--- Reducing Position ---")
    print(desk.sell(1500, 105))  # Sell at profit
    print(desk.status())

    # Try to exceed leverage
    print("--- Testing Leverage Limit ---")
    print("Trying to open large short position...")
    try:
        desk.buy(5000, 150)  # Would create too much leverage
    except LawViolation as e:
        print(f"BLOCKED: {e}")

    print()
    print("=" * 60)
    print("Risk controls prevent dangerous positions.")
    print("The desk can never exceed its mandated limits.")
    print("=" * 60)


if __name__ == "__main__":
    main()
