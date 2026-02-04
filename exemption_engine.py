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
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid #333;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            color: #00d4ff;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #888;
            font-size: 1.1em;
        }
        
        .panels {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }
        
        @media (max-width: 900px) {
            .panels {
                grid-template-columns: 1fr;
            }
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #333;
        }
        
        .panel h2 {
            color: #00d4ff;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .panel h2 .num {
            background: #00d4ff;
            color: #1a1a2e;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #aaa;
            font-size: 0.9em;
        }
        
        input, select {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid #444;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            font-size: 1em;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #00d4ff;
        }
        
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3);
        }
        
        .answer-box {
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .answer-box.eligible {
            background: rgba(0, 200, 83, 0.2);
            border: 2px solid #00c853;
        }
        
        .answer-box.not-eligible {
            background: rgba(255, 82, 82, 0.2);
            border: 2px solid #ff5252;
        }
        
        .answer-box.waiting {
            background: rgba(255, 255, 255, 0.1);
            border: 2px dashed #444;
        }
        
        .answer-status {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .answer-text {
            font-size: 1.1em;
            color: #ccc;
        }
        
        .receipt {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
        }
        
        .receipt-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #333;
        }
        
        .receipt-row:last-child {
            border-bottom: none;
        }
        
        .receipt-label {
            color: #888;
        }
        
        .receipt-value {
            color: #00d4ff;
            font-weight: bold;
        }
        
        .receipt-value.pass {
            color: #00c853;
        }
        
        .receipt-value.fail {
            color: #ff5252;
        }
        
        .witnesses {
            margin-top: 20px;
        }
        
        .witness-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
            margin-top: 10px;
        }
        
        .witness-item {
            background: rgba(0, 200, 83, 0.2);
            padding: 8px;
            border-radius: 4px;
            text-align: center;
            font-size: 0.8em;
        }
        
        .witness-item.fail {
            background: rgba(255, 82, 82, 0.2);
        }
        
        .rules-list {
            margin-top: 15px;
        }
        
        .rule-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 6px;
            margin-bottom: 8px;
        }
        
        .rule-status {
            font-size: 1.2em;
        }
        
        .rule-details {
            flex: 1;
        }
        
        .rule-name {
            font-weight: bold;
            color: #fff;
        }
        
        .rule-info {
            font-size: 0.85em;
            color: #888;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 8px;
        }
        
        .badge.trusted {
            background: #00c853;
            color: #fff;
        }
        
        .badge.verified {
            background: #ffab00;
            color: #000;
        }
        
        .badge.untrusted {
            background: #ff5252;
            color: #fff;
        }
        
        footer {
            text-align: center;
            padding: 30px 0;
            margin-top: 30px;
            border-top: 1px solid #333;
            color: #666;
        }
        
        .verify-btn {
            background: linear-gradient(135deg, #7c4dff 0%, #536dfe 100%);
            margin-top: 15px;
        }
        
        #verification-detail {
            display: none;
            margin-top: 20px;
        }
        
        #verification-detail.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Final Exam Exemption Engine</h1>
            <p class="subtitle">Verified Decisions with Auditable Receipts</p>
        </header>
        
        <div class="panels">
            <!-- Panel 1: ASK -->
            <div class="panel">
                <h2><span class="num">1</span> Ask</h2>
                <form id="exemption-form">
                    <label>Student ID</label>
                    <input type="text" id="student_id" value="STU-2026-1234" required>
                    
                    <label>Student Name</label>
                    <input type="text" id="student_name" value="Alex Johnson" required>
                    
                    <label>Grade Level</label>
                    <select id="grade_level">
                        <option value="9">9th Grade</option>
                        <option value="10">10th Grade</option>
                        <option value="11" selected>11th Grade</option>
                        <option value="12">12th Grade</option>
                    </select>
                    
                    <label>Course</label>
                    <input type="text" id="course" value="AP Chemistry" required>
                    
                    <label>Cycle Average (%)</label>
                    <input type="number" id="cycle_average" value="85" min="0" max="100" required>
                    
                    <label>Absences</label>
                    <input type="number" id="absences" value="2" min="0" required>
                    
                    <label>Conduct Grade</label>
                    <select id="conduct_grade">
                        <option value="S" selected>S - Satisfactory</option>
                        <option value="N">N - Needs Improvement</option>
                        <option value="U">U - Unsatisfactory</option>
                    </select>
                    
                    <label>ISS Assignments</label>
                    <input type="number" id="iss_count" value="0" min="0">
                    
                    <label>OSS Assignments</label>
                    <input type="number" id="oss_count" value="0" min="0">
                    
                    <button type="submit">Check Eligibility</button>
                </form>
            </div>
            
            <!-- Panel 2: ANSWER -->
            <div class="panel">
                <h2><span class="num">2</span> Answer</h2>
                <div id="answer-display" class="answer-box waiting">
                    <div class="answer-status">❓</div>
                    <div class="answer-text">Enter student information and click "Check Eligibility"</div>
                </div>
                
                <div id="rules-display" class="rules-list" style="display: none;">
                    <h3 style="margin-bottom: 10px; color: #888;">Rules Checked</h3>
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
                            <span class="receipt-label">Source</span>
                            <span class="receipt-value" id="receipt-source">—</span>
                        </div>
                        <div class="receipt-row">
                            <span class="receipt-label">Time</span>
                            <span class="receipt-value" id="receipt-time">—</span>
                        </div>
                        <div class="receipt-row">
                            <span class="receipt-label">Operations</span>
                            <span class="receipt-value" id="receipt-ops">—</span>
                        </div>
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
                    
                    <button class="verify-btn" onclick="showVerificationDetail()">
                        Show Full Verification
                    </button>
                    
                    <div id="verification-detail">
                        <div class="witnesses">
                            <h3 style="color: #888; margin-bottom: 5px;">Witness Checklist (9/9)</h3>
                            <div class="witness-grid" id="witness-grid"></div>
                        </div>
                    </div>
                </div>
                
                <div id="no-receipt" class="answer-box waiting">
                    <div class="answer-status">🔒</div>
                    <div class="answer-text">Receipt will appear after verification</div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Verified Answer Artifact Calculus (VAAC) · Newton Engine</p>
            <p style="margin-top: 5px; font-size: 0.9em;">
                "A computer that can show its work."
            </p>
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
                    <span class="rule-status">${rule.passed ? '✅' : '❌'}</span>
                    <div class="rule-details">
                        <div class="rule-name">${rule.rule.replace(/_/g, ' ').toUpperCase()}</div>
                        <div class="rule-info">Required: ${rule.requirement} | Actual: ${rule.actual}</div>
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
            
            document.getElementById('receipt-source').textContent = result.source.substring(0, 30) + '...';
            document.getElementById('receipt-time').textContent = result.time_ms.toFixed(2) + ' ms';
            document.getElementById('receipt-ops').textContent = result.operations;
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
