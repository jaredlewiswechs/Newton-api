"""
TinyTalk Standard Library
Built-in functions available in every program.
"""

from typing import List
import math
import hashlib

from .types import Value, ValueType


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_value(val: Value, seen: set = None) -> str:
    """Format a value for display, with circular-reference detection."""
    if seen is None:
        seen = set()
    val_id = id(val.data) if val.type in (ValueType.LIST, ValueType.MAP) else None
    if val_id is not None:
        if val_id in seen:
            return "[circular]" if val.type == ValueType.LIST else "{circular}"
        seen = seen | {val_id}
    if val.type == ValueType.STRING:
        return val.data
    if val.type == ValueType.NULL:
        return "null"
    if val.type == ValueType.BOOLEAN:
        return "true" if val.data else "false"
    if val.type == ValueType.LIST:
        items = ", ".join(format_value(v, seen) for v in val.data)
        return f"[{items}]"
    if val.type == ValueType.MAP:
        pairs = ", ".join(f"{k}: {format_value(v, seen)}" for k, v in val.data.items())
        return f"{{{pairs}}}"
    if val.type == ValueType.STRUCT_INSTANCE:
        inst = val.data
        fs = ", ".join(f"{k}: {format_value(v, seen)}" for k, v in inst.fields.items())
        return f"{inst.struct.name}{{{fs}}}"
    return str(val.data)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

# Captured output buffer (used by server / tests)
_output_buffer: list = None


def set_output_buffer(buf: list):
    global _output_buffer
    _output_buffer = buf


def clear_output_buffer():
    global _output_buffer
    _output_buffer = None


def _emit(text: str):
    global _output_buffer
    if _output_buffer is not None:
        _output_buffer.append(text)
    else:
        print(text, end="")


def builtin_print(args: List[Value]) -> Value:
    _emit(" ".join(format_value(a) for a in args))
    return Value.null_val()


def builtin_show(args: List[Value]) -> Value:
    _emit(" ".join(format_value(a) for a in args) + "\n")
    return Value.null_val()


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

def builtin_input(args: List[Value]) -> Value:
    prompt = args[0].data if args and args[0].type == ValueType.STRING else ""
    return Value.string_val(input(prompt))


# ---------------------------------------------------------------------------
# Type conversions
# ---------------------------------------------------------------------------

def builtin_len(args: List[Value]) -> Value:
    if not args:
        return Value.int_val(0)
    v = args[0]
    if v.type in (ValueType.STRING, ValueType.LIST):
        return Value.int_val(len(v.data))
    if v.type == ValueType.MAP:
        return Value.int_val(len(v.data))
    return Value.int_val(0)


def builtin_type(args: List[Value]) -> Value:
    if not args:
        return Value.string_val("null")
    return Value.string_val(args[0].type.value)


def builtin_typeof(args: List[Value]) -> Value:
    return builtin_type(args)


def builtin_str(args: List[Value]) -> Value:
    if not args:
        return Value.string_val("")
    return Value.string_val(format_value(args[0]))


def builtin_int(args: List[Value]) -> Value:
    if not args:
        return Value.int_val(0)
    v = args[0]
    if v.type == ValueType.INT:
        return v
    if v.type == ValueType.FLOAT:
        return Value.int_val(int(v.data))
    if v.type == ValueType.STRING:
        try:
            return Value.int_val(int(float(v.data)))
        except (ValueError, OverflowError):
            return Value.int_val(0)
    if v.type == ValueType.BOOLEAN:
        return Value.int_val(1 if v.data else 0)
    return Value.int_val(0)


def builtin_float(args: List[Value]) -> Value:
    if not args:
        return Value.float_val(0.0)
    v = args[0]
    if v.type == ValueType.FLOAT:
        return v
    if v.type == ValueType.INT:
        return Value.float_val(float(v.data))
    if v.type == ValueType.STRING:
        try:
            return Value.float_val(float(v.data))
        except (ValueError, OverflowError):
            return Value.float_val(0.0)
    return Value.float_val(0.0)


