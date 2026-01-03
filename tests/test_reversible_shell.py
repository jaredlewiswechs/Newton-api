#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON REVERSIBLE SHELL - Test Suite
═══════════════════════════════════════════════════════════════════════════════

Tests for the human-centric reversible command language.
Every test validates that commands and their inverses form bijective pairs.

Run with: pytest tests/test_reversible_shell.py -v
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
import sys
import os

# Add parent directory to path for direct imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from shell module to avoid core/__init__.py cryptography deps
import importlib.util
shell_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "core", "shell.py"
)
spec = importlib.util.spec_from_file_location("core.shell", shell_path)
shell_module = importlib.util.module_from_spec(spec)
sys.modules["core.shell"] = shell_module
spec.loader.exec_module(shell_module)

ReversibleShell = shell_module.ReversibleShell
ShellContext = shell_module.ShellContext
CommandResult = shell_module.CommandResult
Outcome = shell_module.Outcome
TryCommand = shell_module.TryCommand
SplitCommand = shell_module.SplitCommand
JoinCommand = shell_module.JoinCommand
LockCommand = shell_module.LockCommand
TakeCommand = shell_module.TakeCommand
GiveCommand = shell_module.GiveCommand
OpenCommand = shell_module.OpenCommand
CloseCommand = shell_module.CloseCommand
RememberCommand = shell_module.RememberCommand
ForgetCommand = shell_module.ForgetCommand
SayCommand = shell_module.SayCommand
PeekCommand = shell_module.PeekCommand
new_shell = shell_module.new_shell


# =============================================================================
# PART 1: SHELL CREATION AND BASIC STATE
# =============================================================================

class TestShellCreation:
    """Test shell initialization and basic properties."""

    def test_create_empty_shell(self):
        """Shell can be created with empty state."""
        shell = ReversibleShell()
        assert shell.state == {}
        assert shell.branch == "main"
        assert shell.history_length == 0

    def test_create_shell_with_initial_state(self):
        """Shell can be created with initial state."""
        shell = ReversibleShell({"x": 10, "y": 20})
        assert shell.state == {"x": 10, "y": 20}

    def test_new_shell_convenience_function(self):
        """new_shell() creates a shell correctly."""
        shell = new_shell({"a": 1})
        assert shell.state == {"a": 1}


# =============================================================================
# PART 2: TRY / UNTRY - Speculative Execution
# =============================================================================

class TestTryUntry:
    """Test the try ↔ untry bijection."""

    def test_try_modifies_state(self):
        """try executes an action that modifies state."""
        shell = new_shell({"x": 0})

        result = shell.try_action(lambda s: {**s, "x": 10}, "set x to 10")

        assert result.result == CommandResult.SUCCESS
        assert shell.state["x"] == 10

    def test_untry_reverses_try(self):
        """untry (undo) reverses the effect of try."""
        shell = new_shell({"x": 0})

        shell.try_action(lambda s: {**s, "x": 10}, "set x to 10")
        assert shell.state["x"] == 10

        result = shell.undo()

        assert result.result == CommandResult.REVERSED
        assert shell.state["x"] == 0

    def test_multiple_try_untry_sequence(self):
        """Multiple try/untry operations maintain consistency."""
        shell = new_shell({"counter": 0})

        # Try 5 increments
        for i in range(1, 6):
            shell.try_action(lambda s: {**s, "counter": s["counter"] + 1}, f"inc {i}")

        assert shell.state["counter"] == 5
        assert shell.history_length == 5

        # Undo all
        for _ in range(5):
            shell.undo()

        assert shell.state["counter"] == 0
        assert shell.history_length == 0

    def test_try_with_exception_rolls_back(self):
        """try that raises exception doesn't modify state."""
        shell = new_shell({"x": 10})

        def bad_action(s):
            raise ValueError("intentional failure")

        result = shell.try_action(bad_action, "bad action")

        assert result.result == CommandResult.BLOCKED
        assert shell.state["x"] == 10
        assert shell.history_length == 0


# =============================================================================
# PART 3: SPLIT / JOIN - Branching
# =============================================================================

