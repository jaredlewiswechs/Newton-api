//! Candidate generation for nonconvex constraint search.
//!
//! When constraints are nonconvex, we can't rely on projection alone.
//! Instead, we generate candidate points and verify each one.
//!
//! The local search follows a strict discipline:
//! 1. **Radial:** Candidates generated in concentric shells around center
//! 2. **Monotonic:** Each shell strictly increases distance from center
//! 3. **Deterministic:** Within each shell, candidates are ordered lexicographically
//! 4. **Bounded:** Early exit on quota OR all shells exhausted

use crate::linalg::Vector;
use crate::primitives::Bounds;
use crate::constraints::ConstraintRef;
use crate::constants::{SHELL_RADII, MAX_CANDIDATES, SHELL_ANGULAR_SAMPLES};
#[allow(unused_imports)]
use crate::constants::EPSILON;
use std::f64::consts::PI;

/// Radial, monotonic local search around a center point.
///
/// Generates candidates in concentric shells, sorted lexicographically
/// within each shell for determinism.
///
/// # Arguments
/// * `center` - The center point (typically the convex projection)
/// * `bounds` - Optional bounds to filter candidates
/// * `existing_candidates` - Number of candidates already generated
///
/// # Returns
/// A list of candidate points, ordered by shell then lexicographically.
pub fn local_search(
    center: &Vector,
    bounds: Option<&Bounds>,
    existing_candidates: usize,
) -> Vec<Vector> {
    let mut candidates = Vec::new();
    let remaining_quota = MAX_CANDIDATES.saturating_sub(existing_candidates);

    if remaining_quota == 0 {
        return candidates;
    }

    let dim = center.dim();

    // Generate candidates in concentric shells
    for &radius in SHELL_RADII.iter() {
        let shell_points = generate_shell_points(center, radius, dim);

        // Filter to valid points and sort lexicographically for determinism
        let mut valid: Vec<_> = shell_points
            .into_iter()
            .filter(|p| bounds.map_or(true, |b| b.contains(p)))
            .collect();

        valid.sort_by(|a, b| a.lexicographic_cmp(b));

        for point in valid {
            candidates.push(point);
            if candidates.len() >= remaining_quota {
                return candidates;
            }
        }
    }

    candidates
}

/// Generate points on a shell (hypersphere surface) of given radius.
///
/// For 2D: points on a circle
/// For nD: points sampled on hypersphere
fn generate_shell_points(center: &Vector, radius: f64, dim: usize) -> Vec<Vector> {
    match dim {
        1 => generate_shell_1d(center, radius),
        2 => generate_shell_2d(center, radius),
        _ => generate_shell_nd(center, radius, dim),
    }
}

/// Generate shell points in 1D (just two points: left and right).
fn generate_shell_1d(center: &Vector, radius: f64) -> Vec<Vector> {
    vec![
        Vector::from_slice(&[center[0] - radius]),
        Vector::from_slice(&[center[0] + radius]),
    ]
}

/// Generate shell points in 2D (points on a circle).
fn generate_shell_2d(center: &Vector, radius: f64) -> Vec<Vector> {
    let n_points = SHELL_ANGULAR_SAMPLES;
    let mut points = Vec::with_capacity(n_points);

    for i in 0..n_points {
        let angle = 2.0 * PI * (i as f64) / (n_points as f64);
        points.push(Vector::from_slice(&[
            center[0] + radius * angle.cos(),
            center[1] + radius * angle.sin(),
        ]));
    }

    points
}

/// Generate shell points in nD (sampled on hypersphere).
fn generate_shell_nd(center: &Vector, radius: f64, dim: usize) -> Vec<Vector> {
    let mut points = Vec::new();

    // For higher dimensions, generate axis-aligned points and some diagonal points
    // This is a deterministic sampling that covers key directions

    // Axis-aligned points (2n points)
    for d in 0..dim {
        let mut pos = center.clone();
        let mut neg = center.clone();
        pos[d] += radius;
        neg[d] -= radius;
        points.push(pos);
        points.push(neg);
    }

    // Diagonal points in 2D subspaces (for dimensions >= 2)
    if dim >= 2 {
        let diag_radius = radius / (2.0_f64).sqrt();
        for d1 in 0..dim {
            for d2 in (d1 + 1)..dim {
                // Four diagonal points in the (d1, d2) plane
                for &sign1 in &[1.0, -1.0] {
                    for &sign2 in &[1.0, -1.0] {
                        let mut point = center.clone();
                        point[d1] += sign1 * diag_radius;
                        point[d2] += sign2 * diag_radius;
                        points.push(point);
                    }
                }
            }
        }
    }

    points
}

