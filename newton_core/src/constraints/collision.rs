//! Collision constraint implementation.
//!
//! Prevents overlap between objects. This is a NONCONVEX constraint
//! that requires candidate search rather than direct projection.

use crate::linalg::Vector;
use crate::constraints::Constraint;
use crate::primitives::Bounds;
use crate::constants::EPSILON;
use serde::{Serialize, Deserialize};

/// Collision avoidance constraint.
///
/// Ensures that an object does not overlap with a fixed obstacle.
/// The feasible region is the complement of the obstacle's bounding box,
/// which is NONCONVEX.
///
/// For nonconvex constraints, `project()` returns the nearest point
/// on the boundary, but this may not be the globally nearest valid point.
/// Use candidate search for better results.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CollisionConstraint {
    /// The obstacle to avoid
    obstacle: Bounds,
    /// Minimum separation distance (padding)
    separation: f64,
    /// Effective bounds (obstacle expanded by separation)
    #[serde(skip)]
    effective_bounds: Option<Bounds>,
}

impl CollisionConstraint {
    /// Create a new collision constraint.
    ///
    /// # Arguments
    /// * `obstacle` - The bounding box of the obstacle to avoid
    /// * `separation` - Minimum distance to maintain from obstacle
    pub fn new(obstacle: Bounds, separation: f64) -> Self {
        let effective_bounds = if separation > 0.0 {
            Some(obstacle.expand(separation))
        } else {
            None
        };

        Self {
            obstacle,
            separation,
            effective_bounds,
        }
    }

    /// Get the obstacle bounds.
    pub fn obstacle(&self) -> &Bounds {
        &self.obstacle
    }

    /// Get the effective bounds (obstacle + separation).
    fn effective(&self) -> &Bounds {
        self.effective_bounds.as_ref().unwrap_or(&self.obstacle)
    }

    /// Get the minimum separation distance.
    pub fn separation(&self) -> f64 {
        self.separation
    }

    /// Generate candidate escape points around the obstacle.
    ///
    /// Returns points on the boundary of the effective obstacle
    /// that could be valid placements.
    pub fn escape_candidates(&self, point: &Vector) -> Vec<Vector> {
        let effective = self.effective();
        let dim = effective.dim();
        let mut candidates = Vec::with_capacity(2 * dim);

        // Use a larger margin to ensure candidates are clearly outside
        let margin = EPSILON * 100.0;

        // For each dimension, generate candidates at min and max boundaries
        for i in 0..dim {
            // Candidate at min boundary (push to left/bottom)
            let mut min_candidate = point.clone();
            min_candidate[i] = effective.min[i] - margin;
            candidates.push(min_candidate);

            // Candidate at max boundary (push to right/top)
            let mut max_candidate = point.clone();
            max_candidate[i] = effective.max[i] + margin;
            candidates.push(max_candidate);
        }

        // Also add corner candidates for 2D (4 corners)
        if dim == 2 {
            // Corners are often useful for diagonal approaches
            let corners = [
                Vector::from_slice(&[effective.min[0] - margin, effective.min[1] - margin]),
                Vector::from_slice(&[effective.min[0] - margin, effective.max[1] + margin]),
                Vector::from_slice(&[effective.max[0] + margin, effective.min[1] - margin]),
                Vector::from_slice(&[effective.max[0] + margin, effective.max[1] + margin]),
            ];
            candidates.extend(corners);
        }

        candidates
    }
}

impl Constraint for CollisionConstraint {
    fn satisfied(&self, point: &Vector) -> bool {
        // Satisfied if point is OUTSIDE the effective obstacle
        !self.effective().contains(point)
    }

    fn distance(&self, point: &Vector) -> f64 {
        let effective = self.effective();

        if !effective.contains(point) {
            // Outside obstacle: return negative distance (margin)
            -effective.distance(point)
        } else {
            // Inside obstacle: return positive distance (violation)
            // Distance is how far into the obstacle we are
            let mut min_dist = f64::INFINITY;
            for i in 0..effective.dim() {
                let dist_to_min = point[i] - effective.min[i];
                let dist_to_max = effective.max[i] - point[i];
                min_dist = min_dist.min(dist_to_min).min(dist_to_max);
            }
            min_dist.max(EPSILON)
        }
    }

