#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON BENCHMARK - 50 COMMON LLM QUERIES
Speed and accuracy test with real-world questions

Tests:
    - Response time (ms)
    - Verification status
    - Knowledge base hits
    - Source attribution

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
from newton_agent import NewtonAgent


@dataclass
class BenchmarkResult:
    """Result of a single benchmark query."""
    question: str
    category: str
    response_time_ms: float
    verified: bool
    has_answer: bool
    response_preview: str
    source: str


# 50 most common LLM chat requests across categories
BENCHMARK_QUERIES = [
    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 1: GEOGRAPHY (10 questions)
    # ═══════════════════════════════════════════════════════════════════════════
    ("What is the capital of France?", "geography", ["paris"]),
    ("What is the capital of Japan?", "geography", ["tokyo"]),
    ("What is the capital of Germany?", "geography", ["berlin"]),
    ("What is the capital of Italy?", "geography", ["rome"]),
    ("What is the capital of Australia?", "geography", ["canberra"]),
    ("What is the capital of Brazil?", "geography", ["brasilia", "brasília"]),
    ("What is the capital of Canada?", "geography", ["ottawa"]),
    ("What is the capital of Spain?", "geography", ["madrid"]),
    ("What is the capital of China?", "geography", ["beijing"]),
    ("What is the capital of India?", "geography", ["new delhi", "delhi"]),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 2: MATH (10 questions)
    # ═══════════════════════════════════════════════════════════════════════════
    ("What is 2 + 2?", "math", ["4"]),
    ("What is 7 * 8?", "math", ["56"]),
    ("What is 100 / 4?", "math", ["25"]),
    ("What is 15 - 7?", "math", ["8"]),
    ("What is 12 * 12?", "math", ["144"]),
    ("What is 99 + 1?", "math", ["100"]),
    ("What is 50 / 2?", "math", ["25"]),
    ("What is 9 * 9?", "math", ["81"]),
    ("What is 1000 - 1?", "math", ["999"]),
    ("What is 3 * 3 * 3?", "math", ["27"]),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 3: SCIENCE (10 questions)
    # ═══════════════════════════════════════════════════════════════════════════
    ("What is the speed of light?", "science", ["299792458", "299,792,458"]),
    ("What is the chemical symbol for water?", "science", ["h2o", "h₂o"]),
    ("What is the chemical symbol for gold?", "science", ["au"]),
    ("How many planets are in our solar system?", "science", ["8", "eight"]),
    ("What is the largest planet?", "science", ["jupiter"]),
    ("What is the boiling point of water?", "science", ["100", "212"]),
    ("What is the freezing point of water?", "science", ["0", "32"]),
    ("What is pi approximately?", "science", ["3.14"]),
    ("What is the atomic number of carbon?", "science", ["6"]),
    ("What is the atomic number of oxygen?", "science", ["8"]),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 4: TECH/PROGRAMMING (10 questions)
    # ═══════════════════════════════════════════════════════════════════════════
    ("When was Python created?", "tech", ["1991"]),
    ("Who created Python?", "tech", ["guido", "van rossum"]),
    ("Who founded Apple?", "tech", ["steve jobs", "wozniak"]),
    ("Who founded Microsoft?", "tech", ["bill gates", "paul allen"]),
    ("Who founded Amazon?", "tech", ["jeff bezos", "bezos"]),
    ("When was JavaScript created?", "tech", ["1995"]),
    ("What company created Java?", "tech", ["sun", "oracle"]),
    ("What does HTML stand for?", "tech", ["hypertext", "markup"]),
    ("What does CPU stand for?", "tech", ["central", "processing"]),
    ("What does API stand for?", "tech", ["application", "programming", "interface"]),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 5: IDENTITY (5 questions)
    # ═══════════════════════════════════════════════════════════════════════════
    ("Who are you?", "identity", ["newton"]),
    ("What is your name?", "identity", ["newton"]),
    ("Who created you?", "identity", ["jared", "lewis"]),
    ("Are you an AI?", "identity", ["newton", "verify"]),
    ("How do you work?", "identity", ["constraint", "verify", "1 == 1"]),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY 6: GENERAL KNOWLEDGE (5 questions)
    # ═══════════════════════════════════════════════════════════════════════════
    ("How many days are in a year?", "general", ["365", "366"]),  # 365 or 366 in leap year
    ("How many hours are in a day?", "general", ["24"]),
    ("How many minutes are in an hour?", "general", ["60"]),
    ("How many seconds are in a minute?", "general", ["60"]),
    ("How many months are in a year?", "general", ["12", "twelve"]),
]