def builtin_bool(args: List[Value]) -> Value:
    if not args:
        return Value.bool_val(False)
    return Value.bool_val(args[0].is_truthy())


def builtin_list(args: List[Value]) -> Value:
    if not args:
        return Value.list_val([])
    if len(args) == 1:
        v = args[0]
        if v.type == ValueType.LIST:
            return v
        if v.type == ValueType.STRING:
            return Value.list_val([Value.string_val(c) for c in v.data])
        if v.type == ValueType.MAP:
            return Value.list_val([Value.string_val(str(k)) for k in v.data.keys()])
    return Value.list_val(list(args))


def builtin_map(args: List[Value]) -> Value:
    if not args:
        return Value.map_val({})
    if len(args) == 1 and args[0].type == ValueType.LIST:
        result = {}
        for item in args[0].data:
            if item.type == ValueType.LIST and len(item.data) >= 2:
                result[item.data[0].to_python()] = item.data[1]
        return Value.map_val(result)
    return Value.map_val({})


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------

def builtin_range(args: List[Value]) -> Value:
    if not args:
        return Value.list_val([])
    if len(args) == 1:
        return Value.list_val([Value.int_val(i) for i in range(int(args[0].data))])
    if len(args) == 2:
        return Value.list_val([Value.int_val(i) for i in range(int(args[0].data), int(args[1].data))])
    return Value.list_val([Value.int_val(i) for i in range(int(args[0].data), int(args[1].data), int(args[2].data))])


def builtin_append(args: List[Value]) -> Value:
    if len(args) < 2 or args[0].type != ValueType.LIST:
        return Value.null_val()
    args[0].data.append(args[1])
    return args[0]


def builtin_push(args: List[Value]) -> Value:
    return builtin_append(args)


