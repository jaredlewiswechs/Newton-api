"""
Core tests for the newTinyTalk language.
Tests lexer, parser, and runtime together via the kernel.
"""

import pytest
from newTinyTalk import TinyTalkKernel, RunResult


@pytest.fixture
def kernel():
    return TinyTalkKernel()


def run(code: str) -> RunResult:
    return TinyTalkKernel().run(code)


def output(code: str) -> str:
    return run(code).output.strip()


def value(code: str):
    return run(code).value


# ===== Literals =====

class TestLiterals:
    def test_integer(self):
        assert output('show(42)') == "42"

    def test_float(self):
        assert output('show(3.14)') == "3.14"

    def test_string(self):
        assert output('show("hello")') == "hello"

    def test_boolean(self):
        assert output('show(true)') == "true"
        assert output('show(false)') == "false"

    def test_null(self):
        assert output('show(null)') == "null"

    def test_hex(self):
        assert output('show(0xFF)') == "255"

    def test_octal(self):
        assert output('show(0o77)') == "63"

    def test_binary(self):
        assert output('show(0b1010)') == "10"


# ===== Arithmetic =====

class TestArithmetic:
    def test_add(self):
        assert output('show(2 + 3)') == "5"

    def test_sub(self):
        assert output('show(10 - 4)') == "6"

    def test_mul(self):
        assert output('show(3 * 7)') == "21"

    def test_div(self):
        assert output('show(10 / 3)') == str(10 / 3)

    def test_floor_div(self):
        assert output('show(10 // 3)') == "3"

    def test_modulo(self):
        assert output('show(10 % 3)') == "1"

    def test_power(self):
        assert output('show(2 ** 10)') == "1024"

    def test_string_concat(self):
        assert output('show("hello" + " " + "world")') == "hello world"

    def test_string_repeat(self):
        assert output('show("ha" * 3)') == "hahaha"

    def test_division_by_zero(self):
        r = run('show(1 / 0)')
        assert not r.success


# ===== Variables =====

class TestVariables:
    def test_let(self):
        assert output('let x = 42\nshow(x)') == "42"

    def test_const(self):
        assert output('const PI = 3.14\nshow(PI)') == "3.14"

    def test_const_reassign_fails(self):
        r = run('const x = 1\nx = 2')
        assert not r.success

    def test_when_constant(self):
        assert output('when PI = 3.14\nshow(PI)') == "3.14"

    def test_compound_assign(self):
        assert output('let x = 10\nx += 5\nshow(x)') == "15"


# ===== Control Flow =====

class TestControlFlow:
    def test_if_true(self):
        assert output('if true { show("yes") }') == "yes"

    def test_if_false(self):
        assert output('if false { show("yes") } else { show("no") }') == "no"

    def test_elif(self):
        assert output('let x = 2\nif x == 1 { show("one") } elif x == 2 { show("two") } else { show("other") }') == "two"

    def test_for_loop(self):
        assert output('for i in range(3) { show(i) }') == "0\n1\n2"

    def test_while_loop(self):
        assert output('let i = 0\nwhile i < 3 { show(i)\ni += 1 }') == "0\n1\n2"

    def test_break(self):
        assert output('for i in range(10) { if i == 3 { break }\nshow(i) }') == "0\n1\n2"

    def test_continue(self):
        assert output('for i in range(5) { if i == 2 { continue }\nshow(i) }') == "0\n1\n3\n4"


# ===== Functions =====

class TestFunctions:
    def test_fn_decl(self):
        assert output('fn square(x) { return x * x }\nshow(square(5))') == "25"

    def test_fn_multiple_args(self):
        assert output('fn add(a, b) { return a + b }\nshow(add(3, 4))') == "7"

    def test_recursion(self):
        code = """
fn fib(n) {
    if n <= 1 { return n }
    return fib(n - 1) + fib(n - 2)
}
show(fib(10))
"""
        assert output(code) == "55"

    def test_lambda(self):
        assert output('let double = (x) => x * 2\nshow(double(5))') == "10"

    def test_closure(self):
        code = """
fn make_adder(n) {
    return (x) => x + n
}
let add5 = make_adder(5)
show(add5(10))
"""
        assert output(code) == "15"

    def test_law_classic(self):
        code = """
law square(x)
    reply x * x
end
show(square(6))
"""
        assert output(code) == "36"

    def test_forge_classic(self):
        code = """
forge greet(name)
    reply "Hello, " + name
end
show(greet("World"))
"""
        assert output(code) == "Hello, World"

    def test_when_function(self):
        code = """
when double(x)
    do x * 2
fin
show(double(7))
"""
        assert output(code) == "14"


