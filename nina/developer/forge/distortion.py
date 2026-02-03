#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
DISTORTION METRIC (Paper Section 10.2)

Geometry mismatch as a type error.

Define:
    g(w): glyph-derived mechanical signature of a word/command
    v(a): physics/action vector of the actual commanded behavior
    
Define distortion:
    D(w, a) = d(v(a), g(w))
    
where d is a metric or divergence.

Rule (GeometryMismatchError):
    If D(w,a) > θ(R), reject as inadmissible and suggest alternatives
    with lower distortion.

From "Newton as a Verified Computation Substrate":
> This formalizes the "TRIM vs DIVE" principle as a semantic soundness 
> gate: language must match physics under the active regime.

═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
import math


class GeometryMismatchError(Exception):
    """
    Raised when distortion D(w,a) exceeds threshold θ(R).
    
    This is the semantic soundness gate: language must match physics.
    """
    
    def __init__(
        self, 
        word: str, 
        action: str,
        distortion: float,
        threshold: float,
        suggestions: Optional[List[str]] = None
    ):
        self.word = word
        self.action = action
        self.distortion = distortion
        self.threshold = threshold
        self.suggestions = suggestions or []
        
        msg = (
            f"GeometryMismatchError: D('{word}', '{action}') = {distortion:.3f} "
            f"> θ = {threshold:.3f}"
        )
        if self.suggestions:
            msg += f"\n  Suggestions: {', '.join(self.suggestions)}"
        
        super().__init__(msg)


@dataclass
class KinematicSignature:
    """
    The glyph-derived mechanical signature g(w) of a word.
    
    Based on kinematic linguistics - each symbol encodes:
    - weight: how much it moves the trajectory (0-1)
    - curvature: how it bends (-1 to 1)
    - commit_strength: how close to commitment/terminus (0-1)
    - is_action: whether this is an action verb
    - force_vector: direction and magnitude of implied force
    """
    word: str
    weight: float = 0.5
    curvature: float = 0.0
    commit_strength: float = 0.5
    is_action: bool = False
    force_vector: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # x, y, z
    
    def magnitude(self) -> float:
        """Magnitude of the force vector."""
        return math.sqrt(sum(x**2 for x in self.force_vector))
    
    def as_vector(self) -> Tuple[float, ...]:
        """Return full signature as a vector for distance computation."""
        return (
            self.weight,
            self.curvature,
            self.commit_strength,
            float(self.is_action),
            *self.force_vector
        )


@dataclass
class PhysicsVector:
    """
    The physics/action vector v(a) of actual commanded behavior.
    
    This represents what the action actually DOES in physical terms:
    - force: magnitude of physical force applied
    - direction: unit vector of force direction
    - reversibility: how reversible is this action (0=irreversible, 1=fully reversible)
    - locality: how localized is the effect (0=global, 1=point)
    - time_scale: characteristic time of the action (seconds)
    """
    action: str
    force: float = 0.0
    direction: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    reversibility: float = 1.0
    locality: float = 1.0
    time_scale: float = 1.0
    
    def as_vector(self) -> Tuple[float, ...]:
        """Return physics as a vector for distance computation."""
        # Normalize force to 0-1 range (assuming max force ~1000)
        normalized_force = min(self.force / 1000.0, 1.0)
        return (
            normalized_force,
            *self.direction,
            self.reversibility,
            self.locality,
            min(self.time_scale / 100.0, 1.0)  # Normalize time
        )