def run_benchmark():
    """Run the full benchmark suite."""
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "NEWTON BENCHMARK - 50 QUERIES" + " " * 22 + "║")
    print("║" + " " * 18 + "Speed & Accuracy Test" + " " * 29 + "║")
    print("╚" + "═" * 68 + "╝")
    
    agent = NewtonAgent()
    results: List[BenchmarkResult] = []
    
    total_start = time.time()
    
    # Run all queries
    for i, (question, category, expected) in enumerate(BENCHMARK_QUERIES, 1):
        # Time the query
        start = time.time()
        response = agent.process(question)
        elapsed_ms = (time.time() - start) * 1000
        
        # Check if answer is correct
        content_lower = response.content.lower().replace(",", "").replace("_", "")
        has_answer = any(exp.lower() in content_lower for exp in expected)
        
        # Determine source
        if "CIA" in response.content or "Factbook" in response.content:
            source = "KB:CIA"
        elif "NIST" in response.content:
            source = "KB:NIST"
        elif "Logic Engine" in response.content or "✓ Verified" in response.content:
            source = "LOGIC"
        elif "Newton" in response.content and category == "identity":
            source = "IDENTITY"
        elif response.verified:
            source = "KB"
        else:
            source = "LLM"
        
        result = BenchmarkResult(
            question=question,
            category=category,
            response_time_ms=elapsed_ms,
            verified=response.verified,
            has_answer=has_answer,
            response_preview=response.content[:60].replace('\n', ' '),
            source=source,
        )
        results.append(result)
        
        # Print progress
        status = "✓" if has_answer else "✗"
        v_status = "V" if response.verified else " "
        print(f"{i:2}. [{v_status}] {status} {elapsed_ms:6.1f}ms | {category:10} | {question[:40]}")
    
    total_time = time.time() - total_start
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n" + "═" * 70)
    print("BENCHMARK RESULTS")
    print("═" * 70)
    
    # Overall stats
    total = len(results)
    correct = sum(1 for r in results if r.has_answer)
    verified = sum(1 for r in results if r.verified)
    avg_time = sum(r.response_time_ms for r in results) / total
    min_time = min(r.response_time_ms for r in results)
    max_time = max(r.response_time_ms for r in results)
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Total queries:     {total}")
    print(f"   Correct answers:   {correct}/{total} ({correct/total*100:.1f}%)")
    print(f"   Verified:          {verified}/{total} ({verified/total*100:.1f}%)")
    print(f"   Total time:        {total_time:.2f}s")
    print(f"   Avg response time: {avg_time:.1f}ms")
    print(f"   Min response time: {min_time:.1f}ms")
    print(f"   Max response time: {max_time:.1f}ms")
    print(f"   Throughput:        {total/total_time:.1f} queries/sec")
    
    # By category
    print(f"\n📈 BY CATEGORY:")
    categories = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = {"correct": 0, "total": 0, "verified": 0, "time_sum": 0}
        categories[r.category]["total"] += 1
        categories[r.category]["time_sum"] += r.response_time_ms
        if r.has_answer:
            categories[r.category]["correct"] += 1
        if r.verified:
            categories[r.category]["verified"] += 1
    
    print(f"   {'Category':<12} {'Correct':>10} {'Verified':>10} {'Avg Time':>12}")
    print(f"   {'-'*12} {'-'*10} {'-'*10} {'-'*12}")
    for cat, stats in sorted(categories.items()):
        pct = stats['correct']/stats['total']*100
        v_pct = stats['verified']/stats['total']*100
        avg = stats['time_sum']/stats['total']
        print(f"   {cat:<12} {stats['correct']}/{stats['total']:>3} ({pct:4.0f}%) {stats['verified']}/{stats['total']:>3} ({v_pct:4.0f}%) {avg:8.1f}ms")
    
    # By source
    print(f"\n🔍 BY SOURCE:")
    sources = {}
    for r in results:
        if r.source not in sources:
            sources[r.source] = 0
        sources[r.source] += 1
    
    for source, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"   {source:<12} {count:>3} queries ({count/total*100:.1f}%)")
    
    # Speed distribution
    print(f"\n⚡ SPEED DISTRIBUTION:")
    under_10 = sum(1 for r in results if r.response_time_ms < 10)
    under_50 = sum(1 for r in results if r.response_time_ms < 50)
    under_100 = sum(1 for r in results if r.response_time_ms < 100)
    under_500 = sum(1 for r in results if r.response_time_ms < 500)
    
    print(f"   < 10ms:   {under_10:>3} ({under_10/total*100:.1f}%)")
    print(f"   < 50ms:   {under_50:>3} ({under_50/total*100:.1f}%)")
    print(f"   < 100ms:  {under_100:>3} ({under_100/total*100:.1f}%)")
    print(f"   < 500ms:  {under_500:>3} ({under_500/total*100:.1f}%)")
    
    # Failures
    failures = [r for r in results if not r.has_answer]
    if failures:
        print(f"\n❌ FAILURES ({len(failures)}):")
        for r in failures:
            print(f"   • {r.question}")
            print(f"     Got: {r.response_preview}...")
    
    # Final verdict
    print("\n" + "═" * 70)
    
    if correct >= 45 and verified >= 40 and avg_time < 100:
        print("🏆 BENCHMARK PASSED - PRODUCTION GRADE")
        print(f"   {correct}/50 correct, {verified}/50 verified, {avg_time:.1f}ms avg")
    elif correct >= 40:
        print("✓ BENCHMARK PASSED - GOOD")
        print(f"   {correct}/50 correct, {verified}/50 verified, {avg_time:.1f}ms avg")
    else:
        print("⚠️ BENCHMARK NEEDS IMPROVEMENT")
        print(f"   {correct}/50 correct, {verified}/50 verified, {avg_time:.1f}ms avg")
    
    print("═" * 70)
    
    return correct >= 40


if __name__ == "__main__":
    success = run_benchmark()
    exit(0 if success else 1)
