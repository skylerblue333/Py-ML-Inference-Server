from __future__ import annotations

import logging
import os
import threading
import time
import uuid
from math import isfinite

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator

from src.model import LinearModel, load_model

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format="%(message)s")
logger = logging.getLogger("sky-inference")

app = FastAPI(title="Sky Inference", version="0.1.0")
model: LinearModel = load_model()
_metrics_lock = threading.Lock()
_request_count = 0
_error_count = 0


class PredictionRequest(BaseModel):
    features: list[float] = Field(min_length=1, max_length=128)

    @field_validator("features")
    @classmethod
    def finite_features(cls, values: list[float]) -> list[float]:
        if not all(isfinite(value) for value in values):
            raise ValueError("features must be finite")
        return values


class PredictionResponse(BaseModel):
    prediction: float
    model: str
    model_version: str
    model_source: str
    feature_count: int


@app.middleware("http")
async def request_context(request: Request, call_next):
    global _request_count, _error_count
    request_id = request.headers.get("x-request-id", "").strip()[:128] or str(uuid.uuid4())
    started = time.perf_counter()
    with _metrics_lock:
        _request_count += 1
    try:
        response: Response = await call_next(request)
    except Exception:
        with _metrics_lock:
            _error_count += 1
        logger.exception("request_failed request_id=%s path=%s", request_id, request.url.path)
        raise
    response.headers["x-request-id"] = request_id
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["referrer-policy"] = "no-referrer"
    logger.info(
        "request_complete request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started) * 1000,
    )
    return response


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "sky-inference"}


@app.get("/readyz")
def readyz() -> dict[str, object]:
    return {
        "status": "ready",
        "model": model.info.name,
        "model_version": model.info.version,
        "model_source": model.info.source,
        "feature_count": model.info.feature_count,
    }


@app.get("/metrics")
def metrics() -> dict[str, int | str]:
    with _metrics_lock:
        requests = _request_count
        errors = _error_count
    return {"service": "sky-inference", "requests_total": requests, "errors_total": errors}


@app.post("/v1/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    try:
        prediction = model.predict(payload.features)
    except ValueError as exc:
        with _metrics_lock:
            global _error_count
            _error_count += 1
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PredictionResponse(
        prediction=prediction,
        model=model.info.name,
        model_version=model.info.version,
        model_source=model.info.source,
        feature_count=model.info.feature_count,
    )
