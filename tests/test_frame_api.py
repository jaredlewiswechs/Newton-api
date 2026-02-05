from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.frame_api import router


app = FastAPI()
app.include_router(router, prefix="/api")
client = TestClient(app)


def test_frames_basic():
    resp = client.post("/api/frames", json={"prompt": "Discuss WW1 causes."})
    assert resp.status_code == 200
    data = resp.json()
    assert "handles" in data


def test_frames_use_llm_flag():
    # When LLM unavailable, endpoint should return 503; if available, it may return 200
    resp = client.post("/api/frames?use_llm=true", json={"prompt": "Short prompt"})
    assert resp.status_code in (200, 503)
