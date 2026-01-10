//! Adversarial tests for Newton Core.
//!
//! These tests target pathological inputs and edge cases that could
//! cause numerical instability, infinite loops, or incorrect results.

use crate::linalg::Vector;
use crate::constraints::{BoxBounds, LinearConstraint, Constraint, boxed, ConstraintRef};
use crate::projection::{project_convex, project_convex_with_history, project_weighted};
use crate::constants::{TOLERANCE, EPSILON, MAX_ITERATIONS};

// ============================================================================
// ADVERSARIAL 1: Thin Slab Converges
// Extremely thin feasible regions should not cause numerical issues.
// ============================================================================

#[test]
fn thin_slab_converges() {
    // Feasible region: 0 ≤ x ≤ 0.0001 (very thin slab)
    let constraints: Vec<ConstraintRef> = vec![
        boxed(LinearConstraint::new(Vector::from_slice(&[-1.0, 0.0]), 0.0)),      // x ≥ 0
        boxed(LinearConstraint::new(Vector::from_slice(&[1.0, 0.0]), 0.0001)),    // x ≤ 0.0001
        boxed(LinearConstraint::new(Vector::from_slice(&[0.0, -1.0]), 0.0)),      // y ≥ 0
        boxed(LinearConstraint::new(Vector::from_slice(&[0.0, 1.0]), 100.0)),     // y ≤ 100
    ];

    // Point far outside
    let point = Vector::from_slice(&[1000.0, 50.0]);

    let projected = project_convex(&point, &constraints);

    // Must land inside
    assert!(projected[0] >= -TOLERANCE, "x below min: {}", projected[0]);
    assert!(projected[0] <= 0.0001 + TOLERANCE, "x above max: {}", projected[0]);
    assert!(projected[1] >= -TOLERANCE, "y below min: {}", projected[1]);
    assert!(projected[1] <= 100.0 + TOLERANCE, "y above max: {}", projected[1]);
}

#[test]
fn thin_slab_no_oscillation() {
    // Same thin slab
    let constraints: Vec<ConstraintRef> = vec![
        boxed(LinearConstraint::new(Vector::from_slice(&[-1.0, 0.0]), 0.0)),
        boxed(LinearConstraint::new(Vector::from_slice(&[1.0, 0.0]), 0.0001)),
        boxed(LinearConstraint::new(Vector::from_slice(&[0.0, -1.0]), 0.0)),
        boxed(LinearConstraint::new(Vector::from_slice(&[0.0, 1.0]), 100.0)),
    ];

    let point = Vector::from_slice(&[1000.0, 50.0]);

    // Track intermediate states
    let (projected, iterations, history) = project_convex_with_history(&point, &constraints);

    // Check for oscillation: distance to final should decrease (mostly)
    let mut increasing_count = 0;
    for i in 1..history.len() {
        let dist_prev = history[i-1].distance(&projected);
        let dist_curr = history[i].distance(&projected);
        if dist_curr > dist_prev + TOLERANCE {
            increasing_count += 1;
        }
    }

    // Allow at most 10% of iterations to increase distance
    let max_allowed = (iterations as f64 * 0.1).ceil() as usize + 1;
    assert!(
        increasing_count <= max_allowed,
        "Too much oscillation: {} increases in {} iterations",
        increasing_count, iterations
    );
}

// ============================================================================
// ADVERSARIAL 2: Skewed Weights Don't Cause Teleportation
// Extreme weight ratios should not cause dimensions to jump wildly.
// ============================================================================

#[test]
fn extreme_weight_skew_still_valid() {
    let bounds = BoxBounds::new(
        Vector::from_slice(&[0.0, 0.0]),
        Vector::from_slice(&[100.0, 100.0]),
    );

    // Point outside bounds
    let point = Vector::from_slice(&[200.0, 200.0]);

    // Extremely skewed weights: dimension 0 is 1000x more important
    let weights = Vector::from_slice(&[1000.0, 1.0]);

    let projected = project_weighted(&point, &bounds, &weights);

    // Must be inside bounds
    assert!(bounds.contains(&projected), "Projected point outside bounds: {:?}", projected.as_slice());
}

