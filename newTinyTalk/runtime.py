"""
TinyTalk Runtime
Interpreter that executes the AST with bounded computation.

Fixes from original:
  - _eval_match uses node.value (not node.expr) and 2-tuple cases
  - _eval_try uses node.body (not node.try_body), no finally_body
  - String interpolation support
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Tuple
import time
import os
import re as _re

from .types import Value, ValueType
from .stdlib import format_value, BUILTIN_FUNCTIONS, STDLIB_CONSTANTS
from .errors import (
    undefined_variable_hint, unknown_step_hint, step_type_mismatch_hint,
    step_args_hint, find_closest,
)
from .typechecker import check_type, check_return_type, check_param_type
from .ast_nodes import (
    ASTNode, Program, Literal, Identifier, BinaryOp, UnaryOp, Call, Index,
    Member, Array, MapLiteral, Lambda, Conditional, Range, Pipe, StepChain,
    StringInterp, LetStmt, ConstStmt, AssignStmt, Block, IfStmt, ForStmt,
    WhileStmt, ReturnStmt, BreakStmt, ContinueStmt, FnDecl, StructDecl,
    EnumDecl, ImportStmt, MatchStmt, TryStmt, ThrowStmt,
)


# ---------------------------------------------------------------------------
# Control flow exceptions
# ---------------------------------------------------------------------------

class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class ReturnException(Exception):
    def __init__(self, value: Value):
        self.value = value


class TinyTalkError(Exception):
    def __init__(self, message: str, line: int = 0):
        self.message = message
        self.line = line
        super().__init__(f"Line {line}: {message}" if line else message)


# ---------------------------------------------------------------------------
# Scope
# ---------------------------------------------------------------------------

class Scope:
    def __init__(self, parent: Optional["Scope"] = None):
        self.parent = parent
        self.variables: Dict[str, Value] = {}
        self.constants: set = set()

    def define(self, name: str, value: Value, const: bool = False):
        self.variables[name] = value
        if const:
            self.constants.add(name)

    def get(self, name: str) -> Optional[Value]:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        return None

    def set(self, name: str, value: Value) -> bool:
        if name in self.variables:
            if name in self.constants:
                raise TinyTalkError(f"Cannot reassign constant '{name}'")
            self.variables[name] = value
            return True
        if self.parent:
            return self.parent.set(name, value)
        return False

    def has(self, name: str) -> bool:
        if name in self.variables:
            return True
        return self.parent.has(name) if self.parent else False


# ---------------------------------------------------------------------------
# Function / Struct / Instance types
# ---------------------------------------------------------------------------

@dataclass
class TinyFunction:
    name: str
    params: List[Tuple[str, Optional[str]]]
    body: Any
    closure: Scope
    is_native: bool = False
    native_fn: Optional[Callable] = None


@dataclass
class TinyStruct:
    name: str
    fields: List[Tuple[str, Optional[str], Optional[Any]]]
    methods: Dict[str, TinyFunction] = field(default_factory=dict)


@dataclass
class StructInstance:
    struct: TinyStruct
    fields: Dict[str, Value]


@dataclass
class BoundMethod:
    method: TinyFunction
    instance: StructInstance


@dataclass
class TinyEnum:
    name: str
    variants: Dict[str, Optional[Any]]


@dataclass
class EnumVariant:
    enum_name: str
    variant_name: str
    data: Optional[Value] = None


# ---------------------------------------------------------------------------
# Execution bounds
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExecutionBounds:
    max_ops: int = 1_000_000
    max_iterations: int = 100_000
    max_recursion: int = 1000
    timeout_seconds: float = 30.0


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------

class Runtime:
    def __init__(self, bounds: Optional[ExecutionBounds] = None, source_dir: str = ""):
        self.bounds = bounds or ExecutionBounds()
        self.global_scope = Scope()
        self.structs: Dict[str, TinyStruct] = {}
        self.enums: Dict[str, TinyEnum] = {}
        self._source_dir = source_dir or os.getcwd()
        self._imported_modules: Dict[str, Scope] = {}

        # metrics
        self.op_count = 0
        self.iteration_count = 0
        self.recursion_depth = 0
        self.start_time = 0.0

        self._register_builtins()

    # -- setup --------------------------------------------------------------

    def _register_builtins(self):
        for name, fn in BUILTIN_FUNCTIONS.items():
            self.global_scope.define(
                name,
                Value.function_val(TinyFunction(name, [], None, self.global_scope, True, fn)),
                const=True,
            )
        for name, val in STDLIB_CONSTANTS.items():
            self.global_scope.define(name, val, const=True)

        # Override higher-order builtins with runtime-aware versions
        # so they can call user-defined (non-native) functions.
        self._register_hof("filter", self._builtin_filter)
        self._register_hof("map_", self._builtin_map_fn)
        self._register_hof("reduce", self._builtin_reduce)

    def _register_hof(self, name: str, fn):
        self.global_scope.variables[name] = Value.function_val(
            TinyFunction(name, [], None, self.global_scope, True, fn)
        )

    def _builtin_filter(self, args: List[Value]) -> Value:
        if len(args) < 2:
            return Value.list_val([])
        fn_val, items = args[0], args[1]
        if fn_val.type != ValueType.FUNCTION or items.type != ValueType.LIST:
            return Value.list_val([])
        return Value.list_val([
            item for item in items.data
            if self._call_function(fn_val.data, [item], self.global_scope, 0).is_truthy()
        ])

    def _builtin_map_fn(self, args: List[Value]) -> Value:
        if len(args) < 2:
            return Value.list_val([])
        fn_val, items = args[0], args[1]
        if fn_val.type != ValueType.FUNCTION or items.type != ValueType.LIST:
            return Value.list_val([])
        return Value.list_val([
            self._call_function(fn_val.data, [item], self.global_scope, 0)
            for item in items.data
        ])

    def _builtin_reduce(self, args: List[Value]) -> Value:
        if len(args) < 3:
            return Value.null_val()
        fn_val, items, initial = args[0], args[1], args[2]
        if fn_val.type != ValueType.FUNCTION or items.type != ValueType.LIST:
            return initial
        acc = initial
        for item in items.data:
            acc = self._call_function(fn_val.data, [acc, item], self.global_scope, 0)
        return acc

    # -- execute ------------------------------------------------------------

    def execute(self, ast) -> Value:
        self.op_count = 0
        self.iteration_count = 0
        self.recursion_depth = 0
        self.start_time = time.time()
        try:
            return self._eval(ast, self.global_scope)
        except ReturnException as e:
            return e.value
        except (BreakException, ContinueException):
            raise TinyTalkError("break/continue outside loop")

    def _check_bounds(self):
        self.op_count += 1
        if self.op_count > self.bounds.max_ops:
            raise TinyTalkError(f"Exceeded max operations ({self.bounds.max_ops})")
        if time.time() - self.start_time > self.bounds.timeout_seconds:
            raise TinyTalkError(f"Exceeded timeout ({self.bounds.timeout_seconds}s)")

    # -- eval dispatcher ----------------------------------------------------

    def _eval(self, node, scope: Scope) -> Value:
        self._check_bounds()

        if isinstance(node, Program):
            result = Value.null_val()
            for stmt in node.statements:
                result = self._eval(stmt, scope)
            return result

        if isinstance(node, Literal):
            return self._eval_literal(node)

        if isinstance(node, Identifier):
            val = scope.get(node.name)
            if val is None:
                available = self._collect_names(scope)
                raise TinyTalkError(
                    undefined_variable_hint(node.name, available), node.line
                )
            return val

        if isinstance(node, BinaryOp):
            return self._eval_binary(node, scope)

        if isinstance(node, UnaryOp):
            return self._eval_unary(node, scope)

        if isinstance(node, Call):
            return self._eval_call(node, scope)

        if isinstance(node, Index):
            return self._eval_index(node, scope)

        if isinstance(node, Member):
            return self._eval_member(node, scope)

        if isinstance(node, Array):
            return Value.list_val([self._eval(el, scope) for el in node.elements])

        if isinstance(node, MapLiteral):
            pairs = {}
            for k, v in node.pairs:
                pairs[self._eval(k, scope).to_python()] = self._eval(v, scope)
            return Value.map_val(pairs)

        if isinstance(node, Lambda):
            params = [(p, None) for p in node.params]
            return Value.function_val(TinyFunction("<lambda>", params, node.body, scope))

        if isinstance(node, Conditional):
            cond = self._eval(node.condition, scope)
            return self._eval(node.then_expr if cond.is_truthy() else node.else_expr, scope)

        if isinstance(node, Range):
            s = self._eval(node.start, scope)
            e = self._eval(node.end, scope)
            end_val = e.data + 1 if node.inclusive else e.data
            return Value.list_val([Value.int_val(i) for i in range(int(s.data), int(end_val))])

        if isinstance(node, Pipe):
            return self._eval_pipe(node, scope)

        if isinstance(node, StepChain):
            return self._eval_step_chain(node, scope)

        if isinstance(node, StringInterp):
            return self._eval_string_interp(node, scope)

        if isinstance(node, LetStmt):
            val = self._eval(node.value, scope) if node.value else Value.null_val()
            if node.type_hint:
                err = check_type(val, node.type_hint, context=f"variable '{node.name}'")
                if err:
                    raise TinyTalkError(err, node.line)
            scope.define(node.name, val, const=False)
            return val

        if isinstance(node, ConstStmt):
            val = self._eval(node.value, scope) if node.value else Value.null_val()
            scope.define(node.name, val, const=True)
            return val

        if isinstance(node, AssignStmt):
            return self._eval_assign(node, scope)

        if isinstance(node, Block):
            block_scope = Scope(scope)
            result = Value.null_val()
            for stmt in node.statements:
                result = self._eval(stmt, block_scope)
            return result

        if isinstance(node, IfStmt):
            return self._eval_if(node, scope)

        if isinstance(node, ForStmt):
            return self._eval_for(node, scope)

        if isinstance(node, WhileStmt):
            return self._eval_while(node, scope)

        if isinstance(node, ReturnStmt):
            val = self._eval(node.value, scope) if node.value else Value.null_val()
            raise ReturnException(val)

        if isinstance(node, BreakStmt):
            raise BreakException()

        if isinstance(node, ContinueStmt):
            raise ContinueException()

        if isinstance(node, FnDecl):
            fn = TinyFunction(node.name, node.params, node.body, scope)
            fn._return_type = getattr(node, 'return_type', None)
            scope.define(node.name, Value.function_val(fn), const=True)
            return Value.null_val()

        if isinstance(node, StructDecl):
            return self._eval_struct_decl(node, scope)

        if isinstance(node, EnumDecl):
            self.enums[node.name] = TinyEnum(node.name, dict(node.variants))
            return Value.null_val()

        if isinstance(node, ImportStmt):
            return self._eval_import(node, scope)

        if isinstance(node, MatchStmt):
            return self._eval_match(node, scope)

        if isinstance(node, TryStmt):
            return self._eval_try(node, scope)

        if isinstance(node, ThrowStmt):
            val = self._eval(node.value, scope) if node.value else Value.null_val()
            raise TinyTalkError(str(val.data), node.line)

        raise TinyTalkError(f"Unknown node type: {type(node).__name__}")

    # -- literals -----------------------------------------------------------

    def _eval_literal(self, node: Literal) -> Value:
        v = node.value
        if v is None:
            return Value.null_val()
        if isinstance(v, bool):
            return Value.bool_val(v)
        if isinstance(v, int):
            return Value.int_val(v)
        if isinstance(v, float):
            return Value.float_val(v)
        if isinstance(v, str):
            return Value.string_val(v)
        return Value.null_val()

    # -- string interpolation -----------------------------------------------

    def _eval_string_interp(self, node: StringInterp, scope: Scope) -> Value:
        parts = []
        for part in node.parts:
            if isinstance(part, str):
                parts.append(part)
            else:
                val = self._eval(part, scope)
                parts.append(self._to_string(val))
        return Value.string_val("".join(parts))

    # -- binary ops ---------------------------------------------------------

    def _eval_binary(self, node: BinaryOp, scope: Scope) -> Value:
        op = node.op

        # Short-circuit
        if op == "and":
            left = self._eval(node.left, scope)
            if not left.is_truthy():
                return Value.bool_val(False)
            return Value.bool_val(self._eval(node.right, scope).is_truthy())

        if op == "or":
            left = self._eval(node.left, scope)
            if left.is_truthy():
                return Value.bool_val(True)
            return Value.bool_val(self._eval(node.right, scope).is_truthy())

        left = self._eval(node.left, scope)
        right = self._eval(node.right, scope)

        # Arithmetic
        if op == "+":
            if left.type == ValueType.STRING or right.type == ValueType.STRING:
                return Value.string_val(self._to_string(left) + self._to_string(right))
            if left.type == ValueType.LIST and right.type == ValueType.LIST:
                return Value.list_val(left.data + right.data)
            return self._numeric_op(left, right, lambda a, b: a + b, node.line)
        if op == "-":
            return self._numeric_op(left, right, lambda a, b: a - b, node.line)
        if op == "*":
            if left.type == ValueType.STRING and right.type == ValueType.INT:
                return Value.string_val(left.data * right.data)
            if left.type == ValueType.LIST and right.type == ValueType.INT:
                return Value.list_val(left.data * right.data)
            return self._numeric_op(left, right, lambda a, b: a * b, node.line)
        if op == "/":
            self._check_null(left, right, node.line)
            if right.data == 0:
                raise TinyTalkError("Division by zero", node.line)
            return Value.float_val(left.data / right.data)
        if op == "//":
            self._check_null(left, right, node.line)
            if right.data == 0:
                raise TinyTalkError("Division by zero", node.line)
            return Value.int_val(int(left.data // right.data))
        if op == "%":
            return self._numeric_op(left, right, lambda a, b: a % b, node.line)
        if op == "**":
            return self._numeric_op(left, right, lambda a, b: a ** b, node.line)

        # Comparison
        if op == "<":
            return Value.bool_val(left.data < right.data)
        if op == ">":
            return Value.bool_val(left.data > right.data)
        if op == "<=":
            return Value.bool_val(left.data <= right.data)
        if op == ">=":
            return Value.bool_val(left.data >= right.data)
        if op in ("==", "is"):
            return self._equal(left, right)
        if op in ("!=", "isnt"):
            return Value.bool_val(not self._equal(left, right).data)

        # Natural-language operators
        if op == "has":
            return self._eval_has(left, right)
        if op == "hasnt":
            return Value.bool_val(not self._eval_has(left, right).data)
        if op == "isin":
            return self._eval_has(right, left)  # swap: x isin list == list has x
        if op == "islike":
            return self._eval_islike(left, right)

        # Bitwise
        if op == "&":
            return Value.int_val(int(left.data) & int(right.data))
        if op == "|":
            return Value.int_val(int(left.data) | int(right.data))
        if op == "^":
            return Value.int_val(int(left.data) ^ int(right.data))
        if op == "<<":
            return Value.int_val(int(left.data) << int(right.data))
        if op == ">>":
            return Value.int_val(int(left.data) >> int(right.data))

        raise TinyTalkError(f"Unknown operator: {op}", node.line)

    def _eval_has(self, container: Value, item: Value) -> Value:
        if container.type == ValueType.LIST:
            return Value.bool_val(any(item.data == v.data for v in container.data))
        if container.type == ValueType.MAP:
            return Value.bool_val(item.to_python() in container.data)
        if container.type == ValueType.STRING:
            return Value.bool_val(str(item.data) in container.data)
        return Value.bool_val(False)

    def _eval_islike(self, left: Value, right: Value) -> Value:
        if left.type != ValueType.STRING or right.type != ValueType.STRING:
            return Value.bool_val(False)
        pattern = _re.escape(right.data)
        pattern = pattern.replace(r"\*", ".*").replace(r"\?", ".")
        try:
            return Value.bool_val(bool(_re.fullmatch(pattern, left.data, _re.IGNORECASE)))
        except Exception:
            return Value.bool_val(False)

    def _check_null(self, left, right, line):
        if left.type == ValueType.NULL or right.type == ValueType.NULL:
            raise TinyTalkError("Cannot perform arithmetic on null", line)

    def _numeric_op(self, left: Value, right: Value, op: Callable, line: int = 0) -> Value:
        if left.type == ValueType.NULL:
            raise TinyTalkError("Cannot perform arithmetic on null", line)
        if right.type == ValueType.NULL:
            raise TinyTalkError("Cannot perform arithmetic on null", line)
        result = op(left.data, right.data)
        if isinstance(result, float) and result.is_integer() and left.type == ValueType.INT and right.type == ValueType.INT:
            return Value.int_val(int(result))
        if isinstance(result, float):
            return Value.float_val(result)
        return Value.int_val(int(result))

    def _equal(self, left: Value, right: Value) -> Value:
        if left.type == right.type:
            if left.type == ValueType.FLOAT:
                if abs(left.data - right.data) < 1e-9:
                    return Value.bool_val(True)
                mx = max(abs(left.data), abs(right.data))
                if mx > 0 and abs(left.data - right.data) / mx < 1e-9:
                    return Value.bool_val(True)
                return Value.bool_val(False)
            if left.type == ValueType.LIST:
                if len(left.data) != len(right.data):
                    return Value.bool_val(False)
                return Value.bool_val(all(self._equal(a, b).data for a, b in zip(left.data, right.data)))
            if left.type == ValueType.MAP:
                if set(left.data.keys()) != set(right.data.keys()):
                    return Value.bool_val(False)
                return Value.bool_val(all(self._equal(left.data[k], right.data[k]).data for k in left.data))
            return Value.bool_val(left.data == right.data)
        if {left.type, right.type} == {ValueType.INT, ValueType.FLOAT}:
            if abs(float(left.data) - float(right.data)) < 1e-9:
                return Value.bool_val(True)
            return Value.bool_val(float(left.data) == float(right.data))
        return Value.bool_val(False)

    # -- unary --------------------------------------------------------------

    def _eval_unary(self, node: UnaryOp, scope: Scope) -> Value:
        operand = self._eval(node.operand, scope)
        if node.op == "-":
            if operand.type == ValueType.FLOAT:
                return Value.float_val(-operand.data)
            return Value.int_val(-int(operand.data))
        if node.op in ("not", "!"):
            return Value.bool_val(not operand.is_truthy())
        if node.op == "~":
            return Value.int_val(~int(operand.data))
        raise TinyTalkError(f"Unknown unary operator: {node.op}", node.line)

    # -- call ---------------------------------------------------------------

    def _eval_call(self, node: Call, scope: Scope) -> Value:
        callee = self._eval(node.callee, scope)
        args = [self._eval_call_arg(a, scope) for a in node.args]
        if callee.type != ValueType.FUNCTION:
            raise TinyTalkError(f"Cannot call {callee.type.value}", node.line)
        fn = callee.data
        if isinstance(fn, BoundMethod):
            return self._call_bound_method(fn, args, scope, node.line)
        return self._call_function(fn, args, scope, node.line)

    def _eval_call_arg(self, node, scope: Scope) -> Value:
        """Evaluate a call argument.  Undefined identifiers are treated as
        bare-word strings so that ``print(Hello, world!)`` works without
        quotes."""
        if isinstance(node, Identifier):
            val = scope.get(node.name)
            if val is not None:
                return val
            # Bare word: treat undefined identifier as a string literal.
            return Value.string_val(node.name)
        return self._eval(node, scope)

    def _call_function(self, fn: TinyFunction, args: List[Value], scope: Scope, line: int) -> Value:
        self.recursion_depth += 1
        if self.recursion_depth > self.bounds.max_recursion:
            raise TinyTalkError(f"Exceeded max recursion ({self.bounds.max_recursion})", line)
        try:
            if fn.is_native:
                return fn.native_fn(args)
            fn_scope = Scope(fn.closure)
            for i, param in enumerate(fn.params):
                pname = param[0]
                ptype = param[1] if len(param) > 1 else None
                default = param[2] if len(param) > 2 else None
                if i < len(args):
                    val = args[i]
                    # Optional type check on parameter
                    if ptype:
                        err = check_param_type(val, ptype, pname, fn.name)
                        if err:
                            raise TinyTalkError(err, line)
                    fn_scope.define(pname, val)
                elif default is not None:
                    fn_scope.define(pname, self._eval(default, fn.closure))
                else:
                    fn_scope.define(pname, Value.null_val())
            try:
                result = self._eval(fn.body, fn_scope)
            except ReturnException as e:
                result = e.value
            # Optional return type check
            if hasattr(fn, '_return_type') and fn._return_type:
                err = check_return_type(result, fn._return_type, fn.name)
                if err:
                    raise TinyTalkError(err, line)
            return result
        finally:
            self.recursion_depth -= 1

    def _call_bound_method(self, bound: BoundMethod, args: List[Value], scope: Scope, line: int) -> Value:
        self.recursion_depth += 1
        if self.recursion_depth > self.bounds.max_recursion:
            raise TinyTalkError(f"Exceeded max recursion ({self.bounds.max_recursion})", line)
        try:
            fn = bound.method
            fn_scope = Scope(fn.closure)
            fn_scope.define("self", Value(ValueType.STRUCT_INSTANCE, bound.instance))
            for i, param in enumerate(fn.params):
                pname = param[0]
                default = param[2] if len(param) > 2 else None
                if i < len(args):
                    fn_scope.define(pname, args[i])
                elif default is not None:
                    fn_scope.define(pname, self._eval(default, fn.closure))
                else:
                    fn_scope.define(pname, Value.null_val())
            try:
                return self._eval(fn.body, fn_scope)
            except ReturnException as e:
                return e.value
        finally:
            self.recursion_depth -= 1

    # -- pipe ---------------------------------------------------------------

    def _eval_pipe(self, node: Pipe, scope: Scope) -> Value:
        left = self._eval(node.left, scope)
        if isinstance(node.right, Call):
            fn_val = self._eval(node.right.callee, scope)
            args = [left] + [self._eval(a, scope) for a in node.right.args]
            return self._call_function(fn_val.data, args, scope, node.line)
        if isinstance(node.right, Identifier):
            fn_val = scope.get(node.right.name)
            if fn_val is None:
                raise TinyTalkError(f"Undefined '{node.right.name}'", node.line)
            return self._call_function(fn_val.data, [left], scope, node.line)
        fn_val = self._eval(node.right, scope)
        return self._call_function(fn_val.data, [left], scope, node.line)

    # -- index / member -----------------------------------------------------

    def _eval_index(self, node: Index, scope: Scope) -> Value:
        obj = self._eval(node.obj, scope)
        idx = self._eval(node.index, scope)
        if obj.type == ValueType.LIST:
            i = int(idx.data)
            if i < 0:
                i += len(obj.data)
            if i < 0 or i >= len(obj.data):
                raise TinyTalkError(f"Index {i} out of bounds", node.line)
            return obj.data[i]
        if obj.type == ValueType.MAP:
            k = idx.to_python()
            return obj.data.get(k, Value.null_val())
        if obj.type == ValueType.STRING:
            i = int(idx.data)
            if i < 0:
                i += len(obj.data)
            if i < 0 or i >= len(obj.data):
                raise TinyTalkError(f"Index {i} out of bounds", node.line)
            return Value.string_val(obj.data[i])
        raise TinyTalkError(f"Cannot index {obj.type.value}", node.line)

    def _eval_member(self, node: Member, scope: Scope) -> Value:
        obj = self._eval(node.obj, scope)
        f = node.field_name

        # Struct instance
        if obj.type == ValueType.STRUCT_INSTANCE:
            inst = obj.data
            if f in inst.fields:
                return inst.fields[f]
            if f in inst.struct.methods:
                return Value(ValueType.FUNCTION, BoundMethod(inst.struct.methods[f], inst))
            raise TinyTalkError(f"Unknown field '{f}'", node.line)

        # Map
        if obj.type == ValueType.MAP:
            return obj.data.get(f, Value.null_val())

        # Property conversions
        if f == "str":
            return Value.string_val(self._to_string(obj))
        if f == "int":
            return self._prop_int(obj)
        if f == "float":
            return self._prop_float(obj)
        if f == "bool":
            return Value.bool_val(obj.is_truthy())
        if f == "type":
            return Value.string_val(obj.type.value)
        if f == "len":
            if obj.type in (ValueType.STRING, ValueType.LIST):
                return Value.int_val(len(obj.data))
            if obj.type == ValueType.MAP:
                return Value.int_val(len(obj.data))
            return Value.int_val(0)
        if f == "num":
            if obj.type == ValueType.STRING:
                try:
                    return Value.float_val(float(obj.data)) if "." in obj.data else Value.int_val(int(obj.data))
                except (ValueError, OverflowError):
                    return Value.int_val(0)
            if obj.type in (ValueType.INT, ValueType.FLOAT):
                return obj
            return Value.int_val(0)

        # String methods
        if obj.type == ValueType.STRING:
            if f in ("length", "size"):
                return Value.int_val(len(obj.data))
            if f in ("upper", "upcase"):
                return Value.string_val(obj.data.upper())
            if f in ("lower", "downcase"):
                return Value.string_val(obj.data.lower())
            if f == "trim":
                return Value.string_val(obj.data.strip())
            if f == "chars":
                return Value.list_val([Value.string_val(c) for c in obj.data])
            if f == "words":
                return Value.list_val([Value.string_val(w) for w in obj.data.split()])
            if f == "lines":
                return Value.list_val([Value.string_val(l) for l in obj.data.splitlines()])
            if f == "reversed":
                return Value.string_val(obj.data[::-1])

        # List methods
        if obj.type == ValueType.LIST:
            if f in ("length", "size"):
                return Value.int_val(len(obj.data))
            if f == "first":
                return obj.data[0] if obj.data else Value.null_val()
            if f == "last":
                return obj.data[-1] if obj.data else Value.null_val()
            if f == "empty":
                return Value.bool_val(len(obj.data) == 0)
            if f == "reversed":
                return Value.list_val(list(reversed(obj.data)))

        raise TinyTalkError(f"Cannot access '.{f}' on {obj.type.value}", node.line)

    def _prop_int(self, obj: Value) -> Value:
        if obj.type == ValueType.STRING:
            try:
                return Value.int_val(int(float(obj.data)))
            except (ValueError, OverflowError):
                return Value.int_val(0)
        if obj.type in (ValueType.INT, ValueType.FLOAT):
            return Value.int_val(int(obj.data))
        if obj.type == ValueType.BOOLEAN:
            return Value.int_val(1 if obj.data else 0)
        return Value.int_val(0)

    def _prop_float(self, obj: Value) -> Value:
        if obj.type == ValueType.STRING:
            try:
                return Value.float_val(float(obj.data))
            except (ValueError, OverflowError):
                return Value.float_val(0.0)
        if obj.type in (ValueType.INT, ValueType.FLOAT):
            return Value.float_val(float(obj.data))
        return Value.float_val(0.0)

    # -- assignment ---------------------------------------------------------

    def _eval_assign(self, node: AssignStmt, scope: Scope) -> Value:
        val = self._eval(node.value, scope)
        if isinstance(node.target, Identifier):
            if node.op == "=":
                if not scope.set(node.target.name, val):
                    scope.define(node.target.name, val)
            else:
                old = scope.get(node.target.name)
                if old is None:
                    raise TinyTalkError(
                        undefined_variable_hint(node.target.name, self._collect_names(scope)),
                        node.line,
                    )
                new = self._apply_op(old, val, node.op[:-1], node.line)
                scope.set(node.target.name, new)
                return new
        elif isinstance(node.target, Index):
            container = self._eval(node.target.obj, scope)
            idx = self._eval(node.target.index, scope)
            if node.op != "=":
                old = self._eval_index(node.target, scope)
                val = self._apply_op(old, val, node.op[:-1], node.line)
            if container.type == ValueType.LIST:
                container.data[int(idx.data)] = val
            elif container.type == ValueType.MAP:
                container.data[idx.to_python()] = val
        elif isinstance(node.target, Member):
            obj = self._eval(node.target.obj, scope)
            if node.op != "=":
                old = self._eval_member(node.target, scope)
                val = self._apply_op(old, val, node.op[:-1], node.line)
            if obj.type == ValueType.STRUCT_INSTANCE:
                obj.data.fields[node.target.field_name] = val
            elif obj.type == ValueType.MAP:
                obj.data[node.target.field_name] = val
        return val

    def _apply_op(self, left: Value, right: Value, op: str, line: int) -> Value:
        ops = {
            "+": lambda a, b: a + b, "-": lambda a, b: a - b,
            "*": lambda a, b: a * b, "/": lambda a, b: a / b,
            "%": lambda a, b: a % b,
        }
        if op not in ops:
            raise TinyTalkError(f"Unknown operator: {op}", line)
        result = ops[op](left.data, right.data)
        if isinstance(result, float) and result.is_integer():
            return Value.int_val(int(result))
        if isinstance(result, float):
            return Value.float_val(result)
        return Value.int_val(int(result))

    # -- control flow -------------------------------------------------------

    def _eval_if(self, node: IfStmt, scope: Scope) -> Value:
        if self._eval(node.condition, scope).is_truthy():
            return self._eval(node.then_branch, scope)
        for cond, body in node.elif_branches:
            if self._eval(cond, scope).is_truthy():
                return self._eval(body, scope)
        if node.else_branch:
            return self._eval(node.else_branch, scope)
        return Value.null_val()

    def _eval_for(self, node: ForStmt, scope: Scope) -> Value:
        iterable = self._eval(node.iterable, scope)
        if iterable.type == ValueType.LIST:
            items = iterable.data
        elif iterable.type == ValueType.STRING:
            items = [Value.string_val(c) for c in iterable.data]
        elif iterable.type == ValueType.MAP:
            items = [Value.string_val(str(k)) for k in iterable.data.keys()]
        else:
            raise TinyTalkError(f"Cannot iterate over {iterable.type.value}", node.line)
        result = Value.null_val()
        for item in items:
            self.iteration_count += 1
            if self.iteration_count > self.bounds.max_iterations:
                raise TinyTalkError(f"Exceeded max iterations ({self.bounds.max_iterations})", node.line)
            loop_scope = Scope(scope)
            loop_scope.define(node.var, item)
            try:
                result = self._eval(node.body, loop_scope)
            except BreakException:
                break
            except ContinueException:
                continue
        return result

    def _eval_while(self, node: WhileStmt, scope: Scope) -> Value:
        result = Value.null_val()
        while True:
            self.iteration_count += 1
            if self.iteration_count > self.bounds.max_iterations:
                raise TinyTalkError(f"Exceeded max iterations ({self.bounds.max_iterations})", node.line)
            if not self._eval(node.condition, scope).is_truthy():
                break
            try:
                result = self._eval(node.body, scope)
            except BreakException:
                break
            except ContinueException:
                continue
        return result

    # -- match (FIXED: uses node.value and 2-tuple cases) -------------------

    def _eval_match(self, node: MatchStmt, scope: Scope) -> Value:
        value = self._eval(node.value, scope)
        for pattern, body in node.cases:
            if self._match_pattern(value, pattern, scope):
                return self._eval(body, scope)
        return Value.null_val()

    def _match_pattern(self, value: Value, pattern, scope: Scope) -> bool:
        if isinstance(pattern, Literal):
            return value.data == pattern.value
        if isinstance(pattern, Identifier):
            if pattern.name == "_":
                return True
            scope.define(pattern.name, value)
            return True
        return False

    # -- try/catch (FIXED: uses node.body, no finally_body) -----------------

    def _eval_try(self, node: TryStmt, scope: Scope) -> Value:
        try:
            return self._eval(node.body, scope)
        except TinyTalkError as e:
            if node.catch_var and node.catch_body:
                catch_scope = Scope(scope)
                catch_scope.define(node.catch_var, Value.string_val(e.message))
                return self._eval(node.catch_body, catch_scope)
            raise

    # -- struct decl --------------------------------------------------------

    def _eval_struct_decl(self, node: StructDecl, scope: Scope) -> Value:
        methods = {}
        for kind, method_decl in node.methods:
            methods[method_decl.name] = TinyFunction(
                method_decl.name, method_decl.params, method_decl.body, scope,
            )
        struct = TinyStruct(node.name, node.fields, methods)
        self.structs[node.name] = struct
        scope.define(
            node.name,
            Value.function_val(TinyFunction(
                node.name, [(f[0], f[1]) for f in node.fields], None, scope, True,
                lambda args, s=struct: self._construct_struct(s, args),
            )),
            const=True,
        )
        return Value.null_val()

    def _construct_struct(self, struct: TinyStruct, args: List[Value]) -> Value:
        fields = {}
        for i, (name, _, default) in enumerate(struct.fields):
            if i < len(args):
                fields[name] = args[i]
            elif default:
                fields[name] = self._eval(default, self.global_scope)
            else:
                fields[name] = Value.null_val()
        return Value(ValueType.STRUCT_INSTANCE, StructInstance(struct, fields))

    # -- imports ------------------------------------------------------------

    def _eval_import(self, node: ImportStmt, scope: Scope) -> Value:
        """Execute an import statement.

        Supported forms:
            import "utils.tt"                 -- run module, import all top-level names
            import "utils.tt" as utils        -- run module, bind to namespace alias
            from "stats.tt" use { mean, median }  -- selective imports
        """
        from .lexer import Lexer
        from .parser import Parser

        mod_path = node.module
        # Resolve relative to source directory
        if not os.path.isabs(mod_path):
            mod_path = os.path.join(self._source_dir, mod_path)

        # Normalize and check for .tt extension
        if not mod_path.endswith(".tt"):
            mod_path += ".tt"

        abs_path = os.path.abspath(mod_path)

        if not os.path.exists(abs_path):
            raise TinyTalkError(f"Module not found: '{node.module}'. Looked in: {abs_path}", node.line)

        # Check for already-imported module (avoid re-execution)
        if abs_path in self._imported_modules:
            mod_scope = self._imported_modules[abs_path]
        else:
            # Read and execute the module
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    source = f.read()
            except OSError as e:
                raise TinyTalkError(f"Cannot read module '{node.module}': {e}", node.line)

            tokens = Lexer(source).tokenize()
            ast = Parser(tokens).parse()

            # Execute in a fresh scope (child of global for builtins)
            mod_scope = Scope(self.global_scope)
            old_dir = self._source_dir
            self._source_dir = os.path.dirname(abs_path)
            try:
                self._eval(ast, mod_scope)
            finally:
                self._source_dir = old_dir

            self._imported_modules[abs_path] = mod_scope

        # Bind names into the current scope
        if node.items:
            # from "module" use { name1, name2 }
            for name in node.items:
                val = mod_scope.variables.get(name)
                if val is None:
                    raise TinyTalkError(
                        f"Module '{node.module}' does not export '{name}'", node.line
                    )
                scope.define(name, val)
        elif node.alias:
            # import "module" as alias -> bind all as a namespace map
            ns = {}
            for name, val in mod_scope.variables.items():
                if not name.startswith("_"):
                    ns[name] = val
            scope.define(node.alias, Value.map_val(ns))
        else:
            # import "module" -> import all top-level (non-underscore) names
            for name, val in mod_scope.variables.items():
                if not name.startswith("_"):
                    scope.define(name, val)

        return Value.null_val()

    # -- step chains --------------------------------------------------------

    def _eval_step_chain(self, node: StepChain, scope: Scope) -> Value:
        data = self._eval(node.source, scope)
        for step_name, step_args in node.steps:
            args = [self._eval(a, scope) for a in step_args]
            data = self._apply_step(data, step_name, args, scope, node.line)
        return data

    def _apply_step(self, data: Value, step: str, args: List[Value], scope: Scope, line: int) -> Value:
        # Steps that work on maps directly (before list conversion)
        if step == "_mapValues":
            if not args or args[0].type != ValueType.FUNCTION:
                raise TinyTalkError("_mapValues requires a function", line)
            fn = args[0].data
            if data.type == ValueType.MAP:
                return Value.map_val({
                    k: self._call_function(fn, [v], scope, line)
                    for k, v in data.data.items()
                })
            raise TinyTalkError("_mapValues requires a map", line)

        # _summarize on a grouped map: aggregate each group into a summary row
        if step == "_summarize" and data.type == ValueType.MAP:
            if not args or args[0].type != ValueType.MAP:
                raise TinyTalkError("_summarize requires a map of aggregation functions", line)
            agg_map = args[0].data
            result = []
            for group_key, group_val in data.data.items():
                row = {}
                group_items = group_val if group_val.type == ValueType.LIST else Value.list_val([group_val])
                for col_name, fn_val in agg_map.items():
                    if fn_val.type == ValueType.FUNCTION:
                        row[col_name] = self._call_function(
                            fn_val.data, [group_items], scope, line
                        )
                    else:
                        row[col_name] = fn_val
                result.append(Value.map_val(row))
            return Value.list_val(result)

        if data.type != ValueType.LIST:
            if data.type == ValueType.STRING:
                data = Value.list_val([Value.string_val(c) for c in data.data])
            else:
                raise TinyTalkError(step_type_mismatch_hint(step, data.type.value), line)
        items = data.data

        if step == "_filter":
            if not args or args[0].type != ValueType.FUNCTION:
                raise TinyTalkError(step_args_hint("_filter"), line)
            return Value.list_val([
                item for item in items
                if self._call_function(args[0].data, [item], scope, line).is_truthy()
            ])

        if step == "_sort":
            if args and args[0].type == ValueType.FUNCTION:
                key_fn = args[0]
                return Value.list_val(sorted(items, key=lambda x: self._call_function(key_fn.data, [x], scope, line).to_python()))
            return Value.list_val(sorted(items, key=lambda x: x.to_python()))

        if step == "_map":
            if not args or args[0].type != ValueType.FUNCTION:
                raise TinyTalkError(step_args_hint("_map"), line)
            return Value.list_val([self._call_function(args[0].data, [item], scope, line) for item in items])

        if step == "_take":
            n = int(args[0].data) if args else 1
            return Value.list_val(items[:n])

        if step == "_drop":
            n = int(args[0].data) if args else 1
            return Value.list_val(items[n:])

        if step == "_first":
            return items[0] if items else Value.null_val()

        if step == "_last":
            return items[-1] if items else Value.null_val()

        if step == "_reverse":
            return Value.list_val(list(reversed(items)))

        if step == "_unique":
            seen = set()
            result = []
            for item in items:
                k = item.to_python()
                if isinstance(k, list):
                    k = tuple(k)
                if k not in seen:
                    seen.add(k)
                    result.append(item)
            return Value.list_val(result)

        if step == "_count":
            if args and args[0].type == ValueType.FUNCTION:
                return Value.int_val(sum(1 for item in items if self._call_function(args[0].data, [item], scope, line).is_truthy()))
            return Value.int_val(len(items))

        if step == "_sum":
            total = sum(item.data for item in items if item.type in (ValueType.INT, ValueType.FLOAT))
            return Value.float_val(total) if any(item.type == ValueType.FLOAT for item in items) else Value.int_val(int(total))

        if step == "_avg":
            nums = [item.data for item in items if item.type in (ValueType.INT, ValueType.FLOAT)]
            return Value.float_val(sum(nums) / len(nums)) if nums else Value.null_val()

        if step == "_min":
            return min(items, key=lambda x: x.to_python()) if items else Value.null_val()

        if step == "_max":
            return max(items, key=lambda x: x.to_python()) if items else Value.null_val()

        if step == "_group":
            if not args or args[0].type != ValueType.FUNCTION:
                raise TinyTalkError("_group requires a function", line)
            groups: dict = {}
            for item in items:
                k = self._call_function(args[0].data, [item], scope, line).to_python()
                groups.setdefault(k, []).append(item)
            return Value.map_val({k: Value.list_val(v) for k, v in groups.items()})

        if step == "_flatten":
            result = []
            for item in items:
                if item.type == ValueType.LIST:
                    result.extend(item.data)
                else:
                    result.append(item)
            return Value.list_val(result)

        if step == "_zip":
            if not args or args[0].type != ValueType.LIST:
                raise TinyTalkError("_zip requires a list", line)
            return Value.list_val([Value.list_val([a, b]) for a, b in zip(items, args[0].data)])

        if step == "_chunk":
            n = int(args[0].data) if args else 2
            return Value.list_val([Value.list_val(items[i:i + n]) for i in range(0, len(items), n)])

        if step == "_reduce":
            if not args or args[0].type != ValueType.FUNCTION:
                raise TinyTalkError("_reduce requires a function", line)
            if len(args) < 2:
                if not items:
                    return Value.null_val()
                acc = items[0]
                remaining = items[1:]
            else:
                acc = args[1]
                remaining = items
            for item in remaining:
                acc = self._call_function(args[0].data, [acc, item], scope, line)
            return acc

        if step == "_sortBy":
            if not args or args[0].type != ValueType.FUNCTION:
                raise TinyTalkError("_sortBy requires a key function", line)
            key_fn = args[0].data
            decorated = [(self._call_function(key_fn, [item], scope, line), item) for item in items]
            decorated.sort(key=lambda pair: pair[0].data)
            return Value.list_val([pair[1] for pair in decorated])

        if step == "_join":
            if not args or args[0].type != ValueType.LIST:
                raise TinyTalkError("_join requires a right-hand list", line)
            right = args[0].data
            if len(args) < 2 or args[1].type != ValueType.FUNCTION:
                raise TinyTalkError("_join requires (right_list, key_fn)", line)
            key_fn = args[1].data
            right_idx: dict = {}
            for r in right:
                k = self._call_function(key_fn, [r], scope, line).to_python()
                right_idx.setdefault(k, []).append(r)
            result = []
            for l_item in items:
                k = self._call_function(key_fn, [l_item], scope, line).to_python()
                for r_item in right_idx.get(k, []):
                    merged = {}
                    if l_item.type == ValueType.MAP:
                        merged.update(l_item.data)
                    if r_item.type == ValueType.MAP:
                        for rk, rv in r_item.data.items():
                            if rk not in merged:
                                merged[rk] = rv
                    result.append(Value.map_val(merged))
            return Value.list_val(result)

        if step == "_each":
            if not args or args[0].type != ValueType.FUNCTION:
                raise TinyTalkError("_each requires a function", line)
            fn = args[0].data
            for item in items:
                self._call_function(fn, [item], scope, line)
            return Value.list_val(items)

        # ---- dplyr-style verbs ------------------------------------------------

        if step == "_select":
            if not args:
                raise TinyTalkError("_select requires column names", line)
            if args[0].type == ValueType.LIST:
                cols = [v.data for v in args[0].data]
                return Value.list_val([
                    Value.map_val({c: row.data.get(c, Value.null_val()) for c in cols})
                    for row in items if row.type == ValueType.MAP
                ])
            if args[0].type == ValueType.STRING:
                cols = [a.data for a in args if a.type == ValueType.STRING]
                return Value.list_val([
                    Value.map_val({c: row.data.get(c, Value.null_val()) for c in cols})
                    for row in items if row.type == ValueType.MAP
                ])
            raise TinyTalkError("_select requires a list of column names or string args", line)

        if step == "_mutate":
            if not args or args[0].type != ValueType.FUNCTION:
                raise TinyTalkError("_mutate requires a function", line)
            fn = args[0].data
            result = []
            for row in items:
                new_fields = self._call_function(fn, [row], scope, line)
                if row.type == ValueType.MAP and new_fields.type == ValueType.MAP:
                    merged = dict(row.data)
                    merged.update(new_fields.data)
                    result.append(Value.map_val(merged))
                else:
                    result.append(row)
            return Value.list_val(result)

        if step == "_summarize":
            if not args or args[0].type != ValueType.MAP:
                raise TinyTalkError("_summarize requires a map of aggregation functions", line)
            agg_map = args[0].data
            result_row = {}
            for col_name, fn_val in agg_map.items():
                if fn_val.type == ValueType.FUNCTION:
                    result_row[col_name] = self._call_function(
                        fn_val.data, [Value.list_val(items)], scope, line
                    )
                else:
                    result_row[col_name] = fn_val
            return Value.map_val(result_row)

        if step == "_rename":
            if not args or args[0].type != ValueType.MAP:
                raise TinyTalkError("_rename requires a map of {old: new}", line)
            rename_map = {k: v.data for k, v in args[0].data.items()
                          if v.type == ValueType.STRING}
            result = []
            for row in items:
                if row.type == ValueType.MAP:
                    new_row = {}
                    for k, v in row.data.items():
                        new_key = rename_map.get(k, k)
                        new_row[new_key] = v
                    result.append(Value.map_val(new_row))
                else:
                    result.append(row)
            return Value.list_val(result)

        if step == "_arrange":
            # Alias for _sortBy with optional "desc" flag
            if not args or args[0].type != ValueType.FUNCTION:
                raise TinyTalkError("_arrange requires a key function", line)
            key_fn = args[0].data
            desc = (len(args) > 1 and args[1].type == ValueType.STRING
                    and args[1].data == "desc")
            decorated = [(self._call_function(key_fn, [item], scope, line), item)
                         for item in items]
            decorated.sort(key=lambda pair: pair[0].data, reverse=desc)
            return Value.list_val([pair[1] for pair in decorated])

        if step == "_distinct":
            if args and args[0].type == ValueType.FUNCTION:
                key_fn = args[0].data
                seen = set()
                result = []
                for item in items:
                    k = self._call_function(key_fn, [item], scope, line).to_python()
                    if isinstance(k, list):
                        k = tuple(k)
                    if k not in seen:
                        seen.add(k)
                        result.append(item)
                return Value.list_val(result)
            if args and args[0].type == ValueType.LIST:
                cols = [v.data for v in args[0].data]
                seen = set()
                result = []
                for item in items:
                    if item.type == ValueType.MAP:
                        k = tuple(item.data.get(c, Value.null_val()).to_python()
                                  for c in cols)
                    else:
                        k = item.to_python()
                        if isinstance(k, list):
                            k = tuple(k)
                    if k not in seen:
                        seen.add(k)
                        result.append(item)
                return Value.list_val(result)
            # No args: unique on whole value (same as _unique)
            seen = set()
            result = []
            for item in items:
                k = item.to_python()
                if isinstance(k, list):
                    k = tuple(k)
                if k not in seen:
                    seen.add(k)
                    result.append(item)
            return Value.list_val(result)

        if step == "_slice":
            start = int(args[0].data) if args else 0
            count = int(args[1].data) if len(args) > 1 else len(items) - start
            return Value.list_val(items[start:start + count])

        if step == "_pull":
            if not args or args[0].type != ValueType.STRING:
                raise TinyTalkError("_pull requires a column name string", line)
            col = args[0].data
            return Value.list_val([
                row.data.get(col, Value.null_val()) if row.type == ValueType.MAP
                else Value.null_val()
                for row in items
            ])

        if step in ("_groupBy", "_group_by"):
            if not args or args[0].type != ValueType.FUNCTION:
                raise TinyTalkError("_groupBy requires a function", line)
            groups: dict = {}
            for item in items:
                k = self._call_function(args[0].data, [item], scope, line).to_python()
                groups.setdefault(k, []).append(item)
            return Value.map_val({k: Value.list_val(v) for k, v in groups.items()})

        if step in ("_leftJoin", "_left_join"):
            if not args or args[0].type != ValueType.LIST:
                raise TinyTalkError("_leftJoin requires a right-hand list", line)
            right = args[0].data
            if len(args) < 2 or args[1].type != ValueType.FUNCTION:
                raise TinyTalkError("_leftJoin requires (right_list, key_fn)", line)
            key_fn = args[1].data
            right_idx: dict = {}
            for r in right:
                k = self._call_function(key_fn, [r], scope, line).to_python()
                right_idx.setdefault(k, []).append(r)
            result = []
            for l_item in items:
                k = self._call_function(key_fn, [l_item], scope, line).to_python()
                matches = right_idx.get(k, [])
                if matches:
                    for r_item in matches:
                        merged = {}
                        if l_item.type == ValueType.MAP:
                            merged.update(l_item.data)
                        if r_item.type == ValueType.MAP:
                            for rk, rv in r_item.data.items():
                                if rk not in merged:
                                    merged[rk] = rv
                        result.append(Value.map_val(merged))
                else:
                    # Left join: keep unmatched left rows
                    result.append(l_item)
            return Value.list_val(result)

        # ---- reshape operations -----------------------------------------------

        if step == "_pivot":
            # _pivot(index_fn, column_fn, value_fn)
            # Converts long-form data to wide-form.
            # Each unique (index, column) pair maps to a value.
            if len(args) < 3:
                raise TinyTalkError("_pivot requires (index_fn, column_fn, value_fn)", line)
            idx_fn, col_fn, val_fn = args[0].data, args[1].data, args[2].data
            # Build: {index_key: {col_key: value, ...}, ...}
            pivot_data: dict = {}
            all_cols: list = []
            for item in items:
                idx = self._call_function(idx_fn, [item], scope, line)
                col = self._call_function(col_fn, [item], scope, line)
                val = self._call_function(val_fn, [item], scope, line)
                idx_key = format_value(idx)
                col_key = format_value(col)
                if idx_key not in pivot_data:
                    pivot_data[idx_key] = {}
                pivot_data[idx_key][col_key] = val
                if col_key not in all_cols:
                    all_cols.append(col_key)
            # Convert to list of maps: [{_index: key, col1: v1, col2: v2}, ...]
            result = []
            for idx_key, cols in pivot_data.items():
                row = {"_index": Value.string_val(idx_key)}
                for c in all_cols:
                    row[c] = cols.get(c, Value.null_val())
                result.append(Value.map_val(row))
            return Value.list_val(result)

        if step == "_unpivot":
            # _unpivot(id_columns) — id_columns is a list of column name strings
            # Converts wide-form to long-form.
            # Columns not in id_columns become (variable, value) pairs.
            if not args or args[0].type != ValueType.LIST:
                raise TinyTalkError("_unpivot requires a list of id column names", line)
            id_cols = {v.data for v in args[0].data if v.type == ValueType.STRING}
            result = []
            for row in items:
                if row.type != ValueType.MAP:
                    continue
                id_data = {k: v for k, v in row.data.items() if k in id_cols}
                for k, v in row.data.items():
                    if k not in id_cols:
                        new_row = dict(id_data)
                        new_row["variable"] = Value.string_val(k)
                        new_row["value"] = v
                        result.append(Value.map_val(new_row))
            return Value.list_val(result)

        # ---- window / rolling operations --------------------------------------

        if step == "_window":
            # _window(size, fn) — sliding window aggregate
            # Returns a list of fn(window) for each position.
            if len(args) < 2:
                raise TinyTalkError("_window requires (window_size, function)", line)
            window_size = int(args[0].data)
            fn = args[1].data
            result = []
            for i in range(len(items)):
                start = max(0, i - window_size + 1)
                window = Value.list_val(items[start:i + 1])
                val = self._call_function(fn, [window], scope, line)
                result.append(val)
            return Value.list_val(result)

        raise TinyTalkError(unknown_step_hint(step), line)

    # -- helpers ------------------------------------------------------------

    def _collect_names(self, scope: Scope) -> list:
        """Collect all variable names visible from the given scope."""
        names = []
        s = scope
        while s:
            names.extend(s.variables.keys())
            s = s.parent
        return list(set(names))

    def _to_string(self, val: Value) -> str:
        return format_value(val)