# ===== Collections =====

class TestCollections:
    def test_array(self):
        assert output('show([1, 2, 3])') == "[1, 2, 3]"

    def test_array_index(self):
        assert output('let a = [10, 20, 30]\nshow(a[1])') == "20"

    def test_array_negative_index(self):
        assert output('let a = [10, 20, 30]\nshow(a[-1])') == "30"

    def test_map_literal(self):
        assert output('let m = {"a": 1}\nshow(m["a"])') == "1"

    def test_map_dot_access(self):
        assert output('let m = {"name": "Alice"}\nshow(m.name)') == "Alice"

    def test_list_append(self):
        assert output('let a = [1, 2]\nappend(a, 3)\nshow(a)') == "[1, 2, 3]"


# ===== Step Chains =====

class TestStepChains:
    def test_sort(self):
        assert output('show([3, 1, 2] _sort)') == "[1, 2, 3]"

    def test_reverse(self):
        assert output('show([1, 2, 3] _reverse)') == "[3, 2, 1]"

    def test_filter(self):
        assert output('show([1, 2, 3, 4, 5] _filter((x) => x > 3))') == "[4, 5]"

    def test_map(self):
        assert output('show([1, 2, 3] _map((x) => x * 2))') == "[2, 4, 6]"

    def test_take(self):
        assert output('show([1, 2, 3, 4, 5] _take(3))') == "[1, 2, 3]"

    def test_chained(self):
        assert output('show([5, 3, 1, 4, 2] _sort _reverse _take(3))') == "[5, 4, 3]"

    def test_sum(self):
        assert output('show([1, 2, 3, 4, 5] _sum)') == "15"

    def test_unique(self):
        assert output('show([1, 2, 2, 3, 3, 3] _unique)') == "[1, 2, 3]"

    def test_count(self):
        assert output('show([1, 2, 3] _count)') == "3"

    def test_first_last(self):
        assert output('show([1, 2, 3] _first)') == "1"
        assert output('show([1, 2, 3] _last)') == "3"

    def test_flatten(self):
        assert output('show([[1, 2], [3, 4]] _flatten)') == "[1, 2, 3, 4]"

    def test_chunk(self):
        assert output('show([1, 2, 3, 4, 5, 6] _chunk(2))') == "[[1, 2], [3, 4], [5, 6]]"


# ===== Natural Comparisons =====

class TestNaturalComparisons:
    def test_is(self):
        assert output('show(1 is 1)') == "true"
        assert output('show(1 is 2)') == "false"

    def test_isnt(self):
        assert output('show(1 isnt 2)') == "true"

    def test_has(self):
        assert output('show([1, 2, 3] has 2)') == "true"
        assert output('show([1, 2, 3] has 5)') == "false"

    def test_hasnt(self):
        assert output('show([1, 2, 3] hasnt 5)') == "true"

    def test_isin(self):
        assert output('show(2 isin [1, 2, 3])') == "true"

    def test_islike(self):
        assert output('show("hello" islike "hel*")') == "true"
        assert output('show("hello" islike "world*")') == "false"


# ===== Property Conversions =====

class TestProperties:
    def test_str(self):
        assert output('show(42 .str)') == "42"

    def test_int(self):
        assert output('show("42" .int)') == "42"

    def test_float(self):
        assert output('show("3.14" .float)') == "3.14"

    def test_bool(self):
        assert output('show(0 .bool)') == "false"
        assert output('show(1 .bool)') == "true"

    def test_type(self):
        assert output('show(42 .type)') == "int"
        assert output('show("hi" .type)') == "string"

    def test_len(self):
        assert output('show([1, 2, 3] .len)') == "3"
        assert output('show("hello" .len)') == "5"


# ===== String Methods =====

class TestStringMethods:
    def test_upcase(self):
        assert output('show("hello".upcase)') == "HELLO"

    def test_downcase(self):
        assert output('show("HELLO".downcase)') == "hello"

    def test_trim(self):
        assert output('show("  hello  ".trim)') == "hello"

    def test_chars(self):
        assert output('show("abc".chars)') == "[a, b, c]"

    def test_words(self):
        assert output('show("hello world".words)') == "[hello, world]"

    def test_reversed(self):
        assert output('show("abc".reversed)') == "cba"


