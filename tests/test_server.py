from fastapi.testclient import TestClient
from src.server import app
import io

client = TestClient(app)

def test_health():
    with TestClient(app) as c: # triggers startup
        res = c.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
        assert res.json()["model_loaded"] == True

def test_predict_invalid_file():
    with TestClient(app) as c:
        res = c.post("/predict", files={"file": ("test.txt", b"hello", "text/plain")})
        assert res.status_code == 400

def test_predict_success():
    with TestClient(app) as c:
        res = c.post("/predict", files={"file": ("test.jpg", b"fakeimg", "image/jpeg")})
        assert res.status_code == 200
        data = res.json()
        assert "predictions" in data
        assert "cat" in data["predictions"]
        assert data["latency_ms"] >= 0
