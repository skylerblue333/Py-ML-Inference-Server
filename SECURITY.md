# Security

Sky Inference is an engineering-beta model-serving boundary, not a public production service.

Report suspected vulnerabilities privately to the repository owner rather than publishing exploit details in an issue.

## Current controls

- bounded request feature arrays
- finite-number validation
- request IDs and basic structured request logging
- `X-Content-Type-Options: nosniff` and `Referrer-Policy: no-referrer`
- dependency auditing in CI
- non-root container execution
- no embedded credentials or model secrets

## Not implemented

Authentication, authorization, TLS termination, distributed rate limiting, signed model artifacts, tenant isolation, durable audit logs, production monitoring, and deployment hardening are outside the current repository scope. Put the service behind an authenticated gateway and trusted network boundary before handling sensitive workloads.
