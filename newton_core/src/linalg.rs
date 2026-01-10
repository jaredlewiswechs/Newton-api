//! Linear algebra primitives.
//!
//! Provides a simple, efficient Vector type for n-dimensional operations.
//! Designed for determinism: all operations produce bitwise-identical results.

use std::ops::{Add, Sub, Mul, Div, Index, IndexMut, Neg};
use std::cmp::Ordering;
use serde::{Serialize, Deserialize};
use crate::constants::{EPSILON, TOLERANCE};

/// An n-dimensional vector of f64 values.
///
/// This is the fundamental numeric type in Newton. All geometric operations
/// are expressed in terms of Vector.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Vector {
    data: Vec<f64>,
}

impl Vector {
    /// Create a new vector from a slice.
    pub fn from_slice(data: &[f64]) -> Self {
        Self { data: data.to_vec() }
    }

    /// Create a zero vector of given dimension.
    pub fn zeros(dim: usize) -> Self {
        Self { data: vec![0.0; dim] }
    }

    /// Create a vector filled with a constant value.
    pub fn from_elem(dim: usize, value: f64) -> Self {
        Self { data: vec![value; dim] }
    }

    /// Create a unit vector along axis i.
    pub fn unit(dim: usize, axis: usize) -> Self {
        let mut data = vec![0.0; dim];
        if axis < dim {
            data[axis] = 1.0;
        }
        Self { data }
    }

    /// Get the dimension of the vector.
    #[inline]
    pub fn dim(&self) -> usize {
        self.data.len()
    }

    /// Get the dimension (alias for compatibility).
    #[inline]
    pub fn len(&self) -> usize {
        self.data.len()
    }

    /// Check if vector is empty.
    #[inline]
    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }

    /// Compute the Euclidean norm (L2 norm).
    pub fn norm(&self) -> f64 {
        self.norm_squared().sqrt()
    }

    /// Compute the squared Euclidean norm.
    pub fn norm_squared(&self) -> f64 {
        self.data.iter().map(|x| x * x).sum()
    }

    /// Compute the dot product with another vector.
    pub fn dot(&self, other: &Vector) -> f64 {
        assert_eq!(self.dim(), other.dim(), "Vector dimensions must match for dot product");
        self.data.iter().zip(other.data.iter()).map(|(a, b)| a * b).sum()
    }

    /// Normalize the vector to unit length.
    /// Returns zero vector if norm is near zero.
    pub fn normalize(&self) -> Self {
        let n = self.norm();
        if n < EPSILON {
            Self::zeros(self.dim())
        } else {
            self / n
        }
    }

    /// Clamp each component to [min, max].
    pub fn clamp(&self, min: f64, max: f64) -> Self {
        Self {
            data: self.data.iter().map(|x| x.clamp(min, max)).collect(),
        }
    }

    /// Component-wise clamp to bounds.
    pub fn clamp_vec(&self, min: &Vector, max: &Vector) -> Self {
        assert_eq!(self.dim(), min.dim());
        assert_eq!(self.dim(), max.dim());
        Self {
            data: self.data.iter()
                .zip(min.data.iter())
                .zip(max.data.iter())
                .map(|((x, lo), hi)| x.clamp(*lo, *hi))
                .collect(),
        }
    }

    /// Compute distance to another vector.
    pub fn distance(&self, other: &Vector) -> f64 {
        (self - other).norm()
    }

    /// Check if all components are finite.
    pub fn is_finite(&self) -> bool {
        self.data.iter().all(|x| x.is_finite())
    }

    /// Check if any component is NaN.
    pub fn has_nan(&self) -> bool {
        self.data.iter().any(|x| x.is_nan())
    }

    /// Get an iterator over components.
    pub fn iter(&self) -> impl Iterator<Item = &f64> {
        self.data.iter()
    }

    /// Get a mutable iterator over components.
    pub fn iter_mut(&mut self) -> impl Iterator<Item = &mut f64> {
        self.data.iter_mut()
    }

    /// Component-wise multiplication.
    pub fn component_mul(&self, other: &Vector) -> Self {
        assert_eq!(self.dim(), other.dim());
        Self {
            data: self.data.iter().zip(other.data.iter()).map(|(a, b)| a * b).collect(),
        }
    }

    /// Component-wise division.
    pub fn component_div(&self, other: &Vector) -> Self {
        assert_eq!(self.dim(), other.dim());
        Self {
            data: self.data.iter().zip(other.data.iter())
                .map(|(a, b)| a / (b + EPSILON))
                .collect(),
        }
    }

    /// Apply sqrt to each component.
    pub fn sqrt(&self) -> Self {
        Self {
            data: self.data.iter().map(|x| x.sqrt()).collect(),
        }
    }

    /// Lexicographic comparison for deterministic ordering.
    pub fn lexicographic_cmp(&self, other: &Vector) -> Ordering {
        for (a, b) in self.data.iter().zip(other.data.iter()) {
            match a.partial_cmp(b) {
                Some(Ordering::Equal) => continue,
                Some(ord) => return ord,
                None => {
                    // Handle NaN: treat as equal for stability
                    if a.is_nan() && b.is_nan() {
                        continue;
                    } else if a.is_nan() {
                        return Ordering::Greater;
                    } else {
                        return Ordering::Less;
                    }
                }
            }
        }
        self.dim().cmp(&other.dim())
    }

    /// Check approximate equality within tolerance.
    pub fn approx_eq(&self, other: &Vector) -> bool {
        if self.dim() != other.dim() {
            return false;
        }
        self.distance(other) < TOLERANCE
    }

    /// Get raw data slice.
    pub fn as_slice(&self) -> &[f64] {
        &self.data
    }
}

