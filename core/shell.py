#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON REVERSIBLE SHELL - Human-Centric Command Language
═══════════════════════════════════════════════════════════════════════════════

A command language where every action maps bijectively to its inverse.
The reversibility of the underlying system is FELT through the grammar.

Design Principle:
    Users don't need to learn that Newton is reversible.
    They feel it because `try` has `untry`, `split` has `join`.
    The bijection is in the language itself.

Command Pairs:
    try     ↔  untry      Speculative execution
    split   ↔  join       Branch / merge
    lock    ↔  unlock     Commit / uncommit
    take    ↔  give       Acquire / release
    open    ↔  close      Begin / end scope
    remember ↔ forget     Persist / clear
    say     ↔  unsay      Emit / retract

Observation (no inverse needed):
    peek                  View diff/state without mutation

═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic
from enum import Enum
import copy
import time
import hashlib


# ═══════════════════════════════════════════════════════════════════════════════
# CORE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class CommandResult(Enum):
    """Outcome of a command execution."""
    SUCCESS = "success"
    BLOCKED = "blocked"      # Law prevented execution
    REVERSED = "reversed"    # Command was undone
    CONFLICT = "conflict"    # Incompatible state


@dataclass
class Outcome:
    """The result of executing a command."""
    result: CommandResult
    message: str
    data: Any = None
    timestamp: float = field(default_factory=time.time)
    fingerprint: str = ""

    def __post_init__(self):
        if not self.fingerprint:
            content = f"{self.result.value}:{self.message}:{self.timestamp}"
            self.fingerprint = hashlib.sha256(content.encode()).hexdigest()[:12]


# ═══════════════════════════════════════════════════════════════════════════════
# REVERSIBLE COMMAND - The Bijective Primitive
# ═══════════════════════════════════════════════════════════════════════════════

class ReversibleCommand(ABC):
    """
    A command that knows its inverse.

    Every command in Newton's shell is reversible by construction.
    The inverse is not an afterthought—it's part of the definition.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The human-readable action verb."""
        pass

    @property
    @abstractmethod
    def inverse_name(self) -> str:
        """The inverse action verb."""
        pass

    @abstractmethod
    def execute(self, context: 'ShellContext') -> Outcome:
        """Execute the forward action."""
        pass

    @abstractmethod
    def reverse(self, context: 'ShellContext') -> Outcome:
        """Execute the inverse action (undo)."""
        pass

    def __repr__(self) -> str:
        return f"{self.name} ↔ {self.inverse_name}"


# ═══════════════════════════════════════════════════════════════════════════════
# SHELL CONTEXT - The Reversible State Container
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Branch:
    """A speculative execution branch."""
    name: str
    state: Dict[str, Any]
    parent: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    locked: bool = False


@dataclass
class Memory:
    """A remembered value."""
    key: str
    value: Any
    remembered_at: float = field(default_factory=time.time)


@dataclass
class Signal:
    """A said (emitted) message."""
    content: str
    said_at: float = field(default_factory=time.time)
    retracted: bool = False


