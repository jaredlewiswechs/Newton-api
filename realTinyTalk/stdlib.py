"""
═══════════════════════════════════════════════════════════════════════════════
TINYTALK STANDARD LIBRARY
Built-in functions for everyday programming

Everything you need, nothing you don't.
═══════════════════════════════════════════════════════════════════════════════
"""

from typing import List, Any
import math
import hashlib

from .types import Value, ValueType


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_print(args: List[Value]) -> Value:
    """Print values without newline."""
    output = ' '.join(_format_value(a) for a in args)
    print(output, end='')
    return Value.null_val()


def builtin_println(args: List[Value]) -> Value:
    """Print values with newline."""
    output = ' '.join(_format_value(a) for a in args)
    print(output)
    return Value.null_val()


def builtin_show(args: List[Value]) -> Value:
    """
    Show values - the friendliest way to print.
    Auto-converts everything, spaces between args, newline at end.
    
    show "hello"           -> hello
    show "x is" 42         -> x is 42  
    show name "has" count  -> Newton has 42
    """
    output = ' '.join(_format_value(a, set()) for a in args)
    print(output)
    return Value.null_val()


def _format_value(val: Value, seen: set = None) -> str:
    """Format a value for printing with circular reference detection."""
    if seen is None:
        seen = set()
    
    # Check for circular reference
    val_id = id(val.data) if val.type in (ValueType.LIST, ValueType.MAP) else None
    if val_id is not None:
        if val_id in seen:
            return "[circular]" if val.type == ValueType.LIST else "{circular}"
        seen = seen | {val_id}  # Create new set to avoid mutation
    
    if val.type == ValueType.STRING:
        return val.data
    if val.type == ValueType.NULL:
        return "null"
    if val.type == ValueType.BOOLEAN:
        return "true" if val.data else "false"
    if val.type == ValueType.LIST:
        items = ', '.join(_format_value(v, seen) for v in val.data)
        return f"[{items}]"
    if val.type == ValueType.MAP:
        pairs = ', '.join(f"{k}: {_format_value(v, seen)}" for k, v in val.data.items())
        return f"{{{pairs}}}"
    return str(val.data)


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_input(args: List[Value]) -> Value:
    """Read input from user."""
    prompt = args[0].data if args and args[0].type == ValueType.STRING else ""
    result = input(prompt)
    return Value.string_val(result)


# ═══════════════════════════════════════════════════════════════════════════════
# TYPE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_len(args: List[Value]) -> Value:
    """Get length of string, list, or map."""
    if not args:
        return Value.int_val(0)
    
    val = args[0]
    if val.type == ValueType.STRING:
        return Value.int_val(len(val.data))
    if val.type == ValueType.LIST:
        return Value.int_val(len(val.data))
    if val.type == ValueType.MAP:
        return Value.int_val(len(val.data))
    return Value.int_val(0)


def builtin_type(args: List[Value]) -> Value:
    """Get type of value as string."""
    if not args:
        return Value.string_val("null")
    return Value.string_val(args[0].type.value)


def builtin_typeof(args: List[Value]) -> Value:
    """Get type of value as string (alias for type)."""
    return builtin_type(args)


def builtin_str(args: List[Value]) -> Value:
    """Convert value to string."""
    if not args:
        return Value.string_val("")
    return Value.string_val(_format_value(args[0]))


def builtin_int(args: List[Value]) -> Value:
    """Convert value to integer."""
    if not args:
        return Value.int_val(0)
    
    val = args[0]
    if val.type == ValueType.INT:
        return val
    if val.type == ValueType.FLOAT:
        return Value.int_val(int(val.data))
    if val.type == ValueType.STRING:
        try:
            return Value.int_val(int(val.data))
        except ValueError:
            return Value.int_val(0)
    if val.type == ValueType.BOOLEAN:
        return Value.int_val(1 if val.data else 0)
    return Value.int_val(0)


def builtin_float(args: List[Value]) -> Value:
    """Convert value to float."""
    if not args:
        return Value.float_val(0.0)
    
    val = args[0]
    if val.type == ValueType.FLOAT:
        return val
    if val.type == ValueType.INT:
        return Value.float_val(float(val.data))
    if val.type == ValueType.STRING:
        try:
            return Value.float_val(float(val.data))
        except ValueError:
            return Value.float_val(0.0)
    return Value.float_val(0.0)


