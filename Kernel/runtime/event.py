from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional


class NSEventType(Enum):
    MOUSE_DOWN = auto()
    MOUSE_UP = auto()
    MOUSE_MOVE = auto()
    KEY_DOWN = auto()
    KEY_UP = auto()


@dataclass
class NSEvent:
    type: NSEventType
    location: Optional[tuple] = None
    button: Optional[int] = None
    modifiers: Optional[int] = None
    timestamp: Optional[float] = None
    user_info: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return {
            'type': self.type.name,
            'location': self.location,
            'button': self.button,
            'modifiers': self.modifiers,
            'timestamp': self.timestamp,
            'user_info': self.user_info,
        }
