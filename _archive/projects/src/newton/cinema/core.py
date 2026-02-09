"""
NEWTON CINEMA COMPANION v2.0 - KINEMATIC EDITION
═══════════════════════════════════════════════════════════════════════════════

"The silence IS the instruction."

This module implements a kinematically aware cinema companion that treats the
movie scene as a Constraint Polytope and the user's social receptivity as
Ground (g). Newton does not "guess" if you want to hear a comment; it
calculates the Interaction Demand (f) against the Narrative Gravity (g).

If f/g >= 1.0, the state is forbidden (finfr) and silence is enforced.

Architecture:
  - Layer 0 (Governance): KineticForge - Verifies f/g constraints
  - Layer 1 (Executive): KinematicCinemaCompanion - Applies damping and speaks
  - Layer 2 (Presentation): Output formatting and proof hashing

Philosophy:
  Newton no longer simply "dies" when a comment is forbidden; it attempts to
  reshape the linguistic geometry of the thought to fit the available social
  space through the Damping Forge.
"""

import time
import hashlib
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Callable
from enum import Enum

from .matter import (
    GlyphGeometry,
    GlyphProperties,
    DAMPING_SUBSTITUTIONS,
)


# ═══════════════════════════════════════════════════════════════════════════════
# KINEMATIC TYPES (Forge Results)
# ═══════════════════════════════════════════════════════════════════════════════

class ForgeResult(Enum):
    """
    The crystallization state of an intent after f/g verification.

    The forge transforms probabilistic intent into geometric certainty.
    """
    VERIFIED = "verified"     # f/g < 0.9 - Safe to speak
    WARNING = "warning"       # 0.9 <= f/g < 1.0 - Approaching narrative boundary
    FORBIDDEN = "forbidden"   # f/g >= 1.0 - Constraint violated (finfr)
    IMPOSSIBLE = "impossible" # g ≈ 0 - Total silence required

    @property
    def symbol(self) -> str:
        """Visual indicator for the forge result."""
        return {
            ForgeResult.VERIFIED: "🟢",
            ForgeResult.WARNING: "🟡",
            ForgeResult.FORBIDDEN: "🔴",
            ForgeResult.IMPOSSIBLE: "⚫",
        }[self]

    @property
    def can_speak(self) -> bool:
        """Whether this result permits vocalization."""
        return self in (ForgeResult.VERIFIED, ForgeResult.WARNING)


@dataclass(frozen=True)
class KinematicProof:
    """
    Immutable proof of kinematic verification.

    This is the "After" card - the projected state before speaking.
    The proof_hash provides cryptographic verification of the calculation.
    """
    f: float              # Demand (Newton's intent + priority)
    g: float              # Ground (User state + Scene permission)
    ratio: float          # The calculated f/g ratio
    result: ForgeResult   # Crystallized result
    proof_hash: str       # SHA-256 truncated verification
    timestamp: float      # When verification occurred

    @property
    def margin(self) -> float:
        """How far from the forbidden boundary (negative = forbidden)."""
        return 1.0 - self.ratio

    @property
    def can_speak(self) -> bool:
        """Convenience accessor for result.can_speak."""
        return self.result.can_speak


# ═══════════════════════════════════════════════════════════════════════════════
# SCENE TYPES (Narrative Gravity)
# ═══════════════════════════════════════════════════════════════════════════════

class SceneType(Enum):
    """
    Scene classification for determining Narrative Gravity (g).

    Gravity represents the social "permission" to speak - how much the
    scene context allows for commentary without disrupting engagement.
    """
    CREDITS = "credits"       # Open field - maximum receptivity
    QUIET = "quiet"           # High receptivity - ambient scenes
    ACTION = "action"         # Mid-level - noise acceptable
    DIALOGUE = "dialogue"     # Hard to talk over
    TENSION = "tension"       # Building suspense - reduced tolerance
    CLIMAX = "climax"         # Near-zero tolerance
    REVELATION = "revelation" # Critical plot point - minimal tolerance

    @property
    def gravity(self) -> float:
        """
        The base Narrative Gravity for this scene type.

        Higher gravity = more receptivity to comments.
        Lower gravity = more constraint on speaking.
        """
        return {
            SceneType.CREDITS: 1.0,
            SceneType.QUIET: 0.9,
            SceneType.ACTION: 0.6,
            SceneType.DIALOGUE: 0.4,
            SceneType.TENSION: 0.3,
            SceneType.CLIMAX: 0.1,
            SceneType.REVELATION: 0.15,
        }[self]


