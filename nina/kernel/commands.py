"""
═══════════════════════════════════════════════════════════════════════════════
FOGHORN COMMANDS — Undo/Redo Command Bus
═══════════════════════════════════════════════════════════════════════════════

The Command pattern in Nina provides:
- Full undo/redo across all actions
- Serializable command history
- Batch operations
- Macro recording

Every user action that modifies state goes through the command bus.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Generic, TypeVar
from enum import Enum

from .objects import (
    FoghornObject, ObjectType, Receipt,
    get_object_store
)


T = TypeVar('T')


class CommandState(Enum):
    """Command execution state."""
    PENDING = "pending"
    EXECUTED = "executed"
    UNDONE = "undone"
    FAILED = "failed"


@dataclass
class Command(ABC):
    """
    Base class for all commands.
    
    Commands encapsulate actions that can be executed, undone, and redone.
    """
    
    # Identity
    id: str = field(default_factory=lambda: f"cmd_{int(time.time() * 1000)}")
    name: str = ""
    description: str = ""
    
    # State
    state: CommandState = CommandState.PENDING
    executed_at: Optional[int] = None
    
    # Result tracking
    before_snapshot: Dict[str, Any] = field(default_factory=dict)
    after_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    # Error handling
    error: Optional[str] = None
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command. Return True on success."""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """Undo the command. Return True on success."""
        pass
    
    def redo(self) -> bool:
        """Redo the command. Default implementation calls execute()."""
        return self.execute()
    
    def can_undo(self) -> bool:
        """Check if command can be undone."""
        return self.state == CommandState.EXECUTED
    
    def can_redo(self) -> bool:
        """Check if command can be redone."""
        return self.state == CommandState.UNDONE
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize command for history."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "state": self.state.value,
            "executed_at": self.executed_at,
            "error": self.error,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONCRETE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AddObjectCommand(Command):
    """Add an object to the store."""
    
    name: str = "Add Object"
    obj: Optional[FoghornObject] = None
    
    def execute(self) -> bool:
        if not self.obj:
            self.error = "No object to add"
            self.state = CommandState.FAILED
            return False
        
        try:
            store = get_object_store()
            self.before_snapshot = {"count": store.count()}
            
            store.add(self.obj)
            
            self.after_snapshot = {
                "count": store.count(),
                "hash": self.obj.hash,
            }
            
            self.state = CommandState.EXECUTED
            self.executed_at = int(time.time() * 1000)
            return True
            
        except Exception as e:
            self.error = str(e)
            self.state = CommandState.FAILED
            return False
    
    def undo(self) -> bool:
        if not self.obj:
            return False
        
        try:
            store = get_object_store()
            # Remove from store (add removal capability if needed)
            if self.obj.hash in store._objects:
                del store._objects[self.obj.hash]
                store._by_type[self.obj.object_type].remove(self.obj.hash)
            
            self.state = CommandState.UNDONE
            return True
            
        except Exception as e:
            self.error = str(e)
            return False


@dataclass
class UpdateObjectCommand(Command):
    """Update an existing object."""
    
    name: str = "Update Object"
    hash: str = ""
    updates: Dict[str, Any] = field(default_factory=dict)
    _old_values: Dict[str, Any] = field(default_factory=dict)
    
    def execute(self) -> bool:
        if not self.hash or not self.updates:
            self.error = "No hash or updates provided"
            self.state = CommandState.FAILED
            return False
        
        try:
            store = get_object_store()
            obj = store.get(self.hash)
            
            if not obj:
                self.error = f"Object not found: {self.hash}"
                self.state = CommandState.FAILED
                return False
            
            # Save old values
            for key in self.updates:
                if hasattr(obj, key):
                    self._old_values[key] = getattr(obj, key)
            
            self.before_snapshot = {"hash": obj.hash}
            
            # Apply updates
            for key, value in self.updates.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            
            # Rehash
            obj.rehash()
            
            self.after_snapshot = {"hash": obj.hash}
            self.state = CommandState.EXECUTED
            self.executed_at = int(time.time() * 1000)
            return True
            
        except Exception as e:
            self.error = str(e)
            self.state = CommandState.FAILED
            return False
    
    def undo(self) -> bool:
        if not self.hash or not self._old_values:
            return False
        
        try:
            store = get_object_store()
            obj = store.get(self.hash)
            
            if not obj:
                # Try to find by old hash
                for stored_obj in store._objects.values():
                    if any(getattr(stored_obj, k, None) == v for k, v in self._old_values.items()):
                        obj = stored_obj
                        break
            
            if not obj:
                self.error = "Object not found for undo"
                return False
            
            # Restore old values
            for key, value in self._old_values.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            
            obj.rehash()
            self.state = CommandState.UNDONE
            return True
            
        except Exception as e:
            self.error = str(e)
            return False


