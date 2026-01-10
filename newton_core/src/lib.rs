//! # Newton Core
//!
//! The mathematical bedrock for Aid-a (Assistive Intelligence for Design Autonomy).
//!
//! This crate provides:
//! - Constraint definition and verification
//! - Convex projection algorithms (Dykstra's algorithm)
//! - Nonconvex candidate generation and search
//! - The Aid-a suggestion engine
//!
//! ## Core Guarantee
//!
//! Aid-a never lies, never loops, and never suggests an invalid state.
//!
//! ## Example
//!
//! ```rust
//! use newton_core::prelude::*;
//!
//! // Define bounds
//! let bounds = BoxBounds::new(
//!     Vector::from_slice(&[0.0, 0.0]),
//!     Vector::from_slice(&[100.0, 100.0]),
//! );
//!
//! // Project a point outside bounds
//! let point = Vector::from_slice(&[150.0, 50.0]);
//! let projected = bounds.project(&point);
//!
//! assert!(bounds.contains(&projected));
//! ```

#![warn(missing_docs)]
#![warn(clippy::all)]
#![deny(unsafe_code)]

pub mod constants;
pub mod linalg;
pub mod primitives;
pub mod constraints;
pub mod projection;
pub mod candidates;
pub mod intent;
pub mod rank;
pub mod explain;
pub mod verify;
pub mod aida;

/// Prelude module for convenient imports
pub mod prelude {
    pub use crate::constants::*;
    pub use crate::linalg::Vector;
    pub use crate::primitives::{Bounds, FGState, NTObject, Delta};
    pub use crate::constraints::{Constraint, ConstraintRef, BoxBounds, LinearConstraint, boxed};
    pub use crate::projection::{project_convex, project_weighted, project_halfspace};
    pub use crate::candidates::local_search;
    pub use crate::aida::{suggest, AidAResponse, Suggestion, SuggestionQuality};
    pub use crate::verify::{verify_contract, ContractViolation};
}

#[cfg(test)]
mod tests {
    pub mod property;
    pub mod adversarial;
}
