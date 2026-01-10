//! Weighted projection.
//!
//! Projects a point using weighted Euclidean distance, allowing certain
//! dimensions to be more "important" than others.
//!
//! # Algorithm
//!
//! Weighted projection works by scaling space:
//! 1. Transform point to scaled space: p' = W^(1/2) * p
//! 2. Project in scaled space: p'* = Π(p')
//! 3. Transform back: p* = W^(-1/2) * p'*
//!
//! Higher weights mean that dimension is more "expensive" to change.

use crate::linalg::Vector;
use crate::constraints::{BoxBounds, Constraint, ConstraintRef};
use crate::constants::{EPSILON, TOLERANCE};

/// Project a point onto box bounds using weighted Euclidean distance.
///
/// # Arguments
/// * `point` - The point to project
/// * `bounds` - The box bounds constraint
/// * `weights` - Per-dimension weights (higher = more important to preserve)
///
/// # Returns
/// The weighted-nearest point in the bounds.
///
/// # Example
/// ```rust
/// use newton_core::projection::project_weighted;
/// use newton_core::constraints::BoxBounds;
/// use newton_core::linalg::Vector;
///
/// let bounds = BoxBounds::new(
///     Vector::from_slice(&[0.0, 0.0]),
///     Vector::from_slice(&[100.0, 100.0]),
/// );
/// let point = Vector::from_slice(&[150.0, 150.0]);
/// // Dimension 0 is 10x more important
/// let weights = Vector::from_slice(&[10.0, 1.0]);
///
/// let projected = project_weighted(&point, &bounds, &weights);
/// // Dimension 0 should change less than dimension 1
/// ```
pub fn project_weighted(point: &Vector, bounds: &BoxBounds, weights: &Vector) -> Vector {
    assert_eq!(point.dim(), bounds.dim());
    assert_eq!(point.dim(), weights.dim());

    let dim = point.dim();

    // Validate weights (must be positive)
    for i in 0..dim {
        assert!(
            weights[i] > EPSILON,
            "Weight in dimension {} must be positive (got {})",
            i,
            weights[i]
        );
    }

    // Compute sqrt of weights for scaling
    let sqrt_weights = weights.sqrt();

    // Transform to scaled space
    let scaled_point = point.component_mul(&sqrt_weights);
    let scaled_min = bounds.min().component_mul(&sqrt_weights);
    let scaled_max = bounds.max().component_mul(&sqrt_weights);

    // Create scaled bounds
    let scaled_bounds = BoxBounds::new(scaled_min, scaled_max);

    // Project in scaled space
    let scaled_projected = scaled_bounds.project(&scaled_point);

    // Transform back to original space
    let inv_sqrt_weights: Vector = (0..dim)
        .map(|i| 1.0 / sqrt_weights[i])
        .collect();

    scaled_projected.component_mul(&inv_sqrt_weights)
}

/// Project onto multiple constraints using weighted distance.
///
/// Uses Dykstra's algorithm in weighted space.
pub fn project_weighted_multi(
    point: &Vector,
    constraints: &[ConstraintRef],
    weights: &Vector,
) -> Vector {
    if constraints.is_empty() {
        return point.clone();
    }

    let dim = point.dim();

    // For general constraints, we use iterative reweighted projection
    // This is an approximation that works well for convex constraints

    let sqrt_weights = weights.sqrt();
    let inv_sqrt_weights: Vector = (0..dim)
        .map(|i| 1.0 / (sqrt_weights[i] + EPSILON))
        .collect();

    // Project in original space but weight the step
    let mut x = point.clone();

    for _ in 0..100 {
        let x_prev = x.clone();

        // Project onto each constraint
        for constraint in constraints {
            let projected = constraint.project(&x);

            // Weight the correction
            let correction = &projected - &x;
            let weighted_correction = correction.component_div(&weights);
            x = &x + &weighted_correction.component_mul(&weights);
        }

        if x.distance(&x_prev) < TOLERANCE {
            break;
        }
    }

    x
}

