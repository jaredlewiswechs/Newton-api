//! Diff generation and explanation formatting.
//!
//! Generates human-readable explanations for why a suggestion was made
//! and what changed from the original state.

use crate::linalg::Vector;
use crate::primitives::FGState;
use crate::constraints::ConstraintRef;
use crate::constants::TOLERANCE;
#[allow(unused_imports)]
use crate::constants::EPSILON;
use serde::{Serialize, Deserialize};

/// A diff between two states.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct StateDiff {
    /// Original state
    pub original: Vector,
    /// New state
    pub suggested: Vector,
    /// Per-dimension changes
    pub changes: Vec<DimensionChange>,
    /// Overall distance moved
    pub total_distance: f64,
}

/// A change in a single dimension.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DimensionChange {
    /// Dimension index
    pub dimension: usize,
    /// Dimension name (if known)
    pub name: Option<String>,
    /// Original value
    pub original: f64,
    /// New value
    pub suggested: f64,
    /// Change amount (can be negative)
    pub delta: f64,
}

impl StateDiff {
    /// Create a diff between two states.
    pub fn new(original: Vector, suggested: Vector) -> Self {
        let dim = original.dim();
        let mut changes = Vec::new();

        for i in 0..dim {
            let delta = suggested[i] - original[i];
            if delta.abs() > TOLERANCE {
                changes.push(DimensionChange {
                    dimension: i,
                    name: None,
                    original: original[i],
                    suggested: suggested[i],
                    delta,
                });
            }
        }

        let total_distance = original.distance(&suggested);

        Self {
            original,
            suggested,
            changes,
            total_distance,
        }
    }

    /// Create a diff with dimension names.
    pub fn with_names(original: Vector, suggested: Vector, names: &[String]) -> Self {
        let mut diff = Self::new(original, suggested);
        for change in &mut diff.changes {
            if change.dimension < names.len() {
                change.name = Some(names[change.dimension].clone());
            }
        }
        diff
    }

    /// Check if there are any changes.
    pub fn has_changes(&self) -> bool {
        !self.changes.is_empty()
    }

    /// Get the number of dimensions that changed.
    pub fn num_changes(&self) -> usize {
        self.changes.len()
    }
}

/// Generate an explanation for a suggestion.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Explanation {
    /// The diff between original and suggested state
    pub diff: StateDiff,
    /// Human-readable summary
    pub summary: String,
    /// Detailed reasons for each constraint interaction
    pub constraint_reasons: Vec<String>,
    /// FG state of the suggestion
    pub fg_state: FGState,
}

impl Explanation {
    /// Create an explanation from a diff and constraints.
    pub fn new(
        original: Vector,
        suggested: Vector,
        fg_state: FGState,
        constraints: &[ConstraintRef],
    ) -> Self {
        let diff = StateDiff::new(original.clone(), suggested.clone());
        let summary = generate_summary(&diff, fg_state);
        let constraint_reasons = generate_constraint_reasons(&suggested, constraints);

        Self {
            diff,
            summary,
            constraint_reasons,
            fg_state,
        }
    }

    /// Create a simple explanation without constraint analysis.
    pub fn simple(original: Vector, suggested: Vector, fg_state: FGState) -> Self {
        let diff = StateDiff::new(original, suggested);
        let summary = generate_summary(&diff, fg_state);

        Self {
            diff,
            summary,
            constraint_reasons: Vec::new(),
            fg_state,
        }
    }
}

/// Generate a human-readable summary of the changes.
fn generate_summary(diff: &StateDiff, fg_state: FGState) -> String {
    if !diff.has_changes() {
        return "No change needed - position is valid.".to_string();
    }

    let direction = match diff.num_changes() {
        1 => {
            let change = &diff.changes[0];
            if change.delta > 0.0 {
                format!("Moved {} by +{:.2}", change.name.as_deref().unwrap_or(&format!("dimension {}", change.dimension)), change.delta)
            } else {
                format!("Moved {} by {:.2}", change.name.as_deref().unwrap_or(&format!("dimension {}", change.dimension)), change.delta)
            }
        }
        n => format!("Adjusted {} dimensions, total distance {:.2}", n, diff.total_distance),
    };

    let quality = match fg_state {
        FGState::Valid => "Now fully valid.",
        FGState::Slack { margin } if margin > 0.5 => "Now valid with good margin.",
        FGState::Slack { .. } => "Now valid but near boundary.",
        FGState::Exact => "Now exactly on boundary.",
        FGState::Finfr { .. } => "Still in violation (relaxed suggestion).",
    };

    format!("{} {}", direction, quality)
}

