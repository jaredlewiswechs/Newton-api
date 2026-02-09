"""
TinyTalk Web IDE Server
Monaco-powered editor with live execution
"""

import sys
import os
import json
import time
import traceback
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flask import Flask, request, jsonify, send_from_directory, session
from realTinyTalk import run, ExecutionBounds
from realTinyTalk.runtime import TinyTalkError
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
import hashlib
import re

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'devsecret')

# Storage root for server-side data
STORAGE_ROOT = Path(__file__).parent / 'storage'
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

# Limits
MAX_SCRIPT_BYTES = 100 * 1024  # 100 KB


def _safe_user(name: str) -> str:
    if not name:
        return 'anonymous'
    # allow simple usernames, replace unsafe chars
    name = re.sub(r'[^A-Za-z0-9_\-]', '-', name)
    name = name.strip('-')
    if len(name) > 32:
        name = name[:32]
    if name == '':
        return 'anonymous'
    return name


def get_user() -> str:
    # Priority: session, X-User header, fallback anonymous
    uname = session.get('user') or request.headers.get('X-User') or 'anonymous'
    return _safe_user(uname)


def current_user_root() -> Path:
    return STORAGE_ROOT / 'users' / get_user()


def ensure_user_dirs():
    r = current_user_root()
    (r / 'scripts').mkdir(parents=True, exist_ok=True)
    (r / 'projects').mkdir(parents=True, exist_ok=True)
    return r


def _safe_name(name: str) -> str:
    # Keep only safe chars for filenames, enforce .tt
    examples = [
        {
            'name': '🔄 Higher-Order Functions',
            'code': '''// Pass functions to other functions!

let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

// Define transforms
law doubled(x)
    reply x * 2
end

law squared(x)
    reply x * x
end

// Define predicates
law is_even(x)
    reply x % 2 == 0
end

law is_odd(x)
    reply x % 2 == 1
end

law greater_than_5(x)
    reply x > 5
end

show("=== Transform with _map ===")
show("Numbers:" numbers)
show("Doubled:" numbers _map(doubled))
show("Squared:" numbers _map(squared))

show("")
show("=== Filter with predicates ===")
show("Evens:" numbers _filter(is_even))
show("Odds:" numbers _filter(is_odd))

show("")
show("=== Chain them! ===")
// Filter to odds, square each, sum
let result = numbers _filter(is_odd) _map(squared) _sum
show("Sum of squared odds:" result)

// Filter >5, double, take 3
show("Big doubled top 3:" numbers _filter(greater_than_5) _map(doubled) _take(3))

show("")
show("=== Functions are values ===")
law apply_twice(func, x)
    reply func(func(x))
end

show("apply_twice(doubled, 3):" apply_twice(doubled, 3))
show("apply_twice(squared, 2):" apply_twice(squared, 2))'''
        },
        {
            'name': '🎮 Turn-Based Strategy Game',
            'code': '''// ═══════════════════════════════════════
// TURN-BASED STRATEGY GAME EXAMPLE
// ═══════════════════════════════════════

// Define units
law Unit(name, health, attack)
    field name
    field health
    field attack
end

// Create units
let knight = Unit("Knight", 100, 15)
let archer = Unit("Archer", 75, 10)

// Battle logic
law battle(attacker, defender)
    defender.health -= attacker.attack
    if defender.health <= 0 {
        show(defender.name + " is defeated!")
    } else {
        show(defender.name + " has " + defender.health.str + " health left.")
    }
end

// Simulate battle
show("Battle Start!")
battle(knight, archer)
battle(archer, knight)
battle(knight, archer)'''
        }
    ]
    return jsonify(examples)
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    uname = _safe_user(username)
    user_dir = STORAGE_ROOT / 'users' / uname
    user_dir.mkdir(parents=True, exist_ok=True)
    authp = _auth_path(uname)
    if authp.exists():
        return jsonify({'error': 'user exists'}), 400
    # create salted hash
    salt = os.urandom(16).hex()
    h = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    authp.write_text(json.dumps({'salt': salt, 'hash': h}))
    return jsonify({'created': uname})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    uname = _safe_user(username)
    authp = _auth_path(uname)
    if not authp.exists():
        return jsonify({'error': 'user not found'}), 404
    auth = json.loads(authp.read_text())
    salt = auth.get('salt')
    expected = auth.get('hash')
    got = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    if got != expected:
        return jsonify({'error': 'invalid credentials'}), 401
    session['user'] = uname
    return jsonify({'logged_in': uname})


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'logged_out': True})


# ═══════════════════════════════════════════════════════════════
# Script storage helpers
# ═══════════════════════════════════════════════════════════════

def _script_dir(name: str) -> Path:
    """Return the directory for a named script under the current user."""
    safe = re.sub(r'[^A-Za-z0-9_\-.]', '-', name)
    return current_user_root() / 'scripts' / safe


