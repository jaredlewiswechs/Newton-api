# Neo (Standalone)

Neo is a standalone news scraper + summary agent.

## Run locally

```bash
cd neo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8789
```

Then open:

- http://localhost:8789/

## API

- `POST /api/analyze`
  - body: `{ "url": "https://..." }` or `{ "text": "..." }`
- `GET /health`

## Notes

- This folder is copy-paste portable into a brand-new account/repo.
- Frontend assets use relative paths, so they do not depend on Newton route mounts.
- If hosted under Newton `/neo`, frontend auto-switches to `/neo/analyze`.
