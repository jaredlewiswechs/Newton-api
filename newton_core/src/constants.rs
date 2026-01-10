//! Numeric constants and policy definitions.
//!
//! These constants are frozen as part of AIDA_SPEC.md v1.0.

/// Machine epsilon for floating point comparisons.
/// Used to determine if two values are "equal" within floating point precision.
pub const EPSILON: f64 = 1e-10;

/// Convergence tolerance for projection algorithms.
/// Iteration stops when change is below this threshold.
pub const TOLERANCE: f64 = 1e-8;

/// Maximum iterations for Dykstra's algorithm.
/// Prevents infinite loops in pathological cases.
pub const MAX_ITERATIONS: usize = 100;

/// Maximum candidates to generate in nonconvex search.
/// Bounds computational cost.
pub const MAX_CANDIDATES: usize = 24;

/// Search radius for local candidate generation.
/// Defines the maximum distance from convex projection to search.
pub const SEARCH_RADIUS: f64 = 100.0;

/// Timeout for suggestion generation (microseconds).
pub const TIMEOUT_US: u64 = 500_000;

/// Shell radii for local search (concentric expansion).
pub const SHELL_RADII: [f64; 5] = [1.0, 2.0, 4.0, 8.0, SEARCH_RADIUS];

/// Dimension for angular sampling in shell generation.
pub const SHELL_ANGULAR_SAMPLES: usize = 8;

/// Safe division that avoids division by zero.
#[inline]
pub fn safe_divide(a: f64, b: f64) -> f64 {
    a / (b + EPSILON)
}

/// Check if a value is effectively zero.
#[inline]
pub fn is_near_zero(x: f64) -> bool {
    x.abs() < EPSILON
}

/// Check if two values are approximately equal.
#[inline]
pub fn approx_eq(a: f64, b: f64) -> bool {
    (a - b).abs() < TOLERANCE
}

/// Check if two values are approximately equal with custom tolerance.
#[inline]
pub fn approx_eq_tol(a: f64, b: f64, tol: f64) -> bool {
    (a - b).abs() < tol
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_safe_divide() {
        assert!(safe_divide(1.0, 0.0).is_finite());
        assert!(approx_eq(safe_divide(10.0, 2.0), 5.0));
    }

    #[test]
    fn test_is_near_zero() {
        assert!(is_near_zero(0.0));
        assert!(is_near_zero(1e-11));
        assert!(!is_near_zero(1e-9));
    }

    #[test]
    fn test_approx_eq() {
        assert!(approx_eq(1.0, 1.0 + 1e-9));
        assert!(!approx_eq(1.0, 1.0 + 1e-7));
    }
}
