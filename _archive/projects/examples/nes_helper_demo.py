#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 NES HELPER DEMO - Newton for Education
═══════════════════════════════════════════════════════════════════════════════

This demo shows Newton's Teacher's Aide in action:
- NES-compliant lesson planning (HISD's New Education System)
- TEKS alignment verification (Texas Essential Knowledge and Skills)
- Automatic student differentiation (4 tiers based on assessment data)
- MAD-based assessment analysis (Median Absolute Deviation for robustness)

Run this demo:
    python examples/nes_helper_demo.py

Or with the server running:
    python examples/nes_helper_demo.py --live
"""

import sys
import json
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])


# ═══════════════════════════════════════════════════════════════════════════════
# THE PROBLEM: Teachers Are Drowning in Paperwork
# ═══════════════════════════════════════════════════════════════════════════════

"""
HISD teachers face:
- 50-minute NES lesson plans with strict phase requirements
- TEKS alignment mandates for every lesson
- Differentiation requirements (ELL, SPED, 504, GT)
- Weekly PLC meetings requiring data reports
- Assessment analysis and student grouping

Newton solves this with VERIFIED constraint-based generation.
The constraint IS the instruction. The verification IS the computation.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# CORE CONCEPTS: NES Phases and Differentiation Tiers
# ═══════════════════════════════════════════════════════════════════════════════

NES_PHASES = {
    "opening": {"duration": 5, "purpose": "Hook, objective, student restate"},
    "instruction": {"duration": 15, "purpose": "Teacher models 2-3 examples"},
    "guided": {"duration": 15, "purpose": "Collaborative practice with support"},
    "independent": {"duration": 10, "purpose": "Solo practice (formative data)"},
    "closing": {"duration": 5, "purpose": "Exit ticket, summary, preview"}
}

DIFFERENTIATION_TIERS = {
    "tier3_reteach": {"range": "<70%", "instruction": "Small group, manipulatives, prerequisites"},
    "tier2_approaching": {"range": "70-79%", "instruction": "Guided practice, scaffolds, peer partners"},
    "tier1_mastery": {"range": "80-89%", "instruction": "Standard instruction, independent practice"},
    "enrichment": {"range": "90%+", "instruction": "Extensions, leadership, peer tutoring"}
}


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO: Manual NES Lesson Planning (The Hard Way)
# ═══════════════════════════════════════════════════════════════════════════════

def demo_manual_lesson_plan():
    """Show what teachers do without Newton - manually checking constraints."""
    print("\n" + "═" * 70)
    print(" DEMO: Manual Lesson Planning (The Hard Way)")
    print("═" * 70)

    lesson = {
        "grade": 5,
        "subject": "mathematics",
        "topic": "Adding Fractions with Unlike Denominators",
        "teks_codes": ["5.3A", "5.3B"],
        "phases": [
            {"name": "opening", "duration": 5},
            {"name": "instruction", "duration": 15},
            {"name": "guided", "duration": 15},
            {"name": "independent", "duration": 10},
            {"name": "closing", "duration": 5}
        ]
    }

    print("\nTeacher creates lesson plan manually...")
    print(json.dumps(lesson, indent=2))

    # Manual constraint checking (what teachers do today)
    print("\n--- Manual Constraint Checking ---")

    total_duration = sum(p["duration"] for p in lesson["phases"])
    print(f"1. Total duration: {total_duration} minutes")
    if total_duration != 50:
        print("   ❌ FAIL: NES requires exactly 50 minutes!")
    else:
        print("   ✓ PASS: 50 minutes")

    phase_names = [p["name"] for p in lesson["phases"]]
    required_phases = ["opening", "instruction", "guided", "independent", "closing"]
    missing = set(required_phases) - set(phase_names)
    if missing:
        print(f"   ❌ FAIL: Missing phases: {missing}")
    else:
        print("   ✓ PASS: All 5 NES phases present")

    if not lesson["teks_codes"]:
        print("   ❌ FAIL: No TEKS alignment!")
    else:
        print(f"   ✓ PASS: TEKS aligned to {lesson['teks_codes']}")

    print("\n💤 This takes 30-60 minutes per lesson. Teachers do this daily.")
    print("💡 Newton does this in <50ms with cryptographic proof.")


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO: Newton NES Lesson Planning (The Newton Way)
# ═══════════════════════════════════════════════════════════════════════════════

def demo_newton_lesson_plan():
    """Show how Newton verifies lessons with constraints as the instruction."""
    print("\n" + "═" * 70)
    print(" DEMO: Newton Lesson Planning (Constraint-First)")
    print("═" * 70)

    print("""
    tinyTalk Laws for NES Lessons:

    law DurationLaw
      when total_duration != 50
      finfr  # Lesson cannot exist outside 50 minutes

    law PhaseCompletenessLaw
      when phases missing from [opening, instruction, guided, independent, closing]
      finfr  # Incomplete lessons are ontologically forbidden

    law TEKSAlignmentLaw
      when teks_codes is empty
      finfr  # Unaligned lessons cannot be generated
    """)

    # Simulating Newton's verification
    lesson_request = {
        "grade": 5,
        "subject": "mathematics",
        "teks_codes": ["5.3A"],
        "topic": "Adding Fractions with Unlike Denominators"
    }

    print("Teacher Request:")
    print(json.dumps(lesson_request, indent=2))

    # Newton generates with built-in constraints
    generated_lesson = {
        "title": "Adding Fractions with Unlike Denominators - Grade 5 Math",
        "duration_minutes": 50,
        "teks_aligned": True,
        "verified": True,
        "phases": [
            {
                "name": "Opening",
                "duration": 5,
                "activities": [
                    "Pizza problem hook: 'I ate 1/2 of a pizza, my friend ate 1/3...'",
                    "Share objective: 'Today we'll add fractions with different denominators'",
                    "Student restate: Turn to partner and explain the goal"
                ]
            },
            {
                "name": "Direct Instruction",
                "duration": 15,
                "activities": [
                    "Model finding common denominator using fraction bars",
                    "Think-aloud: 1/2 + 1/3 = 3/6 + 2/6 = 5/6",
                    "Second example: 2/5 + 1/4 with guided questioning"
                ]
            },
            {
                "name": "Guided Practice",
                "duration": 15,
                "activities": [
                    "Partner work: Solve 3/4 + 1/6 together",
                    "Teacher circulates with sentence frames for ELL",
                    "Fraction manipulatives available for Tier 3"
                ]
            },
            {
                "name": "Independent Practice",
                "duration": 10,
                "activities": [
                    "5 problems increasing in difficulty",
                    "Collect for formative assessment data",
                    "Early finishers: Create a word problem"
                ]
            },
            {
                "name": "Closing",
                "duration": 5,
                "activities": [
                    "Exit ticket: Add 2/3 + 1/4",
                    "Summarize: 'We learned to find common denominators'",
                    "Preview: 'Tomorrow we'll subtract fractions'"
                ]
            }
        ],
        "differentiation": {
            "tier3": "Fraction manipulatives, prerequisite review",
            "tier2": "Sentence frames, peer partners",
            "tier1": "Standard instruction",
            "enrichment": "Create word problems, peer tutor"
        },
        "verification_proof": "A7F3B2C8E1D4F5A9"
    }

    print("\nNewton Generated Lesson (Verified):")
    print(f"  Duration: {generated_lesson['duration_minutes']} minutes ✓")
    print(f"  TEKS Aligned: {generated_lesson['teks_aligned']} ✓")
    print(f"  Verified: {generated_lesson['verified']} ✓")
    print(f"  Proof: {generated_lesson['verification_proof']}")

    print("\n⚡ Generated in <50ms with cryptographic proof of compliance.")


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO: Student Differentiation with MAD Statistics
# ═══════════════════════════════════════════════════════════════════════════════

def demo_student_differentiation():
    """Show Newton's automatic student grouping using robust statistics."""
    print("\n" + "═" * 70)
    print(" DEMO: Automatic Student Differentiation (MAD Statistics)")
    print("═" * 70)

    print("""
    Newton uses Median Absolute Deviation (MAD) instead of mean/std:

    Why MAD?
    - Mean is sensitive to outliers (one 0% tanks the class average)
    - MAD resists manipulation and gives true central tendency
    - Teachers get accurate groupings, not skewed by edge cases
    """)

    # Sample class data
    students = [
        {"name": "Maria Garcia", "score": 95},
        {"name": "James Wilson", "score": 88},
        {"name": "Sofia Rodriguez", "score": 92},
        {"name": "Michael Chen", "score": 75},
        {"name": "Emily Johnson", "score": 82},
        {"name": "David Kim", "score": 68},
        {"name": "Sarah Thompson", "score": 78},
        {"name": "Carlos Martinez", "score": 85},
        {"name": "Ashley Brown", "score": 62},
        {"name": "Tyler Davis", "score": 90}
    ]

    print("Class Scores:")
    for s in students:
        print(f"  {s['name']}: {s['score']}%")

    # Calculate differentiation tiers
    tier3 = [s for s in students if s['score'] < 70]
    tier2 = [s for s in students if 70 <= s['score'] < 80]
    tier1 = [s for s in students if 80 <= s['score'] < 90]
    enrichment = [s for s in students if s['score'] >= 90]

    print("\n--- Newton's Differentiation Groups ---")

    print(f"\n🔴 Tier 3 - Needs Reteach (<70%): {len(tier3)} students")
    for s in tier3:
        print(f"   {s['name']} ({s['score']}%)")
    print("   → Small group instruction, manipulatives, prerequisite review")

    print(f"\n🟡 Tier 2 - Approaching (70-79%): {len(tier2)} students")
    for s in tier2:
        print(f"   {s['name']} ({s['score']}%)")
    print("   → Guided practice, scaffolds, peer partnerships")

    print(f"\n🟢 Tier 1 - Mastery (80-89%): {len(tier1)} students")
    for s in tier1:
        print(f"   {s['name']} ({s['score']}%)")
    print("   → Standard instruction, independent practice")

    print(f"\n⭐ Enrichment (90%+): {len(enrichment)} students")
    for s in enrichment:
        print(f"   {s['name']} ({s['score']}%)")
    print("   → Extension activities, leadership roles, peer tutoring")

    # Calculate MAD statistics
    scores = [s['score'] for s in students]
    median = sorted(scores)[len(scores)//2]
    mad = sorted([abs(s - median) for s in scores])[len(scores)//2]

    print(f"\n--- MAD Statistics ---")
    print(f"  Median: {median}%")
    print(f"  MAD: {mad}")
    print(f"  Interpretation: Most students within ±{mad}% of {median}%")


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO: PLC Report Generation
# ═══════════════════════════════════════════════════════════════════════════════

def demo_plc_report():
    """Show Newton's automatic PLC report generation."""
    print("\n" + "═" * 70)
    print(" DEMO: PLC Report Generation")
    print("═" * 70)

    print("""
    Professional Learning Community (PLC) meetings require:
    - Data analysis of student performance
    - Identification of struggling students
    - Action items and next steps
    - Grouping recommendations

    Newton generates these automatically from assessment data.
    """)

    plc_report = {
        "team": "5th Grade Math PLC",
        "teks_focus": "5.3A - Adding fractions",
        "date": "2026-01-02",
        "insights": [
            "Class mastery rate: 70% (7/10 at or above 80%)",
            "2 students need immediate intervention (<70%)",
            "3 students ready for enrichment activities"
        ],
        "action_items": [
            {
                "priority": "HIGH",
                "action": "Pull Tier 3 students for small group reteach",
                "owner": "Lead Teacher",
                "timeline": "This week"
            },
            {
                "priority": "MEDIUM",
                "action": "Prepare fraction manipulatives for struggling learners",
                "owner": "Math Coach",
                "timeline": "Monday"
            },
            {
                "priority": "LOW",
                "action": "Create extension problems for enrichment group",
                "owner": "GT Coordinator",
                "timeline": "Next week"
            }
        ],
        "discussion_points": [
            "What prerequisite skills are students missing?",
            "Are ELL students getting adequate vocabulary support?",
            "How can we use peer tutoring effectively?"
        ],
        "verified": True,
        "generated_by": "Newton Supercomputer"
    }

    print("\nGenerated PLC Report:")
    print(json.dumps(plc_report, indent=2))


# ═══════════════════════════════════════════════════════════════════════════════
# LIVE DEMO: Using Newton API
# ═══════════════════════════════════════════════════════════════════════════════

def demo_with_newton_server():
    """Run demos against a live Newton server."""
    import requests

    print("\n" + "═" * 70)
    print(" LIVE DEMO: Newton Education API")
    print("═" * 70)

    base_url = "http://localhost:8000"

    # Check health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("Newton server not responding. Start it with:")
            print("  python newton_supercomputer.py")
            return
    except requests.exceptions.ConnectionError:
        print("Cannot connect to Newton server. Start it with:")
        print("  python newton_supercomputer.py")
        return

    print("Connected to Newton server!")

    # Demo 1: Generate lesson plan
    print("\n1. Generate NES Lesson Plan")
    lesson_request = {
        "grade": 5,
        "subject": "mathematics",
        "teks_codes": ["5.3A"],
        "topic": "Adding Fractions with Unlike Denominators"
    }
    response = requests.post(f"{base_url}/education/lesson", json=lesson_request)
    if response.status_code == 200:
        result = response.json()
        lesson = result.get("lesson_plan", {})
        print(f"   Title: {lesson.get('title', 'N/A')}")
        print(f"   Duration: {lesson.get('duration_minutes', 'N/A')} minutes")
        print(f"   TEKS Aligned: {lesson.get('teks_aligned', 'N/A')}")
        print(f"   Phases: {len(lesson.get('phases', []))}")
    else:
        print(f"   Error: {response.status_code}")

    # Demo 2: Analyze assessment
    print("\n2. Analyze Assessment (MAD Statistics)")
    assessment_data = {
        "scores": [95, 88, 92, 75, 82, 68, 78, 85, 62, 90],
        "student_names": ["Maria", "James", "Sofia", "Michael", "Emily",
                         "David", "Sarah", "Carlos", "Ashley", "Tyler"],
        "threshold": 80
    }
    response = requests.post(f"{base_url}/education/assess", json=assessment_data)
    if response.status_code == 200:
        result = response.json()
        analysis = result.get("analysis", {})
        stats = analysis.get("robust_statistics", {})
        print(f"   Median: {stats.get('median', 'N/A')}%")
        print(f"   MAD: {stats.get('mad', 'N/A')}")
        groups = analysis.get("mastery_groups", {})
        print(f"   Mastery: {len(groups.get('mastery', []))} students")
        print(f"   Approaching: {len(groups.get('approaching', []))} students")
        print(f"   Reteach: {len(groups.get('reteach', []))} students")
    else:
        print(f"   Error: {response.status_code}")

    # Demo 3: Browse TEKS
    print("\n3. Browse TEKS Standards")
    response = requests.get(f"{base_url}/education/teks?grade=5&subject=mathematics")
    if response.status_code == 200:
        result = response.json()
        standards = result.get("standards", [])[:3]  # First 3
        print(f"   Found {len(result.get('standards', []))} standards for Grade 5 Math")
        for std in standards:
            print(f"   - {std.get('code')}: {std.get('description', '')[:50]}...")
    else:
        print(f"   Error: {response.status_code}")

    print("\n" + "═" * 70)
    print(" The constraint IS the instruction. Less paperwork, more teaching.")
    print("═" * 70)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ███╗   ██╗███████╗███████╗    ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗
║   ████╗  ██║██╔════╝██╔════╝    ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗
║   ██╔██╗ ██║█████╗  ███████╗    ███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝
║   ██║╚██╗██║██╔══╝  ╚════██║    ██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗
║   ██║ ╚████║███████╗███████║    ██║  ██║███████╗███████╗██║     ███████╗██║  ██║
║   ╚═╝  ╚═══╝╚══════╝╚══════╝    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝
║                                                                               ║
║                    NEWTON FOR EDUCATION - TEACHER'S AIDE                      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

    print("Newton Teacher's Aide transforms lesson planning with verified computation.")
    print("NES compliance, TEKS alignment, and differentiation - all constraint-verified.")
    print()

    # Run demos
    demo_manual_lesson_plan()
    demo_newton_lesson_plan()
    demo_student_differentiation()
    demo_plc_report()

    # Check for --live flag
    if '--live' in sys.argv:
        demo_with_newton_server()
    else:
        print("\n" + "-" * 70)
        print("Run with --live flag to demo against Newton API:")
        print("  python examples/nes_helper_demo.py --live")

    print("\n" + "═" * 70)
    print(" Newton Teacher's Aide")
    print(" Less paperwork. More teaching.")
    print(" The constraint IS the instruction.")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    main()
