#!/usr/bin/env python3
"""
NEWTON CINEMA COMPANION - DEMO
═══════════════════════════════════════════════════════════════════════════════

Demonstrates the kinematic verification system in action.

Run with: python -m newton.cinema.demo
"""

from .core import KinematicCinemaCompanion, SceneType, KinematicLinguistics
from .matter import GlyphGeometry


def main():
    print("=" * 70)
    print("NEWTON CINEMA COMPANION v2.0 - KINEMATIC EDITION")
    print("\"The silence IS the instruction.\"")
    print("=" * 70)
    print()

    companion = KinematicCinemaCompanion(verbose=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 1: High priority comment during a quiet scene (VERIFIED)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("DEMO 1: High priority comment during quiet scene")
    print("─" * 70)
    companion.evaluate_intent(
        "The lighting here is strictly Bauhaus.",
        priority=0.8,
        scene_type=SceneType.QUIET
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 2: Low priority comment during a climax (FORBIDDEN/finfr)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("DEMO 2: Low priority comment during climax")
    print("─" * 70)
    companion.evaluate_intent(
        "I like his hat.",
        priority=0.2,
        scene_type=SceneType.CLIMAX
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 3: After being shushed, the same quiet scene becomes harder
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("DEMO 3: After user shush, ground (g) shrinks")
    print("─" * 70)
    companion.record_user_shush()
    companion.record_user_shush()
    companion.evaluate_intent(
        "Still Bauhaus.",
        priority=0.5,
        scene_type=SceneType.QUIET
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 4: Kinematic Damping in action
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("DEMO 4: Kinematic Damping - Reshaping forbidden speech")
    print("─" * 70)
    # Reset companion for fresh state
    companion = KinematicCinemaCompanion(verbose=True)
    companion.evaluate_intent(
        "That scene was absolutely incredible!",
        priority=0.7,
        scene_type=SceneType.DIALOGUE
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 5: Glyph Geometry Analysis
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("DEMO 5: Glyph Geometry Analysis")
    print("─" * 70)

    test_words = ["STABLE", "STRESS", "AMAZING", "GRAND"]
    for word in test_words:
        stability, vector = GlyphGeometry.analyze_word(word)
        print(f"  {word:12} → stability: {stability:.2f}, vector: {vector}")

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 6: Linguistic Instability Analysis
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("DEMO 6: Linguistic Instability Analysis")
    print("─" * 70)

    test_phrases = [
        "Good movie.",
        "Suspenseful scene!",
        "Zzz boring zzz",
    ]
    for phrase in test_phrases:
        analysis = KinematicLinguistics.analyze_detailed(phrase)
        print(f"  \"{phrase}\"")
        print(f"    Instability: {analysis['instability']:.3f}")
        unstable = KinematicLinguistics.find_unstable_words(phrase)
        if unstable:
            print(f"    Unstable words: {', '.join(unstable)}")
        print()

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 7: Scene Type Gravity Values
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("DEMO 7: Scene Type Gravity (g) Values")
    print("─" * 70)

    for scene_type in SceneType:
        bar = "█" * int(scene_type.gravity * 20)
        print(f"  {scene_type.name:12} g={scene_type.gravity:.2f} {bar}")

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 8: Statistics
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("DEMO 8: Companion Statistics")
    print("─" * 70)

    stats = companion.get_statistics()
    print(f"  Total intents evaluated: {stats['total_intents']}")
    print(f"  Spoken: {stats['spoken']}")
    print(f"  Silenced: {stats['silenced']}")
    print(f"  Damped: {stats['damped']}")
    print(f"  Silence rate: {stats['silence_rate']:.1%}")

    print("\n" + "=" * 70)
    print("Demo complete. Newton respects the Constraint Polytope.")
    print("=" * 70)


if __name__ == "__main__":
    main()
