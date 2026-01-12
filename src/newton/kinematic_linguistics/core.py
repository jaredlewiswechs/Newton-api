"""
KINEMATIC LINGUISTICS - CORE ENGINE
A Geometric Substrate for Semantic Reliability

PARCRI Real Intelligence - January 2026
Specification v1.1 (Validated Refinements)

This module implements the core analysis and verification engines:
  - WordAssemblyAnalyzer: Decompose words into mechanical assemblies
  - DistortionIndexCalculator: Measure semantic/geometric mismatch
  - KinematicCompiler: The Newton semantic constraint engine
  - AntonymAnalyzer: Geometric vs dictionary antonym detection

Core Philosophy: We must move from probabilistic AI to geometric AI.
"""

import time
import hashlib
from dataclasses import dataclass, field as dataclass_field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum

from .matter import (
    GlyphMechanics,
    GlyphRegistry,
    PhonosemanticsRegistry,
    PhonosemanticsCluster,
    StabilityClass,
    LetterPosition,
    WordAssemblyRole,
    WORD_GEOMETRY_EXAMPLES,
)


# ==================================================================================
# WORD ASSEMBLY ANALYSIS (Section 2.2)
# ==================================================================================

@dataclass(frozen=True)
class WordVector:
    """
    The kinematic vector representation of a word.

    From v1.1 Validated Refinements:
    Word_Vector = (2 * Consonant_Force) + (1 * Vowel_Cohesion)
    """
    word: str
    stability_score: float      # Average stability
    instability_score: float    # 1.0 - stability
    consonant_force: float      # Sum of consonant glyph forces
    vowel_cohesion: float       # Sum of vowel glyph cohesion
    weighted_vector: float      # v1.1: (2 * consonant) + (1 * vowel)
    anchor_count: int           # Number of stabilizing glyphs
    destabilizer_count: int     # Number of destabilizing glyphs
    energy_score: float         # Pressure/force glyph contribution
    containment_score: float    # Volume glyph contribution
    dominant_vector_type: str   # Most common vector type
    terminal_state: str         # Mechanical output state (from terminal letter)


@dataclass(frozen=True)
class WordAssembly:
    """
    Complete mechanical assembly breakdown of a word.

    From Section 2.2: Words function as mechanical assemblies.
    Each letter contributes a constraint to the overall structure.
    """
    word: str
    letters: Tuple[WordAssemblyRole, ...]
    vector: WordVector
    phonosemantic_clusters: Tuple[PhonosemanticsCluster, ...]
    mechanical_prediction: str
    stability_class: StabilityClass


