//! Linear constraint (halfspace) implementation.
//!
//! Represents a linear inequality: a·x ≤ b

use crate::linalg::Vector;
use crate::constraints::Constraint;
use crate::constants::{EPSILON, is_near_zero};
use serde::{Serialize, Deserialize};

/// Linear constraint (halfspace).
///
/// The feasible region is the set of all points x where:
/// `a · x ≤ b`
///
/// This is a convex constraint with O(n) projection time.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LinearConstraint {
    /// Normal vector (direction of constraint)
    normal: Vector,
    /// Offset (bound value)
    bound: f64,
    /// Precomputed squared norm of normal for efficiency
    #[serde(skip)]
    normal_norm_sq: f64,
}

impl LinearConstraint {
    /// Create a new linear constraint a·x ≤ b.
    ///
    /// # Arguments
    /// * `normal` - The normal vector 'a' in a·x ≤ b
    /// * `bound` - The bound value 'b'
    ///
    /// # Note
    /// Near-zero normals are handled gracefully (constraint becomes vacuously true).
    pub fn new(normal: Vector, bound: f64) -> Self {
        let normal_norm_sq = normal.norm_squared();
        Self {
            normal,
            bound,
            normal_norm_sq,
        }
    }

    /// Create a constraint x[dim] ≤ bound (upper bound on single dimension).
    pub fn upper_bound(dimension: usize, total_dims: usize, bound: f64) -> Self {
        Self::new(Vector::unit(total_dims, dimension), bound)
    }

    /// Create a constraint x[dim] ≥ bound (lower bound on single dimension).
    pub fn lower_bound(dimension: usize, total_dims: usize, bound: f64) -> Self {
        Self::new(-Vector::unit(total_dims, dimension), -bound)
    }

    /// Create an equality constraint a·x = b (as two halfspaces).
    /// Returns a pair of constraints: (a·x ≤ b, -a·x ≤ -b)
    pub fn equality(normal: Vector, bound: f64) -> (Self, Self) {
        let neg_normal = -&normal;
        (Self::new(normal, bound), Self::new(neg_normal, -bound))
    }

    /// Get the normal vector.
    pub fn normal(&self) -> &Vector {
        &self.normal
    }

    /// Get the bound value.
    pub fn bound(&self) -> f64 {
        self.bound
    }

    /// Compute a·x - b (the "slack" or violation amount).
    /// Negative means satisfied with margin, positive means violated.
    fn slack(&self, point: &Vector) -> f64 {
        self.normal.dot(point) - self.bound
    }

    /// Check if the normal vector is degenerate (near-zero).
    fn is_degenerate(&self) -> bool {
        is_near_zero(self.normal_norm_sq)
    }
}

impl Constraint for LinearConstraint {
    fn satisfied(&self, point: &Vector) -> bool {
        assert_eq!(point.dim(), self.dim());

        // Degenerate constraint: check sign of bound
        if self.is_degenerate() {
            return self.bound >= -EPSILON;
        }

        self.slack(point) <= EPSILON
    }

    fn distance(&self, point: &Vector) -> f64 {
        assert_eq!(point.dim(), self.dim());

        // Degenerate constraint
        if self.is_degenerate() {
            return if self.bound >= 0.0 { -f64::INFINITY } else { f64::INFINITY };
        }

        // slack = a·x - b
        // If slack <= 0: satisfied (inside), return negative distance
        // If slack > 0: violated (outside), return positive distance
        let slack = self.slack(point);
        slack / self.normal_norm_sq.sqrt()
    }

    fn project(&self, point: &Vector) -> Vector {
        assert_eq!(point.dim(), self.dim());

        // Degenerate constraint: return point unchanged
        if self.is_degenerate() {
            return point.clone();
        }

        let slack = self.slack(point);

        // Already satisfied
        if slack <= EPSILON {
            return point.clone();
        }

        // Project: p' = p - ((a·p - b) / ||a||²) * a
        let scale = slack / self.normal_norm_sq;
        point - &(&self.normal * scale)
    }