@dataclass
class DeleteObjectCommand(Command):
    """Delete an object from the store."""
    
    name: str = "Delete Object"
    hash: str = ""
    _deleted_obj: Optional[FoghornObject] = None
    
    def execute(self) -> bool:
        if not self.hash:
            self.error = "No hash provided"
            self.state = CommandState.FAILED
            return False
        
        try:
            store = get_object_store()
            obj = store.get(self.hash)
            
            if not obj:
                self.error = f"Object not found: {self.hash}"
                self.state = CommandState.FAILED
                return False
            
            # Save for undo
            self._deleted_obj = obj
            self.before_snapshot = obj.to_dict()
            
            # Delete
            del store._objects[self.hash]
            if self.hash in store._by_type[obj.object_type]:
                store._by_type[obj.object_type].remove(self.hash)
            
            self.state = CommandState.EXECUTED
            self.executed_at = int(time.time() * 1000)
            return True
            
        except Exception as e:
            self.error = str(e)
            self.state = CommandState.FAILED
            return False
    
    def undo(self) -> bool:
        if not self._deleted_obj:
            return False
        
        try:
            store = get_object_store()
            store.add(self._deleted_obj)
            
            self.state = CommandState.UNDONE
            return True
            
        except Exception as e:
            self.error = str(e)
            return False


@dataclass
class BatchCommand(Command):
    """Execute multiple commands as a batch."""
    
    name: str = "Batch"
    commands: List[Command] = field(default_factory=list)
    _executed_count: int = 0
    
    def execute(self) -> bool:
        self._executed_count = 0
        
        try:
            for cmd in self.commands:
                if cmd.execute():
                    self._executed_count += 1
                else:
                    # Rollback executed commands
                    for i in range(self._executed_count - 1, -1, -1):
                        self.commands[i].undo()
                    
                    self.error = f"Failed at command {self._executed_count}: {cmd.error}"
                    self.state = CommandState.FAILED
                    return False
            
            self.state = CommandState.EXECUTED
            self.executed_at = int(time.time() * 1000)
            return True
            
        except Exception as e:
            self.error = str(e)
            self.state = CommandState.FAILED
            return False
    
    def undo(self) -> bool:
        try:
            # Undo in reverse order
            for cmd in reversed(self.commands):
                if not cmd.undo():
                    self.error = f"Failed to undo: {cmd.error}"
                    return False
            
            self.state = CommandState.UNDONE
            return True
            
        except Exception as e:
            self.error = str(e)
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND BUS
# ═══════════════════════════════════════════════════════════════════════════════

class CommandBus:
    """
    Central command execution system with undo/redo.
    
    The CommandBus is the single point for all state mutations in Nina.
    """
    
    def __init__(self, max_history: int = 100):
        self._history: List[Command] = []
        self._redo_stack: List[Command] = []
        self._max_history = max_history
        self._listeners: List[Callable[[Command], None]] = []
        self._recording: bool = False
        self._recorded_commands: List[Command] = []
    
    def execute(self, cmd: Command) -> bool:
        """Execute a command and add to history."""
        success = cmd.execute()
        
        if success:
            self._history.append(cmd)
            self._redo_stack.clear()  # Clear redo stack on new command
            
            # Trim history if needed
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]
            
            # Recording
            if self._recording:
                self._recorded_commands.append(cmd)
            
            # Notify listeners
            for listener in self._listeners:
                listener(cmd)
        
        return success
    
    def undo(self) -> bool:
        """Undo the last command."""
        if not self._history:
            return False
        
        cmd = self._history.pop()
        
        if cmd.undo():
            self._redo_stack.append(cmd)
            return True
        else:
            # Failed to undo, put back
            self._history.append(cmd)
            return False
    
    def redo(self) -> bool:
        """Redo the last undone command."""
        if not self._redo_stack:
            return False
        
        cmd = self._redo_stack.pop()
        
        if cmd.redo():
            self._history.append(cmd)
            return True
        else:
            # Failed to redo, put back
            self._redo_stack.append(cmd)
            return False
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._history) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command history."""
        return [cmd.to_dict() for cmd in self._history[-limit:]]
    
    def clear_history(self):
        """Clear all history."""
        self._history.clear()
        self._redo_stack.clear()
    
    # Event handling
    def add_listener(self, listener: Callable[[Command], None]):
        """Add a command listener."""
        self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[Command], None]):
        """Remove a command listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    # Macro recording
    def start_recording(self):
        """Start recording commands for macro."""
        self._recording = True
        self._recorded_commands.clear()
    
    def stop_recording(self) -> List[Command]:
        """Stop recording and return recorded commands."""
        self._recording = False
        commands = self._recorded_commands.copy()
        self._recorded_commands.clear()
        return commands
    
    def create_macro(self, name: str) -> BatchCommand:
        """Create a batch command from recorded commands."""
        commands = self.stop_recording()
        return BatchCommand(
            name=name,
            description=f"Macro with {len(commands)} commands",
            commands=commands,
        )


# Global command bus
_command_bus: Optional[CommandBus] = None

def get_command_bus() -> CommandBus:
    """Get the global command bus."""
    global _command_bus
    if _command_bus is None:
        _command_bus = CommandBus()
    return _command_bus


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def execute(cmd: Command) -> bool:
    """Execute a command via the global bus."""
    return get_command_bus().execute(cmd)


def undo() -> bool:
    """Undo via the global bus."""
    return get_command_bus().undo()


def redo() -> bool:
    """Redo via the global bus."""
    return get_command_bus().redo()


def add_object(obj: FoghornObject) -> bool:
    """Add an object via command."""
    return execute(AddObjectCommand(obj=obj))


def update_object(hash: str, **updates) -> bool:
    """Update an object via command."""
    return execute(UpdateObjectCommand(hash=hash, updates=updates))


def delete_object(hash: str) -> bool:
    """Delete an object via command."""
    return execute(DeleteObjectCommand(hash=hash))