/// Compute weighted distance between two points.
pub fn weighted_distance(a: &Vector, b: &Vector, weights: &Vector) -> f64 {
    assert_eq!(a.dim(), b.dim());
    assert_eq!(a.dim(), weights.dim());

    let diff = a - b;
    let weighted_diff = diff.component_mul(weights);
    weighted_diff.norm()
}

/// Compute weighted squared distance (more efficient, no sqrt).
pub fn weighted_distance_squared(a: &Vector, b: &Vector, weights: &Vector) -> f64 {
    assert_eq!(a.dim(), b.dim());
    assert_eq!(a.dim(), weights.dim());

    let diff = a - b;
    let weighted_diff = diff.component_mul(weights);
    weighted_diff.norm_squared()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_weighted_projection_uniform() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let point = Vector::from_slice(&[150.0, 150.0]);
        let weights = Vector::from_slice(&[1.0, 1.0]); // Uniform weights

        let projected = project_weighted(&point, &bounds, &weights);

        // With uniform weights, should project to corner
        assert!((projected[0] - 100.0).abs() < TOLERANCE);
        assert!((projected[1] - 100.0).abs() < TOLERANCE);
    }

    #[test]
    fn test_weighted_projection_skewed() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let point = Vector::from_slice(&[150.0, 150.0]);
        // Dimension 0 is 100x more important
        let weights = Vector::from_slice(&[100.0, 1.0]);

        let projected = project_weighted(&point, &bounds, &weights);

        // Note: For box bounds, each dimension is projected independently,
        // so weights don't affect the result when both dimensions are
        // past the boundary - each gets clamped to its boundary.
        // The weighted projection is more useful for hyperplanes or
        // constraints where there's a trade-off between dimensions.

        // Both dimensions get clamped to the boundary
        assert!((projected[0] - 100.0).abs() < TOLERANCE);
        assert!((projected[1] - 100.0).abs() < TOLERANCE);

        // Verify the result is inside bounds
        assert!(bounds.contains(&projected));
    }

    #[test]
    fn test_weighted_projection_preserves_high_weight() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        // Point with only dim 0 outside
        let point = Vector::from_slice(&[150.0, 50.0]);
        let weights = Vector::from_slice(&[1000.0, 1.0]);

        let projected = project_weighted(&point, &bounds, &weights);

        // Dim 1 should stay the same (already valid)
        assert!((projected[1] - 50.0).abs() < TOLERANCE);

        // Dim 0 must be clamped to boundary
        assert!((projected[0] - 100.0).abs() < TOLERANCE);
    }

    #[test]
    fn test_weighted_distance() {
        let a = Vector::from_slice(&[0.0, 0.0]);
        let b = Vector::from_slice(&[3.0, 4.0]);
        let weights = Vector::from_slice(&[1.0, 1.0]);

        let dist = weighted_distance(&a, &b, &weights);
        assert!((dist - 5.0).abs() < EPSILON);
    }

    #[test]
    fn test_weighted_distance_scaled() {
        let a = Vector::from_slice(&[0.0, 0.0]);
        let b = Vector::from_slice(&[3.0, 4.0]);
        // Weight dim 0 by 2
        let weights = Vector::from_slice(&[2.0, 1.0]);

        let dist = weighted_distance(&a, &b, &weights);
        // sqrt((2*3)^2 + (1*4)^2) = sqrt(36 + 16) = sqrt(52)
        let expected = (36.0 + 16.0_f64).sqrt();
        assert!((dist - expected).abs() < EPSILON);
    }

    #[test]
    fn test_weighted_projection_inside() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let point = Vector::from_slice(&[50.0, 50.0]);
        let weights = Vector::from_slice(&[10.0, 1.0]);

        let projected = project_weighted(&point, &bounds, &weights);

        // Point inside should not move
        assert!(point.approx_eq(&projected));
    }
}
