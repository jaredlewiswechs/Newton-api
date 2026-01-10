//! Projection algorithms for constraint satisfaction.
//!
//! This module provides the core mathematical operations for projecting
//! points onto constraint sets. The primary algorithm is Dykstra's method
//! for projecting onto intersections of convex sets.

mod dykstra;
mod halfspace;
mod weighted;
mod relaxation;

pub use dykstra::{project_convex, project_convex_with_history, DykstraResult};
pub use halfspace::project_halfspace;
pub use weighted::project_weighted;
pub use relaxation::convex_relaxation;

use crate::linalg::Vector;
use crate::constraints::{Constraint, ConstraintRef, BoxBounds};
use crate::constants::TOLERANCE;

/// Project a point onto a single constraint.
pub fn project_single(point: &Vector, constraint: &dyn Constraint) -> Vector {
    constraint.project(point)
}

/// Project a point onto box bounds (convenience function).
pub fn project_box(point: &Vector, bounds: &BoxBounds) -> Vector {
    bounds.project(point)
}

/// Check if projection converged (change below tolerance).
#[inline]
pub fn has_converged(prev: &Vector, current: &Vector) -> bool {
    prev.distance(current) < TOLERANCE
}

/// Compute how far a point is from satisfying all constraints.
pub fn total_violation(point: &Vector, constraints: &[ConstraintRef]) -> f64 {
    constraints
        .iter()
        .map(|c| c.distance(point).max(0.0))
        .sum()
}
