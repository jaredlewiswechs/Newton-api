#!/usr/bin/env python3
"""
Newton PDA - Level 2: Adding Laws
Now we define what CANNOT happen

Run: python examples/pda_level2.py
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from tinytalk_py import Blueprint, field, law, when, finfr

class Contact(Blueprint):
    """A contact with rules"""
    name = field(str, default="")
    phone = field(str, default="")
    email = field(str, default="")

    @law
    def must_have_name(self):
        """Every contact needs a name - can't be empty"""
        when(self.name == "", finfr)

    @law
    def valid_phone_format(self):
        """If phone is provided, it must have at least 7 characters"""
        when(len(self.phone) > 0 and len(self.phone) < 7, finfr)


if __name__ == "__main__":
    print("=== Level 2: Laws (Constraints) ===\n")

    # This works fine
    print("Creating a valid contact...")
    friend = Contact()
    friend.name = "Alex"
    friend.phone = "555-1234"
    print(f"Created: {friend.name} ({friend.phone})")
    print("Laws passed!\n")

    # Demonstrate law checking
    print("--- Law Demonstration ---")
    print("Law 1: must_have_name - contacts need names")
    print("Law 2: valid_phone_format - phone needs 7+ chars if provided")

    print("\n--- What would be blocked: ---")
    print("  - Empty name: BLOCKED by must_have_name")
    print("  - Phone '123': BLOCKED by valid_phone_format (too short)")
    print("  - Phone '': ALLOWED (no phone is okay, just not a short one)")

    print("\n--- The Key Insight ---")
    print("Regular code: try something, catch the error")
    print("Newton code:  define what's impossible, never worry about it")
