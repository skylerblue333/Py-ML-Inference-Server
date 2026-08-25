import math
import os
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Sky Inference", version="0.1.0")

MAX_FEATURES = 256
MODE = os.getenv("SKY_INFERENCE_MODE", "disabled").strip().lower()
if MODE not in {"disabled", "demo"}:
    raise RuntimeError("SKY_INFERENCE_MODE must be 'disabled' or 'demo'")


class InferenceRequest(BaseModel):
    features: list[float] = Field(min_length=1, max_length=MAX_FEATURES)

    @field_validator("features")
    @classmethod
    def finite_features(cls, values: list[float]) -> list[float]:
        if not all(math.isfinite(value) for value in values):
            raise ValueError("features must contain only finite numbers")
        return values


class PredictionResponse(BaseModel):
    mode: Literal["demo"]
    scores: list[float]
    feature_count: int


def _demo_scores(features: list[float]) -> list[float]:
    """Return deterministic normalized scores for contract testing only."""
    maximum = max(features)
    weights = [math.exp(value - maximum) for value in features]
    total = sum(weights)
    return [weight / total for weight in weights]


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "sky-inference"}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    if MODE != "demo":
        raise HTTPException(status_code=503, detail="no inference model is configured")
    return {"status": "ready", "mode": MODE}


@app.get("/metadata")
def metadata() -> dict[str, object]:
    return {
        "service": "sky-inference",
        "mode": MODE,
        "max_features": MAX_FEATURES,
        "trained_model_loaded": False,
    }


@app.post("/v1/predict", response_model=PredictionResponse)
def predict(request: InferenceRequest) -> PredictionResponse:
    if MODE != "demo":
        raise HTTPException(status_code=503, detail="no inference model is configured")
    return PredictionResponse(
        mode="demo",
        scores=_demo_scores(request.features),
        feature_count=len(request.features),
    )
