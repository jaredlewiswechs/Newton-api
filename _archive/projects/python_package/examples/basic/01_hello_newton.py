#!/usr/bin/env python3
"""
01_hello_newton.py - Your First Newton Program

The classic bank account that can't overdraft.
This demonstrates the core "No-First" philosophy.
"""

from newton import Blueprint, field, law, forge, when, finfr, LawViolation


class BankAccount(Blueprint):
    """A bank account that cannot have a negative balance."""

    balance = field(float, default=100.0)

    @law
    def no_overdraft(self):
        """Balance must never go negative."""
        when(self.balance < 0, finfr)

    @forge
    def deposit(self, amount: float):
        """Add money to the account."""
        self.balance += amount
        return f"Deposited ${amount:.2f}. Balance: ${self.balance:.2f}"

    @forge
    def withdraw(self, amount: float):
        """Remove money from the account."""
        self.balance -= amount
        return f"Withdrew ${amount:.2f}. Balance: ${self.balance:.2f}"


if __name__ == "__main__":
    print("=" * 60)
    print("  HELLO NEWTON - Bank Account Demo")
    print("=" * 60)
    print()

    # Create account with $100
    account = BankAccount()
    print(f"Created account with ${account.balance:.2f}")

    # Deposit some money
    print()
    print(account.deposit(50))

    # Make some withdrawals
    print(account.withdraw(30))
    print(account.withdraw(50))

    # Current balance is $70
    print()
    print(f"Current balance: ${account.balance:.2f}")

    # Try to withdraw $100 - this would make balance negative
    print()
    print("Attempting to withdraw $100 (would cause overdraft)...")
    try:
        account.withdraw(100)
        print("SUCCESS - this shouldn't happen!")
    except LawViolation as e:
        print(f"BLOCKED: {e}")
        print(f"Balance is STILL ${account.balance:.2f}")

    print()
    print("=" * 60)
    print("The 'no_overdraft' law prevented the forbidden state.")
    print("This is the 'No-First' philosophy: define what cannot happen.")
    print("=" * 60)
