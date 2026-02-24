"""
TinyTalk Type System
Static types + runtime values.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict, Any


# ---------------------------------------------------------------------------
# Static type representation
# ---------------------------------------------------------------------------

class TypeKind(Enum):
    INT = auto()
    FLOAT = auto()
    STR = auto()
    BOOL = auto()
    NULL = auto()
    LIST = auto()
    MAP = auto()
    TUPLE = auto()
    FUNCTION = auto()
    STRUCT = auto()
    ENUM = auto()
    ANY = auto()
    VOID = auto()
    NEVER = auto()
    UNION = auto()
    OPTIONAL = auto()


@dataclass
class TinyType:
    kind: TypeKind
    name: str = ""
    params: List["TinyType"] = field(default_factory=list)
    fields: Dict[str, "TinyType"] = field(default_factory=dict)
    variants: Dict[str, Optional["TinyType"]] = field(default_factory=dict)
    param_types: List["TinyType"] = field(default_factory=list)
    return_type: Optional["TinyType"] = None

    def __eq__(self, other):
        if not isinstance(other, TinyType):
            return False
        if self.kind != other.kind:
            return False
        if self.kind in (TypeKind.LIST, TypeKind.MAP, TypeKind.TUPLE):
            return self.params == other.params
        if self.kind == TypeKind.FUNCTION:
            return (
                self.param_types == other.param_types
                and self.return_type == other.return_type
            )
        if self.kind in (TypeKind.STRUCT, TypeKind.ENUM):
            return self.name == other.name
        return True

    def __hash__(self):
        return hash((self.kind, self.name, tuple(self.params)))

    def __repr__(self) -> str:
        simple = {
            TypeKind.INT: "int",
            TypeKind.FLOAT: "float",
            TypeKind.STR: "str",
            TypeKind.BOOL: "bool",
            TypeKind.NULL: "null",
            TypeKind.ANY: "any",
            TypeKind.VOID: "void",
            TypeKind.NEVER: "never",
        }
        if self.kind in simple:
            return simple[self.kind]
        if self.kind == TypeKind.LIST:
            inner = self.params[0] if self.params else "any"
            return f"list[{inner}]"
        if self.kind == TypeKind.MAP:
            k = self.params[0] if len(self.params) > 0 else "any"
            v = self.params[1] if len(self.params) > 1 else "any"
            return f"map[{k}, {v}]"
        if self.kind == TypeKind.FUNCTION:
            ps = ", ".join(str(t) for t in self.param_types)
            ret = str(self.return_type) if self.return_type else "void"
            return f"fn({ps}) -> {ret}"
        if self.kind in (TypeKind.STRUCT, TypeKind.ENUM):
            return self.name
        if self.kind == TypeKind.OPTIONAL:
            inner = self.params[0] if self.params else "any"
            return f"?{inner}"
        if self.kind == TypeKind.UNION:
            types = " | ".join(str(t) for t in self.params)
            return f"({types})"
        return f"<{self.kind.name}>"

    # Convenience constructors
    @classmethod
    def int_type(cls):
        return cls(TypeKind.INT)

    @classmethod
    def float_type(cls):
        return cls(TypeKind.FLOAT)

    @classmethod
    def str_type(cls):
        return cls(TypeKind.STR)

    @classmethod
    def bool_type(cls):
        return cls(TypeKind.BOOL)

    @classmethod
    def null_type(cls):
        return cls(TypeKind.NULL)

    @classmethod
    def any_type(cls):
        return cls(TypeKind.ANY)

    @classmethod
    def void_type(cls):
        return cls(TypeKind.VOID)

    @classmethod
    def list_type(cls, element_type):
        return cls(TypeKind.LIST, params=[element_type])

    @classmethod
    def map_type(cls, key_type, value_type):
        return cls(TypeKind.MAP, params=[key_type, value_type])

    @classmethod
    def function_type(cls, param_types, return_type):
        return cls(TypeKind.FUNCTION, param_types=param_types, return_type=return_type)

    @classmethod
    def optional_type(cls, inner):
        return cls(TypeKind.OPTIONAL, params=[inner])

    def is_numeric(self) -> bool:
        return self.kind in (TypeKind.INT, TypeKind.FLOAT)


# ---------------------------------------------------------------------------
# Runtime values
# ---------------------------------------------------------------------------

class ValueType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    NULL = "null"
    LIST = "list"
    MAP = "map"
    FUNCTION = "function"
    STRUCT_INSTANCE = "struct_instance"
    ENUM_VARIANT = "enum_variant"


@dataclass
class Value:
    type: ValueType
    data: Any

    # -- constructors -------------------------------------------------------

    @classmethod
    def int_val(cls, n: int) -> "Value":
        return cls(ValueType.INT, int(n))

    @classmethod
    def float_val(cls, n: float) -> "Value":
        return cls(ValueType.FLOAT, float(n))

    @classmethod
    def string_val(cls, s: str) -> "Value":
        return cls(ValueType.STRING, str(s))

    @classmethod
    def bool_val(cls, b: bool) -> "Value":
        return cls(ValueType.BOOLEAN, bool(b))

    @classmethod
    def null_val(cls) -> "Value":
        return cls(ValueType.NULL, None)

    @classmethod
    def list_val(cls, items: list) -> "Value":
        return cls(ValueType.LIST, items)

    @classmethod
    def map_val(cls, pairs: dict) -> "Value":
        return cls(ValueType.MAP, pairs)

    @classmethod
    def function_val(cls, fn) -> "Value":
        return cls(ValueType.FUNCTION, fn)

    # -- utilities ----------------------------------------------------------

    def is_truthy(self) -> bool:
        if self.type == ValueType.BOOLEAN:
            return self.data
        if self.type == ValueType.NULL:
            return False
        if self.type in (ValueType.INT, ValueType.FLOAT):
            return self.data != 0
        if self.type == ValueType.STRING:
            return len(self.data) > 0
        if self.type == ValueType.LIST:
            return len(self.data) > 0
        if self.type == ValueType.MAP:
            return len(self.data) > 0
        return True

    def to_python(self) -> Any:
        if self.type == ValueType.NULL:
            return None
        if self.type == ValueType.LIST:
            return [v.to_python() for v in self.data]
        if self.type == ValueType.MAP:
            return {k: v.to_python() for k, v in self.data.items()}
        return self.data

    def __repr__(self) -> str:
        if self.type == ValueType.NULL:
            return "null"
        if self.type == ValueType.STRING:
            return f'"{self.data}"'
        if self.type == ValueType.BOOLEAN:
            return "true" if self.data else "false"
        if self.type == ValueType.LIST:
            items = ", ".join(repr(v) for v in self.data)
            return f"[{items}]"
        if self.type == ValueType.MAP:
            pairs = ", ".join(f"{k}: {repr(v)}" for k, v in self.data.items())
            return f"{{{pairs}}}"
        if self.type == ValueType.FUNCTION:
            return "<function>"
        return str(self.data)
