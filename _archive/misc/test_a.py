"""Test A: Bound methods preserve self"""
import sys
sys.path.insert(0, '.')
from realTinyTalk import run

# When you extract a method and call it later, 
# it should still know its original `self`
code = '''
blueprint Counter {
    count: 0
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

print("Testing bound methods (Python)...")
print("Code:")
print(code)
print()
print("Running...")
run(code)
print("Expected: 1, then 2 (method remembers its self)")
