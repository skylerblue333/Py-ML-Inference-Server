from fastapi.testclient import TestClient
from src.main import app

def test_inference_engine():
    with TestClient(app) as client:
        res = client.post("/api/v2/predict", json={"tensor_data": [1.0, 2.0, 3.0]})
        assert res.status_code == 200
        data = res.json()
        assert "predictions" in data
        assert "latency_ms" in data
        assert len(data["predictions"]) == 3

def test_empty_tensor():
    with TestClient(app) as client:
        res = client.post("/api/v2/predict", json={"tensor_data": []})
        assert res.status_code == 400
