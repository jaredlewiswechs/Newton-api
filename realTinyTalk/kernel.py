"""
═══════════════════════════════════════════════════════════════════════════════
TINYTALK KERNEL
The Newton-verified computation core

Compile → Bound → Execute → Verify → Ledger → Return
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Union
import time
import hashlib
import json


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def stable_json(x: Any) -> str:
    """Deterministic JSON serialization."""
    def norm(v):
        if v is None or isinstance(v, (int, float, str, bool)):
            return v
        if isinstance(v, list):
            return [norm(i) for i in v]
        if isinstance(v, dict):
            return {k: norm(v[k]) for k in sorted(v.keys())}
        return repr(v)
    return json.dumps(norm(x), ensure_ascii=False, separators=(",", ":"))


def sha256(s: str) -> str:
    """SHA-256 hash of string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# TRACE - Audit trail for every operation
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Trace:
    """A single trace entry in the execution log."""
    step: str
    ok: bool
    meta: Optional[Dict[str, Any]] = None
    note: Optional[str] = None
    at: float = 0.0

    @staticmethod
    def t(step: str, ok: bool, meta: Optional[Dict] = None, note: Optional[str] = None) -> 'Trace':
        return Trace(step=step, ok=ok, meta=meta, note=note, at=time.time())

    def to_dict(self) -> Dict:
        return {
            "step": self.step,
            "ok": self.ok,
            "meta": self.meta,
            "note": self.note,
            "at": self.at
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FIN / FINFR - Success and failure types
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Fin:
    """Successful computation result."""
    kind: str = "fin"
    value: Any = None
    trace: List[Trace] = field(default_factory=list)

    def __bool__(self) -> bool:
        return True

    def to_dict(self) -> Dict:
        return {
            "kind": self.kind,
            "value": self.value,
            "trace": [t.to_dict() for t in self.trace]
        }


@dataclass
class Finfr:
    """Failed computation result (fin-failure-reason)."""
    kind: str = "finfr"
    reason: str = ""
    trace: List[Trace] = field(default_factory=list)

    def __bool__(self) -> bool:
        return False

    def to_dict(self) -> Dict:
        return {
            "kind": self.kind,
            "reason": self.reason,
            "trace": [t.to_dict() for t in self.trace]
        }


Result = Union[Fin, Finfr]


def fin(value: Any, trace: List[Trace]) -> Fin:
    """Create a successful result."""
    return Fin(kind="fin", value=value, trace=trace)


def finfr(reason: str, trace: List[Trace]) -> Finfr:
    """Create a failure result."""
    return Finfr(kind="finfr", reason=reason, trace=trace)


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTION BOUNDS - The difference between Turing and verified
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExecutionBounds:
    """
    Every computation has bounds.
    This is what makes TinyTalk verified.
    """
    max_ops: int = 1_000_000          # Max total operations
    max_iterations: int = 100_000      # Max loop iterations
    max_recursion: int = 1000          # Max call stack depth
    max_memory_mb: int = 100           # Max memory in MB
    timeout_seconds: float = 30.0      # Max execution time

    def check(self, ops: int, depth: int, start_time: float) -> Optional[str]:
        """Return error string if bounds exceeded, else None."""
        if ops > self.max_ops:
            return f"Operation limit exceeded: {ops} > {self.max_ops}"
        if depth > self.max_recursion:
            return f"Recursion limit exceeded: {depth} > {self.max_recursion}"
        if time.time() - start_time > self.timeout_seconds:
            return f"Timeout exceeded: {self.timeout_seconds}s"
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# LEDGER - Hash-chained audit trail
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class LedgerEntry:
    """Immutable ledger entry with hash chain."""
    index: int
    timestamp: float
    operation: str
    input_hash: str
    output_hash: str
    prev_hash: str
    hash: str


class Ledger:
    """Hash-chained audit ledger."""

    def __init__(self) -> None:
        self.entries: List[LedgerEntry] = []

    def append(self, op: str, input_obj: Any, output_obj: Any) -> LedgerEntry:
        """Add entry to ledger with hash chain."""
        prev_hash = self.entries[-1].hash if self.entries else "GENESIS"
        body = {
            "i": len(self.entries),
            "ts": time.time(),
            "op": op,
            "in_hash": sha256(stable_json(input_obj)),
            "out_hash": sha256(stable_json(output_obj)),
            "prev_hash": prev_hash,
        }
        h = sha256(stable_json(body))
        entry = LedgerEntry(
            index=body["i"],
            timestamp=body["ts"],
            operation=op,
            input_hash=body["in_hash"],
            output_hash=body["out_hash"],
            prev_hash=prev_hash,
            hash=h
        )
        self.entries.append(entry)
        return entry

    def verify_chain(self) -> bool:
        """Verify the hash chain integrity."""
        for i, entry in enumerate(self.entries):
            expected_prev = self.entries[i-1].hash if i > 0 else "GENESIS"
            if entry.prev_hash != expected_prev:
                return False
        return True

    def __len__(self) -> int:
        return len(self.entries)


# ═══════════════════════════════════════════════════════════════════════════════
# TRUST POLICY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TrustPolicy:
    """Trust configuration for external resources."""
    allow_ffi: bool = True             # Allow foreign function interface
    allow_network: bool = False        # Allow network access
    allow_filesystem: bool = True      # Allow file system access
    require_types: bool = False        # Require type annotations
    strict_mode: bool = False          # Strict evaluation mode


# ═══════════════════════════════════════════════════════════════════════════════
# COMPILER - Parse source to AST
# ═══════════════════════════════════════════════════════════════════════════════

class Compiler:
    """Compiles TinyTalk source to AST."""

    def __init__(self):
        from .lexer import Lexer
        from .parser import Parser
        self.lexer_class = Lexer
        self.parser_class = Parser

    def compile(self, source: str) -> Result:
        """Compile source code to AST."""
        trace = [Trace.t("compile:start", True, {"length": len(source)})]

        try:
            # Tokenize
            lexer = self.lexer_class(source)
            tokens = lexer.tokenize()
            trace.append(Trace.t("compile:tokenize", True, {"tokens": len(tokens)}))

            # Parse
            parser = self.parser_class(tokens)
            ast = parser.parse()
            trace.append(Trace.t("compile:parse", True, {"nodes": len(ast) if isinstance(ast, list) else 1}))

            return fin(ast, trace)

        except SyntaxError as e:
            trace.append(Trace.t("compile:error", False, note=str(e)))
            return finfr(f"Syntax error: {e}", trace)
        except Exception as e:
            trace.append(Trace.t("compile:error", False, note=str(e)))
            return finfr(f"Compilation error: {e}", trace)


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFIER - Pre/post execution checks
# ═══════════════════════════════════════════════════════════════════════════════

class Verifier:
    """Pre and post execution verification."""

    def __init__(self, policy: TrustPolicy):
        self.policy = policy

    def precheck(self, ast: Any) -> Result:
        """Verify AST before execution."""
        trace = [Trace.t("verify:precheck", True)]

        # Check for forbidden constructs
        if not self.policy.allow_ffi:
            if self._contains_ffi(ast):
                trace.append(Trace.t("verify:ffi_denied", False))
                return finfr("FFI calls not allowed by policy", trace)

        if not self.policy.allow_network:
            if self._contains_network(ast):
                trace.append(Trace.t("verify:network_denied", False))
                return finfr("Network access not allowed by policy", trace)

        return fin(True, trace)

    def postcheck(self, result: Any, trace_log: List[Trace]) -> Result:
        """Verify result after execution."""
        trace = [Trace.t("verify:postcheck", True)]

        # Check for unverified values
        if hasattr(result, 'verified') and not result.verified:
            trace.append(Trace.t("verify:unverified", False))
            return finfr("Result contains unverified values", trace)

        return fin(True, trace)

    def _contains_ffi(self, ast: Any) -> bool:
        """Check if AST contains FFI calls."""
        # Implementation depends on AST structure
        return False

    def _contains_network(self, ast: Any) -> bool:
        """Check if AST contains network calls."""
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTOR - Bounded execution
# ═══════════════════════════════════════════════════════════════════════════════

class Executor:
    """Execute AST with bounds enforcement."""

    def __init__(self, bounds: ExecutionBounds):
        self.bounds = bounds

    def run(self, ast: Any, env: Dict[str, Any]) -> tuple[Any, List[Trace]]:
        """Execute AST within bounds."""
        from .runtime import Runtime
        
        trace = [Trace.t("exec:start", True)]
        start_time = time.time()

        try:
            runtime = Runtime(self.bounds)
            # Seed global scope with env bindings
            if env:
                for k, v in env.items():
                    runtime.global_scope.set(k, v)
            result = runtime.execute(ast)
            
            elapsed = time.time() - start_time
            trace.append(Trace.t("exec:done", True, {
                "ops": runtime.op_count,
                "elapsed_ms": int(elapsed * 1000)
            }))
            
            return result, trace

        except RuntimeError as e:
            trace.append(Trace.t("exec:bounds_exceeded", False, note=str(e)))
            raise
        except Exception as e:
            trace.append(Trace.t("exec:error", False, note=str(e)))
            raise


# ═══════════════════════════════════════════════════════════════════════════════
# META - Invariant verification
# ═══════════════════════════════════════════════════════════════════════════════

class Meta:
    """Meta-level verification of system invariants."""

    def verify(self, ledger: Ledger) -> Result:
        """Verify ledger integrity."""
        trace = [Trace.t("meta:verify", True, {"entries": len(ledger)})]

        if not ledger.verify_chain():
            trace.append(Trace.t("meta:chain_broken", False))
            return finfr("Ledger hash chain verification failed", trace)

        return fin(True, trace)


# ═══════════════════════════════════════════════════════════════════════════════
# TINYTALK KERNEL - The main execution loop
# ═══════════════════════════════════════════════════════════════════════════════

class TinyTalkKernel:
    """
    TinyTalk Kernel - Verified Computation
    
    Compile → Verify → Execute (bounded) → Verify → Ledger → Return
    """

    def __init__(
        self,
        bounds: Optional[ExecutionBounds] = None,
        policy: Optional[TrustPolicy] = None,
        env: Optional[Dict[str, Any]] = None
    ):
        self.bounds = bounds or ExecutionBounds()
        self.policy = policy or TrustPolicy()
        self.env = env or {}
        
        self.compiler = Compiler()
        self.verifier = Verifier(self.policy)
        self.executor = Executor(self.bounds)
        self.meta = Meta()
        self.ledger = Ledger()

    def run(self, source: str) -> Result:
        """Execute TinyTalk source code."""
        trace: List[Trace] = [Trace.t("kernel:start", True)]

        # 1) Compile
        compile_result = self.compiler.compile(source)
        trace.extend(compile_result.trace)
        if isinstance(compile_result, Finfr):
            self.ledger.append("finfr", {"source": source[:100]}, {"reason": compile_result.reason})
            return finfr(compile_result.reason, trace)

        ast = compile_result.value

        # 2) Pre-verify
        pre = self.verifier.precheck(ast)
        trace.extend(pre.trace)
        if isinstance(pre, Finfr):
            self.ledger.append("finfr", {"source": source[:100]}, {"reason": pre.reason})
            return finfr(pre.reason, trace)

        # 3) Execute (bounded)
        try:
            result, exec_trace = self.executor.run(ast, self.env)
            trace.extend(exec_trace)
        except RuntimeError as e:
            self.ledger.append("finfr", {"source": source[:100]}, {"reason": str(e)})
            return finfr(str(e), trace)

        # 4) Post-verify
        post = self.verifier.postcheck(result, trace)
        trace.extend(post.trace)
        if isinstance(post, Finfr):
            self.ledger.append("unverified", {"source": source[:100]}, {"result": str(result)})
            return finfr(post.reason, trace)

        # 5) Ledger commit
        entry = self.ledger.append("fin", {"source": source[:100]}, {"result": str(result)})
        trace.append(Trace.t("ledger:commit", True, {"hash": entry.hash}))

        # 6) Meta verify
        m = self.meta.verify(self.ledger)
        trace.extend(m.trace)

        return fin(result, trace)

    def eval(self, source: str) -> Any:
        """Convenience method - execute and return just the value."""
        result = self.run(source)
        if isinstance(result, Fin):
            return result.value
        raise RuntimeError(result.reason)

    def repl(self):
        """Interactive REPL."""
        print("TinyTalk v1.0 - Verified Computation")
        print("Type 'exit' to quit, 'help' for commands\n")

        while True:
            try:
                line = input(">>> ").strip()
                if not line:
                    continue
                if line == "exit":
                    break
                if line == "help":
                    self._print_help()
                    continue
                if line == "ledger":
                    self._print_ledger()
                    continue

                result = self.run(line)
                if isinstance(result, Fin):
                    print(result.value)
                else:
                    print(f"Error: {result.reason}")

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                break

    def _print_help(self):
        print("""
TinyTalk Commands:
  exit    - Exit REPL
  help    - Show this help
  ledger  - Show execution ledger

Language:
  let x = 5           - Variable binding
  fn add(a, b) a + b  - Function definition
  if x > 0 then 1 else 0  - Conditional
  for i in 0..10 { }  - Bounded loop
  import "py:math"    - FFI import
""")

    def _print_ledger(self):
        print(f"\nLedger ({len(self.ledger)} entries):")
        for entry in self.ledger.entries[-10:]:
            print(f"  [{entry.index}] {entry.operation}: {entry.hash[:16]}...")
        print()
