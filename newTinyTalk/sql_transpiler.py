"""
TinyTalk → SQL Transpiler

Converts TinyTalk step chain pipelines to equivalent SQL queries.
This is a teaching tool: students write TinyTalk pipelines and see
the SQL equivalent, bridging data manipulation to industry SQL.

Mapping:
    _filter(pred)         →  WHERE pred
    _select("a", "b")     →  SELECT a, b
    _group(key)           →  GROUP BY key
    _summarize(aggs)      →  SELECT agg_fn(col) AS name
    _arrange(key)         →  ORDER BY key
    _arrange(key, "desc") →  ORDER BY key DESC
    _take(n)              →  LIMIT n
    _drop(n)              →  OFFSET n
    _join(right, key)     →  INNER JOIN right ON key
    _leftJoin(right, key) →  LEFT JOIN right ON key
    _distinct             →  SELECT DISTINCT
    _rename({old: new})   →  SELECT old AS new
    _sort                 →  ORDER BY (all columns)
    _count                →  SELECT COUNT(*)
    _sum                  →  SELECT SUM(col)
    _avg                  →  SELECT AVG(col)
    _min                  →  SELECT MIN(col)
    _max                  →  SELECT MAX(col)

Usage:
    from newTinyTalk.sql_transpiler import transpile_sql

    sql = transpile_sql('data _filter((r) => r["age"] > 30) _select("name", "age") _arrange((r) => r["age"])')
    # → SELECT name, age FROM data WHERE age > 30 ORDER BY age
"""

from .ast_nodes import (
    ASTNode, Program, Literal, Identifier, BinaryOp, UnaryOp, Call, Index,
    Member, Array, MapLiteral, Lambda, Conditional, Range, Pipe, StepChain,
    StringInterp, LetStmt, ConstStmt, AssignStmt, Block, IfStmt, ForStmt,
    WhileStmt, ReturnStmt, FnDecl,
)
from .lexer import Lexer
from .parser import Parser


