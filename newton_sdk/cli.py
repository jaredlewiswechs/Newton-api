#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 Newton CLI
═══════════════════════════════════════════════════════════════════════════════

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

    # version
    parser.add_argument("--version", action="version", version="newton-sdk 1.0.0")

    args = parser.parse_args()

    if args.command == "serve":
        from .server import serve
        serve(host=args.host, port=args.port, reload=args.reload)

    elif args.command == "calc":
        from .client import Newton, NewtonError
        try:
            newton = Newton(args.url)
            # Parse simple expression
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
                print("✓ Content verified safe")
            else:
                print("✗ Content flagged")
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

    else:
        parser.print_help()


def parse_expression(expr_str: str) -> dict:
    """Parse a simple math expression into Newton format."""
    expr_str = expr_str.strip()

    # Handle simple binary operations
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

    # Try as single number
    try:
        return {"op": "identity", "args": [float(expr_str)]}
    except ValueError:
        pass

    # Return as-is for complex expressions
    return {"op": "+", "args": [0, 0]}


def run_demo():
    """Run the tinyTalk demo."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  TINYTALK DEMO - The "No-First" Philosophy                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
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
            print(f"  ✗ BLOCKED: {e}")
            print(f"  Balance still: ${account.balance}")

        print("\n" + "═" * 79)
        print("The 'no_overdraft' law prevented the forbidden state (balance < 0).")
        print("This is the 'No-First' philosophy: define what CANNOT happen.")
        print("═" * 79)

    except ImportError as e:
        print(f"Error importing tinyTalk: {e}")
        print("Make sure you're in the Newton-api directory.")
        sys.exit(1)


if __name__ == "__main__":
    main()