/// Generate snap point candidates for grid-aligned positions.
///
/// # Arguments
/// * `center` - The center point
/// * `grid_spacing` - Grid spacing in each dimension
/// * `search_radius` - How far to search from center
pub fn snap_candidates(center: &Vector, grid_spacing: f64, search_radius: f64) -> Vec<Vector> {
    let dim = center.dim();
    let mut candidates = Vec::new();

    // Determine grid range in each dimension
    let half_range = (search_radius / grid_spacing).ceil() as i32;

    // Generate grid points recursively
    fn generate_grid(
        dim: usize,
        current_dim: usize,
        center: &Vector,
        grid_spacing: f64,
        half_range: i32,
        current: &mut Vec<f64>,
        candidates: &mut Vec<Vector>,
        max_candidates: usize,
    ) {
        if candidates.len() >= max_candidates {
            return;
        }

        if current_dim == dim {
            candidates.push(Vector::from_slice(current));
            return;
        }

        let center_val = center[current_dim];
        let base = (center_val / grid_spacing).round() * grid_spacing;

        for offset in -half_range..=half_range {
            let val = base + (offset as f64) * grid_spacing;
            current.push(val);
            generate_grid(
                dim,
                current_dim + 1,
                center,
                grid_spacing,
                half_range,
                current,
                candidates,
                max_candidates,
            );
            current.pop();
        }
    }

    let mut current = Vec::with_capacity(dim);
    generate_grid(
        dim,
        0,
        center,
        grid_spacing,
        half_range,
        &mut current,
        &mut candidates,
        MAX_CANDIDATES,
    );

    // Sort by distance to center, then lexicographically
    candidates.sort_by(|a, b| {
        let dist_a = center.distance(a);
        let dist_b = center.distance(b);
        match dist_a.partial_cmp(&dist_b) {
            Some(std::cmp::Ordering::Equal) => a.lexicographic_cmp(b),
            Some(ord) => ord,
            None => std::cmp::Ordering::Equal,
        }
    });

    candidates.truncate(MAX_CANDIDATES);
    candidates
}

/// Generate boundary candidates from constraint intersections.
///
/// For box bounds, generates corner and edge midpoint candidates.
pub fn boundary_candidates(bounds: &Bounds, existing: usize) -> Vec<Vector> {
    let mut candidates = Vec::new();
    let remaining = MAX_CANDIDATES.saturating_sub(existing);

    if remaining == 0 {
        return candidates;
    }

    let dim = bounds.dim();

    // Corner candidates (2^dim corners)
    if dim <= 5 {
        // Only generate corners for reasonable dimensions
        let n_corners = 1 << dim;
        for i in 0..n_corners {
            let mut corner = Vector::zeros(dim);
            for d in 0..dim {
                corner[d] = if (i >> d) & 1 == 0 {
                    bounds.min[d]
                } else {
                    bounds.max[d]
                };
            }
            candidates.push(corner);
            if candidates.len() >= remaining {
                return candidates;
            }
        }
    }

    // Edge midpoints
    for d in 0..dim {
        // Center of face at min
        let mut min_face = bounds.center();
        min_face[d] = bounds.min[d];
        candidates.push(min_face);

        // Center of face at max
        let mut max_face = bounds.center();
        max_face[d] = bounds.max[d];
        candidates.push(max_face);

        if candidates.len() >= remaining {
            return candidates;
        }
    }

    // Center point
    candidates.push(bounds.center());

    candidates.truncate(remaining);
    candidates
}

