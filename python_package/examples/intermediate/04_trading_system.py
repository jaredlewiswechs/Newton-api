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

    # Current positions (in DOLLAR VALUE, not share count)
    long_value = field(float, default=0.0)    # Dollar value of long positions
    short_value = field(float, default=0.0)   # Dollar value of short positions
    cash = field(float, default=1000000.0)    # Available cash

    # Risk limits (in dollars)
    max_position = field(float, default=500000.0)    # Max single position value
    max_gross = field(float, default=800000.0)       # Max total exposure
    max_leverage = field(float, default=3.0)         # Max leverage ratio

    @law
    def long_position_limit(self):
        """Long position value cannot exceed maximum."""
        when(self.long_value > self.max_position, finfr)

    @law
    def short_position_limit(self):
        """Short position value cannot exceed maximum."""
        when(self.short_value > self.max_position, finfr)

    @law
    def gross_exposure_limit(self):
        """Total exposure cannot exceed maximum."""
        gross = self.long_value + self.short_value
        when(gross > self.max_gross, finfr)

    @law
    def leverage_limit(self):
        """Leverage ratio must stay within limits."""
        gross = self.long_value + self.short_value
        when(ratio(gross, self.cash) > self.max_leverage, finfr)

    @law
    def no_negative_cash(self):
        """Cash cannot go negative."""
        when(self.cash < 0, finfr)

    @forge
    def buy(self, shares: float, price: float):
        """Open or add to long position."""
        cost = shares * price
        self.long_value += cost
        self.cash -= cost
        return f"Bought {shares:.0f} shares @ ${price:.2f}. Long: ${self.long_value:,.0f}, Cash: ${self.cash:,.0f}"

    @forge
    def sell(self, shares: float, price: float):
        """Close long position or open short."""
        value = shares * price
        if value <= self.long_value:
            # Closing long
            self.long_value -= value
        else:
            # Opening/adding to short
            self.short_value += (value - self.long_value)
            self.long_value = 0
        self.cash += value
        return f"Sold {shares:.0f} shares @ ${price:.2f}. Long: ${self.long_value:,.0f}, Short: ${self.short_value:,.0f}"

    @forge
    def cover(self, shares: float, price: float):
        """Close short position."""
        value = shares * price
        self.short_value -= value
        self.cash -= value
        return f"Covered {shares:.0f} shares @ ${price:.2f}. Short: ${self.short_value:,.0f}"

    def status(self):
        """Print current status."""
        gross = self.long_value + self.short_value
        leverage = gross / self.cash if self.cash > 0 else 0
        return f"""
Position Summary:
  Long:  ${self.long_value:,.0f}
  Short: ${self.short_value:,.0f}
  Gross: ${gross:,.0f}
  Cash:  ${self.cash:,.0f}
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
