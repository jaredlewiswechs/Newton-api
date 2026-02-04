"""
═══════════════════════════════════════════════════════════════════════════════
realTinyTalk CONFORMANCE TEST RUNNER v1.1
Industrial-strength test suite with pinpointed failures and categories
═══════════════════════════════════════════════════════════════════════════════

Features:
- Pinpointed failure output (file:line + diff)
- Test categories (core/stdlib/extras/meta)
- Filter by name/category
- CI-friendly exit codes
- Detailed vs summary output modes
"""

import sys
import os
import io
import re
import time
import fnmatch
import traceback
from pathlib import Path
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from enum import Enum

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from realTinyTalk import run
from realTinyTalk.runtime import TinyTalkError


# =============================================================================
# TEST CATEGORIES
# =============================================================================

class TestCategory(Enum):
    """Test categories for organization."""
    CORE = "core"           # Parser/runtime semantics
    STDLIB = "stdlib"       # Bundled library functions
    EXTRAS = "extras"       # Experimental features
    META = "meta"           # Interpreter behavior tests


# Map test files to categories
FILE_CATEGORIES = {
    "01_literals": TestCategory.CORE,
    "02_arithmetic": TestCategory.CORE,
    "03_comparisons": TestCategory.CORE,
    "04_variables": TestCategory.CORE,
    "05_control_flow": TestCategory.CORE,
    "06_functions": TestCategory.CORE,
    "07_lists": TestCategory.CORE,
    "08_maps": TestCategory.CORE,
    "09_strings": TestCategory.STDLIB,
    "10_step_chains": TestCategory.STDLIB,
    "11_blueprints": TestCategory.CORE,
    "12_builtins": TestCategory.STDLIB,
    "13_space_args": TestCategory.CORE,
    "14_properties": TestCategory.STDLIB,
    "15_algorithms": TestCategory.CORE,
    "16_edge_cases": TestCategory.CORE,
    "17_metatests": TestCategory.META,
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    expected: str
    actual: str
    code: str = ""
    file: str = ""
    line: int = 0
    error: Optional[str] = None
    error_line: Optional[int] = None
    time_ms: float = 0.0
    category: TestCategory = TestCategory.CORE


@dataclass
class SuiteResult:
    """Result of a test suite."""
    name: str
    file: str
    category: TestCategory
    results: List[TestResult] = field(default_factory=list)
    time_ms: float = 0.0
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def total(self) -> int:
        return len(self.results)


# =============================================================================
# PARSING
# =============================================================================

def parse_test_file(content: str, filename: str) -> List[Tuple[str, str, str, int]]:
    """
    Parse a .tt test file.
    
    Format:
    // TEST: test name
    // EXPECT: expected output
    //   multi-line expected
    code here
    // END
    
    Returns list of (name, code, expected_output, line_number)
    """
    tests = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for TEST marker
        if line.startswith('// TEST:'):
            name = line[8:].strip()
            start_line = i + 1
            expected_lines = []
            code_lines = []
            
            i += 1
            # Collect EXPECT lines
            while i < len(lines) and lines[i].strip().startswith('// EXPECT:'):
                expected_lines.append(lines[i].strip()[10:].strip())
                i += 1
            
            # Also handle multi-line expects
            while i < len(lines) and lines[i].strip().startswith('//   '):
                expected_lines.append(lines[i].strip()[5:])
                i += 1
            
            code_start = i + 1
            # Collect code until END
            while i < len(lines) and not lines[i].strip().startswith('// END'):
                code_lines.append(lines[i])
                i += 1
            
            expected = '\n'.join(expected_lines)
            code = '\n'.join(code_lines)
            tests.append((name, code, expected, code_start))
        
        i += 1
    
    return tests


# =============================================================================
# TEST EXECUTION
# =============================================================================

def run_test(name: str, code: str, expected: str, file: str, line: int, 
             category: TestCategory) -> TestResult:
    """Run a single test and return detailed result."""
    start = time.time()
    
    stdout_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture):
            run(code)
        
        actual = stdout_capture.getvalue().strip()
        expected_clean = expected.strip()
        
        # Normalize whitespace for comparison
        actual_norm = ' '.join(actual.split())
        expected_norm = ' '.join(expected_clean.split())
        
        passed = actual_norm == expected_norm
        
        return TestResult(
            name=name,
            passed=passed,
            expected=expected_clean,
            actual=actual,
            code=code,
            file=file,
            line=line,
            category=category,
            time_ms=(time.time() - start) * 1000
        )
    
    except Exception as e:
        actual = stdout_capture.getvalue().strip()
        error_str = str(e)
        
        # Try to extract line number from error
        error_line = None
        line_match = re.search(r'Line (\d+)', error_str)
        if line_match:
            error_line = int(line_match.group(1))
        
        # Check if we expected an error
        if expected.startswith('ERROR:'):
            expected_error = expected[6:].strip()
            if expected_error in error_str:
                return TestResult(
                    name=name,
                    passed=True,
                    expected=expected,
                    actual=f"ERROR: {e}",
                    code=code,
                    file=file,
                    line=line,
                    category=category,
                    time_ms=(time.time() - start) * 1000
                )
        
        return TestResult(
            name=name,
            passed=False,
            expected=expected,
            actual=actual,
            code=code,
            file=file,
            line=line,
            error=error_str,
            error_line=error_line,
            category=category,
            time_ms=(time.time() - start) * 1000
        )


