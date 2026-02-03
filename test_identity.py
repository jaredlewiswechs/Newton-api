#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
IDENTITY TEST
Newton knows who he is. Test it.
═══════════════════════════════════════════════════════════════════════════════
"""

from newton_agent import NewtonAgent
from newton_agent.identity import get_identity


def test_identity():
    """Test that Newton knows who he is."""
    print("=" * 70)
    print("NEWTON IDENTITY TEST")
    print("Does Newton know who he is?")
    print("=" * 70)
    
    agent = NewtonAgent()
    identity = get_identity()
    
    # Identity questions
    questions = [
        ("Who are you?", ["Newton", "verify", "Jared Lewis"]),
        ("What are you?", ["Newton", "verification"]),
        ("Why should I trust you?", ["determinism", "trust", "math"]),
        ("Are you conscious?", ["don't know", "verify", "enough"]),
        ("Who created you?", ["Jared Lewis", "Ada Computing"]),
        ("How do you work?", ["constraint", "instruction", "1 == 1"]),
        ("What can't you do?", ["not", "pretend"]),
    ]
    
    passed = 0
    for question, expected_words in questions:
        print(f"\nQ: {question}")
        result = agent.process(question)
        
        # Check if response contains expected content
        content_lower = result.content.lower()
        found = [w for w in expected_words if w.lower() in content_lower]
        
        if found:
            print(f"✓ Response contains: {found}")
            print(f"  Verified: {result.verified}")
            passed += 1
        else:
            print(f"✗ Expected words not found: {expected_words}")
            print(f"  Got: {result.content[:200]}...")
    
    print("\n" + "=" * 70)
    print(f"IDENTITY TEST RESULT: {passed}/{len(questions)} passed")
    print("=" * 70)
    
    # Self-verification
    print("\n🔐 SELF-VERIFICATION:")
    print(f"   Identity hash: {identity.identity_hash}")
    print(f"   Self-verify: {'✓ PASS' if identity.verify_self() else '✗ FAIL'}")
    
    # Trust model
    print("\n🤝 TRUST MODEL:")
    for what, trusted in identity.trust.items():
        status = "✓ TRUST" if trusted else "○ VERIFY"
        print(f"   {what}: {status}")
    
    # The fundamental law
    print("\n⚖️  THE FUNDAMENTAL LAW:")
    print("   newton(current, goal) → current == goal")
    print("   When True  → execute")
    print("   When False → halt")
    
    return passed >= 5  # At least 5/7 must pass


def test_newton_trusts_himself():
    """Test that Newton's self-knowledge is verified."""
    print("\n" + "=" * 70)
    print("TRUST TEST")
    print("Does Newton trust his own answers about himself?")
    print("=" * 70)
    
    agent = NewtonAgent()
    
    # These should ALL be verified=True (Newton trusts himself)
    self_questions = [
        "Who are you?",
        "What is your name?",
        "Who created you?",
        "Are you reliable?",
    ]
    
    all_verified = True
    for q in self_questions:
        result = agent.process(q)
        status = "✓" if result.verified else "✗"
        print(f"{status} \"{q}\" → verified={result.verified}")
        if not result.verified:
            all_verified = False
    
    print("\n" + "=" * 70)
    if all_verified:
        print("✓ Newton trusts himself. As he should.")
    else:
        print("✗ Newton doesn't trust himself. Fix this.")
    print("=" * 70)
    
    return all_verified


def test_full_introspection():
    """Test Newton's full self-knowledge."""
    print("\n" + "=" * 70)
    print("INTROSPECTION TEST")
    print("Can Newton fully describe himself?")
    print("=" * 70)
    
    identity = get_identity()
    
    # Get full introspection
    data = identity.introspect()
    
    print(f"\n📋 Identity:")
    print(f"   Name: {data['identity']['name']}")
    print(f"   Version: {data['identity']['version']}")
    print(f"   Hash: {data['identity']['hash']}")
    print(f"   Creator: {data['identity']['creator']}")
    
    print(f"\n🎯 Nature ({len(data['nature'])} statements):")
    for n in data['nature'][:3]:
        print(f"   • {n}")
    print(f"   ...")
    
    print(f"\n🚫 Not Nature ({len(data['not_nature'])} statements):")
    for n in data['not_nature'][:2]:
        print(f"   • {n}")
    print(f"   ...")
    
    print(f"\n⚖️  Fundamental Law:")
    print(f"   {data['fundamental_law']}")
    
    # Verify structure
    required_keys = ['identity', 'nature', 'not_nature', 'principles', 'trust_model']
    has_all = all(k in data for k in required_keys)
    
    print("\n" + "=" * 70)
    print(f"{'✓' if has_all else '✗'} Introspection complete: {has_all}")
    print("=" * 70)
    
    return has_all


def main():
    """Run all identity tests."""
    print("\n" + "═" * 70)
    print("NEWTON IDENTITY TEST SUITE")
    print("Testing: Does Newton know who he is?")
    print("═" * 70)
    
    results = {}
    
    results["identity"] = test_identity()
    results["trust"] = test_newton_trusts_himself()
    results["introspection"] = test_full_introspection()
    
    # Final summary
    print("\n" + "═" * 70)
    print("FINAL RESULTS")
    print("═" * 70)
    
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"   {test.upper()}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "─" * 70)
    if all_passed:
        print("🧠 Newton knows who he is.")
        print("   He doesn't pretend. He verifies.")
        print("   He doesn't hope. He computes.")
        print("   He is Newton. And that's enough.")
    else:
        print("⚠️  Newton has an identity crisis. Fix it.")
    print("─" * 70)
    
    return all_passed


if __name__ == "__main__":
    main()