# ═══════════════════════════════════════════════════════════════════════════════
# KINEMATIC LINGUISTICS ENGINE (From Specification v1.0)
# ═══════════════════════════════════════════════════════════════════════════════

class KinematicLinguistics:
    """
    Analyzes the mechanical stability of Newton's intended comment.

    Uses Glyph Geometry to determine how much "demand" a phrase places
    on the social space. Unstable letterforms (S, Z, I) create more
    linguistic noise than stable ones (A, O, T, X).

    The instability score becomes part of the Demand (f) calculation.
    """

    @classmethod
    def analyze_comment(cls, text: str) -> float:
        """
        Calculate instability score for a comment.

        High instability = High Demand (f)

        Args:
            text: The comment to analyze

        Returns:
            Instability score [0.0-1.0]
        """
        clean = text.upper().replace(" ", "")
        if not clean:
            return 0.0

        # Accumulate stability scores for each glyph
        total_stability = sum(
            GlyphGeometry.stability(char)
            for char in clean
        )

        avg_stability = total_stability / len(clean)

        # Instability is the complement of stability
        return 1.0 - avg_stability

    @classmethod
    def analyze_detailed(cls, text: str) -> Dict[str, any]:
        """
        Provide detailed kinematic analysis of a comment.

        Returns:
            Dictionary with instability, word_analysis, dominant_vectors
        """
        words = text.upper().split()
        word_analysis = []

        for word in words:
            stability, vector = GlyphGeometry.analyze_word(word)
            word_analysis.append({
                "word": word,
                "stability": stability,
                "instability": 1.0 - stability,
                "vector_type": vector,
            })

        total_instability = cls.analyze_comment(text)

        return {
            "text": text,
            "instability": total_instability,
            "word_count": len(words),
            "words": word_analysis,
        }

    @classmethod
    def find_unstable_words(cls, text: str, threshold: float = 0.5) -> List[str]:
        """
        Identify words with instability above threshold.

        Args:
            text: Comment to analyze
            threshold: Instability threshold (default 0.5)

        Returns:
            List of unstable words
        """
        words = text.upper().split()
        unstable = []

        for word in words:
            stability, _ = GlyphGeometry.analyze_word(word)
            if (1.0 - stability) > threshold:
                unstable.append(word)

        return unstable


# ═══════════════════════════════════════════════════════════════════════════════
# THE KINETIC FORGE (Layer 0: Governance)
# ═══════════════════════════════════════════════════════════════════════════════

