#!/usr/bin/env python3
"""
TinyTalk CLI
Run .tt files, start REPL, or transpile.

Usage:
    tinytalk run <file.tt>            Run a TinyTalk program
    tinytalk repl                     Start interactive REPL
    tinytalk check <file.tt>          Parse and report errors (no execution)
    tinytalk transpile <file.tt>      Transpile to Python
    tinytalk transpile-sql <file.tt>  Transpile to SQL
"""

import sys
import os


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return

    cmd = args[0]

    if cmd == "run" and len(args) >= 2:
        run_file(args[1])
    elif cmd == "repl":
        start_repl()
    elif cmd == "check" and len(args) >= 2:
        check_file(args[1])
    elif cmd == "transpile" and len(args) >= 2:
        transpile_file(args[1])
    elif cmd in ("transpile-sql", "sql") and len(args) >= 2:
        transpile_sql_file(args[1])
    else:
        print(f"Unknown command: {cmd}")
        print("Use 'tinytalk help' for usage.")
        sys.exit(1)


def run_file(path: str):
    from .kernel import TinyTalkKernel

    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)

    with open(path, "r") as f:
        source = f.read()

    source_dir = os.path.dirname(os.path.abspath(path))
    kernel = TinyTalkKernel(capture_output=False, source_dir=source_dir)
    result = kernel.run(source)

    if not result.success:
        print(f"Error: {result.error}", file=sys.stderr)
        sys.exit(1)


def check_file(path: str):
    from .lexer import Lexer
    from .parser import Parser

    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)

    with open(path, "r") as f:
        source = f.read()

    try:
        tokens = Lexer(source).tokenize()
        Parser(tokens).parse()
        print(f"OK: {path} parsed successfully.")
    except SyntaxError as e:
        print(f"Syntax error in {path}: {e}")
        sys.exit(1)


def transpile_file(path: str):
    from .transpiler import transpile

    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)

    with open(path, "r") as f:
        source = f.read()

    print(transpile(source))


def transpile_sql_file(path: str):
    from .sql_transpiler import transpile_sql

    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)

    with open(path, "r") as f:
        source = f.read()

    print(transpile_sql(source))


def start_repl():
    from .kernel import TinyTalkKernel
    TinyTalkKernel(capture_output=False).repl()


if __name__ == "__main__":
    main()
