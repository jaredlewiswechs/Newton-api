"""
Ada Command Line Interface
===========================

Interactive CLI for Ada - the better ChatGPT.
"""

import argparse
import json
import os
import readline
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from .schema import (
    AdaConfig,
    AdaMode,
    CodeLanguage,
    ResponseFormat,
)


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"


def colorize(text: str, color: str, bold: bool = False) -> str:
    """Add color to text."""
    prefix = Colors.BOLD if bold else ""
    return f"{prefix}{color}{text}{Colors.RESET}"


class AdaCLI:
    """
    Interactive command-line interface for Ada.

    Features:
    - Chat mode
    - Research mode
    - Agent mode
    - Canvas mode
    - Code execution
    - Command history
    - Multi-line input

    Commands:
    - /help - Show help
    - /mode <mode> - Switch mode (instant, thinking, pro)
    - /research <query> - Deep research
    - /agent <task> - Execute task
    - /canvas <instruction> - Build document/code
    - /execute <code> - Run code
    - /memory - Memory operations
    - /tasks - Task scheduling
    - /clear - Clear screen
    - /exit - Exit Ada
    """

    BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     █████╗ ██████╗  █████╗                                   ║
║    ██╔══██╗██╔══██╗██╔══██╗                                  ║
║    ███████║██║  ██║███████║                                  ║
║    ██╔══██║██║  ██║██╔══██║                                  ║
║    ██║  ██║██████╔╝██║  ██║                                  ║
║    ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝                                  ║
║                                                               ║
║    The Better ChatGPT - Built on Newton Verification          ║
║    Type /help for commands                                    ║
╚═══════════════════════════════════════════════════════════════╝
"""

    def __init__(self, config: Optional[AdaConfig] = None):
        """Initialize the CLI."""
        from .engine import Ada

        self.config = config or AdaConfig()
        self.ada = Ada(self.config)

        self.running = True
        self.multiline_mode = False
        self.multiline_buffer: List[str] = []

        # Command history
        self.history_file = os.path.expanduser("~/.ada_history")
        self._load_history()

        # Current state
        self.current_mode = AdaMode.INSTANT
        self.show_verification = True

    def _load_history(self):
        """Load command history."""
        try:
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)
        except Exception:
            pass

    def _save_history(self):
        """Save command history."""
        try:
            readline.set_history_length(1000)
            readline.write_history_file(self.history_file)
        except Exception:
            pass

    def print_banner(self):
        """Print the Ada banner."""
        print(colorize(self.BANNER, Colors.CYAN, bold=True))

    def print_help(self):
        """Print help message."""
        help_text = """
Commands:
  /help              - Show this help message
  /mode <mode>       - Switch mode (instant, thinking, pro)
  /research <query>  - Perform deep research
  /agent <task>      - Execute a task autonomously
  /canvas <inst>     - Create/edit document or code
  /execute           - Enter code execution mode
  /memory            - Memory operations
  /tasks             - Task scheduling
  /verify [on|off]   - Toggle verification display
  /export <file>     - Export conversation
  /clear             - Clear screen
  /exit or /quit     - Exit Ada

Modes:
  instant   - Fast, everyday responses
  thinking  - Step-by-step reasoning
  pro       - Maximum capability

