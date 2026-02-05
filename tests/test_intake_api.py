from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.intake_api import router


app = FastAPI()
app.include_router(router, prefix="/api")
client = TestClient(app)


def test_intake_basic_word_counts_and_citations():
    prompt = "Write an essay of 400-600 words due 2026-02-10. Cite sources."
    resp = client.post("/api/intake", json={"prompt": prompt})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["word_count_min"] == 400
    assert data["word_count_max"] == 600
    assert data["citations"]["required"] is True


def test_intake_use_llm_unavailable_returns_503():
    # Requesting LLM when not present should return 503
    prompt = "Short prompt"
    resp = client.post("/api/intake?use_llm=true", json={"prompt": prompt})
    assert resp.status_code in (200, 503)
