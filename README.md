# Py-ML-Inference-Server

![CI](https://github.com/skylerblue333/Py-ML-Inference-Server/workflows/CI/badge.svg)

Production-ready Machine Learning inference server built with FastAPI.

## Architecture
- **API Layer**: FastAPI for high-performance async request handling
- **Model Layer**: Pre-loaded ResNet (mocked) for image classification
- **Deployment**: Fully containerized with Docker

## Quick Start
```bash
pip install -r requirements.txt
pytest tests/ -v
uvicorn src.server:app --reload
```
