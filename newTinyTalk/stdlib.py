"""
TinyTalk Standard Library
Built-in functions available in every program.
"""

from typing import List
import math
import hashlib
import csv
import json
import io
import urllib.request
import urllib.error
from datetime import datetime, timedelta

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
# File I/O: CSV
# ---------------------------------------------------------------------------

def builtin_read_csv(args: List[Value]) -> Value:
    """read_csv(path) -> list of maps.  Each row becomes a {header: value} map."""
    if not args or args[0].type != ValueType.STRING:
        raise ValueError("read_csv requires a file path string")
    path = args[0].data
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                m = {}
                for k, v in row.items():
                    m[k] = _auto_type(v)
                rows.append(Value.map_val(m))
            return Value.list_val(rows)
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except Exception as e:
        raise ValueError(f"read_csv error: {e}")


def builtin_write_csv(args: List[Value]) -> Value:
    """write_csv(data, path) -> null.  data is a list of maps."""
    if len(args) < 2:
        raise ValueError("write_csv requires (data, path)")
    data, path = args[0], args[1]
    if data.type != ValueType.LIST or path.type != ValueType.STRING:
        raise ValueError("write_csv requires (list_of_maps, path_string)")
    rows = data.data
    if not rows:
        with open(path.data, "w", encoding="utf-8") as f:
            pass
        return Value.null_val()
    first = rows[0]
    if first.type != ValueType.MAP:
        raise ValueError("write_csv: each row must be a map")
    headers = list(first.data.keys())
    with open(path.data, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: format_value(v) for k, v in row.data.items()})
    return Value.null_val()


def _auto_type(s: str) -> Value:
    """Convert a CSV string cell to the best-fit TinyTalk value."""
    if s is None or s == "":
        return Value.null_val()
    if s.lower() == "true":
        return Value.bool_val(True)
    if s.lower() == "false":
        return Value.bool_val(False)
    try:
        if "." in s or "e" in s.lower():
            return Value.float_val(float(s))
        return Value.int_val(int(s))
    except ValueError:
        return Value.string_val(s)


# ---------------------------------------------------------------------------
# File I/O: JSON
# ---------------------------------------------------------------------------

def builtin_read_json(args: List[Value]) -> Value:
    """read_json(path) -> value.  Parses a JSON file into TinyTalk values."""
    if not args or args[0].type != ValueType.STRING:
        raise ValueError("read_json requires a file path string")
    path = args[0].data
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return _python_to_value(data)
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def builtin_write_json(args: List[Value]) -> Value:
    """write_json(data, path) -> null.  Writes TinyTalk value as JSON."""
    if len(args) < 2:
        raise ValueError("write_json requires (data, path)")
    data, path = args[0], args[1]
    if path.type != ValueType.STRING:
        raise ValueError("write_json: second argument must be a path string")
    py_data = data.to_python()
    with open(path.data, "w", encoding="utf-8") as f:
        json.dump(py_data, f, indent=2, default=str)
    return Value.null_val()


