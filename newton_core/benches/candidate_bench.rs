//! Performance benchmarks for candidate generation.

use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use newton_core::prelude::*;
use newton_core::candidates::{local_search, snap_candidates, boundary_candidates, filter_and_rank};
use newton_core::constraints::{boxed, ConstraintRef};
use newton_core::primitives::Bounds;

fn bench_local_search(c: &mut Criterion) {
    let mut group = c.benchmark_group("local_search");

    for dim in [2, 4, 8].iter() {
        let center = Vector::from_elem(*dim, 50.0);
        let bounds = Bounds::new(
            Vector::zeros(*dim),
            Vector::from_elem(*dim, 100.0),
        );

        group.bench_with_input(
            BenchmarkId::from_parameter(dim),
            dim,
            |b, _| {
                b.iter(|| {
                    black_box(local_search(&center, Some(&bounds), 0))
                })
            },
        );
    }

    group.finish();
}

fn bench_snap_candidates(c: &mut Criterion) {
    let mut group = c.benchmark_group("snap_candidates");

    for grid_spacing in [1.0, 5.0, 10.0].iter() {
        let center = Vector::from_slice(&[50.0, 50.0]);

        group.bench_with_input(
            BenchmarkId::from_parameter(format!("spacing_{}", grid_spacing)),
            grid_spacing,
            |b, spacing| {
                b.iter(|| {
                    black_box(snap_candidates(&center, *spacing, 20.0))
                })
            },
        );
    }

    group.finish();
}

fn bench_boundary_candidates(c: &mut Criterion) {
    let mut group = c.benchmark_group("boundary_candidates");

    for dim in [2, 3, 4, 5].iter() {
        let bounds = Bounds::new(
            Vector::zeros(*dim),
            Vector::from_elem(*dim, 100.0),
        );

        group.bench_with_input(
            BenchmarkId::from_parameter(dim),
            dim,
            |b, _| {
                b.iter(|| {
                    black_box(boundary_candidates(&bounds, 0))
                })
            },
        );
    }

    group.finish();
}

fn bench_filter_and_rank(c: &mut Criterion) {
    let mut group = c.benchmark_group("filter_and_rank");

    let bounds = BoxBounds::new(
        Vector::from_slice(&[0.0, 0.0]),
        Vector::from_slice(&[100.0, 100.0]),
    );
    let constraints: Vec<ConstraintRef> = vec![boxed(bounds)];
    let intent = Vector::from_slice(&[50.0, 50.0]);

    for n_candidates in [10, 50, 100, 200].iter() {
        // Generate candidates (mix of valid and invalid)
        let candidates: Vec<Vector> = (0..*n_candidates)
            .map(|i| {
                let x = (i as f64 * 7.3) % 150.0;
                let y = (i as f64 * 11.7) % 150.0;
                Vector::from_slice(&[x, y])
            })
            .collect();

        group.bench_with_input(
            BenchmarkId::from_parameter(n_candidates),
            n_candidates,
            |b, _| {
                b.iter(|| {
                    black_box(filter_and_rank(candidates.clone(), &constraints, &intent))
                })
            },
        );
    }

    group.finish();
}

fn bench_full_suggestion(c: &mut Criterion) {
    use newton_core::aida::suggest;
    use newton_core::primitives::Delta;

    let mut group = c.benchmark_group("full_suggestion");

    let bounds = BoxBounds::new(
        Vector::from_slice(&[0.0, 0.0]),
        Vector::from_slice(&[100.0, 100.0]),
    );
    let constraints: Vec<ConstraintRef> = vec![boxed(bounds)];

    // Valid intent (inside bounds)
    let current = Vector::from_slice(&[50.0, 50.0]);
    let delta_valid = Delta::new(Vector::from_slice(&[10.0, 10.0]));

    group.bench_function("valid_intent", |b| {
        b.iter(|| {
            black_box(suggest(&current, &delta_valid, &constraints))
        })
    });

    // Invalid intent (outside bounds)
    let delta_invalid = Delta::new(Vector::from_slice(&[100.0, 100.0]));

    group.bench_function("invalid_intent", |b| {
        b.iter(|| {
            black_box(suggest(&current, &delta_invalid, &constraints))
        })
    });

    group.finish();
}

criterion_group!(
    benches,
    bench_local_search,
    bench_snap_candidates,
    bench_boundary_candidates,
    bench_filter_and_rank,
    bench_full_suggestion
);
criterion_main!(benches);
