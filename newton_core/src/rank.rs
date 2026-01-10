//! Distance metrics and stable ordering for candidate ranking.
//!
//! Provides deterministic ranking of suggestions based on multiple criteria.

use crate::linalg::Vector;
use crate::primitives::FGState;
use crate::intent::IntentVector;
use crate::constants::TOLERANCE;
#[allow(unused_imports)]
use crate::constants::EPSILON;
use std::cmp::Ordering;

/// Ranking criteria for suggestions.
#[derive(Clone, Debug)]
pub struct RankingCriteria {
    /// Weight for distance to intent
    pub intent_weight: f64,
    /// Weight for constraint satisfaction margin
    pub margin_weight: f64,
    /// Weight for staying close to original position
    pub stability_weight: f64,
}

impl Default for RankingCriteria {
    fn default() -> Self {
        Self {
            intent_weight: 1.0,
            margin_weight: 0.5,
            stability_weight: 0.3,
        }
    }
}

/// A scored candidate for ranking.
#[derive(Clone, Debug)]
pub struct ScoredCandidate {
    /// The candidate point
    pub point: Vector,
    /// Score (lower is better)
    pub score: f64,
    /// Individual score components for debugging
    pub components: ScoreComponents,
}

/// Individual components of a candidate's score.
#[derive(Clone, Debug, Default)]
pub struct ScoreComponents {
    /// Distance from intended position
    pub intent_distance: f64,
    /// Constraint margin (negative = inside, higher magnitude = better)
    pub margin: f64,
    /// Distance from original position
    pub stability_distance: f64,
}

/// Rank candidates by multiple criteria.
///
/// Returns candidates sorted by score (lower is better), with ties broken
/// lexicographically for determinism.
pub fn rank_candidates(
    candidates: Vec<Vector>,
    intent: &IntentVector,
    original: &Vector,
    criteria: &RankingCriteria,
) -> Vec<ScoredCandidate> {
    let intended_position = original + &intent.vector();

    let mut scored: Vec<ScoredCandidate> = candidates
        .into_iter()
        .map(|point| {
            let components = ScoreComponents {
                intent_distance: point.distance(&intended_position),
                margin: 0.0, // Would need constraints to compute
                stability_distance: point.distance(original),
            };

            let score = criteria.intent_weight * components.intent_distance
                + criteria.stability_weight * components.stability_distance;

            ScoredCandidate {
                point,
                score,
                components,
            }
        })
        .collect();

    // Sort by score, then lexicographically for ties
    scored.sort_by(|a, b| {
        match a.score.partial_cmp(&b.score) {
            Some(Ordering::Equal) => a.point.lexicographic_cmp(&b.point),
            Some(ord) => ord,
            None => a.point.lexicographic_cmp(&b.point),
        }
    });

    scored
}

/// Stable sort that preserves order for equal elements.
///
/// Uses lexicographic comparison as a tiebreaker for determinism.
pub fn stable_sort_by_distance(points: &mut [Vector], reference: &Vector) {
    points.sort_by(|a, b| {
        let dist_a = reference.distance(a);
        let dist_b = reference.distance(b);
        match dist_a.partial_cmp(&dist_b) {
            Some(Ordering::Equal) => a.lexicographic_cmp(b),
            Some(ord) => ord,
            None => a.lexicographic_cmp(b),
        }
    });
}

/// Check if two scores are effectively equal (within tolerance).
pub fn scores_equal(a: f64, b: f64) -> bool {
    (a - b).abs() < TOLERANCE
}

/// Compute weighted distance incorporating intent weights.
pub fn weighted_intent_distance(
    point: &Vector,
    target: &Vector,
    weights: &Vector,
) -> f64 {
    let diff = point - target;
    let weighted = diff.component_mul(weights);
    weighted.norm()
}

/// Compute a quality score for a suggestion based on FGState.
///
/// Lower is better:
/// - Valid = 0.0
/// - Slack with high margin = 0.1
/// - Slack with low margin = 0.3
/// - Exact = 0.5
/// - Finfr = 1.0+ (should not happen for valid suggestions)
pub fn fg_quality_score(fg_state: &FGState) -> f64 {
    match fg_state {
        FGState::Valid => 0.0,
        FGState::Slack { margin } => 0.1 + 0.2 * (1.0 - margin),
        FGState::Exact => 0.5,
        FGState::Finfr { excess } => 1.0 + excess,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rank_candidates_basic() {
        let candidates = vec![
            Vector::from_slice(&[10.0, 0.0]),
            Vector::from_slice(&[5.0, 0.0]),
            Vector::from_slice(&[8.0, 0.0]),
        ];

        let intent = IntentVector::from_vector(Vector::from_slice(&[10.0, 0.0]));
        let original = Vector::from_slice(&[0.0, 0.0]);
        let criteria = RankingCriteria::default();

        let ranked = rank_candidates(candidates, &intent, &original, &criteria);

        // Should be sorted by score
        for i in 1..ranked.len() {
            assert!(ranked[i - 1].score <= ranked[i].score + EPSILON);
        }
    }

    #[test]
    fn test_rank_candidates_deterministic() {
        let candidates = vec![
            Vector::from_slice(&[10.0, 0.0]),
            Vector::from_slice(&[5.0, 0.0]),
            Vector::from_slice(&[8.0, 0.0]),
        ];

        let intent = IntentVector::from_vector(Vector::from_slice(&[10.0, 0.0]));
        let original = Vector::from_slice(&[0.0, 0.0]);
        let criteria = RankingCriteria::default();

        let ranked1 = rank_candidates(candidates.clone(), &intent, &original, &criteria);
        let ranked2 = rank_candidates(candidates, &intent, &original, &criteria);

        assert_eq!(ranked1.len(), ranked2.len());
        for (r1, r2) in ranked1.iter().zip(ranked2.iter()) {
            for i in 0..r1.point.dim() {
                assert_eq!(r1.point[i].to_bits(), r2.point[i].to_bits());
            }
        }
    }

    #[test]
    fn test_stable_sort_ties() {
        let mut points = vec![
            Vector::from_slice(&[5.0, 1.0]),
            Vector::from_slice(&[5.0, 2.0]),
            Vector::from_slice(&[5.0, 0.0]),
        ];

        let reference = Vector::from_slice(&[0.0, 0.0]);
        stable_sort_by_distance(&mut points, &reference);

        // All have same distance to origin, should be sorted lexicographically
        // by second component: 0.0, 1.0, 2.0
        assert!((points[0][1] - 0.0).abs() < EPSILON);
        assert!((points[1][1] - 1.0).abs() < EPSILON);
        assert!((points[2][1] - 2.0).abs() < EPSILON);
    }

    #[test]
    fn test_fg_quality_score() {
        assert!(fg_quality_score(&FGState::Valid) < fg_quality_score(&FGState::Exact));
        assert!(fg_quality_score(&FGState::Exact) < fg_quality_score(&FGState::Finfr { excess: 0.1 }));

        let slack_high = FGState::Slack { margin: 0.9 };
        let slack_low = FGState::Slack { margin: 0.1 };
        assert!(fg_quality_score(&slack_high) < fg_quality_score(&slack_low));
    }
}