class WordAssemblyAnalyzer:
    """
    Analyzes words as mechanical assemblies.

    From Section 2.2: The sequence matters:
    - Initial letters establish the primary load path
    - Medial letters provide bracing and flow
    - Terminal letters determine the output state

    Assembly Formula:
    Word_Stability = f(Initial_Load, Medial_Bracing, Terminal_State)
    """

    # Position weights for assembly analysis
    INITIAL_WEIGHT = 1.5   # Primary load path
    MEDIAL_WEIGHT = 1.0    # Bracing and flow
    TERMINAL_WEIGHT = 1.3  # Output state determination

    # v1.1: Consonant/vowel weighting
    CONSONANT_WEIGHT = 2.0
    VOWEL_WEIGHT = 1.0

    @classmethod
    def analyze(cls, word: str) -> WordAssembly:
        """
        Perform complete mechanical analysis of a word.

        Args:
            word: The word to analyze

        Returns:
            WordAssembly with full mechanical breakdown
        """
        clean = word.upper().strip()
        if not clean:
            return cls._empty_assembly(word)

        # Step 1: Decompose into letter roles
        letters = cls._decompose_letters(clean)

        # Step 2: Calculate vector
        vector = cls._calculate_vector(clean, letters)

        # Step 3: Detect phonosemantic clusters
        clusters = tuple(PhonosemanticsRegistry.detect_clusters(clean))

        # Step 4: Generate mechanical prediction
        prediction = cls._generate_prediction(clean, letters, clusters)

        # Step 5: Determine stability class
        stability_class = cls._classify_stability(vector.stability_score)

        return WordAssembly(
            word=clean,
            letters=letters,
            vector=vector,
            phonosemantic_clusters=clusters,
            mechanical_prediction=prediction,
            stability_class=stability_class,
        )

    @classmethod
    def _decompose_letters(cls, word: str) -> Tuple[WordAssemblyRole, ...]:
        """Decompose word into position-weighted letter roles."""
        roles = []
        length = len(word)

        for i, char in enumerate(word):
            if not char.isalpha():
                continue

            mechanics = GlyphRegistry.get(char)
            if not mechanics:
                continue

            # Determine position
            if i == 0:
                position = LetterPosition.INITIAL
                weight = cls.INITIAL_WEIGHT
            elif i == length - 1:
                position = LetterPosition.TERMINAL
                weight = cls.TERMINAL_WEIGHT
            else:
                position = LetterPosition.MEDIAL
                weight = cls.MEDIAL_WEIGHT

            roles.append(WordAssemblyRole(
                letter=char,
                position=position,
                glyph_mechanics=mechanics,
                position_weight=weight,
            ))

        return tuple(roles)

    @classmethod
    def _calculate_vector(
        cls,
        word: str,
        letters: Tuple[WordAssemblyRole, ...]
    ) -> WordVector:
        """Calculate the kinematic vector for a word using v1.1 weighting."""
        if not letters:
            return cls._empty_vector(word)

        # Separate consonants and vowels for weighted calculation
        consonant_stabilities = []
        vowel_stabilities = []

        for role in letters:
            if role.glyph_mechanics.is_consonant:
                consonant_stabilities.append(role.weighted_stability)
            else:
                vowel_stabilities.append(role.weighted_stability)

        # v1.1: Calculate weighted vector
        consonant_force = sum(consonant_stabilities) if consonant_stabilities else 0.0
        vowel_cohesion = sum(vowel_stabilities) if vowel_stabilities else 0.0
        weighted_vector = (cls.CONSONANT_WEIGHT * consonant_force) + (cls.VOWEL_WEIGHT * vowel_cohesion)

        # Standard stability calculation
        all_stabilities = [r.weighted_stability for r in letters]
        avg_stability = sum(all_stabilities) / len(all_stabilities)

        # Count glyph categories
        upper_word = word.upper()
        anchor_count = sum(1 for c in upper_word if c in GlyphRegistry.ANCHORS)
        destabilizer_count = sum(1 for c in upper_word if c in GlyphRegistry.DESTABILIZERS)

        # Energy and containment scores
        pressure_chars = [c for c in upper_word if c in GlyphRegistry.PRESSURE_GLYPHS]
        volume_chars = [c for c in upper_word if c in GlyphRegistry.VOLUME_GLYPHS]
        energy_score = sum(GlyphRegistry.stability(c) for c in pressure_chars) / len(pressure_chars) if pressure_chars else 0.0
        containment_score = sum(GlyphRegistry.stability(c) for c in volume_chars) / len(volume_chars) if volume_chars else 0.0

        # Dominant vector type
        vector_counts: Dict[str, int] = {}
        for role in letters:
            vt = role.glyph_mechanics.vector_type
            vector_counts[vt] = vector_counts.get(vt, 0) + 1
        dominant = max(vector_counts.items(), key=lambda x: x[1])[0] if vector_counts else "Neutral"

        # Terminal state from last letter
        terminal_state = letters[-1].glyph_mechanics.vector_type if letters else "Undefined"

        return WordVector(
            word=word,
            stability_score=avg_stability,
            instability_score=1.0 - avg_stability,
            consonant_force=consonant_force,
            vowel_cohesion=vowel_cohesion,
            weighted_vector=weighted_vector,
            anchor_count=anchor_count,
            destabilizer_count=destabilizer_count,
            energy_score=energy_score,
            containment_score=containment_score,
            dominant_vector_type=dominant,
            terminal_state=terminal_state,
        )

    @classmethod
    def _generate_prediction(
        cls,
        word: str,
        letters: Tuple[WordAssemblyRole, ...],
        clusters: Tuple[PhonosemanticsCluster, ...]
    ) -> str:
        """Generate mechanical prediction from assembly analysis."""
        if word in WORD_GEOMETRY_EXAMPLES:
            return WORD_GEOMETRY_EXAMPLES[word]["prediction"]

        if not letters:
            return "Empty assembly"

        # Build prediction from letter sequence
        parts = []
        for role in letters:
            prop = role.glyph_mechanics.physical_property.split(',')[0].strip()
            parts.append(prop.lower())

        # Add cluster influences
        cluster_effects = []
        for cluster in clusters:
            cluster_effects.append(cluster.mechanical_meaning.split('/')[0].strip())

        base_prediction = " -> ".join(parts)
        if cluster_effects:
            base_prediction += f" (with {', '.join(cluster_effects)})"

        return base_prediction

    @classmethod
    def _classify_stability(cls, score: float) -> StabilityClass:
        """Classify stability score into category."""
        if score >= 0.7:
            return StabilityClass.HIGH
        elif score >= 0.5:
            return StabilityClass.MEDIUM
        else:
            return StabilityClass.LOW

    @classmethod
    def _empty_assembly(cls, word: str) -> WordAssembly:
        """Return empty assembly for invalid input."""
        return WordAssembly(
            word=word,
            letters=(),
            vector=cls._empty_vector(word),
            phonosemantic_clusters=(),
            mechanical_prediction="Empty or invalid word",
            stability_class=StabilityClass.MEDIUM,
        )

    @classmethod
    def _empty_vector(cls, word: str) -> WordVector:
        """Return neutral vector for empty word."""
        return WordVector(
            word=word,
            stability_score=0.5,
            instability_score=0.5,
            consonant_force=0.0,
            vowel_cohesion=0.0,
            weighted_vector=0.0,
            anchor_count=0,
            destabilizer_count=0,
            energy_score=0.0,
            containment_score=0.0,
            dominant_vector_type="Neutral",
            terminal_state="Undefined",
        )


