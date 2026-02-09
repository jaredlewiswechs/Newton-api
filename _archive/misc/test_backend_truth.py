"""
Backend Truth Tests - The 3 Classic Transpiler Smell Tests
Tests both Python interpreter and JS target for identical behavior.
"""
import sys
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, '.')
from realTinyTalk import run
from realTinyTalk.backends.js import compile_to_js

def capture_py(code):
    """Run code in Python interpreter, capture output."""
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        run(code)
    return buf.getvalue().strip()

def capture_js(code):
    """Compile to JS and run with Node, capture output."""
    js = compile_to_js(code)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(js)
        f.flush()
        result = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=5)
        Path(f.name).unlink()
    return result.stdout.strip()

def test(name, code, check_match=True):
    """Run test on both backends."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Code:\n{code.strip()}")
    print()
    
    try:
        py_out = capture_py(code)
        print(f"Python: {py_out}")
    except Exception as e:
        print(f"Python ERROR: {e}")
        py_out = f"ERROR: {e}"
    
    try:
        js_out = capture_js(code)
        print(f"JS:     {js_out}")
    except Exception as e:
        print(f"JS ERROR: {e}")
        js_out = f"ERROR: {e}"
    
    # Normalize for comparison (JS arrays print differently)
    py_norm = py_out.replace('[', '').replace(']', '').replace(' ', '')
    js_norm = js_out.replace('[', '').replace(']', '').replace(' ', '')
    
    if check_match:
        if py_norm == js_norm:
            print(f"✅ MATCH")
            return True
        else:
            print(f"❌ MISMATCH")
            return False
    return True

# ═══════════════════════════════════════════════════════════════
# TEST A: Bound methods preserve self
# ═══════════════════════════════════════════════════════════════

test_a = '''
blueprint Counter {
    count: 0,
    
    inc: law() {
        self.count = self.count + 1
        reply self.count
    }
}

let c = Counter()
let f = c.inc
show(f())
show(f())
'''

# ═══════════════════════════════════════════════════════════════
# TEST B: Property magic matches exactly  
# ═══════════════════════════════════════════════════════════════

test_b = '''
show("  HELLO  ".trim.lowcase)
'''

# ═══════════════════════════════════════════════════════════════
# TEST C: Step chains don't mutate original
# ═══════════════════════════════════════════════════════════════

test_c = '''
let a = [3, 1, 2]
let b = a _sort
show(a)
show(b)
'''

# ═══════════════════════════════════════════════════════════════
# RUN ALL TESTS
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("BACKEND TRUTH TESTS - Python vs JavaScript")
print("="*60)

results = []
results.append(("A: Bound methods", test("A: Bound methods preserve self", test_a)))
results.append(("B: Property magic", test("B: Property magic matches", test_b)))
results.append(("C: Step chain immutability", test("C: Step chains don't mutate", test_c)))

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
for name, passed in results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {name}")

all_passed = all(r[1] for r in results)
print()
if all_passed:
    print("🎉 ALL BACKEND TRUTH TESTS PASSED!")
else:
    print("⚠️  Some tests failed - backends differ")
