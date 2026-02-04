"""Test C: Step chains don't mutate - unless spec says so"""
import sys
sys.path.insert(0, '.')
from realTinyTalk import run

# Step chains like `_sort` should NOT mutate the original list
# but `sort!` (bang) might be allowed to
code = '''
let a = [3,1,2]
let b = a _sort
show(a)
show(b)
'''

print("Testing step chain mutation semantics (Python)...")
run(code)
print("Expected: a should still be [3,1,2], b should be [1,2,3]")