Tips:
  - Multi-line input: End message with \\ to continue
  - Code blocks: Use triple backticks ```
  - Verified responses show a ✓ mark
"""
        print(colorize(help_text, Colors.WHITE))

    def prompt(self) -> str:
        """Get the input prompt."""
        mode_colors = {
            AdaMode.INSTANT: Colors.GREEN,
            AdaMode.THINKING: Colors.YELLOW,
            AdaMode.PRO: Colors.MAGENTA,
        }
        color = mode_colors.get(self.current_mode, Colors.WHITE)
        mode_str = self.current_mode.value.upper()
        return f"{colorize(f'[{mode_str}]', color)} {colorize('You:', Colors.CYAN, bold=True)} "

    def format_response(self, response) -> str:
        """Format Ada's response for display."""
        output = []

        # Verification status
        if self.show_verification:
            if response.verified:
                status = colorize("✓ Verified", Colors.GREEN, bold=True)
            else:
                status = colorize("○ Unverified", Colors.YELLOW)
            output.append(f"\n{status} ({response.verification_status})")

        # Content
        output.append(f"\n{colorize('Ada:', Colors.MAGENTA, bold=True)}")
        output.append(response.content)

        # Processing time
        output.append(f"\n{colorize(f'[{response.processing_time_ms}ms]', Colors.DIM)}")

        return "\n".join(output)

    def handle_command(self, command: str) -> bool:
        """
        Handle a slash command.

        Returns:
            True if should continue, False if should exit
        """
        parts = command[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd in ("exit", "quit", "q"):
            print(colorize("\nGoodbye! 👋", Colors.CYAN))
            return False

        elif cmd == "help":
            self.print_help()

        elif cmd == "clear":
            os.system("clear" if os.name != "nt" else "cls")
            self.print_banner()

        elif cmd == "mode":
            self._handle_mode(args)

        elif cmd == "verify":
            self._handle_verify(args)

        elif cmd == "research":
            self._handle_research(args)

        elif cmd == "agent":
            self._handle_agent(args)

        elif cmd == "canvas":
            self._handle_canvas(args)

        elif cmd == "execute":
            self._handle_execute(args)

        elif cmd == "memory":
            self._handle_memory(args)

        elif cmd == "tasks":
            self._handle_tasks(args)

        elif cmd == "export":
            self._handle_export(args)

        elif cmd == "stats":
            stats = self.ada.get_stats()
            print(colorize("\nStatistics:", Colors.CYAN, bold=True))
            for key, value in stats.items():
                print(f"  {key}: {value}")

        else:
            print(colorize(f"Unknown command: /{cmd}", Colors.RED))
            print("Type /help for available commands")

        return True

    def _handle_mode(self, args: str):
        """Handle mode switching."""
        if not args:
            print(f"Current mode: {colorize(self.current_mode.value, Colors.CYAN)}")
            print("Available modes: instant, thinking, pro")
            return

        try:
            self.current_mode = AdaMode(args.lower())
            self.ada.set_mode(self.current_mode)
            print(colorize(f"Switched to {self.current_mode.value} mode", Colors.GREEN))
        except ValueError:
            print(colorize(f"Invalid mode: {args}", Colors.RED))
            print("Available modes: instant, thinking, pro")

    def _handle_verify(self, args: str):
        """Handle verification toggle."""
        if args.lower() == "on":
            self.show_verification = True
            print(colorize("Verification display: ON", Colors.GREEN))
        elif args.lower() == "off":
            self.show_verification = False
            print(colorize("Verification display: OFF", Colors.YELLOW))
        else:
            status = "ON" if self.show_verification else "OFF"
            print(f"Verification display: {status}")
            print("Usage: /verify [on|off]")

    def _handle_research(self, args: str):
        """Handle research command."""
        if not args:
            print(colorize("Usage: /research <query>", Colors.YELLOW))
            return

        print(colorize(f"\nResearching: {args}", Colors.CYAN))
        print(colorize("This may take a moment...", Colors.DIM))

        try:
            report = self.ada.research(args)
            print("\n" + "=" * 60)
            print(report.report)
            print("=" * 60)
            print(colorize(f"\nConfidence: {report.confidence_score:.0%}", Colors.CYAN))
        except Exception as e:
            print(colorize(f"Research error: {e}", Colors.RED))

    def _handle_agent(self, args: str):
        """Handle agent command."""
        if not args:
            print(colorize("Usage: /agent <task>", Colors.YELLOW))
            return

        print(colorize(f"\nExecuting task: {args}", Colors.CYAN))
        print(colorize("Agent is working...", Colors.DIM))

        try:
            result = self.ada.agent(args)
            print("\n" + "=" * 60)
            print(colorize(f"Status: {result.status.value}", Colors.GREEN if result.status.value == "completed" else Colors.YELLOW))
            print(colorize(f"Summary: {result.summary}", Colors.WHITE))

            if result.actions:
                print(colorize("\nActions taken:", Colors.CYAN))
                for action in result.actions:
                    status_color = Colors.GREEN if action.status.value == "completed" else Colors.RED
                    print(f"  • {action.description} [{colorize(action.status.value, status_color)}]")

            print("=" * 60)
        except Exception as e:
            print(colorize(f"Agent error: {e}", Colors.RED))

    def _handle_canvas(self, args: str):
        """Handle canvas command."""
        if not args:
            print(colorize("Usage: /canvas <instruction>", Colors.YELLOW))
            print("Example: /canvas Create a Python function to sort a list")
            return

        print(colorize(f"\nCreating canvas: {args}", Colors.CYAN))

        try:
            doc = self.ada.canvas(args)
            print("\n" + "=" * 60)
            print(colorize(f"Canvas: {doc.title}", Colors.MAGENTA, bold=True))
            print(colorize(f"Type: {doc.canvas_type.value}", Colors.DIM))
            print("-" * 60)
            print(doc.content)
            print("=" * 60)
            print(colorize(f"Canvas ID: {doc.id}", Colors.DIM))
        except Exception as e:
            print(colorize(f"Canvas error: {e}", Colors.RED))

    def _handle_execute(self, args: str):
        """Handle code execution."""
        if args:
            # Single line execution
            code = args
        else:
            # Multi-line code input
            print(colorize("Enter code (Ctrl+D or empty line to execute):", Colors.CYAN))
            lines = []
            try:
                while True:
                    line = input("... ")
                    if not line:
                        break
                    lines.append(line)
            except EOFError:
                pass
            code = "\n".join(lines)

        if not code.strip():
            print(colorize("No code to execute", Colors.YELLOW))
            return

        print(colorize("\nExecuting...", Colors.DIM))

        try:
            result = self.ada.execute(code)
            print("\n" + "-" * 40)
            if result.success:
                print(colorize("✓ Success", Colors.GREEN))
                if result.stdout:
                    print(colorize("Output:", Colors.CYAN))
                    print(result.stdout)
            else:
                print(colorize(f"✗ Error: {result.error}", Colors.RED))
                if result.error_line:
                    print(colorize(f"  at line {result.error_line}", Colors.DIM))
            print(colorize(f"[{result.execution_time_ms}ms]", Colors.DIM))
        except Exception as e:
            print(colorize(f"Execution error: {e}", Colors.RED))

    def _handle_memory(self, args: str):
        """Handle memory operations."""
        parts = args.split(maxsplit=1) if args else []
        subcmd = parts[0] if parts else "list"

        if subcmd == "list":
            results = self.ada.recall("")
            if results:
                print(colorize("\nMemory entries:", Colors.CYAN))
                for entry in results[:10]:
                    verified = colorize("✓", Colors.GREEN) if entry.verified else colorize("○", Colors.DIM)
                    print(f"  {verified} {entry.key}: {str(entry.value)[:50]}")
            else:
                print(colorize("Memory is empty", Colors.DIM))

        elif subcmd == "search":
            query = parts[1] if len(parts) > 1 else ""
            if not query:
                print(colorize("Usage: /memory search <query>", Colors.YELLOW))
                return
            results = self.ada.recall(query)
            print(colorize(f"\nSearch results for '{query}':", Colors.CYAN))
            for entry in results:
                print(f"  • {entry.key}: {entry.value}")

        elif subcmd == "add":
            # Parse key=value
            if len(parts) < 2 or "=" not in parts[1]:
                print(colorize("Usage: /memory add key=value", Colors.YELLOW))
                return
            key, value = parts[1].split("=", 1)
            self.ada.remember(key.strip(), value.strip())
            print(colorize(f"Added: {key}", Colors.GREEN))

        elif subcmd == "forget":
            key = parts[1] if len(parts) > 1 else ""
            if not key:
                print(colorize("Usage: /memory forget <key>", Colors.YELLOW))
                return
            if self.ada.forget(key):
                print(colorize(f"Forgot: {key}", Colors.GREEN))
            else:
                print(colorize(f"Not found: {key}", Colors.YELLOW))

        elif subcmd == "stats":
            stats = self.ada.engine.memory.stats()
            print(colorize("\nMemory statistics:", Colors.CYAN))
            for key, value in stats.items():
                print(f"  {key}: {value}")

        else:
            print(colorize("Memory commands: list, search, add, forget, stats", Colors.YELLOW))

    def _handle_tasks(self, args: str):
        """Handle task scheduling."""
        parts = args.split(maxsplit=1) if args else []
        subcmd = parts[0] if parts else "list"

        if subcmd == "list":
            tasks = self.ada.engine.scheduler.list_tasks()
            if tasks:
                print(colorize("\nScheduled tasks:", Colors.CYAN))
                for task in tasks:
                    status = colorize("●", Colors.GREEN) if task.enabled else colorize("○", Colors.DIM)
                    print(f"  {status} {task.name} ({task.frequency.value})")
                    print(f"    {colorize(task.description, Colors.DIM)}")
            else:
                print(colorize("No scheduled tasks", Colors.DIM))

        elif subcmd == "add":
            print(colorize("Creating new task...", Colors.CYAN))
            name = input("  Name: ")
            prompt = input("  Prompt: ")
            freq = input("  Frequency (daily/hourly/weekly): ") or "daily"

            task = self.ada.schedule(prompt, name, freq)
            print(colorize(f"Created task: {task.name}", Colors.GREEN))

        elif subcmd == "stats":
            stats = self.ada.engine.scheduler.stats()
            print(colorize("\nScheduler statistics:", Colors.CYAN))
            for key, value in stats.items():
                print(f"  {key}: {value}")

        else:
            print(colorize("Task commands: list, add, stats", Colors.YELLOW))

    def _handle_export(self, args: str):
        """Handle conversation export."""
        if not args:
            args = f"ada_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            self.ada.export_conversation(args)
            print(colorize(f"Exported to: {args}", Colors.GREEN))
        except Exception as e:
            print(colorize(f"Export error: {e}", Colors.RED))

    def chat(self, message: str):
        """Send a chat message."""
        response = self.ada.chat(message, mode=self.current_mode)
        print(self.format_response(response))

    def run(self):
        """Run the interactive CLI."""
        self.print_banner()

        while self.running:
            try:
                user_input = input(self.prompt()).strip()

                if not user_input:
                    continue

                # Handle multi-line input
                if user_input.endswith("\\"):
                    self.multiline_buffer.append(user_input[:-1])
                    continue

                if self.multiline_buffer:
                    self.multiline_buffer.append(user_input)
                    user_input = "\n".join(self.multiline_buffer)
                    self.multiline_buffer = []

                # Handle commands
                if user_input.startswith("/"):
                    self.running = self.handle_command(user_input)
                else:
                    self.chat(user_input)

            except KeyboardInterrupt:
                print(colorize("\n\nUse /exit to quit", Colors.YELLOW))

            except EOFError:
                print(colorize("\nGoodbye! 👋", Colors.CYAN))
                break

            except Exception as e:
                print(colorize(f"Error: {e}", Colors.RED))

        self._save_history()


def ada_cli():
    """Entry point for the Ada CLI."""
    parser = argparse.ArgumentParser(
        description="Ada - The Better ChatGPT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ada                     # Start interactive mode
  ada "What is 2+2?"      # Quick query
  ada --mode thinking     # Start in thinking mode
  ada --research "AI"     # Research mode

For more info: https://github.com/newton-api/ada
        """,
    )

    parser.add_argument(
        "message",
        nargs="?",
        help="Message to send (optional)",
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["instant", "thinking", "pro"],
        default="instant",
        help="Intelligence mode",
    )
    parser.add_argument(
        "-r", "--research",
        action="store_true",
        help="Research mode",
    )
    parser.add_argument(
        "-a", "--agent",
        action="store_true",
        help="Agent mode",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Disable verification",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="Start web server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)",
    )

    args = parser.parse_args()

    # Start web server
    if args.server:
        from .web import run_server, AdaWebConfig
        config = AdaWebConfig(port=args.port)
        print(f"Starting Ada server on port {args.port}...")
        run_server(web_config=config)
        return

    # Create config
    config = AdaConfig(
        default_mode=AdaMode(args.mode),
        verify_facts=not args.no_verify,
    )

    # Quick query mode
    if args.message:
        from .engine import Ada
        ada = Ada(config)

        if args.research:
            result = ada.research(args.message)
            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                print(result.report)
        elif args.agent:
            result = ada.agent(args.message)
            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                print(result.summary)
        else:
            response = ada.chat(args.message)
            if args.json:
                print(json.dumps(response.to_dict(), indent=2))
            else:
                print(response.content)
        return

    # Interactive mode
    cli = AdaCLI(config)
    cli.run()


if __name__ == "__main__":
    ada_cli()