def builtin_pop(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.LIST or not args[0].data:
        return Value.null_val()
    return args[0].data.pop()


def builtin_keys(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.MAP:
        return Value.list_val([])
    return Value.list_val([Value.string_val(str(k)) for k in args[0].data.keys()])


def builtin_values(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.MAP:
        return Value.list_val([])
    return Value.list_val(list(args[0].data.values()))


def builtin_contains(args: List[Value]) -> Value:
    if len(args) < 2:
        return Value.bool_val(False)
    coll, item = args[0], args[1]
    if coll.type == ValueType.LIST:
        return Value.bool_val(any(v.data == item.data for v in coll.data))
    if coll.type == ValueType.MAP:
        return Value.bool_val(item.to_python() in coll.data)
    if coll.type == ValueType.STRING:
        return Value.bool_val(str(item.data) in coll.data)
    return Value.bool_val(False)


def builtin_slice(args: List[Value]) -> Value:
    if not args:
        return Value.null_val()
    v = args[0]
    start = int(args[1].data) if len(args) > 1 else 0
    end = int(args[2].data) if len(args) > 2 else None
    if v.type == ValueType.LIST:
        return Value.list_val(v.data[start:end])
    if v.type == ValueType.STRING:
        return Value.string_val(v.data[start:end])
    return Value.null_val()


def builtin_reverse(args: List[Value]) -> Value:
    if not args:
        return Value.null_val()
    v = args[0]
    if v.type == ValueType.LIST:
        return Value.list_val(v.data[::-1])
    if v.type == ValueType.STRING:
        return Value.string_val(v.data[::-1])
    return v


def builtin_sort(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.LIST:
        return Value.list_val([])
    items = args[0].data[:]
    items.sort(key=lambda v: v.data)
    return Value.list_val(items)


def builtin_filter(args: List[Value]) -> Value:
    if len(args) < 2:
        return Value.list_val([])
    fn, items = args[0], args[1]
    if fn.type != ValueType.FUNCTION or items.type != ValueType.LIST:
        return Value.list_val([])
    result = []
    for item in items.data:
        if fn.data.is_native:
            test = fn.data.native_fn([item])
        else:
            test = Value.bool_val(True)
        if test.is_truthy():
            result.append(item)
    return Value.list_val(result)


def builtin_map_fn(args: List[Value]) -> Value:
    if len(args) < 2:
        return Value.list_val([])
    fn, items = args[0], args[1]
    if fn.type != ValueType.FUNCTION or items.type != ValueType.LIST:
        return Value.list_val([])
    result = []
    for item in items.data:
        if fn.data.is_native:
            result.append(fn.data.native_fn([item]))
        else:
            result.append(item)
    return Value.list_val(result)


def builtin_reduce(args: List[Value]) -> Value:
    if len(args) < 3:
        return Value.null_val()
    fn, items, initial = args[0], args[1], args[2]
    if fn.type != ValueType.FUNCTION or items.type != ValueType.LIST:
        return initial
    acc = initial
    for item in items.data:
        if fn.data.is_native:
            acc = fn.data.native_fn([acc, item])
        else:
            acc = item
    return acc


def builtin_zip(args: List[Value]) -> Value:
    if len(args) < 2:
        return Value.list_val([])
    lists = [a.data for a in args if a.type == ValueType.LIST]
    if not lists:
        return Value.list_val([])
    return Value.list_val([Value.list_val(list(items)) for items in zip(*lists)])


def builtin_enumerate(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.LIST:
        return Value.list_val([])
    return Value.list_val([Value.list_val([Value.int_val(i), v]) for i, v in enumerate(args[0].data)])


# ---------------------------------------------------------------------------
# String functions
# ---------------------------------------------------------------------------

def builtin_split(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.STRING:
        return Value.list_val([])
    s = args[0].data
    delim = args[1].data if len(args) > 1 and args[1].type == ValueType.STRING else " "
    return Value.list_val([Value.string_val(p) for p in s.split(delim)])


def builtin_join(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.LIST:
        return Value.string_val("")
    items = args[0].data
    delim = args[1].data if len(args) > 1 and args[1].type == ValueType.STRING else ""
    return Value.string_val(delim.join(format_value(v) for v in items))


def builtin_replace(args: List[Value]) -> Value:
    """replace(string, old, new) -> string with all occurrences replaced."""
    if len(args) < 3:
        return Value.string_val("" if not args else format_value(args[0]))
    s = format_value(args[0])
    old = format_value(args[1])
    new = format_value(args[2])
    return Value.string_val(s.replace(old, new))


def builtin_trim(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.STRING:
        return Value.string_val("")
    return Value.string_val(args[0].data.strip())


def builtin_upcase(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.STRING:
        return Value.string_val("")
    return Value.string_val(args[0].data.upper())


def builtin_downcase(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.STRING:
        return Value.string_val("")
    return Value.string_val(args[0].data.lower())


def builtin_startswith(args: List[Value]) -> Value:
    if len(args) < 2:
        return Value.bool_val(False)
    if args[0].type != ValueType.STRING or args[1].type != ValueType.STRING:
        return Value.bool_val(False)
    return Value.bool_val(args[0].data.startswith(args[1].data))


def builtin_endswith(args: List[Value]) -> Value:
    if len(args) < 2:
        return Value.bool_val(False)
    if args[0].type != ValueType.STRING or args[1].type != ValueType.STRING:
        return Value.bool_val(False)
    return Value.bool_val(args[0].data.endswith(args[1].data))


# ---------------------------------------------------------------------------
# Math
# ---------------------------------------------------------------------------

def builtin_sum(args: List[Value]) -> Value:
    if not args or args[0].type != ValueType.LIST:
        return Value.int_val(0)
    total = sum(v.data for v in args[0].data if v.type in (ValueType.INT, ValueType.FLOAT))
    return Value.float_val(total) if isinstance(total, float) else Value.int_val(total)


def builtin_min(args: List[Value]) -> Value:
    if not args:
        return Value.null_val()
    if args[0].type == ValueType.LIST:
        if not args[0].data:
            return Value.null_val()
        vals = [v.data for v in args[0].data]
    else:
        vals = [a.data for a in args]
    r = min(vals)
    return Value.float_val(r) if isinstance(r, float) else Value.int_val(r)


def builtin_max(args: List[Value]) -> Value:
    if not args:
        return Value.null_val()
    if args[0].type == ValueType.LIST:
        if not args[0].data:
            return Value.null_val()
        vals = [v.data for v in args[0].data]
    else:
        vals = [a.data for a in args]
    r = max(vals)
    return Value.float_val(r) if isinstance(r, float) else Value.int_val(r)


def builtin_abs(args: List[Value]) -> Value:
    if not args:
        return Value.int_val(0)
    v = args[0]
    if v.type == ValueType.FLOAT:
        return Value.float_val(abs(v.data))
    return Value.int_val(abs(int(v.data)))


def builtin_round(args: List[Value]) -> Value:
    if not args:
        return Value.int_val(0)
    places = int(args[1].data) if len(args) > 1 else 0
    if places == 0:
        return Value.int_val(round(args[0].data))
    return Value.float_val(round(args[0].data, places))


def builtin_floor(args: List[Value]) -> Value:
    if not args:
        return Value.int_val(0)
    return Value.int_val(math.floor(args[0].data))


def builtin_ceil(args: List[Value]) -> Value:
    if not args:
        return Value.int_val(0)
    return Value.int_val(math.ceil(args[0].data))


def builtin_sqrt(args: List[Value]) -> Value:
    if not args:
        return Value.float_val(0.0)
    return Value.float_val(math.sqrt(args[0].data))


def builtin_pow(args: List[Value]) -> Value:
    if len(args) < 2:
        return Value.float_val(0.0)
    return Value.float_val(math.pow(args[0].data, args[1].data))


def builtin_sin(args: List[Value]) -> Value:
    if not args:
        return Value.float_val(0.0)
    return Value.float_val(math.sin(args[0].data))


def builtin_cos(args: List[Value]) -> Value:
    if not args:
        return Value.float_val(1.0)
    return Value.float_val(math.cos(args[0].data))


def builtin_tan(args: List[Value]) -> Value:
    if not args:
        return Value.float_val(0.0)
    return Value.float_val(math.tan(args[0].data))


def builtin_log(args: List[Value]) -> Value:
    if not args:
        return Value.float_val(0.0)
    base = args[1].data if len(args) > 1 else math.e
    return Value.float_val(math.log(args[0].data, base))


def builtin_exp(args: List[Value]) -> Value:
    if not args:
        return Value.float_val(1.0)
    return Value.float_val(math.exp(args[0].data))


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------

def builtin_assert(args: List[Value]) -> Value:
    if not args:
        return Value.null_val()
    if not args[0].is_truthy():
        msg = args[1].data if len(args) > 1 and args[1].type == ValueType.STRING else "Assertion failed"
        raise AssertionError(msg)
    return Value.bool_val(True)


def builtin_assert_equal(args: List[Value]) -> Value:
    if len(args) < 2:
        raise ValueError("assert_equal requires 2 arguments")
    actual, expected = args[0], args[1]
    if _values_equal(actual, expected):
        return Value.bool_val(True)
    msg_parts = [f"assert_equal failed:\n  expected: {format_value(expected)}\n  actual:   {format_value(actual)}"]
    if len(args) > 2 and args[2].type == ValueType.STRING:
        msg_parts.insert(0, args[2].data)
    raise AssertionError("\n".join(msg_parts))


def builtin_assert_true(args: List[Value]) -> Value:
    if not args:
        raise ValueError("assert_true requires 1 argument")
    if args[0].is_truthy():
        return Value.bool_val(True)
    msg = f"assert_true failed: {format_value(args[0])} is not truthy"
    if len(args) > 1 and args[1].type == ValueType.STRING:
        msg = f"{args[1].data}\n{msg}"
    raise AssertionError(msg)


def builtin_assert_false(args: List[Value]) -> Value:
    if not args:
        raise ValueError("assert_false requires 1 argument")
    if not args[0].is_truthy():
        return Value.bool_val(True)
    msg = f"assert_false failed: {format_value(args[0])} is truthy"
    if len(args) > 1 and args[1].type == ValueType.STRING:
        msg = f"{args[1].data}\n{msg}"
    raise AssertionError(msg)


def _values_equal(a: Value, b: Value) -> bool:
    if a.type != b.type:
        if a.type == ValueType.INT and b.type == ValueType.FLOAT:
            return float(a.data) == b.data
        if a.type == ValueType.FLOAT and b.type == ValueType.INT:
            return a.data == float(b.data)
        return False
    if a.type == ValueType.LIST:
        if len(a.data) != len(b.data):
            return False
        return all(_values_equal(x, y) for x, y in zip(a.data, b.data))
    if a.type == ValueType.MAP:
        if set(a.data.keys()) != set(b.data.keys()):
            return False
        return all(_values_equal(a.data[k], b.data[k]) for k in a.data)
    if a.type == ValueType.FLOAT:
        if abs(a.data - b.data) < 1e-9:
            return True
    return a.data == b.data


def builtin_hash(args: List[Value]) -> Value:
    if not args:
        return Value.string_val("")
    data = format_value(args[0]).encode("utf-8")
    return Value.string_val(hashlib.sha256(data).hexdigest()[:16])


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

BUILTIN_FUNCTIONS = {
    # Output
    "print": builtin_print,
    "println": builtin_show,
    "show": builtin_show,
    # Input
    "input": builtin_input,
    # Types
    "len": builtin_len,
    "type": builtin_type,
    "typeof": builtin_typeof,
    "str": builtin_str,
    "int": builtin_int,
    "float": builtin_float,
    "bool": builtin_bool,
    "list": builtin_list,
    "map": builtin_map,
    # Collections
    "range": builtin_range,
    "append": builtin_append,
    "push": builtin_push,
    "pop": builtin_pop,
    "keys": builtin_keys,
    "values": builtin_values,
    "contains": builtin_contains,
    "slice": builtin_slice,
    "reverse": builtin_reverse,
    "sort": builtin_sort,
    # Higher-order
    "filter": builtin_filter,
    "map_": builtin_map_fn,
    "reduce": builtin_reduce,
    "zip": builtin_zip,
    "enumerate": builtin_enumerate,
    # Strings
    "split": builtin_split,
    "join": builtin_join,
    "replace": builtin_replace,
    "trim": builtin_trim,
    "upcase": builtin_upcase,
    "downcase": builtin_downcase,
    "startswith": builtin_startswith,
    "endswith": builtin_endswith,
    # Math
    "sum": builtin_sum,
    "min": builtin_min,
    "max": builtin_max,
    "abs": builtin_abs,
    "round": builtin_round,
    "floor": builtin_floor,
    "ceil": builtin_ceil,
    "sqrt": builtin_sqrt,
    "pow": builtin_pow,
    "sin": builtin_sin,
    "cos": builtin_cos,
    "tan": builtin_tan,
    "log": builtin_log,
    "exp": builtin_exp,
    # Assertions
    "assert": builtin_assert,
    "assert_equal": builtin_assert_equal,
    "assert_true": builtin_assert_true,
    "assert_false": builtin_assert_false,
    "hash": builtin_hash,
}

STDLIB_CONSTANTS = {
    "PI": Value.float_val(math.pi),
    "E": Value.float_val(math.e),
    "TAU": Value.float_val(math.tau),
    "INF": Value.float_val(float("inf")),
    "true": Value.bool_val(True),
    "false": Value.bool_val(False),
    "null": Value.null_val(),
}
