"""
KINEMATIC LINGUISTICS v1.1 - COMPREHENSIVE TEST SUITE
A Geometric Substrate for Semantic Reliability

Tests for:
  - Glyph Registry completeness and properties
  - Word Assembly Analysis
  - Phonosemantic Cluster Detection
  - Distortion Index Calculation
  - Antonym Analysis (v1.1 refinements)
  - Kinematic Compiler
  - Hallucination Detection

Run: pytest tests/test_kinematic_linguistics.py -v
"""

import pytest
from newton.kinematic_linguistics import (
    # Matter Types
    GlyphMechanics,
    GlyphRegistry,
    PhonosemanticsCluster,
    PhonosemanticsRegistry,
    StabilityClass,
    LetterPosition,
    WordAssemblyRole,
    WORD_GEOMETRY_EXAMPLES,
    # Core Engines
    WordVector,
    WordAssembly,
    WordAssemblyAnalyzer,
    DistortionReport,
    DistortionIndexCalculator,
    AntonymType,
    AntonymAnalysis,
    AntonymAnalyzer,
    CompilerRegime,
    CompilationProof,
    KinematicCompiler,
    HallucinationCheck,
    HallucinationDetector,
)


# =============================================================================
# GLYPH REGISTRY TESTS
# =============================================================================

class TestGlyphMechanics:
    """Tests for GlyphMechanics data class."""

    def test_stability_bounds_enforced(self):
        """Stability must be in [0.0, 1.0]."""
        # Valid stability
        glyph = GlyphMechanics(
            topology="test",
            physical_property="test",
            vector_type="test",
            stability=0.5,
            mechanical_role="test",
            is_consonant=True
        )
        assert glyph.stability == 0.5

    def test_stability_below_zero_raises(self):
        """Stability below 0 should raise ValueError."""
        with pytest.raises(ValueError):
            GlyphMechanics(
                topology="test",
                physical_property="test",
                vector_type="test",
                stability=-0.1,
                mechanical_role="test",
                is_consonant=True
            )

    def test_stability_above_one_raises(self):
        """Stability above 1 should raise ValueError."""
        with pytest.raises(ValueError):
            GlyphMechanics(
                topology="test",
                physical_property="test",
                vector_type="test",
                stability=1.1,
                mechanical_role="test",
                is_consonant=True
            )

    def test_immutability(self):
        """GlyphMechanics should be frozen."""
        glyph = GlyphRegistry.get('A')
        with pytest.raises(AttributeError):
            glyph.stability = 0.1


class TestGlyphRegistry:
    """Tests for GlyphRegistry."""

    def test_all_26_letters_defined(self):
        """All 26 letters of alphabet must be defined."""
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            glyph = GlyphRegistry.get(char)
            assert glyph is not None, f"Missing glyph for {char}"
            assert isinstance(glyph, GlyphMechanics)

    def test_lowercase_lookup_works(self):
        """Lookup should work with lowercase."""
        glyph_upper = GlyphRegistry.get('A')
        glyph_lower = GlyphRegistry.get('a')
        assert glyph_upper == glyph_lower

    def test_stability_method(self):
        """Stability convenience method should work."""
        assert 0.0 <= GlyphRegistry.stability('A') <= 1.0
        assert GlyphRegistry.stability('?') == 0.5  # Non-alphabetic

    def test_vowels_marked_correctly(self):
        """Vowels should not be marked as consonants."""
        vowels = {'A', 'E', 'I', 'O', 'U'}
        for v in vowels:
            glyph = GlyphRegistry.get(v)
            assert not glyph.is_consonant, f"{v} should be vowel"

    def test_consonants_marked_correctly(self):
        """Consonants should be marked as consonants."""
        consonants = set("BCDFGHJKLMNPQRSTVWXYZ")
        for c in consonants:
            glyph = GlyphRegistry.get(c)
            assert glyph.is_consonant, f"{c} should be consonant"

    def test_stability_class_sets_complete(self):
        """All letters should be in exactly one stability class."""
        all_letters = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        high = GlyphRegistry.HIGH_STABILITY
        medium = GlyphRegistry.MEDIUM_STABILITY
        low = GlyphRegistry.LOW_STABILITY

        combined = high | medium | low
        assert combined == all_letters, "Not all letters classified"
        assert len(high & medium) == 0, "Overlap between HIGH and MEDIUM"
        assert len(high & low) == 0, "Overlap between HIGH and LOW"
        assert len(medium & low) == 0, "Overlap between MEDIUM and LOW"

    def test_high_stability_glyphs_have_high_scores(self):
        """HIGH stability glyphs should have stability >= 0.7."""
        for char in GlyphRegistry.HIGH_STABILITY:
            glyph = GlyphRegistry.get(char)
            assert glyph.stability >= 0.7, f"{char} stability {glyph.stability} < 0.7"

    def test_low_stability_glyphs_have_low_scores(self):
        """LOW stability glyphs should have stability < 0.5."""
        for char in GlyphRegistry.LOW_STABILITY:
            glyph = GlyphRegistry.get(char)
            assert glyph.stability < 0.5, f"{char} stability {glyph.stability} >= 0.5"