class TestSplitJoin:
    """Test the split ↔ join bijection."""

    def test_split_creates_branch(self):
        """split creates a new branch with current state."""
        shell = new_shell({"x": 10})

        result = shell.split("experiment")

        assert result.result == CommandResult.SUCCESS
        assert shell.branch == "experiment"
        assert "experiment" in shell.branches
        assert shell.state["x"] == 10

    def test_split_preserves_parent_state(self):
        """Modifications in branch don't affect parent until join."""
        shell = new_shell({"x": 10})
        shell.split("experiment")

        shell.take("y", 20)

        assert shell.state == {"x": 10, "y": 20}
        assert shell.context.branches["main"].state == {"x": 10}

    def test_unsplit_removes_branch(self):
        """undo of split removes the branch and returns to parent."""
        shell = new_shell({"x": 10})
        shell.split("experiment")
        shell.take("y", 20)

        # Undo take
        shell.undo()
        # Undo split
        result = shell.undo()

        assert result.result == CommandResult.REVERSED
        assert shell.branch == "main"
        assert "experiment" not in shell.branches

    def test_join_merges_branch(self):
        """join merges a branch into current."""
        shell = new_shell({"x": 10})
        shell.split("feature")
        shell.take("y", 20)

        # Switch back to main by undoing split (which also undoes take)
        shell.undo()  # untake
        shell.undo()  # unsplit

        # Create a new branch with different state
        shell.split("feature2")
        shell.take("z", 30)

        # Go back to main
        shell.undo()  # untake
        shell.undo()  # unsplit

        # Now join feature2 (recreate it first)
        shell.split("feature2")
        shell.take("z", 30)

        # Manual switch - this is testing the join mechanics
        shell.context.current_branch = "main"

        result = shell.join("feature2", strategy="theirs")

        assert result.result == CommandResult.SUCCESS
        assert shell.state["z"] == 30

    def test_split_duplicate_name_blocked(self):
        """Cannot split with existing branch name."""
        shell = new_shell()
        shell.split("feature")

        result = shell.split("feature")

        assert result.result == CommandResult.CONFLICT


# =============================================================================
# PART 4: LOCK / UNLOCK - Commit
# =============================================================================

class TestLockUnlock:
    """Test the lock ↔ unlock bijection."""

    def test_lock_marks_branch_as_locked(self):
        """lock commits the current state."""
        shell = new_shell({"x": 10})

        result = shell.lock("initial commit")

        assert result.result == CommandResult.SUCCESS
        assert shell.context.branches["main"].locked is True

    def test_unlock_removes_lock(self):
        """undo of lock removes the lock."""
        shell = new_shell({"x": 10})
        shell.lock("initial commit")

        result = shell.undo()

        assert result.result == CommandResult.REVERSED
        assert shell.context.branches["main"].locked is False

    def test_double_lock_blocked(self):
        """Cannot lock already locked branch."""
        shell = new_shell()
        shell.lock("first")

        result = shell.lock("second")

        assert result.result == CommandResult.BLOCKED


# =============================================================================
# PART 5: TAKE / GIVE - Resource Management
# =============================================================================

class TestTakeGive:
    """Test the take ↔ give bijection."""

    def test_take_adds_value(self):
        """take adds a value to state."""
        shell = new_shell()

        result = shell.take("x", 10)

        assert result.result == CommandResult.SUCCESS
        assert shell.state["x"] == 10

    def test_give_removes_value(self):
        """give removes a value from state."""
        shell = new_shell({"x": 10})

        result = shell.give("x")

        assert result.result == CommandResult.SUCCESS
        assert "x" not in shell.state

    def test_untake_removes_value(self):
        """undo of take removes the value."""
        shell = new_shell()
        shell.take("x", 10)

        result = shell.undo()

        assert result.result == CommandResult.REVERSED
        assert "x" not in shell.state

    def test_ungive_restores_value(self):
        """undo of give restores the value."""
        shell = new_shell({"x": 10})
        shell.give("x")

        result = shell.undo()

        assert result.result == CommandResult.REVERSED
        assert shell.state["x"] == 10

    def test_take_overwrites_existing(self):
        """take on existing key overwrites and can be undone."""
        shell = new_shell({"x": 10})
        shell.take("x", 20)

        assert shell.state["x"] == 20

        shell.undo()

        assert shell.state["x"] == 10

    def test_give_nonexistent_blocked(self):
        """Cannot give what you don't have."""
        shell = new_shell()

        result = shell.give("nonexistent")

        assert result.result == CommandResult.BLOCKED


# =============================================================================
# PART 6: OPEN / CLOSE - Scopes
# =============================================================================

