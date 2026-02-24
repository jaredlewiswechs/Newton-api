"""
TinyTalk Kernel
The main execution pipeline: Source -> Lex -> Parse -> Execute -> Result

Provides the public API for running TinyTalk code.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time
import io
import contextlib

from .lexer import Lexer
from .parser import Parser
from .runtime import Runtime, ExecutionBounds, TinyTalkError
from .stdlib import set_output_buffer, clear_output_buffer


@dataclass
class RunResult:
    """Result of executing TinyTalk code."""
    success: bool
    value: Any = None
    output: str = ""
    error: str = ""
    elapsed_ms: float = 0.0
    op_count: int = 0


class TinyTalkKernel:
    """
    Main entry point for executing TinyTalk code.

    Usage:
        kernel = TinyTalkKernel()
        result = kernel.run('show("Hello, world!")')
        print(result.output)   # "Hello, world!\n"
        print(result.success)  # True
    """

    def __init__(
        self,
        bounds: Optional[ExecutionBounds] = None,
        capture_output: bool = True,
        source_dir: str = "",
    ):
        self.bounds = bounds or ExecutionBounds()
        self.capture_output = capture_output
        self.source_dir = source_dir

    def run(self, source: str) -> RunResult:
        """Execute TinyTalk source code and return a RunResult."""
        start = time.time()

        try:
            # 1. Lex
            tokens = Lexer(source).tokenize()

            # 2. Parse
            ast = Parser(tokens).parse()

            # 3. Execute
            runtime = Runtime(self.bounds, source_dir=self.source_dir)

            if self.capture_output:
                buf: list = []
                set_output_buffer(buf)
                try:
                    result = runtime.execute(ast)
                finally:
                    clear_output_buffer()
                output = "".join(buf)
            else:
                result = runtime.execute(ast)
                output = ""

            elapsed = (time.time() - start) * 1000

            return RunResult(
                success=True,
                value=result,
                output=output,
                elapsed_ms=round(elapsed, 2),
                op_count=runtime.op_count,
            )

        except SyntaxError as e:
            return RunResult(
                success=False,
                error=str(e),
                elapsed_ms=round((time.time() - start) * 1000, 2),
            )
        except TinyTalkError as e:
            return RunResult(
                success=False,
                error=str(e),
                elapsed_ms=round((time.time() - start) * 1000, 2),
            )
        except AssertionError as e:
            return RunResult(
                success=False,
                error=str(e),
                elapsed_ms=round((time.time() - start) * 1000, 2),
            )
        except Exception as e:
            return RunResult(
                success=False,
                error=f"Internal error: {e}",
                elapsed_ms=round((time.time() - start) * 1000, 2),
            )

    def eval(self, source: str) -> Any:
        """Execute and return the raw Python value, raising on error."""
        result = self.run(source)
        if not result.success:
            raise RuntimeError(result.error)
        return result.value.to_python() if result.value else None

    def repl(self):
        """Interactive REPL with persistent state.

        State persists across lines — variables, functions, and structs
        defined in one line are available in subsequent lines.

        Commands:
            exit / quit        Exit the REPL
            :save <file.tt>    Export session history as a .tt file
            :export <file>     Export last result as CSV or JSON
            :load <file>       Load and execute a .tt file or load a CSV/JSON
            :reset             Reset all state
            :vars              Show all defined variables
            :help              Show available commands
        """
        print("TinyTalk v2.0 - Two styles, one language.")
        print("Type ':help' for commands, 'exit' to quit.\n")

        # Persistent runtime that survives across inputs
        runtime = Runtime(self.bounds, source_dir=self.source_dir)
        session_history: list[str] = []
        last_result = None

        while True:
            try:
                line = input(">> ").strip()
                if not line:
                    continue
                if line in ("exit", "quit"):
                    break

                # REPL commands
                if line.startswith(":"):
                    self._repl_command(line, runtime, session_history, last_result)
                    continue

                # Multi-line input: if line ends with { or \, read continuation
                while line.endswith("\\") or (line.count("{") > line.count("}")):
                    try:
                        cont = input(".. ")
                        if line.endswith("\\"):
                            line = line[:-1] + "\n" + cont
                        else:
                            line = line + "\n" + cont
                    except EOFError:
                        break

                session_history.append(line)

                try:
                    tokens = Lexer(line).tokenize()
                    ast = Parser(tokens).parse()

                    buf: list = []
                    set_output_buffer(buf)
                    try:
                        result = runtime.execute(ast)
                    finally:
                        clear_output_buffer()

                    output = "".join(buf)
                    if output:
                        print(output, end="")
                    if result and result.data is not None:
                        if not output:
                            from .stdlib import format_value
                            print(format_value(result))

                    last_result = result

                except SyntaxError as e:
                    print(f"SyntaxError: {e}")
                except TinyTalkError as e:
                    print(f"Error: {e}")
                except AssertionError as e:
                    print(f"AssertionError: {e}")
                except Exception as e:
                    print(f"Internal error: {e}")

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                break

    def _repl_command(self, line: str, runtime, history: list, last_result):
        """Handle REPL meta-commands."""
        parts = line.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd == ":help":
            print("REPL Commands:")
            print("  :vars              Show all defined variables")
            print("  :save <file.tt>    Export session as a .tt file")
            print("  :export <file>     Export last result as CSV/JSON")
            print("  :load <file>       Load a .tt file or CSV/JSON data")
            print("  :reset             Clear all state")
            print("  :help              Show this help")
            return

        if cmd == ":vars":
            from .stdlib import format_value
            for name, val in runtime.global_scope.variables.items():
                if name in runtime.global_scope.constants:
                    continue  # skip builtins
                print(f"  {name} = {format_value(val)}")
            return

        if cmd == ":reset":
            runtime.global_scope = __import__(
                'newTinyTalk.runtime', fromlist=['Scope']
            ).Scope()
            runtime._register_builtins()
            runtime.structs.clear()
            runtime.enums.clear()
            runtime._imported_modules.clear()
            history.clear()
            print("State reset.")
            return

        if cmd == ":save":
            if not arg:
                print("Usage: :save <filename.tt>")
                return
            try:
                with open(arg, "w", encoding="utf-8") as f:
                    f.write("\n".join(history) + "\n")
                print(f"Session saved to {arg}")
            except OSError as e:
                print(f"Error saving: {e}")
            return

        if cmd == ":load":
            if not arg:
                print("Usage: :load <file>")
                return
            import os
            if not os.path.exists(arg):
                print(f"File not found: {arg}")
                return
            if arg.endswith(".tt"):
                try:
                    with open(arg, "r", encoding="utf-8") as f:
                        source = f.read()
                    tokens = Lexer(source).tokenize()
                    ast = Parser(tokens).parse()
                    old_dir = runtime._source_dir
                    runtime._source_dir = os.path.dirname(os.path.abspath(arg))
                    buf: list = []
                    set_output_buffer(buf)
                    try:
                        runtime.execute(ast)
                    finally:
                        clear_output_buffer()
                        runtime._source_dir = old_dir
                    output = "".join(buf)
                    if output:
                        print(output, end="")
                    print(f"Loaded {arg}")
                except Exception as e:
                    print(f"Error loading {arg}: {e}")
            elif arg.endswith(".csv"):
                try:
                    from .stdlib import builtin_read_csv
                    from .types import Value
                    data = builtin_read_csv([Value.string_val(arg)])
                    runtime.global_scope.define("data", data)
                    print(f"Loaded {arg} into variable 'data' ({len(data.data)} rows)")
                except Exception as e:
                    print(f"Error loading CSV: {e}")
            elif arg.endswith(".json"):
                try:
                    from .stdlib import builtin_read_json
                    from .types import Value
                    data = builtin_read_json([Value.string_val(arg)])
                    runtime.global_scope.define("data", data)
                    print(f"Loaded {arg} into variable 'data'")
                except Exception as e:
                    print(f"Error loading JSON: {e}")
            else:
                print(f"Unknown file type: {arg}. Supported: .tt, .csv, .json")
            return

        if cmd == ":export":
            if not arg:
                print("Usage: :export <filename.csv|.json>")
                return
            if last_result is None:
                print("No result to export.")
                return
            from .types import Value
            if arg.endswith(".csv"):
                try:
                    from .stdlib import builtin_write_csv
                    builtin_write_csv([last_result, Value.string_val(arg)])
                    print(f"Exported to {arg}")
                except Exception as e:
                    print(f"Error exporting CSV: {e}")
            elif arg.endswith(".json"):
                try:
                    from .stdlib import builtin_write_json
                    builtin_write_json([last_result, Value.string_val(arg)])
                    print(f"Exported to {arg}")
                except Exception as e:
                    print(f"Error exporting JSON: {e}")
            else:
                print("Supported formats: .csv, .json")
            return

        print(f"Unknown command: {cmd}. Type ':help' for available commands.")
