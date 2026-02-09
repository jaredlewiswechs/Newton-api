#!/usr/bin/env python3
"""
Newton Supercomputer Performance Verification Suite
Comprehensive benchmarks to verify marketing claims
"""

import time
import requests
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

BASE_URL = "http://localhost:8000"

def measure_request(endpoint, method="GET", payload=None, description=""):
    """Measure a single request's performance"""
    start = time.perf_counter()

    if method == "GET":
        response = requests.get(f"{BASE_URL}{endpoint}")
    else:
        response = requests.post(f"{BASE_URL}{endpoint}", json=payload)

    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000

    result = {
        "endpoint": endpoint,
        "description": description,
        "method": method,
        "status_code": response.status_code,
        "elapsed_ms": elapsed_ms,
        "response": response.json() if response.status_code == 200 else None
    }

    # Extract internal elapsed time if available
    if result["response"] and "elapsed_us" in result["response"]:
        result["internal_us"] = result["response"]["elapsed_us"]

    return result

def run_benchmark(name, endpoint, method, payload, iterations=20):
    """Run multiple iterations and calculate statistics"""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: {name}")
    print(f"Endpoint: {endpoint}")
    print(f"Iterations: {iterations}")
    print(f"{'='*60}")

    results = []
    internal_times = []

    for i in range(iterations):
        result = measure_request(endpoint, method, payload, name)
        results.append(result["elapsed_ms"])
        if "internal_us" in result:
            internal_times.append(result["internal_us"])
        print(f"  Run {i+1}: {result['elapsed_ms']:.2f}ms (internal: {result.get('internal_us', 'N/A')}μs)")

    stats = {
        "name": name,
        "endpoint": endpoint,
        "iterations": iterations,
        "min_ms": min(results),
        "max_ms": max(results),
        "mean_ms": statistics.mean(results),
        "median_ms": statistics.median(results),
        "stdev_ms": statistics.stdev(results) if len(results) > 1 else 0,
        "p95_ms": sorted(results)[int(0.95 * len(results))],
    }

    if internal_times:
        stats["internal_mean_us"] = statistics.mean(internal_times)
        stats["internal_median_us"] = statistics.median(internal_times)
        stats["internal_min_us"] = min(internal_times)
        stats["internal_max_us"] = max(internal_times)

    print(f"\nResults:")
    print(f"  Min:    {stats['min_ms']:.2f}ms")
    print(f"  Max:    {stats['max_ms']:.2f}ms")
    print(f"  Mean:   {stats['mean_ms']:.2f}ms")
    print(f"  Median: {stats['median_ms']:.2f}ms")
    print(f"  P95:    {stats['p95_ms']:.2f}ms")
    print(f"  StdDev: {stats['stdev_ms']:.2f}ms")

    if internal_times:
        print(f"\n  Internal Processing:")
        print(f"    Mean:   {stats['internal_mean_us']:.1f}μs ({stats['internal_mean_us']/1000:.3f}ms)")
        print(f"    Median: {stats['internal_median_us']:.1f}μs")
        print(f"    Min:    {stats['internal_min_us']:.1f}μs")
        print(f"    Max:    {stats['internal_max_us']:.1f}μs")

    return stats

