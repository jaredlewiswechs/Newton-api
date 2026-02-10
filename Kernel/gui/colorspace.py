"""Simple NSColorSpace shim supporting basic color spaces."""
from dataclasses import dataclass

@dataclass
class NSColorSpace:
    name: str

    @classmethod
    def device_rgb(cls):
        return cls('deviceRGB')

    @classmethod
    def generic_rgb(cls):
        return cls('sRGB')

    def __repr__(self):
        return f"NSColorSpace({self.name})"