#[test]
fn extreme_weight_skew_no_teleportation() {
    let bounds = BoxBounds::new(
        Vector::from_slice(&[0.0, 0.0, 0.0]),
        Vector::from_slice(&[100.0, 100.0, 100.0]),
    );

    // Point just outside bounds in x only
    let point = Vector::from_slice(&[101.0, 50.0, 50.0]);

    // Dimension 1 and 2 have near-zero weight (but still positive)
    let weights = Vector::from_slice(&[1.0, 0.01, 0.01]);

    let projected = project_weighted(&point, &bounds, &weights);

    // Low-weight dimensions should not "teleport" far from their original values
    // They were already valid, so should stay roughly where they were
    assert!(
        (projected[1] - 50.0).abs() < 20.0,
        "Dimension 1 teleported: {} -> {}",
        50.0, projected[1]
    );
    assert!(
        (projected[2] - 50.0).abs() < 20.0,
        "Dimension 2 teleported: {} -> {}",
        50.0, projected[2]
    );
}

// ============================================================================
// ADVERSARIAL 3: Near-Zero Normals Handled Gracefully
// Degenerate constraints should not cause NaN or crashes.
// ============================================================================

#[test]
fn near_zero_normal_handled() {
    // Constraint with tiny normal: essentially no constraint
    let constraints: Vec<ConstraintRef> = vec![
        boxed(LinearConstraint::new(Vector::from_slice(&[1e-15, 0.0]), 100.0)),  // ~0·x ≤ 100
        boxed(LinearConstraint::new(Vector::from_slice(&[0.0, 1.0]), 50.0)),      // y ≤ 50
    ];

    let point = Vector::from_slice(&[1000.0, 1000.0]);

    // Should not panic or produce NaN
    let projected = project_convex(&point, &constraints);

    assert!(!projected[0].is_nan(), "NaN in dimension 0");
    assert!(!projected[1].is_nan(), "NaN in dimension 1");
    assert!(projected.is_finite(), "Non-finite result");
    assert!(projected[1] <= 50.0 + EPSILON, "y constraint violated: {}", projected[1]);
}

// ============================================================================
// ADVERSARIAL 4: Duplicate Constraints Don't Double-Count
// Same constraint repeated should not over-project.
// ============================================================================

#[test]
fn duplicate_constraints_no_double_count() {
    // Same constraint twice: x ≤ 50
    let constraint = LinearConstraint::new(Vector::from_slice(&[1.0, 0.0]), 50.0);
    let constraints: Vec<ConstraintRef> = vec![boxed(constraint.clone()), boxed(constraint)];

    let point = Vector::from_slice(&[100.0, 25.0]);

    let projected = project_convex(&point, &constraints);

    // Should project to x=50, not overshoot due to double-counting
    assert!(
        (projected[0] - 50.0).abs() < TOLERANCE * 10.0,
        "Double-counted: projected to {} instead of 50",
        projected[0]
    );

    // y should be unchanged
    assert!(
        (projected[1] - 25.0).abs() < TOLERANCE,
        "y changed unexpectedly: {} -> {}",
        25.0, projected[1]
    );
}

// ============================================================================
// ADVERSARIAL 5: Large Coordinate Values
// Very large numbers should not cause overflow or precision loss.
// ============================================================================

#[test]
fn large_coordinates_stable() {
    let bounds = BoxBounds::new(
        Vector::from_slice(&[0.0, 0.0]),
        Vector::from_slice(&[1e12, 1e12]),
    );

    // Point with large coordinates
    let point = Vector::from_slice(&[1e15, 5e11]);

    let projected = bounds.project(&point);

    assert!(projected[0].is_finite(), "Non-finite x");
    assert!(projected[1].is_finite(), "Non-finite y");
    assert!(bounds.contains(&projected), "Outside bounds");
}

// ============================================================================
// ADVERSARIAL 6: Small Coordinate Values
// Very small numbers should not cause underflow.
// ============================================================================

#[test]
fn small_coordinates_stable() {
    let bounds = BoxBounds::new(
        Vector::from_slice(&[0.0, 0.0]),
        Vector::from_slice(&[1e-10, 1e-10]),
    );

    let point = Vector::from_slice(&[1e-8, 5e-11]);

    let projected = bounds.project(&point);

    assert!(projected[0].is_finite(), "Non-finite x");
    assert!(projected[1].is_finite(), "Non-finite y");
    assert!(bounds.contains(&projected), "Outside bounds");
}

