#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
TEST: Newton Cinema Companion - Kinematic Edition
═══════════════════════════════════════════════════════════════════════════════

Tests for Newton's kinematic cinema companion system:
- f = interaction demand (linguistic instability + priority)
- g = narrative gravity (scene type + user receptivity)

When f/g >= 1.0 → finfr (ontological death of comment)

"The silence IS the instruction."
"""

import sys
import os

# Add parent directory to path for imports
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent_dir)
sys.path.insert(0, os.path.join(_parent_dir, 'src'))

import pytest
from newton.cinema import (
    # Matter types
    GlyphProperties,
    GlyphGeometry,
    StabilityClass,
    STABILITY_CLASSES,
    DAMPING_SUBSTITUTIONS,
    # Core types
    ForgeResult,
    KinematicProof,
    SpeechEvent,
    SceneType,
    # Engines
    KinematicLinguistics,
    KineticForge,
    KinematicCinemaCompanion,
)


# ═══════════════════════════════════════════════════════════════════════════════
# GLYPH GEOMETRY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestGlyphProperties:
    """Tests for GlyphProperties dataclass."""

    def test_glyph_properties_immutable(self):
        """GlyphProperties should be immutable (frozen)."""
        props = GlyphProperties(
            topology="Test",
            physical_property="Test",
            vector_type="Test",
            stability=0.5
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            props.stability = 0.9

    def test_glyph_properties_stability_bounds(self):
        """Stability must be in [0.0, 1.0]."""
        with pytest.raises(ValueError):
            GlyphProperties("T", "P", "V", stability=-0.1)
        with pytest.raises(ValueError):
            GlyphProperties("T", "P", "V", stability=1.5)


class TestGlyphGeometry:
    """Tests for GlyphGeometry class."""

    def test_all_letters_defined(self):
        """All 26 letters should be in the geometry map."""
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            props = GlyphGeometry.get(char)
            assert props is not None
            assert 0.0 <= props.stability <= 1.0

    def test_case_insensitive(self):
        """Glyph lookup should be case-insensitive."""
        assert GlyphGeometry.get('a').stability == GlyphGeometry.get('A').stability
        assert GlyphGeometry.get('z').stability == GlyphGeometry.get('Z').stability

    def test_high_stability_glyphs(self):
        """Known high-stability glyphs (A, O, X) should have stability >= 0.9."""
        for char in ['A', 'O', 'X']:
            assert GlyphGeometry.stability(char) >= 0.9

    def test_low_stability_glyphs(self):
        """Known low-stability glyphs (S, Z, I) should have stability <= 0.4."""
        for char in ['S', 'Z', 'I']:
            assert GlyphGeometry.stability(char) <= 0.4

    def test_stability_for_non_alphabetic(self):
        """Non-alphabetic characters should return neutral stability (0.5)."""
        assert GlyphGeometry.stability('1') == 0.5
        assert GlyphGeometry.stability('!') == 0.5
        assert GlyphGeometry.stability(' ') == 0.5

    def test_analyze_word_stability(self):
        """analyze_word should return average stability."""
        stability, vector = GlyphGeometry.analyze_word("AA")  # Both high
        assert stability >= 0.9

        stability, vector = GlyphGeometry.analyze_word("ZZ")  # Both low
        assert stability <= 0.4

    def test_analyze_word_vector_type(self):
        """analyze_word should return the dominant vector type."""
        _, vector = GlyphGeometry.analyze_word("AAA")
        assert vector == "Static equilibrium"

        _, vector = GlyphGeometry.analyze_word("SSS")
        assert vector == "Low friction coefficient"


class TestStabilityClasses:
    """Tests for stability classification."""

    def test_stability_classes_complete(self):
        """All letters should have a stability class."""
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            assert char in STABILITY_CLASSES

    def test_high_stability_classification(self):
        """High stability letters (>=0.7) should be classified HIGH."""
        for char in ['A', 'O', 'T', 'X', 'H', 'B', 'R']:
            assert STABILITY_CLASSES[char] == StabilityClass.HIGH

    def test_low_stability_classification(self):
        """Low stability letters (<0.5) should be classified LOW."""
        for char in ['S', 'Z', 'I', 'C', 'F', 'K', 'W']:
            assert STABILITY_CLASSES[char] == StabilityClass.LOW


# ═══════════════════════════════════════════════════════════════════════════════
# KINEMATIC LINGUISTICS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestKinematicLinguistics:
    """Tests for KinematicLinguistics engine."""

    def test_analyze_empty_string(self):
        """Empty string should have zero instability."""
        assert KinematicLinguistics.analyze_comment("") == 0.0
        assert KinematicLinguistics.analyze_comment("   ") == 0.0

    def test_stable_words_low_instability(self):
        """Words with stable glyphs should have low instability."""
        # "OATH" has O(0.9), A(0.9), T(0.85), H(0.85) = avg 0.875
        instability = KinematicLinguistics.analyze_comment("OATH")
        assert instability < 0.2  # 1.0 - 0.875 = 0.125

    def test_unstable_words_high_instability(self):
        """Words with unstable glyphs should have high instability."""
        # "SIZE" has S(0.3), I(0.3), Z(0.3), E(0.5) = avg 0.35
        instability = KinematicLinguistics.analyze_comment("SIZE")
        assert instability > 0.6  # 1.0 - 0.35 = 0.65

    def test_case_insensitive_analysis(self):
        """Analysis should be case-insensitive."""
        assert (
            KinematicLinguistics.analyze_comment("hello") ==
            KinematicLinguistics.analyze_comment("HELLO")
        )

    def test_find_unstable_words(self):
        """Should identify words with instability above threshold."""
        unstable = KinematicLinguistics.find_unstable_words(
            "STRESS is SIZE wise", threshold=0.5
        )
        # "STRESS" and "SIZE" have high instability
        assert "STRESS" in unstable or "SIZE" in unstable

    def test_analyze_detailed(self):
        """analyze_detailed should return comprehensive analysis."""
        analysis = KinematicLinguistics.analyze_detailed("Hello World")
        assert "text" in analysis
        assert "instability" in analysis
        assert "word_count" in analysis
        assert "words" in analysis
        assert analysis["word_count"] == 2


# ═══════════════════════════════════════════════════════════════════════════════
# SCENE TYPE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestSceneType:
    """Tests for SceneType enum."""

    def test_all_scene_types_have_gravity(self):
        """Every scene type should have a gravity value."""
        for scene_type in SceneType:
            assert 0.0 <= scene_type.gravity <= 1.0

    def test_credits_highest_gravity(self):
        """Credits should have highest gravity (most receptive)."""
        assert SceneType.CREDITS.gravity == 1.0

    def test_climax_lowest_gravity(self):
        """Climax should have lowest gravity (least receptive)."""
        assert SceneType.CLIMAX.gravity <= 0.15
        for scene_type in SceneType:
            assert scene_type.gravity >= SceneType.CLIMAX.gravity

    def test_gravity_ordering(self):
        """Gravity should decrease from credits to climax."""
        assert SceneType.CREDITS.gravity > SceneType.QUIET.gravity
        assert SceneType.QUIET.gravity > SceneType.ACTION.gravity
        assert SceneType.ACTION.gravity > SceneType.DIALOGUE.gravity
        assert SceneType.DIALOGUE.gravity > SceneType.CLIMAX.gravity


# ═══════════════════════════════════════════════════════════════════════════════
# FORGE RESULT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestForgeResult:
    """Tests for ForgeResult enum."""

    def test_can_speak_verified(self):
        """VERIFIED result should allow speaking."""
        assert ForgeResult.VERIFIED.can_speak is True

    def test_can_speak_warning(self):
        """WARNING result should allow speaking (with caution)."""
        assert ForgeResult.WARNING.can_speak is True

    def test_cannot_speak_forbidden(self):
        """FORBIDDEN result should not allow speaking."""
        assert ForgeResult.FORBIDDEN.can_speak is False

    def test_cannot_speak_impossible(self):
        """IMPOSSIBLE result should not allow speaking."""
        assert ForgeResult.IMPOSSIBLE.can_speak is False

    def test_symbols_defined(self):
        """All results should have visual symbols."""
        for result in ForgeResult:
            assert result.symbol is not None
            assert len(result.symbol) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# KINETIC FORGE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestKineticForge:
    """Tests for KineticForge verification engine."""

    def test_verify_returns_proof(self):
        """verify should return a KinematicProof."""
        forge = KineticForge()
        proof = forge.verify(
            intent="Hello",
            priority=0.5,
            scene_type=SceneType.QUIET,
            user_state={}
        )
        assert isinstance(proof, KinematicProof)

    def test_proof_has_all_fields(self):
        """KinematicProof should have all required fields."""
        forge = KineticForge()
        proof = forge.verify("Hello", 0.5, SceneType.QUIET, {})
        assert proof.f >= 0
        assert proof.g >= 0
        assert proof.ratio >= 0
        assert proof.result in ForgeResult
        assert proof.proof_hash is not None
        assert proof.timestamp > 0

    def test_high_gravity_allows_speaking(self):
        """High gravity (credits) should allow most comments."""
        forge = KineticForge()
        proof = forge.verify(
            intent="This was a great movie!",
            priority=0.8,
            scene_type=SceneType.CREDITS,
            user_state={}
        )
        assert proof.can_speak

    def test_low_gravity_forbids_speaking(self):
        """Low gravity (climax) should forbid most comments."""
        forge = KineticForge()
        proof = forge.verify(
            intent="This is boring",
            priority=0.5,
            scene_type=SceneType.CLIMAX,
            user_state={}
        )
        assert not proof.can_speak

    def test_user_shush_reduces_ground(self):
        """User silence streak should reduce ground (g)."""
        forge = KineticForge()

        # Without shush
        proof1 = forge.verify("Nice!", 0.5, SceneType.QUIET, {"silence_streak": 0})

        # With shush streak
        proof2 = forge.verify("Nice!", 0.5, SceneType.QUIET, {"silence_streak": 3})

        assert proof2.g < proof1.g
        assert proof2.ratio > proof1.ratio

    def test_proof_hash_unique(self):
        """Each verification should produce a unique proof hash."""
        forge = KineticForge()
        proof1 = forge.verify("Hello", 0.5, SceneType.QUIET, {})
        proof2 = forge.verify("Hello", 0.5, SceneType.QUIET, {})
        assert proof1.proof_hash != proof2.proof_hash

    def test_verify_batch(self):
        """verify_batch should return proofs for all intents."""
        forge = KineticForge()
        intents = [
            ("Hello", 0.5),
            ("Great!", 0.8),
            ("Boring", 0.3),
        ]
        proofs = forge.verify_batch(intents, SceneType.QUIET, {})
        assert len(proofs) == 3
        assert all(isinstance(p, KinematicProof) for p in proofs)


# ═══════════════════════════════════════════════════════════════════════════════
# KINEMATIC CINEMA COMPANION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestKinematicCinemaCompanion:
    """Tests for KinematicCinemaCompanion."""

    def test_evaluate_intent_returns_tuple(self):
        """evaluate_intent should return (spoken, proof) tuple."""
        companion = KinematicCinemaCompanion(verbose=False)
        result = companion.evaluate_intent("Hello", 0.5, SceneType.QUIET)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], KinematicProof)

    def test_speaks_during_credits(self):
        """Should speak most comments during credits."""
        companion = KinematicCinemaCompanion(verbose=False)
        spoken, proof = companion.evaluate_intent(
            "That was amazing!", 0.8, SceneType.CREDITS
        )
        assert spoken is True

    def test_silent_during_climax(self):
        """Should enforce silence during climax."""
        companion = KinematicCinemaCompanion(verbose=False)
        spoken, proof = companion.evaluate_intent(
            "Look at that!", 0.5, SceneType.CLIMAX
        )
        assert spoken is False

    def test_accepts_string_scene_type(self):
        """Should accept string scene type names."""
        companion = KinematicCinemaCompanion(verbose=False)
        spoken, proof = companion.evaluate_intent(
            "Hello", 0.5, "credits"
        )
        assert spoken is True

    def test_record_user_shush(self):
        """record_user_shush should increase silence streak."""
        companion = KinematicCinemaCompanion(verbose=False)
        assert companion.silence_streak == 0
        companion.record_user_shush()
        assert companion.silence_streak == 1
        companion.record_user_shush()
        assert companion.silence_streak == 2

    def test_shush_affects_verification(self):
        """Multiple shushes should make verification stricter."""
        companion = KinematicCinemaCompanion(verbose=False)

        # First evaluation
        spoken1, proof1 = companion.evaluate_intent(
            "Nice scene", 0.5, SceneType.ACTION
        )

        # Shush twice
        companion.record_user_shush()
        companion.record_user_shush()

        # Same evaluation should have higher ratio
        spoken2, proof2 = companion.evaluate_intent(
            "Nice scene", 0.5, SceneType.ACTION
        )

        assert proof2.ratio > proof1.ratio

    def test_record_user_engagement(self):
        """record_user_engagement should decrease silence streak."""
        companion = KinematicCinemaCompanion(verbose=False)
        companion.silence_streak = 3
        companion.record_user_engagement()
        assert companion.silence_streak == 2

    def test_engagement_doesnt_go_negative(self):
        """Silence streak should not go below 0."""
        companion = KinematicCinemaCompanion(verbose=False)
        assert companion.silence_streak == 0
        companion.record_user_engagement()
        assert companion.silence_streak == 0

    def test_set_mood(self):
        """set_mood should update mood modifier."""
        companion = KinematicCinemaCompanion(verbose=False)
        companion.set_mood(1.5)
        assert companion.mood_modifier == 1.5

    def test_mood_clamped(self):
        """Mood should be clamped to [0.0, 2.0]."""
        companion = KinematicCinemaCompanion(verbose=False)
        companion.set_mood(5.0)
        assert companion.mood_modifier == 2.0
        companion.set_mood(-1.0)
        assert companion.mood_modifier == 0.0

    def test_add_damping_rule(self):
        """Should be able to add custom damping rules."""
        companion = KinematicCinemaCompanion(verbose=False)
        companion.add_damping_rule("BANANA", "APPLE")
        assert "BANANA" in companion.damping_map
        assert companion.damping_map["BANANA"] == "APPLE"

    def test_speech_history_recorded(self):
        """Should record speech events to history."""
        companion = KinematicCinemaCompanion(verbose=False)
        assert len(companion.speech_history) == 0

        companion.evaluate_intent("Hello", 0.5, SceneType.CREDITS)
        assert len(companion.speech_history) == 1

        companion.evaluate_intent("Boring", 0.5, SceneType.CLIMAX)
        assert len(companion.speech_history) == 2

    def test_get_statistics(self):
        """get_statistics should return comprehensive stats."""
        companion = KinematicCinemaCompanion(verbose=False)
        companion.evaluate_intent("Hello", 0.5, SceneType.CREDITS)
        companion.evaluate_intent("Boring", 0.5, SceneType.CLIMAX)

        stats = companion.get_statistics()
        assert stats["total_intents"] == 2
        assert stats["spoken"] + stats["silenced"] == 2
        assert "silence_rate" in stats
        assert "damping_rate" in stats


class TestDamping:
    """Tests for kinematic damping functionality."""

    def test_damping_substitutions_exist(self):
        """Should have predefined damping substitutions."""
        assert len(DAMPING_SUBSTITUTIONS) > 0
        assert "INCREDIBLE" in DAMPING_SUBSTITUTIONS
        assert "STRESSFUL" in DAMPING_SUBSTITUTIONS

    def test_damping_reduces_instability(self):
        """Damped words should have lower instability."""
        for unstable, stable in DAMPING_SUBSTITUTIONS.items():
            unstable_instability = KinematicLinguistics.analyze_comment(unstable)
            stable_instability = KinematicLinguistics.analyze_comment(stable)
            # Stable replacement should have lower or equal instability
            assert stable_instability <= unstable_instability + 0.2  # Allow small margin

    def test_damping_preserves_case(self):
        """Damping should preserve case patterns."""
        companion = KinematicCinemaCompanion(verbose=False)

        # Lowercase
        result = companion._dampen_linguistics("incredible")
        assert result.islower() or result[0].isupper()

        # Uppercase
        result = companion._dampen_linguistics("INCREDIBLE")
        assert result.isupper()

        # Title case
        result = companion._dampen_linguistics("Incredible")
        assert result[0].isupper()


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """Integration tests for the complete cinema system."""

    def test_full_movie_session(self):
        """Simulate a full movie watching session."""
        companion = KinematicCinemaCompanion(verbose=False)

        # Opening credits - chatty
        spoken, _ = companion.evaluate_intent(
            "I heard this won an Oscar", 0.6, SceneType.CREDITS
        )
        assert spoken

        # Quiet scene - still allowed
        spoken, _ = companion.evaluate_intent(
            "Nice cinematography", 0.5, SceneType.QUIET
        )
        assert spoken

        # Dialogue - harder to interrupt
        spoken, _ = companion.evaluate_intent(
            "What did she say?", 0.3, SceneType.DIALOGUE
        )
        # Might be allowed or not depending on exact calculation

        # Climax - should be silenced
        spoken, _ = companion.evaluate_intent(
            "Wow this is intense!", 0.5, SceneType.CLIMAX
        )
        assert not spoken

        # End credits - back to chatty
        spoken, _ = companion.evaluate_intent(
            "That was a great film!", 0.8, SceneType.CREDITS
        )
        assert spoken

    def test_social_training(self):
        """Test that companion learns from user feedback."""
        companion = KinematicCinemaCompanion(verbose=False)

        # Start with normal behavior
        _, proof1 = companion.evaluate_intent(
            "Nice", 0.5, SceneType.ACTION
        )

        # User shushes multiple times
        for _ in range(4):
            companion.record_user_shush()

        # Same comment should now be harder to pass
        _, proof2 = companion.evaluate_intent(
            "Nice", 0.5, SceneType.ACTION
        )

        assert proof2.ratio > proof1.ratio
        # After enough shushes, even simple comments may be blocked
        assert companion.silence_streak == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
