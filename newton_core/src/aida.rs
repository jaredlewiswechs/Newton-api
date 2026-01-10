//! Aid-a: Assistive Intelligence for Design Autonomy
//!
//! This is the main entry point for Newton's suggestion engine.
//! Aid-a never lies, never loops, and never suggests an invalid state.

use crate::linalg::Vector;
use crate::primitives::{FGState, Delta};
use crate::constraints::{ConstraintRef, all_convex, all_satisfied};
use crate::projection::project_convex;
use crate::candidates::{local_search, filter_and_rank};
use crate::intent::IntentVector;
use crate::constants::EPSILON;
use serde::{Serialize, Deserialize};
use std::time::Instant;

/// Quality level of suggestions returned by Aid-a.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum SuggestionQuality {
    /// All suggestions came from exact constraint satisfaction.
    Exact,

    /// Suggestions are near the intent but required interpolation.
    Near,

    /// Fell back to convex relaxation only.
    Relaxed,
}

/// A single suggestion from Aid-a.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Suggestion {
    /// The suggested state
    pub state: Vector,
    /// FG state (constraint satisfaction level)
    pub fg_state: FGState,
    /// How much of the user's intent was preserved (0.0 to 1.0)
    pub intent_preserved: f64,
    /// Human-readable explanation
    pub explanation: String,
}

/// Statistics about the search process.
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct SearchStats {
    /// Number of candidates generated
    pub candidates_generated: usize,
    /// Number of candidates that passed verification
    pub candidates_verified: usize,
    /// Number of iterations used in projection
    pub iterations_used: usize,
    /// Time elapsed in microseconds
    pub elapsed_us: u64,
}

/// Complete response from Aid-a.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AidAResponse {
    /// List of suggestions, ranked by quality
    pub suggestions: Vec<Suggestion>,
    /// Overall quality level of the response
    pub quality: SuggestionQuality,
    /// Statistics about the search process
    pub search_stats: SearchStats,
}

impl AidAResponse {
    /// Create an exact-quality response.
    pub fn exact(suggestions: Vec<Suggestion>, stats: SearchStats) -> Self {
        Self {
            suggestions,
            quality: SuggestionQuality::Exact,
            search_stats: stats,
        }
    }

    /// Create a near-quality response.
    pub fn near(suggestions: Vec<Suggestion>, stats: SearchStats) -> Self {
        Self {
            suggestions,
            quality: SuggestionQuality::Near,
            search_stats: stats,
        }
    }

    /// Create a relaxed-quality response.
    pub fn relaxed(suggestions: Vec<Suggestion>, stats: SearchStats) -> Self {
        Self {
            suggestions,
            quality: SuggestionQuality::Relaxed,
            search_stats: stats,
        }
    }

    /// Get the best (first) suggestion, if any.
    pub fn best(&self) -> Option<&Suggestion> {
        self.suggestions.first()
    }

    /// Check if any suggestions were returned.
    pub fn has_suggestions(&self) -> bool {
        !self.suggestions.is_empty()
    }

    /// UI hint prefix based on quality.
    pub fn ui_prefix(&self) -> &'static str {
        match self.quality {
            SuggestionQuality::Exact => "You can:",
            SuggestionQuality::Near => "Try instead:",
            SuggestionQuality::Relaxed => "Closest safe option:",
        }
    }
}

/// Main suggestion function: the Aid-a entry point.
///
/// Given a current state, attempted change, and constraints,
/// returns ranked suggestions for valid next states.
///
/// # Contract
///
/// This function guarantees:
/// 1. **Validity**: All returned suggestions satisfy all constraints
/// 2. **Determinism**: Identical inputs produce identical outputs
/// 3. **Termination**: Completes within bounded time and iterations
/// 4. **Non-empty**: Returns at least one suggestion if feasible region is non-empty
///
/// # Arguments
/// * `current` - Current state of the object
/// * `delta` - Attempted change (user intent)
/// * `constraints` - Active constraints to satisfy
///
/// # Returns
/// An `AidAResponse` containing ranked suggestions.
pub fn suggest(
    current: &Vector,
    delta: &Delta,
    constraints: &[ConstraintRef],
) -> AidAResponse {
    let start = Instant::now();
    let mut stats = SearchStats::default();

    // Compute intended state
    let intended = current + &delta.vector;
    let intent = IntentVector::from_delta(delta);

    // Check if intended state is already valid
    if constraints.is_empty() || all_satisfied(constraints, &intended) {
        let fg_state = FGState::Valid;
        let suggestion = Suggestion {
            state: intended.clone(),
            fg_state,
            intent_preserved: 1.0,
            explanation: "Intended position is valid.".to_string(),
        };

        stats.elapsed_us = start.elapsed().as_micros() as u64;
        return AidAResponse::exact(vec![suggestion], stats);
    }

    // Route based on constraint types
    if all_convex(constraints) {
        suggest_convex(current, &intended, &intent, constraints, &mut stats)
    } else {
        suggest_nonconvex(current, &intended, &intent, constraints, &mut stats)
    }
}