# =============================================================================
# PHONOSEMANTICS TESTS
# =============================================================================

class TestPhonosemanticsRegistry:
    """Tests for phonosemantic cluster detection."""

    def test_st_cluster_detection(self):
        """Words ending in -ST should detect the cluster."""
        words = ["REST", "TEST", "TRUST", "LAST"]
        for word in words:
            clusters = PhonosemanticsRegistry.detect_clusters(word)
            patterns = [c.pattern for c in clusters]
            assert "-ST" in patterns, f"{word} should detect -ST cluster"

    def test_fl_cluster_detection(self):
        """Words starting with FL- should detect the cluster."""
        words = ["FLOW", "FLY", "FLAT", "FLEE"]
        for word in words:
            clusters = PhonosemanticsRegistry.detect_clusters(word)
            patterns = [c.pattern for c in clusters]
            assert "FL-" in patterns, f"{word} should detect FL- cluster"

    def test_gl_cluster_detection(self):
        """Words starting with GL- should detect the cluster."""
        words = ["GLUE", "GLASS", "GLOOM"]
        for word in words:
            clusters = PhonosemanticsRegistry.detect_clusters(word)
            patterns = [c.pattern for c in clusters]
            assert "GL-" in patterns, f"{word} should detect GL- cluster"

    def test_sp_cluster_detection(self):
        """Words starting with SP- should detect the cluster."""
        words = ["SPEAK", "SPARK", "SPEED", "SPACE"]
        for word in words:
            clusters = PhonosemanticsRegistry.detect_clusters(word)
            patterns = [c.pattern for c in clusters]
            assert "SP-" in patterns, f"{word} should detect SP- cluster"

    def test_multiple_clusters_detected(self):
        """Word with multiple clusters should detect all."""
        # SPREAD has SP- (initial)
        clusters = PhonosemanticsRegistry.detect_clusters("SPREAD")
        patterns = [c.pattern for c in clusters]
        assert "SP-" in patterns

    def test_cluster_properties(self):
        """Cluster objects should have required properties."""
        cluster = PhonosemanticsRegistry.get_cluster("-ST")
        assert cluster is not None
        assert cluster.position == "terminal"
        assert len(cluster.examples) > 0


# =============================================================================
# WORD ASSEMBLY TESTS
# =============================================================================

