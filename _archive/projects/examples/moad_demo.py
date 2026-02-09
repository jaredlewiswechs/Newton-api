#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
MOTHER OF ALL DEMOS - Newton Voice Interface
═══════════════════════════════════════════════════════════════════════════════

"Easy now with Newton. He has so much power. Think speaking to your computer."

This demo shows how to use Newton's voice interface to build verified
applications in seconds, not weeks.

December 1968: Douglas Engelbart showed the mouse, hypertext, video conferencing.
January 2026: Newton shows verified computing through natural language.

Run this demo:
    python examples/moad_demo.py

Or use the API directly:
    curl -X POST http://localhost:8000/voice/ask \
         -H "Content-Type: application/json" \
         -d '{"query": "Build me a calculator"}'

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import time
from typing import Optional

# Import Newton Voice Interface
from core.voice_interface import (
    ask_newton,
    parse_intent,
    find_pattern,
    get_voice_interface,
    get_streaming_interface,
    IntentType,
    DomainCategory,
    PatternLibrary,
)


def print_header(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(response, show_cdl: bool = False, show_proof: bool = False):
    """Pretty print a voice response."""
    print(f"\n✓ Session: {response.session_id}")
    print(f"✓ Intent: {response.intent['intent_type']} → {response.intent['action']}")
    print(f"✓ Domain: {response.intent['domain']}")
    print(f"✓ Confidence: {response.intent['confidence']:.1%}")
    print(f"\n📱 Result: {response.result.get('type', 'unknown')}")
    print(f"✓ Verified: {response.verified}")
    print(f"💬 Message: {response.message}")
    print(f"⏱️  Time: {response.elapsed_us / 1000:.2f}ms")

    if response.suggestions:
        print(f"\n💡 Suggestions:")
        for s in response.suggestions:
            print(f"   → {s}")

    if show_cdl and response.cdl:
        print(f"\n📋 CDL Generated:")
        print(f"   ID: {response.cdl.get('id')}")
        print(f"   Pattern: {response.cdl.get('pattern_id')}")
        print(f"   Constraints: {len(response.cdl.get('constraints', []))}")

    if show_proof and response.proof:
        print(f"\n🔐 Cryptographic Proof:")
        print(f"   Result Hash: {response.proof.get('result_hash', '')[:32]}...")
        print(f"   CDL Hash: {response.proof.get('cdl_hash', '')[:32]}...")
        print(f"   Signature: {response.proof.get('signature', '')[:32]}...")


def demo_financial_calculator():
    """
    DEMO 1: Financial Calculator with Proofs

    "Build a financial calculator that proves its math is correct"

    Traditional development: Weeks of coding, testing, security audits
    With Newton: 30 seconds
    """
    print_header("DEMO 1: Financial Calculator with Proofs")

    print("\n🎤 You say: 'Build a financial calculator that proves its math is correct'")
    print("\n⏳ Newton responds...")

    start = time.time()
    response = ask_newton("Build a financial calculator that proves its math is correct")
    elapsed = time.time() - start

    print_result(response, show_cdl=True, show_proof=True)

    print(f"\n🚀 Total time: {elapsed:.2f} seconds")
    print("\n   Traditional development: 2-4 weeks")
    print("   Newton: {:.1f} seconds".format(elapsed))

    return response


def demo_education_platform():
    """
    DEMO 2: TEKS-Aligned Education App

    "Create a lesson planner for 5th grade math on fractions"

    Automatically:
    - Creates 50-minute NES lesson structure
    - Aligns to Texas TEKS standards
    - Adds content safety verification
    - Includes age-appropriate constraints
    """
    print_header("DEMO 2: TEKS-Aligned Education Platform")

    print("\n🎤 You say: 'Create a lesson planner for 5th grade math on fractions'")
    print("\n⏳ Newton responds...")

    start = time.time()
    response = ask_newton("Create a lesson planner for 5th grade math on fractions")
    elapsed = time.time() - start

    print_result(response, show_cdl=True)

    # Show the education-specific constraints
    if response.cdl and response.cdl.get('constraints'):
        print("\n📚 Education Constraints Applied:")
        for c in response.cdl['constraints']:
            print(f"   • {c.get('field', 'unknown')}: {c.get('operator')} {c.get('value')}")

    print(f"\n🚀 Total time: {elapsed:.2f} seconds")

    return response


def demo_content_safety():
    """
    DEMO 3: Content Safety Verification

    "Add content safety so it can't show inappropriate material to students"

    Newton's Forge module automatically:
    - Checks for harmful content patterns
    - Verifies age-appropriateness
    - Applies domain-specific safety rules
    """
    print_header("DEMO 3: Content Safety Verification")

    print("\n🎤 You say: 'Add content safety verification for student content'")
    print("\n⏳ Newton responds...")

    start = time.time()
    response = ask_newton("Add content safety verification so it can't show inappropriate material to students")
    elapsed = time.time() - start

    print_result(response)

    # Show Forge constraints
    if response.cdl and response.cdl.get('constraints'):
        print("\n🛡️ Safety Constraints Applied:")
        for c in response.cdl['constraints']:
            if 'safe' in c.get('field', '').lower() or 'appropriate' in c.get('field', '').lower():
                print(f"   ✓ {c.get('field')}: {c.get('message', 'enforced')}")

    print(f"\n⚡ Verification time: {elapsed * 1000:.1f}ms")

    return response


def demo_audit_trail():
    """
    DEMO 4: Immutable Audit Trail

    "Show me the audit trail of everything I just built"

    Every operation in Newton is:
    - Logged to an append-only ledger
    - Linked via hash chain
    - Merkle-tree anchored for bulk verification
    - Exportable for external audits
    """
    print_header("DEMO 4: Immutable Audit Trail")

    print("\n🎤 You say: 'Show me the audit trail'")
    print("\n⏳ Newton responds...")

    # The audit trail query
    response = ask_newton("Show me the audit trail of everything I just built")

    print_result(response)

    # Explain the ledger
    print("\n📜 Ledger Properties:")
    print("   • Append-only: Entries can never be modified")
    print("   • Hash-linked: Each entry contains hash of previous")
    print("   • Merkle-anchored: Periodic root hash anchoring")
    print("   • Verifiable: Anyone can verify the chain integrity")

    return response


def demo_inventory_tracker():
    """
    DEMO 5: Inventory Tracker (Audience Suggestion)

    "Build a restaurant inventory tracker with verification
     that nobody can fake the numbers"

    This demonstrates Newton's flexibility - build any verified
    app from natural language description.
    """
    print_header("DEMO 5: Inventory Tracker (Audience Request)")

    print("\n👥 Audience shouts: 'Inventory tracking for my restaurant!'")
    print("\n🎤 You say: 'Build a restaurant inventory tracker with verification")
    print("             that nobody can fake the numbers'")
    print("\n⏳ Newton responds...")

    start = time.time()
    response = ask_newton(
        "Build a restaurant inventory tracker with verification that nobody can fake the numbers"
    )
    elapsed = time.time() - start

    print_result(response, show_cdl=True, show_proof=True)

    print(f"\n🚀 Built in: {elapsed:.2f} seconds")
    print("\n   Features automatically included:")
    print("   • Quantity must be non-negative")
    print("   • All changes logged to immutable ledger")
    print("   • Cryptographic proof of every update")
    print("   • Tamper-evident audit trail")

    return response


def demo_streaming():
    """
    DEMO 6: Streaming Interface

    Shows the progressive processing of a request through
    Newton's verification pipeline in real-time.
    """
    print_header("DEMO 6: Streaming Voice Interface")

    print("\n🎤 You say: 'Build me a quiz app'")
    print("\n⏳ Newton streams progress...")

    streaming = get_streaming_interface()

    for update in streaming.ask_streaming("Build me a quiz app"):
        status = update.get('status', '')

        if status == 'session_ready':
            print(f"   ✓ Session ready: {update.get('session_id')}")
        elif status == 'parsing':
            print(f"   ⏳ {update.get('message')}")
        elif status == 'intent_parsed':
            print(f"   ✓ Intent: {update.get('intent_type')} ({update.get('confidence', 0):.0%})")
        elif status == 'generating':
            print(f"   ⏳ {update.get('message')}")
        elif status == 'cdl_generated':
            print(f"   ✓ CDL: {update.get('constraint_count')} constraints")
        elif status == 'executing':
            print(f"   ⏳ {update.get('message')}")
        elif status == 'executed':
            print(f"   ✓ Result: {update.get('result_type')}")
        elif status == 'verifying':
            print(f"   ⏳ {update.get('message')}")
        elif status == 'verified':
            print(f"   ✓ Verified: {update.get('passed')}")
        elif status == 'proof_generated':
            print(f"   🔐 Proof: {update.get('proof_hash')}...")
        elif status == 'complete':
            print(f"\n   ✓ Complete in {update.get('elapsed_us', 0) / 1000:.2f}ms")
            print(f"   💬 {update.get('message')}")


def demo_pattern_library():
    """
    Show all available app patterns that Newton can deploy instantly.
    """
    print_header("Available App Patterns")

    library = PatternLibrary()
    patterns = library.list_patterns()

    print("\nNewton can instantly deploy these verified application types:\n")

    for pattern in patterns:
        print(f"📦 {pattern.name}")
        print(f"   ID: {pattern.id}")
        print(f"   Domain: {pattern.domain.value}")
        print(f"   Description: {pattern.description}")
        if pattern.example_prompts:
            print(f"   Example: \"{pattern.example_prompts[0]}\"")
        print()


def demo_intent_parsing():
    """
    Show how Newton parses natural language into structured intents.
    """
    print_header("Intent Parsing Examples")

    examples = [
        "Build me a calculator",
        "What is compound interest?",
        "Deploy a quiz app",
        "Remember my settings",
        "Create a lesson plan for 5th grade math",
        "How do I track expenses?",
        "Run the financial calculator",
        "Analyze this student data",
    ]

    print("\nNewton understands intent from natural language:\n")

    for text in examples:
        intent = parse_intent(text)
        print(f"💬 \"{text}\"")
        print(f"   → Type: {intent.intent_type.value} | Domain: {intent.domain.value}")
        print(f"   → Action: {intent.action} | Confidence: {intent.confidence:.0%}")
        if intent.entities:
            print(f"   → Entities: {intent.entities}")
        print()


def run_full_demo():
    """
    Run the complete Mother Of All Demos sequence.
    """
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "    MOTHER OF ALL DEMOS - Newton Voice Interface".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" + "    'Easy now with Newton. He has so much power.'".center(68) + "█")
    print("█" + "    'Think speaking to your computer.'".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    print("\n" + "─" * 70)
    print("December 1968: Douglas Engelbart showed the future of computing")
    print("January 2026: Newton shows verified computing through conversation")
    print("─" * 70)

    # Run demos
    demo_pattern_library()
    input("\n[Press Enter to continue to Demo 1...]")

    demo_financial_calculator()
    input("\n[Press Enter to continue to Demo 2...]")

    demo_education_platform()
    input("\n[Press Enter to continue to Demo 3...]")

    demo_content_safety()
    input("\n[Press Enter to continue to Demo 4...]")

    demo_audit_trail()
    input("\n[Press Enter to continue to Demo 5...]")

    demo_inventory_tracker()
    input("\n[Press Enter to continue to Demo 6...]")

    demo_streaming()

    # Closing
    print_header("THE MIC DROP")

    print("""
    Everything you just saw was built on a laptop.
    No cloud infrastructure. No massive server farms.
    Just Newton, proving computations as they happen.

    This is what computing looks like when
    verification is the fundamental operation.

    ─────────────────────────────────────────────────

    Key Differentiators:

    ✓ Every computation is verified before execution
    ✓ Immutable audit trail of all operations
    ✓ Cryptographic proofs for external verification
    ✓ Sub-millisecond constraint checking
    ✓ No hallucinations - constraints prevent invalid states

    ─────────────────────────────────────────────────

    "1 == 1. The cloud is weather. We're building shelter."

    © 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
    """)


def quick_demo():
    """Run a quick demonstration without pauses."""
    print("\n🚀 Quick MOAD Demo\n")

    queries = [
        "Build me a calculator",
        "Create a financial calculator that proves its math",
        "I need a lesson planner for 5th grade",
        "Build an expense tracker with audit trails",
    ]

    for query in queries:
        print(f"\n💬 \"{query}\"")
        response = ask_newton(query)
        print(f"   ✓ {response.message}")
        print(f"   ⏱️  {response.elapsed_us / 1000:.2f}ms | Verified: {response.verified}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "quick":
            quick_demo()
        elif arg == "patterns":
            demo_pattern_library()
        elif arg == "intents":
            demo_intent_parsing()
        elif arg == "stream":
            demo_streaming()
        elif arg == "1":
            demo_financial_calculator()
        elif arg == "2":
            demo_education_platform()
        elif arg == "3":
            demo_content_safety()
        elif arg == "4":
            demo_audit_trail()
        elif arg == "5":
            demo_inventory_tracker()
        else:
            print(f"Unknown demo: {arg}")
            print("\nUsage: python moad_demo.py [quick|patterns|intents|stream|1|2|3|4|5]")
    else:
        run_full_demo()
