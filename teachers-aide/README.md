# Newton Teacher's Aide

## The Ultimate Teaching Assistant for HISD's New Education System

Newton Teacher's Aide is a Newton Supercomputer-powered web application that transforms how teachers plan, assess, and collaborate. Built with tinyTalk constraint-based verification, it treats TEKS standards and NES requirements as machine-readable objects for guaranteed compliance.

**"1 == 1. The constraint IS the instruction."**

---

## Features

### 📚 Lesson Planner
Generate complete NES-compliant lesson plans in seconds:
- **5 NES Phases**: Opening (5 min), Instruction (15 min), Guided (15 min), Independent (10 min), Closing (5 min)
- **TEKS Alignment**: Verified alignment to Texas Essential Knowledge and Skills
- **Differentiation**: Built-in strategies for below, on, and above level students
- **Accommodations**: Support for ELL, 504, SPED, and GT students
- **Exit Tickets**: Auto-generated assessment questions

### 📊 Slide Deck Generator
Convert lesson plans into presentation-ready slides:
- Title and objective slides
- Vocabulary introduction
- Phase-specific content
- Example and practice problems
- Export to multiple formats

### ✅ Assessment Analyzer
Grade formative assessments and get instant student groupings:
- **Robust Statistics**: Uses Newton's adversarial-resistant MAD algorithm
- **Mastery Classification**: Automatic grouping into reteach, approaching, and mastery
- **Recommendations**: Differentiation strategies for each group
- **Data Visualization**: Clear statistics and student lists

### 📈 PLC Report Generator
Replace traditional PLC meetings with data-driven reports:
- **Insights**: Automated analysis of student performance
- **Action Items**: Prioritized tasks with timelines
- **Student Groupings**: Ready-to-use differentiation groups
- **Discussion Points**: Guided PLC conversation starters
- **Next Steps**: Immediate, short-term, and long-term planning

### 📋 TEKS Browser
Search and explore Texas Essential Knowledge and Skills:
- Filter by grade (K-8) and subject
- Keyword search
- Learning path navigation
- Copy codes for lesson planning
- **188 TEKS standards included** (K-8 across all subjects)

---

## NEW: Teacher's Aide Database

The Teacher's Aide now includes a complete classroom management system designed to make teachers' lives easier.

### Key Features

| Feature | Description |
|---------|-------------|
| **Student Management** | Track students with accommodations (ELL, SPED, 504, GT, Dyslexia, RTI) |
| **Classroom Management** | Create classes, manage rosters, track TEKS focus |
| **Assessment Tracking** | Create assessments, enter scores by name or ID |
| **Auto-Differentiation** | Students automatically grouped into 4 tiers based on performance |
| **Intervention Plans** | Track interventions with progress notes |
| **Data Persistence** | Save/load to JSON for backup and portability |

### The 4 Differentiation Tiers

| Tier | Level | Range | Instruction |
|------|-------|-------|-------------|
| **Tier 3** | Needs Reteach | <70% | Small group with teacher, manipulatives, prerequisite skills |
| **Tier 2** | Approaching | 70-79% | Guided practice with scaffolds, peer partners |
| **Tier 1** | Mastery | 80-89% | Standard instruction, independent practice |
| **Enrichment** | Advanced | 90%+ | Extension activities, leadership roles, peer tutoring |

### Workflow

```
1. Add Students → 2. Create Classroom → 3. Add to Roster
       ↓
4. Create Assessment → 5. Enter Scores → 6. GET GROUPS!
       ↓
7. View Differentiation Report → 8. Plan Interventions
```

---

## Quick Start

### Using the Web App

1. **Visit the Application**
   - Local: http://localhost:8000/teachers-aide/
   - Production: https://newton-teachers-aide.pages.dev/

2. **Generate a Lesson Plan**
   - Select grade level (K-8)
   - Choose subject (Math, Reading, Science, Social Studies)
   - Enter TEKS codes (e.g., 5.3A, 5.3B)
   - Add topic and accommodations (optional)
   - Click "Generate Lesson Plan"

3. **Analyze Assessments**
   - Enter student scores (one per line: Name, Score)
   - Set mastery threshold (default 80%)
   - Click "Analyze Assessment"

4. **Generate PLC Reports**
   - Enter team name and TEKS focus
   - Add student assessment data
   - Click "Generate PLC Report"

---