# ==================================================================================
# DISTORTION INDEX (Section 5.3)
# ==================================================================================

@dataclass(frozen=True)
class DistortionReport:
    """
    Report on semantic distortion between word geometry and reality.

    From Section 5.3: When language is used to obscure rather than describe
    reality, the kinematic framework can quantify the distortion.

    Distortion Index = |Vector(reality) - Vector(word)| / |Vector(reality)|
    """
    word_used: str
    word_vector: float          # Predicted magnitude from word geometry
    reality_vector: float       # Actual magnitude in reality
    distortion_index: float     # 0.0 = perfect match, 1.0 = complete mismatch
    accuracy_percentage: float  # How much of reality the word captures
    is_misleading: bool         # True if distortion > 0.5
    recommended_word: Optional[str]  # Geometrically appropriate alternative
    explanation: str


class DistortionIndexCalculator:
    """
    Calculates semantic distortion between language and reality.

    From Section 5.3 Example:
    - "Correction" implies -5% to -10% market movement
    - A -30% decline is a "CRASH"
    - D = |(-30%) - (-7.5%)| / |-30%| = 0.75 (75% distortion)
    """

    # Word geometry to expected magnitude mappings (from specification)
    WORD_MAGNITUDES: Dict[str, Tuple[float, float]] = {
        # Financial terms
        "CORRECTION": (-0.05, -0.10),   # Mild adjustment
        "DECLINE": (-0.10, -0.20),      # Moderate drop
        "CRASH": (-0.25, -0.50),        # Severe collapse
        "COLLAPSE": (-0.40, -0.70),     # Total failure

        # Safety terms
        "TRIM": (0.01, 0.05),           # Small adjustment
        "ADJUST": (0.02, 0.10),         # Moderate change
        "DIVE": (0.30, 0.90),           # Major descent
        "PLUNGE": (0.50, 1.00),         # Extreme descent

        # Intensity terms
        "MINOR": (0.01, 0.10),
        "MODERATE": (0.10, 0.30),
        "SIGNIFICANT": (0.30, 0.50),
        "SEVERE": (0.50, 0.80),
        "CATASTROPHIC": (0.80, 1.00),
    }

    @classmethod
    def calculate(
        cls,
        word_used: str,
        reality_magnitude: float,
        domain: str = "general"
    ) -> DistortionReport:
        """
        Calculate distortion index for word usage.

        Args:
            word_used: The word being analyzed
            reality_magnitude: The actual magnitude being described (0.0-1.0 scale)
            domain: Context domain for recommendations

        Returns:
            DistortionReport with distortion analysis
        """
        upper_word = word_used.upper()

        # Get expected magnitude range for word
        if upper_word in cls.WORD_MAGNITUDES:
            expected_min, expected_max = cls.WORD_MAGNITUDES[upper_word]
            word_vector = (expected_min + expected_max) / 2
        else:
            # Derive from word stability (high stability = low magnitude)
            assembly = WordAssemblyAnalyzer.analyze(upper_word)
            # Inverse relationship: stable words describe smaller phenomena
            word_vector = 1.0 - assembly.vector.stability_score

        # Handle negative values (like market declines)
        abs_reality = abs(reality_magnitude)
        abs_word = abs(word_vector)

        # Calculate distortion
        if abs_reality > 0.001:  # Avoid division by zero
            distortion = abs(abs_reality - abs_word) / abs_reality
        else:
            distortion = 0.0 if abs_word < 0.01 else 1.0

        distortion = min(distortion, 1.0)  # Cap at 1.0
        accuracy = (1.0 - distortion) * 100

        # Find recommended word
        recommended = cls._find_appropriate_word(abs_reality)

        # Generate explanation
        explanation = cls._generate_explanation(
            word_used, word_vector, reality_magnitude, distortion
        )

        return DistortionReport(
            word_used=word_used,
            word_vector=word_vector,
            reality_vector=reality_magnitude,
            distortion_index=distortion,
            accuracy_percentage=accuracy,
            is_misleading=distortion > 0.5,
            recommended_word=recommended,
            explanation=explanation,
        )

    @classmethod
    def _find_appropriate_word(cls, magnitude: float) -> Optional[str]:
        """Find word with geometry matching the magnitude."""
        abs_mag = abs(magnitude)
        best_match = None
        best_diff = float('inf')

        for word, (min_val, max_val) in cls.WORD_MAGNITUDES.items():
            mid = (abs(min_val) + abs(max_val)) / 2
            diff = abs(abs_mag - mid)
            if diff < best_diff:
                best_diff = diff
                best_match = word

        return best_match

    @classmethod
    def _generate_explanation(
        cls,
        word: str,
        word_vector: float,
        reality: float,
        distortion: float
    ) -> str:
        """Generate human-readable explanation of distortion."""
        if distortion < 0.25:
            quality = "accurately describes"
        elif distortion < 0.5:
            quality = "partially captures"
        elif distortion < 0.75:
            quality = "significantly understates"
        else:
            quality = "fundamentally misrepresents"

        return (
            f"'{word}' {quality} the phenomenon. "
            f"Word geometry predicts magnitude ~{abs(word_vector):.1%}, "
            f"reality shows {abs(reality):.1%}. "
            f"The word captures {(1-distortion)*100:.0f}% of actual magnitude."
        )