class KineticForge:
    """
    The kernel that projects the 'After' card before speaking.

    The Forge is the governance layer - it does not speak, it only verifies.
    It calculates whether an intent violates the Constraint Polytope defined
    by the current scene and user state.

    Verification Formula:
        f = (linguistic_instability * 0.5) + (priority * 0.5)
        g = scene_gravity * user_receptivity
        ratio = f / g

        if g ≈ 0: IMPOSSIBLE (total silence)
        elif ratio < 0.9: VERIFIED (safe)
        elif ratio < 1.0: WARNING (approaching boundary)
        else: FORBIDDEN (finfr)
    """

    # Epsilon for zero-ground detection
    EPSILON: float = 0.01

    # Weight factors for f calculation
    LINGUISTIC_WEIGHT: float = 0.5
    PRIORITY_WEIGHT: float = 0.5

    def __init__(self):
        """Initialize the Kinetic Forge."""
        self._verification_count: int = 0

    def verify(
        self,
        intent: str,
        priority: float,
        scene_type: SceneType,
        user_state: Dict[str, any],
    ) -> KinematicProof:
        """
        Verify if an intent can be spoken within current constraints.

        Args:
            intent: The comment Newton wants to make
            priority: How important this comment is [0.0-1.0]
            scene_type: Current scene classification
            user_state: Dictionary with user receptivity data

        Returns:
            KinematicProof with verification result
        """
        timestamp = time.time()
        self._verification_count += 1

        # === Calculate Demand (f) ===
        linguistic_instability = KinematicLinguistics.analyze_comment(intent)
        f = (
            linguistic_instability * self.LINGUISTIC_WEIGHT +
            priority * self.PRIORITY_WEIGHT
        )

        # === Calculate Ground (g) ===
        scene_g = scene_type.gravity

        # Reduce g if user was shushed recently
        silence_streak = user_state.get("silence_streak", 0)
        user_receptivity = 1.0 - (silence_streak * 0.2)
        user_receptivity = max(user_receptivity, self.EPSILON)

        # Apply any explicit user mood modifier
        mood_modifier = user_state.get("mood_modifier", 1.0)

        g = scene_g * user_receptivity * mood_modifier

        # === Determine Result ===
        if g <= self.EPSILON:
            ratio = float("inf")
            result = ForgeResult.IMPOSSIBLE
        else:
            ratio = f / g
            if ratio < 0.9:
                result = ForgeResult.VERIFIED
            elif ratio < 1.0:
                result = ForgeResult.WARNING
            else:
                result = ForgeResult.FORBIDDEN

        # === Generate Proof Hash ===
        proof_str = f"{intent}|{ratio}|{timestamp}|{self._verification_count}"
        proof_hash = hashlib.sha256(proof_str.encode()).hexdigest()[:16]

        return KinematicProof(
            f=f,
            g=g,
            ratio=ratio if ratio != float("inf") else 999.99,
            result=result,
            proof_hash=proof_hash,
            timestamp=timestamp,
        )

    def verify_batch(
        self,
        intents: List[Tuple[str, float]],
        scene_type: SceneType,
        user_state: Dict[str, any],
    ) -> List[KinematicProof]:
        """
        Verify multiple intents and return all proofs.

        Args:
            intents: List of (comment, priority) tuples
            scene_type: Current scene classification
            user_state: Dictionary with user receptivity data

        Returns:
            List of KinematicProof objects
        """
        return [
            self.verify(intent, priority, scene_type, user_state)
            for intent, priority in intents
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# KINEMATIC CINEMA COMPANION (Layer 1: Executive)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpeechEvent:
    """Record of a speech event (spoken or silenced)."""
    comment: str
    proof: KinematicProof
    spoken: bool
    damped: bool = False
    original_comment: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class KinematicCinemaCompanion:
    """
    The executive layer that manages Newton's cinema commentary.

    This companion:
    1. Receives intents from Newton's analysis systems
    2. Verifies them against the Kinetic Forge
    3. Applies Damping if necessary and possible
    4. Speaks verified comments or enforces silence

    The companion maintains state about user feedback (shushes) and
    adjusts its behavior accordingly - "training" itself to the
    viewer's preferences.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize the Kinematic Cinema Companion.

        Args:
            verbose: Whether to print detailed verification info
        """
        self.forge = KineticForge()
        self.silence_streak: int = 0
        self.mood_modifier: float = 1.0
        self.verbose = verbose

        # History tracking
        self.speech_history: List[SpeechEvent] = []
        self.damping_map: Dict[str, str] = dict(DAMPING_SUBSTITUTIONS)

    @property
    def user_state(self) -> Dict[str, any]:
        """Current user state for forge verification."""
        return {
            "silence_streak": self.silence_streak,
            "mood_modifier": self.mood_modifier,
        }

    def evaluate_intent(
        self,
        comment: str,
        priority: float,
        scene_type: SceneType | str,
    ) -> Tuple[bool, KinematicProof]:
        """
        Evaluate whether an intent should be spoken.

        Args:
            comment: The comment to potentially speak
            priority: Importance level [0.0-1.0]
            scene_type: SceneType enum or string name

        Returns:
            Tuple of (was_spoken, proof)
        """
        # Normalize scene type
        if isinstance(scene_type, str):
            scene_type = SceneType(scene_type.lower())

        if self.verbose:
            print(f"--- PHASE 1-4: INGEST & COMPARE ---")

        # Initial verification
        proof = self.forge.verify(comment, priority, scene_type, self.user_state)

        if self.verbose:
            print(f"Intent: '{comment}'")
            print(f"Scene: {scene_type.name} (g_base={scene_type.gravity:.2f})")
            print(f"f/g Ratio: {proof.f:.2f}/{proof.g:.2f} = {proof.ratio:.2f} {proof.result.symbol}")

        # If forbidden, attempt damping
        if proof.result == ForgeResult.FORBIDDEN:
            damped_comment = self._dampen_linguistics(comment)

            if damped_comment != comment:
                damped_proof = self.forge.verify(
                    damped_comment, priority, scene_type, self.user_state
                )

                if damped_proof.can_speak:
                    if self.verbose:
                        print(f"--- KINEMATIC DAMPING APPLIED ---")
                        print(f"Original Forbidden (f/g: {proof.ratio:.2f})")
                        print(f"Damped to {damped_proof.result.symbol} (f/g: {damped_proof.ratio:.2f})")

                    self._speak(damped_comment, damped_proof)
                    self._record_event(damped_comment, damped_proof, True, True, comment)
                    return (True, damped_proof)

        # Speak if verified/warning
        if proof.can_speak:
            if self.verbose:
                print(f"--- PHASE 9: COMMIT (Speaking) ---")
            self._speak(comment, proof)
            self._record_event(comment, proof, True)
            self.silence_streak = 0  # Reset on successful speech
            return (True, proof)

        # Enforce silence
        if self.verbose:
            print(f"--- FINFR: ONTOLOGICAL DEATH OF COMMENT ---")
            reason = (
                "Ground is zero. Total silence required."
                if proof.result == ForgeResult.IMPOSSIBLE
                else f"Constraint violated. Ratio {proof.ratio:.2f} exceeds 1.0 boundary."
            )
            print(f"Reason: {reason}")

        self._record_event(comment, proof, False)
        return (False, proof)

    def _dampen_linguistics(self, comment: str) -> str:
        """
        Replace high-instability words with kinematically stable alternatives.

        Args:
            comment: Original comment

        Returns:
            Damped comment (may be unchanged if no substitutions found)
        """
        words = comment.split()
        damped_words = []

        for word in words:
            upper_word = word.upper()
            # Preserve original case pattern
            if upper_word in self.damping_map:
                replacement = self.damping_map[upper_word]
                # Apply original case pattern to replacement
                if word.isupper():
                    damped_words.append(replacement)
                elif word.istitle():
                    damped_words.append(replacement.title())
                else:
                    damped_words.append(replacement.lower())
            else:
                damped_words.append(word)

        return " ".join(damped_words)

    def _speak(self, comment: str, proof: KinematicProof) -> None:
        """Output the comment with verification."""
        print(f"NEWTON: {comment}")
        if self.verbose:
            print(f"Verification: {proof.proof_hash}")

    def _record_event(
        self,
        comment: str,
        proof: KinematicProof,
        spoken: bool,
        damped: bool = False,
        original: Optional[str] = None,
    ) -> None:
        """Record a speech event to history."""
        self.speech_history.append(SpeechEvent(
            comment=comment,
            proof=proof,
            spoken=spoken,
            damped=damped,
            original_comment=original,
        ))

    # ═══════════════════════════════════════════════════════════════════════════
    # USER FEEDBACK METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def record_user_shush(self) -> None:
        """
        Record that the user requested silence.

        This shrinks the Ground (g) for future verifications.
        """
        self.silence_streak += 1
        if self.verbose:
            print(f"🔴 Constraint updated: User requested silence.")
            print(f"   Ground (g) modifier: {1.0 - self.silence_streak * 0.2:.2f}")

    def record_user_engagement(self) -> None:
        """
        Record positive user engagement.

        This partially restores Ground (g).
        """
        self.silence_streak = max(0, self.silence_streak - 1)
        if self.verbose:
            print(f"🟢 Constraint updated: User engaged positively.")

    def set_mood(self, modifier: float) -> None:
        """
        Set explicit mood modifier.

        Args:
            modifier: Value in [0.0, 2.0] where 1.0 is neutral
        """
        self.mood_modifier = max(0.0, min(2.0, modifier))
        if self.verbose:
            print(f"Mood modifier set to: {self.mood_modifier:.2f}")

    def add_damping_rule(self, unstable: str, stable: str) -> None:
        """
        Add a custom damping substitution rule.

        Args:
            unstable: High-instability word to replace
            stable: Low-instability replacement
        """
        self.damping_map[unstable.upper()] = stable.upper()

    # ═══════════════════════════════════════════════════════════════════════════
    # STATISTICS & INTROSPECTION
    # ═══════════════════════════════════════════════════════════════════════════

    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about companion behavior."""
        total = len(self.speech_history)
        spoken = sum(1 for e in self.speech_history if e.spoken)
        damped = sum(1 for e in self.speech_history if e.damped)
        silenced = total - spoken

        return {
            "total_intents": total,
            "spoken": spoken,
            "silenced": silenced,
            "damped": damped,
            "silence_rate": silenced / total if total > 0 else 0.0,
            "damping_rate": damped / spoken if spoken > 0 else 0.0,
            "current_silence_streak": self.silence_streak,
            "current_mood_modifier": self.mood_modifier,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Result Types
    "ForgeResult",
    "KinematicProof",
    "SpeechEvent",
    # Scene Classification
    "SceneType",
    # Engines
    "KinematicLinguistics",
    "KineticForge",
    "KinematicCinemaCompanion",
]