class TestOpenClose:
    """Test the open ↔ close bijection."""

    def test_open_adds_scope(self):
        """open begins a new scope."""
        shell = new_shell()

        result = shell.open("transaction")

        assert result.result == CommandResult.SUCCESS
        assert "transaction" in shell.scopes

    def test_close_removes_scope(self):
        """close ends the current scope."""
        shell = new_shell()
        shell.open("transaction")

        result = shell.close()

        assert result.result == CommandResult.SUCCESS
        assert "transaction" not in shell.scopes

    def test_unopen_removes_scope(self):
        """undo of open removes the scope."""
        shell = new_shell()
        shell.open("transaction")

        result = shell.undo()

        assert result.result == CommandResult.REVERSED
        assert "transaction" not in shell.scopes

    def test_unclose_reopens_scope(self):
        """undo of close reopens the scope."""
        shell = new_shell()
        shell.open("transaction")
        shell.close()

        result = shell.undo()

        assert result.result == CommandResult.REVERSED
        assert "transaction" in shell.scopes

    def test_nested_scopes(self):
        """Scopes can be nested."""
        shell = new_shell()
        shell.open("outer")
        shell.open("inner")

        assert shell.scopes == ["outer", "inner"]

        shell.close()
        assert shell.scopes == ["outer"]

        shell.close()
        assert shell.scopes == []

    def test_close_empty_blocked(self):
        """Cannot close when no scopes open."""
        shell = new_shell()

        result = shell.close()

        assert result.result == CommandResult.BLOCKED


# =============================================================================
# PART 7: REMEMBER / FORGET - Memory
# =============================================================================

class TestRememberForget:
    """Test the remember ↔ forget bijection."""

    def test_remember_stores_value(self):
        """remember stores a value in memory."""
        shell = new_shell()

        result = shell.remember("key", "value")

        assert result.result == CommandResult.SUCCESS
        assert shell.context.memory["key"].value == "value"

    def test_forget_removes_from_memory(self):
        """forget removes a value from memory."""
        shell = new_shell()
        shell.remember("key", "value")

        result = shell.forget("key")

        assert result.result == CommandResult.SUCCESS
        assert "key" not in shell.context.memory

    def test_unremember_removes_from_memory(self):
        """undo of remember removes from memory."""
        shell = new_shell()
        shell.remember("key", "value")

        result = shell.undo()

        assert result.result == CommandResult.REVERSED
        assert "key" not in shell.context.memory

    def test_unforget_restores_memory(self):
        """undo of forget restores to memory."""
        shell = new_shell()
        shell.remember("key", "value")
        shell.forget("key")

        result = shell.undo()

        assert result.result == CommandResult.REVERSED
        assert shell.context.memory["key"].value == "value"

    def test_forget_nonexistent_blocked(self):
        """Cannot forget what you don't remember."""
        shell = new_shell()

        result = shell.forget("nonexistent")

        assert result.result == CommandResult.BLOCKED


# =============================================================================
# PART 8: SAY / UNSAY - Signals
# =============================================================================

class TestSayUnsay:
    """Test the say ↔ unsay bijection."""

    def test_say_emits_signal(self):
        """say emits a signal."""
        shell = new_shell()

        result = shell.say("hello world")

        assert result.result == CommandResult.SUCCESS
        assert len(shell.context.signals) == 1
        assert shell.context.signals[0].content == "hello world"
        assert shell.context.signals[0].retracted is False

    def test_unsay_retracts_signal(self):
        """undo of say retracts the signal."""
        shell = new_shell()
        shell.say("hello world")

        result = shell.undo()

        assert result.result == CommandResult.REVERSED
        assert shell.context.signals[0].retracted is True


# =============================================================================
# PART 9: PEEK - Observation
# =============================================================================

class TestPeek:
    """Test peek (observation without mutation)."""

    def test_peek_entire_state(self):
        """peek returns entire state."""
        shell = new_shell({"x": 10, "y": 20})

        result = shell.peek()

        assert result.result == CommandResult.SUCCESS
        assert result.data == {"x": 10, "y": 20}

    def test_peek_specific_key(self):
        """peek can target specific key."""
        shell = new_shell({"x": 10, "y": 20})

        result = shell.peek("x")

        assert result.result == CommandResult.SUCCESS
        assert result.data == {"x": 10}

    def test_peek_does_not_modify_history(self):
        """peek does not add to history (not reversible)."""
        shell = new_shell({"x": 10})
        initial_history = shell.history_length

        shell.peek()
        shell.peek("x")

        assert shell.history_length == initial_history


# =============================================================================
# PART 10: GLOBAL UNDO / UNDO_ALL
# =============================================================================