# ===== Blueprints =====

class TestBlueprints:
    def test_basic_blueprint(self):
        code = """
blueprint Counter
    field value = 0
    forge inc()
        self.value = self.value + 1
        reply self.value
    end
end
let c = Counter(0)
show(c.inc())
show(c.inc())
"""
        assert output(code) == "1\n2"

    def test_struct_modern(self):
        code = """
struct Point {
    x: int,
    y: int,
}
let p = Point(3, 4)
show(p.x)
show(p.y)
"""
        assert output(code) == "3\n4"


# ===== Match Statement (FIXED) =====

class TestMatch:
    def test_basic_match(self):
        code = """
let x = 2
match x {
    1 => "one",
    2 => "two",
    _ => "other",
}
"""
        r = run(code)
        assert r.success

    def test_match_with_output(self):
        code = """
fn describe(x) {
    let result = match x {
        1 => "one",
        2 => "two",
        _ => "other",
    }
    return result
}
show(describe(2))
"""
        assert output(code) == "two"


# ===== Try/Catch (FIXED) =====

class TestTryCatch:
    def test_basic_try(self):
        code = """
try {
    throw "oops"
} catch(e) {
    show("caught: " + e)
}
"""
        assert output(code) == "caught: oops"

    def test_try_no_error(self):
        code = """
try {
    show("ok")
} catch(e) {
    show("error: " + e)
}
"""
        assert output(code) == "ok"


# ===== String Interpolation =====

class TestStringInterpolation:
    def test_basic_interp(self):
        code = """
let name = "World"
show("Hello {name}!")
"""
        assert output(code) == "Hello World!"

    def test_expression_interp(self):
        code = """
let x = 5
show("x squared is {x * x}")
"""
        assert output(code) == "x squared is 25"

    def test_multiple_interp(self):
        code = """
let a = 3
let b = 4
show("{a} + {b} = {a + b}")
"""
        assert output(code) == "3 + 4 = 7"


# ===== Pipe Operator =====

class TestPipe:
    def test_basic_pipe(self):
        code = """
fn double(x) { return x * 2 }
fn add_one(x) { return x + 1 }
show(5 |> double |> add_one)
"""
        assert output(code) == "11"

    def test_r_style_pipe(self):
        code = """
fn double(x) { return x * 2 }
fn add_one(x) { return x + 1 }
show(5 %>% double %>% add_one)
"""
        assert output(code) == "11"

    def test_mixed_pipes(self):
        code = """
fn double(x) { return x * 2 }
fn add_one(x) { return x + 1 }
show(5 |> double %>% add_one)
"""
        assert output(code) == "11"


# ===== Space-Separated Args =====

class TestSpaceArgs:
    def test_show_space_args(self):
        code = """
let name = "World"
show("Hello" name)
"""
        assert output(code) == "Hello World"

    def test_show_mixed_args(self):
        code = """
show("x is" 42 "and y is" 100)
"""
        assert output(code) == "x is 42 and y is 100"


# ===== Bare-Word Strings =====

class TestBareWords:
    def test_print_bare_word(self):
        assert output('show(Hello)') == "Hello"

    def test_print_bare_words_comma(self):
        assert output('show(Hello, World)') == "Hello World"

    def test_print_bare_word_with_bang(self):
        assert output('show(Hello, world!)') == "Hello world!"

    def test_bare_word_does_not_shadow_variable(self):
        code = """
let x = 42
show(x)
"""
        assert output(code) == "42"

    def test_bare_word_mixed_with_variable(self):
        code = """
let name = "Alice"
show(Hello, name)
"""
        assert output(code) == "Hello Alice"


# ===== Builtins =====

class TestBuiltins:
    def test_range(self):
        assert output('show(range(5))') == "[0, 1, 2, 3, 4]"

    def test_len(self):
        assert output('show(len([1, 2, 3]))') == "3"

    def test_sum(self):
        assert output('show(sum([1, 2, 3]))') == "6"

    def test_min_max(self):
        assert output('show(min([3, 1, 2]))') == "1"
        assert output('show(max([3, 1, 2]))') == "3"

    def test_abs(self):
        assert output('show(abs(-5))') == "5"

    def test_sqrt(self):
        assert output('show(sqrt(16))') == "4.0"

    def test_replace(self):
        assert output('show(replace("hello world", "world", "TinyTalk"))') == "hello TinyTalk"

    def test_split(self):
        assert output('show(split("a,b,c", ","))') == "[a, b, c]"

    def test_join(self):
        assert output('show(join(["a", "b", "c"], "-"))') == "a-b-c"

    def test_keys_values(self):
        assert output('show(keys({"a": 1, "b": 2}))') == "[a, b]"

    def test_sort(self):
        assert output('show(sort([3, 1, 2]))') == "[1, 2, 3]"

    def test_reverse(self):
        assert output('show(reverse([1, 2, 3]))') == "[3, 2, 1]"

    def test_type(self):
        assert output('show(type(42))') == "int"
        assert output('show(type("hi"))') == "string"

    def test_trim(self):
        assert output('show(trim("  hello  "))') == "hello"

    def test_upcase_downcase(self):
        assert output('show(upcase("hello"))') == "HELLO"
        assert output('show(downcase("HELLO"))') == "hello"


