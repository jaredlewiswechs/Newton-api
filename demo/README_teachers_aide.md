# Teacher's Aide Service (demo)

Run a compact API that exposes TEKS, semantic search, the Newton logic engine,
and TI-Calc helpers for demo and integration.

Quickstart

1. Ensure the project's virtualenv is active and dependencies installed (FastAPI/uvicorn).
2. Run the service:

```bash
python demo/teachers_aide_service.py
# or with uvicorn directly:
uvicorn demo.teachers_aide_service:app --reload --port 8088
```

Endpoints

- `GET /health` - health check
- `GET /teks` - list TEKS or filter by `?q=` keyword
- `GET /teks/{code}` - get a TEKS standard
- `GET /search?q=...` - semantic search over TEKS + adanpedia examples
- `POST /logic/evaluate` - evaluate Newton logic expression (JSON body `{ "expr": {...} }`)
- `POST /ti/bounded_distance` - compute bounded distance (JSON `{value, lo, hi}`)
- `POST /ti/citation_score` - compute citation score (JSON `{required, found, min_required}`)
- `POST /ti/combine` - combine scores (JSON map of component scores)
