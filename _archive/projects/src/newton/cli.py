#!/usr/bin/env python3
"""
Newton CLI - Command line interface for Newton Supercomputer.

Usage:
    newton serve              # Start the server
    newton calc "2 + 3"       # Quick calculation
    newton verify "text"      # Verify content
    newton health             # Check server health
    newton demo               # Run tinyTalk demo
"""

import argparse
import sys
import json


def main():
    parser = argparse.ArgumentParser(
        prog="newton",
        description="Newton Supercomputer - Verified Computation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  newton serve                    Start the server
  newton serve --port 9000        Start on custom port
  newton calc "2 + 3"             Calculate expression
  newton verify "hello world"     Verify content safety
  newton health                   Check server status
  newton demo                     Run tinyTalk demo
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start Newton server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port")
    serve_parser.add_argument("--reload", action="store_true", help="Auto-reload")

    # calc command
    calc_parser = subparsers.add_parser("calc", help="Calculate expression")
    calc_parser.add_argument("expression", help="Math expression (e.g., '2 + 3')")
    calc_parser.add_argument("--url", default="http://localhost:8000", help="Server URL")

    # verify command
    verify_parser = subparsers.add_parser("verify", help="Verify content")
    verify_parser.add_argument("content", help="Content to verify")
    verify_parser.add_argument("--url", default="http://localhost:8000", help="Server URL")

    # health command
    health_parser = subparsers.add_parser("health", help="Check server health")
    health_parser.add_argument("--url", default="http://localhost:8000", help="Server URL")

    # demo command
    subparsers.add_parser("demo", help="Run tinyTalk demo")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize new Newton project")
    init_parser.add_argument("name", nargs="?", default="newton_project", help="Project name")

    # version
    parser.add_argument("--version", action="version", version="newton-computer 1.0.0")

    args = parser.parse_args()

    if args.command == "serve":
        from .server import serve
        serve(host=args.host, port=args.port, reload=args.reload)

    elif args.command == "calc":
        from .client import Newton, NewtonError
        try:
            newton = Newton(args.url)
            expr = parse_expression(args.expression)
            result = newton.calculate(expr)
            print(f"{result.result}")
        except NewtonError as e:
            print(f"Error: {e.message}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "verify":
        from .client import Newton, NewtonError
        try:
            newton = Newton(args.url)
            result = newton.verify(args.content)
            if result.verified:
                print("Content verified safe")
            else:
                print("Content flagged")
                print(json.dumps(result.content, indent=2))
        except NewtonError as e:
            print(f"Error: {e.message}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "health":
        from .client import Newton, NewtonError
        try:
            newton = Newton(args.url)
            health = newton.health()
            print(f"Status: {health.get('status', 'unknown')}")
            print(f"Server: {args.url}")
        except NewtonError as e:
            print(f"Error: {e.message}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "demo":
        run_demo()

    elif args.command == "init":
        init_project(args.name)

    else:
        parser.print_help()


def parse_expression(expr_str: str) -> dict:
    """Parse a simple math expression into Newton format."""
    expr_str = expr_str.strip()

    for op, symbol in [("+", "+"), ("-", "-"), ("*", "*"), ("/", "/")]:
        if symbol in expr_str:
            parts = expr_str.split(symbol, 1)
            if len(parts) == 2:
                try:
                    a = float(parts[0].strip())
                    b = float(parts[1].strip())
                    return {"op": op, "args": [a, b]}
                except ValueError:
                    pass

    try:
        return {"op": "identity", "args": [float(expr_str)]}
    except ValueError:
        pass

    return {"op": "+", "args": [0, 0]}


def run_demo():
    """Run the tinyTalk demo."""
    print("""
===============================================================================
  TINYTALK DEMO - The "No-First" Philosophy
===============================================================================
""")

    try:
        from . import Blueprint, field, law, forge, when, finfr, LawViolation

        class BankAccount(Blueprint):
            balance = field(float, default=100.0)

            @law
            def no_overdraft(self):
                when(self.balance < 0, finfr)

            @forge
            def withdraw(self, amount):
                self.balance -= amount
                return f"Withdrew ${amount}"

        print("Creating BankAccount with $100...")
        account = BankAccount()
        print(f"  Balance: ${account.balance}")

        print("\nWithdrawing $30...")
        result = account.withdraw(30)
        print(f"  {result}")
        print(f"  Balance: ${account.balance}")

        print("\nWithdrawing $50...")
        result = account.withdraw(50)
        print(f"  {result}")
        print(f"  Balance: ${account.balance}")

        print("\nTrying to withdraw $30 (would overdraft)...")
        try:
            account.withdraw(30)
            print("  Success (shouldn't happen!)")
        except LawViolation as e:
            print(f"  BLOCKED: {e}")
            print(f"  Balance still: ${account.balance}")

        print("\n" + "=" * 79)
        print("The 'no_overdraft' law prevented the forbidden state (balance < 0).")
        print("This is the 'No-First' philosophy: define what CANNOT happen.")
        print("=" * 79)

    except ImportError as e:
        print(f"Error importing tinyTalk: {e}")
        sys.exit(1)


def init_project(name: str):
    """Initialize a new Newton project."""
    import os

    print(f"Creating Newton project: {name}")

    os.makedirs(name, exist_ok=True)

    # Create main.py
    main_content = '''"""
{name} - Built with Newton Supercomputer
"""

from newton import Blueprint, field, law, forge, when, finfr

class MyBlueprint(Blueprint):
    """Your first Newton Blueprint."""

    value = field(float, default=0.0)

    @law
    def must_be_positive(self):
        """Value cannot be negative."""
        when(self.value < 0, finfr)

    @forge
    def set_value(self, v: float):
        """Set the value (respects law)."""
        self.value = v
        return f"Value set to {{self.value}}"


if __name__ == "__main__":
    obj = MyBlueprint()
    print(f"Initial value: {{obj.value}}")

    obj.set_value(42)
    print(f"After set_value(42): {{obj.value}}")

    try:
        obj.set_value(-10)
    except Exception as e:
        print(f"set_value(-10) blocked: {{e}}")
'''.format(name=name)

    with open(os.path.join(name, "main.py"), "w") as f:
        f.write(main_content)

    # Create README
    readme_content = f'''# {name}

Built with Newton Supercomputer.

## Quick Start

```bash
pip install newton-computer
python main.py
```

## Learn More

- [Newton Documentation](https://github.com/jaredlewiswechs/Newton-api)
- [TinyTalk Programming Guide](https://github.com/jaredlewiswechs/Newton-api/blob/main/TINYTALK_PROGRAMMING_GUIDE.md)
'''

    with open(os.path.join(name, "README.md"), "w") as f:
        f.write(readme_content)

    print(f"""
Project created: {name}/
  main.py   - Your first Newton Blueprint
  README.md - Project documentation

Next steps:
  cd {name}
  python main.py
""")


if __name__ == "__main__":
    main()