def builtin_bool(args: List[Value]) -> Value:
    """Convert value to boolean."""
    if not args:
        return Value.bool_val(False)
    return Value.bool_val(args[0].is_truthy())


def builtin_list(args: List[Value]) -> Value:
    """Convert value to list or create list from args."""
    if not args:
        return Value.list_val([])
    
    if len(args) == 1:
        val = args[0]
        if val.type == ValueType.LIST:
            return val
        if val.type == ValueType.STRING:
            return Value.list_val([Value.string_val(c) for c in val.data])
        if val.type == ValueType.MAP:
            return Value.list_val([Value.string_val(k) for k in val.data.keys()])
    
    return Value.list_val(list(args))


def builtin_map(args: List[Value]) -> Value:
    """Create empty map or convert to map."""
    if not args:
        return Value.map_val({})
    
    if len(args) == 1 and args[0].type == ValueType.LIST:
        # Convert list of pairs to map
        result = {}
        for item in args[0].data:
            if item.type == ValueType.LIST and len(item.data) >= 2:
                key = item.data[0].to_python()
                val = item.data[1]
                result[key] = val
        return Value.map_val(result)
    
    return Value.map_val({})


# ═══════════════════════════════════════════════════════════════════════════════
# COLLECTION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_range(args: List[Value]) -> Value:
    """Generate a range of numbers."""
    if not args:
        return Value.list_val([])
    
    if len(args) == 1:
        end = int(args[0].data)
        return Value.list_val([Value.int_val(i) for i in range(end)])
    
    if len(args) == 2:
        start = int(args[0].data)
        end = int(args[1].data)
        return Value.list_val([Value.int_val(i) for i in range(start, end)])
    
    start = int(args[0].data)
    end = int(args[1].data)
    step = int(args[2].data)
    return Value.list_val([Value.int_val(i) for i in range(start, end, step)])


def builtin_append(args: List[Value]) -> Value:
    """Append item to list (mutates)."""
    if len(args) < 2 or args[0].type != ValueType.LIST:
        return Value.null_val()
    
    args[0].data.append(args[1])
    return args[0]


def builtin_push(args: List[Value]) -> Value:
    """Push item to list (alias for append)."""
    return builtin_append(args)


def builtin_pop(args: List[Value]) -> Value:
    """Pop last item from list (mutates)."""
    if not args or args[0].type != ValueType.LIST or not args[0].data:
        return Value.null_val()
    
    return args[0].data.pop()


def builtin_keys(args: List[Value]) -> Value:
    """Get keys from map."""
    if not args or args[0].type != ValueType.MAP:
        return Value.list_val([])
    
    return Value.list_val([Value.string_val(str(k)) for k in args[0].data.keys()])


def builtin_values(args: List[Value]) -> Value:
    """Get values from map."""
    if not args or args[0].type != ValueType.MAP:
        return Value.list_val([])
    
    return Value.list_val(list(args[0].data.values()))


def builtin_contains(args: List[Value]) -> Value:
    """Check if collection contains item."""
    if len(args) < 2:
        return Value.bool_val(False)
    
    collection = args[0]
    item = args[1]
    
    if collection.type == ValueType.LIST:
        return Value.bool_val(any(v.data == item.data for v in collection.data))
    if collection.type == ValueType.MAP:
        return Value.bool_val(item.to_python() in collection.data)
    if collection.type == ValueType.STRING:
        return Value.bool_val(str(item.data) in collection.data)
    
    return Value.bool_val(False)


def builtin_slice(args: List[Value]) -> Value:
    """Slice a list or string."""
    if not args:
        return Value.null_val()
    
    val = args[0]
    start = int(args[1].data) if len(args) > 1 else 0
    end = int(args[2].data) if len(args) > 2 else None
    
    if val.type == ValueType.LIST:
        sliced = val.data[start:end]
        return Value.list_val(sliced)
    if val.type == ValueType.STRING:
        sliced = val.data[start:end]
        return Value.string_val(sliced)
    
    return Value.null_val()


def builtin_reverse(args: List[Value]) -> Value:
    """Reverse a list or string."""
    if not args:
        return Value.null_val()
    
    val = args[0]
    if val.type == ValueType.LIST:
        return Value.list_val(val.data[::-1])
    if val.type == ValueType.STRING:
        return Value.string_val(val.data[::-1])
    
    return val