class ShellContext:
    """
    The execution context for the reversible shell.

    Maintains:
    - Named branches for speculative execution
    - A command history stack for full reversibility
    - Memory for persistent values
    - Signals for communication
    """

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        self.branches: Dict[str, Branch] = {
            "main": Branch(name="main", state=initial_state or {})
        }
        self.current_branch: str = "main"
        self.history: List[ReversibleCommand] = []
        self.memory: Dict[str, Memory] = {}
        self.signals: List[Signal] = []
        self.scopes: List[str] = []  # Stack of open scopes

    @property
    def state(self) -> Dict[str, Any]:
        """Current branch's state."""
        return self.branches[self.current_branch].state

    @state.setter
    def state(self, value: Dict[str, Any]):
        self.branches[self.current_branch].state = value

    def snapshot(self) -> Dict[str, Any]:
        """Deep copy of current state for rollback."""
        return copy.deepcopy(self.state)


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND IMPLEMENTATIONS - The Bijective Pairs
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# TRY / UNTRY - Speculative Execution
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TryCommand(ReversibleCommand):
    """
    try: Execute speculatively, can be undone.

    Human meaning: "Let me try this way"
    """
    action: Callable[[Dict[str, Any]], Dict[str, Any]]
    description: str = ""
    _saved_state: Optional[Dict[str, Any]] = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return "try"

    @property
    def inverse_name(self) -> str:
        return "untry"

    def execute(self, context: ShellContext) -> Outcome:
        # Save state before trying
        self._saved_state = context.snapshot()

        try:
            # Apply the action
            new_state = self.action(context.state)
            context.state = new_state
            context.history.append(self)

            return Outcome(
                result=CommandResult.SUCCESS,
                message=f"tried: {self.description or 'action'}",
                data=new_state
            )
        except Exception as e:
            # Rollback on failure
            context.state = self._saved_state
            return Outcome(
                result=CommandResult.BLOCKED,
                message=f"try blocked: {str(e)}"
            )

    def reverse(self, context: ShellContext) -> Outcome:
        if self._saved_state is None:
            return Outcome(
                result=CommandResult.BLOCKED,
                message="nothing to untry"
            )

        context.state = self._saved_state
        self._saved_state = None

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"untried: {self.description or 'action'}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SPLIT / JOIN - Branch and Merge
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SplitCommand(ReversibleCommand):
    """
    split: Create a new branch for exploration.

    Human meaning: "Let me explore this path"
    """
    branch_name: str
    _parent_branch: Optional[str] = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return "split"

    @property
    def inverse_name(self) -> str:
        return "join"

    def execute(self, context: ShellContext) -> Outcome:
        if self.branch_name in context.branches:
            return Outcome(
                result=CommandResult.CONFLICT,
                message=f"branch '{self.branch_name}' already exists"
            )

        self._parent_branch = context.current_branch

        # Create new branch with copy of current state
        context.branches[self.branch_name] = Branch(
            name=self.branch_name,
            state=context.snapshot(),
            parent=context.current_branch
        )
        context.current_branch = self.branch_name
        context.history.append(self)

        return Outcome(
            result=CommandResult.SUCCESS,
            message=f"split into '{self.branch_name}'",
            data={"branch": self.branch_name, "parent": self._parent_branch}
        )

    def reverse(self, context: ShellContext) -> Outcome:
        if self._parent_branch is None:
            return Outcome(
                result=CommandResult.BLOCKED,
                message="cannot join: no parent branch"
            )

        # Switch back to parent and remove the branch
        context.current_branch = self._parent_branch
        del context.branches[self.branch_name]

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"joined back from '{self.branch_name}'"
        )


@dataclass
class JoinCommand(ReversibleCommand):
    """
    join: Merge a branch back.

    Human meaning: "Bring these together"
    """
    branch_name: str
    merge_strategy: str = "theirs"  # "theirs", "ours", "combine"
    _pre_merge_state: Optional[Dict[str, Any]] = field(default=None, repr=False)
    _merged_branch_state: Optional[Dict[str, Any]] = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return "join"

    @property
    def inverse_name(self) -> str:
        return "split"

    def execute(self, context: ShellContext) -> Outcome:
        if self.branch_name not in context.branches:
            return Outcome(
                result=CommandResult.BLOCKED,
                message=f"branch '{self.branch_name}' does not exist"
            )

        if self.branch_name == context.current_branch:
            return Outcome(
                result=CommandResult.BLOCKED,
                message="cannot join branch into itself"
            )

        self._pre_merge_state = context.snapshot()
        self._merged_branch_state = copy.deepcopy(
            context.branches[self.branch_name].state
        )

        # Merge based on strategy
        if self.merge_strategy == "theirs":
            context.state = self._merged_branch_state
        elif self.merge_strategy == "ours":
            pass  # Keep current state
        elif self.merge_strategy == "combine":
            # Shallow merge - theirs wins on conflict
            context.state.update(self._merged_branch_state)

        # Remove merged branch
        del context.branches[self.branch_name]
        context.history.append(self)

        return Outcome(
            result=CommandResult.SUCCESS,
            message=f"joined '{self.branch_name}' with strategy '{self.merge_strategy}'",
            data=context.state
        )

    def reverse(self, context: ShellContext) -> Outcome:
        if self._pre_merge_state is None or self._merged_branch_state is None:
            return Outcome(
                result=CommandResult.BLOCKED,
                message="cannot reverse join: no saved state"
            )

        # Restore current branch state
        context.state = self._pre_merge_state

        # Recreate the merged branch
        context.branches[self.branch_name] = Branch(
            name=self.branch_name,
            state=self._merged_branch_state,
            parent=context.current_branch
        )

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"split '{self.branch_name}' back out"
        )