// ============================================================================
// ADVERSARIAL 7: Exactly Coincident Boundaries
// Constraints that share a boundary should not cause issues.
// ============================================================================

#[test]
fn coincident_boundaries() {
    // Two constraints that meet at x = 50
    let constraints: Vec<ConstraintRef> = vec![
        boxed(LinearConstraint::new(Vector::from_slice(&[1.0, 0.0]), 50.0)),   // x ≤ 50
        boxed(LinearConstraint::new(Vector::from_slice(&[-1.0, 0.0]), -50.0)), // x ≥ 50 (i.e., -x ≤ -50)
    ];

    // Point at x = 60
    let point = Vector::from_slice(&[60.0, 25.0]);

    let projected = project_convex(&point, &constraints);

    // Should land at x = 50
    assert!(
        (projected[0] - 50.0).abs() < TOLERANCE,
        "Did not land on coincident boundary: x = {}",
        projected[0]
    );
}

// ============================================================================
// ADVERSARIAL 8: Empty Interior (Line Constraint)
// Feasible region is a line, not a full-dimensional region.
// ============================================================================

#[test]
fn line_constraint() {
    // Constrain to the line x = y (via two halfspaces)
    let constraints: Vec<ConstraintRef> = vec![
        boxed(LinearConstraint::new(Vector::from_slice(&[1.0, -1.0]), EPSILON)),  // x - y ≤ ε
        boxed(LinearConstraint::new(Vector::from_slice(&[-1.0, 1.0]), EPSILON)), // -x + y ≤ ε
        boxed(LinearConstraint::new(Vector::from_slice(&[1.0, 0.0]), 100.0)),     // x ≤ 100
        boxed(LinearConstraint::new(Vector::from_slice(&[-1.0, 0.0]), 0.0)),      // x ≥ 0
    ];

    let point = Vector::from_slice(&[30.0, 70.0]);

    let projected = project_convex(&point, &constraints);

    // Should be close to the line x = y
    let line_error = (projected[0] - projected[1]).abs();
    assert!(
        line_error < TOLERANCE * 100.0,
        "Not on line x=y: ({}, {}), error = {}",
        projected[0], projected[1], line_error
    );
}

// ============================================================================
// ADVERSARIAL 9: Rapid Dimension Changes
// Project same point many times with slightly varying bounds.
// ============================================================================

#[test]
fn rapid_bound_changes() {
    let point = Vector::from_slice(&[150.0, 150.0]);

    let mut prev_projected: Option<Vector> = None;

    for i in 0..100 {
        let offset = (i as f64) * 0.1;
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0 + offset, 100.0 + offset]),
        );

        let projected = bounds.project(&point);

        // Each projection should be valid
        assert!(bounds.contains(&projected), "Invalid at iteration {}", i);

        // Changes should be smooth (not jumping around)
        if let Some(prev) = &prev_projected {
            let change = projected.distance(prev);
            assert!(
                change < 1.0,
                "Large jump at iteration {}: change = {}",
                i, change
            );
        }

        prev_projected = Some(projected);
    }
}

// ============================================================================
// ADVERSARIAL 10: Contradictory Constraints (Should Fail Gracefully)
// If constraints are unsatisfiable, should not loop forever.
// ============================================================================

#[test]
fn contradictory_constraints_terminate() {
    // x ≤ 0 and x ≥ 1 are contradictory
    let constraints: Vec<ConstraintRef> = vec![
        boxed(LinearConstraint::new(Vector::from_slice(&[1.0, 0.0]), 0.0)),   // x ≤ 0
        boxed(LinearConstraint::new(Vector::from_slice(&[-1.0, 0.0]), -1.0)), // x ≥ 1
    ];

    let point = Vector::from_slice(&[50.0, 50.0]);

    // Should terminate (not loop forever)
    // The result may not satisfy all constraints, but it should complete
    let start = std::time::Instant::now();
    let _projected = project_convex(&point, &constraints);
    let elapsed = start.elapsed();

    // Should complete quickly (< 100ms)
    assert!(
        elapsed.as_millis() < 100,
        "Took too long: {}ms",
        elapsed.as_millis()
    );
}