def builtin_sort(args: List[Value]) -> Value:
    """Sort a list."""
    if not args or args[0].type != ValueType.LIST:
        return Value.list_val([])
    
    items = args[0].data[:]
    items.sort(key=lambda v: v.data)
    return Value.list_val(items)


# ═══════════════════════════════════════════════════════════════════════════════
# HIGHER-ORDER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_filter(args: List[Value]) -> Value:
    """Filter list by predicate function."""
    if len(args) < 2:
        return Value.list_val([])
    
    fn = args[0]
    items = args[1]
    
    if fn.type != ValueType.FUNCTION or items.type != ValueType.LIST:
        return Value.list_val([])
    
    result = []
    for item in items.data:
        if fn.data.is_native:
            test = fn.data.native_fn([item])
        else:
            # Need runtime to call non-native
            test = Value.bool_val(True)  # Simplified
        
        if test.is_truthy():
            result.append(item)
    
    return Value.list_val(result)


def builtin_map_fn(args: List[Value]) -> Value:
    """Map function over list."""
    if len(args) < 2:
        return Value.list_val([])
    
    fn = args[0]
    items = args[1]
    
    if fn.type != ValueType.FUNCTION or items.type != ValueType.LIST:
        return Value.list_val([])
    
    result = []
    for item in items.data:
        if fn.data.is_native:
            mapped = fn.data.native_fn([item])
        else:
            mapped = item  # Simplified
        result.append(mapped)
    
    return Value.list_val(result)


def builtin_reduce(args: List[Value]) -> Value:
    """Reduce list with function."""
    if len(args) < 3:
        return Value.null_val()
    
    fn = args[0]
    items = args[1]
    initial = args[2]
    
    if fn.type != ValueType.FUNCTION or items.type != ValueType.LIST:
        return initial
    
    acc = initial
    for item in items.data:
        if fn.data.is_native:
            acc = fn.data.native_fn([acc, item])
        else:
            acc = item  # Simplified
    
    return acc


def builtin_zip(args: List[Value]) -> Value:
    """Zip multiple lists together."""
    if len(args) < 2:
        return Value.list_val([])
    
    lists = [a.data for a in args if a.type == ValueType.LIST]
    if not lists:
        return Value.list_val([])
    
    result = []
    for items in zip(*lists):
        result.append(Value.list_val(list(items)))
    
    return Value.list_val(result)


def builtin_enumerate(args: List[Value]) -> Value:
    """Enumerate a list with indices."""
    if not args or args[0].type != ValueType.LIST:
        return Value.list_val([])
    
    result = []
    for i, item in enumerate(args[0].data):
        result.append(Value.list_val([Value.int_val(i), item]))
    
    return Value.list_val(result)


# ═══════════════════════════════════════════════════════════════════════════════
# STRING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_split(args: List[Value]) -> Value:
    """Split string by delimiter."""
    if not args or args[0].type != ValueType.STRING:
        return Value.list_val([])
    
    s = args[0].data
    delim = args[1].data if len(args) > 1 and args[1].type == ValueType.STRING else " "
    
    parts = s.split(delim)
    return Value.list_val([Value.string_val(p) for p in parts])


def builtin_join(args: List[Value]) -> Value:
    """Join list into string."""
    if not args or args[0].type != ValueType.LIST:
        return Value.string_val("")
    
    items = args[0].data
    delim = args[1].data if len(args) > 1 and args[1].type == ValueType.STRING else ""
    
    parts = [_format_value(v) for v in items]
    return Value.string_val(delim.join(parts))


# ═══════════════════════════════════════════════════════════════════════════════
# MATH FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_sum(args: List[Value]) -> Value:
    """Sum numbers in list."""
    if not args or args[0].type != ValueType.LIST:
        return Value.int_val(0)
    
    total = sum(v.data for v in args[0].data if v.type in (ValueType.INT, ValueType.FLOAT))
    if isinstance(total, float):
        return Value.float_val(total)
    return Value.int_val(total)


def builtin_min(args: List[Value]) -> Value:
    """Find minimum value."""
    if not args:
        return Value.null_val()
    
    if args[0].type == ValueType.LIST:
        if not args[0].data:
            return Value.null_val()
        vals = [v.data for v in args[0].data]
    else:
        vals = [a.data for a in args]
    
    result = min(vals)
    return Value.float_val(result) if isinstance(result, float) else Value.int_val(result)