# ===== Bounds =====

class TestBounds:
    def test_infinite_loop_bounded(self):
        r = run('while true { let x = 1 }')
        assert not r.success
        assert "iterations" in r.error.lower() or "operations" in r.error.lower()


# ===== Assertions =====

class TestAssertions:
    def test_assert_passes(self):
        r = run('assert(true)')
        assert r.success

    def test_assert_fails(self):
        r = run('assert(false, "should fail")')
        assert not r.success

    def test_assert_equal_passes(self):
        r = run('assert_equal(1 + 1, 2)')
        assert r.success

    def test_assert_equal_fails(self):
        r = run('assert_equal(1, 2)')
        assert not r.success


# ===== Bug Fix: stdlib higher-order functions with user-defined fns =====

class TestHigherOrderBuiltins:
    def test_filter_with_lambda(self):
        code = """
let evens = filter((x) => x % 2 == 0, [1, 2, 3, 4, 5, 6])
show(evens)
"""
        assert output(code) == "[2, 4, 6]"

    def test_map_with_lambda(self):
        code = """
let doubled = map_((x) => x * 10, [1, 2, 3])
show(doubled)
"""
        assert output(code) == "[10, 20, 30]"

    def test_reduce_with_lambda(self):
        code = """
let total = reduce((acc, x) => acc + x, [1, 2, 3, 4, 5], 0)
show(total)
"""
        assert output(code) == "15"

    def test_reduce_with_named_fn(self):
        code = """
fn add(a, b) { return a + b }
let total = reduce(add, [1, 2, 3, 4], 0)
show(total)
"""
        assert output(code) == "10"

    def test_filter_with_named_fn(self):
        code = """
fn is_positive(x) { return x > 0 }
let result = filter(is_positive, [-2, -1, 0, 1, 2, 3])
show(result)
"""
        assert output(code) == "[1, 2, 3]"


# ===== Bug Fix: compound assignment on Index/Member targets =====

class TestCompoundAssignTargets:
    def test_list_index_plus_eq(self):
        code = """
let a = [10, 20, 30]
a[1] += 5
show(a)
"""
        assert output(code) == "[10, 25, 30]"

    def test_list_index_minus_eq(self):
        code = """
let a = [10, 20, 30]
a[0] -= 3
show(a)
"""
        assert output(code) == "[7, 20, 30]"

    def test_map_index_plus_eq(self):
        code = """
let m = {"score": 10}
m["score"] += 5
show(m["score"])
"""
        assert output(code) == "15"

    def test_member_plus_eq(self):
        code = """
let m = {"x": 10, "y": 20}
m.x += 100
show(m.x)
"""
        assert output(code) == "110"

    def test_struct_field_compound_assign(self):
        code = """
struct Point { x: int, y: int }
let p = Point(3, 4)
p.x += 10
show(p.x)
"""
        assert output(code) == "13"


# ===== Multi-line Lambdas =====

class TestMultiLineLambdas:
    def test_block_lambda(self):
        code = """
let process = (x) => {
    let doubled = x * 2
    return doubled + 1
}
show(process(5))
"""
        assert output(code) == "11"

    def test_block_lambda_implicit_return(self):
        code = """
let calc = (x) => {
    let y = x + 10
    y * 2
}
show(calc(5))
"""
        assert output(code) == "30"

    def test_block_lambda_in_step_chain(self):
        code = """
let result = [1, 2, 3, 4, 5] _map((x) => {
    let squared = x * x
    return squared + 1
})
show(result)
"""
        assert output(code) == "[2, 5, 10, 17, 26]"

    def test_block_lambda_with_conditional(self):
        code = """
let classify = (x) => {
    if x > 0 { return "positive" }
    if x < 0 { return "negative" }
    return "zero"
}
show(classify(5))
show(classify(-3))
show(classify(0))
"""
        assert output(code) == "positive\nnegative\nzero"

    def test_pipe_lambda_still_works(self):
        """Ensure |x| expr lambdas still work."""
        code = """
let double = |x| x * 2
show(double(7))
"""
        assert output(code) == "14"


