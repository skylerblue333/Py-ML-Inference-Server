import pytest
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health_and_readiness() -> None:
    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "service": "sky-inference"}
    assert health.headers["x-content-type-options"] == "nosniff"

    ready = client.get("/readyz")
    assert ready.status_code == 200
    assert ready.json() == {
        "status": "ready",
        "model": "demo-linear",
        "model_version": "demo-v1",
        "model_source": "built-in-demo",
        "feature_count": 3,
    }


def test_predict_uses_declared_demo_model() -> None:
    response = client.post("/v1/predict", json={"features": [1.0, 2.0, 3.0]})
    assert response.status_code == 200
    payload = response.json()
    assert payload["prediction"] == pytest.approx(0.3)
    assert payload["model"] == "demo-linear"
    assert payload["model_source"] == "built-in-demo"
    assert payload["feature_count"] == 3


def test_predict_rejects_wrong_feature_count() -> None:
    response = client.post("/v1/predict", json={"features": [1.0, 2.0]})
    assert response.status_code == 400
    assert response.json()["detail"] == "expected 3 features"


def test_predict_rejects_empty_features() -> None:
    response = client.post("/v1/predict", json={"features": []})
    assert response.status_code == 422


def test_request_id_is_preserved() -> None:
    response = client.get("/healthz", headers={"x-request-id": "test-request"})
    assert response.headers["x-request-id"] == "test-request"


def test_metrics_report_requests_and_errors() -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "sky-inference"
    assert payload["requests_total"] >= 1
    assert payload["errors_total"] >= 1