    fn describe(&self) -> String {
        format!(
            "LinearConstraint: {:?} · x ≤ {}",
            self.normal.as_slice(),
            self.bound
        )
    }

    fn is_convex(&self) -> bool {
        true
    }

    fn dim(&self) -> usize {
        self.normal.dim()
    }

    fn clone_box(&self) -> Box<dyn Constraint> {
        Box::new(self.clone())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_linear_constraint_satisfied() {
        // x ≤ 5
        let constraint = LinearConstraint::new(
            Vector::from_slice(&[1.0, 0.0]),
            5.0,
        );

        assert!(constraint.satisfied(&Vector::from_slice(&[3.0, 10.0])));
        assert!(constraint.satisfied(&Vector::from_slice(&[5.0, 10.0])));
        assert!(!constraint.satisfied(&Vector::from_slice(&[6.0, 10.0])));
    }

    #[test]
    fn test_linear_constraint_project() {
        // x ≤ 5
        let constraint = LinearConstraint::new(
            Vector::from_slice(&[1.0, 0.0]),
            5.0,
        );

        // Already satisfied
        let inside = Vector::from_slice(&[3.0, 10.0]);
        let projected = constraint.project(&inside);
        assert!(inside.approx_eq(&projected));

        // Outside - project to boundary
        let outside = Vector::from_slice(&[8.0, 10.0]);
        let projected = constraint.project(&outside);
        assert!((projected[0] - 5.0).abs() < EPSILON);
        assert!((projected[1] - 10.0).abs() < EPSILON);
    }

    #[test]
    fn test_linear_constraint_diagonal() {
        // x + y ≤ 10
        let constraint = LinearConstraint::new(
            Vector::from_slice(&[1.0, 1.0]),
            10.0,
        );

        assert!(constraint.satisfied(&Vector::from_slice(&[3.0, 3.0])));
        assert!(constraint.satisfied(&Vector::from_slice(&[5.0, 5.0])));
        assert!(!constraint.satisfied(&Vector::from_slice(&[6.0, 6.0])));

        // Project (8, 8) onto x + y = 10
        let outside = Vector::from_slice(&[8.0, 8.0]);
        let projected = constraint.project(&outside);
        // Should move equally in both dimensions
        assert!((projected[0] + projected[1] - 10.0).abs() < EPSILON);
    }

    #[test]
    fn test_linear_constraint_upper_lower() {
        let upper = LinearConstraint::upper_bound(0, 2, 10.0);
        let lower = LinearConstraint::lower_bound(0, 2, 0.0);

        assert!(upper.satisfied(&Vector::from_slice(&[5.0, 100.0])));
        assert!(!upper.satisfied(&Vector::from_slice(&[15.0, 100.0])));

        assert!(lower.satisfied(&Vector::from_slice(&[5.0, 100.0])));
        assert!(!lower.satisfied(&Vector::from_slice(&[-5.0, 100.0])));
    }

    #[test]
    fn test_linear_constraint_degenerate() {
        // Near-zero normal
        let constraint = LinearConstraint::new(
            Vector::from_slice(&[1e-15, 0.0]),
            100.0,
        );

        // Should be vacuously satisfied (bound is positive)
        assert!(constraint.satisfied(&Vector::from_slice(&[1000.0, 1000.0])));

        // Projection should return point unchanged
        let point = Vector::from_slice(&[1000.0, 1000.0]);
        let projected = constraint.project(&point);
        assert!(point.approx_eq(&projected));
    }

    #[test]
    fn test_linear_constraint_idempotent() {
        let constraint = LinearConstraint::new(
            Vector::from_slice(&[1.0, 1.0]),
            10.0,
        );

        let point = Vector::from_slice(&[20.0, 20.0]);
        let proj1 = constraint.project(&point);
        let proj2 = constraint.project(&proj1);

        assert!(proj1.approx_eq(&proj2));
    }
}
