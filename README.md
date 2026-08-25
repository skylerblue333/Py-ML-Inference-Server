# Sky Inference — Python Engineering Beta

Sky Inference is a small FastAPI service that provides a stable, bounded HTTP contract for numeric inference requests. It intentionally does **not** pretend that a trained model is bundled with this repository.

## Status

**Engineering beta.** The default mode is `disabled`: liveness works, but readiness and prediction fail closed with HTTP 503 because no trained model is configured. Setting `SKY_INFERENCE_MODE=demo` enables a deterministic softmax-style scoring function for API integration and contract testing only.

The demo mode is **not a trained machine-learning model**, does not represent model accuracy, and must not be described as GPU/TensorRT/ONNX serving or production inference.

## API

- `GET /healthz` — process liveness.
- `GET /readyz` — returns ready only when an explicit inference mode is available.
- `GET /metadata` — reports mode, feature bound, and whether a trained model is loaded.
- `POST /v1/predict` — accepts `{ "features": [1.0, 2.0] }`; 1–256 finite numbers only.

Example demo run:

```bash
SKY_INFERENCE_MODE=demo uvicorn src.main:app --host 127.0.0.1 --port 8000
curl -s http://127.0.0.1:8000/readyz
curl -s -X POST http://127.0.0.1:8000/v1/predict \
  -H 'content-type: application/json' \
  -d '{"features":[1.0,2.0,3.0]}'
```

## Verification

```bash
python -m compileall -q src tests
ruff check src tests
pytest -q tests/test_main.py
pip-audit -r requirements.txt
docker build -t sky-inference .
docker run --rm --entrypoint=id sky-inference -u
```

CI additionally starts the container and checks `/healthz`. The container runs as UID `10001`.

## Architecture

`src/main.py` is the single canonical application entrypoint. Request validation rejects empty, oversized, and non-finite feature vectors. The service keeps model availability explicit instead of silently substituting a fake model. A future real model adapter should implement a reviewed model-loading boundary and should keep the HTTP contract stable where practical.

## SKYCOIN4444 integration

SKYCOIN4444 services can call this component through `/v1/predict` after readiness succeeds. Consumers should treat HTTP 503 as “model unavailable” rather than fabricating a fallback prediction. This keeps the standalone repository reusable without copying it into the flagship application.

## Security and operational boundaries

This repository does not currently provide authentication, tenant isolation, rate limiting, request signing, model artifact verification, encrypted model storage, GPU isolation, autoscaling, distributed serving, a model registry, drift monitoring, or production deployment evidence. Put appropriate network/auth controls in front of the service before exposing it outside a trusted development environment.

## License

See `LICENSE`.
