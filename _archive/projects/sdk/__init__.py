"""
Newton SDK - Auto-Discovering Verified Computation Engine

Usage:
    from newton import Newton
    n = Newton()
    n.ask("What is 2+2?")

Or:
    import newton
    newton.connect()
    newton.ask("Hello!")
"""

from .newton import (
    Newton,
    NewtonResponse,
    NewtonError,
    NewtonConnectionError,
    NewtonValidationError,
    NewtonAuthError,
    NewtonRateLimitError,
    NewtonVerificationFailed,
    connect,
    ask,
    verify,
    __version__
)

__all__ = [
    "Newton",
    "NewtonResponse",
    "NewtonError",
    "NewtonConnectionError",
    "NewtonValidationError",
    "NewtonAuthError",
    "NewtonRateLimitError",
    "NewtonVerificationFailed",
    "connect",
    "ask",
    "verify",
    "__version__"
]
