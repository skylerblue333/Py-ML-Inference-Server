# Contributing to Sky Inference

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pip-audit
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

## Scope and style

- Keep `src/main.py` as the canonical HTTP contract unless a change intentionally restructures the application.
- Add tests for validation and model-availability behavior.
- Do not introduce fake trained-model, GPU, accuracy, registry, or production-deployment claims.
- Do not load untrusted pickle/joblib model artifacts.
- Keep demo behavior explicitly labeled as contract testing, not ML accuracy.

## Pull requests

1. Create a focused branch.
2. Make the smallest coherent change.
3. Run the verification commands above.
4. Document new model/security boundaries.
5. Open a pull request with a truthful maturity status.

## License

See `LICENSE`.