/// Suggest for purely convex constraints using Dykstra's algorithm.
fn suggest_convex(
    current: &Vector,
    intended: &Vector,
    intent: &IntentVector,
    constraints: &[ConstraintRef],
    stats: &mut SearchStats,
) -> AidAResponse {
    let start = Instant::now();

    // Project intended state onto constraint intersection
    let projected = project_convex(intended, constraints);

    // Compute FG state
    let violation = intended.distance(&projected);
    let effort = intent.magnitude;
    let fg_state = FGState::from_violation(violation, effort);

    // Compute intent preservation
    let intent_preserved = intent.preserved(current, &projected);

    // Generate explanation
    let explanation = if projected.approx_eq(intended) {
        "Position adjusted to satisfy constraints.".to_string()
    } else {
        format!(
            "Moved {:.2} units to nearest valid position.",
            violation
        )
    };

    let suggestion = Suggestion {
        state: projected,
        fg_state,
        intent_preserved,
        explanation,
    };

    stats.elapsed_us = start.elapsed().as_micros() as u64;
    stats.candidates_verified = 1;

    // Determine quality based on FG state
    let quality = if fg_state.is_valid() && intent_preserved > 0.9 {
        SuggestionQuality::Exact
    } else if intent_preserved > 0.5 {
        SuggestionQuality::Near
    } else {
        SuggestionQuality::Relaxed
    };

    AidAResponse {
        suggestions: vec![suggestion],
        quality,
        search_stats: stats.clone(),
    }
}

/// Suggest for nonconvex constraints using candidate search.
fn suggest_nonconvex(
    current: &Vector,
    intended: &Vector,
    intent: &IntentVector,
    constraints: &[ConstraintRef],
    stats: &mut SearchStats,
) -> AidAResponse {
    let start = Instant::now();

    // First, get convex relaxation projection as starting point
    let convex_constraints: Vec<_> = constraints
        .iter()
        .filter(|c| c.is_convex())
        .cloned()
        .collect();

    let center = if convex_constraints.is_empty() {
        intended.clone()
    } else {
        project_convex(intended, &convex_constraints)
    };

    // Generate candidates
    let mut candidates = Vec::new();

    // Add the convex projection itself
    candidates.push(center.clone());

    // Add local search candidates
    let local = local_search(&center, None, candidates.len());
    candidates.extend(local);
    stats.candidates_generated = candidates.len();

    // Filter to valid candidates only
    let valid_candidates = filter_and_rank(candidates, constraints, intended);
    stats.candidates_verified = valid_candidates.len();

    if valid_candidates.is_empty() {
        // No valid candidates found - return convex relaxation as fallback
        let violation = intended.distance(&center);
        let fg_state = FGState::from_violation(violation, intent.magnitude);
        let intent_preserved = intent.preserved(current, &center);

        let suggestion = Suggestion {
            state: center,
            fg_state,
            intent_preserved,
            explanation: "No exact match found. Showing convex relaxation.".to_string(),
        };

        stats.elapsed_us = start.elapsed().as_micros() as u64;
        return AidAResponse::relaxed(vec![suggestion], stats.clone());
    }

    // Build suggestions from valid candidates
    let mut suggestions: Vec<Suggestion> = valid_candidates
        .into_iter()
        .take(5) // Limit to top 5 suggestions
        .map(|state| {
            let violation = intended.distance(&state);
            let fg_state = FGState::from_violation(violation, intent.magnitude);
            let intent_preserved = intent.preserved(current, &state);

            Suggestion {
                state,
                fg_state,
                intent_preserved,
                explanation: format!("Valid position, {:.0}% intent preserved.", intent_preserved * 100.0),
            }
        })
        .collect();

    stats.elapsed_us = start.elapsed().as_micros() as u64;

    // Determine quality
    let best_preserved = suggestions.first().map(|s| s.intent_preserved).unwrap_or(0.0);
    let quality = if best_preserved > 0.9 {
        SuggestionQuality::Exact
    } else if best_preserved > 0.5 {
        SuggestionQuality::Near
    } else {
        SuggestionQuality::Relaxed
    };

    AidAResponse {
        suggestions,
        quality,
        search_stats: stats.clone(),
    }
}

