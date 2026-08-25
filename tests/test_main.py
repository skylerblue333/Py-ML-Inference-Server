from fastapi.testclient import TestClient

import src.main as service


def test_health_is_independent_of_model_mode():
    with TestClient(service.app) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["service"] == "sky-inference"


def test_disabled_mode_fails_closed(monkeypatch):
    monkeypatch.setattr(service, "MODE", "disabled")
    with TestClient(service.app) as client:
        assert client.get("/readyz").status_code == 503
        response = client.post("/v1/predict", json={"features": [1.0, 2.0]})
    assert response.status_code == 503


def test_demo_mode_is_deterministic_and_normalized(monkeypatch):
    monkeypatch.setattr(service, "MODE", "demo")
    with TestClient(service.app) as client:
        response = client.post("/v1/predict", json={"features": [1.0, 2.0, 3.0]})
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "demo"
    assert payload["feature_count"] == 3
    assert abs(sum(payload["scores"]) - 1.0) < 1e-12


def test_input_bounds_and_finite_validation(monkeypatch):
    monkeypatch.setattr(service, "MODE", "demo")
    with TestClient(service.app) as client:
        assert client.post("/v1/predict", json={"features": []}).status_code == 422
        too_many = [1.0] * (service.MAX_FEATURES + 1)
        assert client.post("/v1/predict", json={"features": too_many}).status_code == 422
        assert client.post("/v1/predict", content='{"features":[1e999]}', headers={"content-type": "application/json"}).status_code == 422
