"""
Tests for _pivot, _unpivot, and _window step chain operators.
"""

import pytest
from newTinyTalk import TinyTalkKernel, RunResult


def run(code: str) -> RunResult:
    return TinyTalkKernel().run(code)


def output(code: str) -> str:
    return run(code).output.strip()


def value(code: str):
    r = run(code)
    assert r.success, f"Code failed: {r.error}"
    return r.value.to_python() if r.value else None


# ===== _pivot =====

class TestPivot:
    def test_basic_pivot(self):
        """Long to wide: 2 regions × 2 products → 2 rows with product columns."""
        r = run('''
let data = [
    {"region": "East", "product": "A", "rev": 100},
    {"region": "East", "product": "B", "rev": 200},
    {"region": "West", "product": "A", "rev": 150},
    {"region": "West", "product": "B", "rev": 300}
]
let wide = data _pivot((r) => r["region"], (r) => r["product"], (r) => r["rev"])
show(len(wide))
show(wide _first)
''')
        assert r.success
        lines = r.output.strip().split("\n")
        assert lines[0] == "2"
        assert "A: 100" in lines[1]
        assert "B: 200" in lines[1]

    def test_pivot_preserves_all_columns(self):
        """All unique column values appear in every pivoted row."""
        r = run('''
let data = [
    {"name": "Alice", "subj": "math", "grade": 95},
    {"name": "Alice", "subj": "sci",  "grade": 88},
    {"name": "Bob",   "subj": "math", "grade": 72}
]
let wide = data _pivot((r) => r["name"], (r) => r["subj"], (r) => r["grade"])
for row in wide { show(row) }
''')
        assert r.success
        lines = r.output.strip().split("\n")
        # Bob should have null for sci
        assert "null" in lines[1]

    def test_pivot_single_row(self):
        r = run('''
let data = [{"k": "A", "col": "x", "val": 1}]
let wide = data _pivot((r) => r["k"], (r) => r["col"], (r) => r["val"])
show(len(wide))
''')
        assert r.success
        assert r.output.strip() == "1"

    def test_pivot_requires_three_args(self):
        r = run('let d = [1,2,3]\nd _pivot((x) => x)')
        assert not r.success
        assert "requires" in r.error.lower()


# ===== _unpivot =====

class TestUnpivot:
    def test_basic_unpivot(self):
        """Wide to long: each non-id column becomes a (variable, value) row."""
        r = run('''
let data = [
    {"name": "Alice", "math": 95, "sci": 88},
    {"name": "Bob",   "math": 72, "sci": 91}
]
let long = data _unpivot(["name"])
show(len(long))
for row in long { show(row) }
''')
        assert r.success
        lines = r.output.strip().split("\n")
        assert lines[0] == "4"  # 2 people × 2 subjects
        assert "variable: math" in lines[1]
        assert "value: 95" in lines[1]

    def test_unpivot_single_id(self):
        r = run('''
let data = [{"id": 1, "a": 10, "b": 20}]
let long = data _unpivot(["id"])
show(len(long))
''')
        assert r.success
        assert r.output.strip() == "2"

    def test_unpivot_multiple_ids(self):
        r = run('''
let data = [{"dept": "eng", "team": "A", "q1": 100, "q2": 200}]
let long = data _unpivot(["dept", "team"])
show(len(long))
for row in long { show(row) }
''')
        assert r.success
        lines = r.output.strip().split("\n")
        assert lines[0] == "2"
        # Both id columns should be preserved
        assert "dept: eng" in lines[1]
        assert "team: A" in lines[1]

    def test_unpivot_requires_list(self):
        r = run('let d = [{"a": 1}]\nd _unpivot("a")')
        assert not r.success
        assert "requires" in r.error.lower()


# ===== _window =====

class TestWindow:
    def test_rolling_avg(self):
        r = run('''
let data = [10, 20, 30, 40, 50]
let result = data _window(3, (w) => round(w _avg, 1))
show(result)
''')
        assert r.success
        # Window 1: [10] → 10.0
        # Window 2: [10, 20] → 15.0
        # Window 3: [10, 20, 30] → 20.0
        # Window 4: [20, 30, 40] → 30.0
        # Window 5: [30, 40, 50] → 40.0
        assert r.output.strip() == "[10.0, 15.0, 20.0, 30.0, 40.0]"

    def test_rolling_sum(self):
        r = run('''
let data = [1, 2, 3, 4, 5]
let result = data _window(2, (w) => w _sum)
show(result)
''')
        assert r.success
        assert r.output.strip() == "[1, 3, 5, 7, 9]"

    def test_rolling_max(self):
        r = run('''
let data = [3, 1, 4, 1, 5, 9, 2, 6]
let result = data _window(3, (w) => w _max)
show(result)
''')
        assert r.success
        assert r.output.strip() == "[3, 3, 4, 4, 5, 9, 9, 9]"

    def test_rolling_count(self):
        r = run('''
let data = [1, 2, 3, 4, 5]
let result = data _window(3, (w) => w _count)
show(result)
''')
        assert r.success
        assert r.output.strip() == "[1, 2, 3, 3, 3]"

    def test_window_size_1(self):
        """Window of 1 is just a map."""
        r = run('''
let data = [10, 20, 30]
let result = data _window(1, (w) => w _first)
show(result)
''')
        assert r.success
        assert r.output.strip() == "[10, 20, 30]"

    def test_window_full_size(self):
        """Window size >= list length means growing windows reaching full."""
        r = run('''
let data = [1, 2, 3]
let result = data _window(10, (w) => w _sum)
show(result)
''')
        assert r.success
        # All windows start from index 0
        assert r.output.strip() == "[1, 3, 6]"

    def test_window_requires_two_args(self):
        r = run("let d = [1,2,3]\nd _window(3)")
        assert not r.success
        assert "requires" in r.error.lower()

    def test_window_with_step_chain(self):
        """_window can be chained with other steps."""
        r = run('''
let data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
let result = data _window(3, (w) => w _avg) _filter((x) => x > 5) _count
show(result)
''')
        assert r.success
        assert int(r.output.strip()) > 0


# ===== Integration: pivot + unpivot + window =====

class TestReshapeIntegration:
    def test_pivot_then_unpivot(self):
        """Round-trip: pivot → unpivot should recover the data."""
        r = run('''
let data = [
    {"name": "A", "metric": "x", "val": 1},
    {"name": "A", "metric": "y", "val": 2},
    {"name": "B", "metric": "x", "val": 3},
    {"name": "B", "metric": "y", "val": 4}
]
let wide = data _pivot((r) => r["name"], (r) => r["metric"], (r) => r["val"])
let long = wide _unpivot(["_index"])
show(long _count)
''')
        assert r.success
        # Should have 4 rows (2 names × 2 metrics)
        assert r.output.strip() == "4"

    def test_window_then_filter(self):
        """Compute rolling avg, then filter for values above threshold."""
        r = run('''
let prices = [100, 102, 98, 105, 110, 108, 115, 120]
let ma = prices _window(3, (w) => round(w _avg, 1))
let above = ma _filter((x) => x > 105) _count
show(above)
''')
        assert r.success
        assert int(r.output.strip()) > 0

    def test_unpivot_then_group(self):
        r = run('''
let data = [
    {"id": 1, "a": 10, "b": 20},
    {"id": 2, "a": 30, "b": 40}
]
let long = data _unpivot(["id"])
let grouped = long _group((r) => r["variable"])
show(keys(grouped))
''')
        assert r.success
        assert "a" in r.output
        assert "b" in r.output