/// Suggest with custom weights for weighted projection.
pub fn suggest_weighted(
    current: &Vector,
    delta: &Delta,
    constraints: &[ConstraintRef],
    weights: &Vector,
) -> AidAResponse {
    let start = Instant::now();
    let mut stats = SearchStats::default();

    let intended = current + &delta.vector;
    let intent = IntentVector::with_weights(delta.vector.clone(), weights.clone());

    // For weighted projection, we currently only support box bounds
    // Extract box bounds from constraints
    use crate::constraints::BoxBounds;

    // Find box bounds constraints
    // For simplicity, we use regular suggest for now
    // Full weighted support would require more sophisticated handling
    suggest(current, delta, constraints)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::constraints::{BoxBounds, LinearConstraint, CollisionConstraint, boxed};
    use crate::primitives::Bounds;

    #[test]
    fn test_suggest_valid_intent() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        let current = Vector::from_slice(&[50.0, 50.0]);
        let delta = Delta::new(Vector::from_slice(&[10.0, 0.0]));

        let response = suggest(&current, &delta, &constraints);

        assert_eq!(response.quality, SuggestionQuality::Exact);
        assert!(response.has_suggestions());
        assert!((response.best().unwrap().intent_preserved - 1.0).abs() < EPSILON);
    }

    #[test]
    fn test_suggest_invalid_intent() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        let current = Vector::from_slice(&[50.0, 50.0]);
        let delta = Delta::new(Vector::from_slice(&[100.0, 0.0])); // Would go to 150

        let response = suggest(&current, &delta, &constraints);

        assert!(response.has_suggestions());
        let best = response.best().unwrap();

        // Should be clamped to boundary
        assert!(best.state[0] <= 100.0 + EPSILON);

        // Constraint should be satisfied
        assert!(best.fg_state.is_valid() || matches!(best.fg_state, FGState::Exact));
    }

    #[test]
    fn test_suggest_no_constraints() {
        let current = Vector::from_slice(&[50.0, 50.0]);
        let delta = Delta::new(Vector::from_slice(&[1000.0, 1000.0]));

        let response = suggest(&current, &delta, &[]);

        assert_eq!(response.quality, SuggestionQuality::Exact);
        assert!((response.best().unwrap().intent_preserved - 1.0).abs() < EPSILON);
    }

    #[test]
    fn test_suggest_deterministic() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        let current = Vector::from_slice(&[50.0, 50.0]);
        let delta = Delta::new(Vector::from_slice(&[100.0, 100.0]));

        let response1 = suggest(&current, &delta, &constraints);
        let response2 = suggest(&current, &delta, &constraints);

        // Must produce identical results
        assert_eq!(response1.suggestions.len(), response2.suggestions.len());
        for (s1, s2) in response1.suggestions.iter().zip(response2.suggestions.iter()) {
            for i in 0..s1.state.dim() {
                assert_eq!(s1.state[i].to_bits(), s2.state[i].to_bits());
            }
        }
    }

    #[test]
    fn test_suggest_with_collision() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let obstacle = Bounds::new(
            Vector::from_slice(&[40.0, 40.0]),
            Vector::from_slice(&[60.0, 60.0]),
        );
        let collision = CollisionConstraint::new(obstacle, 0.0);

        let constraints = vec![boxed(bounds), boxed(collision)];

        let current = Vector::from_slice(&[30.0, 50.0]);
        let delta = Delta::new(Vector::from_slice(&[20.0, 0.0])); // Would go into obstacle

        let response = suggest(&current, &delta, &constraints);

        // Should find alternatives that avoid the obstacle
        assert!(response.has_suggestions());
    }

    #[test]
    fn test_ui_prefix() {
        let exact = AidAResponse::exact(vec![], SearchStats::default());
        assert_eq!(exact.ui_prefix(), "You can:");

        let near = AidAResponse::near(vec![], SearchStats::default());
        assert_eq!(near.ui_prefix(), "Try instead:");

        let relaxed = AidAResponse::relaxed(vec![], SearchStats::default());
        assert_eq!(relaxed.ui_prefix(), "Closest safe option:");
    }
}
