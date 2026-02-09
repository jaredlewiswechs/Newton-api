#!/usr/bin/env python3
"""
Newton PDA - Level 1: Your First Blueprint
A simple contact - just data, no constraints yet

Run: python examples/pda_level1.py
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from tinytalk_py import Blueprint, field

class Contact(Blueprint):
    """A contact in your PDA"""
    name = field(str, default="")
    phone = field(str, default="")
    email = field(str, default="")


if __name__ == "__main__":
    print("=== Level 1: Basic Blueprint ===\n")

    # Create a contact
    friend = Contact()
    friend.name = "Alex"
    friend.phone = "555-1234"
    friend.email = "alex@email.com"

    print(f"Contact: {friend.name}")
    print(f"Phone:   {friend.phone}")
    print(f"Email:   {friend.email}")

    print("\n--- Try it yourself! ---")
    print("1. Add more fields like 'birthday' or 'address'")
    print("2. Create multiple contacts")
    print("3. Store them in a list")
