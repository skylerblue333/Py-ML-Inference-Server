from __future__ import annotations

import math
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelInfo:
    name: str
    version: str
    source: str
    feature_count: int


class LinearModel:
    """Small deterministic adapter used to exercise the serving contract.

    The built-in coefficients are not presented as a trained production model. Operators can
    provide MODEL_WEIGHTS and MODEL_BIAS to load an externally selected linear model.
    """

    def __init__(self, weights: tuple[float, ...], bias: float, info: ModelInfo) -> None:
        if not weights:
            raise ValueError("model must contain at least one weight")
        if not all(math.isfinite(value) for value in (*weights, bias)):
            raise ValueError("model coefficients must be finite")
        if info.feature_count != len(weights):
            raise ValueError("feature_count must match weight count")
        self.weights = weights
        self.bias = bias
        self.info = info

    def predict(self, features: list[float]) -> float:
        if len(features) != len(self.weights):
            raise ValueError(f"expected {len(self.weights)} features")
        if not all(math.isfinite(value) for value in features):
            raise ValueError("features must be finite")
        return sum(weight * feature for weight, feature in zip(self.weights, features)) + self.bias


def _parse_weights(raw: str) -> tuple[float, ...]:
    values = tuple(float(part.strip()) for part in raw.split(",") if part.strip())
    if not values:
        raise ValueError("MODEL_WEIGHTS must contain comma-separated numbers")
    if len(values) > 128:
        raise ValueError("MODEL_WEIGHTS supports at most 128 features")
    return values


def load_model() -> LinearModel:
    raw_weights = os.getenv("MODEL_WEIGHTS")
    if raw_weights:
        weights = _parse_weights(raw_weights)
        bias = float(os.getenv("MODEL_BIAS", "0"))
        info = ModelInfo(
            name=os.getenv("MODEL_NAME", "configured-linear"),
            version=os.getenv("MODEL_VERSION", "unversioned"),
            source="environment",
            feature_count=len(weights),
        )
        return LinearModel(weights, bias, info)

    weights = (0.5, -0.25, 0.1)
    return LinearModel(
        weights,
        0.0,
        ModelInfo(
            name="demo-linear",
            version="demo-v1",
            source="built-in-demo",
            feature_count=len(weights),
        ),
    )