def run_suite(path: Path) -> SuiteResult:
    """Run all tests in a file."""
    start = time.time()
    
    content = path.read_text(encoding='utf-8')
    tests = parse_test_file(content, path.name)
    
    # Get category
    stem = path.stem
    category = FILE_CATEGORIES.get(stem, TestCategory.CORE)
    
    results = []
    for name, code, expected, line in tests:
        result = run_test(name, code, expected, path.name, line, category)
        results.append(result)
    
    return SuiteResult(
        name=stem,
        file=path.name,
        category=category,
        results=results,
        time_ms=(time.time() - start) * 1000
    )


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def format_diff(expected: str, actual: str, max_len: int = 60) -> str:
    """Format a diff between expected and actual values."""
    lines = []
    
    exp_lines = expected.split('\n')
    act_lines = actual.split('\n')
    
    # Show first difference
    for i, (e, a) in enumerate(zip(exp_lines, act_lines)):
        if e.strip() != a.strip():
            lines.append(f"  line {i+1}:")
            lines.append(f"    expected: {repr(e[:max_len])}")
            lines.append(f"    actual:   {repr(a[:max_len])}")
            break
    else:
        if len(exp_lines) != len(act_lines):
            lines.append(f"  expected {len(exp_lines)} lines, got {len(act_lines)}")
    
    return '\n'.join(lines)


def format_failure(result: TestResult, show_code: bool = False) -> str:
    """Format a test failure with full context."""
    lines = []
    
    # Header with location
    lines.append(f"FAIL {result.file} :: {result.name}")
    lines.append(f"  at: {result.file}:{result.line}")
    
    # Error info
    if result.error:
        lines.append(f"  error: {result.error}")
        if result.error_line:
            lines.append(f"  error at line: {result.error_line}")
    else:
        # Value diff
        lines.append(f"  expected: {repr(result.expected[:60])}")
        lines.append(f"  got:      {repr(result.actual[:60])}")
        
        if result.expected != result.actual:
            diff = format_diff(result.expected, result.actual)
            if diff:
                lines.append(diff)
    
    # Optionally show code
    if show_code and result.code:
        lines.append("  code:")
        for i, code_line in enumerate(result.code.split('\n')[:5]):
            lines.append(f"    {i+1}: {code_line}")
        if len(result.code.split('\n')) > 5:
            lines.append("    ...")
    
    return '\n'.join(lines)


