#!/usr/bin/env python3
"""
Newton PDA - Level 3: Adding Forges
Forges are guarded actions - they check all Laws automatically

Run: python examples/pda_level3.py
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from tinytalk_py import Blueprint, field, law, forge, when, finfr

class Contact(Blueprint):
    """A contact with guarded actions"""
    name = field(str, default="Unknown")
    phone = field(str, default="")
    email = field(str, default="")
    notes = field(str, default="")
    favorite = field(bool, default=False)

    @law
    def must_have_name(self):
        when(self.name == "", finfr)

    @law
    def valid_phone_format(self):
        when(len(self.phone) > 0 and len(self.phone) < 7, finfr)

    @forge
    def update_phone(self, new_phone: str):
        """Change the phone number - Laws are auto-checked!"""
        self.phone = new_phone
        return f"Updated phone to {new_phone}"

    @forge
    def add_note(self, note: str):
        """Add a note about this contact"""
        if self.notes:
            self.notes += f"\n{note}"
        else:
            self.notes = note
        return f"Note added"

    @forge
    def toggle_favorite(self):
        """Mark or unmark as favorite"""
        self.favorite = not self.favorite
        return f"Favorite: {self.favorite}"


if __name__ == "__main__":
    print("=== Level 3: Forges (Guarded Actions) ===\n")

    # Create a contact
    contact = Contact()
    contact.name = "Sam"
    print(f"Created contact: {contact.name}\n")

    # Use forges - these are guarded by laws
    print("--- Using Forges ---")

    result = contact.update_phone("555-7890")
    print(f"1. {result}")

    result = contact.add_note("Met at coffee shop")
    print(f"2. {result}")

    result = contact.add_note("Likes jazz music")
    print(f"3. {result}")

    result = contact.toggle_favorite()
    print(f"4. {result}")

    print(f"\n--- Contact State ---")
    print(f"Name:     {contact.name}")
    print(f"Phone:    {contact.phone}")
    print(f"Favorite: {contact.favorite}")
    print(f"Notes:\n{contact.notes}")

    print("\n--- Why Forges Matter ---")
    print("Every @forge method automatically checks ALL @law rules")
    print("If any law would be violated, the forge is BLOCKED")
    print("You never write try/catch - Newton handles it")
