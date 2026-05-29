# Feature: Marina Library

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | The `marina` Python package — the single cloud boundary used by the local agent, the Lambdas' callers, and every conformed project. |
| Depends On  | — |
| Provides    | — |

**Description:** The `marina` client library: resource-grouped, intent-named methods over DynamoDB, API
Gateway, SQS, and S3, with SigV4 identity resolved from the environment. The foundation every other
feature depends on. Full rules in `stack/marina-library.md`.

## Trigger

Imported by any caller that touches the cloud: the local control-plane agent (publish, drain, report),
conformed project `bin/` scripts (heartbeat, queue submit, share), and the feature test scripts. Never
triggered by an HTTP route — it is a library, not a service.

## Sequence

1. `Marina()` resolves configuration from the environment: `MARINA_ORG`, `MARINA_ENDPOINT`,
   `MARINA_PROJECT` (default = directory name), and AWS credentials via the standard boto3 chain
   (`AWS_PROFILE`/role).
2. It constructs resource clients lazily: `catalog`, `report`, `queue`, `share`.
3. Each method builds the request, signs it with SigV4 for `execute-api`, and calls API Gateway — or, for
   the local agent's direct-drain path, talks to SQS/S3 through boto3 held inside the library.
4. Network calls retry with exponential backoff + jitter. `report.*` swallows errors (best-effort);
   `catalog.*`, `queue.*`, `share.*` raise typed exceptions (`MarinaAuthError`, `MarinaNotFound`,
   `MarinaTransportError`).

Public surface (Phase 1 + 2):

```
mar.catalog.publish(project_meta, capabilities) / read(project=None) / read_capabilities(tags=None)
mar.report.heartbeat(state, message="") / event(severity, message)         # best-effort
mar.queue.submit(queue, service, tool, payload, priority="normal") / drain(queue=None)   # Phase 2
mar.share.put(local_path, key=None) / get(key, dest) / list(prefix=None)                 # Phase 2
```

## Reads

- Environment: `MARINA_ORG`, `MARINA_ENDPOINT`, `MARINA_PROJECT`, AWS credentials.
- For reads it issues `GET` requests to API Gateway, which read DynamoDB.

## Writes

- None of its own state. It is the conduit for other features' writes (DynamoDB items, SQS messages,
  S3 objects) via their endpoints.

## Test

- **Script:** `bin/test_marina_lib.sh` → runs the library's own pytest suite against `moto`
  (mocked DynamoDB/SQS/S3) plus a live smoke test that calls `mar.catalog.read()` against the deployed
  IAM-authorised endpoint using the caller's AWS profile.
- **Pass criteria:** `import boto3` appears nowhere outside the `marina` package (grep gate); all
  resource methods present with correct signatures; `report.*` never raises on transport failure;
  `catalog.read()` returns a list/dict from the live endpoint.
- **CloudWatch:** the live smoke read appears in the API Gateway access log group
  `/aws/apigw/marina-{project}` (route `GET /catalog`, principal = caller ARN).

## Open Questions

- Should the library expose a thin `mar.raw` escape hatch for one-off operations not yet wrapped, or is
  any un-wrapped need a signal to add a proper method? Leaning: no escape hatch — keep the boundary pure.
- Spike 6: confirm `uv add git+https://.../marina-lib.git@vX.Y.Z` pins cleanly and flows into consumer
  `uv.lock`; settle the library repo name and release tagging flow.
