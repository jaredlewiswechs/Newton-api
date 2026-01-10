//! Convex relaxation for nonconvex constraints.
//!
//! When dealing with nonconvex constraints (like collision avoidance or
//! discrete sets), we first compute a convex relaxation to get a "direction"
//! and then search for actual valid candidates.

use crate::linalg::Vector;
use crate::constraints::{ConstraintRef, BoxBounds, LinearConstraint};
use crate::projection::project_convex;
use crate::constants::EPSILON;

/// Compute a convex relaxation of a set of constraints.
///
/// For nonconvex constraints, this returns their convex hull or a
/// bounding box approximation. The relaxation is always a superset
/// of the original feasible region.
///
/// # Arguments
/// * `constraints` - Original constraints (may include nonconvex)
///
/// # Returns
/// A list of convex constraints that form a relaxation.
pub fn convex_relaxation(constraints: &[ConstraintRef]) -> Vec<ConstraintRef> {
    let mut convex = Vec::new();

    for c in constraints {
        if c.is_convex() {
            // Keep convex constraints as-is
            convex.push(c.clone());
        }
        // For nonconvex constraints, we don't add anything to the relaxation
        // (they'll be handled by candidate search)
    }

    convex
}

/// Project using convex relaxation, ignoring nonconvex constraints.
///
/// This gives a good starting point for candidate search.
pub fn project_relaxed(point: &Vector, constraints: &[ConstraintRef]) -> Vector {
    let convex = convex_relaxation(constraints);
    if convex.is_empty() {
        return point.clone();
    }
    project_convex(point, &convex)
}

/// Check if a constraint set is purely convex.
pub fn is_all_convex(constraints: &[ConstraintRef]) -> bool {
    constraints.iter().all(|c| c.is_convex())
}

/// Count nonconvex constraints in a set.
pub fn count_nonconvex(constraints: &[ConstraintRef]) -> usize {
    constraints.iter().filter(|c| !c.is_convex()).count()
}

/// Create a bounding box constraint from a set of points.
///
/// Useful for creating a convex relaxation from discrete candidates.
pub fn bounding_box_from_points(points: &[Vector]) -> Option<BoxBounds> {
    if points.is_empty() {
        return None;
    }

    let dim = points[0].dim();
    let mut min = points[0].clone();
    let mut max = points[0].clone();

    for point in points.iter().skip(1) {
        for i in 0..dim {
            min[i] = min[i].min(point[i]);
            max[i] = max[i].max(point[i]);
        }
    }

    Some(BoxBounds::new(min, max))
}

/// Create halfspace constraints that bound a set of points.
///
/// Returns constraints of the form a·x ≤ b where all given points
/// satisfy the constraint.
pub fn halfspace_bounds_from_points(points: &[Vector], directions: &[Vector]) -> Vec<LinearConstraint> {
    let mut constraints = Vec::new();

    for direction in directions {
        // Find maximum value of direction·point across all points
        let max_val = points
            .iter()
            .map(|p| direction.dot(p))
            .fold(f64::NEG_INFINITY, f64::max);

        constraints.push(LinearConstraint::new(direction.clone(), max_val + EPSILON));
    }

    constraints
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::constraints::{CollisionConstraint, DiscreteConstraint, boxed};
    use crate::primitives::Bounds;

    #[test]
    fn test_convex_relaxation_keeps_convex() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let linear = LinearConstraint::new(Vector::from_slice(&[1.0, 1.0]), 100.0);

        let constraints = vec![boxed(bounds), boxed(linear)];
        let relaxed = convex_relaxation(&constraints);

        assert_eq!(relaxed.len(), 2);
    }

    #[test]
    fn test_convex_relaxation_drops_nonconvex() {
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
        let relaxed = convex_relaxation(&constraints);

        // Only box bounds should remain
        assert_eq!(relaxed.len(), 1);
    }

    #[test]
    fn test_project_relaxed() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let discrete = DiscreteConstraint::from_scalars(&[0.0, 50.0, 100.0]);

        let constraints = vec![boxed(bounds.clone()), boxed(discrete)];

        // Project outside point
        let point = Vector::from_slice(&[150.0, 50.0]);
        let relaxed = project_relaxed(&point, &constraints);

        // Should satisfy box bounds (convex)
        assert!(bounds.contains(&relaxed));
    }

    #[test]
    fn test_is_all_convex() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        let convex_only = vec![boxed(bounds.clone())];
        assert!(is_all_convex(&convex_only));

        let discrete = DiscreteConstraint::from_scalars(&[0.0, 50.0, 100.0]);
        let with_nonconvex = vec![boxed(bounds), boxed(discrete)];
        assert!(!is_all_convex(&with_nonconvex));
    }

    #[test]
    fn test_bounding_box_from_points() {
        let points = vec![
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[10.0, 5.0]),
            Vector::from_slice(&[5.0, 10.0]),
        ];

        let bbox = bounding_box_from_points(&points).unwrap();

        assert!((bbox.min()[0] - 0.0).abs() < EPSILON);
        assert!((bbox.min()[1] - 0.0).abs() < EPSILON);
        assert!((bbox.max()[0] - 10.0).abs() < EPSILON);
        assert!((bbox.max()[1] - 10.0).abs() < EPSILON);
    }
}
