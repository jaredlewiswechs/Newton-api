"""
═══════════════════════════════════════════════════════════════════════════════
realTinyTalk → Python BACKEND
═══════════════════════════════════════════════════════════════════════════════

Transpiles realTinyTalk AST to readable Python.

Design Principles:
1. Emit READABLE Python, not clever Python
2. Use runtime helpers for TinyTalk-specific features
3. Keep 1:1 mapping where possible
4. Preserve source structure for debugging

Mapping:
  let x = 42           →  x = 42
  when PI = 3.14       →  PI = 3.14  # constant by convention
  law f(x) ... end     →  def f(x): ...
  forge g() ... end    →  def g(): ...
  if/elif/else         →  if/elif/else
  for i in range(n)    →  for i in range(n):
  while cond           →  while cond:
  show(...)            →  tt.show(...)
  x is y               →  tt.is_(x, y)
  x has .f             →  tt.has(x, "f")
  x _sort _filter(fn)  →  tt.chain(x).sort().filter(fn).value()
  blueprint B { }      →  class B: ...
"""

import sys
from pathlib import Path
from typing import List, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from realTinyTalk.parser import (
    Program, ASTNode, NodeType, Member,
    Literal, BinaryOp, UnaryOp, Call, Index, Array, MapLiteral,
    Lambda, Conditional, Range, Pipe, StepChain,
    LetStmt, ConstStmt, AssignStmt, Block, IfStmt, ForStmt, WhileStmt,
    ReturnStmt, FnDecl, StructDecl, ImportStmt, Identifier,
)