# ==================================================================================
# ANTONYM ANALYSIS (v1.1 Refinement 2)
# ==================================================================================

class AntonymType(Enum):
    """Classification of antonym relationship."""
    GEOMETRIC_INVERSION = "geometric"   # True mechanical inversion
    DICTIONARY_ONLY = "dictionary"      # Cultural opposition only
    ORTHOGONAL = "orthogonal"           # Neither aligned nor inverted
    CONGRUENT = "congruent"             # Actually similar (not antonyms)


@dataclass(frozen=True)
class AntonymAnalysis:
    """
    Analysis of antonym relationship between two words.

    From v1.1 Refinement 2: Not all dictionary antonyms are geometric inversions.
    Cultural opposition != mechanical inversion.
    """
    word1: str
    word2: str
    word1_vector: WordVector
    word2_vector: WordVector
    geometric_similarity: float      # -1.0 (inverted) to 1.0 (identical)
    is_geometric_antonym: bool       # True if geometrically inverted
    is_dictionary_antonym: bool      # True if culturally opposite
    antonym_type: AntonymType
    inversion_percentage: float      # How inverted (0-100%)
    explanation: str


class AntonymAnalyzer:
    """
    Analyzes geometric vs dictionary antonym relationships.

    From v1.1: When dictionary and geometry diverge, the word itself
    encodes a mechanical reality missed by definition.
    """

    # Known dictionary antonym pairs for validation
    DICTIONARY_ANTONYMS: Set[Tuple[str, str]] = {
        ("LOVE", "HATE"),
        ("TRUST", "DOUBT"),
        ("SAFE", "DANGER"),
        ("WHOLE", "BROKE"),
        ("HELP", "HARM"),
        ("GOOD", "BAD"),
        ("LIGHT", "DARK"),
        ("FAST", "SLOW"),
        ("HOT", "COLD"),
        ("STRONG", "WEAK"),
    }

    @classmethod
    def analyze(cls, word1: str, word2: str) -> AntonymAnalysis:
        """
        Analyze geometric relationship between two words.

        Args:
            word1: First word
            word2: Second word

        Returns:
            AntonymAnalysis with relationship classification
        """
        upper1, upper2 = word1.upper(), word2.upper()

        # Get word assemblies
        assembly1 = WordAssemblyAnalyzer.analyze(upper1)
        assembly2 = WordAssemblyAnalyzer.analyze(upper2)

        vec1, vec2 = assembly1.vector, assembly2.vector

        # Calculate geometric similarity
        similarity = cls._calculate_geometric_similarity(vec1, vec2)

        # Determine if dictionary antonym
        is_dict_antonym = cls._is_dictionary_antonym(upper1, upper2)

        # Classify relationship
        is_geo_antonym = similarity < -0.5
        inversion = abs(min(0, similarity)) * 100

        antonym_type = cls._classify_relationship(
            similarity, is_dict_antonym
        )

        explanation = cls._generate_explanation(
            upper1, upper2, similarity, is_dict_antonym, antonym_type
        )

        return AntonymAnalysis(
            word1=upper1,
            word2=upper2,
            word1_vector=vec1,
            word2_vector=vec2,
            geometric_similarity=similarity,
            is_geometric_antonym=is_geo_antonym,
            is_dictionary_antonym=is_dict_antonym,
            antonym_type=antonym_type,
            inversion_percentage=inversion,
            explanation=explanation,
        )

    @classmethod
    def _calculate_geometric_similarity(
        cls,
        vec1: WordVector,
        vec2: WordVector
    ) -> float:
        """
        Calculate geometric similarity between word vectors.

        Returns:
            -1.0 (perfect inversion) to 1.0 (identical)
        """
        # Compare multiple dimensions
        stability_diff = abs(vec1.stability_score - vec2.stability_score)
        terminal_match = 1.0 if vec1.terminal_state == vec2.terminal_state else 0.0

        # Check for load path inversion
        # Inverted if one has high anchors and other has high destabilizers
        anchor_balance1 = vec1.anchor_count - vec1.destabilizer_count
        anchor_balance2 = vec2.anchor_count - vec2.destabilizer_count
        balance_product = anchor_balance1 * anchor_balance2

        # Negative product indicates opposition
        if balance_product < 0:
            inversion_factor = -abs(balance_product) / max(abs(anchor_balance1), abs(anchor_balance2), 1)
        else:
            inversion_factor = min(balance_product / max(vec1.anchor_count + vec2.anchor_count, 1), 1)

        # Energy/containment comparison
        energy_diff = abs(vec1.energy_score - vec2.energy_score)
        containment_diff = abs(vec1.containment_score - vec2.containment_score)

        # Weighted similarity calculation
        similarity = (
            (1.0 - stability_diff) * 0.3 +
            terminal_match * 0.2 +
            inversion_factor * 0.3 +
            (1.0 - energy_diff) * 0.1 +
            (1.0 - containment_diff) * 0.1
        )

        # Normalize to [-1, 1] range
        return (similarity * 2) - 1

    @classmethod
    def _is_dictionary_antonym(cls, word1: str, word2: str) -> bool:
        """Check if words are known dictionary antonyms."""
        pair = tuple(sorted([word1, word2]))
        return pair in cls.DICTIONARY_ANTONYMS or (word2, word1) in cls.DICTIONARY_ANTONYMS

    @classmethod
    def _classify_relationship(
        cls,
        similarity: float,
        is_dict_antonym: bool
    ) -> AntonymType:
        """Classify the antonym relationship type."""
        if similarity < -0.5:  # Strong geometric inversion
            return AntonymType.GEOMETRIC_INVERSION
        elif is_dict_antonym and similarity > 0.3:
            return AntonymType.DICTIONARY_ONLY
        elif abs(similarity) < 0.3:
            return AntonymType.ORTHOGONAL
        elif similarity > 0.5:
            return AntonymType.CONGRUENT
        else:
            return AntonymType.DICTIONARY_ONLY if is_dict_antonym else AntonymType.ORTHOGONAL

    @classmethod
    def _generate_explanation(
        cls,
        word1: str,
        word2: str,
        similarity: float,
        is_dict: bool,
        antonym_type: AntonymType
    ) -> str:
        """Generate explanation of the relationship."""
        if antonym_type == AntonymType.GEOMETRIC_INVERSION:
            return (
                f"'{word1}' and '{word2}' are geometrically inverted "
                f"(similarity: {similarity:.2f}). Their mechanical structures "
                f"represent opposite load paths."
            )
        elif antonym_type == AntonymType.DICTIONARY_ONLY:
            return (
                f"'{word1}' and '{word2}' are cultural antonyms but not "
                f"geometric inversions (similarity: {similarity:.2f}). "
                f"The dictionary opposition reflects social convention, not mechanical reality."
            )
        elif antonym_type == AntonymType.ORTHOGONAL:
            return (
                f"'{word1}' and '{word2}' are orthogonal "
                f"(similarity: {similarity:.2f}). They occupy different semantic dimensions "
                f"rather than opposing positions on the same axis."
            )
        else:
            return (
                f"'{word1}' and '{word2}' are geometrically similar "
                f"(similarity: {similarity:.2f}), not antonyms. "
                f"Their mechanical structures follow similar patterns."
            )


