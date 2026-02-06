# realTinyTalk — Educator / Developer Pack

This bundle provides a lightweight, shippable package you can sell on Gumroad: a deployable realTinyTalk editor bundle, teacher guide, and a couple of curated TinyTalk lessons to demo in-class or locally.

Contents
- `start.sh` — simple runner for Unix-like systems
- `start.ps1` — runner for Windows PowerShell
- `TeacherGuide.md` — lesson plan + learning objectives
- `lessons/` — curated TinyTalk lessons (Mandelbrot, Neighborhood builder)
- `assets/` — screenshots / listing suggestions

How to run (local development)
1. Create a Python virtualenv and install dependencies (project root contains `requirements.txt`):

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Windows
.venv/bin/pip install -r requirements.txt         # Mac/Linux
```

2. Run the realTinyTalk web server from repo root:

```bash
.venv\Scripts\python.exe realTinyTalk/web/server.py   # Windows
.venv/bin/python realTinyTalk/web/server.py            # Mac/Linux
```

3. Open the editor in your browser at: `http://127.0.0.1:5555/`

Packaging for Gumroad
- Zip the `selling/` folder, include `lessons/` and `TeacherGuide.md`
- Add 1–2 GIFs or screenshots (see `assets/` for suggestions)
- Provide a short README with a 1-paragraph description and install steps (already included)

Next steps I can do for you:
- Curate 20–40 lessons into `selling/lessons/` (copy and polish)
- Auto-build a bundled zip and upload assets
- Produce 2 short demo GIFs (instructions for recording) and `TeacherGuide.pdf`

Tell me which next step you want me to take.