# Security Policy

## Supported status

Sky Inference is an **engineering beta**. The repository verifies Python compilation, linting, tests, dependency auditing, container build, non-root execution, and a liveness smoke check in CI. Those checks do not establish production security or deployment readiness.

## Current boundaries

The service validates feature-vector cardinality and rejects non-finite numeric input. By default it fails closed because no trained model is configured.

It does not currently implement authentication, authorization, tenant isolation, request signing, rate limiting, model artifact signature verification, encrypted model storage, sandboxed model execution, GPU isolation, drift detection, or production infrastructure controls.

Do not load untrusted serialized Python model artifacts. A future real model adapter should use a reviewed artifact format and explicit integrity verification rather than arbitrary pickle/joblib deserialization from untrusted sources.

## Reporting

Report suspected vulnerabilities privately through GitHub security reporting when available. Do not include credentials, private model artifacts, customer data, or sensitive inference payloads in public issues.