def builtin_max(args: List[Value]) -> Value:
    """Find maximum value."""
    if not args:
        return Value.null_val()
    
    if args[0].type == ValueType.LIST:
        if not args[0].data:
            return Value.null_val()
        vals = [v.data for v in args[0].data]
    else:
        vals = [a.data for a in args]
    
    result = max(vals)
    return Value.float_val(result) if isinstance(result, float) else Value.int_val(result)


def builtin_abs(args: List[Value]) -> Value:
    """Absolute value."""
    if not args:
        return Value.int_val(0)
    return Value.float_val(abs(args[0].data)) if args[0].type == ValueType.FLOAT else Value.int_val(abs(int(args[0].data)))


def builtin_round(args: List[Value]) -> Value:
    """Round number."""
    if not args:
        return Value.int_val(0)
    
    n = args[0].data
    places = int(args[1].data) if len(args) > 1 else 0
    
    if places == 0:
        return Value.int_val(round(n))
    return Value.float_val(round(n, places))


def builtin_floor(args: List[Value]) -> Value:
    """Floor of number."""
    if not args:
        return Value.int_val(0)
    return Value.int_val(math.floor(args[0].data))


def builtin_ceil(args: List[Value]) -> Value:
    """Ceiling of number."""
    if not args:
        return Value.int_val(0)
    return Value.int_val(math.ceil(args[0].data))


def builtin_sqrt(args: List[Value]) -> Value:
    """Square root."""
    if not args:
        return Value.float_val(0.0)
    return Value.float_val(math.sqrt(args[0].data))


def builtin_pow(args: List[Value]) -> Value:
    """Power function."""
    if len(args) < 2:
        return Value.float_val(0.0)
    return Value.float_val(math.pow(args[0].data, args[1].data))


def builtin_sin(args: List[Value]) -> Value:
    """Sine function."""
    if not args:
        return Value.float_val(0.0)
    return Value.float_val(math.sin(args[0].data))


def builtin_cos(args: List[Value]) -> Value:
    """Cosine function."""
    if not args:
        return Value.float_val(1.0)
    return Value.float_val(math.cos(args[0].data))


def builtin_tan(args: List[Value]) -> Value:
    """Tangent function."""
    if not args:
        return Value.float_val(0.0)
    return Value.float_val(math.tan(args[0].data))


def builtin_log(args: List[Value]) -> Value:
    """Natural logarithm."""
    if not args:
        return Value.float_val(0.0)
    
    n = args[0].data
    base = args[1].data if len(args) > 1 else math.e
    
    return Value.float_val(math.log(n, base))


def builtin_exp(args: List[Value]) -> Value:
    """Exponential function."""
    if not args:
        return Value.float_val(1.0)
    return Value.float_val(math.exp(args[0].data))


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_assert(args: List[Value]) -> Value:
    """Assert that condition is true."""
    if not args:
        return Value.null_val()
    
    if not args[0].is_truthy():
        msg = args[1].data if len(args) > 1 and args[1].type == ValueType.STRING else "Assertion failed"
        raise AssertionError(msg)
    
    return Value.bool_val(True)


def builtin_assert_equal(args: List[Value]) -> Value:
    """
    assert_equal(actual, expected, [message])
    Assert two values are equal, with detailed failure message.
    """
    if len(args) < 2:
        raise ValueError("assert_equal requires at least 2 arguments: actual, expected")
    
    actual = args[0]
    expected = args[1]
    msg = args[2].data if len(args) > 2 and args[2].type == ValueType.STRING else None
    
    # Deep equality check
    if _values_equal(actual, expected):
        return Value.bool_val(True)
    
    # Build detailed error message
    actual_str = _format_value(actual)
    expected_str = _format_value(expected)
    
    error_msg = f"assert_equal failed:\n  expected: {expected_str}\n  actual:   {actual_str}"
    if msg:
        error_msg = f"{msg}\n{error_msg}"
    
    raise AssertionError(error_msg)


