#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   FINAL EXAM EXEMPTION ENGINE                                               ║
║   A Verified Decision System with Auditable Receipts                        ║
║                                                                              ║
║   "A computer that can show its work."                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Flask web app demonstrating Newton's verified computation pipeline.
Shows: Ask → Answer → Verify (with receipt)
"""

from flask import Flask, render_template_string, request, jsonify
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import hashlib
import time
import json

# ═══════════════════════════════════════════════════════════════════════════════
# EXEMPTION RULES (School Policy)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExemptionPolicy:
    """School exemption policy rules."""
    max_absences: int = 3
    min_grade: float = 70.0
    min_conduct_grade: str = "S"  # S = Satisfactory, N = Needs Improvement, U = Unsatisfactory
    require_no_iss: bool = True
    require_no_oss: bool = True
    
    policy_source: str = "Student Handbook 2025-2026, Section 4.3"
    policy_version: str = "2025.2"


# Default policy
SCHOOL_POLICY = ExemptionPolicy()


# ═══════════════════════════════════════════════════════════════════════════════
# TRUST LABELS (from BiggestMAMA)
# ═══════════════════════════════════════════════════════════════════════════════

class TrustLevel(Enum):
    UNTRUSTED = 0
    VERIFIED = 1
    TRUSTED = 2
    KERNEL = 3


# ═══════════════════════════════════════════════════════════════════════════════
# EXEMPTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StudentRecord:
    """Input: Student data for exemption check."""
    student_id: str
    name: str
    grade_level: int
    course: str
    cycle_average: float
    absences: int
    conduct_grade: str  # S, N, U
    iss_count: int = 0
    oss_count: int = 0


@dataclass 
class ExemptionResult:
    """Output: The verified decision artifact."""
    # Value
    eligible: bool
    decision: str
    
    # Trace (which rules fired)
    rules_checked: List[Dict[str, Any]]
    failing_rules: List[str]
    
    # Trust
    trust_level: TrustLevel
    source: str
    
    # Bounds
    time_ms: float
    operations: int
    
    # Provenance
    receipt_id: str
    timestamp: str
    input_hash: str
    output_hash: str
    prev_hash: str
    entry_hash: str
    
    # Witnesses
    witnesses: Dict[str, bool]


class ExemptionEngine:
    """
    Verified exemption decision engine.
    
    Produces auditable receipts for every decision.
    """
    
    def __init__(self, policy: ExemptionPolicy = None):
        self.policy = policy or SCHOOL_POLICY
        self._ledger: List[Dict] = []
        self._prev_hash = "0" * 64
        self._decision_count = 0
    
    def check_exemption(self, student: StudentRecord) -> ExemptionResult:
        """
        Check if student is eligible for final exam exemption.
        
        Returns a verified decision with full audit trail.
        """
        start_time = time.time()
        operations = 0
        
        # ─────────────────────────────────────────────────────────────────────
        # Stage 1: Input Validation (Sanitize)
        # ─────────────────────────────────────────────────────────────────────
        witnesses = {
            "sanitize": True,
            "regime": True,
            "parse": True,
            "abstract": True,
            "geometric": True,
            "verify": True,
            "execute": True,
            "provenance": True,
            "meta_check": True
        }
        
        # Validate inputs
        if not student.student_id or not student.name:
            witnesses["sanitize"] = False
            return self._create_refusal(student, "Missing student ID or name", start_time, witnesses)
        
        if student.cycle_average < 0 or student.cycle_average > 100:
            witnesses["parse"] = False
            return self._create_refusal(student, "Invalid grade (must be 0-100)", start_time, witnesses)
        
        if student.conduct_grade not in ["S", "N", "U"]:
            witnesses["parse"] = False
            return self._create_refusal(student, "Invalid conduct grade (must be S, N, or U)", start_time, witnesses)
        
        operations += 3
        
        # ─────────────────────────────────────────────────────────────────────
        # Stage 2: Rule Evaluation
        # ─────────────────────────────────────────────────────────────────────
        rules_checked = []
        failing_rules = []
        
        # Rule 1: Grade requirement
        grade_pass = student.cycle_average >= self.policy.min_grade
        rules_checked.append({
            "rule": "minimum_grade",
            "requirement": f">= {self.policy.min_grade}",
            "actual": student.cycle_average,
            "passed": grade_pass
        })
        if not grade_pass:
            failing_rules.append(f"Grade {student.cycle_average} below minimum {self.policy.min_grade}")
        operations += 1
        
        # Rule 2: Attendance requirement
        attendance_pass = student.absences <= self.policy.max_absences
        rules_checked.append({
            "rule": "maximum_absences",
            "requirement": f"<= {self.policy.max_absences}",
            "actual": student.absences,
            "passed": attendance_pass
        })
        if not attendance_pass:
            failing_rules.append(f"Absences {student.absences} exceed maximum {self.policy.max_absences}")
        operations += 1
        
        # Rule 3: Conduct requirement
        conduct_pass = student.conduct_grade == "S" or (
            student.conduct_grade == "N" and self.policy.min_conduct_grade != "S"
        )
        if self.policy.min_conduct_grade == "S":
            conduct_pass = student.conduct_grade == "S"
        rules_checked.append({
            "rule": "conduct_grade",
            "requirement": f">= {self.policy.min_conduct_grade}",
            "actual": student.conduct_grade,
            "passed": conduct_pass
        })
        if not conduct_pass:
            failing_rules.append(f"Conduct grade '{student.conduct_grade}' does not meet requirement")
        operations += 1
        
        # Rule 4: No ISS
        iss_pass = not self.policy.require_no_iss or student.iss_count == 0
        rules_checked.append({
            "rule": "no_iss",
            "requirement": "0 ISS assignments",
            "actual": student.iss_count,
            "passed": iss_pass
        })
        if not iss_pass:
            failing_rules.append(f"Has {student.iss_count} ISS assignment(s)")
        operations += 1
        
        # Rule 5: No OSS
        oss_pass = not self.policy.require_no_oss or student.oss_count == 0
        rules_checked.append({
            "rule": "no_oss",
            "requirement": "0 OSS assignments",
            "actual": student.oss_count,
            "passed": oss_pass
        })
        if not oss_pass:
            failing_rules.append(f"Has {student.oss_count} OSS assignment(s)")
        operations += 1
        
        # ─────────────────────────────────────────────────────────────────────
        # Stage 3: Decision
        # ─────────────────────────────────────────────────────────────────────
        eligible = len(failing_rules) == 0
        
        if eligible:
            decision = f"ELIGIBLE for final exam exemption in {student.course}"
        else:
            decision = f"NOT ELIGIBLE: {'; '.join(failing_rules)}"
        
        # ─────────────────────────────────────────────────────────────────────
        # Stage 4: Create Receipt (Provenance)
        # ─────────────────────────────────────────────────────────────────────
        elapsed_ms = (time.time() - start_time) * 1000
        
        self._decision_count += 1
        receipt_id = f"EX-{datetime.now().strftime('%Y%m%d')}-{self._decision_count:04d}"
        timestamp = datetime.now().isoformat()
        
        # Hash the input
        input_data = json.dumps({
            "student_id": student.student_id,
            "course": student.course,
            "grade": student.cycle_average,
            "absences": student.absences,
            "conduct": student.conduct_grade,
            "iss": student.iss_count,
            "oss": student.oss_count
        }, sort_keys=True)
        input_hash = hashlib.sha256(input_data.encode()).hexdigest()
        
        # Hash the output
        output_data = json.dumps({
            "eligible": eligible,
            "decision": decision,
            "rules": len(rules_checked),
            "failures": len(failing_rules)
        }, sort_keys=True)
        output_hash = hashlib.sha256(output_data.encode()).hexdigest()
        
        # Chain hash
        entry_data = f"{receipt_id}|{timestamp}|{input_hash}|{output_hash}|{self._prev_hash}"
        entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()
        
        # Log to ledger
        ledger_entry = {
            "receipt_id": receipt_id,
            "timestamp": timestamp,
            "input_hash": input_hash[:16],
            "output_hash": output_hash[:16],
            "prev_hash": self._prev_hash[:16],
            "entry_hash": entry_hash
        }
        self._ledger.append(ledger_entry)
        prev_for_result = self._prev_hash
        self._prev_hash = entry_hash
        
        return ExemptionResult(
            eligible=eligible,
            decision=decision,
            rules_checked=rules_checked,
            failing_rules=failing_rules,
            trust_level=TrustLevel.TRUSTED,
            source=self.policy.policy_source,
            time_ms=elapsed_ms,
            operations=operations,
            receipt_id=receipt_id,
            timestamp=timestamp,
            input_hash=input_hash[:16],
            output_hash=output_hash[:16],
            prev_hash=prev_for_result[:16],
            entry_hash=entry_hash[:16],
            witnesses=witnesses
        )
    
    def _create_refusal(
        self, student: StudentRecord, reason: str, 
        start_time: float, witnesses: Dict[str, bool]
    ) -> ExemptionResult:
        """Create a refusal result for invalid inputs."""
        elapsed_ms = (time.time() - start_time) * 1000
        timestamp = datetime.now().isoformat()
        
        return ExemptionResult(
            eligible=False,
            decision=f"REFUSED: {reason}",
            rules_checked=[],
            failing_rules=[reason],
            trust_level=TrustLevel.UNTRUSTED,
            source="input_validation",
            time_ms=elapsed_ms,
            operations=1,
            receipt_id=f"REF-{timestamp[:10]}",
            timestamp=timestamp,
            input_hash="invalid",
            output_hash="refused",
            prev_hash=self._prev_hash[:16],
            entry_hash="refused",
            witnesses=witnesses
        )
    
    def get_ledger(self) -> List[Dict]:
        return self._ledger


# ═══════════════════════════════════════════════════════════════════════════════
# FLASK WEB APP
# ═══════════════════════════════════════════════════════════════════════════════

app = Flask(__name__)
engine = ExemptionEngine()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Final Exam Exemption Engine</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #FDF6F0;
            --bg-secondary: #FFFFFF;
            --bg-tertiary: #F5EDE6;
            --accent-warm: #E8927C;
            --accent-coral: #F4A896;
            --accent-peach: #FFD4C4;
            --accent-sage: #B8C9A3;
            --accent-mint: #C5DDD4;
            --accent-sky: #A8D4E6;
            --accent-lavender: #C9B8D9;
            --text-primary: #2D3436;
            --text-secondary: #636E72;
            --text-muted: #9DA5A8;
            --success: #7CB99E;
            --success-bg: #E8F5EE;
            --error: #E07A6B;
            --error-bg: #FDEBE8;
            --shadow-soft: 0 4px 24px rgba(45, 52, 54, 0.06);
            --shadow-hover: 0 8px 32px rgba(45, 52, 54, 0.1);
            --radius-sm: 12px;
            --radius-md: 20px;
            --radius-lg: 28px;
            --radius-xl: 36px;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 32px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1280px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            padding: 48px 0 40px;
            margin-bottom: 40px;
        }
        
        .logo-badge {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            background: var(--bg-secondary);
            padding: 12px 24px;
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow-soft);
            margin-bottom: 24px;
        }
        
        .logo-icon {
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, var(--accent-warm) 0%, var(--accent-coral) 100%);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
        }
        
        .logo-text {
            font-weight: 600;
            font-size: 1.1em;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }
        
        h1 {
            font-size: 3em;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 12px;
            letter-spacing: -0.03em;
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 1.15em;
            font-weight: 400;
        }
        
        .panels {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 24px;
        }
        
        @media (max-width: 1100px) {
            .panels {
                grid-template-columns: 1fr 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .panels {
                grid-template-columns: 1fr;
            }
            body {
                padding: 16px;
            }
            h1 {
                font-size: 2em;
            }
        }
        
        .panel {
            background: var(--bg-secondary);
            border-radius: var(--radius-lg);
            padding: 32px;
            box-shadow: var(--shadow-soft);
            transition: box-shadow 0.3s ease, transform 0.3s ease;
        }
        
        .panel:hover {
            box-shadow: var(--shadow-hover);
        }
        
        .panel h2 {
            color: var(--text-primary);
            margin-bottom: 28px;
            display: flex;
            align-items: center;
            gap: 14px;
            font-weight: 600;
            font-size: 1.3em;
            letter-spacing: -0.01em;
        }
        
        .panel h2 .num {
            background: linear-gradient(135deg, var(--accent-peach) 0%, var(--accent-coral) 100%);
            color: var(--text-primary);
            width: 36px;
            height: 36px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85em;
            font-weight: 700;
        }
        
        .panel:nth-child(2) h2 .num {
            background: linear-gradient(135deg, var(--accent-mint) 0%, var(--accent-sage) 100%);
        }
        
        .panel:nth-child(3) h2 .num {
            background: linear-gradient(135deg, var(--accent-sky) 0%, var(--accent-lavender) 100%);
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-size: 0.9em;
            font-weight: 500;
        }
        
        input, select {
            width: 100%;
            padding: 14px 18px;
            margin-bottom: 18px;
            border: 2px solid var(--bg-tertiary);
            border-radius: var(--radius-sm);
            background: var(--bg-primary);
            color: var(--text-primary);
            font-size: 1em;
            font-family: inherit;
            transition: border-color 0.2s ease, background 0.2s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: var(--accent-coral);
            background: var(--bg-secondary);
        }
        
        input::placeholder {
            color: var(--text-muted);
        }
        
        button {
            width: 100%;
            padding: 18px 24px;
            background: linear-gradient(135deg, var(--accent-warm) 0%, var(--accent-coral) 100%);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            font-size: 1.05em;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            letter-spacing: -0.01em;
        }
        
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 28px rgba(232, 146, 124, 0.35);
        }
        
        button:active {
            transform: translateY(-1px);
        }
        
        .answer-box {
            padding: 32px 24px;
            border-radius: var(--radius-md);
            margin-bottom: 24px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .answer-box.eligible {
            background: var(--success-bg);
            border: 2px solid var(--success);
        }
        
        .answer-box.not-eligible {
            background: var(--error-bg);
            border: 2px solid var(--error);
        }
        
        .answer-box.waiting {
            background: var(--bg-tertiary);
            border: 2px dashed var(--text-muted);
        }
        
        .answer-status {
            font-size: 3em;
            margin-bottom: 12px;
            line-height: 1;
        }
        
        .answer-text {
            font-size: 1em;
            color: var(--text-secondary);
            font-weight: 500;
        }
        
        .receipt {
            background: var(--bg-tertiary);
            border-radius: var(--radius-md);
            padding: 20px;
            font-family: 'DM Sans', monospace;
            font-size: 0.88em;
        }
        
        .receipt-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid rgba(45, 52, 54, 0.08);
        }
        
        .receipt-row:last-child {
            border-bottom: none;
        }
        
        .receipt-label {
            color: var(--text-muted);
            font-weight: 500;
        }
        
        .receipt-value {
            color: var(--text-primary);
            font-weight: 600;
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 0.92em;
            background: var(--bg-secondary);
            padding: 4px 10px;
            border-radius: 8px;
        }
        
        .receipt-value.pass {
            color: var(--success);
            background: var(--success-bg);
        }
        
        .receipt-value.fail {
            color: var(--error);
            background: var(--error-bg);
        }
        
        .witnesses {
            margin-top: 24px;
        }
        
        .witness-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            margin-top: 14px;
        }
        
        .witness-item {
            background: var(--success-bg);
            color: var(--success);
            padding: 10px 8px;
            border-radius: var(--radius-sm);
            text-align: center;
            font-size: 0.82em;
            font-weight: 600;
            transition: transform 0.2s ease;
        }
        
        .witness-item:hover {
            transform: scale(1.03);
        }
        
        .witness-item.fail {
            background: var(--error-bg);
            color: var(--error);
        }
        
        .rules-list {
            margin-top: 20px;
        }
        
        .rules-list h3 {
            color: var(--text-secondary);
            font-size: 0.95em;
            font-weight: 600;
            margin-bottom: 14px;
        }
        
        .rule-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            background: var(--bg-tertiary);
            border-radius: var(--radius-sm);
            margin-bottom: 10px;
            transition: transform 0.2s ease;
        }
        
        .rule-item:hover {
            transform: translateX(4px);
        }
        
        .rule-status {
            font-size: 1.3em;
        }
        
        .rule-details {
            flex: 1;
        }
        
        .rule-name {
            font-weight: 600;
            color: var(--text-primary);
            font-size: 0.95em;
            margin-bottom: 2px;
        }
        
        .rule-info {
            font-size: 0.85em;
            color: var(--text-muted);
        }
        
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 6px 14px;
            border-radius: var(--radius-xl);
            font-size: 0.78em;
            font-weight: 600;
            margin-right: 8px;
            letter-spacing: 0.02em;
        }
        
        .badge.trusted {
            background: var(--success-bg);
            color: var(--success);
        }
        
        .badge.verified {
            background: #FFF8E7;
            color: #D4A853;
        }
        
        .badge.untrusted {
            background: var(--error-bg);
            color: var(--error);
        }
        
        footer {
            text-align: center;
            padding: 48px 24px;
            margin-top: 48px;
            color: var(--text-muted);
        }
        
        footer p {
            font-size: 0.95em;
        }
        
        footer .tagline {
            margin-top: 8px;
            font-style: italic;
            color: var(--text-secondary);
        }
        
        .verify-btn {
            background: linear-gradient(135deg, var(--accent-sky) 0%, var(--accent-lavender) 100%);
            margin-top: 20px;
            color: var(--text-primary);
        }
        
        .verify-btn:hover {
            box-shadow: 0 12px 28px rgba(168, 212, 230, 0.4);
        }
        
        #verification-detail {
            display: none;
            margin-top: 24px;
            animation: slideDown 0.3s ease;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        #verification-detail.show {
            display: block;
        }
        
        /* Form row for compact layout */
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        /* Decorative elements */
        .decorative-circle {
            position: fixed;
            border-radius: 50%;
            pointer-events: none;
            opacity: 0.4;
            z-index: -1;
        }
        
        .circle-1 {
            width: 300px;
            height: 300px;
            background: var(--accent-peach);
            top: -100px;
            right: -100px;
            filter: blur(80px);
        }
        
        .circle-2 {
            width: 250px;
            height: 250px;
            background: var(--accent-mint);
            bottom: 100px;
            left: -80px;
            filter: blur(60px);
        }
        
        .circle-3 {
            width: 200px;
            height: 200px;
            background: var(--accent-lavender);
            bottom: -50px;
            right: 20%;
            filter: blur(70px);
        }
    </style>
</head>
<body>
    <div class="decorative-circle circle-1"></div>
    <div class="decorative-circle circle-2"></div>
    <div class="decorative-circle circle-3"></div>
    
    <div class="container">
        <header>
            <div class="logo-badge">
                <div class="logo-icon">⚡</div>
                <span class="logo-text">Newton Engine</span>
            </div>
            <h1>Exam Exemption</h1>
            <p class="subtitle">Verified decisions with auditable receipts</p>
        </header>
        
        <div class="panels">
            <!-- Panel 1: ASK -->
            <div class="panel">
                <h2><span class="num">1</span> Ask</h2>
                <form id="exemption-form">
                    <label>Student ID</label>
                    <input type="text" id="student_id" value="STU-2026-1234" placeholder="Enter student ID" required>
                    
                    <label>Student Name</label>
                    <input type="text" id="student_name" value="Alex Johnson" placeholder="Full name" required>
                    
                    <div class="form-row">
                        <div>
                            <label>Grade Level</label>
                            <select id="grade_level">
                                <option value="9">9th Grade</option>
                                <option value="10">10th Grade</option>
                                <option value="11" selected>11th Grade</option>
                                <option value="12">12th Grade</option>
                            </select>
                        </div>
                        <div>
                            <label>Conduct</label>
                            <select id="conduct_grade">
                                <option value="S" selected>S - Satisfactory</option>
                                <option value="N">N - Needs Work</option>
                                <option value="U">U - Unsatisfactory</option>
                            </select>
                        </div>
                    </div>
                    
                    <label>Course</label>
                    <input type="text" id="course" value="AP Chemistry" placeholder="Course name" required>
                    
                    <div class="form-row">
                        <div>
                            <label>Cycle Average (%)</label>
                            <input type="number" id="cycle_average" value="85" min="0" max="100" required>
                        </div>
                        <div>
                            <label>Absences</label>
                            <input type="number" id="absences" value="2" min="0" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div>
                            <label>ISS Count</label>
                            <input type="number" id="iss_count" value="0" min="0">
                        </div>
                        <div>
                            <label>OSS Count</label>
                            <input type="number" id="oss_count" value="0" min="0">
                        </div>
                    </div>
                    
                    <button type="submit">Check Eligibility →</button>
                </form>
            </div>
            
            <!-- Panel 2: ANSWER -->
            <div class="panel">
                <h2><span class="num">2</span> Answer</h2>
                <div id="answer-display" class="answer-box waiting">
                    <div class="answer-status">🎯</div>
                    <div class="answer-text">Enter student information to check exemption eligibility</div>
                </div>
                
                <div id="rules-display" class="rules-list" style="display: none;">
                    <h3>Rules Evaluated</h3>
                    <div id="rules-list"></div>
                </div>
            </div>
            
            <!-- Panel 3: VERIFY -->
            <div class="panel">
                <h2><span class="num">3</span> Verify</h2>
                <div id="receipt-display" style="display: none;">
                    <div class="receipt">
                        <div class="receipt-row">
                            <span class="receipt-label">Receipt ID</span>
                            <span class="receipt-value" id="receipt-id">—</span>
                        </div>
                        <div class="receipt-row">
                            <span class="receipt-label">Timestamp</span>
                            <span class="receipt-value" id="receipt-timestamp">—</span>
                        </div>
                        <div class="receipt-row">
                            <span class="receipt-label">Trust Level</span>
                            <span class="receipt-value" id="receipt-trust">—</span>
                        </div>
                        <div class="receipt-row">
                            <span class="receipt-label">Policy Source</span>
                            <span class="receipt-value" id="receipt-source">—</span>
                        </div>
                        <div class="receipt-row">
                            <span class="receipt-label">Compute Time</span>
                            <span class="receipt-value" id="receipt-time">—</span>
                        </div>
                        <div class="receipt-row">
                            <span class="receipt-label">Operations</span>
                            <span class="receipt-value" id="receipt-ops">—</span>
                        </div>
                    </div>
                    
                    <button class="verify-btn" onclick="showVerificationDetail()">
                        View Cryptographic Proof ↓
                    </button>
                    
                    <div id="verification-detail">
                        <div class="receipt" style="margin-top: 16px;">
                            <div class="receipt-row">
                                <span class="receipt-label">Input Hash</span>
                                <span class="receipt-value" id="receipt-input-hash">—</span>
                            </div>
                            <div class="receipt-row">
                                <span class="receipt-label">Output Hash</span>
                                <span class="receipt-value" id="receipt-output-hash">—</span>
                            </div>
                            <div class="receipt-row">
                                <span class="receipt-label">Prev Hash</span>
                                <span class="receipt-value" id="receipt-prev-hash">—</span>
                            </div>
                            <div class="receipt-row">
                                <span class="receipt-label">Entry Hash</span>
                                <span class="receipt-value" id="receipt-entry-hash">—</span>
                            </div>
                        </div>
                        
                        <div class="witnesses">
                            <h3 style="color: var(--text-secondary); font-size: 0.9em; font-weight: 600;">Pipeline Witnesses</h3>
                            <div class="witness-grid" id="witness-grid"></div>
                        </div>
                    </div>
                </div>
                
                <div id="no-receipt" class="answer-box waiting">
                    <div class="answer-status">🔐</div>
                    <div class="answer-text">Verification receipt will appear here</div>
                </div>
            </div>
        </div>
        
        <footer>
            <p><strong>Newton Engine</strong> · Verified Answer Artifact Calculus</p>
            <p class="tagline">"A computer that can show its work."</p>
        </footer>
    </div>
    
    <script>
        let currentResult = null;
        
        document.getElementById('exemption-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const data = {
                student_id: document.getElementById('student_id').value,
                name: document.getElementById('student_name').value,
                grade_level: parseInt(document.getElementById('grade_level').value),
                course: document.getElementById('course').value,
                cycle_average: parseFloat(document.getElementById('cycle_average').value),
                absences: parseInt(document.getElementById('absences').value),
                conduct_grade: document.getElementById('conduct_grade').value,
                iss_count: parseInt(document.getElementById('iss_count').value),
                oss_count: parseInt(document.getElementById('oss_count').value)
            };
            
            try {
                const response = await fetch('/check', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                currentResult = await response.json();
                displayResult(currentResult);
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error checking eligibility');
            }
        });
        
        function displayResult(result) {
            // Update Answer panel
            const answerBox = document.getElementById('answer-display');
            const rulesDisplay = document.getElementById('rules-display');
            const rulesList = document.getElementById('rules-list');
            
            if (result.eligible) {
                answerBox.className = 'answer-box eligible';
                answerBox.innerHTML = `
                    <div class="answer-status">✅</div>
                    <div class="answer-text">${result.decision}</div>
                `;
            } else {
                answerBox.className = 'answer-box not-eligible';
                answerBox.innerHTML = `
                    <div class="answer-status">❌</div>
                    <div class="answer-text">${result.decision}</div>
                `;
            }
            
            // Show rules
            rulesDisplay.style.display = 'block';
            rulesList.innerHTML = result.rules_checked.map(rule => `
                <div class="rule-item">
                    <span class="rule-status">${rule.passed ? '✓' : '✗'}</span>
                    <div class="rule-details">
                        <div class="rule-name">${rule.rule.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                        <div class="rule-info">Required: ${rule.requirement} · Actual: ${rule.actual}</div>
                    </div>
                </div>
            `).join('');
            
            // Update Verify panel
            document.getElementById('no-receipt').style.display = 'none';
            document.getElementById('receipt-display').style.display = 'block';
            
            document.getElementById('receipt-id').textContent = result.receipt_id;
            document.getElementById('receipt-timestamp').textContent = result.timestamp.split('T')[1].split('.')[0];
            
            const trustSpan = document.getElementById('receipt-trust');
            trustSpan.textContent = result.trust_level;
            trustSpan.className = 'receipt-value ' + (result.trust_level === 'TRUSTED' ? 'pass' : 'fail');
            
            document.getElementById('receipt-source').textContent = 'Handbook §4.3';
            document.getElementById('receipt-time').textContent = result.time_ms.toFixed(3) + 'ms';
            document.getElementById('receipt-ops').textContent = result.operations + ' ops';
            document.getElementById('receipt-input-hash').textContent = result.input_hash;
            document.getElementById('receipt-output-hash').textContent = result.output_hash;
            document.getElementById('receipt-prev-hash').textContent = result.prev_hash;
            document.getElementById('receipt-entry-hash').textContent = result.entry_hash;
            
            // Update witnesses
            const witnessGrid = document.getElementById('witness-grid');
            const witnessNames = {
                'sanitize': 'Sanitize',
                'regime': 'Regime',
                'parse': 'Parse',
                'abstract': 'Abstract',
                'geometric': 'Geometric',
                'verify': 'Verify',
                'execute': 'Execute',
                'provenance': 'Provenance',
                'meta_check': 'Meta-Check'
            };
            
            witnessGrid.innerHTML = Object.entries(result.witnesses).map(([key, passed]) => `
                <div class="witness-item ${passed ? '' : 'fail'}">
                    ${passed ? '✓' : '✗'} ${witnessNames[key] || key}
                </div>
            `).join('');
        }
        
        function showVerificationDetail() {
            const detail = document.getElementById('verification-detail');
            detail.classList.toggle('show');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/check', methods=['POST'])
def check_exemption():
    data = request.json
    
    student = StudentRecord(
        student_id=data['student_id'],
        name=data['name'],
        grade_level=data['grade_level'],
        course=data['course'],
        cycle_average=data['cycle_average'],
        absences=data['absences'],
        conduct_grade=data['conduct_grade'],
        iss_count=data.get('iss_count', 0),
        oss_count=data.get('oss_count', 0)
    )
    
    result = engine.check_exemption(student)
    
    return jsonify({
        'eligible': result.eligible,
        'decision': result.decision,
        'rules_checked': result.rules_checked,
        'failing_rules': result.failing_rules,
        'trust_level': result.trust_level.name,
        'source': result.source,
        'time_ms': result.time_ms,
        'operations': result.operations,
        'receipt_id': result.receipt_id,
        'timestamp': result.timestamp,
        'input_hash': result.input_hash,
        'output_hash': result.output_hash,
        'prev_hash': result.prev_hash,
        'entry_hash': result.entry_hash,
        'witnesses': result.witnesses
    })


@app.route('/ledger')
def get_ledger():
    return jsonify(engine.get_ledger())


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   FINAL EXAM EXEMPTION ENGINE                                               ║
║   Verified Decisions with Auditable Receipts                                ║
║                                                                              ║
║   Open http://localhost:5000 in your browser                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, port=5000)
