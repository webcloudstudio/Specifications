# ARCHITECTURE: Marina

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | Two-plane hybrid: a local control plane and a private AWS broadcast plane, with all cloud access behind the `marina` library and all infrastructure in layered Terraform. |

**Description:** Module layout, the `marina` library boundary, the AWS broadcast plane, and the Terraform
infrastructure layout for Phase 1 and Phase 2.

---

## Two Planes

### Plane A — Local Control Plane (out of scope for this build, summarised)
Runs on the developer's machine: scanner, process engine, log ingestor, scheduler. It is **outbound
only** — it opens no public listener. It publishes catalog/metadata and reports heartbeats/events to the
cloud, and drains the SQS queue when alive. Built later, reusing GAME modules.

### Plane B — Cloud Broadcast Plane (this specification)
Serverless, scales to zero, private:
- **DynamoDB** — single-table hierarchical catalog/state (see `DATABASE.md`).
- **API Gateway (HTTP API) + Lambda** — IAM/SigV4-authorised read and ingest endpoints. No anonymous
  access, no public IP on the caller side.
- **SQS** — durable store-and-forward queue (Phase 2).
- **S3** — VoiceForward audio blobs and the per-user company share (Phase 2).

```
[ local agent ] --SigV4--> [ API Gateway ] --> [ Lambda ] --> [ DynamoDB ]
[ producers   ] ------------------------------> [ SQS ] <--drain-- [ local agent ]
[ members     ] --marina lib / AWS CLI (SigV4)--> [ API Gateway ] (read 24x7)
[ blobs/share ] -------------------------------> [ S3 ]
```

## The `marina` Library Boundary

All cloud access — from the local agent, from Lambdas' callers, and from any conformed project — goes
through the `marina` Python library (`stack/marina-library.md`). Project code never imports boto3.
Resource groups: `marina.catalog`, `marina.report`, `marina.queue`, `marina.share`. The library resolves
identity (AWS profile), the org, and the API endpoint from the environment and signs every call with
SigV4. It is the swap layer that keeps Marina from being welded to AWS.

## Lambda Modules (Plane B compute)

| Module | Route | Purpose | Phase |
|--------|-------|---------|-------|
| `catalog_publish` | `POST /catalog` | Upsert a project's metadata + capabilities into DynamoDB | 1 |
| `catalog_read` | `GET /catalog`, `GET /catalog/{project}` | Read the org tree or one project subtree | 1 |
| `capabilities_read` | `GET /capabilities` | List capabilities, filterable by tag | 1 |
| `report_ingest` | `POST /heartbeat`, `POST /events` | Append heartbeat/event items | 1 |
| `health_read` | `GET /health/{project}` | Aggregate last-known health for one project | 1 |
| `queue_submit` | `POST /queue/{queue}` | Enqueue a message to SQS | 2 |
| `share_index` | `GET /share`, `POST /share` | List/register company-share objects (bytes go direct to S3) | 2 |

Each Lambda is thin (validate → one storage op → respond) per `stack/aws-lambda.md`. Authorisation
(repo→capability gate) is enforced in a shared module described in `FEATURE-ACCESS-CONTROL.md`.

**Local-plane queue handlers (Plane A).** Some capabilities run only on the box (they touch the
filesystem) and are dispatched by draining the SQS queue, not by a cloud Lambda. The first is
`prototyper` — exposing Prototyper's conformance scripts (`ProjectValidate/Update/Initialize/Document`)
through the AsyncQueue, allow-listed and reported as events (see `FEATURE-PROJECT-OPS.md`). The cloud
carries only the job request and the result report; no project code runs in the cloud.

## Directory Layout

The build produces two artifacts: the Lambda/source tree and the Terraform tree. (The `marina` library
lives in its own repository — see `stack/marina-library.md`.)

