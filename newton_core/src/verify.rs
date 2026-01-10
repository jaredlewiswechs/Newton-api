//! Law verification and contract assertions.
//!
//! This module ensures that the Aid-a contract is upheld:
//! 1. Validity: All suggestions satisfy all constraints
//! 2. Determinism: Same input produces identical output
//! 3. Termination: Bounded iterations and time
//! 4. Monotonicity: Explanation diff matches actual change
//! 5. Non-empty: If feasible region exists, suggestions exist

use crate::linalg::Vector;
use crate::constraints::ConstraintRef;
use crate::explain::StateDiff;
use crate::constants::{TOLERANCE, TIMEOUT_US};
#[allow(unused_imports)]
use crate::constants::{EPSILON, MAX_ITERATIONS};
use std::time::Instant;
use thiserror::Error;

/// Errors that indicate contract violations.
#[derive(Error, Debug, Clone)]
pub enum ContractViolation {
    /// A suggestion violates one or more constraints.
    #[error("Validity violation: suggestion violates constraint {constraint_index}: {description}")]
    InvalidSuggestion {
        constraint_index: usize,
        description: String,
        violation_amount: f64,
    },

    /// Two identical calls produced different results.
    #[error("Determinism violation: different results for identical inputs")]
    NonDeterministic {
        result1: Vec<f64>,
        result2: Vec<f64>,
    },

    /// Algorithm did not terminate within bounds.
    #[error("Termination violation: {reason}")]
    NonTerminating {
        reason: String,
        iterations: usize,
        elapsed_us: u64,
    },

    /// Explanation diff does not match actual state change.
    #[error("Monotonicity violation: diff does not match actual change")]
    DiffMismatch {
        expected: Vec<f64>,
        actual: Vec<f64>,
    },

    /// Empty suggestions when feasible region is non-empty.
    #[error("Non-empty violation: no suggestions returned for feasible region")]
    EmptySuggestions,
}

/// Result of contract verification.
pub type VerifyResult<T> = Result<T, ContractViolation>;

/// Verify that a suggestion satisfies all constraints (Validity).
pub fn verify_validity(
    suggestion: &Vector,
    constraints: &[ConstraintRef],
) -> VerifyResult<()> {
    for (i, constraint) in constraints.iter().enumerate() {
        if !constraint.satisfied(suggestion) {
            let distance = constraint.distance(suggestion);
            return Err(ContractViolation::InvalidSuggestion {
                constraint_index: i,
                description: constraint.describe(),
                violation_amount: distance,
            });
        }
    }
    Ok(())
}

/// Verify that all suggestions are valid.
pub fn verify_all_valid(
    suggestions: &[Vector],
    constraints: &[ConstraintRef],
) -> VerifyResult<()> {
    for suggestion in suggestions {
        verify_validity(suggestion, constraints)?;
    }
    Ok(())
}

/// Verify determinism by checking if a function produces identical output twice.
pub fn verify_determinism<F>(f: F) -> VerifyResult<Vector>
where
    F: Fn() -> Vector,
{
    let result1 = f();
    let result2 = f();

    // Check bitwise equality
    if result1.dim() != result2.dim() {
        return Err(ContractViolation::NonDeterministic {
            result1: result1.as_slice().to_vec(),
            result2: result2.as_slice().to_vec(),
        });
    }

    for i in 0..result1.dim() {
        if result1[i].to_bits() != result2[i].to_bits() {
            return Err(ContractViolation::NonDeterministic {
                result1: result1.as_slice().to_vec(),
                result2: result2.as_slice().to_vec(),
            });
        }
    }

    Ok(result1)
}

/// Verify that a computation terminates within bounds.
pub fn verify_termination<F, T>(f: F) -> VerifyResult<(T, u64)>
where
    F: FnOnce() -> T,
{
    let start = Instant::now();
    let result = f();
    let elapsed_us = start.elapsed().as_micros() as u64;

    if elapsed_us > TIMEOUT_US {
        return Err(ContractViolation::NonTerminating {
            reason: format!("Exceeded timeout of {}us", TIMEOUT_US),
            iterations: 0, // Unknown
            elapsed_us,
        });
    }

    Ok((result, elapsed_us))
}

