"""
═══════════════════════════════════════════════════════════════════════════════
 Teacher's Aide Database - Easy-to-Use Education Data Management
═══════════════════════════════════════════════════════════════════════════════

A simple, teacher-friendly database for managing students, classrooms,
assessments, and differentiated instruction. Designed to make teachers'
lives easier by automating grouping and tracking.

"Less paperwork, more teaching."

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from datetime import datetime, date
import json
import hashlib
import os

from .education import (
    Subject, CognitiveLevel, TEKSStandard, TEKSLibrary, get_teks_library,
    StudentScore, AssessmentAnalyzer
)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS - Status and Types
# ═══════════════════════════════════════════════════════════════════════════════

class MasteryLevel(Enum):
    """Student mastery levels for differentiation."""
    NOT_ASSESSED = "not_assessed"
    NEEDS_RETEACH = "needs_reteach"      # Below 70%
    APPROACHING = "approaching"           # 70-79%
    MASTERY = "mastery"                   # 80-89%
    ADVANCED = "advanced"                 # 90%+


class AccommodationType(Enum):
    """Types of student accommodations."""
    NONE = "none"
    ELL = "ell"                           # English Language Learner
    SPED = "sped"                         # Special Education
    PLAN_504 = "504"                      # 504 Plan
    GT = "gt"                             # Gifted & Talented
    DYSLEXIA = "dyslexia"
    RTI = "rti"                           # Response to Intervention


class GradingPeriod(Enum):
    """Grading periods for Texas schools."""
    Q1 = "q1"
    Q2 = "q2"
    Q3 = "q3"
    Q4 = "q4"


# ═══════════════════════════════════════════════════════════════════════════════
# STUDENT MODEL - Individual Student Data
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Student:
    """
    A student in the classroom.

    Tracks all relevant data for differentiated instruction.
    """
    student_id: str
    first_name: str
    last_name: str
    grade: int

    # Accommodations & Support
    accommodations: List[AccommodationType] = field(default_factory=list)
    accommodation_notes: str = ""

    # Current Performance by Subject (TEKS code -> MasteryLevel)
    mastery_by_teks: Dict[str, MasteryLevel] = field(default_factory=dict)

    # Assessment History (assessment_id -> percentage)
    assessment_history: Dict[str, float] = field(default_factory=dict)

    # Grouping (auto-calculated)
    current_group: MasteryLevel = MasteryLevel.NOT_ASSESSED

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self) -> str:
        """Last, First format for rosters."""
        return f"{self.last_name}, {self.first_name}"

    def has_accommodation(self, acc_type: AccommodationType) -> bool:
        """Check if student has a specific accommodation."""
        return acc_type in self.accommodations

    def get_average_score(self) -> float:
        """Get average assessment score."""
        if not self.assessment_history:
            return 0.0
        return sum(self.assessment_history.values()) / len(self.assessment_history)

    def update_mastery(self, teks_code: str, percentage: float):
        """Update mastery level for a TEKS standard based on score."""
        if percentage >= 90:
            level = MasteryLevel.ADVANCED
        elif percentage >= 80:
            level = MasteryLevel.MASTERY
        elif percentage >= 70:
            level = MasteryLevel.APPROACHING
        else:
            level = MasteryLevel.NEEDS_RETEACH

        self.mastery_by_teks[teks_code] = level
        self.updated_at = datetime.now().isoformat()
        self._recalculate_group()

    def _recalculate_group(self):
        """Recalculate current group based on recent mastery levels."""
        if not self.mastery_by_teks:
            self.current_group = MasteryLevel.NOT_ASSESSED
            return

        # Use most recent 5 standards to determine group
        recent = list(self.mastery_by_teks.values())[-5:]

        # Count levels
        counts = {level: recent.count(level) for level in MasteryLevel}

        # Majority wins, with bias toward intervention
        if counts[MasteryLevel.NEEDS_RETEACH] >= 2:
            self.current_group = MasteryLevel.NEEDS_RETEACH
        elif counts[MasteryLevel.APPROACHING] >= 2:
            self.current_group = MasteryLevel.APPROACHING
        elif counts[MasteryLevel.ADVANCED] >= 3:
            self.current_group = MasteryLevel.ADVANCED
        else:
            self.current_group = MasteryLevel.MASTERY

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "grade": self.grade,
            "accommodations": [a.value for a in self.accommodations],
            "accommodation_notes": self.accommodation_notes,
            "current_group": self.current_group.value,
            "average_score": round(self.get_average_score(), 1),
            "assessments_taken": len(self.assessment_history),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def to_simple_dict(self) -> Dict[str, Any]:
        """Simplified dict for grouping displays."""
        return {
            "id": self.student_id,
            "name": self.full_name,
            "group": self.current_group.value,
            "avg": round(self.get_average_score(), 1),
            "accommodations": [a.value for a in self.accommodations]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSROOM MODEL - Group of Students
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Classroom:
    """
    A classroom/class period.

    Contains students and provides easy grouping methods.
    """
    classroom_id: str
    name: str                              # e.g., "5th Period Math"
    grade: int
    subject: Subject
    teacher_name: str = ""

    # Students (student_id -> Student)
    students: Dict[str, Student] = field(default_factory=dict)

    # Current TEKS focus
    current_teks: List[str] = field(default_factory=list)

    # Metadata
    school_year: str = field(default_factory=lambda: f"{datetime.now().year}-{datetime.now().year + 1}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def student_count(self) -> int:
        return len(self.students)

    def add_student(self, student: Student) -> str:
        """Add a student to the classroom."""
        self.students[student.student_id] = student
        return f"Added {student.full_name}"

    def remove_student(self, student_id: str) -> str:
        """Remove a student from the classroom."""
        if student_id in self.students:
            name = self.students[student_id].full_name
            del self.students[student_id]
            return f"Removed {name}"
        return "Student not found"

    def get_student(self, student_id: str) -> Optional[Student]:
        """Get a student by ID."""
        return self.students.get(student_id)

    def get_students_by_name(self, name: str) -> List[Student]:
        """Search students by name (partial match)."""
        name_lower = name.lower()
        return [s for s in self.students.values()
                if name_lower in s.full_name.lower()]

    # ═══════════════════════════════════════════════════════════════════════════
    # DIFFERENTIATION - The Key Feature for Teachers
    # ═══════════════════════════════════════════════════════════════════════════

    def get_groups(self) -> Dict[str, List[Student]]:
        """
        Get students grouped by mastery level.

        This is THE key method for differentiation.
        Returns groups ready for small group instruction.
        """
        groups = {
            "needs_reteach": [],
            "approaching": [],
            "mastery": [],
            "advanced": [],
            "not_assessed": []
        }

        for student in self.students.values():
            if student.current_group == MasteryLevel.NEEDS_RETEACH:
                groups["needs_reteach"].append(student)
            elif student.current_group == MasteryLevel.APPROACHING:
                groups["approaching"].append(student)
            elif student.current_group == MasteryLevel.MASTERY:
                groups["mastery"].append(student)
            elif student.current_group == MasteryLevel.ADVANCED:
                groups["advanced"].append(student)
            else:
                groups["not_assessed"].append(student)

        return groups

    def get_differentiation_report(self) -> Dict[str, Any]:
        """
        Generate a differentiation report for the classroom.

        Designed to be printed and used during planning.
        """
        groups = self.get_groups()

        return {
            "classroom": self.name,
            "grade": self.grade,
            "subject": self.subject.value,
            "total_students": self.student_count,
            "current_teks": self.current_teks,
            "groups": {
                "tier_3_intensive": {
                    "label": "🔴 Needs Reteach (Tier 3)",
                    "count": len(groups["needs_reteach"]),
                    "students": [s.to_simple_dict() for s in groups["needs_reteach"]],
                    "instruction": "Small group with teacher, prerequisite skills, manipulatives",
                    "time": "15-20 min daily"
                },
                "tier_2_targeted": {
                    "label": "🟡 Approaching (Tier 2)",
                    "count": len(groups["approaching"]),
                    "students": [s.to_simple_dict() for s in groups["approaching"]],
                    "instruction": "Guided practice with scaffolds, peer partners",
                    "time": "10-15 min daily"
                },
                "tier_1_core": {
                    "label": "🟢 Mastery (Tier 1)",
                    "count": len(groups["mastery"]),
                    "students": [s.to_simple_dict() for s in groups["mastery"]],
                    "instruction": "Independent practice, can assist peers",
                    "time": "Standard instruction"
                },
                "enrichment": {
                    "label": "🔵 Advanced (Enrichment)",
                    "count": len(groups["advanced"]),
                    "students": [s.to_simple_dict() for s in groups["advanced"]],
                    "instruction": "Extension activities, leadership roles, peer tutoring",
                    "time": "Challenge problems"
                }
            },
            "accommodations_summary": self._get_accommodations_summary(),
            "generated_at": datetime.now().isoformat()
        }

    def _get_accommodations_summary(self) -> Dict[str, List[str]]:
        """Get summary of accommodations in class."""
        summary = {}
        for student in self.students.values():
            for acc in student.accommodations:
                if acc.value not in summary:
                    summary[acc.value] = []
                summary[acc.value].append(student.full_name)
        return summary

    def get_students_with_accommodation(self, acc_type: AccommodationType) -> List[Student]:
        """Get all students with a specific accommodation."""
        return [s for s in self.students.values() if s.has_accommodation(acc_type)]

    def get_roster(self) -> List[Dict[str, Any]]:
        """Get class roster sorted by last name."""
        students = sorted(self.students.values(), key=lambda s: s.last_name)
        return [s.to_dict() for s in students]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classroom_id": self.classroom_id,
            "name": self.name,
            "grade": self.grade,
            "subject": self.subject.value,
            "teacher_name": self.teacher_name,
            "student_count": self.student_count,
            "current_teks": self.current_teks,
            "school_year": self.school_year,
            "created_at": self.created_at
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ASSESSMENT MODEL - Track Assessments and Results
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Assessment:
    """
    An assessment (test, quiz, exit ticket).

    Links to TEKS and automatically groups students after entry.
    """
    assessment_id: str
    name: str
    classroom_id: str
    teks_codes: List[str]
    total_points: float

    # Assessment type
    assessment_type: str = "formative"    # formative, summative, diagnostic

    # Scores (student_id -> points earned)
    scores: Dict[str, float] = field(default_factory=dict)

    # Computed stats
    class_average: float = 0.0
    mastery_rate: float = 0.0

    # Thresholds
    mastery_threshold: float = 80.0

    # Metadata
    date_given: str = field(default_factory=lambda: date.today().isoformat())
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_score(self, student_id: str, points: float):
        """Add a student's score."""
        self.scores[student_id] = points
        self._recalculate_stats()

    def add_scores_batch(self, scores: Dict[str, float]):
        """Add multiple scores at once."""
        self.scores.update(scores)
        self._recalculate_stats()

    def get_percentage(self, student_id: str) -> float:
        """Get a student's percentage score."""
        if student_id not in self.scores:
            return 0.0
        return (self.scores[student_id] / self.total_points) * 100

    def _recalculate_stats(self):
        """Recalculate class statistics."""
        if not self.scores:
            return

        percentages = [(s / self.total_points) * 100 for s in self.scores.values()]
        self.class_average = sum(percentages) / len(percentages)

        mastery_count = sum(1 for p in percentages if p >= self.mastery_threshold)
        self.mastery_rate = (mastery_count / len(percentages)) * 100

    def get_results_grouped(self) -> Dict[str, List[str]]:
        """Get student IDs grouped by mastery level."""
        groups = {
            "needs_reteach": [],
            "approaching": [],
            "mastery": [],
            "advanced": []
        }

        for student_id, points in self.scores.items():
            pct = (points / self.total_points) * 100
            if pct >= 90:
                groups["advanced"].append(student_id)
            elif pct >= 80:
                groups["mastery"].append(student_id)
            elif pct >= 70:
                groups["approaching"].append(student_id)
            else:
                groups["needs_reteach"].append(student_id)

        return groups

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "name": self.name,
            "classroom_id": self.classroom_id,
            "teks_codes": self.teks_codes,
            "total_points": self.total_points,
            "assessment_type": self.assessment_type,
            "students_assessed": len(self.scores),
            "class_average": round(self.class_average, 1),
            "mastery_rate": round(self.mastery_rate, 1),
            "date_given": self.date_given,
            "created_at": self.created_at
        }