# ===== Default Parameters =====

class TestDefaultParams:
    def test_basic_default(self):
        code = """
fn greet(name = "World") {
    return "Hello, " + name
}
show(greet())
show(greet("Alice"))
"""
        assert output(code) == "Hello, World\nHello, Alice"

    def test_multiple_defaults(self):
        code = """
fn make_point(x = 0, y = 0) {
    return [x, y]
}
show(make_point())
show(make_point(5))
show(make_point(3, 4))
"""
        assert output(code) == "[0, 0]\n[5, 0]\n[3, 4]"

    def test_mixed_required_and_default(self):
        code = """
fn repeat_str(s, n = 3) {
    return s * n
}
show(repeat_str("ha"))
show(repeat_str("ho", 2))
"""
        assert output(code) == "hahaha\nhoho"

    def test_default_with_expression(self):
        code = """
const BASE = 10
fn add_base(x, base = BASE) {
    return x + base
}
show(add_base(5))
show(add_base(5, 20))
"""
        assert output(code) == "15\n25"


# ===== _reduce Step Chain =====

class TestReduceStep:
    def test_reduce_sum(self):
        code = """
show([1, 2, 3, 4, 5] _reduce((acc, x) => acc + x, 0))
"""
        assert output(code) == "15"

    def test_reduce_product(self):
        code = """
show([1, 2, 3, 4, 5] _reduce((acc, x) => acc * x, 1))
"""
        assert output(code) == "120"

    def test_reduce_without_initial(self):
        code = """
show([1, 2, 3, 4] _reduce((acc, x) => acc + x))
"""
        assert output(code) == "10"

    def test_reduce_string_concat(self):
        code = """
show(["a", "b", "c"] _reduce((acc, x) => acc + x, ""))
"""
        assert output(code) == "abc"

    def test_reduce_in_chain(self):
        code = """
show([1, 2, 3, 4, 5] _filter((x) => x > 2) _reduce((acc, x) => acc + x, 0))
"""
        assert output(code) == "12"

    def test_reduce_empty_with_initial(self):
        code = """
show([] _reduce((acc, x) => acc + x, 42))
"""
        assert output(code) == "42"

    def test_reduce_empty_without_initial(self):
        code = """
show([] _reduce((acc, x) => acc + x))
"""
        assert output(code) == "null"


# ===== CSV I/O =====

import tempfile
import os

