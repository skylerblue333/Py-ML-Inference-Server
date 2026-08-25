# Sky Inference

Sky Inference is a small FastAPI service for validating an inference-serving boundary before connecting a real model runtime. It exposes a bounded numeric prediction contract, health/readiness checks, request IDs, lightweight runtime metrics, tests, dependency auditing, and a non-root container.

**Status: engineering beta.** The repository does not claim GPU acceleration, TensorRT, ONNX Runtime, image classification accuracy, model training, autoscaling, authentication, or production deployment.

## Model behavior

By default the service loads a deliberately simple deterministic linear demo model with three coefficients. The demo model exists to make API behavior executable and testable; it is not described as a trained production model.

Operators can provide their own linear coefficients through environment configuration:

```bash
export MODEL_WEIGHTS="0.7,-0.2,0.15"
export MODEL_BIAS="0.05"
export MODEL_NAME="price-risk-linear"
export MODEL_VERSION="2026-08-24"
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

`MODEL_WEIGHTS` accepts 1–128 comma-separated finite numbers. The request feature count must match the configured weight count.

## API

`GET /healthz` is a liveness endpoint. `GET /readyz` reports the loaded adapter name/version/source and expected feature count. `GET /metrics` reports process-local request and error counters. `POST /v1/predict` accepts:

```json
{"features":[1.0,2.0,3.0]}
```

The built-in demo returns the deterministic score `0.3` for that example and identifies its source as `built-in-demo` so downstream callers cannot mistake it for a trained model.

## Local verification

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
ruff check src tests
pytest -q
pip-audit -r requirements.txt
```

Build and run the container:

```bash
docker build -t sky-inference .
docker run --rm -p 8000:8000 sky-inference
curl http://127.0.0.1:8000/readyz
```

The image runs as the unprivileged `app` user. CI performs linting, tests, dependency audit, container build, non-root verification, and a live container health check.

## SKYCOIN4444 integration

This service can sit behind Sky Gateway as a stable inference adapter. Ecosystem callers should depend only on the documented HTTP contract rather than importing this repository's implementation. A future real model runtime should replace the adapter behind the same versioned interface and add its own model provenance, evaluation, resource, and deployment evidence.

## Current limits

There is no authentication or authorization, TLS termination, distributed metrics backend, persistent request history, model artifact signature verification, rollout/canary control, batching, GPU scheduling, or production observability. Do not expose this beta directly to untrusted public traffic without those controls and an appropriate deployment review.
