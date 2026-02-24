"""
Tests for the TinyTalk → Python transpiler.
Validates both output correctness and round-trip equivalence.
"""

import pytest
import io
import contextlib

from newTinyTalk import TinyTalkKernel, transpile, transpile_pandas


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_tt(code: str) -> str:
    """Run TinyTalk code, return stdout."""
    return TinyTalkKernel().run(code).output.strip()


def run_py(code: str) -> str:
    """Execute transpiled Python code, return stdout."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(code, {"__builtins__": __builtins__})
    return buf.getvalue().strip()


def assert_roundtrip(tt_code: str):
    """Assert that TinyTalk output matches transpiled Python output."""
    tt_out = run_tt(tt_code)
    py_code = transpile(tt_code)
    py_out = run_py(py_code)
    assert tt_out == py_out, (
        f"Round-trip mismatch:\n"
        f"  TinyTalk: {tt_out!r}\n"
        f"  Python:   {py_out!r}\n"
        f"  Code:\n{py_code}"
    )


# ---------------------------------------------------------------------------
# Transpiler output tests
# ---------------------------------------------------------------------------

class TestTranspilerBasics:
    def test_literal_int(self):
        assert "42" in transpile("show(42)")

    def test_literal_string(self):
        assert '"hello"' in transpile('show("hello")')

    def test_variable_assignment(self):
        py = transpile("let x = 10")
        assert "x = 10" in py

    def test_const_assignment(self):
        py = transpile("const PI_APPROX = 3.14")
        assert "PI_APPROX = 3.14" in py

    def test_boolean_true(self):
        py = transpile("let flag = true")
        assert "True" in py

    def test_boolean_false(self):
        py = transpile("let flag = false")
        assert "False" in py

    def test_null(self):
        py = transpile("let x = null")
        assert "None" in py

    def test_math_constants(self):
        py = transpile("show(PI)")
        assert "math.pi" in py
        assert "import math" in py


class TestTranspilerControlFlow:
    def test_if_else(self):
        py = transpile('if true { show("yes") } else { show("no") }')
        assert "if True:" in py
        assert "else:" in py

    def test_for_loop(self):
        py = transpile("for i in range(5) { show(i) }")
        assert "for i in" in py

    def test_while_loop(self):
        py = transpile("let x = 0\nwhile x < 5 { x += 1 }")
        assert "while" in py

    def test_function_def(self):
        py = transpile("fn add(a, b) { return a + b }")
        assert "def add(a, b):" in py
        assert "return" in py

    def test_break_continue(self):
        py = transpile("""
