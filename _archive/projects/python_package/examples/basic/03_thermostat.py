#!/usr/bin/env python3
"""
03_thermostat.py - Bounded Values with Multiple Laws

A thermostat that cannot be set to dangerous temperatures.
Demonstrates multiple laws working together.
"""

from newton import Blueprint, field, law, forge, when, finfr, LawViolation


class Thermostat(Blueprint):
    """A thermostat with safe temperature bounds."""

    temperature = field(float, default=20.0)
    min_temp = field(float, default=5.0)     # Freeze protection
    max_temp = field(float, default=35.0)    # Safety limit

    @law
    def no_freezing(self):
        """Temperature cannot go below minimum."""
        when(self.temperature < self.min_temp, finfr)

    @law
    def no_overheating(self):
        """Temperature cannot exceed maximum."""
        when(self.temperature > self.max_temp, finfr)

    @forge
    def set_temperature(self, temp: float):
        """Set the target temperature."""
        old_temp = self.temperature
        self.temperature = temp
        return f"Changed from {old_temp}C to {self.temperature}C"

    @forge
    def increase(self, delta: float = 1.0):
        """Increase temperature."""
        self.temperature += delta
        return f"Temperature now {self.temperature}C"

    @forge
    def decrease(self, delta: float = 1.0):
        """Decrease temperature."""
        self.temperature -= delta
        return f"Temperature now {self.temperature}C"


def main():
    print("=" * 60)
    print("  THERMOSTAT - Bounded Temperature Control")
    print("=" * 60)
    print()

    # Create thermostat
    thermostat = Thermostat()
    print(f"Initial temperature: {thermostat.temperature}C")
    print(f"Safe range: {thermostat.min_temp}C - {thermostat.max_temp}C")
    print()

    # Normal operations
    print("--- Normal Operations ---")
    print(thermostat.set_temperature(22))
    print(thermostat.increase(3))
    print(thermostat.decrease(5))
    print()

    # Try to set too high
    print("--- Testing Upper Bound ---")
    print(f"Current: {thermostat.temperature}C")
    print("Trying to set to 40C (above max of 35C)...")
    try:
        thermostat.set_temperature(40)
    except LawViolation as e:
        print(f"BLOCKED: {e}")
        print(f"Temperature still: {thermostat.temperature}C")
    print()

    # Try to set too low
    print("--- Testing Lower Bound ---")
    print(f"Current: {thermostat.temperature}C")
    print("Trying to set to 0C (below min of 5C)...")
    try:
        thermostat.set_temperature(0)
    except LawViolation as e:
        print(f"BLOCKED: {e}")
        print(f"Temperature still: {thermostat.temperature}C")
    print()

    # Incremental changes hitting bounds
    print("--- Incremental Changes ---")
    thermostat.set_temperature(33)
    print(f"Set to {thermostat.temperature}C")

    print("Trying to increase by 5...")
    try:
        thermostat.increase(5)
    except LawViolation as e:
        print(f"BLOCKED: {e}")
        print(f"Temperature still: {thermostat.temperature}C")

    print()
    print("=" * 60)
    print("Multiple laws enforce safe temperature bounds.")
    print("The thermostat can never reach dangerous temperatures.")
    print("=" * 60)


if __name__ == "__main__":
    main()