class DistortionMetric:
    """
    Computes distortion D(w, a) = d(v(a), g(w)).
    
    This measures the semantic distance between what a word MEANS
    (its glyph-derived mechanical signature) and what an action DOES
    (its physics vector).
    
    Example:
        "TRIM" has low force, high reversibility, local effect
        "DIVE" has high force, low reversibility, trajectory change
        
        If you say "TRIM the hedge" → low distortion (match)
        If you say "TRIM into the water" → high distortion (mismatch!)
        
        The system suggests "DIVE into the water" as a lower-distortion alternative.
    """
    
    def __init__(self):
        # Word signature database
        self._signatures: Dict[str, KinematicSignature] = {}
        # Action physics database  
        self._physics: Dict[str, PhysicsVector] = {}
        # Initialize with built-in vocabulary
        self._init_vocabulary()
    
    def _init_vocabulary(self):
        """Initialize built-in word signatures and action physics."""
        
        # === WORD SIGNATURES (what words MEAN mechanically) ===
        
        # Gentle/precise actions
        self._signatures["trim"] = KinematicSignature(
            word="trim", weight=0.3, curvature=0.1, commit_strength=0.4,
            is_action=True, force_vector=(0.1, 0.0, 0.0)
        )
        self._signatures["adjust"] = KinematicSignature(
            word="adjust", weight=0.2, curvature=0.2, commit_strength=0.3,
            is_action=True, force_vector=(0.1, 0.1, 0.0)
        )
        self._signatures["nudge"] = KinematicSignature(
            word="nudge", weight=0.2, curvature=0.0, commit_strength=0.3,
            is_action=True, force_vector=(0.15, 0.0, 0.0)
        )
        
        # Forceful/irreversible actions
        self._signatures["dive"] = KinematicSignature(
            word="dive", weight=0.8, curvature=-0.7, commit_strength=0.9,
            is_action=True, force_vector=(0.0, 0.0, -0.8)
        )
        self._signatures["plunge"] = KinematicSignature(
            word="plunge", weight=0.9, curvature=-0.8, commit_strength=0.95,
            is_action=True, force_vector=(0.0, 0.0, -0.9)
        )
        self._signatures["crash"] = KinematicSignature(
            word="crash", weight=1.0, curvature=0.0, commit_strength=1.0,
            is_action=True, force_vector=(0.9, 0.0, 0.0)
        )
        self._signatures["delete"] = KinematicSignature(
            word="delete", weight=0.8, curvature=0.0, commit_strength=0.9,
            is_action=True, force_vector=(0.0, 0.0, 0.0)
        )
        
        # Movement actions
        self._signatures["walk"] = KinematicSignature(
            word="walk", weight=0.4, curvature=0.0, commit_strength=0.5,
            is_action=True, force_vector=(0.3, 0.0, 0.0)
        )
        self._signatures["run"] = KinematicSignature(
            word="run", weight=0.6, curvature=0.0, commit_strength=0.6,
            is_action=True, force_vector=(0.6, 0.0, 0.0)
        )
        self._signatures["jump"] = KinematicSignature(
            word="jump", weight=0.7, curvature=0.5, commit_strength=0.7,
            is_action=True, force_vector=(0.0, 0.5, 0.3)
        )
        
        # Information actions
        self._signatures["verify"] = KinematicSignature(
            word="verify", weight=0.3, curvature=0.0, commit_strength=0.6,
            is_action=True, force_vector=(0.0, 0.0, 0.0)
        )
        self._signatures["check"] = KinematicSignature(
            word="check", weight=0.2, curvature=0.0, commit_strength=0.5,
            is_action=True, force_vector=(0.0, 0.0, 0.0)
        )
        self._signatures["calculate"] = KinematicSignature(
            word="calculate", weight=0.4, curvature=0.0, commit_strength=0.7,
            is_action=True, force_vector=(0.0, 0.0, 0.0)
        )
        
        # === ACTION PHYSICS (what actions actually DO) ===
        
        # Physical movements
        self._physics["enter_water_gentle"] = PhysicsVector(
            action="enter_water_gentle", force=10.0, direction=(0.0, 0.0, -0.3),
            reversibility=0.9, locality=0.8, time_scale=2.0
        )
        self._physics["enter_water_forceful"] = PhysicsVector(
            action="enter_water_forceful", force=500.0, direction=(0.0, 0.0, -0.9),
            reversibility=0.3, locality=0.5, time_scale=0.5
        )
        self._physics["cut_precise"] = PhysicsVector(
            action="cut_precise", force=20.0, direction=(0.1, 0.0, 0.0),
            reversibility=0.2, locality=0.95, time_scale=1.0
        )
        self._physics["cut_rough"] = PhysicsVector(
            action="cut_rough", force=100.0, direction=(0.5, 0.0, 0.0),
            reversibility=0.1, locality=0.6, time_scale=0.5
        )
        
        # Data operations  
        self._physics["data_read"] = PhysicsVector(
            action="data_read", force=0.0, direction=(0.0, 0.0, 0.0),
            reversibility=1.0, locality=1.0, time_scale=0.01
        )
        self._physics["data_write"] = PhysicsVector(
            action="data_write", force=5.0, direction=(0.0, 0.0, 0.0),
            reversibility=0.8, locality=1.0, time_scale=0.01
        )
        self._physics["data_delete"] = PhysicsVector(
            action="data_delete", force=50.0, direction=(0.0, 0.0, 0.0),
            reversibility=0.1, locality=0.9, time_scale=0.01
        )
    
    def get_signature(self, word: str) -> KinematicSignature:
        """Get or compute the kinematic signature for a word."""
        word_lower = word.lower()
        if word_lower in self._signatures:
            return self._signatures[word_lower]
        
        # Generate default signature from word properties
        return self._compute_default_signature(word)
    
    def _compute_default_signature(self, word: str) -> KinematicSignature:
        """Compute a default signature from word properties."""
        # Use simple heuristics based on word structure
        word_lower = word.lower()
        length = len(word)
        
        # Longer words tend to be more complex/forceful
        weight = min(length / 10.0, 1.0)
        
        # Words ending in certain patterns suggest action
        is_action = word_lower.endswith(('e', 'ed', 'ing', 'ify', 'ize'))
        
        # Words with certain letters suggest force
        force_letters = set('bpdtkgq')
        force_count = sum(1 for c in word_lower if c in force_letters)
        force_x = force_count / max(length, 1)
        
        return KinematicSignature(
            word=word,
            weight=weight,
            curvature=0.0,
            commit_strength=0.5,
            is_action=is_action,
            force_vector=(force_x, 0.0, 0.0)
        )
    
    def get_physics(self, action: str) -> PhysicsVector:
        """Get or compute the physics vector for an action."""
        if action in self._physics:
            return self._physics[action]
        
        # Return neutral physics for unknown actions
        return PhysicsVector(action=action)
    
    def compute_distortion(
        self, 
        word: str, 
        action: str,
        metric: str = "euclidean"
    ) -> float:
        """
        Compute distortion D(w, a) = d(v(a), g(w)).
        
        Args:
            word: The word/command
            action: The actual action being performed
            metric: Distance metric to use ("euclidean", "cosine", "manhattan")
            
        Returns:
            Distortion value (0.0 = perfect match, higher = more mismatch)
        """
        sig = self.get_signature(word)
        phys = self.get_physics(action)
        
        sig_vec = sig.as_vector()
        phys_vec = phys.as_vector()
        
        # Pad vectors to same length
        max_len = max(len(sig_vec), len(phys_vec))
        sig_vec = sig_vec + (0.0,) * (max_len - len(sig_vec))
        phys_vec = phys_vec + (0.0,) * (max_len - len(phys_vec))
        
        if metric == "euclidean":
            return self._euclidean_distance(sig_vec, phys_vec)
        elif metric == "cosine":
            return self._cosine_distance(sig_vec, phys_vec)
        elif metric == "manhattan":
            return self._manhattan_distance(sig_vec, phys_vec)
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def _euclidean_distance(self, v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
        """Euclidean distance between two vectors."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))
    
    def _cosine_distance(self, v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
        """Cosine distance (1 - cosine similarity) between two vectors."""
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a ** 2 for a in v1))
        mag2 = math.sqrt(sum(b ** 2 for b in v2))
        
        if mag1 == 0 or mag2 == 0:
            return 1.0  # Maximum distance if either vector is zero
        
        similarity = dot / (mag1 * mag2)
        return 1.0 - similarity
    
    def _manhattan_distance(self, v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
        """Manhattan distance between two vectors."""
        return sum(abs(a - b) for a, b in zip(v1, v2))
    
    def check_admissibility(
        self,
        word: str,
        action: str,
        threshold: float,
        suggest_alternatives: bool = True
    ) -> Tuple[bool, float, List[str]]:
        """
        Check if word-action pairing is admissible under threshold.
        
        Args:
            word: The word/command
            action: The actual action
            threshold: Maximum allowed distortion θ(R)
            suggest_alternatives: Whether to find alternative words
            
        Returns:
            (is_admissible, distortion, suggestions)
        """
        distortion = self.compute_distortion(word, action)
        
        suggestions = []
        if distortion > threshold and suggest_alternatives:
            suggestions = self.suggest_alternatives(action, threshold)
        
        return distortion <= threshold, distortion, suggestions
    
    def suggest_alternatives(
        self, 
        action: str, 
        max_distortion: float,
        limit: int = 5
    ) -> List[str]:
        """
        Suggest alternative words that better match the action.
        
        Returns words sorted by distortion (lowest first).
        """
        candidates = []
        
        for word in self._signatures.keys():
            distortion = self.compute_distortion(word, action)
            if distortion <= max_distortion * 2:  # Include some over threshold
                candidates.append((word, distortion))
        
        # Sort by distortion
        candidates.sort(key=lambda x: x[1])
        
        return [word for word, _ in candidates[:limit]]
    
    def verify_or_raise(
        self,
        word: str,
        action: str,
        threshold: float
    ) -> float:
        """
        Verify word-action admissibility, raising GeometryMismatchError if not.
        
        Returns:
            The distortion value if admissible
            
        Raises:
            GeometryMismatchError if distortion exceeds threshold
        """
        is_admissible, distortion, suggestions = self.check_admissibility(
            word, action, threshold
        )
        
        if not is_admissible:
            raise GeometryMismatchError(
                word=word,
                action=action,
                distortion=distortion,
                threshold=threshold,
                suggestions=suggestions
            )
        
        return distortion
    
    def register_signature(self, word: str, signature: KinematicSignature) -> None:
        """Register a custom word signature."""
        self._signatures[word.lower()] = signature
    
    def register_physics(self, action: str, physics: PhysicsVector) -> None:
        """Register a custom action physics."""
        self._physics[action] = physics


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_metric: Optional[DistortionMetric] = None

def get_distortion_metric() -> DistortionMetric:
    """Get the global distortion metric instance."""
    global _metric
    if _metric is None:
        _metric = DistortionMetric()
    return _metric


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("DISTORTION METRIC TEST")
    print("D(w, a) = d(v(a), g(w))")
    print("=" * 70)
    
    metric = DistortionMetric()
    threshold = 0.5
    
    # Test cases: (word, action, expected_admissible)
    test_cases = [
        ("trim", "cut_precise", True),      # Match: gentle word, precise cut
        ("trim", "enter_water_forceful", False),  # Mismatch: gentle word, forceful action
        ("dive", "enter_water_forceful", True),   # Match: forceful word, forceful action
        ("dive", "cut_precise", False),     # Mismatch: forceful word, gentle action
        ("delete", "data_delete", True),    # Match: delete means delete
        ("nudge", "data_write", True),      # Match: gentle word, gentle action
    ]
    
    print(f"\nThreshold θ = {threshold}\n")
    
    for word, action, expected in test_cases:
        admissible, distortion, suggestions = metric.check_admissibility(
            word, action, threshold
        )
        
        status = "✓" if admissible == expected else "✗"
        match_str = "ADMIT" if admissible else "REJECT"
        
        print(f"{status} D('{word}', '{action}') = {distortion:.3f} → {match_str}")
        if suggestions:
            print(f"   Suggestions: {', '.join(suggestions)}")
    
    # Test GeometryMismatchError
    print(f"\n{'=' * 70}")
    print("Testing GeometryMismatchError...")
    print("=" * 70)
    
    try:
        metric.verify_or_raise("trim", "enter_water_forceful", threshold=0.3)
    except GeometryMismatchError as e:
        print(f"\n{e}")