/// Filter and rank candidates by validity and distance.
///
/// Returns candidates that satisfy all constraints, sorted by distance to intent.
pub fn filter_and_rank(
    candidates: Vec<Vector>,
    constraints: &[ConstraintRef],
    intent: &Vector,
) -> Vec<Vector> {
    let mut valid: Vec<_> = candidates
        .into_iter()
        .filter(|c| constraints.iter().all(|con| con.satisfied(c)))
        .collect();

    // Sort by distance to intent, then lexicographically for determinism
    valid.sort_by(|a, b| {
        let dist_a = intent.distance(a);
        let dist_b = intent.distance(b);
        match dist_a.partial_cmp(&dist_b) {
            Some(std::cmp::Ordering::Equal) => a.lexicographic_cmp(b),
            Some(ord) => ord,
            None => std::cmp::Ordering::Equal,
        }
    });

    valid
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_local_search_basic() {
        let center = Vector::from_slice(&[50.0, 50.0]);
        let bounds = Bounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        let candidates = local_search(&center, Some(&bounds), 0);

        // Should generate some candidates
        assert!(!candidates.is_empty());

        // All candidates should be within bounds
        for c in &candidates {
            assert!(bounds.contains(c), "Candidate {:?} outside bounds", c);
        }
    }

    #[test]
    fn test_local_search_respects_quota() {
        let center = Vector::from_slice(&[50.0, 50.0]);
        let bounds = Bounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        // Already have many candidates
        let candidates = local_search(&center, Some(&bounds), MAX_CANDIDATES - 2);
        assert!(candidates.len() <= 2);

        // Already at quota
        let candidates = local_search(&center, Some(&bounds), MAX_CANDIDATES);
        assert!(candidates.is_empty());
    }

    #[test]
    fn test_local_search_deterministic() {
        let center = Vector::from_slice(&[50.0, 50.0]);
        let bounds = Bounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        let candidates1 = local_search(&center, Some(&bounds), 0);
        let candidates2 = local_search(&center, Some(&bounds), 0);

        assert_eq!(candidates1.len(), candidates2.len());
        for (c1, c2) in candidates1.iter().zip(candidates2.iter()) {
            for i in 0..c1.dim() {
                assert_eq!(c1[i].to_bits(), c2[i].to_bits());
            }
        }
    }

    #[test]
    fn test_snap_candidates() {
        let center = Vector::from_slice(&[5.3, 7.8]);
        let candidates = snap_candidates(&center, 5.0, 10.0);

        // Should have some candidates
        assert!(!candidates.is_empty());

        // All should be grid-aligned
        for c in &candidates {
            assert!((c[0] % 5.0).abs() < EPSILON || (c[0] % 5.0 - 5.0).abs() < EPSILON);
            assert!((c[1] % 5.0).abs() < EPSILON || (c[1] % 5.0 - 5.0).abs() < EPSILON);
        }
    }

    #[test]
    fn test_boundary_candidates() {
        let bounds = Bounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );

        let candidates = boundary_candidates(&bounds, 0);

        // Should include corners
        assert!(candidates.iter().any(|c| c.approx_eq(&Vector::from_slice(&[0.0, 0.0]))));
        assert!(candidates.iter().any(|c| c.approx_eq(&Vector::from_slice(&[100.0, 100.0]))));

        // Should include center
        assert!(candidates.iter().any(|c| c.approx_eq(&Vector::from_slice(&[50.0, 50.0]))));
    }

    #[test]
    fn test_shell_points_2d() {
        let center = Vector::from_slice(&[0.0, 0.0]);
        let radius = 10.0;
        let points = generate_shell_points(&center, radius, 2);

        // All points should be at the correct radius
        for p in &points {
            let dist = center.distance(p);
            assert!((dist - radius).abs() < EPSILON, "Point {:?} at distance {} not {}", p, dist, radius);
        }
    }

    #[test]
    fn test_filter_and_rank() {
        use crate::constraints::{BoxBounds, boxed};

        let bounds = BoxBounds::new(
            Vector::from_slice(&[0.0, 0.0]),
            Vector::from_slice(&[100.0, 100.0]),
        );
        let constraints = vec![boxed(bounds)];

        let candidates = vec![
            Vector::from_slice(&[50.0, 50.0]),   // Valid
            Vector::from_slice(&[150.0, 50.0]),  // Invalid
            Vector::from_slice(&[25.0, 25.0]),   // Valid
        ];

        let intent = Vector::from_slice(&[30.0, 30.0]);
        let ranked = filter_and_rank(candidates, &constraints, &intent);

        // Should only have valid candidates
        assert_eq!(ranked.len(), 2);

        // Should be sorted by distance to intent
        let dist0 = intent.distance(&ranked[0]);
        let dist1 = intent.distance(&ranked[1]);
        assert!(dist0 <= dist1);
    }
}