## API Reference

### Education Endpoints (`/education/*`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/education/lesson` | POST | Generate NES-compliant lesson plan |
| `/education/slides` | POST | Generate slide deck from lesson plan |
| `/education/assess` | POST | Analyze assessment data |
| `/education/plc` | POST | Generate PLC report |
| `/education/teks` | GET | Browse TEKS standards |
| `/education/teks/{code}` | GET | Get specific TEKS standard |
| `/education/teks/search` | POST | Search TEKS by keyword |
| `/education/info` | GET | Get education endpoint info |

### Teacher's Aide Database Endpoints (`/teachers/*`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/teachers/students` | POST | Add a new student |
| `/teachers/students/batch` | POST | Add multiple students at once |
| `/teachers/students` | GET | List/search students |
| `/teachers/students/{id}` | GET | Get student details |
| `/teachers/classrooms` | POST | Create a new classroom |
| `/teachers/classrooms` | GET | List all classrooms |
| `/teachers/classrooms/{id}` | GET | Get classroom with roster |
| `/teachers/classrooms/{id}/students` | POST | Add students to classroom |
| `/teachers/classrooms/{id}/groups` | GET | **Get differentiated groups (KEY FEATURE!)** |
| `/teachers/classrooms/{id}/reteach` | GET | Get reteach group students |
| `/teachers/assessments` | POST | Create a new assessment |
| `/teachers/assessments/{id}/scores` | POST | Enter scores by student ID |
| `/teachers/assessments/{id}/quick-scores` | POST | Enter scores by student name |
| `/teachers/interventions` | POST | Create intervention plan |
| `/teachers/teks` | GET | Browse 188 TEKS standards (K-8) |
| `/teachers/db/save` | POST | Save database to JSON file |
| `/teachers/db/load` | POST | Load database from JSON file |
| `/teachers/info` | GET | Get Teacher's Aide API docs |

### Example: Add Students and Get Groups

```bash
# 1. Add students
curl -X POST http://localhost:8000/teachers/students \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Maria", "last_name": "Garcia", "grade": 5, "accommodations": ["ell"]}'

# 2. Create classroom
curl -X POST http://localhost:8000/teachers/classrooms \
  -H "Content-Type: application/json" \
  -d '{"name": "5th Period Math", "grade": 5, "subject": "mathematics", "teacher_name": "Ms. Johnson"}'

# 3. Add student to classroom
curl -X POST http://localhost:8000/teachers/classrooms/CLASS001/students \
  -H "Content-Type: application/json" \
  -d '{"student_ids": ["STU0001"]}'

# 4. Create assessment and enter scores
curl -X POST http://localhost:8000/teachers/assessments \
  -H "Content-Type: application/json" \
  -d '{"name": "Exit Ticket", "classroom_id": "CLASS001", "teks_codes": ["5.3A"], "total_points": 3}'

# 5. Enter scores by name (THE EASY WAY!)
curl -X POST http://localhost:8000/teachers/assessments/ASSESS0001/quick-scores \
  -H "Content-Type: application/json" \
  -d '{"scores": [["Maria Garcia", 3], ["John Smith", 2]]}'

# 6. GET DIFFERENTIATED GROUPS!
curl http://localhost:8000/teachers/classrooms/CLASS001/groups
```

### Example: Generate Lesson Plan

```bash
curl -X POST http://localhost:8000/education/lesson \
  -H "Content-Type: application/json" \
  -d '{
    "grade": 5,
    "subject": "mathematics",
    "teks_codes": ["5.3A", "5.3B"],
    "topic": "Adding fractions with unlike denominators",
    "student_needs": {
      "ell": ["Maria", "Carlos"],
      "gt": ["Sofia"]
    }
  }'
```

---

## Deployment

### Cloudflare Pages (Recommended)

```bash
# Deploy the frontend
npx wrangler pages deploy teachers-aide

# Or use the Cloudflare dashboard
# 1. Connect your GitHub repository
# 2. Set build directory: teachers-aide
# 3. Deploy
```

### Docker

```bash
# Build and run the full Newton stack
docker-compose up -d

# Access the Teacher's Aide at http://localhost:8000/teachers-aide/
```

### Manual

```bash
# Start the Newton API
cd Newton-api
python -m uvicorn newton_supercomputer:app --host 0.0.0.0 --port 8000

# Serve the Teacher's Aide frontend
# (files are in teachers-aide/)
```