// Index traits
impl Index<usize> for Vector {
    type Output = f64;
    fn index(&self, index: usize) -> &Self::Output {
        &self.data[index]
    }
}

impl IndexMut<usize> for Vector {
    fn index_mut(&mut self, index: usize) -> &mut Self::Output {
        &mut self.data[index]
    }
}

// Arithmetic with owned values
impl Add for Vector {
    type Output = Vector;
    fn add(self, rhs: Vector) -> Self::Output {
        &self + &rhs
    }
}

impl Sub for Vector {
    type Output = Vector;
    fn sub(self, rhs: Vector) -> Self::Output {
        &self - &rhs
    }
}

// Arithmetic with references
impl Add for &Vector {
    type Output = Vector;
    fn add(self, rhs: &Vector) -> Self::Output {
        assert_eq!(self.dim(), rhs.dim(), "Vector dimensions must match for addition");
        Vector {
            data: self.data.iter().zip(rhs.data.iter()).map(|(a, b)| a + b).collect(),
        }
    }
}

impl Sub for &Vector {
    type Output = Vector;
    fn sub(self, rhs: &Vector) -> Self::Output {
        assert_eq!(self.dim(), rhs.dim(), "Vector dimensions must match for subtraction");
        Vector {
            data: self.data.iter().zip(rhs.data.iter()).map(|(a, b)| a - b).collect(),
        }
    }
}

// Scalar multiplication
impl Mul<f64> for Vector {
    type Output = Vector;
    fn mul(self, rhs: f64) -> Self::Output {
        &self * rhs
    }
}

impl Mul<f64> for &Vector {
    type Output = Vector;
    fn mul(self, rhs: f64) -> Self::Output {
        Vector {
            data: self.data.iter().map(|x| x * rhs).collect(),
        }
    }
}

impl Div<f64> for Vector {
    type Output = Vector;
    fn div(self, rhs: f64) -> Self::Output {
        &self / rhs
    }
}

impl Div<f64> for &Vector {
    type Output = Vector;
    fn div(self, rhs: f64) -> Self::Output {
        Vector {
            data: self.data.iter().map(|x| x / rhs).collect(),
        }
    }
}

impl Neg for Vector {
    type Output = Vector;
    fn neg(self) -> Self::Output {
        Vector {
            data: self.data.iter().map(|x| -x).collect(),
        }
    }
}

impl Neg for &Vector {
    type Output = Vector;
    fn neg(self) -> Self::Output {
        Vector {
            data: self.data.iter().map(|x| -x).collect(),
        }
    }
}

// FromIterator for convenient construction
impl FromIterator<f64> for Vector {
    fn from_iter<I: IntoIterator<Item = f64>>(iter: I) -> Self {
        Self { data: iter.into_iter().collect() }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_vector_creation() {
        let v = Vector::from_slice(&[1.0, 2.0, 3.0]);
        assert_eq!(v.dim(), 3);
        assert_eq!(v[0], 1.0);
        assert_eq!(v[1], 2.0);
        assert_eq!(v[2], 3.0);
    }

    #[test]
    fn test_vector_zeros() {
        let v = Vector::zeros(5);
        assert_eq!(v.dim(), 5);
        assert!(v.iter().all(|&x| x == 0.0));
    }

    #[test]
    fn test_vector_norm() {
        let v = Vector::from_slice(&[3.0, 4.0]);
        assert!((v.norm() - 5.0).abs() < EPSILON);
    }

    #[test]
    fn test_vector_dot() {
        let a = Vector::from_slice(&[1.0, 2.0, 3.0]);
        let b = Vector::from_slice(&[4.0, 5.0, 6.0]);
        assert!((a.dot(&b) - 32.0).abs() < EPSILON);
    }

    #[test]
    fn test_vector_normalize() {
        let v = Vector::from_slice(&[3.0, 4.0]);
        let n = v.normalize();
        assert!((n.norm() - 1.0).abs() < EPSILON);
    }

    #[test]
    fn test_vector_arithmetic() {
        let a = Vector::from_slice(&[1.0, 2.0]);
        let b = Vector::from_slice(&[3.0, 4.0]);

        let sum = &a + &b;
        assert_eq!(sum[0], 4.0);
        assert_eq!(sum[1], 6.0);

        let diff = &b - &a;
        assert_eq!(diff[0], 2.0);
        assert_eq!(diff[1], 2.0);

        let scaled = &a * 2.0;
        assert_eq!(scaled[0], 2.0);
        assert_eq!(scaled[1], 4.0);
    }

    #[test]
    fn test_vector_clamp() {
        let v = Vector::from_slice(&[-5.0, 50.0, 150.0]);
        let clamped = v.clamp(0.0, 100.0);
        assert_eq!(clamped[0], 0.0);
        assert_eq!(clamped[1], 50.0);
        assert_eq!(clamped[2], 100.0);
    }

    #[test]
    fn test_lexicographic_cmp() {
        let a = Vector::from_slice(&[1.0, 2.0, 3.0]);
        let b = Vector::from_slice(&[1.0, 2.0, 4.0]);
        let c = Vector::from_slice(&[1.0, 3.0, 0.0]);

        assert_eq!(a.lexicographic_cmp(&b), Ordering::Less);
        assert_eq!(b.lexicographic_cmp(&a), Ordering::Greater);
        assert_eq!(a.lexicographic_cmp(&c), Ordering::Less);
    }

    #[test]
    fn test_distance() {
        let a = Vector::from_slice(&[0.0, 0.0]);
        let b = Vector::from_slice(&[3.0, 4.0]);
        assert!((a.distance(&b) - 5.0).abs() < EPSILON);
    }
}
