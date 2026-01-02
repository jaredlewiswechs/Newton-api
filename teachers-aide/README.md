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
- Filter by grade (3-8) and subject
- Keyword search
- Learning path navigation
- Copy codes for lesson planning

---

## Quick Start

### Using the Web App

1. **Visit the Application**
   - Local: http://localhost:8000/teachers-aide/
   - Production: https://newton-teachers-aide.pages.dev/

2. **Generate a Lesson Plan**
   - Select grade level (3-8)
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

The Teacher's Aide is powered by the Newton Education API. All endpoints are available at `/education/*`.

### Endpoints

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

### Example: Analyze Assessment

```bash
curl -X POST http://localhost:8000/education/assess \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_name": "Unit 3 Exit Ticket",
    "teks_codes": ["5.3A"],
    "total_points": 100,
    "mastery_threshold": 80,
    "students": [
      {"id": "1", "name": "Maria", "score": 85},
      {"id": "2", "name": "James", "score": 72},
      {"id": "3", "name": "Sofia", "score": 95}
    ]
  }'
```

### Example: Generate PLC Report

```bash
curl -X POST http://localhost:8000/education/plc \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "5th Grade Math Team",
    "teks_codes": ["5.3A", "5.3B"],
    "assessment_data": [
      {"name": "Maria", "score": 85},
      {"name": "James", "score": 72},
      {"name": "Sofia", "score": 95}
    ]
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

## TEKS Standards

The system includes machine-readable TEKS standards for:

### Mathematics (Grades 3-8)
- Number and Operations
- Algebraic Reasoning
- Geometry and Measurement
- Data Analysis

### Reading/ELA (Grades 3-8)
- Comprehension of Literary Text
- Comprehension of Informational Text
- Author's Purpose and Craft

### Science (Grades 5, 8)
- Matter and Energy
- Force, Motion, and Energy

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
└── education.py    # tinyTalk education module
    ├── TEKSLibrary           # TEKS standards database
    ├── NESLessonPlan         # Blueprint with laws
    ├── AssessmentAnalyzer    # Blueprint with laws
    ├── LessonPlanGenerator   # Verified generator
    ├── SlideDeckGenerator    # Verified generator
    ├── PLCReportGenerator    # Verified generator
    └── EducationCartridge    # Newton cartridge

newton_supercomputer.py
└── /education/*    # Education API endpoints
```

---

## Best Practices

### For Teachers
1. **Be specific with TEKS codes** - Enter exact codes for better alignment
2. **Use the topic field** - A specific topic improves lesson focus
3. **Include accommodations** - List students needing ELL, 504, SPED, or GT support
4. **Analyze exit tickets immediately** - Use the Assessment Analyzer right after class
5. **Generate PLC reports weekly** - Keep your team informed with regular data updates

### For Administrators
1. **Review mastery rates** - Track progress toward campus goals
2. **Monitor reteach groups** - Identify students needing intervention
3. **Use PLC reports for walkthrough planning** - See what instruction looks like
4. **Compare TEKS coverage** - Ensure all standards are addressed

---

## Support

- **Issues**: https://github.com/anthropics/Newton-api/issues
- **Documentation**: https://newton-docs.pages.dev/education

---

## Credits

**Newton Teacher's Aide** is part of the Newton Supercomputer project.

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas

*"The cloud is weather. We're building shelter."*
