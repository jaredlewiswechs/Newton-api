//! Box bounds constraint implementation.
//!
//! Represents axis-aligned rectangular bounds: min ≤ x ≤ max per dimension.

use crate::linalg::Vector;
use crate::constraints::Constraint;
use crate::constants::EPSILON;
use serde::{Serialize, Deserialize};

/// Axis-aligned box bounds constraint.
///
/// The feasible region is the set of all points x where:
/// `min[i] ≤ x[i] ≤ max[i]` for all dimensions i.
///
/// This is a convex constraint with O(n) projection time.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BoxBounds {
    /// Minimum values per dimension
    min: Vector,
    /// Maximum values per dimension
    max: Vector,
    /// Whether constraints were added in reverse order (for order-independence testing)
    #[serde(skip)]
    reversed: bool,
}

impl BoxBounds {
    /// Create new box bounds from min and max vectors.
    ///
    /// # Arguments
    /// * `min` - Minimum values per dimension
    /// * `max` - Maximum values per dimension
    ///
    /// # Panics
    /// Panics if dimensions don't match or if min > max in any dimension.
    pub fn new(min: Vector, max: Vector) -> Self {
        assert_eq!(min.dim(), max.dim(), "Dimensions must match");
        for i in 0..min.dim() {
            assert!(
                min[i] <= max[i] + EPSILON,
                "min must be <= max in dimension {} (got {} > {})",
                i, min[i], max[i]
            );
        }
        Self { min, max, reversed: false }
    }

    /// Create new box bounds with reversed internal ordering.
    /// Used for testing order-independence of projection.
    pub fn new_reversed(min: Vector, max: Vector) -> Self {
        let mut bounds = Self::new(min, max);
        bounds.reversed = true;
        bounds
    }

    /// Create a unit hypercube [0,1]^n.
    pub fn unit_cube(dim: usize) -> Self {
        Self::new(Vector::zeros(dim), Vector::from_elem(dim, 1.0))
    }

    /// Create bounds centered at origin with given half-extents.
    pub fn centered(half_extents: Vector) -> Self {
        Self::new(-&half_extents, half_extents)
    }

    /// Get the minimum bounds.
    pub fn min(&self) -> &Vector {
        &self.min
    }

    /// Get the maximum bounds.
    pub fn max(&self) -> &Vector {
        &self.max
    }

    /// Get the center of the box.
    pub fn center(&self) -> Vector {
        (&self.min + &self.max) / 2.0
    }

    /// Get the size (extent) in each dimension.
    pub fn size(&self) -> Vector {
        &self.max - &self.min
    }

    /// Check if a point is inside the box.
    pub fn contains(&self, point: &Vector) -> bool {
        self.satisfied(point)
    }

    /// Expand the box by a margin in all directions.
    pub fn expand(&self, margin: f64) -> Self {
        let margin_vec = Vector::from_elem(self.dim(), margin);
        Self::new(&self.min - &margin_vec, &self.max + &margin_vec)
    }

    /// Get the dimension of the constraint.
    pub fn dimension(&self) -> usize {
        self.min.dim()
    }
}

impl Constraint for BoxBounds {
    fn satisfied(&self, point: &Vector) -> bool {
        assert_eq!(point.dim(), self.dim());
        for i in 0..self.dim() {
            if point[i] < self.min[i] - EPSILON || point[i] > self.max[i] + EPSILON {
                return false;
            }
        }
        true
    }

    fn distance(&self, point: &Vector) -> f64 {
        assert_eq!(point.dim(), self.dim());
        let mut dist_sq = 0.0;
        for i in 0..self.dim() {
            if point[i] < self.min[i] {
                dist_sq += (self.min[i] - point[i]).powi(2);
            } else if point[i] > self.max[i] {
                dist_sq += (point[i] - self.max[i]).powi(2);
            }
        }
        dist_sq.sqrt()
    }

    fn project(&self, point: &Vector) -> Vector {
        assert_eq!(point.dim(), self.dim());

        // Process dimensions in order (or reversed for testing)
        let indices: Vec<usize> = if self.reversed {
            (0..self.dim()).rev().collect()
        } else {
            (0..self.dim()).collect()
        };

        let mut result = point.clone();
        for i in indices {
            result[i] = result[i].clamp(self.min[i], self.max[i]);
        }
        result
    }

    fn describe(&self) -> String {
        format!(
            "BoxBounds: {} ≤ x ≤ {}",
            format!("{:?}", self.min.as_slice()),
            format!("{:?}", self.max.as_slice())
        )
    }

    fn is_convex(&self) -> bool {
        true
    }

    fn dim(&self) -> usize {
        self.min.dim()
    }

    fn clone_box(&self) -> Box<dyn Constraint> {
        Box::new(self.clone())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_box_bounds_satisfied() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        assert!(bounds.satisfied(&Vector::from_slice(&[50.0, 50.0])));
        assert!(bounds.satisfied(&Vector::from_slice(&[0.0, 0.0])));
        assert!(bounds.satisfied(&Vector::from_slice(&[100.0, 100.0])));
        assert!(!bounds.satisfied(&Vector::from_slice(&[150.0, 50.0])));
        assert!(!bounds.satisfied(&Vector::from_slice(&[-10.0, 50.0])));
    }

    #[test]
    fn test_box_bounds_project() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        // Point inside - should not move
        let inside = Vector::from_slice(&[50.0, 50.0]);
        let projected = bounds.project(&inside);
        assert!(inside.approx_eq(&projected));

        // Point outside - should project to boundary
        let outside = Vector::from_slice(&[150.0, 50.0]);
        let projected = bounds.project(&outside);
        assert!((projected[0] - 100.0).abs() < EPSILON);
        assert!((projected[1] - 50.0).abs() < EPSILON);

        // Corner case
        let corner = Vector::from_slice(&[150.0, 150.0]);
        let projected = bounds.project(&corner);
        assert!((projected[0] - 100.0).abs() < EPSILON);
        assert!((projected[1] - 100.0).abs() < EPSILON);
    }

    #[test]
    fn test_box_bounds_distance() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        // Inside point - distance 0
        assert_eq!(bounds.distance(&Vector::from_slice(&[50.0, 50.0])), 0.0);

        // Outside point
        let dist = bounds.distance(&Vector::from_slice(&[103.0, 104.0]));
        assert!((dist - 5.0).abs() < EPSILON); // 3-4-5 triangle
    }

    #[test]
    fn test_box_bounds_order_independence() {
        let min = Vector::from_slice(&[0.0, 0.0, 0.0]);
        let max = Vector::from_slice(&[100.0, 100.0, 100.0]);

        let forward = BoxBounds::new(min.clone(), max.clone());
        let reversed = BoxBounds::new_reversed(min, max);

        let point = Vector::from_slice(&[150.0, -50.0, 200.0]);

        let proj_forward = forward.project(&point);
        let proj_reversed = reversed.project(&point);

        assert!(proj_forward.approx_eq(&proj_reversed));
    }

    #[test]
    fn test_box_bounds_idempotent() {
        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        let point = Vector::from_slice(&[150.0, -50.0]);
        let proj1 = bounds.project(&point);
        let proj2 = bounds.project(&proj1);

        assert!(proj1.approx_eq(&proj2));
    }
}