def builtin_parse_json(args: List[Value]) -> Value:
    """parse_json(string) -> value.  Parses a JSON string into TinyTalk values."""
    if not args or args[0].type != ValueType.STRING:
        raise ValueError("parse_json requires a JSON string")
    try:
        data = json.loads(args[0].data)
        return _python_to_value(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def builtin_to_json(args: List[Value]) -> Value:
    """to_json(value) -> string.  Serializes a TinyTalk value to a JSON string."""
    if not args:
        return Value.string_val("null")
    return Value.string_val(json.dumps(args[0].to_python(), default=str))


def _python_to_value(obj) -> Value:
    """Convert a Python object (from json.load) to a TinyTalk Value."""
    if obj is None:
        return Value.null_val()
    if isinstance(obj, bool):
        return Value.bool_val(obj)
    if isinstance(obj, int):
        return Value.int_val(obj)
    if isinstance(obj, float):
        return Value.float_val(obj)
    if isinstance(obj, str):
        return Value.string_val(obj)
    if isinstance(obj, list):
        return Value.list_val([_python_to_value(x) for x in obj])
    if isinstance(obj, dict):
        return Value.map_val({k: _python_to_value(v) for k, v in obj.items()})
    return Value.string_val(str(obj))


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def builtin_http_get(args: List[Value]) -> Value:
    """http_get(url) -> value.  GET a URL and parse the response as JSON."""
    if not args or args[0].type != ValueType.STRING:
        raise ValueError("http_get requires a URL string")
    url = args[0].data
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "TinyTalk/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
        try:
            return _python_to_value(json.loads(body))
        except json.JSONDecodeError:
            return Value.string_val(body)
    except urllib.error.HTTPError as e:
        raise ValueError(f"HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise ValueError(f"HTTP error: {e.reason}")
    except Exception as e:
        raise ValueError(f"http_get failed: {e}")


# ---------------------------------------------------------------------------
# Date / Time
# ---------------------------------------------------------------------------

_DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
]


def builtin_date_now(args: List[Value]) -> Value:
    """date_now() -> string.  Current date-time as ISO string."""
    return Value.string_val(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def builtin_date_parse(args: List[Value]) -> Value:
    """date_parse(string) -> string.  Parse a date string to normalized ISO format."""
    if not args or args[0].type != ValueType.STRING:
        raise ValueError("date_parse requires a date string")
    s = args[0].data.strip()
    for fmt in _DATE_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            return Value.string_val(dt.strftime("%Y-%m-%d %H:%M:%S"))
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: '{s}'")


def builtin_date_format(args: List[Value]) -> Value:
    """date_format(date_str, fmt) -> string.  Format a date using strftime codes."""
    if len(args) < 2:
        raise ValueError("date_format requires (date_string, format_string)")
    dt = _parse_date(args[0].data)
    return Value.string_val(dt.strftime(args[1].data))


def builtin_date_floor(args: List[Value]) -> Value:
    """date_floor(date_str, unit) -> string.  Truncate to start of unit.
    Units: "day", "week", "month", "year", "hour"."""
    if len(args) < 2:
        raise ValueError("date_floor requires (date_string, unit)")
    dt = _parse_date(args[0].data)
    unit = args[1].data if args[1].type == ValueType.STRING else "day"
    if unit == "day":
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif unit == "week":
        dt = dt - timedelta(days=dt.weekday())
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif unit == "month":
        dt = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif unit == "year":
        dt = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif unit == "hour":
        dt = dt.replace(minute=0, second=0, microsecond=0)
    else:
        raise ValueError(f"Unknown date unit: '{unit}'")
    return Value.string_val(dt.strftime("%Y-%m-%d %H:%M:%S"))


def builtin_date_add(args: List[Value]) -> Value:
    """date_add(date_str, amount, unit) -> string.  Add time to a date.
    Units: "days", "hours", "minutes", "seconds", "weeks"."""
    if len(args) < 3:
        raise ValueError("date_add requires (date_string, amount, unit)")
    dt = _parse_date(args[0].data)
    n = int(args[1].data)
    unit = args[2].data if args[2].type == ValueType.STRING else "days"
    if unit in ("day", "days"):
        dt += timedelta(days=n)
    elif unit in ("hour", "hours"):
        dt += timedelta(hours=n)
    elif unit in ("minute", "minutes"):
        dt += timedelta(minutes=n)
    elif unit in ("second", "seconds"):
        dt += timedelta(seconds=n)
    elif unit in ("week", "weeks"):
        dt += timedelta(weeks=n)
    else:
        raise ValueError(f"Unknown date unit: '{unit}'")
    return Value.string_val(dt.strftime("%Y-%m-%d %H:%M:%S"))


def builtin_date_diff(args: List[Value]) -> Value:
    """date_diff(date1, date2, unit) -> number.  Difference between two dates.
    Units: "days", "hours", "minutes", "seconds".  Returns date1 - date2."""
    if len(args) < 2:
        raise ValueError("date_diff requires (date1, date2[, unit])")
    dt1 = _parse_date(args[0].data)
    dt2 = _parse_date(args[1].data)
    unit = args[2].data if len(args) > 2 and args[2].type == ValueType.STRING else "days"
    delta = dt1 - dt2
    total_seconds = delta.total_seconds()
    if unit in ("day", "days"):
        return Value.float_val(total_seconds / 86400)
    if unit in ("hour", "hours"):
        return Value.float_val(total_seconds / 3600)
    if unit in ("minute", "minutes"):
        return Value.float_val(total_seconds / 60)
    if unit in ("second", "seconds"):
        return Value.float_val(total_seconds)
    raise ValueError(f"Unknown date unit: '{unit}'")


def _parse_date(s: str) -> datetime:
    """Parse a date string trying multiple formats."""
    s = s.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: '{s}'")


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
    # File I/O
    "read_csv": builtin_read_csv,
    "write_csv": builtin_write_csv,
    "read_json": builtin_read_json,
    "write_json": builtin_write_json,
    "parse_json": builtin_parse_json,
    "to_json": builtin_to_json,
    # HTTP
    "http_get": builtin_http_get,
    # Date/Time
    "date_now": builtin_date_now,
    "date_parse": builtin_date_parse,
    "date_format": builtin_date_format,
    "date_floor": builtin_date_floor,
    "date_add": builtin_date_add,
    "date_diff": builtin_date_diff,
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
