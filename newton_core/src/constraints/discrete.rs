//! Discrete constraint implementation.
//!
//! Restricts values to a finite set of allowed points (e.g., grid snapping).
//! This is a NONCONVEX constraint.

use crate::linalg::Vector;
use crate::constraints::Constraint;
use crate::constants::EPSILON;
use serde::{Serialize, Deserialize};

/// Discrete constraint - values must be in a finite set.
///
/// The feasible region is a finite set of points:
/// `x ∈ {v1, v2, ..., vn}`
///
/// This is a NONCONVEX constraint. Projection returns the nearest
/// allowed point.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DiscreteConstraint {
    /// Allowed values
    allowed: Vec<Vector>,
    /// Dimension
    dim: usize,
}

impl DiscreteConstraint {
    /// Create a discrete constraint from a list of allowed values.
    ///
    /// # Arguments
    /// * `allowed` - The set of allowed points
    ///
    /// # Panics
    /// Panics if the allowed set is empty or if dimensions don't match.
    pub fn new(allowed: Vec<Vector>) -> Self {
        assert!(!allowed.is_empty(), "Discrete constraint must have at least one allowed value");
        let dim = allowed[0].dim();
        for v in &allowed {
            assert_eq!(v.dim(), dim, "All allowed values must have same dimension");
        }
        Self { allowed, dim }
    }

    /// Create a grid constraint (snap to grid).
    ///
    /// # Arguments
    /// * `dim` - Number of dimensions
    /// * `spacing` - Grid spacing in each dimension
    /// * `bounds` - Region to generate grid points within (min, max per dimension)
    pub fn grid(dim: usize, spacing: f64, bounds: &[(f64, f64)]) -> Self {
        assert_eq!(bounds.len(), dim);
        assert!(spacing > EPSILON, "Grid spacing must be positive");

        let mut allowed = Vec::new();

        // Generate grid points recursively
        fn generate_grid(
            dim: usize,
            current_dim: usize,
            spacing: f64,
            bounds: &[(f64, f64)],
            current: &mut Vec<f64>,
            allowed: &mut Vec<Vector>,
        ) {
            if current_dim == dim {
                allowed.push(Vector::from_slice(current));
                return;
            }

            let (min, max) = bounds[current_dim];
            let mut val = min;
            while val <= max + EPSILON {
                current.push(val);
                generate_grid(dim, current_dim + 1, spacing, bounds, current, allowed);
                current.pop();
                val += spacing;
            }
        }

        let mut current = Vec::with_capacity(dim);
        generate_grid(dim, 0, spacing, bounds, &mut current, &mut allowed);

        Self { allowed, dim }
    }

    /// Create a 1D discrete constraint from allowed scalar values.
    pub fn from_scalars(values: &[f64]) -> Self {
        let allowed: Vec<Vector> = values.iter().map(|&v| Vector::from_slice(&[v])).collect();
        Self::new(allowed)
    }

    /// Get the allowed values.
    pub fn allowed(&self) -> &[Vector] {
        &self.allowed
    }

    /// Find the nearest allowed value to a point.
    pub fn nearest(&self, point: &Vector) -> &Vector {
        self.allowed
            .iter()
            .min_by(|a, b| {
                let dist_a = point.distance(a);
                let dist_b = point.distance(b);
                dist_a.partial_cmp(&dist_b).unwrap_or(std::cmp::Ordering::Equal)
            })
            .unwrap() // Safe because we enforce non-empty in constructor
    }
}

impl Constraint for DiscreteConstraint {
    fn satisfied(&self, point: &Vector) -> bool {
        assert_eq!(point.dim(), self.dim);
        self.allowed.iter().any(|v| point.approx_eq(v))
    }

    fn distance(&self, point: &Vector) -> f64 {
        assert_eq!(point.dim(), self.dim);
        let nearest = self.nearest(point);
        let dist = point.distance(nearest);
        if dist < EPSILON {
            -f64::INFINITY // On an allowed point
        } else {
            dist // Distance to nearest allowed point
        }
    }

    fn project(&self, point: &Vector) -> Vector {
        assert_eq!(point.dim(), self.dim);
        self.nearest(point).clone()
    }

    fn describe(&self) -> String {
        if self.allowed.len() <= 5 {
            format!(
                "DiscreteConstraint: x ∈ {:?}",
                self.allowed.iter().map(|v| v.as_slice()).collect::<Vec<_>>()
            )
        } else {
            format!(
                "DiscreteConstraint: x ∈ {{...}} ({} values)",
                self.allowed.len()
            )
        }
    }

    fn is_convex(&self) -> bool {
        false // Discrete constraints are NONCONVEX (unless single point)
    }

    fn dim(&self) -> usize {
        self.dim
    }

    fn clone_box(&self) -> Box<dyn Constraint> {
        Box::new(self.clone())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_discrete_satisfied() {
        let constraint = DiscreteConstraint::from_scalars(&[0.0, 5.0, 10.0]);

        assert!(constraint.satisfied(&Vector::from_slice(&[0.0])));
        assert!(constraint.satisfied(&Vector::from_slice(&[5.0])));
        assert!(constraint.satisfied(&Vector::from_slice(&[10.0])));
        assert!(!constraint.satisfied(&Vector::from_slice(&[3.0])));
    }

    #[test]
    fn test_discrete_project() {
        let constraint = DiscreteConstraint::from_scalars(&[0.0, 5.0, 10.0]);

        // Should snap to nearest
        assert!((constraint.project(&Vector::from_slice(&[2.0]))[0] - 0.0).abs() < EPSILON);
        assert!((constraint.project(&Vector::from_slice(&[3.0]))[0] - 5.0).abs() < EPSILON);
        assert!((constraint.project(&Vector::from_slice(&[8.0]))[0] - 10.0).abs() < EPSILON);
    }

    #[test]
    fn test_discrete_2d() {
        let allowed = vec![
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[10.0, 0.0]),
            Vector::from_slice(&[0.0, 10.0]),
            Vector::from_slice(&[10.0, 10.0]),
        ];
        let constraint = DiscreteConstraint::new(allowed);

        // Point (3, 2) should snap to (0, 0)
        let projected = constraint.project(&Vector::from_slice(&[3.0, 2.0]));
        assert!(projected.approx_eq(&Vector::from_slice(&[0.0, 0.0])));

        // Point (8, 9) should snap to (10, 10)
        let projected = constraint.project(&Vector::from_slice(&[8.0, 9.0]));
        assert!(projected.approx_eq(&Vector::from_slice(&[10.0, 10.0])));
    }

    #[test]
    fn test_discrete_grid() {
        let constraint = DiscreteConstraint::grid(2, 10.0, &[(0.0, 20.0), (0.0, 20.0)]);

        // Should have 9 points: (0,0), (0,10), (0,20), (10,0), (10,10), (10,20), (20,0), (20,10), (20,20)
        assert_eq!(constraint.allowed().len(), 9);

        // (15, 15) should snap to (20, 20) or (10, 10) or (10, 20) or (20, 10)
        let projected = constraint.project(&Vector::from_slice(&[15.0, 15.0]));
        assert!(constraint.satisfied(&projected));
    }

    #[test]
    fn test_discrete_is_nonconvex() {
        let constraint = DiscreteConstraint::from_scalars(&[0.0, 10.0]);
        assert!(!constraint.is_convex());
    }
}
