//! Constraint definitions and implementations.
//!
//! This module provides the `Constraint` trait and concrete implementations
//! for various constraint types used in Newton's projection system.

mod r#trait;
mod box_bounds;
mod linear;
mod collision;
mod discrete;

pub use r#trait::Constraint;
pub use box_bounds::BoxBounds;
pub use linear::LinearConstraint;
pub use collision::CollisionConstraint;
pub use discrete::DiscreteConstraint;

use crate::linalg::Vector;

/// A reference-counted constraint for shared ownership.
pub type ConstraintRef = std::sync::Arc<dyn Constraint>;

/// Create a boxed constraint from any Constraint implementation.
pub fn boxed<C: Constraint + 'static>(constraint: C) -> ConstraintRef {
    std::sync::Arc::new(constraint)
}

/// Check if all constraints in a list are satisfied by a point.
pub fn all_satisfied(constraints: &[ConstraintRef], point: &Vector) -> bool {
    constraints.iter().all(|c| c.satisfied(point))
}

/// Get the maximum violation distance across all constraints.
pub fn max_violation(constraints: &[ConstraintRef], point: &Vector) -> f64 {
    constraints
        .iter()
        .map(|c| c.distance(point).max(0.0))
        .fold(0.0, f64::max)
}

/// Check if all constraints in a list are convex.
pub fn all_convex(constraints: &[ConstraintRef]) -> bool {
    constraints.iter().all(|c| c.is_convex())
}
