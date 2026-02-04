#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
realTinyTalk CLI
The Sovereign Stack Language Command Line Interface
═══════════════════════════════════════════════════════════════════════════════

Usage:
    tinytalk run <file>              Run a .tt file
    tinytalk build --target js <file>  Compile to JavaScript
    tinytalk test                    Run test suite
    tinytalk repl                    Interactive REPL
"""

import sys
import argparse
from pathlib import Path

# Ensure package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


def cmd_run(args):
    """Run a tinyTalk file."""
    from realTinyTalk import run
    
    source = Path(args.file).read_text(encoding='utf-8')
    result = run(source)
    
    if result is not None and not args.quiet:
        print(result)


def cmd_build(args):
    """Compile to target language."""
    if args.target == 'js':
        from realTinyTalk.backends.js import compile_to_js
        
        source = Path(args.file).read_text(encoding='utf-8')
        js = compile_to_js(source, include_runtime=not args.no_runtime)
        
        if args.output:
            Path(args.output).write_text(js, encoding='utf-8')
            print(f'✓ Compiled to {args.output}')
        else:
            print(js)
    else:
        print(f'Unknown target: {args.target}')
        sys.exit(1)


def cmd_test(args):
    """Run the test suite."""
    import subprocess
    
    runner = Path(__file__).parent / 'tests' / 'runner.py'
    
    cmd = [sys.executable, str(runner)]
    if args.verbose:
        cmd.append('-v')
    if args.filter:
        cmd.extend(['--filter', args.filter])
    if args.target:
        cmd.extend(['--target', args.target])
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def cmd_repl(args):
    """Start interactive REPL."""
    from realTinyTalk import run
    
    print("realTinyTalk REPL v1.0")
    print("Type 'exit' or Ctrl+C to quit")
    print()
    
    while True:
        try:
            code = input(">>> ")
            if code.strip().lower() in ('exit', 'quit'):
                break
            
            # Handle multi-line input
            while code.count('{') > code.count('}'):
                code += '\n' + input("... ")
            
            result = run(code)
            if result is not None:
                print(result)
        
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except EOFError:
            print("\nBye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='realTinyTalk - The Sovereign Stack Language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tinytalk run hello.tt              Run a program
  tinytalk build -t js app.tt -o app.js  Compile to JavaScript
  tinytalk test                      Run test suite
  tinytalk test --target js          Run tests against JS output
  tinytalk repl                      Interactive mode
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # run command
    run_parser = subparsers.add_parser('run', help='Run a .tt file')
    run_parser.add_argument('file', help='File to run')
    run_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress result output')
    
    # build command
    build_parser = subparsers.add_parser('build', help='Compile to target language')
    build_parser.add_argument('file', help='File to compile')
    build_parser.add_argument('-t', '--target', default='js', choices=['js'], help='Target language')
    build_parser.add_argument('-o', '--output', help='Output file')
    build_parser.add_argument('--no-runtime', action='store_true', help='Omit runtime shim')
    
    # test command
    test_parser = subparsers.add_parser('test', help='Run test suite')
    test_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    test_parser.add_argument('--filter', help='Filter tests by name')
    test_parser.add_argument('--target', choices=['py', 'js'], help='Test against target')
    
    # repl command
    repl_parser = subparsers.add_parser('repl', help='Interactive REPL')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        cmd_run(args)
    elif args.command == 'build':
        cmd_build(args)
    elif args.command == 'test':
        cmd_test(args)
    elif args.command == 'repl':
        cmd_repl(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
