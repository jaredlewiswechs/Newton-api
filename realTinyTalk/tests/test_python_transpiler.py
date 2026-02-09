"""
═══════════════════════════════════════════════════════════════
ACID TEST: Python Transpiler
Tests all node types and edge cases
═══════════════════════════════════════════════════════════════
"""

import sys
sys.path.insert(0, '.')

from realTinyTalk.lexer import Lexer
from realTinyTalk.parser import Parser, NodeType
from realTinyTalk.backends.python.emitter import PythonEmitter, transpile_to_python


def test_transpile(name: str, code: str, expected_contains: list = None, should_fail: bool = False):
    """Test helper that transpiles and checks output."""
    try:
        result = transpile_to_python(code, include_runtime=False)
        
        if should_fail:
            print(f"❌ {name}: Expected failure but got success")
            return False
            
        # Check expected substrings
        if expected_contains:
            for expected in expected_contains:
                if expected not in result:
                    print(f"❌ {name}: Missing '{expected}'")
                    print(f"   Got: {result[:200]}...")
                    return False
        
        print(f"✅ {name}")
        return True
        
    except Exception as e:
        if should_fail:
            print(f"✅ {name}: Expected failure - {e}")
            return True
        print(f"❌ {name}: {type(e).__name__}: {e}")
        return False