    fn project(&self, point: &Vector) -> Vector {
        // If already satisfied, return unchanged
        if self.satisfied(point) {
            return point.clone();
        }

        let effective = self.effective();
        // Use a larger margin to ensure result is clearly outside
        let margin = EPSILON * 100.0;

        // Find the nearest boundary face
        let mut best_proj = point.clone();
        let mut best_dist = f64::INFINITY;

        for i in 0..effective.dim() {
            // Project to min face
            let mut proj_min = point.clone();
            proj_min[i] = effective.min[i] - margin;
            let dist_min = point.distance(&proj_min);
            if dist_min < best_dist {
                best_dist = dist_min;
                best_proj = proj_min;
            }

            // Project to max face
            let mut proj_max = point.clone();
            proj_max[i] = effective.max[i] + margin;
            let dist_max = point.distance(&proj_max);
            if dist_max < best_dist {
                best_dist = dist_max;
                best_proj = proj_max;
            }
        }

        best_proj
    }

    fn describe(&self) -> String {
        format!(
            "CollisionConstraint: avoid {:?} with separation {}",
            self.obstacle, self.separation
        )
    }

    fn is_convex(&self) -> bool {
        false // Collision avoidance is NONCONVEX
    }

    fn dim(&self) -> usize {
        self.obstacle.dim()
    }

    fn clone_box(&self) -> Box<dyn Constraint> {
        Box::new(self.clone())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_collision_satisfied() {
        let obstacle = Bounds::new(
            Vector::from_slice(&[40.0, 40.0]),
            Vector::from_slice(&[60.0, 60.0]),
        );
        let constraint = CollisionConstraint::new(obstacle, 0.0);

        // Outside obstacle - satisfied
        assert!(constraint.satisfied(&Vector::from_slice(&[0.0, 0.0])));
        assert!(constraint.satisfied(&Vector::from_slice(&[100.0, 100.0])));

        // Inside obstacle - not satisfied
        assert!(!constraint.satisfied(&Vector::from_slice(&[50.0, 50.0])));
    }

    #[test]
    fn test_collision_with_separation() {
        let obstacle = Bounds::new(
            Vector::from_slice(&[40.0, 40.0]),
            Vector::from_slice(&[60.0, 60.0]),
        );
        let constraint = CollisionConstraint::new(obstacle, 5.0);

        // Point that would be outside obstacle but within separation
        assert!(!constraint.satisfied(&Vector::from_slice(&[37.0, 50.0])));

        // Point outside effective bounds
        assert!(constraint.satisfied(&Vector::from_slice(&[30.0, 50.0])));
    }

    #[test]
    fn test_collision_project() {
        let obstacle = Bounds::new(
            Vector::from_slice(&[40.0, 40.0]),
            Vector::from_slice(&[60.0, 60.0]),
        );
        let constraint = CollisionConstraint::new(obstacle, 0.0);

        // Point inside - should project to nearest boundary
        let inside = Vector::from_slice(&[50.0, 45.0]);
        let projected = constraint.project(&inside);
        assert!(constraint.satisfied(&projected));
    }

    #[test]
    fn test_collision_is_nonconvex() {
        let obstacle = Bounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[10.0, 10.0]),
        );
        let constraint = CollisionConstraint::new(obstacle, 0.0);

        assert!(!constraint.is_convex());
    }

    #[test]
    fn test_escape_candidates() {
        let obstacle = Bounds::new(
            Vector::from_slice(&[40.0, 40.0]),
            Vector::from_slice(&[60.0, 60.0]),
        );
        let constraint = CollisionConstraint::new(obstacle, 0.0);

        let point = Vector::from_slice(&[50.0, 50.0]);
        let candidates = constraint.escape_candidates(&point);

        // Should have candidates at all boundaries plus corners
        assert!(!candidates.is_empty());

        // All candidates should be outside the obstacle
        for candidate in &candidates {
            assert!(constraint.satisfied(candidate), "Candidate {:?} is inside obstacle", candidate);
        }
    }
}
