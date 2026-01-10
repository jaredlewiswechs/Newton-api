//! Dykstra's algorithm for projecting onto intersections of convex sets.
//!
//! This is the core projection algorithm used by Newton for convex constraints.
//! It iteratively projects onto each constraint while maintaining correction
//! vectors to ensure convergence to the true nearest point.
//!
//! # Algorithm
//!
//! Given point p and convex constraints C = {C_1, ..., C_m}:
//!
//! 1. Initialize x_0 = p, y_i = 0 for all i
//! 2. For each iteration:
//!    - For each constraint C_i:
//!      - z = x + y_i
//!      - x' = Π_{C_i}(z)
//!      - y_i = z - x'
//!      - x = x'
//! 3. Repeat until convergence: ||x - x_prev|| < tolerance
//!
//! # Convergence
//!
//! Dykstra's algorithm converges for any collection of closed convex sets
//! with non-empty intersection. Convergence is typically linear.
//!
//! # References
//!
//! - Dykstra, R.L. (1983). "An Algorithm for Restricted Least Squares Regression"
//! - Boyle & Dykstra (1986). "A Method for Finding Projections..."

use crate::linalg::Vector;
use crate::constraints::ConstraintRef;
use crate::constants::{TOLERANCE, MAX_ITERATIONS};

/// Result of Dykstra's projection algorithm.
#[derive(Clone, Debug)]
pub struct DykstraResult {
    /// The projected point
    pub point: Vector,
    /// Number of iterations used
    pub iterations: usize,
    /// Whether the algorithm converged
    pub converged: bool,
    /// Final change magnitude
    pub final_change: f64,
}

/// Project a point onto the intersection of convex constraints using Dykstra's algorithm.
///
/// # Arguments
/// * `point` - The point to project
/// * `constraints` - List of convex constraints defining the feasible region
///
/// # Returns
/// The nearest point in the intersection of all constraints.
///
/// # Panics
/// Panics if any constraint is not convex.
///
/// # Example
/// ```rust
/// use newton_core::prelude::*;
///
/// let bounds = BoxBounds::new(
///     Vector::from_slice(&[0.0, 0.0]),
///     Vector::from_slice(&[100.0, 100.0]),
/// );
/// let point = Vector::from_slice(&[150.0, 50.0]);
/// let constraints = vec![boxed(bounds)];
/// let projected = project_convex(&point, &constraints);
/// ```
pub fn project_convex(point: &Vector, constraints: &[ConstraintRef]) -> Vector {
    let result = project_convex_internal(point, constraints);
    result.point
}

/// Project with full result information including iteration count and convergence.
pub fn project_convex_with_result(point: &Vector, constraints: &[ConstraintRef]) -> DykstraResult {
    project_convex_internal(point, constraints)
}

/// Project with iteration history for debugging/testing.
pub fn project_convex_with_history(
    point: &Vector,
    constraints: &[ConstraintRef],
) -> (Vector, usize, Vec<Vector>) {
    let mut x = point.clone();
    let mut history = vec![x.clone()];

    // Handle edge cases
    if constraints.is_empty() {
        return (x, 0, history);
    }

    // Verify all constraints are convex
    for c in constraints {
        assert!(
            c.is_convex(),
            "Dykstra's algorithm requires convex constraints"
        );
    }

    // Initialize increment vectors (one per constraint)
    let m = constraints.len();
    let dim = point.dim();
    let mut y: Vec<Vector> = vec![Vector::zeros(dim); m];

    let mut iterations = 0;

    for _ in 0..MAX_ITERATIONS {
        let x_prev = x.clone();
        iterations += 1;

        // Cycle through all constraints
        for i in 0..m {
            // z = x + y_i
            let z = &x + &y[i];

            // x' = project(z) onto constraint i
            let x_new = constraints[i].project(&z);

            // y_i = z - x' (correction vector)
            y[i] = &z - &x_new;

            // Update x
            x = x_new;
        }

        history.push(x.clone());

        // Check convergence
        let change = x.distance(&x_prev);
        if change < TOLERANCE {
            break;
        }
    }

    (x, iterations, history)
}

/// Internal implementation with full result.
fn project_convex_internal(point: &Vector, constraints: &[ConstraintRef]) -> DykstraResult {
    let mut x = point.clone();

    // Handle edge cases
    if constraints.is_empty() {
        return DykstraResult {
            point: x,
            iterations: 0,
            converged: true,
            final_change: 0.0,
        };
    }

    // Check if already feasible
    if constraints.iter().all(|c| c.satisfied(&x)) {
        return DykstraResult {
            point: x,
            iterations: 0,
            converged: true,
            final_change: 0.0,
        };
    }

    // Verify all constraints are convex
    for c in constraints {
        assert!(
            c.is_convex(),
            "Dykstra's algorithm requires convex constraints"
        );
    }

    // Initialize increment vectors (one per constraint)
    let m = constraints.len();
    let dim = point.dim();
    let mut y: Vec<Vector> = vec![Vector::zeros(dim); m];

    let mut iterations = 0;
    let mut final_change = f64::INFINITY;

    for _ in 0..MAX_ITERATIONS {
        let x_prev = x.clone();
        iterations += 1;

        // Cycle through all constraints
        for i in 0..m {
            // z = x + y_i
            let z = &x + &y[i];

            // x' = project(z) onto constraint i
            let x_new = constraints[i].project(&z);

            // y_i = z - x' (correction vector)
            y[i] = &z - &x_new;

            // Update x
            x = x_new;
        }

        // Check convergence
        final_change = x.distance(&x_prev);
        if final_change < TOLERANCE {
            return DykstraResult {
                point: x,
                iterations,
                converged: true,
                final_change,
            };
        }
    }

    // Did not converge within max iterations
    DykstraResult {
        point: x,
        iterations,
        converged: false,
        final_change,
    }
}