class PythonEmitter:
    """
    Transpiles realTinyTalk AST to Python source code.
    """
    
    def __init__(self, include_runtime: bool = True, indent_size: int = 4):
        self.include_runtime = include_runtime
        self.indent_size = indent_size
        self.indent_level = 0
        self.output_lines: List[str] = []
    
    def emit(self, ast: Program) -> str:
        """Emit Python from AST."""
        self.output_lines = []
        self.indent_level = 0
        
        if self.include_runtime:
            self._emit_runtime_header()
        
        for stmt in ast.statements:
            py = self._emit_node(stmt)
            if py:
                self._write(py)
        
        return '\n'.join(self.output_lines)
    
    def _indent(self) -> str:
        return ' ' * (self.indent_level * self.indent_size)
    
    def _write(self, line: str):
        if line.strip():
            self.output_lines.append(self._indent() + line)
        else:
            self.output_lines.append('')
    
    def _write_raw(self, line: str):
        self.output_lines.append(line)
    
    def _emit_runtime_header(self):
        """Emit the Python runtime helper."""
        self._write_raw('"""')
        self._write_raw('Generated from realTinyTalk')
        self._write_raw('"""')
        self._write_raw('')
        self._write_raw('# ═══════════════════════════════════════════════════════════════')
        self._write_raw('# TinyTalk Runtime')
        self._write_raw('# ═══════════════════════════════════════════════════════════════')
        self._write_raw('')
        self._write_raw('class TinyTalkRuntime:')
        self._write_raw('    """Runtime helpers for TinyTalk operations."""')
        self._write_raw('    ')
        self._write_raw('    @staticmethod')
        self._write_raw('    def show(*args):')
        self._write_raw('        print(" ".join(str(a) for a in args))')
        self._write_raw('    ')
        self._write_raw('    @staticmethod')
        self._write_raw('    def is_(a, b):')
        self._write_raw('        return type(a) == type(b) and a == b')
        self._write_raw('    ')
        self._write_raw('    @staticmethod')
        self._write_raw('    def has(obj, item):')
        self._write_raw('        """Check if obj contains item (list/dict) or has attribute."""')
        self._write_raw('        if isinstance(obj, (list, tuple, set)):')
        self._write_raw('            return item in obj')
        self._write_raw('        if isinstance(obj, dict):')
        self._write_raw('            return item in obj')
        self._write_raw('        if isinstance(obj, str):')
        self._write_raw('            return item in obj')
        self._write_raw('        return hasattr(obj, str(item))')
        self._write_raw('    ')
        self._write_raw('    @staticmethod')
        self._write_raw('    def islike(s, pattern):')
        self._write_raw('        """Glob-style pattern matching (N* matches Newton)."""')
        self._write_raw('        import fnmatch')
        self._write_raw('        return fnmatch.fnmatch(str(s), pattern)')
        self._write_raw('    ')
        self._write_raw('    @staticmethod')
        self._write_raw('    def prop(obj, name):')
        self._write_raw('        """Get property with TinyTalk magic."""')
        self._write_raw('        if isinstance(obj, str):')
        self._write_raw('            props = {')
        self._write_raw('                "len": len(obj), "length": len(obj),')
        self._write_raw('                "upcase": obj.upper(), "upper": obj.upper(),')
        self._write_raw('                "lowcase": obj.lower(), "lower": obj.lower(),')
        self._write_raw('                "trim": obj.strip(), "strip": obj.strip(),')
        self._write_raw('                "reversed": obj[::-1],')
        self._write_raw('                "first": obj[0] if obj else "",')
        self._write_raw('                "last": obj[-1] if obj else "",')
        self._write_raw('                "words": obj.split(),')
        self._write_raw('                "lines": obj.splitlines(),')
        self._write_raw('                "chars": list(obj),')
        self._write_raw('            }')
        self._write_raw('            if name in props:')
        self._write_raw('                return props[name]')
        self._write_raw('        if isinstance(obj, (list, tuple)):')
        self._write_raw('            props = {')
        self._write_raw('                "len": len(obj), "length": len(obj), "count": len(obj),')
        self._write_raw('                "first": obj[0] if obj else None,')
        self._write_raw('                "last": obj[-1] if obj else None,')
        self._write_raw('                "sum": sum(obj) if obj else 0,')
        self._write_raw('                "min": min(obj) if obj else None,')
        self._write_raw('                "max": max(obj) if obj else None,')
        self._write_raw('                "avg": sum(obj)/len(obj) if obj else 0,')
        self._write_raw('                "sorted": sorted(obj),')
        self._write_raw('                "reversed": list(reversed(obj)),')
        self._write_raw('                "unique": list(dict.fromkeys(obj)),')
        self._write_raw('            }')
        self._write_raw('            if name in props:')
        self._write_raw('                return props[name]')
        self._write_raw('        if hasattr(obj, name):')
        self._write_raw('            return getattr(obj, name)')
        self._write_raw('        if isinstance(obj, dict) and name in obj:')
        self._write_raw('            return obj[name]')
        self._write_raw('        return None')
        self._write_raw('    ')
        self._write_raw('    class Chain:')
        self._write_raw('        """Chainable operations on data."""')
        self._write_raw('        def __init__(self, data):')
        self._write_raw('            self._data = list(data) if not isinstance(data, list) else data')
        self._write_raw('        ')
        self._write_raw('        def sort(self, key=None, reverse=False):')
        self._write_raw('            self._data = sorted(self._data, key=key, reverse=reverse)')
        self._write_raw('            return self')
        self._write_raw('        ')
        self._write_raw('        def filter(self, fn):')
        self._write_raw('            self._data = [x for x in self._data if fn(x)]')
        self._write_raw('            return self')
        self._write_raw('        ')
        self._write_raw('        def map(self, fn):')
        self._write_raw('            self._data = [fn(x) for x in self._data]')
        self._write_raw('            return self')
        self._write_raw('        ')
        self._write_raw('        def take(self, n):')
        self._write_raw('            self._data = self._data[:n]')
        self._write_raw('            return self')
        self._write_raw('        ')
        self._write_raw('        def skip(self, n):')
        self._write_raw('            self._data = self._data[n:]')
        self._write_raw('            return self')
        self._write_raw('        ')
        self._write_raw('        def unique(self):')
        self._write_raw('            self._data = list(dict.fromkeys(self._data))')
        self._write_raw('            return self')
        self._write_raw('        ')
        self._write_raw('        def reverse(self):')
        self._write_raw('            self._data = list(reversed(self._data))')
        self._write_raw('            return self')
        self._write_raw('        ')
        self._write_raw('        def sum(self):')
        self._write_raw('            return sum(self._data)')
        self._write_raw('        ')
        self._write_raw('        def avg(self):')
        self._write_raw('            return sum(self._data) / len(self._data) if self._data else 0')
        self._write_raw('        ')
        self._write_raw('        def first(self):')
        self._write_raw('            return self._data[0] if self._data else None')
        self._write_raw('        ')
        self._write_raw('        def last(self):')
        self._write_raw('            return self._data[-1] if self._data else None')
        self._write_raw('        ')
        self._write_raw('        def value(self):')
        self._write_raw('            return self._data')
        self._write_raw('    ')
        self._write_raw('    @classmethod')
        self._write_raw('    def chain(cls, data):')
        self._write_raw('        return cls.Chain(data)')
        self._write_raw('')
        self._write_raw('')
        self._write_raw('tt = TinyTalkRuntime()')
        self._write_raw('')
        self._write_raw('# ═══════════════════════════════════════════════════════════════')
        self._write_raw('# Generated Code')
        self._write_raw('# ═══════════════════════════════════════════════════════════════')
        self._write_raw('')
    
    def _emit_node(self, node: ASTNode) -> str:
        """Emit Python for a single AST node."""
        if node is None:
            return ''
        
        ntype = node.type
        
        # Literals
        if ntype == NodeType.LITERAL:
            return self._emit_literal(node)
        
        # Identifiers
        if ntype == NodeType.IDENTIFIER:
            return node.name
        
        # Binary operations
        if ntype == NodeType.BINARY_OP:
            return self._emit_binary(node)
        
        # Unary operations
        if ntype == NodeType.UNARY_OP:
            return self._emit_unary(node)
        
        # Function calls
        if ntype == NodeType.CALL:
            return self._emit_call(node)
        
        # Index access
        if ntype == NodeType.INDEX:
            return self._emit_index(node)
        
        # Member access
        if ntype == NodeType.MEMBER:
            return self._emit_member(node)
        
        # Array literal
        if ntype == NodeType.ARRAY:
            return self._emit_array(node)
        
        # Map/Object literal
        if ntype == NodeType.MAP_LITERAL:
            return self._emit_map(node)
        
        # Lambda
        if ntype == NodeType.LAMBDA:
            return self._emit_lambda(node)
        
        # Conditional expression
        if ntype == NodeType.CONDITIONAL:
            return self._emit_conditional_expr(node)
        
        # Range
        if ntype == NodeType.RANGE:
            return self._emit_range(node)
        
        # Pipe
        if ntype == NodeType.PIPE:
            return self._emit_pipe(node)
        
        # Step chain
        if ntype == NodeType.STEP_CHAIN:
            return self._emit_step_chain(node)
        
        # Statements
        if ntype == NodeType.LET_STMT:
            return self._emit_let(node)
        
        if ntype == NodeType.CONST_STMT:
            return self._emit_const(node)
        
        if ntype == NodeType.ASSIGN:
            return self._emit_assign(node)
        
        if ntype == NodeType.BLOCK_STMT:
            return self._emit_block(node)
        
        if ntype == NodeType.IF_STMT:
            return self._emit_if(node)
        
        if ntype == NodeType.FOR_STMT:
            return self._emit_for(node)
        
        if ntype == NodeType.WHILE_STMT:
            return self._emit_while(node)
        
        if ntype == NodeType.RETURN_STMT:
            return self._emit_return(node)
        
        if ntype == NodeType.BREAK_STMT:
            return 'break'
        
        if ntype == NodeType.CONTINUE_STMT:
            return 'continue'
        
        if ntype == NodeType.FN_DECL:
            return self._emit_function(node)
        
        if ntype == NodeType.STRUCT_DECL or ntype == NodeType.BLUEPRINT:
            return self._emit_struct(node)
        
        if ntype == NodeType.IMPORT_STMT:
            return self._emit_import(node)
        
        # TinyTalk specific
        if ntype == NodeType.EXPR_STMT:
            return self._emit_node(node.expression) if hasattr(node, 'expression') else ''
        
        if ntype == NodeType.LAW or ntype == NodeType.FORGE:
            return self._emit_function(node)
        
        if ntype == NodeType.REPLY_STMT:
            return self._emit_return(node)
        
        return f'# Unknown node: {ntype}'
    
    def _emit_literal(self, node: Literal) -> str:
        val = node.value
        if val is None:
            return 'None'
        if isinstance(val, bool):
            return 'True' if val else 'False'
        if isinstance(val, str):
            escaped = val.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            return f'"{escaped}"'
        return str(val)
    
    def _emit_binary(self, node: BinaryOp) -> str:
        left = self._emit_node(node.left)
        right = self._emit_node(node.right)
        op = node.op
        
        # Operator mapping
        op_map = {
            'and': 'and',
            'or': 'or',
            'is': '==',
            'isnt': '!=',
            '==': '==',
            '!=': '!=',
            '<': '<',
            '>': '>',
            '<=': '<=',
            '>=': '>=',
            '+': '+',
            '-': '-',
            '*': '*',
            '/': '/',
            '%': '%',
            '**': '**',
            '^': '**',
            '..': '',  # range handled separately
        }
        
        # Special cases
        if op == 'is':
            return f'tt.is_({left}, {right})'
        if op == 'has':
            return f'tt.has({left}, {right})'
        if op == 'in':
            return f'({left} in {right})'
        if op == '..':
            return f'range({left}, {right} + 1)'
        if op == 'islike':
            # Convert glob pattern to regex
            return f'tt.islike({left}, {right})'
        
        py_op = op_map.get(op, op)
        return f'({left} {py_op} {right})'
    
    def _emit_unary(self, node: UnaryOp) -> str:
        operand = self._emit_node(node.operand)
        op = node.op
        
        if op == 'not' or op == '!':
            return f'(not {operand})'
        if op == '-':
            return f'(-{operand})'
        
        return f'{op}{operand}'
    
    def _emit_call(self, node: Call) -> str:
        callee = self._emit_node(node.callee)
        args = ', '.join(self._emit_node(a) for a in node.args)
        
        # Built-in function mapping
        builtins = {
            'show': 'tt.show',
            'print': 'tt.show',
            'len': 'len',
            'str': 'str',
            'int': 'int',
            'float': 'float',
            'bool': 'bool',
            'list': 'list',
            'type': 'type',
            'range': 'range',
            'abs': 'abs',
            'min': 'min',
            'max': 'max',
            'sum': 'sum',
            'sorted': 'sorted',
            'reversed': 'reversed',
            'enumerate': 'enumerate',
            'zip': 'zip',
            'map': 'map',
            'filter': 'filter',
            'input': 'input',
            'sqrt': 'math.sqrt',
            'floor': 'math.floor',
            'ceil': 'math.ceil',
            'round': 'round',
            'random': 'random.random',
        }
        
        py_callee = builtins.get(callee, callee)
        return f'{py_callee}({args})'
    
    def _emit_index(self, node: Index) -> str:
        obj = self._emit_node(node.obj)
        idx = self._emit_node(node.index)
        return f'{obj}[{idx}]'
    
    def _emit_member(self, node: Member) -> str:
        # Collect chain of member fields
        fields = []
        cur = node
        while isinstance(cur, Member):
            fields.append(cur.field)
            cur = cur.obj
        base = self._emit_node(cur)

        # If single member, prefer tt.prop for magic properties to preserve TinyTalk semantics
        if len(fields) == 1:
            field = fields[0]
            if field == 'str':
                return f'str({base})'
            return f'tt.prop({base}, "{field}")'

        # For chained properties (e.g., a.upcase.len) emit nested builtins when possible
        builtin_map = {
            'upcase': 'upcase',
            'len': 'len',
            'reversed': 'reversed',
            'str': 'str',
        }
        result = base
        for field in reversed(fields):
            if field in builtin_map:
                fn = builtin_map[field]
                result = f'{fn}({result})'
            else:
                result = f'tt.prop({result}, "{field}")'
        return result
    
    def _emit_array(self, node: Array) -> str:
        elements = ', '.join(self._emit_node(e) for e in node.elements)
        return f'[{elements}]'
    
    def _emit_map(self, node: MapLiteral) -> str:
        pairs = []
        for k, v in node.pairs:
            key = self._emit_node(k) if not isinstance(k, str) else f'"{k}"'
            val = self._emit_node(v)
            pairs.append(f'{key}: {val}')
        return '{' + ', '.join(pairs) + '}'
    
    def _emit_lambda(self, node: Lambda) -> str:
        params = ', '.join(node.params)
        body = self._emit_node(node.body)
        return f'(lambda {params}: {body})'
    
    def _emit_conditional_expr(self, node: Conditional) -> str:
        cond = self._emit_node(node.condition)
        then = self._emit_node(node.then_expr)
        else_ = self._emit_node(node.else_expr) if node.else_expr else 'None'
        return f'({then} if {cond} else {else_})'
    
    def _emit_range(self, node: Range) -> str:
        start = self._emit_node(node.start)
        end = self._emit_node(node.end)
        if node.inclusive:
            return f'range({start}, {end} + 1)'
        return f'range({start}, {end})'
    
    def _emit_pipe(self, node: Pipe) -> str:
        # x |> f(y) becomes f(x, y)
        left = self._emit_node(node.left)
        right = node.right
        
        if right.type == NodeType.CALL:
            callee = self._emit_node(right.callee)
            args = [left] + [self._emit_node(a) for a in right.args]
            return f'{callee}({", ".join(args)})'
        
        return f'{self._emit_node(right)}({left})'
    
    def _emit_step_chain(self, node: StepChain) -> str:
        obj = self._emit_node(node.source)
        steps = node.steps
        terminal_ops = ['sum', 'avg', 'first', 'last', 'find', 'any', 'all', 'none', 'count', 'join']
        # If dotted chain (written with dots), emit nested function-style calls: sum(take(reverse(sort(obj)), 2))
        if getattr(node, 'dotted', False):
            nested = obj
            for step_name, step_args in reversed(steps):
                py_method = step_name.lstrip('_')
                if step_args:
                    args = ', '.join(self._emit_node(a) for a in step_args)
                    nested = f'{py_method}({nested}, {args})'
                else:
                    nested = f'{py_method}({nested})'
            return nested
        # Otherwise (space-separated chain tokens), emit chain method for readability (.sort(), .take(n), etc.)
        result = f'tt.chain({obj})'
        for step_name, step_args in steps:
            py_method = step_name.lstrip('_')
            args = ', '.join(self._emit_node(a) for a in step_args) if step_args else ''
            result += f'.{py_method}({args})'
        last_step = steps[-1][0].lstrip('_') if steps else ''
        if last_step not in terminal_ops:
            result += '.value()'
        return result
    
    def _emit_let(self, node: LetStmt) -> str:
        name = node.name
        value = self._emit_node(node.value)
        return f'{name} = {value}'
    
    def _emit_const(self, node: ConstStmt) -> str:
        name = node.name
        value = self._emit_node(node.value)
        return f'{name} = {value}  # constant'
    
    def _emit_assign(self, node: AssignStmt) -> str:
        target = self._emit_node(node.target)
        value = self._emit_node(node.value)
        return f'{target} = {value}'
    
    def _emit_block(self, node: Block) -> str:
        lines = []
        for stmt in node.statements:
            line = self._emit_node(stmt)
            if line:
                lines.append(line)
        return '\n'.join(self._indent() + line for line in lines) if lines else 'pass'
    
    def _emit_if(self, node: IfStmt) -> str:
        lines = []
        cond = self._emit_node(node.condition)
        lines.append(f'if {cond}:')
        
        self.indent_level += 1
        then_body = self._emit_node(node.then_branch)
        if then_body:
            for line in then_body.split('\n'):
                lines.append(line)
        else:
            lines.append(self._indent() + 'pass')
        self.indent_level -= 1
        
        # elif branches
        for elif_cond, elif_body in node.elif_branches:
            elif_cond_str = self._emit_node(elif_cond)
            lines.append(f'elif {elif_cond_str}:')
            self.indent_level += 1
            elif_body_str = self._emit_node(elif_body)
            if elif_body_str:
                for line in elif_body_str.split('\n'):
                    lines.append(line)
            else:
                lines.append(self._indent() + 'pass')
            self.indent_level -= 1
        
        # else branch
        if node.else_branch:
            lines.append('else:')
            self.indent_level += 1
            else_body = self._emit_node(node.else_branch)
            if else_body:
                for line in else_body.split('\n'):
                    lines.append(line)
            else:
                lines.append(self._indent() + 'pass')
            self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def _emit_for(self, node: ForStmt) -> str:
        lines = []
        var = node.var
        iterable = self._emit_node(node.iterable)
        lines.append(f'for {var} in {iterable}:')
        
        self.indent_level += 1
        body = self._emit_node(node.body)
        if body:
            for line in body.split('\n'):
                lines.append(line)
        else:
            lines.append(self._indent() + 'pass')
        self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def _emit_while(self, node: WhileStmt) -> str:
        lines = []
        cond = self._emit_node(node.condition)
        lines.append(f'while {cond}:')
        
        self.indent_level += 1
        body = self._emit_node(node.body)
        if body:
            for line in body.split('\n'):
                lines.append(line)
        else:
            lines.append(self._indent() + 'pass')
        self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def _emit_return(self, node: ReturnStmt) -> str:
        if node.value:
            val = self._emit_node(node.value)
            return f'return {val}'
        return 'return'
    
    def _emit_function(self, node: FnDecl) -> str:
        lines = []
        name = node.name
        # params is [(name, type_hint), ...]
        params = ', '.join(p[0] if isinstance(p, tuple) else p for p in node.params)
        lines.append(f'def {name}({params}):')
        
        self.indent_level += 1
        body = self._emit_node(node.body)
        if body:
            for line in body.split('\n'):
                lines.append(line)
        else:
            lines.append(self._indent() + 'pass')
        self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def _emit_struct(self, node: StructDecl) -> str:
        lines = []
        name = node.name
        lines.append(f'class {name}:')
        
        self.indent_level += 1
        
        # __init__ method - fields is [(name, type, default), ...]
        fields = node.fields if hasattr(node, 'fields') else []
        if fields:
            # f[0]=name, f[1]=type, f[2]=default
            field_params = ', '.join(
                f'{f[0]}={self._emit_node(f[2])}' if len(f) > 2 and f[2] else f'{f[0]}=None' 
                for f in fields
            )
            lines.append(self._indent() + f'def __init__(self, {field_params}):')
            self.indent_level += 1
            for f in fields:
                lines.append(self._indent() + f'self.{f[0]} = {f[0]}')
            self.indent_level -= 1
        else:
            lines.append(self._indent() + 'def __init__(self):')
            self.indent_level += 1
            lines.append(self._indent() + 'pass')
            self.indent_level -= 1
        
        # Methods - methods is [(method_type, FnDecl), ...]
        methods = node.methods if hasattr(node, 'methods') else []
        for method_type, method_fn in methods:
            lines.append('')
            method_str = self._emit_method(method_fn)
            for line in method_str.split('\n'):
                lines.append(line)
        
        self.indent_level -= 1
        return '\n'.join(lines)
    
    def _emit_method(self, node: FnDecl) -> str:
        lines = []
        name = node.name
        # params is [(name, type_hint), ...]
        params = ['self'] + [p[0] if isinstance(p, tuple) else p for p in node.params]
        params_str = ', '.join(params)
        lines.append(self._indent() + f'def {name}({params_str}):')
        
        self.indent_level += 1
        body = self._emit_node(node.body)
        if body:
            for line in body.split('\n'):
                lines.append(line)
        else:
            lines.append(self._indent() + 'pass')
        self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def _emit_import(self, node: ImportStmt) -> str:
        module = node.module
        if node.alias:
            return f'import {module} as {node.alias}'
        return f'import {module}'


def transpile_to_python(code: str, include_runtime: bool = True) -> str:
    """Convenience function to transpile TinyTalk code to Python."""
    from realTinyTalk.lexer import Lexer
    from realTinyTalk.parser import Parser
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    emitter = PythonEmitter(include_runtime=include_runtime)
    return emitter.emit(ast)
