#!/usr/bin/env python3
"""
KINEMATIC LINGUISTICS v1.1 - DEMONSTRATION
A Geometric Substrate for Semantic Reliability

This demo implements the empirical validation cases from the specification:
- Section 3: Blind Geometry Tests (TRUST, FORCE, DREAM, SAFE, FIX)
- Section 4: Phonosemantic Cluster Analysis
- Section 5: Applied Case Studies (Distortion Index)
- Section 6: Hallucination Prevention

Run: python -m newton.kinematic_linguistics.demo
"""

from . import (
    GlyphRegistry,
    PhonosemanticsRegistry,
    WordAssemblyAnalyzer,
    DistortionIndexCalculator,
    AntonymAnalyzer,
    KinematicCompiler,
    CompilerRegime,
    HallucinationDetector,
    WORD_GEOMETRY_EXAMPLES,
)


def print_header(title: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def demo_glyph_table() -> None:
    """Demonstrate the Glyph Geometry Model (Section 2.1)."""
    print_header("GLYPH GEOMETRY MODEL (Section 2.1)")

    print("\nSample Glyph Properties:")
    print("-" * 70)
    print(f"{'Glyph':<6} {'Topology':<30} {'Stability':<10} {'Type'}")
    print("-" * 70)

    for char in ['A', 'S', 'T', 'O', 'K', 'M']:
        glyph = GlyphRegistry.get(char)
        print(f"{char:<6} {glyph.topology:<30} {glyph.stability:<10.2f} "
              f"{'Consonant' if glyph.is_consonant else 'Vowel'}")

    print("\nStability Classes:")
    print(f"  HIGH (0.7+): {', '.join(sorted(GlyphRegistry.HIGH_STABILITY))}")
    print(f"  MEDIUM (0.5-0.69): {', '.join(sorted(GlyphRegistry.MEDIUM_STABILITY))}")
    print(f"  LOW (<0.5): {', '.join(sorted(GlyphRegistry.LOW_STABILITY))}")


def demo_blind_geometry_tests() -> None:
    """Demonstrate Blind Geometry Tests (Section 3)."""
    print_header("BLIND GEOMETRY TESTS (Section 3)")

    test_words = ["TRUST", "FORCE", "DREAM", "SAFE", "FIX"]

    for word in test_words:
        print(f"\n--- Test Case: {word} ---")
        assembly = WordAssemblyAnalyzer.analyze(word)

        print(f"\nLetter Decomposition:")
        for role in assembly.letters:
            pos = role.position.value.upper()
            print(f"  {role.letter} ({pos}): {role.glyph_mechanics.mechanical_role}")

        print(f"\nMechanical Prediction: {assembly.mechanical_prediction}")
        print(f"Stability: {assembly.vector.stability_score:.2f} ({assembly.stability_class.value})")

        if assembly.phonosemantic_clusters:
            clusters = [c.pattern for c in assembly.phonosemantic_clusters]
            print(f"Phonosemantic Clusters: {', '.join(clusters)}")

        # Check if we have a reference prediction
        if word in WORD_GEOMETRY_EXAMPLES:
            ref = WORD_GEOMETRY_EXAMPLES[word]
            print(f"Reference Assembly: {ref['assembly']}")


def demo_antonym_validation() -> None:
    """Demonstrate Antonym Analysis (Section 3 + v1.1 Refinement 2)."""
    print_header("ANTONYM GEOMETRIC VALIDATION (Section 3 + v1.1)")

    test_pairs = [
        ("TRUST", "DOUBT"),
        ("TRUST", "BETRAY"),
        ("SAFE", "DANGER"),
        ("FORCE", "WEAK"),
        ("DREAM", "REALITY"),
        ("FIX", "BREAK"),
    ]

    for word1, word2 in test_pairs:
        analysis = AntonymAnalyzer.analyze(word1, word2)
        print(f"\n{word1} vs {word2}:")
        print(f"  Type: {analysis.antonym_type.value}")
        print(f"  Geometric Similarity: {analysis.geometric_similarity:.2f}")
        print(f"  Dictionary Antonym: {analysis.is_dictionary_antonym}")
        print(f"  Geometric Antonym: {analysis.is_geometric_antonym}")
        print(f"  {analysis.explanation}")


def demo_phonosemantic_clusters() -> None:
    """Demonstrate Phonosemantic Cluster Analysis (Section 4)."""
    print_header("PHONOSEMANTIC CLUSTER ANALYSIS (Section 4)")

    clusters_to_demo = ["-ST", "FL-", "GL-", "SP-"]

    for pattern in clusters_to_demo:
        cluster = PhonosemanticsRegistry.get_cluster(pattern)
        if cluster:
            print(f"\n{pattern} Cluster ({cluster.position}):")
            print(f"  Meaning: {cluster.mechanical_meaning}")
            print(f"  Examples: {', '.join(cluster.examples)}")

    print("\n--- Cluster Detection in Words ---")
    test_words = ["TRUST", "FLOW", "GLASS", "SPEED", "SPREAD"]
    for word in test_words:
        clusters = PhonosemanticsRegistry.detect_clusters(word)
        if clusters:
            patterns = [c.pattern for c in clusters]
            print(f"  {word}: {', '.join(patterns)}")
        else:
            print(f"  {word}: (no clusters)")


def demo_distortion_index() -> None:
    """Demonstrate Distortion Index Calculation (Section 5.3)."""
    print_header("DISTORTION INDEX ANALYSIS (Section 5.3)")

    print("\n--- Market Decline Example ---")
    # From specification: -30% described as "Correction"
    report = DistortionIndexCalculator.calculate("Correction", -0.30)
    print(f"Word: '{report.word_used}'")
    print(f"Word Geometry Predicts: {abs(report.word_vector):.1%}")
    print(f"Reality: {abs(report.reality_vector):.1%}")
    print(f"Distortion Index: {report.distortion_index:.2f}")
    print(f"Accuracy: {report.accuracy_percentage:.0f}%")
    print(f"Is Misleading: {report.is_misleading}")
    print(f"Recommended Word: {report.recommended_word}")
    print(f"Explanation: {report.explanation}")

    print("\n--- Additional Examples ---")
    examples = [
        ("Decline", -0.15),
        ("Crash", -0.35),
        ("Minor", 0.05),
        ("Severe", 0.70),
    ]

    for word, reality in examples:
        report = DistortionIndexCalculator.calculate(word, reality)
        status = "OK" if not report.is_misleading else "MISLEADING"
        print(f"  '{word}' for {abs(reality):.0%}: "
              f"D={report.distortion_index:.2f} [{status}]")


def demo_compiler() -> None:
    """Demonstrate Kinematic Compiler (Section 6)."""
    print_header("KINEMATIC COMPILER (Section 6)")

    # Test with different regimes
    print("\n--- General Regime ---")
    compiler = KinematicCompiler(CompilerRegime.GENERAL)
    proof = compiler.compile("Execute standard trim adjustment")
    print(f"Input: '{proof.input_text}'")
    print(f"f/g Ratio: {proof.f_demand:.2f}/{proof.g_ground:.2f} = {proof.fg_ratio:.2f}")
    print(f"Admissible: {proof.is_admissible}")
    print(f"Proof Hash: {proof.proof_hash}")

    print("\n--- Safety-Critical Regime ---")
    compiler = KinematicCompiler(CompilerRegime.SAFETY_CRITICAL)
    proof = compiler.compile("Initiate emergency dive procedure")
    print(f"Input: '{proof.input_text}'")
    print(f"f/g Ratio: {proof.f_demand:.2f}/{proof.g_ground:.2f} = {proof.fg_ratio:.2f}")
    print(f"Admissible: {proof.is_admissible}")
    if proof.structural_failures:
        print(f"Failures:")
        for failure in proof.structural_failures:
            print(f"  - {failure}")

    # MCAS example from specification
    print("\n--- MCAS Terminology Check (Section 5.1) ---")
    compiler = KinematicCompiler(CompilerRegime.SAFETY_CRITICAL)
    proof, warning = compiler.compile_and_verify_pair(
        "TRIM",
        "repeated nose-down commands at dive magnitude"
    )
    print(f"Action Word: TRIM")
    print(f"Target Description: '{proof.input_text}'")
    if warning:
        print(f"WARNING: {warning}")
    print(f"Target Admissible: {proof.is_admissible}")


def demo_hallucination_detection() -> None:
    """Demonstrate Hallucination Prevention (Section 6.3)."""
    print_header("HALLUCINATION DETECTION (Section 6.3)")

    test_phrases = [
        "Safe Risk",           # From specification - contradictory
        "Stable Foundation",   # Should be stable
        "Sudden Stillness",    # Contradictory terminals
        "Powerful Force",      # Congruent
        "Weak Strength",       # Contradictory
    ]

    for phrase in test_phrases:
        check = HallucinationDetector.check(phrase)
        status = "HALLUCINATION" if check.is_hallucination else "STABLE"
        print(f"\n'{phrase}': [{status}]")
        print(f"  Stability: {check.stability_score:.2f}")
        print(f"  Contradiction: {check.contradiction_detected}")
        print(f"  {check.explanation}")


def demo_v11_refinements() -> None:
    """Demonstrate v1.1 Validated Refinements."""
    print_header("v1.1 VALIDATED REFINEMENTS")

    print("\n--- Refinement 1: Consonant Dominance ---")
    print("Consonants carry ~2x semantic load of vowels")
    print("Formula: Word_Vector = (2 * Consonant_Force) + (1 * Vowel_Cohesion)")

    test_words = ["STRENGTH", "AURA", "RHYTHM"]
    for word in test_words:
        assembly = WordAssemblyAnalyzer.analyze(word)
        vec = assembly.vector
        print(f"\n  {word}:")
        print(f"    Consonant Force: {vec.consonant_force:.2f}")
        print(f"    Vowel Cohesion: {vec.vowel_cohesion:.2f}")
        print(f"    Weighted Vector: {vec.weighted_vector:.2f}")

    print("\n--- Refinement 2: Dictionary vs Geometric Antonyms ---")
    print("Cultural opposition != mechanical inversion")

    # TRUST/DOUBT example from refinement
    analysis = AntonymAnalyzer.analyze("TRUST", "DOUBT")
    print(f"\n  TRUST vs DOUBT:")
    print(f"    Dictionary Antonym: {analysis.is_dictionary_antonym}")
    print(f"    Geometric Antonym: {analysis.is_geometric_antonym}")
    print(f"    Type: {analysis.antonym_type.value}")
    print(f"    Note: DOUBT is contained uncertainty, not inverse trust")


def main():
    """Run all demonstrations."""
    print("=" * 70)
    print(" KINEMATIC LINGUISTICS v1.1")
    print(" A Geometric Substrate for Semantic Reliability")
    print(" PARCRI Real Intelligence - January 2026")
    print("=" * 70)

    demo_glyph_table()
    demo_blind_geometry_tests()
    demo_antonym_validation()
    demo_phonosemantic_clusters()
    demo_distortion_index()
    demo_compiler()
    demo_hallucination_detection()
    demo_v11_refinements()

    print("\n" + "=" * 70)
    print(" END OF DEMONSTRATION")
    print("=" * 70)
    print("\nCore Axiom: Language is a conserved geometric system.")
    print("We move from probabilistic AI to geometric AI.")


if __name__ == "__main__":
    main()
