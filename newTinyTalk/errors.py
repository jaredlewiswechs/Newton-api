"""
TinyTalk Error Messages That Teach

Provides helpful, educational error messages with:
  - "Did you mean?" suggestions for typos (Levenshtein distance)
  - Contextual hints for type mismatches
  - Step chain usage guidance
"""

from typing import List, Optional, Dict


# ---------------------------------------------------------------------------
# Edit distance (Levenshtein)
# ---------------------------------------------------------------------------

def _edit_distance(a: str, b: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(a) < len(b):
        return _edit_distance(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


def find_closest(name: str, candidates: List[str], max_distance: int = 2) -> Optional[str]:
    """Find the closest match to `name` from a list of candidates."""
    if not candidates:
        return None
    best = None
    best_dist = max_distance + 1
    for c in candidates:
        d = _edit_distance(name.lower(), c.lower())
        if d < best_dist:
            best_dist = d
            best = c
    return best if best_dist <= max_distance else None


# ---------------------------------------------------------------------------
# Known step chain names and their valid contexts
# ---------------------------------------------------------------------------

ALL_STEP_NAMES = [
    "_filter", "_sort", "_map", "_take", "_drop", "_first", "_last",
    "_reverse", "_unique", "_count", "_sum", "_avg", "_min", "_max",
    "_group", "_flatten", "_zip", "_chunk", "_reduce", "_sortBy",
    "_join", "_mapValues", "_each",
    "_select", "_mutate", "_summarize", "_rename", "_arrange",
    "_distinct", "_slice", "_pull", "_groupBy", "_group_by",
    "_leftJoin", "_left_join", "_pivot", "_unpivot", "_window",
]

# Steps that require a list
STEPS_REQUIRING_LIST = {
    "_filter", "_sort", "_map", "_take", "_drop", "_first", "_last",
    "_reverse", "_unique", "_count", "_sum", "_avg", "_min", "_max",
    "_flatten", "_zip", "_chunk", "_reduce", "_sortBy", "_each",
    "_select", "_mutate", "_rename", "_arrange", "_distinct",
    "_slice", "_pull", "_leftJoin", "_left_join",
    "_pivot", "_unpivot", "_window",
}

# Steps that work on maps
STEPS_REQUIRING_MAP = {"_mapValues"}

# Steps that can work on grouped maps (map of lists)
STEPS_ON_GROUPED = {"_summarize"}


# ---------------------------------------------------------------------------
# Error message builders
# ---------------------------------------------------------------------------

def undefined_variable_hint(name: str, available: List[str]) -> str:
    """Build an error message for an undefined variable with suggestions."""
    msg = f"Undefined variable '{name}'"
    suggestion = find_closest(name, available)
    if suggestion:
        msg += f". Did you mean '{suggestion}'?"
    return msg


def unknown_step_hint(step_name: str) -> str:
    """Build an error message for an unknown step chain with suggestions."""
    msg = f"Unknown step '{step_name}'"
    suggestion = find_closest(step_name, ALL_STEP_NAMES)
    if suggestion:
        msg += f". Did you mean '{suggestion}'?"
    return msg


def step_type_mismatch_hint(step_name: str, actual_type: str) -> str:
    """Build an error message when a step is used on the wrong type."""
    if step_name in STEPS_REQUIRING_MAP:
        msg = f"'{step_name}' works on maps. You have a {actual_type}"
        if actual_type == "list":
            msg += f" — try converting to a map first with _group, or use _map instead."
        return msg

    if step_name in STEPS_REQUIRING_LIST:
        msg = f"'{step_name}' works on lists. You have a {actual_type}"
        if actual_type == "map":
            msg += f" — try keys(data) {step_name} or values(data) {step_name}."
        elif actual_type == "string":
            msg += f" — try data.chars {step_name} or data.words {step_name}."
        return msg

    return f"Step '{step_name}' requires a list, got {actual_type}"


def step_args_hint(step_name: str) -> str:
    """Provide usage hints for a step chain that received wrong arguments."""
    hints: Dict[str, str] = {
        "_filter": "_filter requires a function: data _filter((x) => condition)",
        "_map": "_map requires a function: data _map((x) => transform(x))",
        "_sort": "_sort optionally takes a key function: data _sort or data _sort((x) => x.field)",
        "_reduce": "_reduce requires a function and optional initial value: data _reduce((acc, x) => acc + x, 0)",
        "_group": "_group requires a key function: data _group((x) => x.category)",
        "_groupBy": "_groupBy requires a key function: data _groupBy((x) => x.category)",
        "_join": "_join requires (right_list, key_fn): left _join(right, (r) => r.id)",
        "_leftJoin": "_leftJoin requires (right_list, key_fn): left _leftJoin(right, (r) => r.id)",
        "_left_join": "_left_join requires (right_list, key_fn): left _left_join(right, (r) => r.id)",
        "_select": '_select requires column names: data _select(["name", "age"]) or data _select("name", "age")',
        "_mutate": "_mutate requires a function returning a map: data _mutate((r) => {\"new_col\": value})",
        "_summarize": "_summarize requires a map of aggregation functions: data _summarize({\"total\": (rows) => rows _sum})",
        "_rename": "_rename requires a map of {old: new}: data _rename({\"old_name\": \"new_name\"})",
        "_arrange": "_arrange requires a key function: data _arrange((r) => r.field)",
        "_sortBy": "_sortBy requires a key function: data _sortBy((x) => x.field)",
        "_each": "_each requires a function: data _each((x) => show(x))",
        "_mapValues": "_mapValues requires a function: map_data _mapValues((v) => transform(v))",
        "_zip": "_zip requires a list: list1 _zip(list2)",
        "_chunk": "_chunk requires a size: data _chunk(3)",
        "_pivot": "_pivot requires (index_fn, column_fn, value_fn)",
        "_unpivot": "_unpivot requires a list of id column names",
        "_window": "_window requires (window_size, function)",
        "_pull": '_pull requires a column name: data _pull("column_name")',
        "_distinct": "_distinct optionally takes a key function or column list",
    }
    return hints.get(step_name, f"Check the usage of '{step_name}'")


def type_error_hint(operation: str, left_type: str, right_type: str) -> str:
    """Build a hint for type mismatches in operations."""
    msg = f"Cannot {operation} {left_type} and {right_type}"

    if operation in ("add", "+"):
        if left_type == "string" or right_type == "string":
            non_str = right_type if left_type == "string" else left_type
            msg += f". Convert to string first: value.str"
    elif operation in ("subtract", "-", "multiply", "*", "divide", "/"):
        if "string" in (left_type, right_type):
            msg += ". Arithmetic operations require numbers. Use .int or .float to convert."

    return msg


def function_call_hint(name: str, expected_args: int, actual_args: int) -> str:
    """Build a hint for wrong number of arguments."""
    if actual_args < expected_args:
        return f"'{name}' expects {expected_args} argument(s), but got {actual_args}. Missing {expected_args - actual_args} argument(s)."
    return f"'{name}' expects {expected_args} argument(s), but got {actual_args}. Too many arguments."
