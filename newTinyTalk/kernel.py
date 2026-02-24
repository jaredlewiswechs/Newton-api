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
    ):
        self.bounds = bounds or ExecutionBounds()
        self.capture_output = capture_output

    def run(self, source: str) -> RunResult:
        """Execute TinyTalk source code and return a RunResult."""
        start = time.time()

        try:
            # 1. Lex
            tokens = Lexer(source).tokenize()

            # 2. Parse
            ast = Parser(tokens).parse()

            # 3. Execute
            runtime = Runtime(self.bounds)

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
        """Interactive REPL."""
        print("TinyTalk v2.0 - Two styles, one language.")
        print("Type 'exit' to quit.\n")
        while True:
            try:
                line = input(">> ").strip()
                if not line:
                    continue
                if line == "exit":
                    break
                result = self.run(line)
                if result.output:
                    print(result.output, end="")
                if result.success and result.value and result.value.data is not None:
                    if not result.output:
                        print(result.value)
                if not result.success:
                    print(f"Error: {result.error}")
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                break
