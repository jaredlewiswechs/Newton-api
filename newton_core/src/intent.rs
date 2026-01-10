//! Intent vector and inference.
//!
//! The intent vector represents what the user is trying to do.
//! It captures the direction and magnitude of an attempted change.

use crate::linalg::Vector;
use crate::primitives::Delta;
use crate::constants::EPSILON;
use serde::{Serialize, Deserialize};

/// An intent vector representing user intention.
///
/// This captures:
/// - The direction of attempted change
/// - The magnitude (how strongly the user is pushing)
/// - Per-dimension weights (what's important to preserve)
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct IntentVector {
    /// The direction of intent (normalized)
    pub direction: Vector,
    /// The magnitude of intent
    pub magnitude: f64,
    /// Per-dimension importance weights
    pub weights: Vector,
    /// Source of the intent (e.g., "drag", "resize", "keyboard")
    pub source: Option<String>,
}

impl IntentVector {
    /// Create an intent vector from a delta.
    pub fn from_delta(delta: &Delta) -> Self {
        let magnitude = delta.magnitude();
        let direction = if magnitude > EPSILON {
            delta.vector.normalize()
        } else {
            Vector::zeros(delta.vector.dim())
        };

        Self {
            direction,
            magnitude,
            weights: Vector::from_elem(delta.vector.dim(), 1.0),
            source: delta.source.clone(),
        }
    }

    /// Create an intent vector from a raw vector.
    pub fn from_vector(vector: Vector) -> Self {
        let magnitude = vector.norm();
        let direction = if magnitude > EPSILON {
            vector.normalize()
        } else {
            Vector::zeros(vector.dim())
        };

        Self {
            direction,
            magnitude,
            weights: Vector::from_elem(vector.dim(), 1.0),
            source: None,
        }
    }

    /// Create an intent with custom weights.
    pub fn with_weights(vector: Vector, weights: Vector) -> Self {
        let mut intent = Self::from_vector(vector);
        intent.weights = weights;
        intent
    }

    /// Get the full intent vector (direction * magnitude).
    pub fn vector(&self) -> Vector {
        &self.direction * self.magnitude
    }

    /// Get the dimension.
    pub fn dim(&self) -> usize {
        self.direction.dim()
    }

    /// Compute how much of this intent is preserved by a given result.
    ///
    /// Returns a value in [0, 1] where:
    /// - 1.0 = intent fully preserved
    /// - 0.0 = intent completely blocked
    pub fn preserved(&self, original: &Vector, result: &Vector) -> f64 {
        if self.magnitude < EPSILON {
            return 1.0; // No intent to preserve
        }

        let actual_change = result - original;
        let actual_magnitude = actual_change.norm();

        if actual_magnitude < EPSILON {
            return 0.0; // No change happened
        }

        // Compute directional alignment
        let alignment = self.direction.dot(&actual_change.normalize());

        // Compute magnitude ratio (capped at 1.0)
        let magnitude_ratio = (actual_magnitude / self.magnitude).min(1.0);

        // Intent preservation is alignment * magnitude ratio
        // Negative alignment means we went backwards
        (alignment * magnitude_ratio).max(0.0)
    }

    /// Scale the intent by a factor.
    pub fn scale(&self, factor: f64) -> Self {
        Self {
            direction: self.direction.clone(),
            magnitude: self.magnitude * factor,
            weights: self.weights.clone(),
            source: self.source.clone(),
        }
    }

    /// Combine with another intent (e.g., from different input sources).
    pub fn combine(&self, other: &IntentVector) -> Self {
        // Weighted average of directions
        let combined_dir = &(&self.direction * self.magnitude)
            + &(&other.direction * other.magnitude);
        let combined_mag = combined_dir.norm();

        Self::from_vector(combined_dir)
    }
}

/// Infer user intent from a sequence of recent deltas.
///
/// Uses exponential weighting to favor more recent inputs.
pub fn infer_intent(deltas: &[Delta], decay: f64) -> IntentVector {
    if deltas.is_empty() {
        return IntentVector {
            direction: Vector::zeros(2), // Default 2D
            magnitude: 0.0,
            weights: Vector::from_elem(2, 1.0),
            source: None,
        };
    }

    let dim = deltas[0].vector.dim();
    let mut weighted_sum = Vector::zeros(dim);
    let mut total_weight = 0.0;

    for (i, delta) in deltas.iter().rev().enumerate() {
        let weight = decay.powi(i as i32);
        weighted_sum = &weighted_sum + &(&delta.vector * weight);
        total_weight += weight;
    }

    if total_weight > EPSILON {
        weighted_sum = &weighted_sum / total_weight;
    }

    let mut intent = IntentVector::from_vector(weighted_sum);
    intent.source = deltas.last().and_then(|d| d.source.clone());
    intent
}