# ─────────────────────────────────────────────────────────────────────────────
# LOCK / UNLOCK - Commit and Uncommit
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LockCommand(ReversibleCommand):
    """
    lock: Commit to current state.

    Human meaning: "I'm sure about this"
    """
    message: str
    _pre_lock_history_length: int = field(default=0, repr=False)

    @property
    def name(self) -> str:
        return "lock"

    @property
    def inverse_name(self) -> str:
        return "unlock"

    def execute(self, context: ShellContext) -> Outcome:
        branch = context.branches[context.current_branch]

        if branch.locked:
            return Outcome(
                result=CommandResult.BLOCKED,
                message="branch already locked"
            )

        self._pre_lock_history_length = len(context.history)
        branch.locked = True
        context.history.append(self)

        # Create fingerprint of locked state
        state_str = str(sorted(context.state.items()))
        fingerprint = hashlib.sha256(state_str.encode()).hexdigest()[:8]

        return Outcome(
            result=CommandResult.SUCCESS,
            message=f"locked: {self.message}",
            data={"fingerprint": fingerprint, "branch": context.current_branch}
        )

    def reverse(self, context: ShellContext) -> Outcome:
        branch = context.branches[context.current_branch]

        if not branch.locked:
            return Outcome(
                result=CommandResult.BLOCKED,
                message="branch not locked"
            )

        branch.locked = False

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"unlocked: {self.message}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAKE / GIVE - Resource Acquisition and Release
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TakeCommand(ReversibleCommand):
    """
    take: Acquire a resource or value.

    Human meaning: "I need this"
    """
    key: str
    value: Any
    _previous_value: Any = field(default=None, repr=False)
    _existed: bool = field(default=False, repr=False)

    @property
    def name(self) -> str:
        return "take"

    @property
    def inverse_name(self) -> str:
        return "give"

    def execute(self, context: ShellContext) -> Outcome:
        self._existed = self.key in context.state
        self._previous_value = context.state.get(self.key)

        context.state[self.key] = self.value
        context.history.append(self)

        return Outcome(
            result=CommandResult.SUCCESS,
            message=f"took {self.key}",
            data={self.key: self.value}
        )

    def reverse(self, context: ShellContext) -> Outcome:
        if self._existed:
            context.state[self.key] = self._previous_value
        else:
            del context.state[self.key]

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"gave back {self.key}"
        )


