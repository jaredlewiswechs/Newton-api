"""Quick test B only - property magic"""
import sys
sys.path.insert(0, '.')
from realTinyTalk import run

code = 'show("  HELLO  ".trim.lowcase)'
print("Testing property magic...")
run(code)
print("Done")