for i in range(10) {
    if i == 5 { break }
    if i % 2 == 0 { continue }
}
""")
        assert "break" in py
        assert "continue" in py


class TestTranspilerExpressions:
    def test_binary_ops(self):
        py = transpile("show(2 + 3 * 4)")
        assert "+" in py
        assert "*" in py

    def test_comparison(self):
        py = transpile("show(5 > 3)")
        assert ">" in py

    def test_is_operator(self):
        py = transpile("show(5 is 5)")
        assert "==" in py

    def test_has_operator(self):
        py = transpile("show([1,2,3] has 2)")
        assert "in" in py

    def test_ternary(self):
        py = transpile("let x = true ? 1 : 0")
        assert "if" in py
        assert "else" in py

    def test_lambda(self):
        py = transpile("let f = (x) => x * 2")
        assert "lambda" in py

    def test_string_interpolation(self):
        py = transpile('let name = "world"\nshow("hello {name}")')
        assert "f\"" in py

    def test_array_literal(self):
        py = transpile("let a = [1, 2, 3]")
        assert "[1, 2, 3]" in py

    def test_map_literal(self):
        py = transpile('let m = {"a": 1, "b": 2}')
        assert '"a": 1' in py


class TestTranspilerStepChains:
    def test_filter(self):
        py = transpile("let r = [1,2,3,4,5] _filter((x) => x > 2)")
        assert "for x in" in py or "filter" in py

    def test_map(self):
        py = transpile("let r = [1,2,3] _map((x) => x * 2)")
        assert "for x in" in py or "map" in py

    def test_sort(self):
        py = transpile("let r = [3,1,2] _sort")
        assert "sorted" in py

    def test_sortBy(self):
        py = transpile('let r = data _sortBy((x) => x["age"])')
        assert "sorted" in py

    def test_reverse(self):
        py = transpile("let r = [1,2,3] _reverse")
        assert "reversed" in py

    def test_take(self):
        py = transpile("let r = [1,2,3,4,5] _take(3)")
        assert "[:3]" in py

    def test_drop(self):
        py = transpile("let r = [1,2,3,4,5] _drop(2)")
        assert "[2:]" in py

    def test_first(self):
        py = transpile("let r = [1,2,3] _first")
        assert "[0]" in py

    def test_last(self):
        py = transpile("let r = [1,2,3] _last")
        assert "[-1]" in py

    def test_unique(self):
        py = transpile("let r = [1,1,2,2,3] _unique")
        assert "dict.fromkeys" in py

    def test_count(self):
        py = transpile("let r = [1,2,3] _count")
        assert "len" in py

    def test_sum(self):
        py = transpile("let r = [1,2,3] _sum")
        assert "sum" in py

    def test_avg(self):
        py = transpile("let r = [1,2,3] _avg")
        assert "sum" in py
        assert "len" in py

    def test_min_max(self):
        py = transpile("let r = [1,2,3] _min")
        assert "min" in py
        py = transpile("let r = [1,2,3] _max")
        assert "max" in py

    def test_flatten(self):
        py = transpile("let r = [[1,2],[3,4]] _flatten")
        assert "sublist" in py or "flatten" in py

    def test_chunk(self):
        py = transpile("let r = [1,2,3,4,5,6] _chunk(2)")
        assert "range" in py

    def test_reduce(self):
        py = transpile("let r = [1,2,3,4] _reduce((a, b) => a + b, 0)")
        assert "reduce" in py

    def test_chain_multiple(self):
        py = transpile("let r = data _filter((x) => x > 0) _sort _take(5)")
        assert "sorted" in py
        assert "[:5]" in py

    def test_pivot(self):
        py = transpile('data _pivot((r) => r["k1"], (r) => r["k2"], (r) => r["v"])')
        assert "lambda" in py

    def test_unpivot(self):
        py = transpile('data _unpivot(["id"])')
        assert "variable" in py

    def test_window(self):
        py = transpile("data _window(3, (w) => w)")
        assert "range" in py


class TestTranspilerBuiltins:
    def test_len(self):
        py = transpile("show(len([1,2,3]))")
        assert "len" in py

    def test_split(self):
        py = transpile('show(split("a,b,c", ","))')
        assert ".split" in py

    def test_join(self):
        py = transpile('show(join(["a","b","c"], "-"))')
        assert ".join" in py

    def test_upcase(self):
        py = transpile('show(upcase("hello"))')
        assert ".upper()" in py

    def test_downcase(self):
        py = transpile('show(downcase("HELLO"))')
        assert ".lower()" in py

    def test_trim(self):
        py = transpile('show(trim("  hello  "))')
        assert ".strip()" in py

    def test_math_functions(self):
        py = transpile("show(sqrt(16))")
        assert "math.sqrt" in py

    def test_append(self):
        py = transpile('let a = []\nappend(a, 1)')
        assert ".append(" in py

    def test_keys(self):
        py = transpile('show(keys({"a": 1}))')
        assert ".keys()" in py

    def test_assert(self):
        py = transpile('assert(true, "should be true")')
        assert "assert True" in py

    def test_assert_equal(self):
        py = transpile("assert_equal(1, 1)")
        assert "assert 1 == 1" in py


class TestTranspilerDplyrVerbs:
    def test_select(self):
        py = transpile('data _select(["name", "age"])')
        assert "row" in py

    def test_mutate(self):
        py = transpile('data _mutate((r) => {"doubled": r["x"] * 2})')
        assert "row" in py or "**" in py

    def test_rename(self):
        py = transpile('data _rename({"old": "new"})')
        assert "get" in py or "rename" in py

    def test_pull(self):
        py = transpile('data _pull("name")')
        assert "row" in py

    def test_arrange(self):
        py = transpile('data _arrange((r) => r["age"])')
        assert "sorted" in py


# ---------------------------------------------------------------------------
# Round-trip equivalence tests (TinyTalk output == transpiled Python output)
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_arithmetic(self):
        assert_roundtrip("show(2 + 3 * 4)")

    def test_string_ops(self):
        assert_roundtrip('show(upcase("hello"))')

    def test_filter_sort_take(self):
        assert_roundtrip(
            "let data = [1,2,3,4,5,6,7,8,9,10]\n"
            "let r = data _filter((x) => x > 3) _sort _reverse _take(3)\n"
            "show(r)"
        )

    def test_function(self):
        assert_roundtrip("""
fn double(n) {
    return n * 2
}
show(double(21))
""")

    def test_for_loop(self):
        assert_roundtrip("""
let total = 0
for i in range(5) {
    total += i
}
show(total)
""")

    def test_map_step(self):
        assert_roundtrip(
            "let r = [1,2,3] _map((x) => x * x)\nshow(r)"
        )

    def test_sum_avg(self):
        assert_roundtrip(
            "let data = [10, 20, 30]\nshow(data _sum)\nshow(data _avg)"
        )

    def test_conditional(self):
        assert_roundtrip(
            "show(true ? \"yes\" : \"no\")"
        )

    def test_string_interpolation(self):
        assert_roundtrip(
            'let x = 42\nshow("{x} is the answer")'
        )

    def test_math(self):
        assert_roundtrip("show(round(3.14159, 2))")

    def test_nested_chain(self):
        assert_roundtrip(
            "let r = [5,3,1,4,2] _sort _reverse _first\nshow(r)"
        )


# ---------------------------------------------------------------------------
# Pandas mode tests (structural — we test that pandas code is generated)
# ---------------------------------------------------------------------------

class TestPandasMode:
    def test_generates_pandas_import(self):
        py = transpile_pandas("data _filter((x) => x > 0)")
        assert "import pandas as pd" in py
        assert "pd.DataFrame" in py

    def test_filter_uses_apply(self):
        py = transpile_pandas("data _filter((r) => r > 0)")
        assert ".apply(" in py

    def test_head(self):
        py = transpile_pandas("data _take(10)")
        assert ".head(10)" in py

    def test_sort_values(self):
        py = transpile_pandas('data _sortBy((r) => r["age"])')
        assert ".sort_values" in py

    def test_drop_duplicates(self):
        py = transpile_pandas("data _unique")
        assert ".drop_duplicates()" in py

    def test_select_columns(self):
        py = transpile_pandas('data _select(["name", "age"])')
        assert '["name", "age"]' in py

    def test_rename(self):
        py = transpile_pandas('data _rename({"old": "new"})')
        assert ".rename(columns=" in py

    def test_melt(self):
        py = transpile_pandas('data _unpivot(["id"])')
        assert ".melt(" in py

    def test_rolling(self):
        py = transpile_pandas("data _window(3, avg_fn)")
        assert ".rolling(3)" in py
