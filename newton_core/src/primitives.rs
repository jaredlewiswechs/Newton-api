//! Core primitive types for Newton.
//!
//! These types form the foundation of the constraint system:
//! - `NTObject`: The universal primitive (everything is an NTObject)
//! - `Bounds`: Axis-aligned bounding box
//! - `FGState`: The f/g ratio state enumeration
//! - `Delta`: A change vector with metadata

use uuid::Uuid;
use serde::{Serialize, Deserialize};
use crate::linalg::Vector;
use crate::constants::{EPSILON, safe_divide};

/// The f/g ratio state - measures constraint violation relative to effort.
///
/// This is the core signal that drives haptic feedback and UI coloring.
/// The state is computed from the f/g ratio where:
/// - f = violation magnitude (distance to valid set)
/// - g = effort magnitude (size of attempted change)
#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub enum FGState {
    /// f/g = 0. Fully inside bounds, no violation.
    Valid,

    /// 0 < f/g < 1. Inside bounds with margin remaining.
    /// `margin` ∈ (0, 1] where 1.0 = far from boundary, approaching 0 = near boundary.
    Slack {
        /// Remaining margin before hitting boundary (1.0 - f/g)
        margin: f64,
    },

    /// f/g ≈ 1. On the boundary exactly.
    Exact,

    /// f/g > 1. Outside bounds (violation exceeds effort).
    /// `excess` > 0 indicates how far past the boundary.
    Finfr {
        /// Amount by which f/g exceeds 1.0
        excess: f64,
    },
}

/// UI color for constraint state visualization.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Color {
    /// Valid state - green
    Green,
    /// Warning state - yellow
    Yellow,
    /// Violation state - red
    Red,
}

impl FGState {
    /// Create FGState from violation and effort magnitudes.
    ///
    /// # Arguments
    /// * `violation` - Distance from attempted state to valid set
    /// * `effort` - Magnitude of attempted change
    pub fn from_violation(violation: f64, effort: f64) -> Self {
        let fg = safe_divide(violation, effort);

        if fg < EPSILON {
            FGState::Valid
        } else if fg < 1.0 - EPSILON {
            FGState::Slack { margin: 1.0 - fg }
        } else if fg < 1.0 + EPSILON {
            FGState::Exact
        } else {
            FGState::Finfr { excess: fg - 1.0 }
        }
    }

    /// Create FGState directly from f/g ratio.
    pub fn from_ratio(ratio: f64) -> Self {
        if ratio < EPSILON {
            FGState::Valid
        } else if ratio < 1.0 - EPSILON {
            FGState::Slack { margin: 1.0 - ratio }
        } else if ratio < 1.0 + EPSILON {
            FGState::Exact
        } else {
            FGState::Finfr { excess: ratio - 1.0 }
        }
    }

    /// Get the raw f/g ratio value.
    pub fn ratio(&self) -> f64 {
        match self {
            FGState::Valid => 0.0,
            FGState::Slack { margin } => 1.0 - margin,
            FGState::Exact => 1.0,
            FGState::Finfr { excess } => 1.0 + excess,
        }
    }

    /// Haptic amplitude: 0.0 (no feedback) to 1.0 (maximum resistance).
    ///
    /// Monotonic: less margin = stronger feedback.
    /// This drives the "feel" of constraints.
    pub fn haptic_amplitude(&self) -> f64 {
        match self {
            FGState::Valid => 0.0,
            FGState::Slack { margin } => {
                // margin ∈ (0, 1], feedback ∈ [0, 0.3]
                // Less margin = more feedback
                0.3 * (1.0 - margin)
            }
            FGState::Exact => 0.5,
            FGState::Finfr { excess } => {
                // excess > 0, feedback ∈ [0.5, 1.0], capped
                (0.5 + 0.5 * excess.min(1.0)).min(1.0)
            }
        }
    }

    /// UI color signal for constraint state.
    pub fn color(&self) -> Color {
        match self {
            FGState::Valid => Color::Green,
            FGState::Slack { margin } if *margin > 0.5 => Color::Green,
            FGState::Slack { .. } => Color::Yellow,
            FGState::Exact => Color::Yellow,
            FGState::Finfr { .. } => Color::Red,
        }
    }

    /// Check if state represents a valid (non-violating) position.
    pub fn is_valid(&self) -> bool {
        !matches!(self, FGState::Finfr { .. })
    }

    /// Check if state represents a boundary position.
    pub fn is_on_boundary(&self) -> bool {
        matches!(self, FGState::Exact)
    }

    /// Check if state represents a violation.
    pub fn is_violation(&self) -> bool {
        matches!(self, FGState::Finfr { .. })
    }
}