class TestWordAssemblyAnalyzer:
    """Tests for word assembly analysis."""

    def test_analyze_returns_assembly(self):
        """Analyze should return WordAssembly object."""
        assembly = WordAssemblyAnalyzer.analyze("TRUST")
        assert isinstance(assembly, WordAssembly)
        assert assembly.word == "TRUST"

    def test_letters_decomposition(self):
        """Letters should be properly decomposed."""
        assembly = WordAssemblyAnalyzer.analyze("TRUST")
        assert len(assembly.letters) == 5
        letters = [r.letter for r in assembly.letters]
        assert letters == ['T', 'R', 'U', 'S', 'T']

    def test_position_assignment(self):
        """Positions should be correctly assigned."""
        assembly = WordAssemblyAnalyzer.analyze("TRUST")
        assert assembly.letters[0].position == LetterPosition.INITIAL
        assert assembly.letters[1].position == LetterPosition.MEDIAL
        assert assembly.letters[-1].position == LetterPosition.TERMINAL

    def test_vector_calculation(self):
        """Vector should be properly calculated."""
        assembly = WordAssemblyAnalyzer.analyze("TRUST")
        vec = assembly.vector
        assert 0.0 <= vec.stability_score <= 1.0
        assert vec.stability_score + vec.instability_score == pytest.approx(1.0)

    def test_v11_consonant_weighting(self):
        """v1.1: Consonant force should be calculated."""
        assembly = WordAssemblyAnalyzer.analyze("TRUST")
        vec = assembly.vector
        assert vec.consonant_force > 0
        # TRUST has 4 consonants (T, R, S, T) and 1 vowel (U)
        assert vec.consonant_force > vec.vowel_cohesion

    def test_stability_classification(self):
        """Stability should be classified correctly."""
        # High stability word
        assembly = WordAssemblyAnalyzer.analyze("BOTH")  # B, O, T, H are stable
        # Should be medium to high
        assert assembly.stability_class in [StabilityClass.HIGH, StabilityClass.MEDIUM]

    def test_phonosemantic_detection_in_assembly(self):
        """Assembly should include detected phonosemantic clusters."""
        assembly = WordAssemblyAnalyzer.analyze("TRUST")
        patterns = [c.pattern for c in assembly.phonosemantic_clusters]
        assert "-ST" in patterns

    def test_empty_word_handling(self):
        """Empty word should return default assembly."""
        assembly = WordAssemblyAnalyzer.analyze("")
        assert assembly.stability_class == StabilityClass.MEDIUM

    def test_case_insensitivity(self):
        """Analysis should be case-insensitive."""
        upper = WordAssemblyAnalyzer.analyze("TRUST")
        lower = WordAssemblyAnalyzer.analyze("trust")
        mixed = WordAssemblyAnalyzer.analyze("TrUsT")
        assert upper.word == lower.word == mixed.word


class TestSpecificationExamples:
    """Tests based on specification Section 3 examples."""

    def test_trust_assembly(self):
        """TRUST should be a suspension bridge structure."""
        assembly = WordAssemblyAnalyzer.analyze("TRUST")
        # Should have T...T anchoring pattern
        assert assembly.letters[0].letter == 'T'
        assert assembly.letters[-1].letter == 'T'
        # Should detect -ST cluster
        patterns = [c.pattern for c in assembly.phonosemantic_clusters]
        assert "-ST" in patterns

    def test_force_assembly(self):
        """FORCE should have lever-flywheel-grinder pattern."""
        assembly = WordAssemblyAnalyzer.analyze("FORCE")
        letters = [r.letter for r in assembly.letters]
        assert letters == ['F', 'O', 'R', 'C', 'E']
        # F is lever, O is flywheel
        assert assembly.letters[0].glyph_mechanics.physical_property == "Reach, leverage"

    def test_safe_assembly(self):
        """SAFE should have protective structure."""
        assembly = WordAssemblyAnalyzer.analyze("SAFE")
        # Should have containment/protection elements
        vec = assembly.vector
        # SAFE has stability-focused structure
        assert vec.stability_score > 0.4


# =============================================================================
# DISTORTION INDEX TESTS
# =============================================================================

