from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import numpy as np
import io
from src.model import MockResNet

app = FastAPI(title="ML Inference API", version="2.0.0")
model = MockResNet()

@app.on_event("startup")
def load_model():
    model.load()

class PredictResponse(BaseModel):
    predictions: dict
    latency_ms: float

@app.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Must be an image")
        
    content = await file.read()
    # In real app: img = Image.open(io.BytesIO(content))
    # tensor = preprocess(img)
    tensor = np.random.randn(1, 3, 224, 224)
    
    import time
    start = time.time()
    preds = model.predict(tensor)
    latency = (time.time() - start) * 1000
    
    return PredictResponse(predictions=preds, latency_ms=latency)

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model.loaded}
