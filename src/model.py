from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class InferenceModel(Protocol):
    loaded: bool
    def load(self) -> None: ...
    def predict(self, image_tensor: np.ndarray) -> dict[str, float]: ...


@dataclass
class MockResNet:
    """Deterministic development model; replace with a real model adapter in production."""

    classes: tuple[str, ...] = ("cat", "dog", "car", "truck")
    loaded: bool = False

    def load(self) -> None:
        self.loaded = True

    def predict(self, image_tensor: np.ndarray) -> dict[str, float]:
        if not self.loaded:
            raise RuntimeError("Model not loaded")
        if image_tensor.ndim != 4 or image_tensor.shape[1:] != (3, 224, 224):
            raise ValueError("expected tensor shape (batch, 3, 224, 224)")
        logits = np.asarray([0.4, 0.3, 0.2, 0.1], dtype=np.float64)
        probabilities = np.exp(logits - np.max(logits))
        probabilities /= probabilities.sum()
        return {label: float(probability) for label, probability in zip(self.classes, probabilities)}