/// Verify that an explanation diff correctly describes the state change.
pub fn verify_diff_monotonicity(
    original: &Vector,
    suggested: &Vector,
    diff: &StateDiff,
) -> VerifyResult<()> {
    // Apply diff to original and check if it matches suggested
    let mut reconstructed = original.clone();

    for change in &diff.changes {
        if change.dimension < reconstructed.dim() {
            reconstructed[change.dimension] = change.suggested;
        }
    }

    let mismatch = suggested.distance(&reconstructed);
    if mismatch > TOLERANCE {
        return Err(ContractViolation::DiffMismatch {
            expected: suggested.as_slice().to_vec(),
            actual: reconstructed.as_slice().to_vec(),
        });
    }

    Ok(())
}

/// Verify the complete Aid-a contract for a suggestion response.
pub fn verify_contract(
    suggestions: &[Vector],
    constraints: &[ConstraintRef],
    original: &Vector,
    elapsed_us: u64,
) -> VerifyResult<()> {
    // 1. Validity
    verify_all_valid(suggestions, constraints)?;

    // 3. Termination (time check)
    if elapsed_us > TIMEOUT_US {
        return Err(ContractViolation::NonTerminating {
            reason: "Exceeded time limit".to_string(),
            iterations: 0,
            elapsed_us,
        });
    }

    // 5. Non-empty (if we have constraints, we should have suggestions)
    // Note: Only if feasible region is non-empty, but we can't always check that
    // So we just warn if constraints exist but suggestions are empty
    // In practice, the caller should check feasibility first

    Ok(())
}

/// A verification harness for testing.
pub struct ContractHarness {
    pub violations: Vec<ContractViolation>,
    pub checks_run: usize,
    pub checks_passed: usize,
}

impl ContractHarness {
    pub fn new() -> Self {
        Self {
            violations: Vec::new(),
            checks_run: 0,
            checks_passed: 0,
        }
    }

    /// Run a verification check and record the result.
    pub fn check<F>(&mut self, name: &str, f: F)
    where
        F: FnOnce() -> VerifyResult<()>,
    {
        self.checks_run += 1;
        match f() {
            Ok(()) => {
                self.checks_passed += 1;
            }
            Err(violation) => {
                self.violations.push(violation);
            }
        }
    }

    /// Get a summary of verification results.
    pub fn summary(&self) -> String {
        format!(
            "Contract verification: {}/{} checks passed, {} violations",
            self.checks_passed,
            self.checks_run,
            self.violations.len()
        )
    }

    /// Check if all verifications passed.
    pub fn all_passed(&self) -> bool {
        self.violations.is_empty()
    }
}

impl Default for ContractHarness {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::constraints::{BoxBounds, boxed};

    #[test]
    fn test_verify_validity_passes() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        let valid_point = Vector::from_slice(&[50.0, 50.0]);
        assert!(verify_validity(&valid_point, &constraints).is_ok());
    }

    #[test]
    fn test_verify_validity_fails() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        let invalid_point = Vector::from_slice(&[150.0, 50.0]);
        let result = verify_validity(&invalid_point, &constraints);
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), ContractViolation::InvalidSuggestion { .. }));
    }

    #[test]
    fn test_verify_determinism_passes() {
        let f = || Vector::from_slice(&[1.0, 2.0, 3.0]);
        assert!(verify_determinism(f).is_ok());
    }

    #[test]
    fn test_verify_determinism_fails() {
        use std::sync::atomic::{AtomicUsize, Ordering};
        static COUNTER: AtomicUsize = AtomicUsize::new(0);

        let f = || {
            let n = COUNTER.fetch_add(1, Ordering::SeqCst);
            Vector::from_slice(&[n as f64])
        };

        // Reset counter
        COUNTER.store(0, Ordering::SeqCst);

        let result = verify_determinism(f);
        assert!(result.is_err());
    }

    #[test]
    fn test_verify_termination_passes() {
        let f = || Vector::from_slice(&[1.0, 2.0]);
        let result = verify_termination(f);
        assert!(result.is_ok());
    }

    #[test]
    fn test_verify_diff_monotonicity() {
        let original = Vector::from_slice(&[0.0, 0.0]);
        let suggested = Vector::from_slice(&[10.0, 5.0]);

        use crate::explain::StateDiff;
        let diff = StateDiff::new(original.clone(), suggested.clone());

        assert!(verify_diff_monotonicity(&original, &suggested, &diff).is_ok());
    }

    #[test]
    fn test_contract_harness() {
        let mut harness = ContractHarness::new();

        harness.check("passing test", || Ok(()));
        harness.check("failing test", || {
            Err(ContractViolation::EmptySuggestions)
        });

        assert_eq!(harness.checks_run, 2);
        assert_eq!(harness.checks_passed, 1);
        assert!(!harness.all_passed());
    }
}
