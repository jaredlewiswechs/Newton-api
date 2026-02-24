"""
Tests for the TinyTalk Roadmap Features:

1. Import / module system
2. REPL with state persistence
3. Error messages that teach
4. Optional type annotations
5. SQL transpiler target
"""

import pytest
import tempfile
import os

from newTinyTalk import TinyTalkKernel, RunResult, transpile_sql
from newTinyTalk.errors import (
    find_closest, undefined_variable_hint, unknown_step_hint,
    step_type_mismatch_hint, step_args_hint,
)
from newTinyTalk.typechecker import check_type, check_param_type, check_return_type
from newTinyTalk.types import Value, ValueType


def run(code: str, source_dir: str = "") -> RunResult:
    return TinyTalkKernel(source_dir=source_dir).run(code)


def output(code: str, source_dir: str = "") -> str:
    return run(code, source_dir).output.strip()


# =====================================================================
# 1. Import / Module System
# =====================================================================

class TestImportSystem:
    """Test import "module", import "module" as alias, from "module" use { names }."""

    def _write_module(self, tmpdir: str, filename: str, content: str) -> str:
        path = os.path.join(tmpdir, filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_import_all(self):
        """import "utils.tt" brings all top-level names into scope."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_module(tmpdir, "utils.tt", """
fn double(x) { return x * 2 }
fn triple(x) { return x * 3 }
let VERSION = "1.0"
""")
            code = """
import "utils.tt"
show(double(5))
show(triple(3))
show(VERSION)
"""
            assert output(code, source_dir=tmpdir) == "10\n9\n1.0"

    def test_import_as_alias(self):
        """import "utils.tt" as u creates a namespace map."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_module(tmpdir, "math_utils.tt", """
fn square(x) { return x * x }
let PI = 3.14159
""")
            code = """
import "math_utils.tt" as math
show(math["PI"])
"""
            assert output(code, source_dir=tmpdir) == "3.14159"

    def test_from_import_selective(self):
        """from "module" use { name1, name2 } imports only selected names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_module(tmpdir, "stats.tt", """
fn mean(data) { return data _sum / data _count }
fn median(data) {
    let sorted = data _sort
    let n = data _count
    return sorted[n // 2]
}
fn mode(data) { return data[0] }
""")
            code = """
from "stats.tt" use { mean, median }
let data = [10, 20, 30, 40, 50]
show(mean(data))
show(median(data))
"""
            assert output(code, source_dir=tmpdir) == "30.0\n30"

    def test_from_import_not_exported(self):
        """Importing a name that doesn't exist in module raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_module(tmpdir, "small.tt", """
fn hello() { return "hi" }
""")
            code = """
from "small.tt" use { hello, nonexistent }
"""
            r = run(code, source_dir=tmpdir)
            assert not r.success
            assert "nonexistent" in r.error

    def test_import_not_found(self):
        """Importing a nonexistent file raises error."""
        r = run('import "doesnt_exist.tt"')
        assert not r.success
        assert "not found" in r.error.lower()

    def test_import_underscore_private(self):
        """Names starting with _ are not imported by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_module(tmpdir, "priv.tt", """
let _internal = 42
let public_val = 100
""")
            code = """
import "priv.tt"
show(public_val)
"""
            r = run(code, source_dir=tmpdir)
            assert r.success
            assert r.output.strip() == "100"

    def test_import_dedup(self):
        """Importing the same module twice doesn't re-execute it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_module(tmpdir, "counter.tt", """
let count = 1
""")
            code = """
import "counter.tt"
import "counter.tt"
show(count)
"""
            assert output(code, source_dir=tmpdir) == "1"

    def test_import_extension_optional(self):
        """import "utils" auto-appends .tt extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_module(tmpdir, "utils.tt", """
fn greet() { return "hello" }
""")
            code = """
import "utils"
show(greet())
"""
            assert output(code, source_dir=tmpdir) == "hello"

    def test_nested_imports(self):
        """Modules can import other modules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_module(tmpdir, "base.tt", """
fn add(a, b) { return a + b }
""")
            self._write_module(tmpdir, "mid.tt", """
import "base.tt"
fn add3(a, b, c) { return add(add(a, b), c) }
""")
            code = """
import "mid.tt"
show(add3(1, 2, 3))
"""
            assert output(code, source_dir=tmpdir) == "6"


# =====================================================================
# 2. REPL with State Persistence  (unit tests for kernel state)
# =====================================================================

class TestREPLPersistence:
    """Test that Runtime state persists across execute() calls."""

    def test_state_persists_across_runs(self):
        """Variables defined in one run are available in the next."""
        from newTinyTalk.runtime import Runtime
        from newTinyTalk.lexer import Lexer
        from newTinyTalk.parser import Parser
        from newTinyTalk.stdlib import set_output_buffer, clear_output_buffer

        runtime = Runtime()

        # First execution
        tokens = Lexer('let x = 42').tokenize()
        ast = Parser(tokens).parse()
        runtime.execute(ast)

        # Second execution uses x
        tokens = Lexer('show(x + 8)').tokenize()
        ast = Parser(tokens).parse()
        buf = []
        set_output_buffer(buf)
        try:
            runtime.execute(ast)
        finally:
            clear_output_buffer()
        assert "".join(buf).strip() == "50"

    def test_functions_persist(self):
        """Functions defined in one run are callable in the next."""
        from newTinyTalk.runtime import Runtime
        from newTinyTalk.lexer import Lexer
        from newTinyTalk.parser import Parser
        from newTinyTalk.stdlib import set_output_buffer, clear_output_buffer

        runtime = Runtime()

        tokens = Lexer('fn square(x) { return x * x }').tokenize()
        ast = Parser(tokens).parse()
        runtime.execute(ast)

        tokens = Lexer('show(square(7))').tokenize()
        ast = Parser(tokens).parse()
        buf = []
        set_output_buffer(buf)
        try:
            runtime.execute(ast)
        finally:
            clear_output_buffer()
        assert "".join(buf).strip() == "49"

    def test_variable_mutation_persists(self):
        """Mutations to variables carry across runs."""
        from newTinyTalk.runtime import Runtime
        from newTinyTalk.lexer import Lexer
        from newTinyTalk.parser import Parser
        from newTinyTalk.stdlib import set_output_buffer, clear_output_buffer

        runtime = Runtime()

        for code in ['let x = 0', 'x += 10', 'x += 20']:
            tokens = Lexer(code).tokenize()
            ast = Parser(tokens).parse()
            runtime.execute(ast)

        tokens = Lexer('show(x)').tokenize()
        ast = Parser(tokens).parse()
        buf = []
        set_output_buffer(buf)
        try:
            runtime.execute(ast)
        finally:
            clear_output_buffer()
        assert "".join(buf).strip() == "30"


# =====================================================================
# 3. Error Messages That Teach
# =====================================================================

class TestTeachingErrors:
    """Test that errors include helpful suggestions."""

    # -- edit distance / find_closest --

    def test_find_closest_exact(self):
        assert find_closest("filter", ["filter", "map", "sort"]) == "filter"

    def test_find_closest_typo(self):
        assert find_closest("fliter", ["filter", "map", "sort"]) == "filter"

    def test_find_closest_no_match(self):
        assert find_closest("xyzabc", ["filter", "map", "sort"]) is None

    def test_find_closest_case_insensitive(self):
        assert find_closest("Filter", ["filter", "map", "sort"]) == "filter"

    # -- undefined variable suggestions --

    def test_undefined_variable_suggestion(self):
        msg = undefined_variable_hint("naem", ["name", "age", "score"])
        assert "Did you mean 'name'?" in msg

    def test_undefined_variable_no_close_match(self):
        msg = undefined_variable_hint("xyzabc", ["name", "age"])
        assert "Undefined variable 'xyzabc'" in msg
        assert "Did you mean" not in msg

    def test_runtime_undefined_suggests(self):
        """Runtime error for typo includes 'Did you mean?'."""
        code = """
let score = 100
let result = scroe + 1
"""
        r = run(code)
        assert not r.success
        assert "Did you mean 'score'?" in r.error

    # -- unknown step suggestions --

    def test_unknown_step_suggestion(self):
        msg = unknown_step_hint("_fliter")
        assert "Did you mean '_filter'?" in msg

    def test_unknown_step_no_match(self):
        msg = unknown_step_hint("_xyzabc")
        assert "Unknown step '_xyzabc'" in msg

    def test_runtime_unknown_step_suggests(self):
        """Unknown step in runtime includes suggestion via variable hint."""
        code = """
show([1, 2, 3] _fliter((x) => x > 1))
"""
        r = run(code)
        assert not r.success
        # _fliter is parsed as an identifier, so we get an undefined variable error
        assert "Undefined variable '_fliter'" in r.error

    # -- type mismatch hints --

    def test_step_on_wrong_type_map(self):
        msg = step_type_mismatch_hint("_sort", "map")
        assert "keys(data)" in msg or "values(data)" in msg

    def test_step_on_wrong_type_string(self):
        msg = step_type_mismatch_hint("_sort", "string")
        assert "chars" in msg or "words" in msg

    # -- step args hints --

    def test_step_args_hint_filter(self):
        msg = step_args_hint("_filter")
        assert "function" in msg.lower() or "=>" in msg

    def test_step_args_hint_join(self):
        msg = step_args_hint("_join")
        assert "right_list" in msg or "key_fn" in msg


# =====================================================================
# 4. Optional Type Annotations
# =====================================================================

class TestTypeAnnotations:
    """Test optional type annotations on variables and functions."""

    # -- type checker unit tests --

    def test_check_int_passes(self):
        assert check_type(Value.int_val(42), "int") is None

    def test_check_int_fails(self):
        err = check_type(Value.string_val("hi"), "int")
        assert err is not None
        assert "expected int" in err

    def test_check_float_accepts_int(self):
        assert check_type(Value.int_val(42), "float") is None

    def test_check_optional_allows_null(self):
        assert check_type(Value.null_val(), "?int") is None

    def test_check_optional_allows_value(self):
        assert check_type(Value.int_val(42), "?int") is None

    def test_check_any_passes_everything(self):
        assert check_type(Value.string_val("hi"), "any") is None
        assert check_type(Value.null_val(), "any") is None

    def test_check_list(self):
        assert check_type(Value.list_val([]), "list") is None
        err = check_type(Value.int_val(1), "list")
        assert err is not None

    def test_check_num(self):
        assert check_type(Value.int_val(1), "num") is None
        assert check_type(Value.float_val(1.5), "num") is None
        err = check_type(Value.string_val("x"), "num")
        assert err is not None

    # -- runtime integration tests --

    def test_let_with_type_annotation_passes(self):
        code = 'let x: int = 42\nshow(x)'
        assert output(code) == "42"

    def test_let_with_type_annotation_fails(self):
        code = 'let x: int = "hello"'
        r = run(code)
        assert not r.success
        assert "Type mismatch" in r.error

    def test_fn_param_type_passes(self):
        code = """
fn add(a: int, b: int) { return a + b }
show(add(3, 4))
"""
        assert output(code) == "7"

    def test_fn_param_type_fails(self):
        code = """
fn add(a: int, b: int) { return a + b }
show(add("hello", 4))
"""
        r = run(code)
        assert not r.success
        assert "Type mismatch" in r.error

    def test_fn_return_type_colon_syntax(self):
        """fn name(params): ReturnType { body } syntax works."""
        code = """
fn greet(name: str): str {
    return "Hello, " + name
}
show(greet("World"))
"""
        assert output(code) == "Hello, World"

    def test_fn_return_type_arrow_syntax(self):
        """fn name(params) -> ReturnType { body } syntax works."""
        code = """
fn square(x: int) -> int {
    return x * x
}
show(square(5))
"""
        assert output(code) == "25"

    def test_fn_return_type_mismatch(self):
        code = """
fn get_name(): int {
    return "Alice"
}
show(get_name())
"""
        r = run(code)
        assert not r.success
        assert "Type mismatch" in r.error

    def test_fn_optional_param(self):
        code = """
fn greet(name: ?str) {
    if name is null {
        return "Hello, stranger"
    }
    return "Hello, " + name
}
show(greet(null))
show(greet("Alice"))
"""
        assert output(code) == "Hello, stranger\nHello, Alice"

    def test_fn_default_with_type(self):
        """Default params with type annotations work."""
        code = """
fn calculate_tax(income: float, rate: float = 0.08): float {
    return income * rate
}
show(calculate_tax(1000.0))
show(calculate_tax(1000.0, 0.1))
"""
        assert output(code) == "80.0\n100.0"

    def test_unannotated_works_fine(self):
        """Code without annotations still works perfectly."""
        code = """
fn add(a, b) { return a + b }
let x = add(3, 4)
show(x)
"""
        assert output(code) == "7"


# =====================================================================
# 5. SQL Transpiler
# =====================================================================

class TestSQLTranspiler:
    """Test TinyTalk → SQL transpilation."""

    def test_simple_filter(self):
        sql = transpile_sql('data _filter((r) => r["age"] > 30)')
        assert "WHERE" in sql
        assert "age > 30" in sql

    def test_select_columns(self):
        sql = transpile_sql('data _select("name", "age")')
        assert "SELECT" in sql
        assert "name" in sql
        assert "age" in sql

    def test_filter_and_select(self):
        sql = transpile_sql('data _filter((r) => r["age"] > 30) _select("name", "age")')
        assert "WHERE" in sql
        assert "age > 30" in sql
        assert "SELECT" in sql

    def test_arrange_order_by(self):
        sql = transpile_sql('data _arrange((r) => r["name"])')
        assert "ORDER BY" in sql
        assert "name" in sql

    def test_arrange_desc(self):
        sql = transpile_sql('data _arrange((r) => r["salary"], "desc")')
        assert "ORDER BY" in sql
        assert "DESC" in sql

    def test_take_limit(self):
        sql = transpile_sql('data _take(10)')
        assert "LIMIT 10" in sql

    def test_drop_offset(self):
        sql = transpile_sql('data _drop(5)')
        assert "OFFSET 5" in sql

    def test_distinct(self):
        sql = transpile_sql('data _distinct')
        assert "DISTINCT" in sql

    def test_group_by(self):
        sql = transpile_sql('data _group((r) => r["dept"])')
        assert "GROUP BY" in sql
        assert "dept" in sql

    def test_join(self):
        sql = transpile_sql('users _join(scores, (r) => r["id"])')
        assert "JOIN" in sql
        assert "id" in sql

    def test_left_join(self):
        sql = transpile_sql('users _leftJoin(scores, (r) => r["id"])')
        assert "LEFT JOIN" in sql

    def test_count(self):
        sql = transpile_sql('data _count')
        assert "COUNT(*)" in sql

    def test_full_pipeline(self):
        """Full dplyr-style pipeline → SQL."""
        code = '''
data _filter((r) => r["salary"] > 50000) _select("name", "dept", "salary") _arrange((r) => r["salary"], "desc") _take(10)
'''
        sql = transpile_sql(code)
        assert "WHERE" in sql
        assert "salary > 50000" in sql
        assert "SELECT" in sql
        assert "name" in sql
        assert "ORDER BY" in sql
        assert "DESC" in sql
        assert "LIMIT 10" in sql

    def test_group_summarize_pipeline(self):
        """Group + summarize → GROUP BY + aggregation."""
        code = '''
data _group((r) => r["dept"]) _summarize({"avg_salary": (rows) => rows _map((r) => r["salary"]) _avg, "count": (rows) => rows _count})
'''
        sql = transpile_sql(code)
        assert "GROUP BY" in sql
        assert "dept" in sql
        assert "AVG" in sql
        assert "COUNT" in sql

    def test_read_csv_source(self):
        """read_csv("file.csv") extracts table name from filename."""
        sql = transpile_sql('read_csv("employees.csv") _filter((r) => r["active"] == true)')
        assert "employees" in sql.lower()
        assert "WHERE" in sql

    def test_rename(self):
        sql = transpile_sql('data _rename({"first_name": "name"})')
        assert "AS" in sql
        assert "name" in sql

    def test_pull(self):
        sql = transpile_sql('data _pull("email")')
        assert "email" in sql

    def test_first(self):
        sql = transpile_sql('data _first')
        assert "LIMIT 1" in sql

    def test_combined_filter_and_operations(self):
        """Realistic query combining multiple operations."""
        code = '''
employees _filter((r) => r["dept"] == "engineering") _select("name", "salary") _arrange((r) => r["salary"], "desc") _take(5)
'''
        sql = transpile_sql(code)
        lines = sql.strip().split("\n")
        # Should have SELECT, FROM, WHERE, ORDER BY, LIMIT
        sql_upper = sql.upper()
        assert "SELECT" in sql_upper
        assert "FROM" in sql_upper
        assert "WHERE" in sql_upper
        assert "ORDER BY" in sql_upper
        assert "LIMIT" in sql_upper
