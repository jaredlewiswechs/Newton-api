"""
TinyTalk → Python/pandas Transpiler

Walks the TinyTalk AST and emits equivalent Python code.
Step chains map to pandas operations when operating on DataFrames,
or to plain Python list comprehensions for simple data.

Usage:
    from newTinyTalk.transpiler import transpile, transpile_pandas

    # Plain Python output
    python_code = transpile('let x = [1,2,3] _filter((n) => n > 1) _sum')

    # Pandas-flavored output (DataFrames for list-of-maps)
    pandas_code = transpile_pandas('data _filter((r) => r["age"] > 30) _sort')
"""

from .ast_nodes import (
    ASTNode, Program, Literal, Identifier, BinaryOp, UnaryOp, Call, Index,
    Member, Array, MapLiteral, Lambda, Conditional, Range, Pipe, StepChain,
    StringInterp, LetStmt, ConstStmt, AssignStmt, Block, IfStmt, ForStmt,
    WhileStmt, ReturnStmt, BreakStmt, ContinueStmt, FnDecl, StructDecl,
    EnumDecl, MatchStmt, TryStmt, ThrowStmt,
)
from .lexer import Lexer
from .parser import Parser


# ---------------------------------------------------------------------------
# Built-in function mappings: TinyTalk name → Python expression template
# ---------------------------------------------------------------------------

# {0}, {1}, etc. are positional args
_BUILTIN_MAP = {
    "show": "print({args})",
    "println": "print({args})",
    "print": "print({args}, end='')",
    "len": "len({0})",
    "type": "type({0}).__name__",
    "typeof": "type({0}).__name__",
    "str": "str({0})",
    "int": "int({0})",
    "float": "float({0})",
    "bool": "bool({0})",
    "range": "list(range({args}))",
    "append": "{0}.append({1})",
    "push": "{0}.append({1})",
    "pop": "{0}.pop()",
    "keys": "list({0}.keys())",
    "values": "list({0}.values())",
    "contains": "{1} in {0}",
    "slice": "{0}[{1}:{2}]",
    "reverse": "{0}[::-1]",
    "sort": "sorted({0})",
    "abs": "abs({0})",
    "round": "round({args})",
    "floor": "math.floor({0})",
    "ceil": "math.ceil({0})",
    "sqrt": "math.sqrt({0})",
    "pow": "{0} ** {1}",
    "sin": "math.sin({0})",
    "cos": "math.cos({0})",
    "tan": "math.tan({0})",
    "log": "math.log({args})",
    "exp": "math.exp({0})",
    "sum": "sum({0})",
    "min": "min({args})",
    "max": "max({args})",
    "split": "{0}.split({1})" if True else None,
    "join": "{1}.join({0})" if True else None,
    "replace": "{0}.replace({1}, {2})",
    "trim": "{0}.strip()",
    "upcase": "{0}.upper()",
    "downcase": "{0}.lower()",
    "startswith": "{0}.startswith({1})",
    "endswith": "{0}.endswith({1})",
    "zip": "list(zip({args}))",
    "enumerate": "list(enumerate({0}))",
    "hash": "hashlib.sha256(str({0}).encode()).hexdigest()[:16]",
    "read_csv": "pd.read_csv({0}).to_dict('records')",
    "write_csv": "pd.DataFrame({0}).to_csv({1}, index=False)",
    "parse_json": "json.loads({0})",
    "to_json": "json.dumps({0})",
    "read_json": "json.load(open({0}))",
    "write_json": "json.dump({0}, open({1}, 'w'), indent=2)",
}

# Operator mappings: TinyTalk → Python
_OP_MAP = {
    "==": "==",
    "!=": "!=",
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "//": "//",
    "%": "%",
    "**": "**",
    "<": "<",
    ">": ">",
    "<=": "<=",
    ">=": ">=",
    "and": "and",
    "or": "or",
    "is": "==",
    "isnt": "!=",
    "&": "&",
    "|": "|",
    "^": "^",
    "<<": "<<",
    ">>": ">>",
}


