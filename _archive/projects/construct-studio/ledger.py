"""
Construct Studio Ledger
=======================

The immutable audit trail. Every force application is recorded.
The Ledger is append-only - it cannot be modified, only extended.

The Ledger serves three purposes:
1. Compliance artifact - prove what happened
2. Debug tool - understand why death occurred
3. Simulation replay - reproduce any state

In CAD terms: the Ledger is the version history.
In finance terms: the Ledger is the audit log.
In physics terms: the Ledger is the timeline.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import json
import uuid
import threading
from pathlib import Path


class EntryType(Enum):
    """Types of ledger entries."""
    FORCE_SUCCESS = "force_success"      # Force applied successfully
    FORCE_DEATH = "force_death"          # Force caused Ontological Death
    FLOOR_CREATED = "floor_created"      # New Floor instantiated
    FLOOR_RESET = "floor_reset"          # Floor capacities reset
    SIMULATION_START = "sim_start"       # Simulation begun
    SIMULATION_END = "sim_end"           # Simulation ended
    CHECKPOINT = "checkpoint"            # Manual checkpoint


@dataclass
class LedgerEntry:
    """
    A single immutable entry in the Ledger.

    Each entry captures a moment in the constraint timeline.
    """

    entry_id: str
    timestamp: datetime
    entry_type: EntryType

    # Force details (for force entries)
    matter_value: Optional[float] = None
    matter_unit: Optional[str] = None
    matter_label: Optional[str] = None

    # Target details
    target_name: Optional[str] = None
    target_capacity_before: Optional[float] = None
    target_capacity_after: Optional[float] = None
    target_maximum: Optional[float] = None

    # Ratio details
    ratio_value: Optional[float] = None
    ratio_fits: Optional[bool] = None
    overflow: Optional[float] = None

    # Additional context
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.entry_id is None:
            self.entry_id = str(uuid.uuid4())[:12]

    @property
    def success(self) -> bool:
        return self.entry_type == EntryType.FORCE_SUCCESS

    @property
    def death(self) -> bool:
        return self.entry_type == EntryType.FORCE_DEATH

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "entry_type": self.entry_type.value,
            "matter": {
                "value": self.matter_value,
                "unit": self.matter_unit,
                "label": self.matter_label,
            } if self.matter_value is not None else None,
            "target": {
                "name": self.target_name,
                "capacity_before": self.target_capacity_before,
                "capacity_after": self.target_capacity_after,
                "maximum": self.target_maximum,
            } if self.target_name else None,
            "ratio": {
                "value": self.ratio_value,
                "fits": self.ratio_fits,
                "overflow": self.overflow,
            } if self.ratio_value is not None else None,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LedgerEntry':
        """Create from dictionary."""
        matter = data.get("matter") or {}
        target = data.get("target") or {}
        ratio = data.get("ratio") or {}

        return cls(
            entry_id=data["entry_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            entry_type=EntryType(data["entry_type"]),
            matter_value=matter.get("value"),
            matter_unit=matter.get("unit"),
            matter_label=matter.get("label"),
            target_name=target.get("name"),
            target_capacity_before=target.get("capacity_before"),
            target_capacity_after=target.get("capacity_after"),
            target_maximum=target.get("maximum"),
            ratio_value=ratio.get("value"),
            ratio_fits=ratio.get("fits"),
            overflow=ratio.get("overflow"),
            context=data.get("context", {}),
        )

    def __repr__(self) -> str:
        if self.death:
            return f"[{self.entry_id}] DEATH: {self.matter_value} {self.matter_unit} >> {self.target_name} (overflow: {self.overflow})"
        elif self.success:
            return f"[{self.entry_id}] OK: {self.matter_value} {self.matter_unit} >> {self.target_name} ({self.ratio_value:.1%})"
        else:
            return f"[{self.entry_id}] {self.entry_type.value}"


class Ledger:
    """
    The immutable audit trail for Construct operations.

    Features:
    - Append-only: entries cannot be modified
    - Thread-safe: multiple constructs can write simultaneously
    - Serializable: can be persisted to JSON
    - Queryable: find entries by type, target, time range

    Usage:
        ledger = Ledger("my_simulation")

        # Entries are automatically recorded by Force
        # But you can also record manually:
        ledger.checkpoint("Before big transaction")

        # Query the ledger:
        deaths = ledger.get_deaths()
        recent = ledger.get_recent(10)
        by_target = ledger.get_by_target("Budget")
    """

    def __init__(self, name: str = "default"):
        self.name = name
        self._entries: List[LedgerEntry] = []
        self._lock = threading.Lock()
        self.created_at = datetime.utcnow()

    def _append(self, entry: LedgerEntry) -> None:
        """Thread-safe append."""
        with self._lock:
            self._entries.append(entry)

    def record_success(
        self,
        matter: 'Matter',
        target: Any,
        ratio: 'Ratio',
        context: Optional[Dict[str, Any]] = None
    ) -> LedgerEntry:
        """Record a successful force application."""
        # Import here to avoid circular imports
        try:
            from .core import Capacity, Floor
        except ImportError:
            from core import Capacity, Floor

        target_name = self._get_target_name(target)
        capacity = self._get_capacity(target)

        entry = LedgerEntry(
            entry_id=str(uuid.uuid4())[:12],
            timestamp=datetime.utcnow(),
            entry_type=EntryType.FORCE_SUCCESS,
            matter_value=matter.value,
            matter_unit=matter.unit,
            matter_label=matter.label,
            target_name=target_name,
            target_capacity_before=ratio.denominator + matter.value,
            target_capacity_after=ratio.denominator,
            target_maximum=capacity.maximum.value if capacity else None,
            ratio_value=ratio.value,
            ratio_fits=True,
            overflow=0,
            context=context or {},
        )

        self._append(entry)
        return entry

    def record_death(
        self,
        matter: 'Matter',
        target: Any,
        ratio: 'Ratio',
        context: Optional[Dict[str, Any]] = None
    ) -> LedgerEntry:
        """Record an Ontological Death."""
        try:
            from .core import Capacity, Floor
        except ImportError:
            from core import Capacity, Floor

        target_name = self._get_target_name(target)
        capacity = self._get_capacity(target)

        entry = LedgerEntry(
            entry_id=str(uuid.uuid4())[:12],
            timestamp=datetime.utcnow(),
            entry_type=EntryType.FORCE_DEATH,
            matter_value=matter.value,
            matter_unit=matter.unit,
            matter_label=matter.label,
            target_name=target_name,
            target_capacity_before=ratio.denominator,
            target_capacity_after=ratio.denominator,  # Unchanged - death
            target_maximum=capacity.maximum.value if capacity else None,
            ratio_value=ratio.value,
            ratio_fits=False,
            overflow=ratio.overflow,
            context=context or {},
        )

        self._append(entry)
        return entry

    def checkpoint(self, message: str, context: Optional[Dict[str, Any]] = None) -> LedgerEntry:
        """Record a manual checkpoint."""
        entry = LedgerEntry(
            entry_id=str(uuid.uuid4())[:12],
            timestamp=datetime.utcnow(),
            entry_type=EntryType.CHECKPOINT,
            context={"message": message, **(context or {})},
        )
        self._append(entry)
        return entry

    def _get_target_name(self, target: Any) -> str:
        """Extract target name."""
        try:
            from .core import Capacity, Floor
        except ImportError:
            from core import Capacity, Floor

        if isinstance(target, Capacity):
            return target.name
        if isinstance(target, Floor):
            return target.name
        if isinstance(target, type):
            return target.__name__
        return str(target)

    def _get_capacity(self, target: Any) -> Optional['Capacity']:
        """Extract capacity from target."""
        try:
            from .core import Capacity, Floor
        except ImportError:
            from core import Capacity, Floor

        if isinstance(target, Capacity):
            return target
        if isinstance(target, Floor):
            caps = list(target._capacities.values())
            return caps[0] if caps else None
        return None

    # Query methods

    @property
    def entries(self) -> List[LedgerEntry]:
        """Get all entries (read-only copy)."""
        with self._lock:
            return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self.entries)

    def get_recent(self, n: int = 10) -> List[LedgerEntry]:
        """Get the N most recent entries."""
        with self._lock:
            return list(self._entries[-n:])

    def get_deaths(self) -> List[LedgerEntry]:
        """Get all Ontological Death entries."""
        return [e for e in self.entries if e.death]

    def get_successes(self) -> List[LedgerEntry]:
        """Get all successful force entries."""
        return [e for e in self.entries if e.success]

    def get_by_target(self, target_name: str) -> List[LedgerEntry]:
        """Get entries for a specific target."""
        return [e for e in self.entries if e.target_name == target_name]

    def get_by_type(self, entry_type: EntryType) -> List[LedgerEntry]:
        """Get entries of a specific type."""
        return [e for e in self.entries if e.entry_type == entry_type]

    def get_time_range(
        self,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[LedgerEntry]:
        """Get entries within a time range."""
        end = end or datetime.utcnow()
        return [e for e in self.entries if start <= e.timestamp <= end]

    # Statistics

    @property
    def stats(self) -> Dict[str, Any]:
        """Get ledger statistics."""
        entries = self.entries
        deaths = [e for e in entries if e.death]
        successes = [e for e in entries if e.success]

        return {
            "total_entries": len(entries),
            "successes": len(successes),
            "deaths": len(deaths),
            "death_rate": len(deaths) / len(entries) if entries else 0,
            "first_entry": entries[0].timestamp.isoformat() if entries else None,
            "last_entry": entries[-1].timestamp.isoformat() if entries else None,
            "targets": list(set(e.target_name for e in entries if e.target_name)),
        }

    # Serialization

    def to_json(self, indent: int = 2) -> str:
        """Serialize ledger to JSON."""
        return json.dumps({
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "stats": self.stats,
            "entries": [e.to_dict() for e in self.entries],
        }, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> 'Ledger':
        """Deserialize ledger from JSON."""
        data = json.loads(json_str)
        ledger = cls(data["name"])
        ledger.created_at = datetime.fromisoformat(data["created_at"])
        for entry_data in data["entries"]:
            ledger._entries.append(LedgerEntry.from_dict(entry_data))
        return ledger

    def save(self, path: Union[str, Path]) -> None:
        """Save ledger to file."""
        path = Path(path)
        path.write_text(self.to_json())

    @classmethod
    def load(cls, path: Union[str, Path]) -> 'Ledger':
        """Load ledger from file."""
        path = Path(path)
        return cls.from_json(path.read_text())

    def clear(self) -> None:
        """Clear all entries. Use with caution."""
        with self._lock:
            self._entries.clear()

    # Display

    def print_summary(self) -> None:
        """Print a summary of the ledger."""
        stats = self.stats
        print(f"\n╔══════════════════════════════════════════╗")
        print(f"║  LEDGER: {self.name:^30} ║")
        print(f"╠══════════════════════════════════════════╣")
        print(f"║  Total Entries:  {stats['total_entries']:>22} ║")
        print(f"║  Successes:      {stats['successes']:>22} ║")
        print(f"║  Deaths:         {stats['deaths']:>22} ║")
        print(f"║  Death Rate:     {stats['death_rate']:>21.1%} ║")
        print(f"╚══════════════════════════════════════════╝\n")

    def print_recent(self, n: int = 5) -> None:
        """Print recent entries."""
        print(f"\n─── Recent Entries ({n}) ───")
        for entry in self.get_recent(n):
            print(f"  {entry}")
        print()

    def __repr__(self) -> str:
        return f"Ledger({self.name}, {len(self)} entries)"


# Global ledger instance
global_ledger = Ledger("global")


def get_ledger() -> Ledger:
    """Get the global ledger."""
    return global_ledger


def new_ledger(name: str) -> Ledger:
    """Create a new named ledger."""
    return Ledger(name)
