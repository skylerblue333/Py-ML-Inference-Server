"""FastAPI inference adapter for plugging in an existing model implementation."""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SKYCOIN4444 ML Inference")

class PredictionRequest(BaseModel):
    features: list[float]

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/predict")
def predict(request: PredictionRequest):
    # Replace this adapter with the selected production model; no fake prediction is returned.
    return {"status": "model_not_configured", "feature_count": len(request.features)}