/// Generate reasons for each constraint interaction.
fn generate_constraint_reasons(point: &Vector, constraints: &[ConstraintRef]) -> Vec<String> {
    let mut reasons = Vec::new();

    for (i, constraint) in constraints.iter().enumerate() {
        let distance = constraint.distance(point);
        if distance.abs() < TOLERANCE {
            reasons.push(format!("Constraint {}: exactly on boundary ({})", i, constraint.describe()));
        } else if distance < 0.0 {
            reasons.push(format!("Constraint {}: satisfied with margin {:.2} ({})", i, -distance, constraint.describe()));
        } else {
            reasons.push(format!("Constraint {}: violated by {:.2} ({})", i, distance, constraint.describe()));
        }
    }

    reasons
}

/// Format an explanation for display.
pub fn format_explanation(explanation: &Explanation) -> String {
    let mut output = String::new();

    output.push_str(&explanation.summary);
    output.push('\n');

    if !explanation.diff.changes.is_empty() {
        output.push_str("\nChanges:\n");
        for change in &explanation.diff.changes {
            let default_name = format!("dim[{}]", change.dimension);
            let name = change.name.as_deref().unwrap_or(&default_name);
            output.push_str(&format!("  {}: {:.2} → {:.2} (Δ{:+.2})\n",
                name, change.original, change.suggested, change.delta));
        }
    }

    if !explanation.constraint_reasons.is_empty() {
        output.push_str("\nConstraint status:\n");
        for reason in &explanation.constraint_reasons {
            output.push_str(&format!("  {}\n", reason));
        }
    }

    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_state_diff_basic() {
        let original = Vector::from_slice(&[0.0, 0.0]);
        let suggested = Vector::from_slice(&[10.0, 0.0]);

        let diff = StateDiff::new(original, suggested);

        assert!(diff.has_changes());
        assert_eq!(diff.num_changes(), 1);
        assert!((diff.total_distance - 10.0).abs() < EPSILON);
    }

    #[test]
    fn test_state_diff_no_changes() {
        let original = Vector::from_slice(&[5.0, 5.0]);
        let suggested = Vector::from_slice(&[5.0, 5.0]);

        let diff = StateDiff::new(original, suggested);

        assert!(!diff.has_changes());
        assert_eq!(diff.num_changes(), 0);
    }

    #[test]
    fn test_state_diff_with_names() {
        let original = Vector::from_slice(&[0.0, 0.0]);
        let suggested = Vector::from_slice(&[10.0, 5.0]);
        let names = vec!["x".to_string(), "y".to_string()];

        let diff = StateDiff::with_names(original, suggested, &names);

        assert_eq!(diff.changes[0].name.as_deref(), Some("x"));
        assert_eq!(diff.changes[1].name.as_deref(), Some("y"));
    }

    #[test]
    fn test_explanation_simple() {
        let original = Vector::from_slice(&[150.0, 50.0]);
        let suggested = Vector::from_slice(&[100.0, 50.0]);

        let explanation = Explanation::simple(original, suggested, FGState::Valid);

        assert!(explanation.summary.contains("Moved"));
        assert!(explanation.diff.has_changes());
    }

    #[test]
    fn test_format_explanation() {
        let original = Vector::from_slice(&[0.0, 0.0]);
        let suggested = Vector::from_slice(&[10.0, 5.0]);

        let explanation = Explanation::simple(original, suggested, FGState::Valid);
        let formatted = format_explanation(&explanation);

        assert!(!formatted.is_empty());
        assert!(formatted.contains("Changes:"));
    }
}
