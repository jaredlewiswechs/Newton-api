"""Quick test B - JS backend property magic"""
import sys
sys.path.insert(0, '.')
from realTinyTalk.backends.js.emitter import compile_to_js
import subprocess
import tempfile
import os

code = 'show("  HELLO  ".trim.lowcase)'
print("Testing JS backend property magic...")

js = compile_to_js(code)
print("Generated JS:")
print(js)
print()

# Write to temp file and run
with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
    f.write(js)
    tmp = f.name

try:
    result = subprocess.run(['node', tmp], capture_output=True, text=True, timeout=5)
    print("Node output:", result.stdout.strip())
    if result.stderr:
        print("Errors:", result.stderr)
finally:
    os.unlink(tmp)
