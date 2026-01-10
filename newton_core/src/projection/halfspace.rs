//! Halfspace projection.
//!
//! Projects a point onto a halfspace defined by a linear inequality a·x ≤ b.
//!
//! # Formula
//!
//! For halfspace H = {x : a·x ≤ b}, the projection of point p is:
//!
//! ```text
//! Π_H(p) = p - max(0, (a·p - b) / ||a||²) * a
//! ```
//!
//! If p is already in H (a·p ≤ b), the projection is p itself.
//! Otherwise, we move p along the normal direction until it touches the boundary.

use crate::linalg::Vector;
use crate::constants::{EPSILON, is_near_zero};

/// Project a point onto a halfspace a·x ≤ b.
///
/// # Arguments
/// * `point` - The point to project
/// * `normal` - The normal vector 'a' (direction of constraint)
/// * `bound` - The bound value 'b'
///
/// # Returns
/// The projection onto the halfspace.
///
/// # Example
/// ```rust
/// use newton_core::projection::project_halfspace;
/// use newton_core::linalg::Vector;
///
/// // Project onto x ≤ 5
/// let point = Vector::from_slice(&[10.0, 3.0]);
/// let normal = Vector::from_slice(&[1.0, 0.0]);
/// let projected = project_halfspace(&point, &normal, 5.0);
///
/// assert!((projected[0] - 5.0).abs() < 1e-10);
/// assert!((projected[1] - 3.0).abs() < 1e-10);
/// ```
pub fn project_halfspace(point: &Vector, normal: &Vector, bound: f64) -> Vector {
    assert_eq!(point.dim(), normal.dim(), "Dimensions must match");

    let normal_norm_sq = normal.norm_squared();

    // Handle degenerate normal (near-zero)
    if is_near_zero(normal_norm_sq) {
        return point.clone();
    }

    // Compute slack: a·p - b
    let slack = normal.dot(point) - bound;

    // If already satisfied (slack ≤ 0), return point unchanged
    if slack <= EPSILON {
        return point.clone();
    }

    // Project: p' = p - (slack / ||a||²) * a
    let scale = slack / normal_norm_sq;
    point - &(normal * scale)
}

/// Project onto the boundary of a halfspace (equality constraint a·x = b).
///
/// This always moves the point to the hyperplane, even if it's inside the halfspace.
pub fn project_hyperplane(point: &Vector, normal: &Vector, bound: f64) -> Vector {
    assert_eq!(point.dim(), normal.dim(), "Dimensions must match");

    let normal_norm_sq = normal.norm_squared();

    // Handle degenerate normal
    if is_near_zero(normal_norm_sq) {
        return point.clone();
    }

    // Compute signed distance to hyperplane
    let slack = normal.dot(point) - bound;

    // Project: p' = p - (slack / ||a||²) * a
    let scale = slack / normal_norm_sq;
    point - &(normal * scale)
}

/// Compute the signed distance from a point to a halfspace boundary.
///
/// Returns negative if inside, positive if outside, zero if on boundary.
pub fn halfspace_distance(point: &Vector, normal: &Vector, bound: f64) -> f64 {
    let normal_norm = normal.norm();
    if is_near_zero(normal_norm) {
        return 0.0;
    }
    (normal.dot(point) - bound) / normal_norm
}

/// Check if a point satisfies a halfspace constraint a·x ≤ b.
pub fn in_halfspace(point: &Vector, normal: &Vector, bound: f64) -> bool {
    normal.dot(point) <= bound + EPSILON
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_project_halfspace_outside() {
        // x ≤ 5
        let point = Vector::from_slice(&[10.0, 3.0]);
        let normal = Vector::from_slice(&[1.0, 0.0]);
        let projected = project_halfspace(&point, &normal, 5.0);

        assert!((projected[0] - 5.0).abs() < EPSILON);
        assert!((projected[1] - 3.0).abs() < EPSILON);
    }

    #[test]
    fn test_project_halfspace_inside() {
        // x ≤ 5
        let point = Vector::from_slice(&[3.0, 7.0]);
        let normal = Vector::from_slice(&[1.0, 0.0]);
        let projected = project_halfspace(&point, &normal, 5.0);

        assert!(point.approx_eq(&projected));
    }

    #[test]
    fn test_project_halfspace_diagonal() {
        // x + y ≤ 10
        let point = Vector::from_slice(&[8.0, 8.0]);
        let normal = Vector::from_slice(&[1.0, 1.0]);
        let projected = project_halfspace(&point, &normal, 10.0);

        // Should satisfy constraint
        assert!(normal.dot(&projected) <= 10.0 + EPSILON);

        // Should be nearest point on boundary
        assert!((projected[0] + projected[1] - 10.0).abs() < EPSILON);
    }

    #[test]
    fn test_project_hyperplane() {
        // x = 5
        let point = Vector::from_slice(&[3.0, 7.0]);
        let normal = Vector::from_slice(&[1.0, 0.0]);
        let projected = project_hyperplane(&point, &normal, 5.0);

        assert!((projected[0] - 5.0).abs() < EPSILON);
        assert!((projected[1] - 7.0).abs() < EPSILON);
    }

    #[test]
    fn test_halfspace_distance() {
        let normal = Vector::from_slice(&[1.0, 0.0]);

        // Inside
        let inside = Vector::from_slice(&[3.0, 5.0]);
        assert!(halfspace_distance(&inside, &normal, 5.0) < 0.0);

        // Outside
        let outside = Vector::from_slice(&[7.0, 5.0]);
        assert!(halfspace_distance(&outside, &normal, 5.0) > 0.0);

        // On boundary
        let boundary = Vector::from_slice(&[5.0, 5.0]);
        assert!(halfspace_distance(&boundary, &normal, 5.0).abs() < EPSILON);
    }

    #[test]
    fn test_degenerate_normal() {
        let point = Vector::from_slice(&[10.0, 10.0]);
        let normal = Vector::from_slice(&[1e-15, 0.0]); // Near-zero
        let projected = project_halfspace(&point, &normal, 5.0);

        // Should return point unchanged
        assert!(point.approx_eq(&projected));
    }

    #[test]
    fn test_idempotent() {
        let point = Vector::from_slice(&[10.0, 10.0]);
        let normal = Vector::from_slice(&[1.0, 1.0]);
        let bound = 10.0;

        let proj1 = project_halfspace(&point, &normal, bound);
        let proj2 = project_halfspace(&proj1, &normal, bound);

        assert!(proj1.approx_eq(&proj2));
    }
}
