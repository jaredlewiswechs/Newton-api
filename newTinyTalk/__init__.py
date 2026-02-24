"""
newTinyTalk - A Smalltalk-inspired programming language.

Two styles, one language:
  - Modern:  let, fn, return, { }
  - Classic: when, law, forge, reply, end

Standout features:
  - Step chains:  data _filter(pred) _sort _take(3)
  - Property conversions:  x.str  x.int  x.type  x.len
  - Natural comparisons:  x is y, list has item, s islike "A*"
  - Space-separated args:  show "hello" name
  - String interpolation:  "Hello {name}, you are {age}"
  - Bounded execution:  max ops, max time, max recursion

Quick usage:
    from newTinyTalk import TinyTalkKernel

    kernel = TinyTalkKernel()
    result = kernel.run('show("Hello!")')
    print(result.output)   # Hello!\n
    print(result.success)  # True
"""

from .kernel import TinyTalkKernel, RunResult
from .runtime import ExecutionBounds, TinyTalkError
from .types import Value, ValueType

__version__ = "2.0.0"
__all__ = [
    "TinyTalkKernel",
    "RunResult",
    "ExecutionBounds",
    "TinyTalkError",
    "Value",
    "ValueType",
]