# ═══════════════════════════════════════════════════════════════════════════════
# INTERVENTION PLAN - Track Differentiated Interventions
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class InterventionPlan:
    """
    A differentiated intervention plan for a group of students.

    Created automatically when students are grouped after assessment.
    """
    plan_id: str
    classroom_id: str
    teks_codes: List[str]
    target_group: MasteryLevel

    # Students in this intervention
    student_ids: List[str] = field(default_factory=list)

    # Intervention details
    strategy: str = ""
    materials: List[str] = field(default_factory=list)
    duration_minutes: int = 15
    frequency: str = "daily"              # daily, 3x_week, weekly

    # Progress tracking
    start_date: str = field(default_factory=lambda: date.today().isoformat())
    end_date: Optional[str] = None
    status: str = "active"                # active, completed, paused

    # Notes
    notes: List[str] = field(default_factory=list)

    def add_note(self, note: str):
        """Add a progress note."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.notes.append(f"[{timestamp}] {note}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "classroom_id": self.classroom_id,
            "teks_codes": self.teks_codes,
            "target_group": self.target_group.value,
            "student_count": len(self.student_ids),
            "student_ids": self.student_ids,
            "strategy": self.strategy,
            "materials": self.materials,
            "duration_minutes": self.duration_minutes,
            "frequency": self.frequency,
            "status": self.status,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "notes": self.notes
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TEACHER'S AIDE DATABASE - Main Database Class
# ═══════════════════════════════════════════════════════════════════════════════

class TeachersAideDB:
    """
    Teacher's Aide Database - Easy data management for educators.

    Designed to be simple and teacher-friendly:
    - Add students quickly
    - Enter scores easily
    - Get groups automatically
    - Track interventions

    All data can be saved/loaded from JSON for portability.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the database."""
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "data", "teachers_aide")

        # Core data stores
        self.students: Dict[str, Student] = {}
        self.classrooms: Dict[str, Classroom] = {}
        self.assessments: Dict[str, Assessment] = {}
        self.interventions: Dict[str, InterventionPlan] = {}

        # TEKS library reference
        self.teks = get_teks_library()

        # Counters for auto-IDs
        self._student_counter = 0
        self._classroom_counter = 0
        self._assessment_counter = 0
        self._intervention_counter = 0

    # ═══════════════════════════════════════════════════════════════════════════
    # STUDENT OPERATIONS - Simple CRUD
    # ═══════════════════════════════════════════════════════════════════════════

    def add_student(
        self,
        first_name: str,
        last_name: str,
        grade: int,
        accommodations: Optional[List[str]] = None,
        student_id: Optional[str] = None
    ) -> Student:
        """
        Add a new student.

        Example:
            db.add_student("Maria", "Garcia", 5, accommodations=["ell"])
        """
        if student_id is None:
            self._student_counter += 1
            student_id = f"STU{self._student_counter:04d}"

        # Parse accommodations
        acc_list = []
        if accommodations:
            for acc in accommodations:
                try:
                    acc_list.append(AccommodationType(acc.lower()))
                except ValueError:
                    pass  # Skip invalid accommodation types

        student = Student(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            grade=grade,
            accommodations=acc_list
        )

        self.students[student_id] = student
        return student

    def get_student(self, student_id: str) -> Optional[Student]:
        """Get a student by ID."""
        return self.students.get(student_id)

    def find_students(self, name: str) -> List[Student]:
        """Find students by name (partial match)."""
        name_lower = name.lower()
        return [s for s in self.students.values()
                if name_lower in s.full_name.lower()]

    def list_students(self, grade: Optional[int] = None) -> List[Student]:
        """List all students, optionally filtered by grade."""
        students = list(self.students.values())
        if grade is not None:
            students = [s for s in students if s.grade == grade]
        return sorted(students, key=lambda s: s.last_name)

    # ═══════════════════════════════════════════════════════════════════════════
    # CLASSROOM OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def create_classroom(
        self,
        name: str,
        grade: int,
        subject: str,
        teacher_name: str = "",
        classroom_id: Optional[str] = None
    ) -> Classroom:
        """
        Create a new classroom.

        Example:
            db.create_classroom("5th Period Math", 5, "math", "Ms. Johnson")
        """
        if classroom_id is None:
            self._classroom_counter += 1
            classroom_id = f"CLASS{self._classroom_counter:03d}"

        # Parse subject
        try:
            subj = Subject(subject.lower())
        except ValueError:
            subj = Subject.MATH  # Default to math

        classroom = Classroom(
            classroom_id=classroom_id,
            name=name,
            grade=grade,
            subject=subj,
            teacher_name=teacher_name
        )

        self.classrooms[classroom_id] = classroom
        return classroom

    def get_classroom(self, classroom_id: str) -> Optional[Classroom]:
        """Get a classroom by ID."""
        return self.classrooms.get(classroom_id)

    def add_student_to_classroom(self, student_id: str, classroom_id: str) -> str:
        """Add a student to a classroom."""
        student = self.students.get(student_id)
        classroom = self.classrooms.get(classroom_id)

        if not student:
            return f"Student {student_id} not found"
        if not classroom:
            return f"Classroom {classroom_id} not found"

        return classroom.add_student(student)

    def add_students_to_classroom(self, student_ids: List[str], classroom_id: str) -> str:
        """Add multiple students to a classroom."""
        results = []
        for sid in student_ids:
            result = self.add_student_to_classroom(sid, classroom_id)
            results.append(result)
        return f"Added {len(student_ids)} students"

    # ═══════════════════════════════════════════════════════════════════════════
    # ASSESSMENT OPERATIONS - Enter Scores Easily
    # ═══════════════════════════════════════════════════════════════════════════

    def create_assessment(
        self,
        name: str,
        classroom_id: str,
        teks_codes: List[str],
        total_points: float,
        assessment_type: str = "formative"
    ) -> Assessment:
        """
        Create a new assessment.

        Example:
            db.create_assessment(
                "Exit Ticket 5.3A",
                "CLASS001",
                ["5.3A"],
                total_points=3
            )
        """
        self._assessment_counter += 1
        assessment_id = f"ASSESS{self._assessment_counter:04d}"

        assessment = Assessment(
            assessment_id=assessment_id,
            name=name,
            classroom_id=classroom_id,
            teks_codes=teks_codes,
            total_points=total_points,
            assessment_type=assessment_type
        )

        self.assessments[assessment_id] = assessment
        return assessment

    def enter_scores(
        self,
        assessment_id: str,
        scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Enter scores for an assessment.

        Automatically updates student mastery levels and groupings.

        Example:
            db.enter_scores("ASSESS0001", {
                "STU0001": 3,
                "STU0002": 2,
                "STU0003": 1
            })
        """
        assessment = self.assessments.get(assessment_id)
        if not assessment:
            return {"error": f"Assessment {assessment_id} not found"}

        # Add scores to assessment
        assessment.add_scores_batch(scores)

        # Update student records
        for student_id, points in scores.items():
            student = self.students.get(student_id)
            if student:
                percentage = (points / assessment.total_points) * 100

                # Update assessment history
                student.assessment_history[assessment_id] = percentage

                # Update mastery for each TEKS
                for teks_code in assessment.teks_codes:
                    student.update_mastery(teks_code, percentage)

        # Get updated groupings
        classroom = self.classrooms.get(assessment.classroom_id)
        groups = assessment.get_results_grouped()

        return {
            "assessment": assessment.name,
            "students_scored": len(scores),
            "class_average": round(assessment.class_average, 1),
            "mastery_rate": round(assessment.mastery_rate, 1),
            "groups": {
                "needs_reteach": len(groups["needs_reteach"]),
                "approaching": len(groups["approaching"]),
                "mastery": len(groups["mastery"]),
                "advanced": len(groups["advanced"])
            }
        }

    def quick_enter_scores(
        self,
        assessment_id: str,
        scores_list: List[Tuple[str, float]]
    ) -> Dict[str, Any]:
        """
        Quick score entry using list of tuples.

        Example:
            db.quick_enter_scores("ASSESS0001", [
                ("Maria Garcia", 3),
                ("John Smith", 2),
                ("Ana Lopez", 3)
            ])
        """
        # Find students by name and build scores dict
        scores = {}
        not_found = []

        for name, points in scores_list:
            found = self.find_students(name)
            if found:
                scores[found[0].student_id] = points
            else:
                not_found.append(name)

        result = self.enter_scores(assessment_id, scores)
        if not_found:
            result["students_not_found"] = not_found

        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # DIFFERENTIATION - The Core Feature
    # ═══════════════════════════════════════════════════════════════════════════

    def get_groups(self, classroom_id: str) -> Dict[str, Any]:
        """
        Get differentiated groups for a classroom.

        This is the MAIN method teachers will use.
        Returns groups ready for small group instruction.
        """
        classroom = self.classrooms.get(classroom_id)
        if not classroom:
            return {"error": f"Classroom {classroom_id} not found"}

        return classroom.get_differentiation_report()

    def get_reteach_group(self, classroom_id: str) -> List[Student]:
        """Get students who need reteaching."""
        classroom = self.classrooms.get(classroom_id)
        if not classroom:
            return []

        groups = classroom.get_groups()
        return groups["needs_reteach"]

    def create_intervention(
        self,
        classroom_id: str,
        teks_codes: List[str],
        target_group: str,
        strategy: str,
        student_ids: Optional[List[str]] = None
    ) -> InterventionPlan:
        """
        Create an intervention plan for a group.

        If student_ids not provided, auto-populates from current grouping.
        """
        self._intervention_counter += 1
        plan_id = f"INT{self._intervention_counter:04d}"

        # Parse target group
        try:
            group = MasteryLevel(target_group.lower())
        except ValueError:
            group = MasteryLevel.NEEDS_RETEACH

        # Auto-populate students if not provided
        if student_ids is None:
            classroom = self.classrooms.get(classroom_id)
            if classroom:
                groups = classroom.get_groups()
                if group == MasteryLevel.NEEDS_RETEACH:
                    student_ids = [s.student_id for s in groups["needs_reteach"]]
                elif group == MasteryLevel.APPROACHING:
                    student_ids = [s.student_id for s in groups["approaching"]]
                else:
                    student_ids = []

        plan = InterventionPlan(
            plan_id=plan_id,
            classroom_id=classroom_id,
            teks_codes=teks_codes,
            target_group=group,
            student_ids=student_ids or [],
            strategy=strategy
        )

        self.interventions[plan_id] = plan
        return plan

    # ═══════════════════════════════════════════════════════════════════════════
    # TEKS OPERATIONS - Easy Standard Lookup
    # ═══════════════════════════════════════════════════════════════════════════

    def search_teks(self, query: str) -> List[Dict[str, Any]]:
        """Search TEKS standards by keyword."""
        results = self.teks.search(query)
        return [r.to_dict() for r in results]

    def get_teks(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a specific TEKS standard."""
        standard = self.teks.get(code)
        return standard.to_dict() if standard else None

    def get_teks_by_grade(self, grade: int) -> List[Dict[str, Any]]:
        """Get all TEKS for a grade level."""
        standards = self.teks.get_by_grade(grade)
        return [s.to_dict() for s in standards]

    def get_teks_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """Get all TEKS for a subject."""
        try:
            subj = Subject(subject.lower())
            standards = self.teks.get_by_subject(subj)
            return [s.to_dict() for s in standards]
        except ValueError:
            return []

    # ═══════════════════════════════════════════════════════════════════════════
    # PERSISTENCE - Save and Load
    # ═══════════════════════════════════════════════════════════════════════════

    def save(self, filename: Optional[str] = None) -> str:
        """
        Save database to JSON file.

        Example:
            db.save("my_class_data.json")
        """
        if filename is None:
            filename = f"teachers_aide_{date.today().isoformat()}.json"

        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        filepath = os.path.join(self.data_dir, filename)

        # Serialize data
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "counters": {
                "student": self._student_counter,
                "classroom": self._classroom_counter,
                "assessment": self._assessment_counter,
                "intervention": self._intervention_counter
            },
            "students": {sid: self._serialize_student(s) for sid, s in self.students.items()},
            "classrooms": {cid: self._serialize_classroom(c) for cid, c in self.classrooms.items()},
            "assessments": {aid: a.to_dict() for aid, a in self.assessments.items()},
            "interventions": {iid: i.to_dict() for iid, i in self.interventions.items()}
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        return filepath

    def load(self, filename: str) -> str:
        """
        Load database from JSON file.

        Example:
            db.load("my_class_data.json")
        """
        filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            return f"File not found: {filepath}"

        with open(filepath, 'r') as f:
            data = json.load(f)

        # Restore counters
        counters = data.get("counters", {})
        self._student_counter = counters.get("student", 0)
        self._classroom_counter = counters.get("classroom", 0)
        self._assessment_counter = counters.get("assessment", 0)
        self._intervention_counter = counters.get("intervention", 0)

        # Restore students
        self.students = {}
        for sid, sdata in data.get("students", {}).items():
            self.students[sid] = self._deserialize_student(sdata)

        # Restore classrooms
        self.classrooms = {}
        for cid, cdata in data.get("classrooms", {}).items():
            self.classrooms[cid] = self._deserialize_classroom(cdata)

        # Restore assessments
        self.assessments = {}
        for aid, adata in data.get("assessments", {}).items():
            self.assessments[aid] = self._deserialize_assessment(adata)

        # Restore interventions
        self.interventions = {}
        for iid, idata in data.get("interventions", {}).items():
            self.interventions[iid] = self._deserialize_intervention(idata)

        return f"Loaded from {filepath}"

    def _serialize_student(self, student: Student) -> Dict[str, Any]:
        """Serialize student for JSON."""
        return {
            "student_id": student.student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "grade": student.grade,
            "accommodations": [a.value for a in student.accommodations],
            "accommodation_notes": student.accommodation_notes,
            "mastery_by_teks": {k: v.value for k, v in student.mastery_by_teks.items()},
            "assessment_history": student.assessment_history,
            "current_group": student.current_group.value,
            "created_at": student.created_at,
            "updated_at": student.updated_at
        }

    def _deserialize_student(self, data: Dict[str, Any]) -> Student:
        """Deserialize student from JSON."""
        student = Student(
            student_id=data["student_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            grade=data["grade"],
            accommodations=[AccommodationType(a) for a in data.get("accommodations", [])],
            accommodation_notes=data.get("accommodation_notes", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )
        student.mastery_by_teks = {k: MasteryLevel(v) for k, v in data.get("mastery_by_teks", {}).items()}
        student.assessment_history = data.get("assessment_history", {})
        student.current_group = MasteryLevel(data.get("current_group", "not_assessed"))
        return student

    def _serialize_classroom(self, classroom: Classroom) -> Dict[str, Any]:
        """Serialize classroom for JSON."""
        return {
            "classroom_id": classroom.classroom_id,
            "name": classroom.name,
            "grade": classroom.grade,
            "subject": classroom.subject.value,
            "teacher_name": classroom.teacher_name,
            "student_ids": list(classroom.students.keys()),
            "current_teks": classroom.current_teks,
            "school_year": classroom.school_year,
            "created_at": classroom.created_at
        }

    def _deserialize_classroom(self, data: Dict[str, Any]) -> Classroom:
        """Deserialize classroom from JSON."""
        classroom = Classroom(
            classroom_id=data["classroom_id"],
            name=data["name"],
            grade=data["grade"],
            subject=Subject(data["subject"]),
            teacher_name=data.get("teacher_name", ""),
            current_teks=data.get("current_teks", []),
            school_year=data.get("school_year", ""),
            created_at=data.get("created_at", datetime.now().isoformat())
        )

        # Re-link students
        for sid in data.get("student_ids", []):
            if sid in self.students:
                classroom.students[sid] = self.students[sid]

        return classroom

    def _deserialize_assessment(self, data: Dict[str, Any]) -> Assessment:
        """Deserialize assessment from JSON."""
        return Assessment(
            assessment_id=data["assessment_id"],
            name=data["name"],
            classroom_id=data["classroom_id"],
            teks_codes=data["teks_codes"],
            total_points=data["total_points"],
            assessment_type=data.get("assessment_type", "formative"),
            class_average=data.get("class_average", 0.0),
            mastery_rate=data.get("mastery_rate", 0.0),
            date_given=data.get("date_given", date.today().isoformat()),
            created_at=data.get("created_at", datetime.now().isoformat())
        )

    def _deserialize_intervention(self, data: Dict[str, Any]) -> InterventionPlan:
        """Deserialize intervention from JSON."""
        return InterventionPlan(
            plan_id=data["plan_id"],
            classroom_id=data["classroom_id"],
            teks_codes=data["teks_codes"],
            target_group=MasteryLevel(data["target_group"]),
            student_ids=data.get("student_ids", []),
            strategy=data.get("strategy", ""),
            materials=data.get("materials", []),
            duration_minutes=data.get("duration_minutes", 15),
            frequency=data.get("frequency", "daily"),
            start_date=data.get("start_date", date.today().isoformat()),
            end_date=data.get("end_date"),
            status=data.get("status", "active"),
            notes=data.get("notes", [])
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # SUMMARY AND REPORTS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_summary(self) -> Dict[str, Any]:
        """Get database summary."""
        return {
            "total_students": len(self.students),
            "total_classrooms": len(self.classrooms),
            "total_assessments": len(self.assessments),
            "total_interventions": len(self.interventions),
            "teks_available": len(self.teks.all_codes())
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_db_instance: Optional[TeachersAideDB] = None

def get_teachers_aide_db() -> TeachersAideDB:
    """Get or create the global TeachersAideDB instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = TeachersAideDB()
    return _db_instance


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'MasteryLevel',
    'AccommodationType',
    'GradingPeriod',

    # Models
    'Student',
    'Classroom',
    'Assessment',
    'InterventionPlan',

    # Database
    'TeachersAideDB',
    'get_teachers_aide_db',
]
