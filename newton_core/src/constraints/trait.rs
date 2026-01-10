//! The Constraint trait definition.

use crate::linalg::Vector;

/// A constraint that can be checked and projected onto.
///
/// All constraints in Newton implement this trait. The trait defines
/// the core operations needed for the projection algorithm:
/// - Checking if a point satisfies the constraint
/// - Computing distance to the constraint boundary
/// - Projecting a point onto the constraint set
///
/// # Determinism
///
/// All implementations MUST be deterministic: given the same input,
/// they must produce bitwise-identical output.
///
/// # Thread Safety
///
/// All implementations must be `Send + Sync` for use in parallel algorithms.
pub trait Constraint: Send + Sync + std::fmt::Debug {
    /// Check if a point satisfies this constraint.
    ///
    /// Returns true if the point is inside or on the boundary of the
    /// constraint's feasible region.
    fn satisfied(&self, point: &Vector) -> bool;

    /// Compute signed distance from a point to the constraint boundary.
    ///
    /// - Negative: point is inside the constraint (satisfied with margin)
    /// - Zero: point is on the boundary
    /// - Positive: point is outside (violating)
    fn distance(&self, point: &Vector) -> f64;

    /// Project a point onto the constraint's feasible region.
    ///
    /// Returns the nearest point in the constraint set.
    /// If the point is already satisfied, returns a copy of the point.
    fn project(&self, point: &Vector) -> Vector;

    /// Human-readable description of the constraint.
    fn describe(&self) -> String;

    /// Check if this constraint defines a convex set.
    ///
    /// Convex constraints can be handled efficiently by Dykstra's algorithm.
    /// Nonconvex constraints require candidate search.
    fn is_convex(&self) -> bool {
        true // Default to convex, override for nonconvex
    }

    /// Get the dimension this constraint operates in.
    fn dim(&self) -> usize;

    /// Clone the constraint into a boxed trait object.
    fn clone_box(&self) -> Box<dyn Constraint>;
}

impl Clone for Box<dyn Constraint> {
    fn clone(&self) -> Self {
        self.clone_box()
    }
}
