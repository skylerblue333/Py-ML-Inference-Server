# Py-ML-Inference-Server

![CI](https://github.com/skylerblue333/Py-ML-Inference-Server/workflows/CI/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103-00a393.svg)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=flat&logo=redis&logoColor=white)

A production-grade inference server designed for sub-millisecond neural network forward passes, supporting TensorRT/ONNX backends.

## System Architecture


```mermaid
graph TD
    Client-->|REST/gRPC|API[API Gateway]
    API-->|OpenTelemetry|Tracer[Jaeger/Zipkin]
    API-->|Pub/Sub|Redis[(Redis Event Bus)]
    Redis-->Worker1[AI Worker Node]
    Redis-->Worker2[Data Worker Node]
    Worker1-->LLM[OpenAI/LLM API]
    Worker2-->DB[(PostgreSQL)]
```


## Elite Features
- **Zero-Copy Arrays**: Numpy tensor memory mapping.
- **Sub-millisecond Latency**: Optimized FastAPI routing.
- **Telemetry**: Built-in latency tracking and model versioning.

## Quick Start
```bash
docker-compose up -d redis
pip install -r requirements.txt
pytest tests/ -v
uvicorn src.main:app --reload
```