# ==================================================================================
# KINEMATIC COMPILER (Section 6)
# ==================================================================================

class CompilerRegime(Enum):
    """
    Compilation regime determining constraint strictness.

    From Section 6.1 Phase 0 - Intent Lock: Establish the physical regime.
    """
    GENERAL = "general"              # Standard compilation
    SAFETY_CRITICAL = "safety"       # Aviation, medical, nuclear
    LEGAL = "legal"                  # Contracts, policies
    CREATIVE = "creative"            # Allow more ambiguity


@dataclass(frozen=True)
class CompilationProof:
    """
    Immutable proof of kinematic compilation.

    The Newton compiler transforms language into verified geometric structures.
    """
    input_text: str
    regime: CompilerRegime
    f_demand: float           # Total linguistic demand
    g_ground: float           # Available geometric ground
    fg_ratio: float           # f/g constraint ratio
    is_admissible: bool       # Passes geometric verification
    structural_failures: Tuple[str, ...]  # Failed constraints
    word_vectors: Tuple[WordVector, ...]  # All analyzed words
    distortion_warnings: Tuple[str, ...]  # Potential misleading language
    proof_hash: str           # SHA-256 truncated
    timestamp: float


class StructuralFailure(Enum):
    """Types of structural failure in compilation."""
    INSUFFICIENT_ANCHORING = "insufficient_anchoring"
    LOAD_PATH_CONTRADICTION = "load_path_contradiction"
    GEOMETRY_MISMATCH = "geometry_mismatch"
    SEMANTIC_INSTABILITY = "semantic_instability"
    ANTONYM_COLLISION = "antonym_collision"