/// Axis-aligned bounding box.
///
/// Defines the valid region for an object's position/size.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Bounds {
    /// Minimum values per dimension
    pub min: Vector,
    /// Maximum values per dimension
    pub max: Vector,
}

impl Bounds {
    /// Create new bounds from min and max vectors.
    ///
    /// # Panics
    /// Panics if dimensions don't match or min > max in any dimension.
    pub fn new(min: Vector, max: Vector) -> Self {
        assert_eq!(min.dim(), max.dim(), "Bounds dimensions must match");
        for i in 0..min.dim() {
            assert!(min[i] <= max[i], "min must be <= max in dimension {}", i);
        }
        Self { min, max }
    }

    /// Create bounds without validation (for internal use).
    pub(crate) fn new_unchecked(min: Vector, max: Vector) -> Self {
        Self { min, max }
    }

    /// Get the dimension of the bounds.
    pub fn dim(&self) -> usize {
        self.min.dim()
    }

    /// Check if a point is inside the bounds.
    pub fn contains(&self, point: &Vector) -> bool {
        assert_eq!(point.dim(), self.dim());
        for i in 0..self.dim() {
            if point[i] < self.min[i] - EPSILON || point[i] > self.max[i] + EPSILON {
                return false;
            }
        }
        true
    }

    /// Check if a point is strictly inside (not on boundary).
    pub fn contains_strict(&self, point: &Vector) -> bool {
        assert_eq!(point.dim(), self.dim());
        for i in 0..self.dim() {
            if point[i] <= self.min[i] + EPSILON || point[i] >= self.max[i] - EPSILON {
                return false;
            }
        }
        true
    }

    /// Get the center of the bounds.
    pub fn center(&self) -> Vector {
        (&self.min + &self.max) / 2.0
    }

    /// Get the size (extent) in each dimension.
    pub fn size(&self) -> Vector {
        &self.max - &self.min
    }

    /// Compute distance from a point to the bounds.
    /// Returns 0 if point is inside.
    pub fn distance(&self, point: &Vector) -> f64 {
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

    /// Expand bounds by a margin in all directions.
    pub fn expand(&self, margin: f64) -> Self {
        let margin_vec = Vector::from_elem(self.dim(), margin);
        Self {
            min: &self.min - &margin_vec,
            max: &self.max + &margin_vec,
        }
    }

    /// Compute intersection with another bounds.
    /// Returns None if no intersection.
    pub fn intersect(&self, other: &Bounds) -> Option<Self> {
        assert_eq!(self.dim(), other.dim());
        let mut min = Vector::zeros(self.dim());
        let mut max = Vector::zeros(self.dim());

        for i in 0..self.dim() {
            min[i] = self.min[i].max(other.min[i]);
            max[i] = self.max[i].min(other.max[i]);
            if min[i] > max[i] {
                return None;
            }
        }

        Some(Self { min, max })
    }

    /// Check if bounds overlap with another.
    pub fn overlaps(&self, other: &Bounds) -> bool {
        self.intersect(other).is_some()
    }
}

/// A change vector with metadata.
///
/// Represents an attempted change (delta) from current state.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Delta {
    /// The change vector
    pub vector: Vector,
    /// Optional source identifier (e.g., "drag", "resize", "keyboard")
    pub source: Option<String>,
    /// Timestamp in microseconds
    pub timestamp_us: u64,
}

impl Delta {
    /// Create a new delta from a vector.
    pub fn new(vector: Vector) -> Self {
        Self {
            vector,
            source: None,
            timestamp_us: 0,
        }
    }

    /// Create a delta with source information.
    pub fn with_source(vector: Vector, source: &str) -> Self {
        Self {
            vector,
            source: Some(source.to_string()),
            timestamp_us: 0,
        }
    }

    /// Get the magnitude of the delta.
    pub fn magnitude(&self) -> f64 {
        self.vector.norm()
    }

    /// Normalize the delta to unit length.
    pub fn normalize(&self) -> Self {
        Self {
            vector: self.vector.normalize(),
            source: self.source.clone(),
            timestamp_us: self.timestamp_us,
        }
    }
}

/// The universal primitive in Newton.
///
/// Everything in Newton is an NTObject: windows, documents, constraints,
/// even individual characters. Each has identity (UUID), name, bounds,
/// and associated constraints.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NTObject {
    /// Unique identifier
    pub id: Uuid,
    /// Human-readable name
    pub name: String,
    /// Bounding box defining valid region
    pub bounds: Bounds,
    /// Associated constraint IDs
    pub constraint_ids: Vec<Uuid>,
}

