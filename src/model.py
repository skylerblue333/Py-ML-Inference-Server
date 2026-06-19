import numpy as np
from typing import List, Dict
import time

class MockResNet:
    def __init__(self):
        self.classes = ['cat', 'dog', 'car', 'truck']
        self.loaded = False
        
    def load(self):
        time.sleep(0.5) # Simulate IO
        self.loaded = True
        
    def predict(self, image_tensor: np.ndarray) -> Dict[str, float]:
        if not self.loaded:
            raise RuntimeError("Model not loaded")
        # Simulate inference
        logits = np.random.randn(len(self.classes))
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)
        return {c: float(p) for c, p in zip(self.classes, probs)}