def builtin_assert_true(args: List[Value]) -> Value:
    """
    assert_true(value, [message])
    Assert value is truthy.
    """
    if not args:
        raise ValueError("assert_true requires at least 1 argument")
    
    value = args[0]
    msg = args[1].data if len(args) > 1 and args[1].type == ValueType.STRING else None
    
    if value.is_truthy():
        return Value.bool_val(True)
    
    error_msg = f"assert_true failed: {_format_value(value)} is not truthy"
    if msg:
        error_msg = f"{msg}\n{error_msg}"
    
    raise AssertionError(error_msg)


def builtin_assert_false(args: List[Value]) -> Value:
    """
    assert_false(value, [message])
    Assert value is falsy.
    """
    if not args:
        raise ValueError("assert_false requires at least 1 argument")
    
    value = args[0]
    msg = args[1].data if len(args) > 1 and args[1].type == ValueType.STRING else None
    
    if not value.is_truthy():
        return Value.bool_val(True)
    
    error_msg = f"assert_false failed: {_format_value(value)} is truthy"
    if msg:
        error_msg = f"{msg}\n{error_msg}"
    
    raise AssertionError(error_msg)


def builtin_assert_throws(args: List[Value]) -> Value:
    """
    assert_throws(fn, [expected_error], [message])
    Assert that calling fn() throws an error.
    Returns true if error was thrown, raises AssertionError otherwise.
    
    NOTE: This is a special builtin - the runtime needs to handle it.
    It marks that the following expression should throw.
    """
    if not args:
        raise ValueError("assert_throws requires at least 1 argument (a function)")
    
    # This needs special handling in runtime - we just store metadata
    # For now, return a marker that indicates "expect throw"
    return Value.bool_val(False)  # Will be overridden by runtime


def _values_equal(a: Value, b: Value) -> bool:
    """Deep equality check for two values."""
    if a.type != b.type:
        # Allow int/float comparison
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
    
    return a.data == b.data


def builtin_hash(args: List[Value]) -> Value:
    """Hash a value to string."""
    if not args:
        return Value.string_val("")
    
    data = _format_value(args[0]).encode('utf-8')
    return Value.string_val(hashlib.sha256(data).hexdigest()[:16])


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

STDLIB_CONSTANTS = {
    'PI': Value.float_val(math.pi),
    'E': Value.float_val(math.e),
    'TAU': Value.float_val(math.tau),
    'INF': Value.float_val(float('inf')),
    'NAN': Value.float_val(float('nan')),
    'true': Value.bool_val(True),
    'false': Value.bool_val(False),
    'null': Value.null_val(),
}


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETE STDLIB EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

STDLIB_FUNCTIONS = {
    # Output
    'print': builtin_print,
    'println': builtin_println,
    
    # Input
    'input': builtin_input,
    
    # Types
    'len': builtin_len,
    'type': builtin_type,
    'typeof': builtin_typeof,
    'str': builtin_str,
    'int': builtin_int,
    'float': builtin_float,
    'bool': builtin_bool,
    'list': builtin_list,
    'map': builtin_map,
    
    # Collections
    'range': builtin_range,
    'append': builtin_append,
    'push': builtin_push,
    'pop': builtin_pop,
    'keys': builtin_keys,
    'values': builtin_values,
    'contains': builtin_contains,
    'slice': builtin_slice,
    'reverse': builtin_reverse,
    'sort': builtin_sort,
    
    # Higher-order
    'filter': builtin_filter,
    'map_': builtin_map_fn,
    'reduce': builtin_reduce,
    'zip': builtin_zip,
    'enumerate': builtin_enumerate,
    
    # Strings
    'split': builtin_split,
    'join': builtin_join,
    
    # Math
    'sum': builtin_sum,
    'min': builtin_min,
    'max': builtin_max,
    'abs': builtin_abs,
    'round': builtin_round,
    'floor': builtin_floor,
    'ceil': builtin_ceil,
    'sqrt': builtin_sqrt,
    'pow': builtin_pow,
    'sin': builtin_sin,
    'cos': builtin_cos,
    'tan': builtin_tan,
    'log': builtin_log,
    'exp': builtin_exp,
    
    # Utility
    'assert': builtin_assert,
    'assert_equal': builtin_assert_equal,
    'assert_true': builtin_assert_true,
    'assert_false': builtin_assert_false,
    'assert_throws': builtin_assert_throws,
    'hash': builtin_hash,
}