class KinematicCompiler:
    """
    The Newton semantic constraint compiler.

    From Section 6.1: The kinematic linguistics framework integrates into
    a semantic compiler with the following phases:

    Phase 0 - Intent Lock: Establish physical regime
    Phase 1 - Glyph Decomposition: Parse into mechanical components
    Phase 2 - Vector Mapping: Transform metaphors into physics vectors
    Phase 3 - Constraint Verification: Check geometry against reality
    Phase 4 - Execution or Rejection: Only verified commands proceed
    """

    # Regime-specific thresholds
    REGIME_THRESHOLDS: Dict[CompilerRegime, Dict[str, float]] = {
        CompilerRegime.GENERAL: {
            "stability_min": 0.4,
            "fg_max": 1.0,
            "distortion_warn": 0.5,
        },
        CompilerRegime.SAFETY_CRITICAL: {
            "stability_min": 0.6,
            "fg_max": 0.9,
            "distortion_warn": 0.25,
        },
        CompilerRegime.LEGAL: {
            "stability_min": 0.5,
            "fg_max": 0.95,
            "distortion_warn": 0.3,
        },
        CompilerRegime.CREATIVE: {
            "stability_min": 0.2,
            "fg_max": 1.5,
            "distortion_warn": 0.75,
        },
    }

    def __init__(self, regime: CompilerRegime = CompilerRegime.GENERAL):
        """Initialize compiler with specified regime."""
        self.regime = regime
        self.thresholds = self.REGIME_THRESHOLDS[regime]
        self._compilation_count = 0

    def compile(self, text: str) -> CompilationProof:
        """
        Compile text through kinematic verification.

        Args:
            text: The text to compile

        Returns:
            CompilationProof with verification results
        """
        timestamp = time.time()
        self._compilation_count += 1

        # Phase 1: Glyph Decomposition
        words = text.split()
        word_vectors = []
        total_instability = 0.0

        for word in words:
            clean = ''.join(c for c in word if c.isalpha())
            if clean:
                assembly = WordAssemblyAnalyzer.analyze(clean)
                word_vectors.append(assembly.vector)
                total_instability += assembly.vector.instability_score

        # Phase 2: Vector Mapping - Calculate f (demand)
        if word_vectors:
            avg_instability = total_instability / len(word_vectors)
            f_demand = avg_instability
        else:
            f_demand = 0.5

        # Calculate g (ground) based on regime
        g_ground = self._calculate_ground(word_vectors)

        # Phase 3: Constraint Verification
        fg_ratio = f_demand / g_ground if g_ground > 0.01 else float('inf')
        failures = self._verify_constraints(word_vectors, fg_ratio)
        distortion_warnings = self._check_distortion(words)

        # Phase 4: Determine admissibility
        is_admissible = (
            fg_ratio <= self.thresholds["fg_max"] and
            len(failures) == 0
        )

        # Generate proof hash
        proof_str = f"{text}|{fg_ratio}|{timestamp}|{self._compilation_count}"
        proof_hash = hashlib.sha256(proof_str.encode()).hexdigest()[:16]

        return CompilationProof(
            input_text=text,
            regime=self.regime,
            f_demand=f_demand,
            g_ground=g_ground,
            fg_ratio=min(fg_ratio, 999.99),
            is_admissible=is_admissible,
            structural_failures=tuple(failures),
            word_vectors=tuple(word_vectors),
            distortion_warnings=tuple(distortion_warnings),
            proof_hash=proof_hash,
            timestamp=timestamp,
        )

    def _calculate_ground(self, vectors: List[WordVector]) -> float:
        """Calculate available ground (g) from word vectors."""
        if not vectors:
            return 0.5

        # Ground increases with stability and anchoring
        total_anchors = sum(v.anchor_count for v in vectors)
        avg_stability = sum(v.stability_score for v in vectors) / len(vectors)

        # Base ground from stability
        base_ground = avg_stability

        # Bonus for anchoring
        anchor_bonus = min(total_anchors * 0.05, 0.3)

        return base_ground + anchor_bonus

    def _verify_constraints(
        self,
        vectors: List[WordVector],
        fg_ratio: float
    ) -> List[str]:
        """Verify structural constraints and return failures."""
        failures = []

        for vec in vectors:
            # Check minimum stability
            if vec.stability_score < self.thresholds["stability_min"]:
                failures.append(
                    f"INSUFFICIENT_ANCHORING: '{vec.word}' stability "
                    f"{vec.stability_score:.2f} < {self.thresholds['stability_min']}"
                )

            # Check anchor/destabilizer balance
            if vec.destabilizer_count > vec.anchor_count + 2:
                failures.append(
                    f"SEMANTIC_INSTABILITY: '{vec.word}' has "
                    f"{vec.destabilizer_count} destabilizers vs {vec.anchor_count} anchors"
                )

        # Check f/g ratio
        if fg_ratio > self.thresholds["fg_max"]:
            failures.append(
                f"GEOMETRY_MISMATCH: f/g ratio {fg_ratio:.2f} exceeds "
                f"regime threshold {self.thresholds['fg_max']}"
            )

        return failures

    def _check_distortion(self, words: List[str]) -> List[str]:
        """Check for potentially misleading language."""
        warnings = []

        for word in words:
            clean = ''.join(c for c in word if c.isalpha()).upper()
            if clean in DistortionIndexCalculator.WORD_MAGNITUDES:
                warnings.append(
                    f"VERIFY: '{clean}' has specific magnitude implications - "
                    f"ensure reality matches word geometry"
                )

        return warnings

    def compile_and_verify_pair(
        self,
        action_word: str,
        target_description: str
    ) -> Tuple[CompilationProof, Optional[str]]:
        """
        Verify action word matches target reality.

        From Section 5.2 MCAS example: TRIM vs DIVE mismatch.

        Args:
            action_word: The word describing the action
            target_description: Description of actual target/effect

        Returns:
            (proof, error_message or None)
        """
        action_assembly = WordAssemblyAnalyzer.analyze(action_word)
        target_proof = self.compile(target_description)

        # Check for geometry mismatch
        if action_assembly.stability_class != StabilityClass.HIGH:
            if self.regime == CompilerRegime.SAFETY_CRITICAL:
                return (
                    target_proof,
                    f"WARNING: Action word '{action_word}' has "
                    f"{action_assembly.stability_class.value} stability. "
                    f"Safety-critical systems require high-stability terminology."
                )

        return (target_proof, None)


