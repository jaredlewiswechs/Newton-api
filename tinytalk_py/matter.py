"""
═══════════════════════════════════════════════════════════════════════════════
 tinyTalk Matter - Typed Values with Units
═══════════════════════════════════════════════════════════════════════════════

Matter types prevent unit confusion - you can't accidentally add Money to Mass.
This prevents bugs like the Mars Climate Orbiter disaster.
"""

from dataclasses import dataclass
from typing import TypeVar, Generic, Union
from abc import ABC, abstractmethod


class Matter(ABC):
    """
    Base class for all typed values with units.

    Matter enforces type safety:
        Money(100) + Money(50)  -> Money(150)  # OK
        Money(100) + Mass(50)   -> TypeError    # Prevented
    """

    @property
    @abstractmethod
    def value(self) -> float:
        """The numeric value."""
        pass

    @property
    @abstractmethod
    def unit(self) -> str:
        """The unit string."""
        pass

    def __add__(self, other):
        if type(self) != type(other):
            raise TypeError(
                f"Cannot add {type(self).__name__} and {type(other).__name__}"
            )
        return type(self)(self.value + other.value)

    def __sub__(self, other):
        if type(self) != type(other):
            raise TypeError(
                f"Cannot subtract {type(other).__name__} from {type(self).__name__}"
            )
        return type(self)(self.value - other.value)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value * other)
        raise TypeError(f"Cannot multiply {type(self).__name__} by {type(other).__name__}")

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value / other)
        if type(self) == type(other):
            return self.value / other.value  # Returns scalar
        raise TypeError(f"Cannot divide {type(self).__name__} by {type(other).__name__}")

    def __lt__(self, other):
        if type(self) != type(other):
            raise TypeError(
                f"Cannot compare {type(self).__name__} with {type(other).__name__}"
            )
        return self.value < other.value

    def __le__(self, other):
        if type(self) != type(other):
            raise TypeError(
                f"Cannot compare {type(self).__name__} with {type(other).__name__}"
            )
        return self.value <= other.value

    def __gt__(self, other):
        if type(self) != type(other):
            raise TypeError(
                f"Cannot compare {type(self).__name__} with {type(other).__name__}"
            )
        return self.value > other.value

    def __ge__(self, other):
        if type(self) != type(other):
            raise TypeError(
                f"Cannot compare {type(self).__name__} with {type(other).__name__}"
            )
        return self.value >= other.value

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.value == other.value

    def __repr__(self):
        return f"{type(self).__name__}({self.value})"

    def __str__(self):
        return f"{self.value} {self.unit}"


# ═══════════════════════════════════════════════════════════════════════════════
# FINANCIAL MATTER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Money(Matter):
    """Monetary value. Default unit: USD."""
    _value: float
    _unit: str = "USD"

    def __init__(self, value: float, unit: str = "USD"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit


# ═══════════════════════════════════════════════════════════════════════════════
# PHYSICAL MATTER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Mass(Matter):
    """Mass value. Default unit: kg."""
    _value: float
    _unit: str = "kg"

    def __init__(self, value: float, unit: str = "kg"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit


def Kilograms(value: float) -> Mass:
    """Create a Mass in kilograms."""
    return Mass(value, "kg")


@dataclass
class Distance(Matter):
    """Distance value. Default unit: m."""
    _value: float
    _unit: str = "m"

    def __init__(self, value: float, unit: str = "m"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit


def Meters(value: float) -> Distance:
    """Create a Distance in meters."""
    return Distance(value, "m")


@dataclass
class Volume(Matter):
    """Volume value. Default unit: L."""
    _value: float
    _unit: str = "L"

    def __init__(self, value: float, unit: str = "L"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit


def Liters(value: float) -> Volume:
    """Create a Volume in liters."""
    return Volume(value, "L")


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPERATURE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Temperature(Matter):
    """Temperature value with unit conversion."""
    _value: float
    _unit: str = "C"

    def __init__(self, value: float, unit: str = "C"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

    def to_celsius(self) -> 'Temperature':
        if self._unit == "C":
            return self
        elif self._unit == "F":
            return Temperature((self._value - 32) * 5 / 9, "C")
        elif self._unit == "K":
            return Temperature(self._value - 273.15, "C")
        return self

    def to_fahrenheit(self) -> 'Temperature':
        if self._unit == "F":
            return self
        elif self._unit == "C":
            return Temperature(self._value * 9 / 5 + 32, "F")
        elif self._unit == "K":
            return Temperature((self._value - 273.15) * 9 / 5 + 32, "F")
        return self

    def to_kelvin(self) -> 'Temperature':
        if self._unit == "K":
            return self
        elif self._unit == "C":
            return Temperature(self._value + 273.15, "K")
        elif self._unit == "F":
            return Temperature((self._value - 32) * 5 / 9 + 273.15, "K")
        return self

    def __lt__(self, other):
        if not isinstance(other, Temperature):
            raise TypeError(f"Cannot compare Temperature with {type(other).__name__}")
        return self.to_celsius().value < other.to_celsius().value

    def __gt__(self, other):
        if not isinstance(other, Temperature):
            raise TypeError(f"Cannot compare Temperature with {type(other).__name__}")
        return self.to_celsius().value > other.to_celsius().value

    def __le__(self, other):
        if not isinstance(other, Temperature):
            raise TypeError(f"Cannot compare Temperature with {type(other).__name__}")
        return self.to_celsius().value <= other.to_celsius().value

    def __ge__(self, other):
        if not isinstance(other, Temperature):
            raise TypeError(f"Cannot compare Temperature with {type(other).__name__}")
        return self.to_celsius().value >= other.to_celsius().value


def Celsius(value: float) -> Temperature:
    """Create a Temperature in Celsius."""
    return Temperature(value, "C")


def Fahrenheit(value: float) -> Temperature:
    """Create a Temperature in Fahrenheit."""
    return Temperature(value, "F")


# ═══════════════════════════════════════════════════════════════════════════════
# PRESSURE & FLOW
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Pressure(Matter):
    """Pressure value. Default unit: PSI."""
    _value: float
    _unit: str = "PSI"

    def __init__(self, value: float, unit: str = "PSI"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit


def PSI(value: float) -> Pressure:
    """Create a Pressure in PSI."""
    return Pressure(value, "PSI")


@dataclass
class FlowRate(Matter):
    """Flow rate value. Default unit: L/min."""
    _value: float
    _unit: str = "L/min"

    def __init__(self, value: float, unit: str = "L/min"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit


# ═══════════════════════════════════════════════════════════════════════════════
# MOTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Velocity(Matter):
    """Velocity value. Default unit: m/s."""
    _value: float
    _unit: str = "m/s"

    def __init__(self, value: float, unit: str = "m/s"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit


@dataclass
class Time(Matter):
    """Time value. Default unit: s."""
    _value: float
    _unit: str = "s"

    def __init__(self, value: float, unit: str = "s"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit
