# TEKS Principles of Information Technology Lesson Plans

This set of lesson plans uses **realTinyTalk** (the full language in `realTinyTalk/`) to teach core Principles of Information Technology concepts while aligning to **TEKS 130.272** strands (digital citizenship, data representation, programming, networking, cybersecurity, and project management). Each lesson includes classroom flow, assessment, and a runnable realTinyTalk program that can be transpiled to **JavaScript** or **Python**.

> **Note:** TEKS codes are provided in the format commonly used for Principles of IT (130.272). Adjust to your district’s official wording if needed.

## How to Use the realTinyTalk Files

Run any lesson’s `.tt` file:

```bash
python -m realTinyTalk run docs/lesson_plans/teks-principles-of-it/01_digital_citizenship.tt
```

Compile to JavaScript:

```bash
python -m realTinyTalk.cli build -t js docs/lesson_plans/teks-principles-of-it/01_digital_citizenship.tt -o 01_digital_citizenship.js
```

Compile to Python (module API):

```bash
python - <<'PY'
from pathlib import Path
from realTinyTalk.backends.python.emitter import PythonEmitter
from realTinyTalk.parser import parse

source = Path("docs/lesson_plans/teks-principles-of-it/01_digital_citizenship.tt").read_text()
ast = parse(source)
print(PythonEmitter().emit(ast))
PY
```

## Lesson Lineup

| Lesson | Focus | TEKS Alignment (130.272) | Code Sample |
| --- | --- | --- | --- |
| 01 | Digital citizenship & ethics | (c)(1)(A)(B), (c)(2)(A) | `01_digital_citizenship.tt` |
| 02 | Data representation | (c)(4)(A)(B) | `02_data_representation.tt` |
| 03 | Algorithms & programming | (c)(5)(A)(B)(C) | `03_algorithms.tt` |
| 04 | Cybersecurity fundamentals | (c)(6)(A)(B)(C) | `04_cybersecurity.tt` |
| 05 | Networks & the web | (c)(7)(A)(B) | `05_networking.tt` |
| 06 | Project planning & collaboration | (c)(8)(A)(B)(C) | `06_project_planner.tt` |

## Materials (All Lessons)

- Computers with Python installed.
- `realTinyTalk/` in the repo.
- Optional: a browser to run JavaScript output.

## Assessment Formats

- Quick checks (5-minute exit tickets).
- Code walkthroughs using the `.tt` files.
- Mini-projects that extend the lesson program.

## Extensions

- Convert each lesson’s `.tt` file into JavaScript and run it in a browser console.
- Have students adapt the Python output for unit testing or documentation.
