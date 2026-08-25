# Changelog

## 0.1.0 — Engineering beta

- replace conflicting Flask, mock image, and duplicate adapter entrypoints with one canonical FastAPI service
- fail closed when no inference mode is configured
- add explicit deterministic `demo` mode for contract testing only
- bound feature vectors to 1–256 finite numeric values
- add health, readiness, metadata, and versioned prediction endpoints
- add deterministic tests, Ruff, dependency audit, Docker build, non-root and container smoke CI gates
- document SKYCOIN4444 integration and security/product boundaries

This release does not include or claim a trained production model.