def print_results(suites: List[SuiteResult], verbose: bool = False, 
                  show_code: bool = False, max_failures: int = 10) -> bool:
    """Print test results with industrial-strength formatting."""
    total_passed = 0
    total_failed = 0
    total_time = 0.0
    all_failures: List[TestResult] = []
    
    # Category stats
    category_stats: Dict[TestCategory, Tuple[int, int]] = {}
    
    print()
    print("=" * 65)
    print("  realTinyTalk v1.0 CONFORMANCE TEST RESULTS")
    print("=" * 65)
    print()
    
    for suite in suites:
        status = "[PASS]" if suite.failed == 0 else "[FAIL]"
        cat_label = f"[{suite.category.value}]"
        
        print(f"{status} {cat_label:8} {suite.name}: {suite.passed}/{suite.total} ({suite.time_ms:.1f}ms)")
        
        # Track category stats
        cat = suite.category
        prev = category_stats.get(cat, (0, 0))
        category_stats[cat] = (prev[0] + suite.passed, prev[1] + suite.total)
        
        if verbose:
            for result in suite.results:
                status = "[PASS]" if result.passed else "[FAIL]"
                print(f"    {status} {result.name}")
        
        # Collect failures
        for result in suite.results:
            if not result.passed:
                all_failures.append(result)
        
        total_passed += suite.passed
        total_failed += suite.failed
        total_time += suite.time_ms
    
    # Print category summary
    print()
    print("-" * 65)
    print("  Category Summary:")
    for cat in TestCategory:
        if cat in category_stats:
            passed, total = category_stats[cat]
            pct = (passed / total * 100) if total > 0 else 0
            status = "[OK]" if passed == total else "[!!]"
            print(f"    {status} {cat.value:8}: {passed}/{total} ({pct:.0f}%)")
    
    # Print failures (up to max)
    if all_failures:
        print()
        print("-" * 65)
        print(f"  FAILURES ({len(all_failures)} total, showing first {min(len(all_failures), max_failures)}):")
        print()
        
        for i, failure in enumerate(all_failures[:max_failures]):
            print(format_failure(failure, show_code))
            print()
        
        if len(all_failures) > max_failures:
            print(f"  ... and {len(all_failures) - max_failures} more failures")
    
    # Final summary
    print("-" * 65)
    
    if total_failed == 0:
        print(f"[OK] ALL {total_passed} TESTS PASSED")
    else:
        print(f"[!!] {total_failed} FAILED, {total_passed} passed")
    
    print(f"     time: {total_time/1000:.2f}s")
    print("=" * 65)
    print()
    
    return total_failed == 0


# =============================================================================
# CLI
# =============================================================================

def main():
    """Run conformance tests with full CLI support."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='realTinyTalk Conformance Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python runner.py                    # Run all tests
  python runner.py -v                 # Verbose output
  python runner.py --filter strings   # Run tests matching 'strings'
  python runner.py --category core    # Run only core tests
  python runner.py 09_strings.tt      # Run specific file
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Show all test results')
    parser.add_argument('-c', '--code', action='store_true',
                        help='Show code for failed tests')
    parser.add_argument('--filter', type=str, default=None,
                        help='Filter tests by name pattern')
    parser.add_argument('--category', type=str, default=None,
                        choices=['core', 'stdlib', 'extras', 'meta'],
                        help='Run only tests in category')
    parser.add_argument('--max-failures', type=int, default=10,
                        help='Maximum failures to display')
    parser.add_argument('files', nargs='*', help='Specific test files to run')
    
    args = parser.parse_args()
    
    tests_dir = Path(__file__).parent
    
    # Collect test files
    if args.files:
        test_files = []
        for f in args.files:
            if '*' in f:
                test_files.extend(tests_dir.glob(f))
            else:
                path = tests_dir / f if not Path(f).is_absolute() else Path(f)
                if path.exists():
                    test_files.append(path)
                else:
                    print(f"Warning: {f} not found")
    else:
        test_files = sorted(tests_dir.glob('*.tt'))
    
    if not test_files:
        print("No test files found!")
        return 1
    
    # Filter by category
    if args.category:
        target_cat = TestCategory(args.category)
        test_files = [
            f for f in test_files 
            if FILE_CATEGORIES.get(f.stem, TestCategory.CORE) == target_cat
        ]
    
    # Run suites
    suites = []
    for path in test_files:
        suite = run_suite(path)
        
        # Filter results by name pattern
        if args.filter:
            suite.results = [
                r for r in suite.results 
                if fnmatch.fnmatch(r.name.lower(), f'*{args.filter.lower()}*')
            ]
        
        if suite.results:  # Only add if has matching tests
            suites.append(suite)
    
    if not suites:
        print("No tests matched filters!")
        return 1
    
    success = print_results(
        suites, 
        verbose=args.verbose, 
        show_code=args.code,
        max_failures=args.max_failures
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