class PythonTranspiler:
    """Transpiles TinyTalk AST to plain Python code."""

    def __init__(self, pandas_mode: bool = False):
        self.pandas_mode = pandas_mode
        self._indent = 0
        self._lines: list[str] = []
        self._imports: set[str] = set()

    def transpile(self, source: str) -> str:
        """Parse and transpile TinyTalk source to Python."""
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        return self.emit(ast)

    def emit(self, node: ASTNode) -> str:
        """Emit Python code from an AST."""
        self._indent = 0
        self._lines = []
        self._imports = set()

        if isinstance(node, Program):
            for stmt in node.statements:
                line = self._emit_stmt(stmt)
                if line is not None:
                    self._lines.append(line)
        else:
            self._lines.append(self._emit_expr(node))

        # Build final output with imports
        parts = []
        if self._imports:
            for imp in sorted(self._imports):
                parts.append(imp)
            parts.append("")
        parts.extend(self._lines)
        return "\n".join(parts)

    # -------------------------------------------------------------------
    # Statements
    # -------------------------------------------------------------------

    def _emit_stmt(self, node: ASTNode) -> str:
        """Emit a statement, returning the line(s) as a string."""
        indent = "    " * self._indent

        if isinstance(node, LetStmt):
            if node.value is not None:
                return f"{indent}{node.name} = {self._emit_expr(node.value)}"
            return f"{indent}{node.name} = None"

        if isinstance(node, ConstStmt):
            return f"{indent}{node.name} = {self._emit_expr(node.value)}"

        if isinstance(node, AssignStmt):
            target = self._emit_expr(node.target)
            value = self._emit_expr(node.value)
            return f"{indent}{target} {node.op} {value}"

        if isinstance(node, IfStmt):
            lines = []
            lines.append(f"{indent}if {self._emit_expr(node.condition)}:")
            lines.extend(self._emit_block_body(node.then_branch))
            for cond, body in node.elif_branches:
                lines.append(f"{indent}elif {self._emit_expr(cond)}:")
                lines.extend(self._emit_block_body(body))
            if node.else_branch:
                lines.append(f"{indent}else:")
                lines.extend(self._emit_block_body(node.else_branch))
            return "\n".join(lines)

        if isinstance(node, ForStmt):
            lines = []
            lines.append(f"{indent}for {node.var} in {self._emit_expr(node.iterable)}:")
            lines.extend(self._emit_block_body(node.body))
            return "\n".join(lines)

        if isinstance(node, WhileStmt):
            lines = []
            lines.append(f"{indent}while {self._emit_expr(node.condition)}:")
            lines.extend(self._emit_block_body(node.body))
            return "\n".join(lines)

        if isinstance(node, ReturnStmt):
            if node.value:
                return f"{indent}return {self._emit_expr(node.value)}"
            return f"{indent}return"

        if isinstance(node, BreakStmt):
            return f"{indent}break"

        if isinstance(node, ContinueStmt):
            return f"{indent}continue"

        if isinstance(node, FnDecl):
            params = ", ".join(p[0] for p in node.params)
            lines = [f"{indent}def {node.name}({params}):"]
            lines.extend(self._emit_block_body(node.body))
            return "\n".join(lines)

        if isinstance(node, Block):
            stmts = []
            for s in node.statements:
                line = self._emit_stmt(s)
                if line is not None:
                    stmts.append(line)
            return "\n".join(stmts) if stmts else f"{indent}pass"

        if isinstance(node, TryStmt):
            lines = [f"{indent}try:"]
            lines.extend(self._emit_block_body(node.body))
            if node.catch_body:
                var = node.catch_var or "e"
                lines.append(f"{indent}except Exception as {var}:")
                lines.extend(self._emit_block_body(node.catch_body))
            return "\n".join(lines)

        if isinstance(node, ThrowStmt):
            return f"{indent}raise Exception({self._emit_expr(node.value)})"

        if isinstance(node, MatchStmt):
            lines = []
            val_expr = self._emit_expr(node.value)
            lines.append(f"{indent}_match_val = {val_expr}")
            for i, (pattern, body) in enumerate(node.cases):
                kw = "if" if i == 0 else "elif"
                lines.append(f"{indent}{kw} _match_val == {self._emit_expr(pattern)}:")
                lines.extend(self._emit_block_body(body))
            return "\n".join(lines)

        # Expression statement
        return f"{indent}{self._emit_expr(node)}"

    def _emit_block_body(self, node: ASTNode) -> list[str]:
        """Emit the body of a block, indented one level."""
        self._indent += 1
        indent = "    " * self._indent
        if isinstance(node, Block):
            lines = []
            for s in node.statements:
                line = self._emit_stmt(s)
                if line is not None:
                    lines.append(line)
            if not lines:
                lines.append(f"{indent}pass")
        else:
            line = self._emit_stmt(node)
            lines = [line] if line is not None else [f"{indent}pass"]
        self._indent -= 1
        return lines

    # -------------------------------------------------------------------
    # Expressions
    # -------------------------------------------------------------------

    def _emit_expr(self, node: ASTNode) -> str:
        if isinstance(node, Literal):
            return self._emit_literal(node)

        if isinstance(node, Identifier):
            # Map TinyTalk constants to Python
            name_map = {"true": "True", "false": "False", "null": "None",
                        "PI": "math.pi", "E": "math.e", "TAU": "math.tau",
                        "INF": "float('inf')"}
            if node.name in name_map:
                if "math." in name_map[node.name]:
                    self._imports.add("import math")
                return name_map[node.name]
            return node.name

        if isinstance(node, BinaryOp):
            return self._emit_binary(node)

        if isinstance(node, UnaryOp):
            return self._emit_unary(node)

        if isinstance(node, Call):
            return self._emit_call(node)

        if isinstance(node, Index):
            return f"{self._emit_expr(node.obj)}[{self._emit_expr(node.index)}]"

        if isinstance(node, Member):
            return f"{self._emit_expr(node.obj)}.{node.field_name}"

        if isinstance(node, Array):
            elements = ", ".join(self._emit_expr(e) for e in node.elements)
            return f"[{elements}]"

        if isinstance(node, MapLiteral):
            pairs = ", ".join(
                f"{self._emit_expr(k)}: {self._emit_expr(v)}"
                for k, v in node.pairs
            )
            return f"{{{pairs}}}"

        if isinstance(node, Lambda):
            params = ", ".join(node.params)
            body = self._emit_expr(node.body)
            return f"lambda {params}: {body}"

        if isinstance(node, Conditional):
            return (f"({self._emit_expr(node.then_expr)} "
                    f"if {self._emit_expr(node.condition)} "
                    f"else {self._emit_expr(node.else_expr)})")

        if isinstance(node, Range):
            if node.inclusive:
                return f"list(range({self._emit_expr(node.start)}, {self._emit_expr(node.end)} + 1))"
            return f"list(range({self._emit_expr(node.start)}, {self._emit_expr(node.end)}))"

        if isinstance(node, Pipe):
            return f"{self._emit_expr(node.right)}({self._emit_expr(node.left)})"

        if isinstance(node, StepChain):
            return self._emit_step_chain(node)

        if isinstance(node, StringInterp):
            return self._emit_string_interp(node)

        # Fallback
        return f"<{type(node).__name__}>"

    def _emit_literal(self, node: Literal) -> str:
        if node.value is None:
            return "None"
        if isinstance(node.value, bool):
            return "True" if node.value else "False"
        if isinstance(node.value, str):
            escaped = node.value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            return f'"{escaped}"'
        return str(node.value)

    def _emit_binary(self, node: BinaryOp) -> str:
        left = self._emit_expr(node.left)
        right = self._emit_expr(node.right)
        op = node.op

        if op == "has":
            return f"{right} in {left}"
        if op == "hasnt":
            return f"{right} not in {left}"
        if op == "isin":
            return f"{left} in {right}"
        if op == "islike":
            self._imports.add("import re")
            return f"bool(re.match({right}.replace('*', '.*'), {left}))"

        py_op = _OP_MAP.get(op, op)
        return f"({left} {py_op} {right})"

    def _emit_unary(self, node: UnaryOp) -> str:
        operand = self._emit_expr(node.operand)
        if node.op == "not":
            return f"not {operand}"
        if node.op == "~":
            return f"~{operand}"
        return f"-{operand}"

    def _emit_call(self, node: Call) -> str:
        args_strs = [self._emit_expr(a) for a in node.args]

        # Check if it's a known builtin
        if isinstance(node.callee, Identifier):
            name = node.callee.name
            if name in _BUILTIN_MAP:
                template = _BUILTIN_MAP[name]

                # Add imports as needed
                if "math." in template:
                    self._imports.add("import math")
                if "hashlib." in template:
                    self._imports.add("import hashlib")
                if "json." in template:
                    self._imports.add("import json")
                if "pd." in template:
                    self._imports.add("import pandas as pd")

                # Handle special multi-arg templates
                if name == "split":
                    if len(args_strs) == 1:
                        return f"{args_strs[0]}.split()"
                    return f"{args_strs[0]}.split({args_strs[1]})"
                if name == "join":
                    if len(args_strs) == 1:
                        return f"''.join(str(x) for x in {args_strs[0]})"
                    return f"{args_strs[1]}.join(str(x) for x in {args_strs[0]})"
                if name == "slice":
                    if len(args_strs) == 2:
                        return f"{args_strs[0]}[{args_strs[1]}:]"
                    return f"{args_strs[0]}[{args_strs[1]}:{args_strs[2]}]"
                if name == "contains":
                    return f"{args_strs[1]} in {args_strs[0]}"

                # Generic template substitution
                result = template
                for i, a in enumerate(args_strs):
                    result = result.replace(f"{{{i}}}", a)
                result = result.replace("{args}", ", ".join(args_strs))
                return result

            # assert functions
            if name == "assert":
                if len(args_strs) == 1:
                    return f"assert {args_strs[0]}"
                return f"assert {args_strs[0]}, {args_strs[1]}"
            if name == "assert_equal":
                return f"assert {args_strs[0]} == {args_strs[1]}"
            if name == "assert_true":
                return f"assert {args_strs[0]}"
            if name == "assert_false":
                return f"assert not {args_strs[0]}"

            # http_get
            if name == "http_get":
                self._imports.add("import requests")
                return f"requests.get({args_strs[0]}).json()"

            # date functions
            if name == "date_now":
                self._imports.add("from datetime import datetime")
                return 'datetime.now().strftime("%Y-%m-%d %H:%M:%S")'
            if name == "date_parse":
                self._imports.add("from dateutil.parser import parse as _dateparse")
                return f'_dateparse({args_strs[0]}).strftime("%Y-%m-%d %H:%M:%S")'
            if name == "date_format":
                self._imports.add("from dateutil.parser import parse as _dateparse")
                return f"_dateparse({args_strs[0]}).strftime({args_strs[1]})"
            if name == "date_add":
                self._imports.add("from datetime import datetime, timedelta")
                self._imports.add("from dateutil.parser import parse as _dateparse")
                return (f'(_dateparse({args_strs[0]}) + timedelta(**{{{args_strs[2]}: {args_strs[1]}}}))'
                        f'.strftime("%Y-%m-%d %H:%M:%S")')
            if name == "date_diff":
                self._imports.add("from dateutil.parser import parse as _dateparse")
                return f"(_dateparse({args_strs[0]}) - _dateparse({args_strs[1]})).total_seconds() / 86400"

        # Generic function call
        callee = self._emit_expr(node.callee)
        return f"{callee}({', '.join(args_strs)})"

    def _emit_string_interp(self, node: StringInterp) -> str:
        parts = []
        for part in node.parts:
            if isinstance(part, str):
                parts.append(part.replace("{", "{{").replace("}", "}}"))
            else:
                parts.append(f"{{{self._emit_expr(part)}}}")
        return f'f"{"".join(parts)}"'

    # -------------------------------------------------------------------
    # Step chains
    # -------------------------------------------------------------------

    def _emit_step_chain(self, node: StepChain) -> str:
        if self.pandas_mode:
            return self._emit_pandas_chain(node)
        return self._emit_python_chain(node)

    def _emit_python_chain(self, node: StepChain) -> str:
        """Emit step chain as plain Python list operations."""
        result = self._emit_expr(node.source)

        for step_name, step_args in node.steps:
            args = [self._emit_expr(a) for a in step_args]
            result = self._apply_python_step(result, step_name, args)

        return result

    def _apply_python_step(self, data: str, step: str, args: list[str]) -> str:
        """Convert a single step chain operation to Python."""

        if step == "_filter":
            fn = args[0] if args else "None"
            return f"[x for x in {data} if ({fn})(x)]"

        if step == "_map":
            fn = args[0] if args else "None"
            return f"[({fn})(x) for x in {data}]"

        if step == "_sort":
            if args:
                return f"sorted({data}, key={args[0]})"
            return f"sorted({data})"

        if step == "_sortBy":
            return f"sorted({data}, key={args[0]})"

        if step == "_reverse":
            return f"list(reversed({data}))"

        if step == "_take":
            return f"{data}[:{args[0]}]"

        if step == "_drop":
            return f"{data}[{args[0]}:]"

        if step == "_first":
            return f"({data})[0]"

        if step == "_last":
            return f"({data})[-1]"

        if step == "_unique":
            return f"list(dict.fromkeys({data}))"

        if step == "_flatten":
            return f"[item for sublist in {data} for item in (sublist if isinstance(sublist, list) else [sublist])]"

        if step == "_count":
            if args:
                return f"sum(1 for x in {data} if ({args[0]})(x))"
            return f"len({data})"

        if step == "_sum":
            return f"sum({data})"

        if step == "_avg":
            return f"(sum({data}) / len({data}))"

        if step == "_min":
            return f"min({data})"

        if step == "_max":
            return f"max({data})"

        if step == "_group":
            self._imports.add("from itertools import groupby")
            self._imports.add("from collections import defaultdict")
            fn = args[0]
            return (f"{{k: v for k, v in (lambda _d: "
                    f"(lambda _g: {{_k: list(_vs) for _k, _vs in _g.items()}})"
                    f"((lambda: ((_dd := defaultdict(list)), "
                    f"[_dd[({fn})(x)].append(x) for x in _d], _dd)[-1])()))({data})}}")

        if step == "_reduce":
            self._imports.add("from functools import reduce")
            fn = args[0]
            if len(args) > 1:
                return f"reduce({fn}, {data}, {args[1]})"
            return f"reduce({fn}, {data})"

        if step == "_each":
            return f"(lambda _l: [({args[0]})(x) for x in _l] and _l)({data})"

        if step == "_zip":
            return f"list(zip({data}, {args[0]}))"

        if step == "_chunk":
            n = args[0] if args else "2"
            return f"[{data}[i:i+{n}] for i in range(0, len({data}), {n})]"

        if step == "_join":
            # SQL-style join
            right = args[0]
            fn = args[1]
            return (f"[{{**l, **r}} for l in {data} "
                    f"for r in {right} if ({fn})(l) == ({fn})(r)]")

        if step in ("_leftJoin", "_left_join"):
            right = args[0]
            fn = args[1]
            return (f"[{{**l, **next((r for r in {right} if ({fn})(r) == ({fn})(l)), {{}})}} "
                    f"for l in {data}]")

        # dplyr-style verbs
        if step == "_select":
            if len(args) == 1:
                cols = args[0]
                return f"[{{k: row[k] for k in {cols}}} for row in {data}]"
            cols_str = ", ".join(args)
            return f"[{{k: row[k] for k in [{cols_str}]}} for row in {data}]"

        if step == "_mutate":
            fn = args[0]
            return f"[{{**row, **({fn})(row)}} for row in {data}]"

        if step == "_summarize":
            # args[0] is a map of {name: fn}
            return f"{{k: fn({data}) for k, fn in {args[0]}.items()}}"

        if step == "_rename":
            rename_map = args[0]
            return (f"[{{({rename_map}).get(k, k): v for k, v in row.items()}} "
                    f"for row in {data}]")

        if step == "_arrange":
            fn = args[0]
            if len(args) > 1:
                return f"sorted({data}, key={fn}, reverse=True)"
            return f"sorted({data}, key={fn})"

        if step in ("_distinct", "_unique"):
            if args:
                fn = args[0]
                return (f"list({{({fn})(x): x for x in {data}}}.values())")
            return f"list(dict.fromkeys({data}))"

        if step == "_slice":
            start = args[0] if args else "0"
            if len(args) > 1:
                return f"{data}[{start}:{start}+{args[1]}]"
            return f"{data}[{start}:]"

        if step == "_pull":
            col = args[0]
            return f"[row[{col}] for row in {data}]"

        if step in ("_groupBy", "_group_by"):
            return self._apply_python_step(data, "_group", args)

        if step == "_mapValues":
            fn = args[0]
            return f"{{k: ({fn})(v) for k, v in {data}.items()}}"

        if step == "_pivot":
            # _pivot(index_fn, column_fn, value_fn)
            idx_fn, col_fn, val_fn = args[0], args[1], args[2]
            return (f"(lambda _rows: (lambda _d: "
                    f"{{idx: {{col: val for _, col, val in grp}} "
                    f"for idx, grp in (lambda _items: "
                    f"{{k: [(i,c,v) for i,c,v in _items if i == k] "
                    f"for k in dict.fromkeys(i for i,_,_ in _items)}})"
                    f"([(({idx_fn})(r), ({col_fn})(r), ({val_fn})(r)) for r in _rows]).items()}}"
                    f")(_rows))({data})")

        if step == "_unpivot":
            id_cols = args[0]
            return (f"[{{**{{k: row[k] for k in {id_cols}}}, "
                    f"'variable': col, 'value': row[col]}} "
                    f"for row in {data} "
                    f"for col in row if col not in {id_cols}]")

        if step == "_window":
            n = args[0]
            fn = args[1]
            return (f"[({fn})({data}[max(0,i-{n}+1):i+1]) "
                    f"for i in range(len({data}))]")

        return f"<unknown_step:{step}>({data})"

    # -------------------------------------------------------------------
    # Pandas mode: step chains → DataFrame operations
    # -------------------------------------------------------------------

    def _emit_pandas_chain(self, node: StepChain) -> str:
        """Emit step chain as pandas DataFrame operations."""
        self._imports.add("import pandas as pd")
        source = self._emit_expr(node.source)

        # Wrap source in DataFrame if it looks like a list
        result = f"pd.DataFrame({source})"

        for step_name, step_args in node.steps:
            args = [self._emit_expr(a) for a in step_args]
            result = self._apply_pandas_step(result, step_name, args)

        return result

    def _apply_pandas_step(self, df: str, step: str, args: list[str]) -> str:
        """Convert a step chain operation to a pandas method chain."""

        if step == "_filter":
            fn = args[0] if args else "None"
            return f"{df}[{df}.apply({fn}, axis=1)]"

        if step == "_map":
            fn = args[0] if args else "None"
            return f"{df}.apply({fn}, axis=1)"

        if step in ("_sort", "_sortBy", "_arrange"):
            fn = args[0] if args else "None"
            desc = len(args) > 1 and "desc" in args[1]
            ascending = "False" if desc else "True"
            return f"{df}.sort_values(key=lambda s: s.map({fn}), ascending={ascending})"

        if step == "_reverse":
            return f"{df}.iloc[::-1].reset_index(drop=True)"

        if step == "_take":
            return f"{df}.head({args[0]})"

        if step == "_drop":
            return f"{df}.tail(-{args[0]})"

        if step == "_first":
            return f"{df}.iloc[0]"

        if step == "_last":
            return f"{df}.iloc[-1]"

        if step == "_unique":
            return f"{df}.drop_duplicates()"

        if step == "_count":
            if args:
                fn = args[0]
                return f"{df}[{df}.apply({fn}, axis=1)].shape[0]"
            return f"len({df})"

        if step == "_sum":
            return f"{df}.sum()"

        if step == "_avg":
            return f"{df}.mean()"

        if step == "_min":
            return f"{df}.min()"

        if step == "_max":
            return f"{df}.max()"

        if step in ("_group", "_groupBy", "_group_by"):
            fn = args[0]
            return f"{df}.groupby({df}.apply({fn}, axis=1))"

        if step == "_select":
            if len(args) == 1:
                return f"{df}[{args[0]}]"
            cols = ", ".join(args)
            return f"{df}[[{cols}]]"

        if step == "_mutate":
            fn = args[0]
            return f"{df}.assign(**{df}.apply({fn}, axis=1, result_type='expand'))"

        if step == "_rename":
            return f"{df}.rename(columns={args[0]})"

        if step in ("_distinct",):
            return f"{df}.drop_duplicates()"

        if step == "_pull":
            return f"{df}[{args[0]}].tolist()"

        if step == "_flatten":
            return f"{df}.explode().reset_index(drop=True)"

        if step == "_pivot":
            # _pivot(index_fn, column_fn, value_fn)
            return f"{df}.pivot_table(index={df}.apply({args[0]}, axis=1), columns={df}.apply({args[1]}, axis=1), values={df}.apply({args[2]}, axis=1))"

        if step == "_unpivot":
            return f"{df}.melt(id_vars={args[0]})"

        if step == "_window":
            n = args[0]
            fn = args[1]
            return f"{df}.rolling({n}).apply({fn})"

        if step == "_join":
            right = args[0]
            fn = args[1]
            return f"{df}.merge(pd.DataFrame({right}), on={fn})"

        if step in ("_leftJoin", "_left_join"):
            right = args[0]
            fn = args[1]
            return f"{df}.merge(pd.DataFrame({right}), on={fn}, how='left')"

        if step == "_slice":
            start = args[0] if args else "0"
            if len(args) > 1:
                return f"{df}.iloc[{start}:{start}+{args[1]}]"
            return f"{df}.iloc[{start}:]"

        if step == "_summarize":
            return f"{df}.agg({args[0]})"

        if step == "_chunk":
            n = args[0] if args else "2"
            self._imports.add("import numpy as np")
            return f"np.array_split({df}, len({df}) // {n})"

        if step == "_reduce":
            fn = args[0]
            if len(args) > 1:
                self._imports.add("from functools import reduce")
                return f"reduce({fn}, {df}.values.tolist(), {args[1]})"
            self._imports.add("from functools import reduce")
            return f"reduce({fn}, {df}.values.tolist())"

        return f"<unknown_step:{step}>({df})"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def transpile(source: str) -> str:
    """Transpile TinyTalk source to plain Python code."""
    return PythonTranspiler(pandas_mode=False).transpile(source)


def transpile_pandas(source: str) -> str:
    """Transpile TinyTalk source to Python with pandas DataFrames."""
    return PythonTranspiler(pandas_mode=True).transpile(source)