def _read_meta(dirp: Path) -> dict:
    """Read meta.json from a script directory."""
    mp = dirp / 'meta.json'
    if mp.exists():
        return json.loads(mp.read_text())
    return {'versions': []}


def _write_meta(dirp: Path, meta: dict):
    """Write meta.json to a script directory."""
    mp = dirp / 'meta.json'
    mp.write_text(json.dumps(meta, indent=2))


def _latest_version(dirp: Path) -> dict | None:
    """Return the latest version entry from meta.json, or None."""
    meta = _read_meta(dirp)
    versions = meta.get('versions', [])
    return versions[-1] if versions else None


def _save_version(dirp: Path, code: str, message: str = '') -> dict:
    """Save a new version of a script and return the version record."""
    dirp.mkdir(parents=True, exist_ok=True)
    (dirp / 'versions').mkdir(parents=True, exist_ok=True)
    meta = _read_meta(dirp)
    vid = f"v{len(meta['versions']) + 1}"
    entry = {
        'id': vid,
        'message': message,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    meta['versions'].append(entry)
    _write_meta(dirp, meta)
    (dirp / 'versions' / f"{vid}.tt").write_text(code)
    return entry


def require_auth():
    """Return current user name or None if not authenticated."""
    user = get_user()
    return user if user != 'anonymous' else None


# API: list all scripts for the current user
@app.route('/api/scripts', methods=['GET'])
def list_scripts():
    ensure_user_dirs()
    scripts_dir = current_user_root() / 'scripts'
    result = []
    if scripts_dir.exists():
        for d in sorted(scripts_dir.iterdir()):
            if d.is_dir():
                meta = _read_meta(d)
                result.append({'name': d.name, 'versions': len(meta.get('versions', []))})
    return jsonify(result)


# API: get script metadata and latest content
@app.route('/api/scripts/<name>', methods=['GET'])
def get_script(name):
    dirp = _script_dir(name)
    if not dirp.exists():
        return jsonify({'error': 'not found'}), 404
    meta = _read_meta(dirp)
    latest = _latest_version(dirp)
    content = ''
    if latest:
        vpath = dirp / 'versions' / f"{latest['id']}.tt"
        if vpath.exists():
            content = vpath.read_text()
    return jsonify({'name': name, 'content': content, 'versions': meta.get('versions', [])})


# API: get specific version content
@app.route('/api/scripts/<name>/version/<vid>', methods=['GET'])
def get_script_version(name, vid):
    dirp = _script_dir(name)
    vpath = dirp / 'versions' / f"{vid}.tt"
    if not vpath.exists():
        return jsonify({'error': 'not found'}), 404
    return jsonify({'id': vid, 'content': vpath.read_text()})


# API: save new script (create or new version)
@app.route('/api/scripts', methods=['POST'])
def save_script():
    data = request.get_json() or {}
    name = data.get('name') or f"untitled-{int(time.time())}.tt"
    code = data.get('code', '')
    message = data.get('message', '')
    # enforce size limits
    if len(code.encode('utf-8')) > MAX_SCRIPT_BYTES:
        return jsonify({'error': 'script too large'}), 400
    dirp = _script_dir(name)
    saved = _save_version(dirp, code, message)
    return jsonify({'saved': saved, 'name': dirp.name})


# API: restore a version (create new version from old)
@app.route('/api/scripts/<name>/restore', methods=['POST'])
def restore_script(name):
    data = request.get_json() or {}
    vid = data.get('version_id')
    dirp = _script_dir(name)
    vpath = dirp / 'versions' / f"{vid}.tt"
    if not vpath.exists():
        return jsonify({'error': 'version not found'}), 404
    code = vpath.read_text()
    # enforce size
    if len(code.encode('utf-8')) > MAX_SCRIPT_BYTES:
        return jsonify({'error': 'version too large'}), 400
    saved = _save_version(dirp, code, f"restore:{vid}")
    return jsonify({'restored': saved})


# API: delete script
@app.route('/api/scripts/<name>', methods=['DELETE'])
def delete_script(name):
    dirp = _script_dir(name)
    if not dirp.exists():
        return jsonify({'error': 'not found'}), 404
    # delete recursively
    for p in dirp.rglob('*'):
        if p.is_file():
            p.unlink()
    for p in sorted(dirp.rglob('*'), reverse=True):
        try:
            if p.is_dir():
                p.rmdir()
        except Exception:
            pass
    try:
        dirp.rmdir()
    except Exception:
        pass
    return jsonify({'deleted': name})


@app.route('/api/scripts/<name>/merge', methods=['POST'])
def merge_script(name):
    # Accept merged code from client and create a new version
    user = require_auth()
    if not user:
        return jsonify({'error': 'authentication required'}), 401
    data = request.get_json() or {}
    merged = data.get('merged')
    message = data.get('message', 'merged from UI')
    if merged is None:
        return jsonify({'error': 'merged content required'}), 400
    if len(merged.encode('utf-8')) > MAX_SCRIPT_BYTES:
        return jsonify({'error': 'merged too large'}), 400
    dirp = _script_dir(name)
    if not dirp.exists():
        return jsonify({'error': 'script not found'}), 404
    saved = _save_version(dirp, merged, message)
    return jsonify({'merged': saved})


@app.route('/api/scripts/<name>/diff/<vid1>/<vid2>', methods=['GET'])
def diff_versions(name, vid1, vid2):
    import difflib
    dirp = _script_dir(name)
    v1 = dirp / 'versions' / f"{vid1}.tt"
    v2 = dirp / 'versions' / f"{vid2}.tt"
    if not v1.exists() or not v2.exists():
        return jsonify({'error': 'version not found'}), 404
    a = v1.read_text().splitlines()
    b = v2.read_text().splitlines()
    ud = list(difflib.unified_diff(a, b, fromfile=vid1, tofile=vid2, lineterm=''))
    return jsonify({'diff': '\n'.join(ud)})


@app.route('/api/scripts/<name>/ancestor', methods=['GET'])
def find_ancestor(name):
    # Query params: v1, v2
    v1 = request.args.get('v1')
    v2 = request.args.get('v2')
    dirp = _script_dir(name)
    if not dirp.exists():
        return jsonify({'error': 'not found'}), 404
    meta = _read_meta(dirp)
    versions = meta.get('versions', [])
    ids = [v['id'] for v in versions]
    try:
        i1 = ids.index(v1) if v1 in ids else None
        i2 = ids.index(v2) if v2 in ids else None
    except ValueError:
        return jsonify({'error': 'version id not found'}), 404
    if i1 is None or i2 is None:
        return jsonify({'error': 'version id not found'}), 404
    base_idx = min(i1, i2) - 1
    if base_idx < 0:
        # no earlier common ancestor; return first version as base
        base_idx = 0
    base_id = ids[base_idx]
    return jsonify({'base_id': base_id})


def _three_way_merge_lines(base, a, b):
    """
    Three-way merge on lists of lines (base, a, b).
    Returns (merged_lines, conflicts_bool).
    Algorithm: compute opcodes for base->a and base->b, split base into boundary ranges
    from those opcodes, then for each range collect the corresponding a/b target slices
    and apply merge rules: prefer identical edits, prefer single-sided edits, otherwise mark conflict.
    """
    merged = []
    conflicts = False

    base_lines = base
    a_lines = a
    b_lines = b

    sma = SequenceMatcher(None, base_lines, a_lines)
    smb = SequenceMatcher(None, base_lines, b_lines)
    op_a = sma.get_opcodes()
    op_b = smb.get_opcodes()

    # collect boundaries from base ranges and insertion points
    bounds = {0, len(base_lines)}
    for tag, i1, i2, j1, j2 in op_a:
        bounds.add(i1); bounds.add(i2)
        if tag == 'insert': bounds.add(i1)
    for tag, i1, i2, j1, j2 in op_b:
        bounds.add(i1); bounds.add(i2)
        if tag == 'insert': bounds.add(i1)
    bounds = sorted(bounds)

    def collect_target_for_range(opcodes, target_lines, start, end):
        out = []
        for tag, i1, i2, j1, j2 in opcodes:
            # insertion at position i1 (i1==i2)
            if tag == 'insert':
                if start <= i1 <= end:
                    out.extend(target_lines[j1:j2])
                continue
            if i2 <= start or i1 >= end:
                continue
            # overlap
            overlap_start = max(i1, start)
            overlap_end = min(i2, end)
            if overlap_end > overlap_start:
                off = overlap_start - i1
                out.extend(target_lines[j1 + off: j1 + off + (overlap_end - overlap_start)])
        return out

    # iterate ranges
    for k in range(len(bounds)-1):
        s = bounds[k]; e = bounds[k+1]
        base_seg = base_lines[s:e]
        a_seg = collect_target_for_range(op_a, a_lines, s, e)
        b_seg = collect_target_for_range(op_b, b_lines, s, e)

        # If both sides same -> accept
        if a_seg == b_seg:
            merged.extend(a_seg)
            continue
        # If one side unchanged from base -> take the other
        if a_seg == base_seg and b_seg != base_seg:
            merged.extend(b_seg)
            continue
        if b_seg == base_seg and a_seg != base_seg:
            merged.extend(a_seg)
            continue
        # If both differ from base and each other -> conflict
        conflicts = True
        merged.append('<<<<<<< A')
        merged.extend(a_seg)
        merged.append('=======')
        merged.extend(b_seg)
        merged.append('>>>>>>> B')

    return merged, conflicts


@app.route('/api/scripts/<name>/merge3', methods=['POST'])
def merge_three_way(name):
    """Perform a simple server-side 3-way merge using an ancestor/base version.
    JSON body: { "v1": "<id>", "v2": "<id>", "base_id": "<id>" (optional) }
    If base_id omitted, an approximate ancestor is chosen from history.
    Returns merged content and conflict indicator, and saves merged result as a new version.
    """
    data = request.get_json() or {}
    v1 = data.get('v1')
    v2 = data.get('v2')
    base_id = data.get('base_id')
    if not v1 or not v2:
        return jsonify({'error': 'v1 and v2 are required'}), 400

    dirp = _script_dir(name)
    if not dirp.exists():
        return jsonify({'error': 'script not found'}), 404

    meta = _read_meta(dirp)
    versions = meta.get('versions', [])
    ids = [v['id'] for v in versions]
    if v1 not in ids or v2 not in ids:
        return jsonify({'error': 'version id not found'}), 404

    if not base_id:
        i1 = ids.index(v1)
        i2 = ids.index(v2)
        base_idx = min(i1, i2) - 1
        if base_idx < 0:
            base_idx = 0
        base_id = ids[base_idx]

    def _read_version(vid):
        p = dirp / 'versions' / f"{vid}.tt"
        if not p.exists():
            return ''
        return p.read_text(encoding='utf-8')

    base = _read_version(base_id).splitlines()
    a = _read_version(v1).splitlines()
    b = _read_version(v2).splitlines()

    # Attempt to use git's merge-file for a more battle-tested merge when available
    merged_text = None
    conflicts = False
    try:
        from shutil import which
        import subprocess, tempfile
        if which('git'):
            with tempfile.TemporaryDirectory() as td:
                basef = Path(td) / 'base.tt'
                af = Path(td) / 'a.tt'
                bf = Path(td) / 'b.tt'
                basef.write_text('\n'.join(base), encoding='utf-8')
                af.write_text('\n'.join(a), encoding='utf-8')
                bf.write_text('\n'.join(b), encoding='utf-8')
                # git merge-file current base other -> print to stdout with -p
                proc = subprocess.run(['git', 'merge-file', '-p', str(af), str(basef), str(bf)], capture_output=True, text=True)
                if proc.returncode in (0, 1):
                    merged_text = proc.stdout
                    conflicts = '<<<<<<<' in merged_text or '>>>>>>>' in merged_text
    except Exception:
        merged_text = None

    if merged_text is None:
        merged_lines, conflicts = _three_way_merge_lines(base, a, b)
        merged_text = '\n'.join(merged_lines)

    # Save the merged content as a new version
    saved = _save_version(dirp, merged_text, message=f'three-way-merge {v1} {v2}')

    return jsonify({'merged': {'id': saved['id'], 'conflicts': conflicts, 'content': merged_text}})


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve the main IDE page."""
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

@app.route('/api/run', methods=['POST'])
def run_code():
    """Execute TinyTalk code and return results."""
    data = request.get_json()
    code = data.get('code', '')
    
    # Capture print output
    import io
    from contextlib import redirect_stdout
    
    stdout_capture = io.StringIO()
    
    start_time = time.time()
    
    try:
        bounds = ExecutionBounds(
            max_ops=1_000_000,
            max_iterations=100_000,
            max_recursion=500,
            timeout_seconds=10.0
        )
        
        with redirect_stdout(stdout_capture):
            result = run(code, bounds)
        
        elapsed = (time.time() - start_time) * 1000
        output = stdout_capture.getvalue()
        
        # Format result
        result_str = str(result) if result.type.value != 'null' else ''
        
        return jsonify({
            'success': True,
            'output': output,
            'result': result_str,
            'elapsed_ms': round(elapsed, 2)
        })
        
    except TinyTalkError as e:
        elapsed = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': str(e),
            'output': stdout_capture.getvalue(),
            'elapsed_ms': round(elapsed, 2)
        })
    except SyntaxError as e:
        elapsed = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': f"Syntax Error: {e}",
            'output': stdout_capture.getvalue(),
            'elapsed_ms': round(elapsed, 2)
        })
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': f"{type(e).__name__}: {e}",
            'output': stdout_capture.getvalue(),
            'elapsed_ms': round(elapsed, 2)
        })


@app.route('/api/transpile/js', methods=['POST'])
def transpile_to_js():
    """Transpile TinyTalk code to JavaScript."""
    data = request.get_json()
    code = data.get('code', '')
    include_runtime = data.get('include_runtime', True)
    
    start_time = time.time()
    
    try:
        from realTinyTalk.lexer import Lexer
        from realTinyTalk.parser import Parser
        from realTinyTalk.backends.js.emitter import JSEmitter
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        emitter = JSEmitter(include_runtime=include_runtime)
        js_code = emitter.emit(ast)
        
        elapsed = (time.time() - start_time) * 1000
        
        return jsonify({
            'success': True,
            'code': js_code,
            'language': 'javascript',
            'elapsed_ms': round(elapsed, 2)
        })
        
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': f"{type(e).__name__}: {e}",
            'elapsed_ms': round(elapsed, 2)
        })


@app.route('/api/transpile/python', methods=['POST'])
def transpile_to_python():
    """Transpile TinyTalk code to Python."""
    data = request.get_json()
    code = data.get('code', '')
    include_runtime = data.get('include_runtime', True)
    
    start_time = time.time()
    
    try:
        from realTinyTalk.lexer import Lexer
        from realTinyTalk.parser import Parser
        from realTinyTalk.backends.python.emitter import PythonEmitter
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        emitter = PythonEmitter(include_runtime=include_runtime)
        py_code = emitter.emit(ast)
        
        elapsed = (time.time() - start_time) * 1000
        
        return jsonify({
            'success': True,
            'code': py_code,
            'language': 'python',
            'elapsed_ms': round(elapsed, 2)
        })
        
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': f"{type(e).__name__}: {e}",
            'elapsed_ms': round(elapsed, 2)
        })


@app.route('/api/examples')
def get_examples():
    """Get example programs - using ultra-clean tinyTalk syntax."""
    examples = [
        {
            'name': '👋 Hello World',
            'code': '''// ═══════════════════════════════════════════════════════════
// Welcome to realTinyTalk!
// The friendliest programming language
// ═══════════════════════════════════════════════════════════

show("Hello World!")

// Space-separated args - no commas needed!
let name = "Newton"
show("Welcome" name "to realTinyTalk!")

// Property magic - no parentheses needed!
show("Uppercase:" name.upcase)
show("Length:" name.len)
show("Reversed:" name.reversed)'''
        },
        {
            'name': '📖 Tutorial: Basics',
            'code': '''// ═══════════════════════════════════════
// TUTORIAL 1: The Basics
// ═══════════════════════════════════════

// Variables with 'let'
let greeting = "Hello"
let number = 42
let pi = 3.14159

// show() prints anything - space-separated args
show("greeting:" greeting)
show("number:" number)
show("pi:" pi)

// Math just works
show("")
show("=== Math ===")
let sum = 2 + 3
let product = 10 * 4
let power = 2 ** 8
show("2 + 3 =" sum)
show("10 * 4 =" product)
show("2 ** 8 =" power)

// Strings
show("")
show("=== Strings ===")
let name = "Alice"
show("Hello" name "!")
show("Length:" name.len)
show("Uppercase:" name.upcase)
show("Reversed:" name.reversed)'''
        },
        {
            'name': '📖 Tutorial: Functions',
            'code': '''// ═══════════════════════════════════════
// TUTORIAL 2: Functions
// ═══════════════════════════════════════

// LAW = pure function (no side effects)
law square(x)
    reply x * x
end

law greet(name)
    reply "Hello " + name + "!"
end

show("square(5) =" square(5))
show(greet("World"))

// Functions can call functions
law sum_of_squares(a, b)
    reply square(a) + square(b)
end

show("sum_of_squares(3, 4) =" sum_of_squares(3, 4))

// Recursion works too
law factorial(n)
    if n <= 1 { reply 1 }
    reply n * factorial(n - 1)
end

show("")
show("=== Factorials ===")
for i in range(1, 8) {
    show(i.str + "! =" factorial(i))
}'''
        },
        {
            'name': '📖 Tutorial: Collections',
            'code': '''// ═══════════════════════════════════════
// TUTORIAL 3: Lists & Maps
// ═══════════════════════════════════════

// Lists
let fruits = ["apple", "banana", "cherry"]
show("Fruits:" fruits)
show("First:" fruits.first)
show("Last:" fruits.last)
show("Length:" fruits.len)

// Loop through lists
show("")
show("=== Each fruit ===")
for fruit in fruits {
    show("-" fruit)
}

// Maps (like dictionaries)
let person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}

show("")
show("=== Person ===")
show("Name:" person.name)
show("Age:" person.age)
show("City:" person.city)

// Add to map
person.country = "USA"
show("Country:" person.country)'''
        },
        {
            'name': '📖 Tutorial: Control Flow',
            'code': '''// ═══════════════════════════════════════
// TUTORIAL 4: Control Flow
// ═══════════════════════════════════════

// If statements
let age = 25

if age >= 18 {
    show("You are an adult")
} else {
    show("You are a minor")
}

// For loops
show("")
show("=== Countdown ===")
for i in range(5, 0, -1) {
    show(i)
}
show("Liftoff!")

// While loops
show("")
show("=== Doubling ===")
let x = 1
while x < 100 {
    show(x)
    x = x * 2
}

// Break and continue
show("")
show("=== Skip evens, stop at 7 ===")
for i in range(10) {
    if i % 2 == 0 { continue }
    if i > 7 { break }
    show(i)
}'''
        },
        {
            'name': '🔧 Property Magic',
            'code': '''// Property conversions - no parentheses needed!
// .str   -> convert to string
// .int   -> convert to integer
// .float -> convert to float  
// .bool  -> convert to boolean
// .type  -> get type name
// .len   -> get length

let num = 42
let text = "3.14"

show("=== Type Conversions ===")
show("num.str:" num.str)
show("text.float:" text.float)
show("text.int:" text.int)
show("num.type:" num.type)

show("")
show("=== String Properties ===")
let msg = "  hello world  "
show("original:" msg)
show("trimmed:" msg.trim)
show("upcase:" msg.upcase)
show("lowcase:" msg.lowcase)
show("len:" msg.len)
show("reversed:" msg.reversed)

show("")
show("=== List Properties ===")
let items = [1, 2, 3, 4, 5]
show("items:" items)
show("first:" items.first)
show("last:" items.last)
show("empty:" items.empty)
show("len:" items.len)'''
        },
        {
            'name': '📜 when (Constants)',
            'code': '''// WHEN - Declares immutable facts
// (Cannot be changed after creation)

when PI = 3.14159
when GRAVITY = 9.81
when APP_NAME = "MyApp"

show("PI:" PI)
show("Gravity:" GRAVITY)
show("App:" APP_NAME)

// Calculate with constants
law circle_area(radius)
    reply PI * radius * radius
end

show("")
show("=== Circle Areas ===")
for r in range(1, 6) {
    show("radius" r "-> area" circle_area(r))
}

// Try uncommenting this - you'll get an error!
// PI = 3.0  // ERROR: Cannot reassign constant'''
        },
        {
            'name': '🔨 forge (Actions)',
            'code': '''// FORGE - Actions that can change state
// Use when you need side effects

forge greet(name)
    show("Hello" name "!")
    reply "greeted"
end

forge countdown(n)
    while n > 0 {
        show(n)
        n = n - 1
    }
    show("Liftoff!")
end

greet("World")
show("")
countdown(5)'''
        },
        {
            'name': '⚖️ when/do/finfr (NEW!)',
            'code': '''// The NEW way to define functions!
// when name(params)
//   do expression
// finfr  (fin for real!)

when square(x)
  do x * x
finfr

when double(x)
  do x * 2
finfr

when add(a, b)
  do a + b
finfr

show("square(5):" square(5))
show("double(21):" double(21))
show("add(10, 32):" add(10, 32))

// With conditionals
when factorial(n)
  if n <= 1 { do 1 }
  do n * factorial(n - 1)
finfr

show("")
show("=== Factorials ===")
for i in range(1, 8) {
    show(i.str "! =" factorial(i))
}

// when also works for constants!
when PI = 3.14159
show("")
show("PI =" PI)'''
        },
        {
            'name': '⚖️ law/reply/end (classic)',
            'code': '''// Classic function syntax (still works!)
// law name(params)
//   reply expression
// end

law square(x)
    reply x * x
end

law factorial(n)
    if n <= 1 { reply 1 }
    reply n * factorial(n - 1)
end

law is_even(n)
    reply n % 2 == 0
end

show("square(5):" square(5))
show("factorial(6):" factorial(6))
show("is_even(4):" is_even(4))
show("is_even(7):" is_even(7))'''
        },
        {
            'name': '🔢 Fibonacci',
            'code': '''// Fibonacci - clean and simple

law fib(n)
    if n <= 1 { reply n }
    reply fib(n - 1) + fib(n - 2)
end

show("=== Fibonacci Sequence ===")
for i in range(12) {
    show("fib(" i.str ") =" fib(i))
}'''
        },
        {
            'name': '🎯 FizzBuzz',
            'code': '''// The classic interview question

law fizzbuzz(n)
    if n % 15 == 0 { reply "FizzBuzz" }
    if n % 3 == 0 { reply "Fizz" }
    if n % 5 == 0 { reply "Buzz" }
    reply n
end

show("=== FizzBuzz 1-20 ===")
for i in range(1, 21) {
    show(fizzbuzz(i))
}'''
        },
        {
            'name': '🔍 Prime Numbers',
            'code': '''// Find prime numbers

law is_prime(n)
    if n < 2 { reply false }
    for i in range(2, n) {
        if n % i == 0 { reply false }
    }
    reply true
end

show("=== Primes up to 50 ===")
let primes = []
for n in range(2, 51) {
    if is_prime(n) {
        primes = primes + [n]
    }
}
show(primes)
show("")
show("Found" primes.len "primes")'''
        },
        {
            'name': '📊 Quicksort',
            'code': '''// Quicksort algorithm

law quicksort(arr)
    if arr.len <= 1 { reply arr }
    
    let pivot = arr[0]
    let less = []
    let greater = []
    
    for i in range(1, arr.len) {
        if arr[i] < pivot {
            less = less + [arr[i]]
        } else {
            greater = greater + [arr[i]]
        }
    }
    
    reply quicksort(less) + [pivot] + quicksort(greater)
end

let unsorted = [64, 34, 25, 12, 22, 11, 90]
show("Unsorted:" unsorted)
show("Sorted:" quicksort(unsorted))'''
        },
        {
            'name': '🧮 Calculator',
            'code': '''// Simple calculator with error handling

law add(a, b)
    reply a + b
end

law subtract(a, b)
    reply a - b
end

law multiply(a, b)
    reply a * b
end

law divide(a, b)
    if b == 0 { 
        reply {"error": "division by zero", "value": null}
    }
    reply {"error": null, "value": a / b}
end

show("=== Calculator ===")
show("10 + 5 =" add(10, 5))
show("10 - 5 =" subtract(10, 5))
show("10 * 5 =" multiply(10, 5))

let result = divide(10, 5)
show("10 / 5 =" result.value)

let bad = divide(10, 0)
show("10 / 0 =" bad.error)'''
        },
        {
            'name': '🔗 Step Chains (NEW!)',
            'code': '''// dplyr-style data manipulation
// Chain operations with _underscore steps!

let numbers = [5, 2, 8, 1, 9, 3, 7, 4, 6]
show("Numbers:" numbers)

// Chain multiple steps: sort, take top 3
let top3 = numbers _sort _reverse _take(3)
show("Top 3:" top3)

// Filter and count
law is_even(x)
    reply x % 2 == 0
end

let evens = numbers _filter(is_even)
show("Evens:" evens)
show("Even count:" numbers _filter(is_even) _count)

// Sum and average
show("Sum:" numbers _sum)
show("Average:" numbers _avg)
show("Min:" numbers _min)
show("Max:" numbers _max)

// Transform with _map
law doubled(x)
    reply x * 2
end

show("Doubled:" numbers _map(doubled))

// Combine operations: filter > 3, sort, take 3
show("")
show("=== Complex Chain ===")
law big(x)
    reply x > 3
end

let result = numbers _filter(big) _sort _take(3)
show("filter(>3) + sort + take(3):" result)'''
        },
        {
            'name': '💬 Natural Comparisons',
            'code': '''// Natural language comparisons!
// is, isnt, has, hasnt, isin, islike

let name = "Alice"
let numbers = [1, 2, 3, 4, 5]
let text = "Hello World"

// is / isnt - natural equality
show("=== is / isnt ===")
show("name is Alice:" (name is "Alice"))
show("name isnt Bob:" (name isnt "Bob"))
show("5 is 5:" (5 is 5))
show("5 isnt 6:" (5 isnt 6))

// has / hasnt - container checks
show("")
show("=== has / hasnt ===")
show("numbers has 3:" (numbers has 3))
show("numbers hasnt 99:" (numbers hasnt 99))
show("text has World:" (text has "World"))
show("text hasnt Goodbye:" (text hasnt "Goodbye"))

// isin - element membership
show("")
show("=== isin ===")
show("3 isin numbers:" (3 isin numbers))
show("99 isin numbers:" (99 isin numbers))

// islike - pattern matching (* and ?)
show("")
show("=== islike (wildcards) ===")
show("Alice islike A*:" ("Alice" islike "A*"))
show("Alice islike *ice:" ("Alice" islike "*ice"))
show("Alice islike Al?ce:" ("Alice" islike "Al?ce"))
show("Bob islike A*:" ("Bob" islike "A*"))'''
        },
        {
            'name': '✨ String Properties',
            'code': '''// String properties - no parentheses needed!

let msg = "  Hello World  "

show("=== String Properties ===")
show("original:" msg)
show("trimmed:" msg.trim)
show("upcase:" msg.upcase)
show("lowcase:" msg.lowcase)
show("reversed:" msg.reversed)
show("len:" msg.len)

// Split into parts
show("")
show("=== Split Operations ===")
let sentence = "the quick brown fox"
show("words:" sentence.words)
show("chars:" sentence.chars)

// Works with step chains!
show("")
show("=== String + Steps ===")
let words = sentence.words
show("first 2 words:" words _take(2))
show("sorted words:" words _sort)
show("unique chars:" sentence.chars _unique _sort)'''
        },
        {
            'name': '🏗️ Blueprints (OOP)',
            'code': '''// Blueprints = Classes in realTinyTalk
// Define types with fields and methods

blueprint Counter
    field value
    
    forge inc()
        self.value = self.value + 1
        reply self.value
    end
    
    forge add(n)
        self.value = self.value + n
        reply self.value
    end
    
    forge reset()
        self.value = 0
        reply self.value
    end
end

// Create instances
let c = Counter(0)
show("Initial:" c.value)

// Call methods
show("After inc():" c.inc())
show("After inc():" c.inc())
show("After add(10):" c.add(10))
show("After reset():" c.reset())

// Bound methods preserve self!
let increment = c.inc
show("Calling bound method:" increment())
show("Again:" increment())'''
        },
        {
            'name': '🔄 Higher-Order Functions',
            'code': '''// Pass functions to other functions!

let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

// Define transforms
law doubled(x)
    reply x * 2
end

law squared(x)
    reply x * x
end

// Define predicates
law is_even(x)
    reply x % 2 == 0
end

law is_odd(x)
    reply x % 2 == 1
end

law greater_than_5(x)
    reply x > 5
end

show("=== Transform with _map ===")
show("Numbers:" numbers)
show("Doubled:" numbers _map(doubled))
show("Squared:" numbers _map(squared))

show("")
show("=== Filter with predicates ===")
show("Evens:" numbers _filter(is_even))
show("Odds:" numbers _filter(is_odd))

show("")
show("=== Chain them! ===")
// Filter to odds, square each, sum
let result = numbers _filter(is_odd) _map(squared) _sum
show("Sum of squared odds:" result)

// Filter >5, double, take 3
show("Big doubled top 3:" numbers _filter(greater_than_5) _map(doubled) _take(3))

show("")
show("=== Functions are values ===")
law apply_twice(func, x)
    reply func(func(x))
end

show("apply_twice(doubled, 3):" apply_twice(doubled, 3))
show("apply_twice(squared, 2):" apply_twice(squared, 2))'''
        },
    ]
    return jsonify(examples)


# ========== Projects API ===========
@app.route('/api/projects', methods=['GET'])
def list_projects():
    ensure_user_dirs()
    proot = current_user_root() / 'projects'
    projects = []
    for p in proot.iterdir():
        if p.is_dir():
            m = p / 'manifest.json'
            manifest = {}
            if m.exists():
                try:
                    manifest = json.loads(m.read_text())
                except Exception:
                    manifest = {}
            projects.append({'name': p.name, 'manifest': manifest})
    return jsonify(projects)


@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name required'}), 400
    pname = re.sub(r'[^A-Za-z0-9_\-]', '-', Path(name).name)[:64]
    ensure_user_dirs()
    pdir = current_user_root() / 'projects' / pname
    pdir.mkdir(parents=True, exist_ok=True)
    manifest = {'name': pname, 'created': _now_ts(), 'files': []}
    (pdir / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    return jsonify({'created': pname})


@app.route('/api/projects/<proj>', methods=['GET'])
def get_project(proj):
    pdir = current_user_root() / 'projects' / proj
    m = pdir / 'manifest.json'
    if not m.exists():
        return jsonify({'error': 'not found'}), 404
    return jsonify(json.loads(m.read_text()))


@app.route('/api/projects/<proj>/add', methods=['POST'])
def project_add(proj):
    data = request.get_json() or {}
    script = data.get('script')
    if not script:
        return jsonify({'error': 'script required'}), 400
    pdir = current_user_root() / 'projects' / proj
    mpath = pdir / 'manifest.json'
    if not mpath.exists():
        return jsonify({'error': 'project not found'}), 404
    manifest = json.loads(mpath.read_text())
    if script not in manifest.get('files', []):
        manifest.setdefault('files', []).append(script)
        mpath.write_text(json.dumps(manifest, indent=2))
    return jsonify({'added': script})


@app.route('/api/projects/<proj>', methods=['DELETE'])
def delete_project(proj):
    pdir = current_user_root() / 'projects' / proj
    if not pdir.exists():
        return jsonify({'error': 'not found'}), 404
    for p in pdir.rglob('*'):
        if p.is_file():
            p.unlink()
    for p in sorted(pdir.rglob('*'), reverse=True):
        try:
            if p.is_dir():
                p.rmdir()
        except Exception:
            pass
    try:
        pdir.rmdir()
    except Exception:
        pass
    return jsonify({'deleted': proj})


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  realTinyTalk Web IDE")
    print("  The Verified General-Purpose Programming Language")
    print("  Every loop bounded. Every operation traced.")
    print("=" * 60 + "\n")
    print("Starting server at http://localhost:5555")
    print("Press Ctrl+C to stop\n")
    
    # Prevent starting multiple server instances on the same port.
    import socket

    def _port_in_use(host: str, port: int) -> bool:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except Exception:
            return False

    HOST = '127.0.0.1'
    PORT = 5555
    if _port_in_use(HOST, PORT):
        print(f"Server appears to be already running on {HOST}:{PORT}. Not starting a new instance.")
    else:
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False, threaded=True)