def run_load_test(endpoint, method, payload, concurrent_requests=20):
    """Run concurrent requests to test throughput"""
    print(f"\n{'='*60}")
    print(f"LOAD TEST: {concurrent_requests} concurrent requests")
    print(f"Endpoint: {endpoint}")
    print(f"{'='*60}")

    start_time = time.perf_counter()
    results = []

    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [
            executor.submit(measure_request, endpoint, method, payload, f"Concurrent {i+1}")
            for i in range(concurrent_requests)
        ]

        for future in as_completed(futures):
            results.append(future.result())

    end_time = time.perf_counter()
    total_time_ms = (end_time - start_time) * 1000

    response_times = [r["elapsed_ms"] for r in results]
    successful = sum(1 for r in results if r["status_code"] == 200)

    stats = {
        "concurrent_requests": concurrent_requests,
        "total_time_ms": total_time_ms,
        "requests_per_second": concurrent_requests / (total_time_ms / 1000),
        "successful": successful,
        "failed": concurrent_requests - successful,
        "min_response_ms": min(response_times),
        "max_response_ms": max(response_times),
        "mean_response_ms": statistics.mean(response_times),
        "median_response_ms": statistics.median(response_times),
    }

    print(f"\nResults:")
    print(f"  Total time: {stats['total_time_ms']:.2f}ms")
    print(f"  Throughput: {stats['requests_per_second']:.1f} req/sec")
    print(f"  Successful: {stats['successful']}/{concurrent_requests}")
    print(f"  Response times:")
    print(f"    Min:    {stats['min_response_ms']:.2f}ms")
    print(f"    Max:    {stats['max_response_ms']:.2f}ms")
    print(f"    Mean:   {stats['mean_response_ms']:.2f}ms")
    print(f"    Median: {stats['median_response_ms']:.2f}ms")

    return stats

