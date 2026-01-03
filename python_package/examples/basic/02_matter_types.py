#!/usr/bin/env python3
"""
02_matter_types.py - Type-Safe Units

Prevent unit confusion like the Mars Climate Orbiter disaster.
Matter types ensure you can't accidentally mix incompatible units.
"""

from newton import Money, Mass, Distance, Temperature, Celsius, Fahrenheit


def main():
    print("=" * 60)
    print("  MATTER TYPES - Type-Safe Units")
    print("=" * 60)
    print()

    # =========================================================================
    # Money - Financial Values
    # =========================================================================
    print("--- Money ---")
    budget = Money(1000)
    expense = Money(150)
    tax = Money(50)

    remaining = budget - expense - tax
    print(f"Budget: {budget}")
    print(f"Expense: {expense}")
    print(f"Tax: {tax}")
    print(f"Remaining: {remaining}")
    print()

    # =========================================================================
    # Mass - Weight Values
    # =========================================================================
    print("--- Mass ---")
    package1 = Mass(2.5)
    package2 = Mass(1.5)

    total_weight = package1 + package2
    print(f"Package 1: {package1}")
    print(f"Package 2: {package2}")
    print(f"Total weight: {total_weight}")
    print()

    # =========================================================================
    # Distance - Length Values
    # =========================================================================
    print("--- Distance ---")
    leg1 = Distance(100)
    leg2 = Distance(250)
    leg3 = Distance(150)

    total_distance = leg1 + leg2 + leg3
    print(f"Leg 1: {leg1}")
    print(f"Leg 2: {leg2}")
    print(f"Leg 3: {leg3}")
    print(f"Total distance: {total_distance}")
    print()

    # =========================================================================
    # Temperature - With Conversions
    # =========================================================================
    print("--- Temperature ---")
    room_temp = Celsius(22)
    body_temp = Fahrenheit(98.6)

    print(f"Room temperature: {room_temp}")
    print(f"Room temp in F: {room_temp.to_fahrenheit()}")
    print(f"Room temp in K: {room_temp.to_kelvin()}")
    print()
    print(f"Body temperature: {body_temp}")
    print(f"Body temp in C: {body_temp.to_celsius()}")
    print()

    # =========================================================================
    # Type Safety - Preventing Mistakes
    # =========================================================================
    print("--- Type Safety Demo ---")
    print()
    print("Trying to add Money + Mass...")

    try:
        # This will raise TypeError
        result = budget + package1
        print(f"Result: {result}")
    except TypeError as e:
        print(f"BLOCKED: {e}")

    print()
    print("Trying to compare Distance and Money...")

    try:
        # This will also raise TypeError
        if leg1 > budget:
            print("Distance is greater")
    except TypeError as e:
        print(f"BLOCKED: {e}")

    print()
    print("=" * 60)
    print("Matter types prevent unit confusion at compile time.")
    print("No more Mars Climate Orbiter disasters!")
    print("=" * 60)


if __name__ == "__main__":
    main()
