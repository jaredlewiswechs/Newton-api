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
