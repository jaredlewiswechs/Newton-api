//! Performance benchmarks for projection algorithms.

use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use newton_core::prelude::*;
use newton_core::constraints::{boxed, ConstraintRef};

fn bench_box_projection(c: &mut Criterion) {
    let mut group = c.benchmark_group("box_projection");

    for dim in [2, 4, 8, 16, 32].iter() {
        let bounds = BoxBounds::new(
            Vector::zeros(*dim),
            Vector::from_elem(*dim, 100.0),
        );

        // Point outside bounds
        let point = Vector::from_elem(*dim, 150.0);

        group.bench_with_input(
            BenchmarkId::from_parameter(dim),
            dim,
            |b, _| {
                b.iter(|| {
                    black_box(bounds.project(&point))
                })
            },
        );
    }

    group.finish();
}

fn bench_weighted_projection(c: &mut Criterion) {
    let mut group = c.benchmark_group("weighted_projection");

    for dim in [2, 4, 8, 16].iter() {
        let bounds = BoxBounds::new(
            Vector::zeros(*dim),
            Vector::from_elem(*dim, 100.0),
        );
        let point = Vector::from_elem(*dim, 150.0);
        let weights = Vector::from_elem(*dim, 1.0);

        group.bench_with_input(
            BenchmarkId::from_parameter(dim),
            dim,
            |b, _| {
                b.iter(|| {
                    black_box(project_weighted(&point, &bounds, &weights))
                })
            },
        );
    }

    group.finish();
}

fn bench_halfspace_projection(c: &mut Criterion) {
    let mut group = c.benchmark_group("halfspace_projection");

    for n_constraints in [1, 4, 8, 16, 32].iter() {
        // Generate constraints
        let constraints: Vec<ConstraintRef> = (0..*n_constraints)
            .map(|i| {
                let mut normal = Vector::zeros(4);
                normal[i % 4] = 1.0;
                boxed(LinearConstraint::new(normal, 50.0))
            })
            .collect();

        let point = Vector::from_elem(4, 100.0);

        group.bench_with_input(
            BenchmarkId::from_parameter(n_constraints),
            n_constraints,
            |b, _| {
                b.iter(|| {
                    black_box(project_convex(&point, &constraints))
                })
            },
        );
    }

    group.finish();
}

fn bench_dykstra_convergence(c: &mut Criterion) {
    let mut group = c.benchmark_group("dykstra_convergence");

    // Test convergence speed for various constraint configurations
    let configs = vec![
        ("simple_box_2d", 2, 4),
        ("simple_box_4d", 4, 8),
        ("many_halfspaces", 4, 16),
    ];

    for (name, dim, n_constraints) in configs {
        let constraints: Vec<ConstraintRef> = (0..n_constraints)
            .map(|i| {
                let mut normal = Vector::zeros(dim);
                normal[i % dim] = if i < dim { 1.0 } else { -1.0 };
                let bound = if i < dim { 100.0 } else { 0.0 };
                boxed(LinearConstraint::new(normal, bound))
            })
            .collect();

        let point = Vector::from_elem(dim, 150.0);

        group.bench_function(name, |b| {
            b.iter(|| {
                black_box(project_convex(&point, &constraints))
            })
        });
    }

    group.finish();
}

criterion_group!(
    benches,
    bench_box_projection,
    bench_weighted_projection,
    bench_halfspace_projection,
    bench_dykstra_convergence
);
criterion_main!(benches);