```
Marina/
  src/                         # Lambda handlers (one package per function)
    catalog_publish/handler.py
    catalog_read/handler.py
    capabilities_read/handler.py
    report_ingest/handler.py
    health_read/handler.py
    queue_submit/handler.py     # Phase 2
    share_index/handler.py      # Phase 2
    common/                     # shared: auth gate, response helper, dynamo key builders
  infra/                        # Terraform (see Terraform Layout below)
    backend/                    # one-shot bootstrap: S3 state bucket + DynamoDB lock table
    foundation/                 # rare: DynamoDB catalog table, IAM/OIDC roles, SQS, S3 buckets
    services/                   # rerun-anytime: Lambdas, API Gateway, integrations
    modules/                    # reusable: lambda_fn, http_route
    bin/                        # tf-init.sh / tf-plan.sh / tf-apply.sh <layer>
    env.tfvars                  # project/org/region/phase variables (no secrets)
  bin/                          # test scripts (one per feature) + common.sh/common.py
    test_catalog_publish.sh
    test_catalog_read.sh
    test_report_ingest.sh
    test_access_control.sh
    test_asyncqueue.sh          # Phase 2
    test_voice_capture.sh       # Phase 2
    test_s3_share.sh            # Phase 2
  tests/                        # pytest suites for Lambda handlers (moto-backed)
  .github/workflows/            # ci.yml, deploy.yml (OIDC; see stack/github-actions.md)
  pyproject.toml                # uv-managed; ruff configured
  uv.lock
  METADATA.md  AGENTS.md  CLAUDE.md  .env.sample  docs/
```

## Terraform Layout (folded from the infra plan)

Infrastructure is layered so routine code deploys (`services/`) never risk the foundation
(`foundation/`), and the remote backend bootstrap (`backend/`) is run once. State lives in **S3**;
locking uses **DynamoDB** — state is never local beyond `backend/`. See `stack/terraform.md` for the
backend, naming (`marina-{project}-{resource}`), tag set, and bash wrappers.

| Layer | Cadence | Contents |
|-------|---------|----------|
| `backend/` | one-shot | S3 state bucket, DynamoDB lock table (local state, applied once) |
| `foundation/` | rare, gated apply | DynamoDB catalog table, IAM/OIDC roles, SQS queues, S3 buckets |
| `services/` | every deploy | Lambdas, API Gateway HTTP API, routes, integrations |

## Observability Without Screens

Marina ships no UI in Phase 1/2. Every feature is verified through (a) a callable `bin/test_*.sh`
script that exercises it via the `marina` library or AWS CLI, and (b) the CloudWatch log group / metric
the feature emits to. Each `FEATURE-*.md` names its test script and its CloudWatch log group.

## Configuration

Local clients read `MARINA_ORG`, `MARINA_ENDPOINT`, `MARINA_PROJECT`, and the AWS profile from the
environment (see `stack/marina-library.md`). Lambdas read `TABLE_NAME`, `QUEUE_URL`, `SHARE_BUCKET`, and
`LOG_LEVEL` from Terraform-set environment variables (no `.env` in Lambda).

## Authorisation Gate Caching

The shared gate caches each ACL grant **in-process per warm Lambda with a 5-minute TTL** (keyed by
`org, project, principal`), falling back to a DynamoDB `GetItem` on miss. At PAY_PER_REQUEST a grant
read costs a fraction of a cent, so the cache is purely a latency optimisation (a cold `GetItem` adds
2–8 ms). The 5-minute window bounds staleness: a revoked grant stops working within five minutes, which
is acceptable because onboarding is admin-controlled and revocations are deliberate and infrequent.

## Startup Gate

Marina (local Flask app) refuses to start if the working directory is not a git repository with an upstream remote configured. On startup:
1. Verify `git rev-parse --git-dir` exits 0 — abort with a clear error if not.
2. Read `git remote get-url origin` — abort if no remote is set.
3. Extract GitHub username from the remote URL and store in `settings.github_username` if not already set.

This ensures the local control plane is always associated with a real repository, and the GitHub username seed is always available without user intervention.

## Health Aggregation

`health_read` computes aggregate health **in the Lambda at read time** from the latest heartbeat and
recent event items — it does **not** store a precomputed aggregate. Read-time compute keeps the write
path (heartbeat/event ingest) a single point write, and lets the aggregation rule change without a data
migration. The read cost is trivial (a small `Query` per project), so the flexibility is free.

## Open Questions

- None open.
