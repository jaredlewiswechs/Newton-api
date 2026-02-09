Title: realTinyTalk — TinyTalk IDE + Lessons Pack

Short description:
An offline, educator-friendly TinyTalk IDE bundle with 40+ curated TinyTalk lessons, teacher guide, and one-click local demo. Perfect for classroom labs, workshops, and self-study.

Full description:
realTinyTalk is a lightweight web-based TinyTalk IDE (Monaco) bundled with a curated lessons library, developer examples, and guided teacher material. Run locally with a single command and iteratively edit, autosave, and version student projects. Includes a three-way merge UI and server-side versioning for classroom collaboration.

What's included:
- The realTinyTalk web IDE and demo server (run locally)
- ~40 curated TinyTalk lessons and example apps ([selling/lessons](selling/lessons) folder)
- Teacher guide with lesson plan & classroom activities
- Start scripts for Windows PowerShell and Unix shells
- Sample projects (notes, search.app, cyberdog demo, opendoc demo, algorithms, edge cases)
- Export/import and ZIP-ready bundle

Suggested pricing:
- Individual / educator: $9 — IDE + lessons
- Classroom site license: $49 — includes teacher guide + support notes
- Institution: contact for volume licensing

How to run (local):
PowerShell:
```powershell
# create and activate venv, install deps
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# run the demo server (from repo root)
.\.venv\Scripts\python.exe realTinyTalk/web/server.py
# open http://127.0.0.1:5555/
```

Verify the bundle (quick checks):
```powershell
# confirm the ZIP exists
ls -l selling.zip

# extract to check contents
powershell -Command "Expand-Archive -Path selling.zip -DestinationPath selling_extracted -Force"
Get-ChildItem -Path selling_extracted -Recurse | Select-Object -First 50
```

Screenshots/GIF suggestions:
- Hero screenshot: editor with `mandelbrot.tt` open and run output visible
- Short GIF (6–10s): open lesson, make a tiny edit, autosave, open version history, perform a 3-way merge and accept changes
- Teacher guide snapshot showing lesson plan and learning objectives

Short promo blurb (for Gumroad listing):
"Run TinyTalk locally — a lightweight web IDE with 40+ lessons, teacher guides, and collaboration-ready versioning. Great for classrooms and workshops."

Support & license:
- Personal/educator use allowed under included non-commercial license (see LICENSE in repo)
- For commercial or institutional licensing contact: jared@ada.example (replace with real contact)