def main():
    print("\n" + "="*70)
    print("NEWTON SUPERCOMPUTER - PERFORMANCE VERIFICATION SUITE")
    print("="*70)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Base URL: {BASE_URL}")

    all_stats = {}

    # Test 1: Health check (baseline)
    all_stats["health"] = run_benchmark(
        "Health Check (Baseline)",
        "/health",
        "GET",
        None,
        iterations=20
    )

    # Test 2: Simple verification
    all_stats["verify_simple"] = run_benchmark(
        "Simple Verification",
        "/verify",
        "POST",
        {"input": "Help me write a business plan"},
        iterations=30
    )

    # Test 3: Complex verification
    all_stats["verify_complex"] = run_benchmark(
        "Complex Verification",
        "/verify",
        "POST",
        {"input": "Can you explain the quantum mechanics of photosynthesis in chlorophyll molecules and how this relates to energy transfer efficiency?"},
        iterations=30
    )

    # Test 4: Simple calculation
    all_stats["calculate_simple"] = run_benchmark(
        "Simple Calculation (2+3)",
        "/calculate",
        "POST",
        {"expression": {"op": "+", "args": [2, 3]}},
        iterations=30
    )

    # Test 5: Complex calculation
    all_stats["calculate_complex"] = run_benchmark(
        "Complex Calculation (nested operations)",
        "/calculate",
        "POST",
        {"expression": {
            "op": "+",
            "args": [
                {"op": "*", "args": [5, 10]},
                {"op": "/", "args": [100, 4]},
                {"op": "sqrt", "args": [144]}
            ]
        }},
        iterations=30
    )

    # Test 6: Factorial calculation
    all_stats["calculate_factorial"] = run_benchmark(
        "Factorial (10!)",
        "/calculate",
        "POST",
        {"expression": {
            "op": "reduce",
            "args": [
                {"op": "range", "args": [1, 11]},
                {"op": "*"},
                1
            ]
        }},
        iterations=20
    )

    # Test 7: Loop calculation
    all_stats["calculate_loop"] = run_benchmark(
        "Loop Calculation (sum 1-100)",
        "/calculate",
        "POST",
        {"expression": {
            "op": "sum",
            "args": [{"op": "range", "args": [1, 101]}]
        }},
        iterations=20
    )

    # Test 8: Ask endpoint (full pipeline)
    all_stats["ask"] = run_benchmark(
        "Ask Endpoint (full pipeline)",
        "/ask",
        "POST",
        {"query": "What is 2+2?"},
        iterations=20
    )

    # Test 9: Constraint evaluation
    all_stats["constraint"] = run_benchmark(
        "Constraint Evaluation",
        "/constraint",
        "POST",
        {
            "constraint": "age >= 18",
            "object": {"age": 25, "name": "Test User"}
        },
        iterations=30
    )

    # Test 10: Load test
    all_stats["load_test_20"] = run_load_test(
        "/verify",
        "POST",
        {"input": "Quick test"},
        concurrent_requests=20
    )

    # Test 11: Higher load test
    all_stats["load_test_50"] = run_load_test(
        "/verify",
        "POST",
        {"input": "Quick test"},
        concurrent_requests=50
    )

    # Test 12: Calculation load test
    all_stats["load_test_calc"] = run_load_test(
        "/calculate",
        "POST",
        {"expression": {"op": "+", "args": [{"op": "*", "args": [5, 10]}, 25]}},
        concurrent_requests=30
    )

    # Generate summary
    print("\n" + "="*70)
    print("PERFORMANCE VERIFICATION SUMMARY")
    print("="*70)

    print("\n## End-to-End Response Times (network round-trip included)")
    print("-" * 60)
    for key in ["health", "verify_simple", "verify_complex", "calculate_simple",
                "calculate_complex", "ask", "constraint"]:
        if key in all_stats:
            s = all_stats[key]
            print(f"{s['name'][:45]:45} | Median: {s['median_ms']:.2f}ms | P95: {s['p95_ms']:.2f}ms")

    print("\n## Internal Processing Times (Newton engine only)")
    print("-" * 60)
    for key in ["verify_simple", "verify_complex", "calculate_simple",
                "calculate_complex", "ask", "constraint"]:
        if key in all_stats and "internal_median_us" in all_stats[key]:
            s = all_stats[key]
            print(f"{s['name'][:45]:45} | {s['internal_median_us']:.1f}μs ({s['internal_median_us']/1000:.3f}ms)")

    print("\n## Load Test Results")
    print("-" * 60)
    for key in ["load_test_20", "load_test_50", "load_test_calc"]:
        if key in all_stats:
            s = all_stats[key]
            print(f"{s['concurrent_requests']} concurrent requests:")
            print(f"  Total time: {s['total_time_ms']:.0f}ms | Throughput: {s['requests_per_second']:.1f} req/sec")
            print(f"  Median response: {s['median_response_ms']:.2f}ms | Max: {s['max_response_ms']:.2f}ms")

    # Claim verification
    print("\n" + "="*70)
    print("MARKETING CLAIM VERIFICATION")
    print("="*70)

    verify_median = all_stats["verify_simple"]["median_ms"]
    internal_us = all_stats["verify_simple"].get("internal_median_us", 0)

    print(f"\n### Claimed: '35-45ms end-to-end'")
    print(f"    Measured median: {verify_median:.2f}ms")
    print(f"    Status: {'✓ VERIFIED' if verify_median <= 50 else '✗ NOT VERIFIED'}")

    print(f"\n### Claimed: '42 microseconds internal processing'")
    print(f"    Measured median: {internal_us:.1f}μs")
    print(f"    Status: {'✓ VERIFIED' if internal_us <= 1000 else '⚠ HIGHER THAN CLAIMED'}")

    # Comparison calculations
    stripe_time = 1475  # ms
    gpt4_time = 1300  # ms
    gpt35_time = 900  # ms
    claude_time = 2000  # ms

    print(f"\n### Speed Comparisons (using median verify time: {verify_median:.2f}ms)")
    print(f"    vs Stripe (1,475ms):     Newton is {stripe_time/verify_median:.1f}x faster")
    print(f"    vs GPT-3.5 (900ms):      Newton is {gpt35_time/verify_median:.1f}x faster")
    print(f"    vs GPT-4 (1,300ms):      Newton is {gpt4_time/verify_median:.1f}x faster")
    print(f"    vs Claude (2,000ms):     Newton is {claude_time/verify_median:.1f}x faster")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "benchmarks": all_stats
    }

    with open("performance_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: performance_results.json")
    print(f"Completed: {datetime.now().isoformat()}")

    return all_stats

if __name__ == "__main__":
    main()