/// Simplified alternating projections (without correction vectors).
/// Faster but may not converge to the true nearest point in some cases.
/// Use only when constraints are "nice" (e.g., orthogonal halfspaces).
pub fn project_alternating(point: &Vector, constraints: &[ConstraintRef]) -> Vector {
    let mut x = point.clone();

    if constraints.is_empty() {
        return x;
    }

    for _ in 0..MAX_ITERATIONS {
        let x_prev = x.clone();

        for constraint in constraints {
            x = constraint.project(&x);
        }

        if x.distance(&x_prev) < TOLERANCE {
            break;
        }
    }

    x
}

/// Project onto constraints in a single pass (no iteration).
/// Fast but only exact when constraints are independent (e.g., box bounds).
pub fn project_single_pass(point: &Vector, constraints: &[ConstraintRef]) -> Vector {
    let mut x = point.clone();
    for constraint in constraints {
        x = constraint.project(&x);
    }
    x
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::constraints::{BoxBounds, LinearConstraint, boxed};
    use crate::constants::EPSILON;

    #[test]
    fn test_dykstra_box_bounds() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        // Point outside
        let point = Vector::from_slice(&[150.0, 50.0]);
        let projected = project_convex(&point, &constraints);

        assert!((projected[0] - 100.0).abs() < EPSILON);
        assert!((projected[1] - 50.0).abs() < EPSILON);
    }

    #[test]
    fn test_dykstra_halfspaces() {
        // x ≤ 10 and y ≤ 10
        let c1 = LinearConstraint::new(Vector::from_slice(&[1.0, 0.0]), 10.0);
        let c2 = LinearConstraint::new(Vector::from_slice(&[0.0, 1.0]), 10.0);
        let constraints = vec![boxed(c1), boxed(c2)];

        let point = Vector::from_slice(&[20.0, 20.0]);
        let projected = project_convex(&point, &constraints);

        assert!((projected[0] - 10.0).abs() < TOLERANCE);
        assert!((projected[1] - 10.0).abs() < TOLERANCE);
    }

    #[test]
    fn test_dykstra_intersection() {
        // x + y ≤ 10 and x ≥ 0 and y ≥ 0
        let c1 = LinearConstraint::new(Vector::from_slice(&[1.0, 1.0]), 10.0);
        let c2 = LinearConstraint::new(Vector::from_slice(&[-1.0, 0.0]), 0.0);
        let c3 = LinearConstraint::new(Vector::from_slice(&[0.0, -1.0]), 0.0);
        let constraints = vec![boxed(c1), boxed(c2), boxed(c3)];

        // Point outside all
        let point = Vector::from_slice(&[-5.0, -5.0]);
        let projected = project_convex(&point, &constraints);

        // Should be at origin (nearest point in triangle)
        assert!((projected[0]).abs() < TOLERANCE);
        assert!((projected[1]).abs() < TOLERANCE);
    }

    #[test]
    fn test_dykstra_already_feasible() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        let point = Vector::from_slice(&[50.0, 50.0]);
        let result = project_convex_with_result(&point, &constraints);

        assert!(result.converged);
        assert_eq!(result.iterations, 0);
        assert!(point.approx_eq(&result.point));
    }

    #[test]
    fn test_dykstra_empty_constraints() {
        let point = Vector::from_slice(&[50.0, 50.0]);
        let projected = project_convex(&point, &[]);

        assert!(point.approx_eq(&projected));
    }

    #[test]
    fn test_dykstra_idempotent() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        let point = Vector::from_slice(&[150.0, 150.0]);
        let proj1 = project_convex(&point, &constraints);
        let proj2 = project_convex(&proj1, &constraints);

        assert!(proj1.approx_eq(&proj2));
    }

    #[test]
    fn test_dykstra_deterministic() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        let point = Vector::from_slice(&[150.0, -50.0]);

        let result1 = project_convex(&point, &constraints);
        let result2 = project_convex(&point, &constraints);

        // Must be bitwise identical
        for i in 0..point.dim() {
            assert_eq!(result1[i].to_bits(), result2[i].to_bits());
        }
    }

    #[test]
    fn test_dykstra_with_history() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        let point = Vector::from_slice(&[150.0, 150.0]);
        let (projected, iterations, history) = project_convex_with_history(&point, &constraints);

        assert!(iterations > 0);
        assert!(!history.is_empty());
        assert!(projected.approx_eq(history.last().unwrap()));
    }
}