class SQLTranspiler:
    """Transpiles TinyTalk step chain pipelines to SQL."""

    def __init__(self):
        self._table_counter = 0

    def transpile(self, source: str) -> str:
        """Parse TinyTalk source and emit SQL for step chain expressions."""
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        return self.emit(ast)

    def emit(self, node: ASTNode) -> str:
        """Emit SQL from an AST, targeting step chain pipelines."""
        if isinstance(node, Program):
            results = []
            for stmt in node.statements:
                sql = self._emit_node(stmt)
                if sql:
                    results.append(sql)
            return "\n\n".join(results)
        return self._emit_node(node)

    def _emit_node(self, node: ASTNode) -> str:
        if isinstance(node, StepChain):
            return self._emit_step_chain(node)
        if isinstance(node, LetStmt):
            if node.value and isinstance(node.value, StepChain):
                sql = self._emit_step_chain(node.value)
                return f"-- {node.name}\n{sql}"
            return ""
        if isinstance(node, ConstStmt):
            if node.value and isinstance(node.value, StepChain):
                sql = self._emit_step_chain(node.value)
                return f"-- {node.name}\n{sql}"
            return ""
        return ""

    # -------------------------------------------------------------------
    # Step chain → SQL
    # -------------------------------------------------------------------

    def _emit_step_chain(self, node: StepChain) -> str:
        """Convert a step chain pipeline into a SQL SELECT statement."""
        # Extract the source table name
        table = self._emit_source(node.source)

        # Build SQL clauses from steps
        select_cols = ["*"]
        where_clauses = []
        group_by = []
        having_clauses = []
        order_by = []
        limit = None
        offset = None
        joins = []
        distinct = False
        agg_selects = []
        renames = {}

        for step_name, step_args in node.steps:
            if step_name == "_filter":
                cond = self._lambda_to_sql(step_args[0] if step_args else None, table)
                if cond:
                    where_clauses.append(cond)

            elif step_name == "_select":
                cols = self._extract_column_names(step_args)
                if cols:
                    select_cols = cols

            elif step_name in ("_group", "_groupBy", "_group_by"):
                if step_args:
                    col = self._lambda_to_column(step_args[0])
                    if col:
                        group_by.append(col)

            elif step_name == "_summarize":
                agg_map = self._extract_agg_map(step_args)
                if agg_map:
                    agg_selects = agg_map

            elif step_name in ("_arrange", "_sortBy", "_sort"):
                if step_args:
                    col = self._lambda_to_column(step_args[0])
                    desc = (len(step_args) > 1 and
                            isinstance(step_args[1], Literal) and
                            step_args[1].value == "desc")
                    if col:
                        order_by.append(f"{col} DESC" if desc else col)
                elif step_name == "_sort":
                    order_by.append("1")  # ORDER BY first column

            elif step_name == "_take":
                if step_args and isinstance(step_args[0], Literal):
                    limit = int(step_args[0].value)

            elif step_name == "_drop":
                if step_args and isinstance(step_args[0], Literal):
                    offset = int(step_args[0].value)

            elif step_name in ("_join", "_leftJoin", "_left_join"):
                join_type = "LEFT JOIN" if "left" in step_name.lower() else "INNER JOIN"
                if len(step_args) >= 2:
                    right_table = self._emit_source(step_args[0])
                    on_col = self._lambda_to_column(step_args[1])
                    if right_table and on_col:
                        joins.append(f"{join_type} {right_table} ON {table}.{on_col} = {right_table}.{on_col}")

            elif step_name in ("_distinct", "_unique"):
                distinct = True

            elif step_name == "_rename":
                renames = self._extract_rename_map(step_args)

            elif step_name == "_count":
                agg_selects = [("count", "COUNT(*)", None)]

            elif step_name == "_sum":
                agg_selects = [("total", "SUM(*)", None)]

            elif step_name == "_avg":
                agg_selects = [("average", "AVG(*)", None)]

            elif step_name == "_min":
                agg_selects = [("minimum", "MIN(*)", None)]

            elif step_name == "_max":
                agg_selects = [("maximum", "MAX(*)", None)]

            elif step_name == "_mutate":
                # _mutate adds computed columns — express as SELECT *, expr AS name
                computed = self._extract_mutate_cols(step_args)
                if computed and select_cols == ["*"]:
                    select_cols = ["*"] + computed

            elif step_name == "_pull":
                if step_args and isinstance(step_args[0], Literal):
                    select_cols = [step_args[0].value]

            elif step_name == "_reverse":
                if order_by:
                    # Reverse existing order
                    order_by = [
                        o.replace(" ASC", " DESC") if " DESC" not in o
                        else o.replace(" DESC", " ASC")
                        for o in order_by
                    ]
                else:
                    order_by.append("1 DESC")

            elif step_name == "_slice":
                if step_args:
                    offset = int(step_args[0].value) if isinstance(step_args[0], Literal) else None
                    if len(step_args) > 1 and isinstance(step_args[1], Literal):
                        limit = int(step_args[1].value)

            elif step_name == "_first":
                limit = 1

            elif step_name == "_last":
                limit = 1
                if not order_by:
                    order_by.append("1 DESC")

        # Build the SELECT clause
        if agg_selects:
            if isinstance(agg_selects[0], tuple):
                sel_parts = []
                for item in agg_selects:
                    if len(item) == 3:
                        alias, expr, _ = item
                        sel_parts.append(f"{expr} AS {alias}")
                    else:
                        sel_parts.append(str(item))
                if group_by:
                    sel_parts = [g for g in group_by] + sel_parts
                select_clause = ", ".join(sel_parts)
            else:
                select_clause = ", ".join(str(a) for a in agg_selects)
        else:
            # Apply renames
            if renames:
                if select_cols == ["*"]:
                    # When renaming with *, express as: *, old AS new
                    rename_parts = [f"{old} AS {new}" for old, new in renames.items()]
                    select_cols = ["*"] + rename_parts
                else:
                    renamed_cols = []
                    for c in select_cols:
                        if c in renames:
                            renamed_cols.append(f"{c} AS {renames[c]}")
                        else:
                            renamed_cols.append(c)
                    select_cols = renamed_cols

            select_clause = ", ".join(select_cols)

        # Assemble SQL
        parts = []
        parts.append(f"SELECT {'DISTINCT ' if distinct else ''}{select_clause}")
        parts.append(f"FROM {table}")

        for j in joins:
            parts.append(j)

        if where_clauses:
            parts.append(f"WHERE {' AND '.join(where_clauses)}")

        if group_by:
            parts.append(f"GROUP BY {', '.join(group_by)}")

        if having_clauses:
            parts.append(f"HAVING {' AND '.join(having_clauses)}")

        if order_by:
            parts.append(f"ORDER BY {', '.join(order_by)}")

        if limit is not None:
            parts.append(f"LIMIT {limit}")

        if offset is not None:
            parts.append(f"OFFSET {offset}")

        return "\n".join(parts) + ";"

    # -------------------------------------------------------------------
    # Helpers: extracting SQL fragments from AST nodes
    # -------------------------------------------------------------------

    def _emit_source(self, node: ASTNode) -> str:
        """Get a table name from the source expression."""
        if isinstance(node, Identifier):
            return node.name
        if isinstance(node, Literal) and isinstance(node.value, str):
            return node.value
        if isinstance(node, Call) and isinstance(node.callee, Identifier):
            if node.callee.name == "read_csv":
                if node.args and isinstance(node.args[0], Literal):
                    # Extract filename without extension as table name
                    import os
                    fname = os.path.basename(node.args[0].value)
                    return os.path.splitext(fname)[0]
            return node.callee.name
        return "source_table"

    def _lambda_to_sql(self, node: ASTNode, table: str = "") -> str:
        """Convert a lambda's body expression to a SQL WHERE condition."""
        if node is None:
            return ""
        if isinstance(node, Lambda):
            return self._expr_to_sql(node.body)
        return self._expr_to_sql(node)

    def _lambda_to_column(self, node: ASTNode) -> str:
        """Extract the column name from a simple lambda like (r) => r["col"]."""
        if isinstance(node, Lambda):
            return self._extract_column_ref(node.body)
        if isinstance(node, Literal) and isinstance(node.value, str):
            return node.value
        return self._extract_column_ref(node)

    def _extract_column_ref(self, node: ASTNode) -> str:
        """Extract column name from r["col"] or r.col patterns."""
        if isinstance(node, Index):
            if isinstance(node.index, Literal) and isinstance(node.index.value, str):
                return node.index.value
        if isinstance(node, Member):
            return node.field_name
        if isinstance(node, Identifier):
            return node.name
        return self._expr_to_sql(node)

    def _expr_to_sql(self, node: ASTNode) -> str:
        """Convert a TinyTalk expression to a SQL expression."""
        if isinstance(node, Literal):
            if node.value is None:
                return "NULL"
            if isinstance(node.value, bool):
                return "TRUE" if node.value else "FALSE"
            if isinstance(node.value, str):
                escaped = node.value.replace("'", "''")
                return f"'{escaped}'"
            return str(node.value)

        if isinstance(node, Identifier):
            return node.name

        if isinstance(node, BinaryOp):
            left = self._expr_to_sql(node.left)
            right = self._expr_to_sql(node.right)
            op = self._sql_op(node.op)
            return f"{left} {op} {right}"

        if isinstance(node, UnaryOp):
            operand = self._expr_to_sql(node.operand)
            if node.op in ("not", "!"):
                return f"NOT {operand}"
            return f"-{operand}"

        if isinstance(node, Index):
            if isinstance(node.index, Literal) and isinstance(node.index.value, str):
                return node.index.value
            return f"{self._expr_to_sql(node.obj)}[{self._expr_to_sql(node.index)}]"

        if isinstance(node, Member):
            return node.field_name

        if isinstance(node, Call):
            if isinstance(node.callee, Identifier):
                fn_name = node.callee.name
                args = [self._expr_to_sql(a) for a in node.args]
                sql_fn = self._sql_function(fn_name)
                if sql_fn:
                    return f"{sql_fn}({', '.join(args)})"
            return f"{self._expr_to_sql(node.callee)}({', '.join(self._expr_to_sql(a) for a in node.args)})"

        if isinstance(node, Conditional):
            cond = self._expr_to_sql(node.condition)
            then = self._expr_to_sql(node.then_expr)
            els = self._expr_to_sql(node.else_expr)
            return f"CASE WHEN {cond} THEN {then} ELSE {els} END"

        if isinstance(node, StepChain):
            # Nested step chain → subquery
            sub_sql = self._emit_step_chain(node)
            return f"({sub_sql.rstrip(';')})"

        return "?"

    def _sql_op(self, op: str) -> str:
        """Map TinyTalk operators to SQL."""
        op_map = {
            "==": "=", "!=": "<>", "is": "=", "isnt": "<>",
            "and": "AND", "or": "OR", "not": "NOT",
            "+": "+", "-": "-", "*": "*", "/": "/",
            "%": "%", "**": "POWER",
            "<": "<", ">": ">", "<=": "<=", ">=": ">=",
            "has": "IN", "isin": "IN",
            "islike": "LIKE",
        }
        return op_map.get(op, op)

    def _sql_function(self, name: str) -> str:
        """Map TinyTalk function names to SQL function names."""
        fn_map = {
            "len": "LENGTH",
            "upcase": "UPPER",
            "downcase": "LOWER",
            "trim": "TRIM",
            "abs": "ABS",
            "round": "ROUND",
            "floor": "FLOOR",
            "ceil": "CEIL",
            "sqrt": "SQRT",
            "pow": "POWER",
            "sum": "SUM",
            "min": "MIN",
            "max": "MAX",
            "avg": "AVG",
            "count": "COUNT",
            "replace": "REPLACE",
            "startswith": None,  # no direct SQL equivalent
            "endswith": None,
        }
        return fn_map.get(name)

    def _extract_column_names(self, args: list) -> list:
        """Extract column names from _select arguments."""
        cols = []
        for arg in args:
            if isinstance(arg, Literal) and isinstance(arg.value, str):
                cols.append(arg.value)
            elif isinstance(arg, Array):
                for el in arg.elements:
                    if isinstance(el, Literal) and isinstance(el.value, str):
                        cols.append(el.value)
        return cols

    def _extract_rename_map(self, args: list) -> dict:
        """Extract {old: new} mapping from _rename argument."""
        renames = {}
        if args and isinstance(args[0], MapLiteral):
            for k, v in args[0].pairs:
                if isinstance(k, Literal) and isinstance(v, Literal):
                    renames[k.value] = v.value
        return renames

    def _extract_agg_map(self, args: list) -> list:
        """Extract aggregation expressions from _summarize argument."""
        aggs = []
        if not args:
            return aggs
        arg = args[0]
        if isinstance(arg, MapLiteral):
            for k, v in arg.pairs:
                alias = k.value if isinstance(k, Literal) else "?"
                sql_expr = self._agg_lambda_to_sql(v)
                aggs.append((alias, sql_expr, None))
        return aggs

    def _agg_lambda_to_sql(self, node: ASTNode) -> str:
        """Convert an aggregation lambda to SQL (e.g., (rows) => rows _sum → SUM(*))."""
        if isinstance(node, Lambda):
            body = node.body
            if isinstance(body, StepChain):
                # (rows) => rows _map((r) => r["col"]) _sum
                col = "*"
                agg_fn = None
                for step_name, step_args in body.steps:
                    if step_name == "_map" and step_args:
                        col = self._lambda_to_column(step_args[0])
                    elif step_name == "_sum":
                        agg_fn = "SUM"
                    elif step_name == "_avg":
                        agg_fn = "AVG"
                    elif step_name == "_min":
                        agg_fn = "MIN"
                    elif step_name == "_max":
                        agg_fn = "MAX"
                    elif step_name == "_count":
                        agg_fn = "COUNT"
                if agg_fn:
                    return f"{agg_fn}({col})"
            return self._expr_to_sql(body)
        return "?"

    def _extract_mutate_cols(self, args: list) -> list:
        """Extract computed column expressions from _mutate lambda."""
        if not args:
            return []
        arg = args[0]
        if isinstance(arg, Lambda) and isinstance(arg.body, MapLiteral):
            cols = []
            for k, v in arg.body.pairs:
                alias = k.value if isinstance(k, Literal) else "?"
                expr = self._expr_to_sql(v)
                cols.append(f"{expr} AS {alias}")
            return cols
        return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def transpile_sql(source: str) -> str:
    """Transpile TinyTalk source to SQL."""
    return SQLTranspiler().transpile(source)