---

## Understanding NES Phases

The New Education System (NES) structures lessons into 5 phases totaling 50 minutes:

| Phase | Duration | Purpose |
|-------|----------|---------|
| **Opening** | 5 min | Hook students, share objective, students restate goal |
| **Direct Instruction** | 15 min | Teacher models 2-3 examples using think-aloud |
| **Guided Practice** | 15 min | Collaborative practice in pairs/groups with teacher support |
| **Independent Practice** | 10 min | Solo practice (formative assessment data) |
| **Closing** | 5 min | Exit ticket, summarize learning, preview tomorrow |

---

## TEKS Standards (188 Standards Included)

The system includes machine-readable TEKS standards for:

### Mathematics (Grades K-8)
- Number and Operations
- Algebraic Reasoning
- Geometry and Measurement
- Data Analysis

### Reading/ELA (Grades 3-8)
- Comprehension of Literary Text
- Comprehension of Informational Text
- Author's Purpose and Craft

### Science (Grades 3-8)
- Matter and Energy
- Force, Motion, and Energy

### Social Studies (Grades 3-5)
- History
- Geography
- Government

---

## Architecture

```
teachers-aide/
├── index.html      # Main application HTML
├── styles.css      # Newton-themed styles
├── app.js          # Frontend application logic
├── wrangler.toml   # Cloudflare Pages config
├── _headers        # HTTP security headers
├── _redirects      # SPA routing
└── README.md       # This file

tinytalk_py/
├── education.py        # tinyTalk education module
│   ├── TEKSLibrary           # TEKS standards database
│   ├── NESLessonPlan         # Blueprint with laws
│   ├── AssessmentAnalyzer    # Blueprint with laws
│   ├── LessonPlanGenerator   # Verified generator
│   ├── SlideDeckGenerator    # Verified generator
│   ├── PLCReportGenerator    # Verified generator
│   └── EducationCartridge    # Newton cartridge
│
├── teachers_aide_db.py  # Teacher's Aide Database (NEW)
│   ├── Student               # Student with accommodations
│   ├── Classroom             # Classroom with auto-grouping
│   ├── Assessment            # Assessment with score tracking
│   ├── InterventionPlan      # Intervention tracking
│   └── TeachersAideDB        # Main database class
│
└── teks_database.py     # Extended TEKS (NEW)
    └── ExtendedTEKSLibrary   # 188 K-8 standards

newton_supercomputer.py
├── /education/*    # Education API endpoints
└── /teachers/*     # Teacher's Aide Database API (NEW)
```

---

## Best Practices

### For Teachers
1. **Be specific with TEKS codes** - Enter exact codes for better alignment
2. **Use the topic field** - A specific topic improves lesson focus
3. **Include accommodations** - List students needing ELL, 504, SPED, or GT support
4. **Analyze exit tickets immediately** - Use the Assessment Analyzer right after class
5. **Generate PLC reports weekly** - Keep your team informed with regular data updates
6. **Enter scores by name** - Use `/quick-scores` for fast entry without IDs
7. **Check groups daily** - Use `/groups` endpoint to see updated differentiation tiers

### For Administrators
1. **Review mastery rates** - Track progress toward campus goals
2. **Monitor reteach groups** - Identify students needing intervention
3. **Use PLC reports for walkthrough planning** - See what instruction looks like
4. **Compare TEKS coverage** - Ensure all standards are addressed
5. **Export data regularly** - Use `/teachers/db/save` for backup

---

## tinyTalk Education Laws

The education module is built with tinyTalk constraint laws:

```python
class NESLessonPlan(Blueprint):
    @law
    def duration_law(self):
        """Total lesson duration must be 50 minutes."""
        when(self.total_duration != 50, finfr)

    @law
    def teks_alignment_law(self):
        """Lesson must align to at least one TEKS standard."""
        when(len(self.teks_codes) == 0, finfr)

    @law
    def phase_completeness_law(self):
        """Lesson must include all 5 NES phases."""
        when(phase_types != required, finfr)
```

---

## Support

- **Issues**: https://github.com/jaredlewiswechs/Newton-api/issues
- **Documentation**: https://newton-docs.pages.dev/education

---

## Credits

**Newton Teacher's Aide** is part of the Newton Supercomputer project.

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas

*"Less paperwork, more teaching."*