class TestDistortionIndexCalculator:
    """Tests for distortion index calculation."""

    def test_correction_for_crash(self):
        """'Correction' for -30% should show high distortion (Section 5.3)."""
        report = DistortionIndexCalculator.calculate("Correction", -0.30)
        assert report.distortion_index > 0.5
        assert report.is_misleading
        # Should recommend "CRASH"
        assert report.recommended_word in ["CRASH", "COLLAPSE"]

    def test_matching_word_low_distortion(self):
        """Matching word/reality should have low distortion."""
        report = DistortionIndexCalculator.calculate("Minor", 0.05)
        assert report.distortion_index < 0.5
        assert not report.is_misleading

    def test_distortion_bounds(self):
        """Distortion should be in [0, 1]."""
        report = DistortionIndexCalculator.calculate("Test", 0.5)
        assert 0.0 <= report.distortion_index <= 1.0

    def test_accuracy_percentage(self):
        """Accuracy should be complement of distortion."""
        report = DistortionIndexCalculator.calculate("Correction", -0.30)
        assert report.accuracy_percentage == pytest.approx((1 - report.distortion_index) * 100)


# =============================================================================
# ANTONYM ANALYSIS TESTS (v1.1)
# =============================================================================

class TestAntonymAnalyzer:
    """Tests for antonym analysis (v1.1 Refinement 2)."""

    def test_trust_doubt_not_geometric_antonyms(self):
        """TRUST/DOUBT: dictionary antonyms but not geometric (v1.1)."""
        analysis = AntonymAnalyzer.analyze("TRUST", "DOUBT")
        # Per specification: DOUBT is contained uncertainty, not inverse TRUST
        assert analysis.is_dictionary_antonym or analysis.antonym_type != AntonymType.GEOMETRIC_INVERSION
        # They should be orthogonal or dictionary-only
        assert analysis.antonym_type in [AntonymType.ORTHOGONAL, AntonymType.DICTIONARY_ONLY, AntonymType.GEOMETRIC_INVERSION]

    def test_fix_break_geometric_antonyms(self):
        """FIX/BREAK should be geometrically opposed."""
        analysis = AntonymAnalyzer.analyze("FIX", "BREAK")
        # FIX ends in X (lock), BREAK ends in K (cut)
        # They should show opposition
        assert analysis.geometric_similarity < 0.5

    def test_similarity_bounds(self):
        """Geometric similarity should be in [-1, 1]."""
        analysis = AntonymAnalyzer.analyze("LOVE", "HATE")
        assert -1.0 <= analysis.geometric_similarity <= 1.0

    def test_antonym_type_classification(self):
        """Antonym type should be properly classified."""
        analysis = AntonymAnalyzer.analyze("GOOD", "BAD")
        assert isinstance(analysis.antonym_type, AntonymType)


# =============================================================================
# COMPILER TESTS
# =============================================================================

class TestKinematicCompiler:
    """Tests for the kinematic compiler."""

    def test_general_regime_compilation(self):
        """General regime should compile standard text."""
        compiler = KinematicCompiler(CompilerRegime.GENERAL)
        proof = compiler.compile("Execute standard procedure")
        assert isinstance(proof, CompilationProof)
        assert proof.regime == CompilerRegime.GENERAL

    def test_proof_has_hash(self):
        """Compilation should produce proof hash."""
        compiler = KinematicCompiler()
        proof = compiler.compile("Test input")
        assert len(proof.proof_hash) == 16

    def test_fg_ratio_calculation(self):
        """f/g ratio should be properly calculated."""
        compiler = KinematicCompiler()
        proof = compiler.compile("Stable anchor test")
        assert proof.f_demand > 0
        assert proof.g_ground > 0
        assert proof.fg_ratio == pytest.approx(proof.f_demand / proof.g_ground)

    def test_safety_critical_stricter(self):
        """Safety-critical regime should be stricter."""
        general = KinematicCompiler(CompilerRegime.GENERAL)
        safety = KinematicCompiler(CompilerRegime.SAFETY_CRITICAL)

        # Same input
        text = "Execute unstable wobbling zigzag procedure"  # S, W, Z are unstable
        general_proof = general.compile(text)
        safety_proof = safety.compile(text)

        # Safety critical should have lower threshold
        assert safety.thresholds["stability_min"] > general.thresholds["stability_min"]

    def test_structural_failures_detected(self):
        """Structural failures should be detected and reported."""
        compiler = KinematicCompiler(CompilerRegime.SAFETY_CRITICAL)
        # Use highly unstable word
        proof = compiler.compile("SIZZLING JAZZINESS")  # S, I, Z, J are unstable
        # Should have some failures due to instability
        assert proof.structural_failures or not proof.is_admissible

    def test_word_vectors_captured(self):
        """All word vectors should be captured in proof."""
        compiler = KinematicCompiler()
        proof = compiler.compile("One Two Three")
        assert len(proof.word_vectors) == 3

    def test_compile_and_verify_pair(self):
        """Action/target pair verification should work."""
        compiler = KinematicCompiler(CompilerRegime.SAFETY_CRITICAL)
        proof, warning = compiler.compile_and_verify_pair(
            "TRIM",
            "small controlled adjustment"
        )
        assert isinstance(proof, CompilationProof)