def run_all_tests():
    """Run all transpiler tests."""
    print("=" * 60)
    print("PYTHON TRANSPILER ACID TEST")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    # ═══════════════════════════════════════════════════════════════
    # LITERALS
    # ═══════════════════════════════════════════════════════════════
    print("── Literals ──")
    
    if test_transpile("Integer literal", "let x = 42", ["x = 42"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Float literal", "let x = 3.14", ["x = 3.14"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("String literal", 'let x = "hello"', ['x = "hello"']):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Boolean true", "let x = true", ["x = True"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Boolean false", "let x = false", ["x = False"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Null literal", "let x = null", ["x = None"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # ARRAYS AND MAPS
    # ═══════════════════════════════════════════════════════════════
    print("\n── Arrays & Maps ──")
    
    if test_transpile("Array literal", "let arr = [1, 2, 3]", ["arr = [1, 2, 3]"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Empty array", "let arr = []", ["arr = []"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # BINARY OPERATORS
    # ═══════════════════════════════════════════════════════════════
    print("\n── Binary Operators ──")
    
    if test_transpile("Addition", "let x = 1 + 2", ["x = (1 + 2)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Subtraction", "let x = 5 - 3", ["x = (5 - 3)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Multiplication", "let x = 2 * 3", ["x = (2 * 3)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Division", "let x = 10 / 2", ["x = (10 / 2)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Modulo", "let x = 10 % 3", ["x = (10 % 3)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Power with **", "let x = 2 ** 3", ["x = (2 ** 3)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Power with ^", "let x = 2 ^ 3", ["x = (2 ** 3)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Comparison <", "let x = 1 < 2", ["x = (1 < 2)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Comparison >", "let x = 2 > 1", ["x = (2 > 1)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Comparison <=", "let x = 1 <= 2", ["x = (1 <= 2)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Comparison >=", "let x = 2 >= 1", ["x = (2 >= 1)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Equality ==", "let x = 1 == 1", ["x = (1 == 1)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Inequality !=", "let x = 1 != 2", ["x = (1 != 2)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Logical and", "let x = true and false", ["x = (True and False)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Logical or", "let x = true or false", ["x = (True or False)"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # TINYTALK-SPECIFIC OPERATORS
    # ═══════════════════════════════════════════════════════════════
    print("\n── TinyTalk Operators ──")
    
    if test_transpile("is operator", "let x = 5 is 5", ["tt.is_(5, 5)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("has operator", 'let arr = [1,2,3]\nlet x = arr has 2', ["tt.has("]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("has array contains", "let arr = [1,2,3]\nlet x = arr has 2", ["tt.has(arr, 2)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("islike operator", 'let name = "Newton"\nlet x = name islike "N*"', ["tt.islike(name,"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # PROPERTY ACCESS (MAGIC PROPERTIES)
    # ═══════════════════════════════════════════════════════════════
    print("\n── Property Access ──")
    
    if test_transpile(".upcase property", 'let s = "hello"\nshow(s.upcase)', ['tt.prop(s, "upcase")']):
        passed += 1
    else:
        failed += 1
        
    if test_transpile(".len property", 'let s = "hello"\nshow(s.len)', ['tt.prop(s, "len")']):
        passed += 1
    else:
        failed += 1
        
    if test_transpile(".str conversion", "let x = 5\nshow(x.str)", ["str(x)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile(".reversed property", 'let s = "hello"\nshow(s.reversed)', ['tt.prop(s, "reversed")']):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # FUNCTION CALLS
    # ═══════════════════════════════════════════════════════════════
    print("\n── Function Calls ──")
    
    if test_transpile("show() call", 'show("hello")', ['tt.show("hello")']):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("show() multiple args", 'show("x =" x)', ['tt.show("x =", x)']):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("len() builtin", "let x = len([1,2,3])", ["len([1, 2, 3])"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("range() builtin", "for i in range(5) { show(i) }", ["range(5)"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # CONTROL FLOW
    # ═══════════════════════════════════════════════════════════════
    print("\n── Control Flow ──")
    
    if test_transpile("if statement", "if true { show(1) }", ["if True:", "tt.show(1)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("if-else statement", "if false { show(1) } else { show(2) }", ["if False:", "else:"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("for loop", "for i in range(3) { show(i) }", ["for i in range(3):", "tt.show(i)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("while loop", "let x = 0\nwhile x < 5 { x = x + 1 }", ["while (x < 5):"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # FUNCTIONS
    # ═══════════════════════════════════════════════════════════════
    print("\n── Functions ──")
    
    if test_transpile("fn declaration", "fn add(a, b) { return a + b }", ["def add(a, b):", "return (a + b)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("law declaration", "law square(x)\n    reply x * x\nend", ["def square(x):", "return (x * x)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Function call", "fn greet() { show(\"hi\") }\ngreet()", ["def greet():", "greet()"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # STEP CHAINS
    # ═══════════════════════════════════════════════════════════════
    print("\n── Step Chains ──")
    
    if test_transpile("_sort step", "let nums = [3,1,2]\nshow(nums _sort)", [".sort()"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("_reverse step", "let nums = [1,2,3]\nshow(nums _reverse)", [".reverse()"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("_take step", "let nums = [1,2,3,4,5]\nshow(nums _take(3))", [".take(3)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("_sum terminal", "let nums = [1,2,3]\nshow(nums _sum)", [".sum()"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("Chained steps", "let nums = [5,2,8]\nshow(nums _sort _reverse _take(2))", [".sort()", ".reverse()", ".take(2)"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # INDEX ACCESS
    # ═══════════════════════════════════════════════════════════════
    print("\n── Index Access ──")
    
    if test_transpile("Array index", "let arr = [1,2,3]\nlet x = arr[0]", ["x = arr[0]"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("String index", 'let s = "hello"\nlet c = s[0]', ["c = s[0]"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # UNARY OPERATORS
    # ═══════════════════════════════════════════════════════════════
    print("\n── Unary Operators ──")
    
    if test_transpile("Negation", "let x = -5", ["x = (-5)"]):
        passed += 1
    else:
        failed += 1
        
    if test_transpile("not operator", "let x = not true", ["x = (not True)"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # LAMBDAS
    # ═══════════════════════════════════════════════════════════════
    print("\n── Lambdas ──")
    
    # Note: TinyTalk lambda syntax may vary - test what the parser supports
    
    # ═══════════════════════════════════════════════════════════════
    # COMPLEX EXAMPLES
    # ═══════════════════════════════════════════════════════════════
    print("\n── Complex Examples ──")
    
    fib_code = '''
law fib(n)
    if n <= 1 { reply n }
    reply fib(n - 1) + fib(n - 2)
end
'''
    if test_transpile("Fibonacci function", fib_code, ["def fib(n):", "if (n <= 1):", "return n", "return (fib((n - 1)) + fib((n - 2)))"]):
        passed += 1
    else:
        failed += 1
    
    # ═══════════════════════════════════════════════════════════════
    # ADDITIONAL EDGE CASES
    # ═══════════════════════════════════════════════════════════════
    print("\n── Additional Edge Cases ──")

    # 1. Syntax error: missing closing bracket
    if test_transpile("Syntax error: missing bracket", "let x = [1, 2, 3", should_fail=True):
        passed += 1
    else:
        failed += 1

    # 2. Nested function definitions
    nested_fn_code = '''
law outer(a)
    law inner(b)
        reply b * 2
    end
    reply inner(a) + 1
end
'''
    if test_transpile("Nested function definitions", nested_fn_code, ["def outer(a):", "def inner(b):", "return (b * 2)", "return (inner(a) + 1)"]):
        passed += 1
    else:
        failed += 1

    # 3. Deeply chained step operations
    if test_transpile("Deeply chained steps", "let x = [1,2,3]._sort._reverse._take(2)._sum", ["x = sum(take(reverse(sort([1, 2, 3])), 2))"]):
        passed += 1
    else:
        failed += 1

    # 4. Complex control flow: nested loops/conditionals
    complex_cf_code = '''
let total = 0
for i in range(3) {
    if i % 2 == 0 {
        total = total + i
    }
}
'''
    if test_transpile("Complex control flow", complex_cf_code, ["for i in range(3):", "if ((i % 2) == 0):", "total = (total + i)"]):
        passed += 1
    else:
        failed += 1

    # 5. Unusual property access/operator combinations
    if test_transpile("Unusual property access", "let s = 'abc'.upcase.len", ['s = len(upcase("abc"))']):
        passed += 1
    else:
        failed += 1

    # ═══════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════
    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
