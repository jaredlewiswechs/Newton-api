"""
TinyTalk Optional Type Checker

Validates type annotations at runtime when present.
Annotations are always optional — code without annotations runs unchanged.

Type annotations appear in:
  - let declarations:   let x: int = 42
  - fn parameters:      fn add(a: int, b: int): int { ... }
  - fn return types:    fn name() -> str { ... }  or  fn name(): str { ... }

Type names: int, float, str, bool, list, map, any, void
Parameterized: list[int], map[str, int]
Optional: ?int (allows null)
"""

from typing import Optional

from .types import Value, ValueType


# Map from annotation strings to ValueType(s)
_TYPE_MAP = {
    "int": {ValueType.INT},
    "float": {ValueType.FLOAT},
    "str": {ValueType.STRING},
    "string": {ValueType.STRING},
    "bool": {ValueType.BOOLEAN},
    "boolean": {ValueType.BOOLEAN},
    "list": {ValueType.LIST},
    "map": {ValueType.MAP},
    "any": None,  # any matches everything
    "void": {ValueType.NULL},
    "null": {ValueType.NULL},
    "num": {ValueType.INT, ValueType.FLOAT},
    "number": {ValueType.INT, ValueType.FLOAT},
}


def check_type(value: Value, annotation: Optional[str], context: str = "") -> Optional[str]:
    """Check if a value matches a type annotation.

    Returns None if the check passes, or an error message string if it fails.
    If annotation is None or "any", always passes.
    """
    if annotation is None:
        return None

    annotation = annotation.strip()

    if annotation == "any":
        return None

    # Optional type: ?type allows null
    if annotation.startswith("?"):
        if value.type == ValueType.NULL:
            return None
        annotation = annotation[1:]

    # Parameterized types: list[int], map[str, int]
    if "[" in annotation:
        base = annotation[:annotation.index("[")]
        # Just check the base type — deep element checking would
        # require iterating all elements which is expensive.
        base_types = _TYPE_MAP.get(base.lower())
        if base_types is None:
            return None  # unknown base → pass
        if value.type not in base_types:
            ctx = f" for {context}" if context else ""
            return f"Type mismatch{ctx}: expected {annotation}, got {value.type.value}"
        return None

    # Simple type
    expected_types = _TYPE_MAP.get(annotation.lower())
    if expected_types is None:
        # Unknown type name — could be a struct name, pass through
        return None

    if value.type in expected_types:
        return None

    # Special case: int is compatible with float annotations
    if annotation.lower() == "float" and value.type == ValueType.INT:
        return None

    ctx = f" for {context}" if context else ""
    return f"Type mismatch{ctx}: expected {annotation}, got {value.type.value}"


def check_return_type(value: Value, annotation: Optional[str], fn_name: str) -> Optional[str]:
    """Check if a function's return value matches its declared return type."""
    if annotation is None:
        return None
    return check_type(value, annotation, context=f"return value of '{fn_name}'")


def check_param_type(value: Value, annotation: Optional[str], param_name: str, fn_name: str) -> Optional[str]:
    """Check if a function argument matches the parameter's type annotation."""
    if annotation is None:
        return None
    return check_type(value, annotation, context=f"parameter '{param_name}' of '{fn_name}'")
