#!/usr/bin/env python3
"""
TI CALCULATOR COMPREHENSIVE TEST
Tests all TI-84 style calculations through Newton Agent.
"""

from newton_agent import NewtonAgent


def test_ti_calculator():
    """Test TI-84 style calculations."""
    agent = NewtonAgent()
    
    tests = [
        # Basic operations
        ("2 + 2", "4"),
        ("3 * 3 * 3", "27"),
        ("10 - 5 + 2", "7"),
        ("100 / 4", "25"),
        ("2 + 3 * 4", "14"),  # Precedence
        ("(2 + 3) * 4", "20"),  # Parentheses
        
        # Powers
        ("2^10", "1024"),
        ("3^3", "27"),
        ("2**8", "256"),
        
        # Functions
        ("sqrt(16)", "4"),
        ("sqrt(144)", "12"),
        ("abs(-42)", "42"),
        ("floor(3.7)", "3"),
        ("ceil(3.2)", "4"),
        
        # Trig (basic)
        ("sin(0)", "0"),
        ("cos(0)", "1"),
        
        # Logs
        ("log(100)", "2"),  # Base 10
        
        # Factorial
        ("5!", "120"),
        
        # Complex
        ("sqrt(16) + 2^3", "12"),
        ("2 * 3 + 4 * 5", "26"),
        ("100 / 10 / 2", "5"),
        
        # Natural language
        ("What is 3 * 3 * 3?", "27"),
        ("calculate 2^10", "1024"),
        ("what's sqrt(256)?", "16"),
        
        # Negative numbers
        ("-5 + 10", "5"),
        ("5 + -3", "2"),
    ]
    
    print("=" * 60)
    print("TI CALCULATOR INTEGRATION TEST")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for query, expected in tests:
        result = agent.process(query)
        # Check if expected value is in the response
        got_correct = expected in result.content
        
        if got_correct:
            status = "✓"
            passed += 1
        else:
            status = "✗"
            failed += 1
            
        print(f"{status} {query:30} | Expected: {expected:8} | Got: {got_correct}")
        
        if not got_correct:
            print(f"  Full response: {result.content[:100]}...")
    
    print("=" * 60)
    print(f"Results: {passed}/{passed + failed} passed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = test_ti_calculator()
    exit(0 if success else 1)