impl NTObject {
    /// Create a new NTObject with generated UUID.
    pub fn new(name: &str, bounds: Bounds) -> Self {
        Self {
            id: Uuid::new_v4(),
            name: name.to_string(),
            bounds,
            constraint_ids: Vec::new(),
        }
    }

    /// Create a new NTObject with specific UUID.
    pub fn with_id(id: Uuid, name: &str, bounds: Bounds) -> Self {
        Self {
            id,
            name: name.to_string(),
            bounds,
            constraint_ids: Vec::new(),
        }
    }

    /// Add a constraint reference to this object.
    pub fn add_constraint(&mut self, constraint_id: Uuid) {
        if !self.constraint_ids.contains(&constraint_id) {
            self.constraint_ids.push(constraint_id);
        }
    }

    /// Remove a constraint reference from this object.
    pub fn remove_constraint(&mut self, constraint_id: &Uuid) {
        self.constraint_ids.retain(|id| id != constraint_id);
    }
}

impl PartialEq for NTObject {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}

impl Eq for NTObject {}

impl std::hash::Hash for NTObject {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.id.hash(state);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fg_state_from_violation() {
        // Valid: no violation
        let state = FGState::from_violation(0.0, 10.0);
        assert_eq!(state, FGState::Valid);

        // Slack: some violation but less than effort
        let state = FGState::from_violation(3.0, 10.0);
        assert!(matches!(state, FGState::Slack { margin } if (margin - 0.7).abs() < 0.01));

        // Exact: violation equals effort
        let state = FGState::from_violation(10.0, 10.0);
        assert_eq!(state, FGState::Exact);

        // Finfr: violation exceeds effort
        let state = FGState::from_violation(15.0, 10.0);
        assert!(matches!(state, FGState::Finfr { excess } if (excess - 0.5).abs() < 0.01));
    }

    #[test]
    fn test_fg_state_haptic_amplitude() {
        assert_eq!(FGState::Valid.haptic_amplitude(), 0.0);
        assert_eq!(FGState::Exact.haptic_amplitude(), 0.5);

        let slack = FGState::Slack { margin: 0.5 };
        assert!((slack.haptic_amplitude() - 0.15).abs() < 0.01);

        let finfr = FGState::Finfr { excess: 1.0 };
        assert_eq!(finfr.haptic_amplitude(), 1.0);
    }

    #[test]
    fn test_bounds_contains() {
        let bounds = Bounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        assert!(bounds.contains(&Vector::from_slice(&[50.0, 50.0])));
        assert!(bounds.contains(&Vector::from_slice(&[0.0, 0.0])));
        assert!(bounds.contains(&Vector::from_slice(&[100.0, 100.0])));
        assert!(!bounds.contains(&Vector::from_slice(&[150.0, 50.0])));
        assert!(!bounds.contains(&Vector::from_slice(&[-10.0, 50.0])));
    }

    #[test]
    fn test_bounds_distance() {
        let bounds = Bounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        // Inside point
        assert_eq!(bounds.distance(&Vector::from_slice(&[50.0, 50.0])), 0.0);

        // Outside point
        let dist = bounds.distance(&Vector::from_slice(&[103.0, 104.0]));
        assert!((dist - 5.0).abs() < EPSILON); // 3-4-5 triangle
    }

    #[test]
    fn test_bounds_intersect() {
        let a = Bounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let b = Bounds::new(
            Vector::from_slice(&[50.0, 50.0]),
            Vector::from_slice(&[150.0, 150.0]),
        );

        let intersection = a.intersect(&b).unwrap();
        assert_eq!(intersection.min[0], 50.0);
        assert_eq!(intersection.min[1], 50.0);
        assert_eq!(intersection.max[0], 100.0);
        assert_eq!(intersection.max[1], 100.0);
    }

    #[test]
    fn test_nt_object() {
        let bounds = Bounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let mut obj = NTObject::new("test", bounds);

        assert!(!obj.id.is_nil());
        assert_eq!(obj.name, "test");
        assert!(obj.constraint_ids.is_empty());

        let constraint_id = Uuid::new_v4();
        obj.add_constraint(constraint_id);
        assert_eq!(obj.constraint_ids.len(), 1);

        obj.add_constraint(constraint_id); // Duplicate
        assert_eq!(obj.constraint_ids.len(), 1);

        obj.remove_constraint(&constraint_id);
        assert!(obj.constraint_ids.is_empty());
    }

    #[test]
    fn test_delta() {
        let delta = Delta::new(Vector::from_slice(&[3.0, 4.0]));
        assert!((delta.magnitude() - 5.0).abs() < EPSILON);

        let delta = Delta::with_source(Vector::from_slice(&[1.0, 0.0]), "drag");
        assert_eq!(delta.source.as_deref(), Some("drag"));
    }
}