/// Compute perceptual weights from recent interaction.
///
/// Dimensions that the user has been manipulating get higher weight.
pub fn perceptual_weights(deltas: &[Delta], base_weight: f64, active_boost: f64) -> Vector {
    if deltas.is_empty() {
        return Vector::from_elem(2, base_weight);
    }

    let dim = deltas[0].vector.dim();
    let mut activity = Vector::zeros(dim);

    // Sum absolute changes per dimension
    for delta in deltas {
        for i in 0..dim {
            activity[i] += delta.vector[i].abs();
        }
    }

    // Normalize and apply boost
    let max_activity = activity.iter().cloned().fold(0.0_f64, f64::max);
    if max_activity > EPSILON {
        activity = &activity / max_activity;
    }

    // Create weights: base + activity * boost
    let mut weights = Vector::from_elem(dim, base_weight);
    for i in 0..dim {
        weights[i] += activity[i] * active_boost;
    }

    weights
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_intent_from_delta() {
        let delta = Delta::new(Vector::from_slice(&[3.0, 4.0]));
        let intent = IntentVector::from_delta(&delta);

        assert!((intent.magnitude - 5.0).abs() < EPSILON);
        assert!((intent.direction.norm() - 1.0).abs() < EPSILON);
    }

    #[test]
    fn test_intent_preserved_full() {
        let intent = IntentVector::from_vector(Vector::from_slice(&[10.0, 0.0]));
        let original = Vector::from_slice(&[0.0, 0.0]);
        let result = Vector::from_slice(&[10.0, 0.0]);

        let preserved = intent.preserved(&original, &result);
        assert!((preserved - 1.0).abs() < EPSILON);
    }

    #[test]
    fn test_intent_preserved_partial() {
        let intent = IntentVector::from_vector(Vector::from_slice(&[10.0, 0.0]));
        let original = Vector::from_slice(&[0.0, 0.0]);
        let result = Vector::from_slice(&[5.0, 0.0]); // Only half

        let preserved = intent.preserved(&original, &result);
        assert!((preserved - 0.5).abs() < EPSILON);
    }

    #[test]
    fn test_intent_preserved_blocked() {
        let intent = IntentVector::from_vector(Vector::from_slice(&[10.0, 0.0]));
        let original = Vector::from_slice(&[0.0, 0.0]);
        let result = Vector::from_slice(&[0.0, 0.0]); // No change

        let preserved = intent.preserved(&original, &result);
        assert!(preserved < EPSILON);
    }

    #[test]
    fn test_intent_preserved_opposite() {
        let intent = IntentVector::from_vector(Vector::from_slice(&[10.0, 0.0]));
        let original = Vector::from_slice(&[0.0, 0.0]);
        let result = Vector::from_slice(&[-5.0, 0.0]); // Opposite direction

        let preserved = intent.preserved(&original, &result);
        assert!(preserved < EPSILON); // Should be 0 or negative clamped to 0
    }

    #[test]
    fn test_infer_intent() {
        let deltas = vec![
            Delta::new(Vector::from_slice(&[1.0, 0.0])),
            Delta::new(Vector::from_slice(&[2.0, 0.0])),
            Delta::new(Vector::from_slice(&[3.0, 0.0])),
        ];

        let intent = infer_intent(&deltas, 0.9);

        // Should point in positive x direction
        assert!(intent.direction[0] > 0.0);
        assert!(intent.direction[1].abs() < EPSILON);
    }

    #[test]
    fn test_perceptual_weights() {
        let deltas = vec![
            Delta::new(Vector::from_slice(&[10.0, 1.0])),
            Delta::new(Vector::from_slice(&[10.0, 1.0])),
        ];

        let weights = perceptual_weights(&deltas, 1.0, 5.0);

        // Dimension 0 was more active, should have higher weight
        assert!(weights[0] > weights[1]);
    }
}