@dataclass
class GiveCommand(ReversibleCommand):
    """
    give: Release a resource or value.

    Human meaning: "I don't need this anymore"
    """
    key: str
    _previous_value: Any = field(default=None, repr=False)
    _existed: bool = field(default=False, repr=False)

    @property
    def name(self) -> str:
        return "give"

    @property
    def inverse_name(self) -> str:
        return "take"

    def execute(self, context: ShellContext) -> Outcome:
        self._existed = self.key in context.state

        if not self._existed:
            return Outcome(
                result=CommandResult.BLOCKED,
                message=f"cannot give '{self.key}': not held"
            )

        self._previous_value = context.state.pop(self.key)
        context.history.append(self)

        return Outcome(
            result=CommandResult.SUCCESS,
            message=f"gave {self.key}",
            data={self.key: self._previous_value}
        )

    def reverse(self, context: ShellContext) -> Outcome:
        context.state[self.key] = self._previous_value

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"took back {self.key}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# OPEN / CLOSE - Scoped Execution
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class OpenCommand(ReversibleCommand):
    """
    open: Begin a new scope.

    Human meaning: "Let's start this section"
    """
    scope_name: str
    _state_at_open: Optional[Dict[str, Any]] = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return "open"

    @property
    def inverse_name(self) -> str:
        return "close"

    def execute(self, context: ShellContext) -> Outcome:
        self._state_at_open = context.snapshot()
        context.scopes.append(self.scope_name)
        context.history.append(self)

        return Outcome(
            result=CommandResult.SUCCESS,
            message=f"opened scope '{self.scope_name}'",
            data={"scope": self.scope_name, "depth": len(context.scopes)}
        )

    def reverse(self, context: ShellContext) -> Outcome:
        if not context.scopes or context.scopes[-1] != self.scope_name:
            return Outcome(
                result=CommandResult.BLOCKED,
                message=f"scope '{self.scope_name}' not at top of stack"
            )

        context.scopes.pop()
        # Optionally restore state at open for full reversibility
        if self._state_at_open is not None:
            context.state = self._state_at_open

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"closed scope '{self.scope_name}'"
        )


@dataclass
class CloseCommand(ReversibleCommand):
    """
    close: End the current scope.

    Human meaning: "We're done with this section"
    """
    _closed_scope: Optional[str] = field(default=None, repr=False)
    _state_at_close: Optional[Dict[str, Any]] = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return "close"

    @property
    def inverse_name(self) -> str:
        return "open"

    def execute(self, context: ShellContext) -> Outcome:
        if not context.scopes:
            return Outcome(
                result=CommandResult.BLOCKED,
                message="no scope to close"
            )

        self._closed_scope = context.scopes.pop()
        self._state_at_close = context.snapshot()
        context.history.append(self)

        return Outcome(
            result=CommandResult.SUCCESS,
            message=f"closed scope '{self._closed_scope}'",
            data={"scope": self._closed_scope}
        )

    def reverse(self, context: ShellContext) -> Outcome:
        if self._closed_scope is None:
            return Outcome(
                result=CommandResult.BLOCKED,
                message="no scope to reopen"
            )

        context.scopes.append(self._closed_scope)

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"reopened scope '{self._closed_scope}'"
        )


# ─────────────────────────────────────────────────────────────────────────────
# REMEMBER / FORGET - Persistent Memory
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RememberCommand(ReversibleCommand):
    """
    remember: Store a value in persistent memory.

    Human meaning: "Keep this for later"
    """
    key: str
    value: Any
    _previous_memory: Optional[Memory] = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return "remember"

    @property
    def inverse_name(self) -> str:
        return "forget"

    def execute(self, context: ShellContext) -> Outcome:
        self._previous_memory = context.memory.get(self.key)

        context.memory[self.key] = Memory(key=self.key, value=self.value)
        context.history.append(self)

        return Outcome(
            result=CommandResult.SUCCESS,
            message=f"remembered '{self.key}'",
            data={self.key: self.value}
        )

    def reverse(self, context: ShellContext) -> Outcome:
        if self._previous_memory:
            context.memory[self.key] = self._previous_memory
        else:
            del context.memory[self.key]

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"forgot '{self.key}'"
        )