# ==================================================================================
# HALLUCINATION PREVENTION (Section 6.3)
# ==================================================================================

@dataclass(frozen=True)
class HallucinationCheck:
    """
    Result of hallucination detection check.

    From Section 6.3: AI hallucinations are often geometrically unstable
    assemblies—word combinations that cannot bear semantic load.
    """
    phrase: str
    is_hallucination: bool
    stability_score: float
    contradiction_detected: bool
    explanation: str


class HallucinationDetector:
    """
    Detects geometrically unstable word combinations.

    From Section 6.3 Example: "Safe Risk"
    - SAFE terminates in protective layering (E)
    - RISK terminates in cutting action (K)
    - Junction cannot bear semantic load
    """

    # Known contradictory terminal pairs
    CONTRADICTORY_TERMINALS: Set[Tuple[str, str]] = {
        ("E", "K"),  # Layers vs Cut
        ("T", "S"),  # Stop vs Slip
        ("O", "Z"),  # Containment vs Dissipation
        ("B", "W"),  # Block vs Wave
        ("H", "I"),  # Bridge vs single axis (weak connection)
    }

    @classmethod
    def check(cls, phrase: str) -> HallucinationCheck:
        """
        Check phrase for geometric hallucination.

        Args:
            phrase: The phrase to check

        Returns:
            HallucinationCheck with analysis
        """
        words = phrase.split()
        if len(words) < 2:
            return HallucinationCheck(
                phrase=phrase,
                is_hallucination=False,
                stability_score=1.0,
                contradiction_detected=False,
                explanation="Single word - no junction to analyze"
            )

        # Analyze each word
        assemblies = [WordAssemblyAnalyzer.analyze(w) for w in words]

        # Check for contradictory terminals between adjacent words
        contradiction_found = False
        contradiction_details = []

        for i in range(len(assemblies) - 1):
            if not assemblies[i].letters or not assemblies[i + 1].letters:
                continue

            terminal1 = assemblies[i].letters[-1].letter
            initial2 = assemblies[i + 1].letters[0].letter

            pair = tuple(sorted([terminal1, initial2]))
            if pair in cls.CONTRADICTORY_TERMINALS or (initial2, terminal1) in cls.CONTRADICTORY_TERMINALS:
                contradiction_found = True
                contradiction_details.append(
                    f"'{words[i]}' ({terminal1}) -> '{words[i + 1]}' ({initial2})"
                )

        # Calculate overall stability
        if assemblies:
            avg_stability = sum(a.vector.stability_score for a in assemblies) / len(assemblies)
        else:
            avg_stability = 0.5

        # Determine hallucination status
        is_hallucination = contradiction_found and avg_stability < 0.6

        if is_hallucination:
            explanation = (
                f"GEOMETRIC INSTABILITY: Load path contradiction at junction(s): "
                f"{'; '.join(contradiction_details)}. "
                f"Assembly cannot bear semantic load."
            )
        elif contradiction_found:
            explanation = (
                f"WARNING: Potential instability at junction(s): "
                f"{'; '.join(contradiction_details)}. "
                f"Stability score {avg_stability:.2f} provides marginal support."
            )
        else:
            explanation = (
                f"Geometric structure is stable (score: {avg_stability:.2f}). "
                f"No contradictory load paths detected."
            )

        return HallucinationCheck(
            phrase=phrase,
            is_hallucination=is_hallucination,
            stability_score=avg_stability,
            contradiction_detected=contradiction_found,
            explanation=explanation,
        )


# ==================================================================================
# EXPORTS
# ==================================================================================

__all__ = [
    # Word Assembly
    "WordVector",
    "WordAssembly",
    "WordAssemblyAnalyzer",
    # Distortion Analysis
    "DistortionReport",
    "DistortionIndexCalculator",
    # Antonym Analysis
    "AntonymType",
    "AntonymAnalysis",
    "AntonymAnalyzer",
    # Compiler
    "CompilerRegime",
    "CompilationProof",
    "StructuralFailure",
    "KinematicCompiler",
    # Hallucination Detection
    "HallucinationCheck",
    "HallucinationDetector",
]