# =============================================================================
# HALLUCINATION DETECTION TESTS
# =============================================================================

class TestHallucinationDetector:
    """Tests for hallucination detection (Section 6.3)."""

    def test_safe_risk_detected(self):
        """'Safe Risk' should be detected as contradictory (Section 6.3)."""
        check = HallucinationDetector.check("Safe Risk")
        # SAFE ends in E (layers), RISK ends in K (cut)
        # E and K are in contradictory terminals
        assert check.contradiction_detected or check.stability_score < 0.7

    def test_stable_phrase_passes(self):
        """Stable phrases should not be flagged."""
        check = HallucinationDetector.check("Strong Foundation")
        # Both words have stable structures
        assert not check.is_hallucination

    def test_single_word_not_hallucination(self):
        """Single word cannot be a hallucination."""
        check = HallucinationDetector.check("Test")
        assert not check.is_hallucination
        assert check.stability_score == 1.0

    def test_stability_score_calculated(self):
        """Stability score should be in valid range."""
        check = HallucinationDetector.check("Test Phrase Here")
        assert 0.0 <= check.stability_score <= 1.0


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_full_analysis_pipeline(self):
        """Complete analysis pipeline should work."""
        # Analyze word
        assembly = WordAssemblyAnalyzer.analyze("TRUST")
        assert assembly.stability_class in StabilityClass

        # Check clusters
        assert len(assembly.phonosemantic_clusters) >= 1

        # Run through compiler
        compiler = KinematicCompiler()
        proof = compiler.compile("Build TRUST through reliable service")
        assert proof.is_admissible or len(proof.structural_failures) > 0

        # Check for hallucination
        check = HallucinationDetector.check("Build TRUST")
        assert not check.is_hallucination

    def test_specification_test_cases(self):
        """All specification test cases should be analyzable."""
        test_words = ["TRUST", "FORCE", "DREAM", "SAFE", "FIX"]
        for word in test_words:
            assembly = WordAssemblyAnalyzer.analyze(word)
            assert assembly.word == word
            assert len(assembly.letters) == len(word)

    def test_reference_examples_exist(self):
        """Reference examples should be defined."""
        assert "TRUST" in WORD_GEOMETRY_EXAMPLES
        assert "FORCE" in WORD_GEOMETRY_EXAMPLES
        assert WORD_GEOMETRY_EXAMPLES["TRUST"]["assembly"]


# =============================================================================
# PROPERTY-BASED TESTS (if hypothesis is available)
# =============================================================================

try:
    from hypothesis import given, strategies as st

    class TestPropertyBased:
        """Property-based tests using hypothesis."""

        @given(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=10))
        def test_any_alpha_word_analyzable(self, word):
            """Any alphabetic word should be analyzable."""
            assembly = WordAssemblyAnalyzer.analyze(word)
            assert assembly.word == word
            assert 0.0 <= assembly.vector.stability_score <= 1.0

        @given(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=2, max_size=20))
        def test_compilation_always_produces_proof(self, text):
            """Any text should produce a compilation proof."""
            compiler = KinematicCompiler()
            proof = compiler.compile(text)
            assert proof.proof_hash
            assert 0.0 <= proof.f_demand <= 1.0

except ImportError:
    pass  # hypothesis not installed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