@dataclass
class ForgetCommand(ReversibleCommand):
    """
    forget: Remove a value from memory.

    Human meaning: "I don't need to remember this"
    """
    key: str
    _forgotten_memory: Optional[Memory] = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return "forget"

    @property
    def inverse_name(self) -> str:
        return "remember"

    def execute(self, context: ShellContext) -> Outcome:
        if self.key not in context.memory:
            return Outcome(
                result=CommandResult.BLOCKED,
                message=f"cannot forget '{self.key}': not remembered"
            )

        self._forgotten_memory = context.memory.pop(self.key)
        context.history.append(self)

        return Outcome(
            result=CommandResult.SUCCESS,
            message=f"forgot '{self.key}'"
        )

    def reverse(self, context: ShellContext) -> Outcome:
        if self._forgotten_memory is None:
            return Outcome(
                result=CommandResult.BLOCKED,
                message="nothing to remember back"
            )

        context.memory[self.key] = self._forgotten_memory

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"remembered '{self.key}' again"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SAY / UNSAY - Signal Emission and Retraction
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SayCommand(ReversibleCommand):
    """
    say: Emit a signal/message.

    Human meaning: "I'm saying this"
    """
    content: str
    _signal_index: int = field(default=-1, repr=False)

    @property
    def name(self) -> str:
        return "say"

    @property
    def inverse_name(self) -> str:
        return "unsay"

    def execute(self, context: ShellContext) -> Outcome:
        signal = Signal(content=self.content)
        context.signals.append(signal)
        self._signal_index = len(context.signals) - 1
        context.history.append(self)

        return Outcome(
            result=CommandResult.SUCCESS,
            message=f"said: {self.content}",
            data={"signal": self.content, "index": self._signal_index}
        )

    def reverse(self, context: ShellContext) -> Outcome:
        if self._signal_index < 0 or self._signal_index >= len(context.signals):
            return Outcome(
                result=CommandResult.BLOCKED,
                message="signal not found"
            )

        context.signals[self._signal_index].retracted = True

        return Outcome(
            result=CommandResult.REVERSED,
            message=f"unsaid: {self.content}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# PEEK - Observation (No inverse needed, doesn't mutate)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PeekCommand:
    """
    peek: Observe state without mutation.

    Human meaning: "Let me see"

    Note: Not a ReversibleCommand because it doesn't mutate state.
    """
    target: Optional[str] = None  # None = entire state

    def execute(self, context: ShellContext) -> Outcome:
        if self.target:
            value = context.state.get(self.target)
            return Outcome(
                result=CommandResult.SUCCESS,
                message=f"peeked at '{self.target}'",
                data={self.target: value}
            )
        else:
            return Outcome(
                result=CommandResult.SUCCESS,
                message="peeked at state",
                data=context.state
            )


# ═══════════════════════════════════════════════════════════════════════════════
# THE REVERSIBLE SHELL - Main Interface
# ═══════════════════════════════════════════════════════════════════════════════

class ReversibleShell:
    """
    Newton's human-centric reversible shell.

    Every action has an inverse. The bijection is in the grammar.

    Usage:
        shell = ReversibleShell()

        shell.try_action(lambda s: {**s, "x": 10}, "set x to 10")
        shell.split("experiment")
        shell.take("y", 20)
        shell.undo()  # untake
        shell.undo()  # unsplit

        shell.peek()  # View current state
    """

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        self.context = ShellContext(initial_state or {})

    # ─────────────────────────────────────────────────────────────────────
    # COMMAND METHODS - The Human Interface
    # ─────────────────────────────────────────────────────────────────────

    def try_action(
        self,
        action: Callable[[Dict[str, Any]], Dict[str, Any]],
        description: str = ""
    ) -> Outcome:
        """try: Execute speculatively."""
        cmd = TryCommand(action=action, description=description)
        return cmd.execute(self.context)

    def split(self, branch_name: str) -> Outcome:
        """split: Create a new branch."""
        cmd = SplitCommand(branch_name=branch_name)
        return cmd.execute(self.context)

    def join(self, branch_name: str, strategy: str = "theirs") -> Outcome:
        """join: Merge a branch."""
        cmd = JoinCommand(branch_name=branch_name, merge_strategy=strategy)
        return cmd.execute(self.context)

    def lock(self, message: str) -> Outcome:
        """lock: Commit current state."""
        cmd = LockCommand(message=message)
        return cmd.execute(self.context)

    def take(self, key: str, value: Any) -> Outcome:
        """take: Acquire a value."""
        cmd = TakeCommand(key=key, value=value)
        return cmd.execute(self.context)

    def give(self, key: str) -> Outcome:
        """give: Release a value."""
        cmd = GiveCommand(key=key)
        return cmd.execute(self.context)

    def open(self, scope_name: str) -> Outcome:
        """open: Begin a scope."""
        cmd = OpenCommand(scope_name=scope_name)
        return cmd.execute(self.context)

    def close(self) -> Outcome:
        """close: End current scope."""
        cmd = CloseCommand()
        return cmd.execute(self.context)

    def remember(self, key: str, value: Any) -> Outcome:
        """remember: Store in memory."""
        cmd = RememberCommand(key=key, value=value)
        return cmd.execute(self.context)

    def forget(self, key: str) -> Outcome:
        """forget: Remove from memory."""
        cmd = ForgetCommand(key=key)
        return cmd.execute(self.context)

    def say(self, content: str) -> Outcome:
        """say: Emit a signal."""
        cmd = SayCommand(content=content)
        return cmd.execute(self.context)

    def peek(self, target: Optional[str] = None) -> Outcome:
        """peek: Observe without mutation."""
        cmd = PeekCommand(target=target)
        return cmd.execute(self.context)

    # ─────────────────────────────────────────────────────────────────────
    # UNDO / REDO - Global Reversibility
    # ─────────────────────────────────────────────────────────────────────

    def undo(self) -> Outcome:
        """Undo the last command (execute its inverse)."""
        if not self.context.history:
            return Outcome(
                result=CommandResult.BLOCKED,
                message="nothing to undo"
            )

        last_command = self.context.history.pop()
        return last_command.reverse(self.context)

    def undo_all(self) -> List[Outcome]:
        """Undo all commands in reverse order."""
        outcomes = []
        while self.context.history:
            outcomes.append(self.undo())
        return outcomes

    # ─────────────────────────────────────────────────────────────────────
    # INSPECTION
    # ─────────────────────────────────────────────────────────────────────

    @property
    def state(self) -> Dict[str, Any]:
        """Current state."""
        return self.context.state

    @property
    def branch(self) -> str:
        """Current branch name."""
        return self.context.current_branch

    @property
    def branches(self) -> List[str]:
        """All branch names."""
        return list(self.context.branches.keys())

    @property
    def history_length(self) -> int:
        """Number of undoable commands."""
        return len(self.context.history)

    @property
    def scopes(self) -> List[str]:
        """Currently open scopes."""
        return self.context.scopes.copy()

    def __repr__(self) -> str:
        return (
            f"ReversibleShell("
            f"branch='{self.branch}', "
            f"state={self.state}, "
            f"history={self.history_length})"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS - Functional Interface
# ═══════════════════════════════════════════════════════════════════════════════

def new_shell(initial_state: Optional[Dict[str, Any]] = None) -> ReversibleShell:
    """Create a new reversible shell."""
    return ReversibleShell(initial_state)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print(" NEWTON REVERSIBLE SHELL - Demo")
    print("=" * 60)

    shell = ReversibleShell()

    print("\n1. take x = 10")
    print(f"   {shell.take('x', 10)}")

    print("\n2. split 'experiment'")
    print(f"   {shell.split('experiment')}")

    print("\n3. take y = 20 (in experiment branch)")
    print(f"   {shell.take('y', 20)}")

    print("\n4. peek (observe state)")
    print(f"   {shell.peek()}")

    print("\n5. undo (untake y)")
    print(f"   {shell.undo()}")

    print("\n6. undo (unsplit - join back to main)")
    print(f"   {shell.undo()}")

    print("\n7. peek (back to main, only x)")
    print(f"   {shell.peek()}")

    print("\n8. Final state:")
    print(f"   branch: {shell.branch}")
    print(f"   state: {shell.state}")
    print(f"   history length: {shell.history_length}")

    print("\n" + "=" * 60)
