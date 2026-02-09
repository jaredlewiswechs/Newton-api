#!/usr/bin/env python3
"""
06_api_client.py - Using the Newton Remote API

Connect to a Newton server for verified computation.
Run this with a Newton server available.
"""

from newton import Newton, NewtonError


def main():
    print("=" * 60)
    print("  NEWTON API CLIENT - Remote Verified Computation")
    print("=" * 60)
    print()

    # Connect to Newton server
    # Use your server URL here
    server_url = "http://localhost:8000"

    print(f"Connecting to Newton at {server_url}...")
    newton = Newton(server_url)

    try:
        # Check health
        print()
        print("--- Health Check ---")
        health = newton.health()
        print(f"Status: {health.get('status', 'unknown')}")

        # Verified calculation
        print()
        print("--- Verified Calculations ---")

        # Simple math
        result = newton.calculate({"op": "+", "args": [2, 3]})
        print(f"2 + 3 = {result.result} (verified: {result.verified})")

        result = newton.calculate({"op": "*", "args": [7, 8]})
        print(f"7 * 8 = {result.result} (verified: {result.verified})")

        # Nested expression
        result = newton.calculate({
            "op": "*",
            "args": [
                {"op": "+", "args": [1, 2]},
                {"op": "+", "args": [3, 4]}
            ]
        })
        print(f"(1+2) * (3+4) = {result.result} (verified: {result.verified})")

        # Using convenience methods
        print()
        print("--- Convenience Methods ---")
        print(f"add(10, 20) = {newton.add(10, 20)}")
        print(f"subtract(100, 37) = {newton.subtract(100, 37)}")
        print(f"multiply(12, 12) = {newton.multiply(12, 12)}")
        print(f"divide(100, 4) = {newton.divide(100, 4)}")

        # Content verification
        print()
        print("--- Content Verification ---")
        content = "This is a test message."
        result = newton.verify(content)
        print(f"Content: '{content}'")
        print(f"Verified: {result.verified}")

        # Constraint evaluation
        print()
        print("--- Constraint Evaluation ---")
        constraint = {
            "field": "balance",
            "operator": "ge",
            "value": 0
        }
        obj = {"balance": 100}
        result = newton.constraint(constraint, obj)
        print(f"Constraint: balance >= 0")
        print(f"Object: {obj}")
        print(f"Result: {result.result}")

        # Another constraint
        obj_negative = {"balance": -50}
        result = newton.constraint(constraint, obj_negative)
        print(f"Object: {obj_negative}")
        print(f"Result: {result.result}")

        # Robust statistics
        print()
        print("--- Robust Statistics ---")
        data = [1, 2, 3, 4, 5, 100]  # Note the outlier
        result = newton.statistics(data)
        print(f"Data: {data}")
        print(f"Statistics: {result}")

    except NewtonError as e:
        print()
        print(f"Error: {e.message}")
        print()
        print("Make sure the Newton server is running:")
        print("  newton serve --port 8000")
        print()
        print("Or install server dependencies:")
        print("  pip install newton-computer[server]")

    print()
    print("=" * 60)
    print("The Newton API provides verified computation over HTTP.")
    print("All calculations come with cryptographic verification.")
    print("=" * 60)


if __name__ == "__main__":
    main()