class TestCSV:
    def test_read_write_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            f.write("name,age,score\nAlice,25,95.5\nBob,30,87\n")
            path = f.name
        try:
            code = f'''
let data = read_csv("{path}")
show(len(data))
show(data[0]["name"])
show(data[1]["age"])
'''
            assert output(code) == "2\nAlice\n30"
        finally:
            os.unlink(path)

    def test_write_csv_roundtrip(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            code = f'''
let data = [{{"name": "Alice", "score": 90}}, {{"name": "Bob", "score": 85}}]
write_csv(data, "{path}")
let loaded = read_csv("{path}")
show(len(loaded))
show(loaded[0]["name"])
show(loaded[1]["score"])
'''
            assert output(code) == "2\nAlice\n85"
        finally:
            os.unlink(path)

    def test_csv_auto_type(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            f.write("val,flag\n42,true\n3.14,false\n")
            path = f.name
        try:
            code = f'''
let data = read_csv("{path}")
show(type(data[0]["val"]))
show(type(data[1]["val"]))
show(data[0]["flag"])
'''
            assert output(code) == "int\nfloat\ntrue"
        finally:
            os.unlink(path)


# ===== JSON I/O =====

class TestJSON:
    def test_read_write_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('[{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]')
            path = f.name
        try:
            code = f'''
let data = read_json("{path}")
show(len(data))
show(data[0]["name"])
show(data[1]["age"])
'''
            assert output(code) == "2\nAlice\n30"
        finally:
            os.unlink(path)

    def test_write_json_roundtrip(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            code = f'''
let data = {{"name": "Alice", "scores": [90, 85, 95]}}
write_json(data, "{path}")
let loaded = read_json("{path}")
show(loaded["name"])
show(loaded["scores"])
'''
            assert output(code) == "Alice\n[90, 85, 95]"
        finally:
            os.unlink(path)

    def test_parse_json(self):
        code = '''
let data = parse_json("[1, 2, 3]")
show(data)
show(type(data))
'''
        assert output(code) == "[1, 2, 3]\nlist"

    def test_to_json(self):
        code = '''
let s = to_json({"a": 1, "b": [2, 3]})
show(s)
'''
        r = run(code)
        assert r.success
        import json
        parsed = json.loads(r.output.strip())
        assert parsed == {"a": 1, "b": [2, 3]}


# ===== Date/Time =====

class TestDates:
    def test_date_now(self):
        code = '''
let now = date_now()
show(len(now) > 0)
'''
        assert output(code) == "true"

    def test_date_parse(self):
        code = '''
show(date_parse("2024-03-15"))
'''
        assert output(code) == "2024-03-15 00:00:00"

    def test_date_parse_iso(self):
        code = '''
show(date_parse("2024-03-15T10:30:00"))
'''
        assert output(code) == "2024-03-15 10:30:00"

    def test_date_floor_week(self):
        code = '''
show(date_floor("2024-03-15", "week"))
'''
        # 2024-03-15 is Friday, Monday = 2024-03-11
        assert output(code) == "2024-03-11 00:00:00"

    def test_date_floor_month(self):
        code = '''
show(date_floor("2024-03-15 14:30:00", "month"))
'''
        assert output(code) == "2024-03-01 00:00:00"

    def test_date_add_days(self):
        code = '''
show(date_add("2024-03-15", 10, "days"))
'''
        assert output(code) == "2024-03-25 00:00:00"

    def test_date_add_negative(self):
        code = '''
show(date_add("2024-03-15", -5, "days"))
'''
        assert output(code) == "2024-03-10 00:00:00"

    def test_date_diff(self):
        code = '''
let d = date_diff("2024-03-20", "2024-03-15", "days")
show(d)
'''
        assert output(code) == "5.0"

    def test_date_format(self):
        code = '''
show(date_format("2024-03-15", "%B %d, %Y"))
'''
        assert output(code) == "March 15, 2024"


# ===== New Step Chains: _sortBy, _join, _mapValues, _each =====

class TestNewStepChains:
    def test_sort_by(self):
        code = '''
let people = [{"name": "Charlie", "age": 20}, {"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
let sorted = people _sortBy((p) => p["age"])
show(sorted[0]["name"])
show(sorted[2]["name"])
'''
        assert output(code) == "Charlie\nAlice"

    def test_sort_by_string(self):
        code = '''
let people = [{"name": "Charlie"}, {"name": "Alice"}, {"name": "Bob"}]
let sorted = people _sortBy((p) => p["name"])
show(sorted[0]["name"])
'''
        assert output(code) == "Alice"

    def test_join(self):
        code = '''
let users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
let scores = [{"id": 1, "score": 95}, {"id": 2, "score": 87}]
let joined = users _join(scores, (r) => r["id"])
show(joined[0]["name"])
show(joined[0]["score"])
show(joined[1]["name"])
'''
        assert output(code) == "Alice\n95\nBob"

    def test_join_no_match(self):
        code = '''
let left = [{"id": 1, "name": "Alice"}, {"id": 3, "name": "Charlie"}]
let right = [{"id": 1, "score": 95}]
let joined = left _join(right, (r) => r["id"])
show(len(joined))
show(joined[0]["name"])
'''
        assert output(code) == "1\nAlice"

    def test_map_values(self):
        code = '''
let grouped = {"math": [90, 85, 92], "science": [88, 76, 95]}
let counts = grouped _mapValues((xs) => xs _count)
show(counts["math"])
show(counts["science"])
'''
        assert output(code) == "3\n3"

    def test_map_values_with_avg(self):
        code = '''
let grouped = {"a": [10, 20, 30], "b": [5, 15]}
let avgs = grouped _mapValues((xs) => xs _avg)
show(avgs["a"])
show(avgs["b"])
'''
        assert output(code) == "20.0\n10.0"

    def test_each(self):
        code = '''
let results = []
[1, 2, 3] _each((x) => { append(results, x * 10) })
show(results)
'''
        assert output(code) == "[10, 20, 30]"

    def test_each_returns_original(self):
        code = '''
let data = [1, 2, 3]
let same = data _each((x) => x)
show(same)
'''
        assert output(code) == "[1, 2, 3]"


# ===== dplyr-Style Verbs =====

class TestDplyrSelect:
    def test_select_list_of_cols(self):
        code = '''
let people = [{"name": "Alice", "age": 30, "city": "NYC"}, {"name": "Bob", "age": 25, "city": "LA"}]
let slim = people _select(["name", "age"])
show(slim[0])
show(slim[1])
'''
        assert output(code) == '{name: Alice, age: 30}\n{name: Bob, age: 25}'

    def test_select_string_args(self):
        code = '''
let data = [{"a": 1, "b": 2, "c": 3}]
let r = data _select("a", "c")
show(r[0])
'''
        assert output(code) == '{a: 1, c: 3}'

    def test_select_missing_col(self):
        code = '''
let data = [{"name": "Alice"}]
let r = data _select(["name", "age"])
show(r[0]["age"])
'''
        assert output(code) == "null"


class TestDplyrMutate:
    def test_mutate_add_column(self):
        code = '''
let people = [{"name": "Alice", "salary": 100}, {"name": "Bob", "salary": 80}]
let enriched = people _mutate((r) => {"bonus": r["salary"] * 0.1})
show(enriched[0]["bonus"])
show(enriched[1]["bonus"])
'''
        assert output(code) == "10.0\n8.0"

    def test_mutate_overwrite_column(self):
        code = '''
let data = [{"x": 10}]
let r = data _mutate((row) => {"x": row["x"] * 2, "y": 99})
show(r[0]["x"])
show(r[0]["y"])
'''
        assert output(code) == "20\n99"

    def test_mutate_preserves_existing(self):
        code = '''
let data = [{"a": 1, "b": 2}]
let r = data _mutate((row) => {"c": 3})
show(r[0]["a"])
show(r[0]["b"])
show(r[0]["c"])
'''
        assert output(code) == "1\n2\n3"


class TestDplyrSummarize:
    def test_summarize_on_list(self):
        code = '''
let data = [{"val": 10}, {"val": 20}, {"val": 30}]
let summary = data _summarize({
    "total": (rows) => rows _map((r) => r["val"]) _sum,
    "n": (rows) => rows _count
})
show(summary["total"])
show(summary["n"])
'''
        assert output(code) == "60\n3"

    def test_summarize_on_grouped_map(self):
        code = '''
let data = [
    {"dept": "eng", "salary": 100},
    {"dept": "eng", "salary": 120},
    {"dept": "sales", "salary": 80}
]
let result = data _group((r) => r["dept"]) _summarize({
    "avg_salary": (rows) => rows _map((r) => r["salary"]) _avg,
    "count": (rows) => rows _count
})
show(len(result))
show(result[0]["count"] + result[1]["count"])
'''
        assert output(code) == "2\n3"

    def test_summarize_avg(self):
        code = '''
let scores = [{"s": 90}, {"s": 80}, {"s": 70}]
let r = scores _summarize({
    "mean": (rows) => rows _map((r) => r["s"]) _avg
})
show(r["mean"])
'''
        assert output(code) == "80.0"


class TestDplyrRename:
    def test_rename_columns(self):
        code = '''
let data = [{"first_name": "Alice", "age": 30}]
let r = data _rename({"first_name": "name"})
show(r[0]["name"])
show(r[0]["age"])
'''
        assert output(code) == "Alice\n30"

    def test_rename_multiple(self):
        code = '''
let data = [{"a": 1, "b": 2, "c": 3}]
let r = data _rename({"a": "x", "b": "y"})
show(r[0]["x"])
show(r[0]["y"])
show(r[0]["c"])
'''
        assert output(code) == "1\n2\n3"


class TestDplyrArrange:
    def test_arrange_ascending(self):
        code = '''
let data = [{"name": "C", "val": 30}, {"name": "A", "val": 10}, {"name": "B", "val": 20}]
let sorted = data _arrange((r) => r["val"])
show(sorted[0]["name"])
show(sorted[2]["name"])
'''
        assert output(code) == "A\nC"

    def test_arrange_descending(self):
        code = '''
let data = [{"name": "C", "val": 30}, {"name": "A", "val": 10}, {"name": "B", "val": 20}]
let sorted = data _arrange((r) => r["val"], "desc")
show(sorted[0]["name"])
show(sorted[2]["name"])
'''
        assert output(code) == "C\nA"


class TestDplyrDistinct:
    def test_distinct_no_args(self):
        code = '''
show([1, 2, 2, 3, 3, 3] _distinct _count)
'''
        assert output(code) == "3"

    def test_distinct_by_function(self):
        code = '''
let data = [{"name": "Alice", "dept": "eng"}, {"name": "Bob", "dept": "eng"}, {"name": "Charlie", "dept": "sales"}]
let r = data _distinct((r) => r["dept"])
show(len(r))
'''
        assert output(code) == "2"

    def test_distinct_by_columns(self):
        code = '''
let data = [{"a": 1, "b": "x"}, {"a": 1, "b": "x"}, {"a": 1, "b": "y"}]
let r = data _distinct(["a", "b"])
show(len(r))
'''
        assert output(code) == "2"


class TestDplyrSlice:
    def test_slice_start_count(self):
        code = '''
show([10, 20, 30, 40, 50] _slice(1, 3))
'''
        assert output(code) == "[20, 30, 40]"

    def test_slice_start_only(self):
        code = '''
show([10, 20, 30, 40, 50] _slice(2))
'''
        assert output(code) == "[30, 40, 50]"


class TestDplyrPull:
    def test_pull_column(self):
        code = '''
let data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
show(data _pull("name"))
'''
        assert output(code) == "[Alice, Bob]"

    def test_pull_numeric(self):
        code = '''
let data = [{"val": 10}, {"val": 20}, {"val": 30}]
show(data _pull("val") _sum)
'''
        assert output(code) == "60"


class TestDplyrGroupBy:
    def test_group_by_alias(self):
        code = '''
let data = [{"dept": "eng", "n": 1}, {"dept": "sales", "n": 2}, {"dept": "eng", "n": 3}]
let g = data _groupBy((r) => r["dept"])
show(len(g["eng"]))
show(len(g["sales"]))
'''
        assert output(code) == "2\n1"


class TestDplyrLeftJoin:
    def test_left_join_all_match(self):
        code = '''
let users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
let scores = [{"id": 1, "score": 95}, {"id": 2, "score": 87}]
let joined = users _leftJoin(scores, (r) => r["id"])
show(joined[0]["name"])
show(joined[0]["score"])
show(len(joined))
'''
        assert output(code) == "Alice\n95\n2"

    def test_left_join_unmatched(self):
        code = '''
let left = [{"id": 1, "name": "Alice"}, {"id": 3, "name": "Charlie"}]
let right = [{"id": 1, "score": 95}]
let joined = left _leftJoin(right, (r) => r["id"])
show(len(joined))
show(joined[0]["name"])
show(joined[0]["score"])
show(joined[1]["name"])
'''
        assert output(code) == "2\nAlice\n95\nCharlie"


class TestDplyrPipeline:
    """End-to-end tests showing dplyr-like data analysis pipelines."""

    def test_full_pipeline(self):
        code = '''
let employees = [
    {"name": "Alice", "dept": "eng", "salary": 120},
    {"name": "Bob", "dept": "eng", "salary": 100},
    {"name": "Charlie", "dept": "sales", "salary": 90},
    {"name": "Diana", "dept": "sales", "salary": 110},
    {"name": "Eve", "dept": "eng", "salary": 130}
]

let result = employees
    _filter((r) => r["salary"] > 95)
    _select(["name", "dept", "salary"])
    _mutate((r) => {"bonus": r["salary"] * 0.1})
    _arrange((r) => r["salary"], "desc")

show(result[0]["name"])
show(result[0]["bonus"])
show(len(result))
'''
        assert output(code) == "Eve\n13.0\n4"

    def test_group_summarize_pipeline(self):
        code = '''
let sales = [
    {"product": "A", "qty": 10},
    {"product": "B", "qty": 20},
    {"product": "A", "qty": 15},
    {"product": "B", "qty": 5}
]

let summary = sales
    _group((r) => r["product"])
    _summarize({
        "total_qty": (rows) => rows _map((r) => r["qty"]) _sum,
        "avg_qty": (rows) => rows _map((r) => r["qty"]) _avg
    })

show(len(summary))
'''
        assert output(code) == "2"

    def test_select_mutate_pull(self):
        code = '''
let data = [{"x": 1, "y": 10}, {"x": 2, "y": 20}, {"x": 3, "y": 30}]
let totals = data
    _mutate((r) => {"total": r["x"] + r["y"]})
    _pull("total")
show(totals)
show(totals _sum)
'''
        assert output(code) == "[11, 22, 33]\n66"
