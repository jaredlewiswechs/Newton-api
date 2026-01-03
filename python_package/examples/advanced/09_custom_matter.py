#!/usr/bin/env python3
"""
09_custom_matter.py - Creating Custom Matter Types

Extend the Matter system with your own type-safe units.
"""

from dataclasses import dataclass
from newton import Matter


# ============================================================================
# Custom Matter Type: Energy
# ============================================================================

@dataclass
class Energy(Matter):
    """Energy value. Default unit: J (Joules)."""
    _value: float
    _unit: str = "J"

    def __init__(self, value: float, unit: str = "J"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

    def to_kilowatt_hours(self) -> 'Energy':
        """Convert to kWh."""
        if self._unit == "kWh":
            return self
        elif self._unit == "J":
            return Energy(self._value / 3_600_000, "kWh")
        return self

    def to_joules(self) -> 'Energy':
        """Convert to Joules."""
        if self._unit == "J":
            return self
        elif self._unit == "kWh":
            return Energy(self._value * 3_600_000, "J")
        return self


def Joules(value: float) -> Energy:
    return Energy(value, "J")


def KilowattHours(value: float) -> Energy:
    return Energy(value, "kWh")


# ============================================================================
# Custom Matter Type: Bytes (Data Size)
# ============================================================================

@dataclass
class DataSize(Matter):
    """Data size value. Default unit: bytes."""
    _value: float
    _unit: str = "B"

    def __init__(self, value: float, unit: str = "B"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

    def to_bytes(self) -> 'DataSize':
        """Convert to bytes."""
        multipliers = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
        bytes_val = self._value * multipliers.get(self._unit, 1)
        return DataSize(bytes_val, "B")

    def to_megabytes(self) -> 'DataSize':
        """Convert to megabytes."""
        bytes_val = self.to_bytes().value
        return DataSize(bytes_val / (1024**2), "MB")

    def to_gigabytes(self) -> 'DataSize':
        """Convert to gigabytes."""
        bytes_val = self.to_bytes().value
        return DataSize(bytes_val / (1024**3), "GB")


def Bytes(value: float) -> DataSize:
    return DataSize(value, "B")


def Kilobytes(value: float) -> DataSize:
    return DataSize(value, "KB")


def Megabytes(value: float) -> DataSize:
    return DataSize(value, "MB")


def Gigabytes(value: float) -> DataSize:
    return DataSize(value, "GB")


# ============================================================================
# Custom Matter Type: Angle
# ============================================================================

import math


@dataclass
class Angle(Matter):
    """Angle value. Default unit: degrees."""
    _value: float
    _unit: str = "deg"

    def __init__(self, value: float, unit: str = "deg"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

    def to_degrees(self) -> 'Angle':
        if self._unit == "deg":
            return self
        elif self._unit == "rad":
            return Angle(math.degrees(self._value), "deg")
        return self

    def to_radians(self) -> 'Angle':
        if self._unit == "rad":
            return self
        elif self._unit == "deg":
            return Angle(math.radians(self._value), "rad")
        return self

    def sin(self) -> float:
        rad = self.to_radians().value
        return math.sin(rad)

    def cos(self) -> float:
        rad = self.to_radians().value
        return math.cos(rad)


def Degrees(value: float) -> Angle:
    return Angle(value, "deg")


def Radians(value: float) -> Angle:
    return Angle(value, "rad")


# ============================================================================
# Demo
# ============================================================================

def main():
    print("=" * 60)
    print("  CUSTOM MATTER TYPES - Extending the Type System")
    print("=" * 60)
    print()

    # Energy demo
    print("--- Energy ---")
    battery = KilowattHours(50)  # Electric car battery
    consumption = Joules(1_800_000)  # Some energy used

    print(f"Battery: {battery}")
    print(f"Battery in Joules: {battery.to_joules()}")
    print()
    print(f"Consumption: {consumption}")
    print(f"Consumption in kWh: {consumption.to_kilowatt_hours()}")
    print()

    # Type safety
    print("Trying to add Energy to DataSize...")
    try:
        result = battery + Megabytes(100)
    except TypeError as e:
        print(f"BLOCKED: {e}")
    print()

    # DataSize demo
    print("--- DataSize ---")
    file1 = Megabytes(25.5)
    file2 = Megabytes(14.5)
    total = file1 + file2

    print(f"File 1: {file1}")
    print(f"File 2: {file2}")
    print(f"Total: {total}")
    print(f"Total in GB: {total.to_gigabytes()}")
    print()

    disk = Gigabytes(256)
    used = Megabytes(51200)
    print(f"Disk: {disk}")
    print(f"Used: {used} ({used.to_gigabytes()})")
    print()

    # Angle demo
    print("--- Angle ---")
    angle = Degrees(45)
    print(f"Angle: {angle}")
    print(f"In radians: {angle.to_radians()}")
    print(f"sin(45): {angle.sin():.4f}")
    print(f"cos(45): {angle.cos():.4f}")
    print()

    right_angle = Degrees(90)
    half = right_angle / 2
    print(f"90 / 2 = {half}")
    print()

    # Type safety
    print("Trying to add Angle to Energy...")
    try:
        result = angle + battery
    except TypeError as e:
        print(f"BLOCKED: {e}")

    print()
    print("=" * 60)
    print("Custom Matter types extend type safety to any domain.")
    print("Just subclass Matter and implement value/unit properties.")
    print("=" * 60)


if __name__ == "__main__":
    main()