class TestGlobalUndo:
    """Test global undo operations."""

    def test_undo_empty_blocked(self):
        """undo with no history is blocked."""
        shell = new_shell()

        result = shell.undo()

        assert result.result == CommandResult.BLOCKED

    def test_undo_all_reverses_everything(self):
        """undo_all reverses all commands."""
        shell = new_shell({"x": 0})

        shell.take("a", 1)
        shell.take("b", 2)
        shell.take("c", 3)

        assert shell.state == {"x": 0, "a": 1, "b": 2, "c": 3}

        outcomes = shell.undo_all()

        assert len(outcomes) == 3
        assert shell.state == {"x": 0}
        assert shell.history_length == 0


# =============================================================================
# PART 11: COMPLEX SCENARIOS
# =============================================================================

class TestComplexScenarios:
    """Test complex multi-command scenarios."""

    def test_branch_modify_undo_sequence(self):
        """Complex sequence: branch, modify, undo back to start."""
        shell = new_shell({"base": 100})

        # Start a transaction
        shell.open("transaction")
        shell.take("x", 10)
        shell.split("experiment")
        shell.take("y", 20)
        shell.remember("checkpoint", shell.state)

        assert shell.state == {"base": 100, "x": 10, "y": 20}

        # Undo everything
        shell.undo_all()

        assert shell.state == {"base": 100}
        assert shell.branch == "main"
        assert shell.scopes == []

    def test_interleaved_commands_bijective(self):
        """Interleaved commands maintain bijectivity."""
        shell = new_shell()

        commands_executed = []

        # Execute a series of interleaved commands
        shell.take("a", 1)
        commands_executed.append("take a")

        shell.open("scope1")
        commands_executed.append("open scope1")

        shell.take("b", 2)
        commands_executed.append("take b")

        shell.remember("mem", "value")
        commands_executed.append("remember mem")

        shell.say("message")
        commands_executed.append("say message")

        assert shell.history_length == 5

        # Undo in reverse order
        for _ in commands_executed:
            shell.undo()

        assert shell.state == {}
        assert shell.scopes == []
        assert len(shell.context.memory) == 0
        assert shell.history_length == 0

    def test_state_isolation_between_branches(self):
        """Branches maintain isolated state."""
        shell = new_shell({"shared": 100})

        shell.split("branch_a")
        shell.take("a_only", 1)

        # Switch back to main manually
        shell.undo()  # untake
        shell.undo()  # unsplit

        shell.split("branch_b")
        shell.take("b_only", 2)

        assert shell.state == {"shared": 100, "b_only": 2}
        assert "a_only" not in shell.state


# =============================================================================
# PART 12: REVERSIBILITY PROPERTIES (Mathematical)
# =============================================================================

class TestReversibilityProperties:
    """Test that reversibility properties hold mathematically."""

    def test_every_command_has_inverse(self):
        """Every ReversibleCommand has name and inverse_name."""
        commands = [
            TryCommand(action=lambda s: s, description="test"),
            SplitCommand(branch_name="test"),
            JoinCommand(branch_name="test"),
            LockCommand(message="test"),
            TakeCommand(key="k", value="v"),
            GiveCommand(key="k"),
            OpenCommand(scope_name="test"),
            CloseCommand(),
            RememberCommand(key="k", value="v"),
            ForgetCommand(key="k"),
            SayCommand(content="test"),
        ]

        for cmd in commands:
            assert hasattr(cmd, 'name')
            assert hasattr(cmd, 'inverse_name')
            assert cmd.name != cmd.inverse_name

    def test_execute_reverse_is_identity(self):
        """For any command c: reverse(execute(c)) = identity."""
        shell = new_shell({"x": 10})
        original_state = shell.context.snapshot()

        # Execute then reverse
        shell.take("y", 20)
        shell.undo()

        assert shell.state == original_state

    def test_double_reverse_blocked(self):
        """Cannot reverse a command that wasn't executed."""
        shell = new_shell()
        shell.take("x", 10)
        shell.undo()

        # Second undo should be blocked (nothing to undo)
        result = shell.undo()

        assert result.result == CommandResult.BLOCKED

    def test_history_is_lifo(self):
        """Command history is strictly LIFO."""
        shell = new_shell()

        shell.take("a", 1)
        shell.take("b", 2)
        shell.take("c", 3)

        # Undo c first
        shell.undo()
        assert "c" not in shell.state

        # Then b
        shell.undo()
        assert "b" not in shell.state

        # Then a
        shell.undo()
        assert "a" not in shell.state


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" NEWTON REVERSIBLE SHELL - Test Suite")
    print("=" * 60)
    pytest.main([__file__, "-v", "--tb=short"])
