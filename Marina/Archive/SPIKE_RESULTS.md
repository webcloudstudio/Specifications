# SPIKE_RESULTS: Marina

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | Investigation findings for all six pre-build spikes listed in IDEAS.md. Each entry is a closed question: decision, rationale, and the exact pattern to encode. |

---

## Spike 1 — API Gateway IAM/SigV4 Across Heterogeneous Home Networks

**Question:** Can cross-account AWS Org principals invoke an IAM-authorised HTTP API from arbitrary home networks (no fixed IP, no VPN) with no public anonymous path?

**Decision: Yes — no network constraint is needed. Authentication is credential-based, not network-based. Use HTTP API v2 with a per-member invoke role as the Org perimeter (the REST-v1 resource-policy option below was considered and rejected — see Final Decision).**

### Finding

API Gateway HTTP API endpoints are publicly reachable HTTPS URLs by design. "No public anonymous path" means the `AWS_IAM` authoriser rejects unsigned requests at the API layer — it does not mean the endpoint itself is network-private. A caller on a home broadband connection signs the request with SigV4 using their AWS credentials; the network origin is irrelevant. The API Gateway resource policy restricts which *principals* may call, not which IP ranges.

The `marina` library's SigV4 signing step uses the standard `botocore` `AWSRequestsAuth` or `requests-aws4auth` approach — the caller's `AWS_PROFILE` credential chain signs the `execute-api` scope. This works from any outbound HTTPS-capable network.

### Pattern to Encode

**Resource policy on the HTTP API (Terraform `aws_api_gateway_rest_api_policy` equivalent for HTTP APIs — applied via `aws_apigatewayv2_api` + `aws_apigatewayv2_policy`):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowOrgPrincipals",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:{region}:{account}:{api-id}/*/*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalOrgID": "{org-id}"
        }
      }
    }
  ]
}
```

> **Final Decision (overrides the resource-policy block above): HTTP API v2 + per-member invoke role.**
> HTTP API v2 does not support resource policies, but Marina does not need one. The `AWS_IAM` authoriser
> plus a `marina-{project}-invoke` role (granting `execute-api:Invoke` on the route ARNs) that only Org
> member accounts can assume fully enforces "only Org principals." REST API v1 was rejected — its only
> advantage here is the resource policy, which the invoke-role model makes unnecessary, and it is more
> expensive and higher-latency. The `aws:PrincipalOrgID` resource-policy JSON above is retained only to
> show the equivalent org-boundary intent; it is not what is deployed.

**Invoke role per member account:**

```hcl
resource "aws_iam_role" "marina_invoke" {
  name = "marina-invoke-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { AWS = "arn:aws:iam::${var.member_account_id}:root" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "marina_invoke" {
  role = aws_iam_role.marina_invoke.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "execute-api:Invoke"
      Resource = "arn:aws:execute-api:${var.region}:${var.org_account_id}:${aws_apigatewayv2_api.marina.id}/*/*"
    }]
  })
}
```

**In `marina` library — SigV4 signing:**

```python
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
import requests

session = boto3.Session(profile_name=os.getenv("AWS_PROFILE"))
creds = session.get_credentials().get_frozen_credentials()

req = AWSRequest(method="GET", url=endpoint, data=body)
SigV4Auth(creds, "execute-api", region).add_auth(req)
response = requests.request(req.method, req.url, headers=dict(req.headers), data=body)
```

**ARCHITECTURE.md open question resolved:** No IP allow-list or VPC endpoint required. `aws:PrincipalOrgID` is the sole perimeter.

---

## Spike 2 — Repo-access → Capability-access Binding

**Question:** How does onboarding verify repo access, and does the gate cache the ACL per warm Lambda?

**Decision: GitHub API token check at onboard-time; gate caches ACL with a 5-minute in-process TTL.**

### Finding — Onboarding Verification

At `POST /onboard`, the caller supplies their GitHub personal access token (PAT) or fine-grained token as a request body field (never stored). The onboarding Lambda calls the GitHub REST API to enumerate accessible repos:

```
GET https://api.github.com/user/repos?visibility=all&affiliation=owner,collaborator,organization_member
Authorization: Bearer {token}
```

For each repo that maps to a Marina project (matched on `repo` field in the project item), write the ACL grant with `access` derived from the collaborator's permission level:

- `admin` / `maintain` / `write` → `readwrite`
- `triage` / `read` → `readonly`

The GitHub token is **not persisted** — it is used once and discarded. The ACL item records the `repo` slug and permission at grant time. Re-onboarding or a nightly re-sync job re-derives grants; the gate does not call GitHub at request time.

### Finding — Gate Caching

Direct DynamoDB read (GetItem) per protected request costs ~$0.00000025 per read at PAY_PER_REQUEST, negligible at Marina's scale. However, the latency concern is real: a cold GetItem adds 2–8 ms per request.

**Recommendation: cache the ACL result in-process per warm Lambda, 5-minute TTL.**

```python
from functools import lru_cache
from time import time

_acl_cache: dict[tuple, tuple[dict, float]] = {}
_ACL_TTL = 300  # 5 minutes

def get_grant(dynamo, table, org, project, principal):
    key = (org, project, principal)
    if key in _acl_cache:
        grant, ts = _acl_cache[key]
        if time() - ts < _ACL_TTL:
            return grant
    resp = dynamo.get_item(
        TableName=table,
        Key={"PK": {"S": f"ORG#{org}"}, "SK": {"S": f"PROJECT#{project}#ACL#{principal}"}}
    )
    grant = resp.get("Item")
    _acl_cache[key] = (grant, time())
    return grant
```

Staleness window: if a grant is revoked, the gate sees it within 5 minutes. Acceptable — onboarding is admin-controlled, not self-serve, so revocations are deliberate and low-frequency.

**FEATURE-ACCESS-CONTROL.md open questions resolved:**
- Repo→grant derivation: GitHub API token check at onboard-time only; gate reads ACL table.
- Caching: yes, 5-minute in-process TTL.
- Re-sync: nightly scheduled Lambda re-derives all grants (cheap; keeps grants current as repo access changes).
- `POST /onboard` is Org-admin-only — trust policy on the onboarding Lambda allows only the admin principal ARN.

---

## Spike 3 — Terraform Remote Backend Bootstrap

**Question:** What is the clean sequence for bootstrapping the S3 state bucket + DynamoDB lock table, then migrating `foundation/` and `services/` to remote state?

**Decision: `backend/` stays on local state permanently. `foundation/` and `services/` are initialised directly against the S3 backend — no migration step.**

### Finding

The chicken-and-egg is resolved by keeping `backend/` on local state intentionally:

```
infra/backend/     — local backend (no backend block, or explicit local)
infra/foundation/  — s3 backend referencing resources created by backend/
infra/services/    — s3 backend referencing same bucket, different key
```

### Bootstrap Sequence

```bash
# Step 1 — create the state bucket and lock table (local state, applied once)
terraform -chdir=infra/backend init
terraform -chdir=infra/backend apply -var-file=../env.tfvars
# → outputs: state_bucket, lock_table_name

# Step 2 — foundation: init directly against s3 backend (no prior local state to migrate)
terraform -chdir=infra/foundation init \
  -backend-config="bucket=$(terraform -chdir=infra/backend output -raw state_bucket)" \
  -backend-config="key=marina/foundation/terraform.tfstate" \
  -backend-config="dynamodb_table=$(terraform -chdir=infra/backend output -raw lock_table_name)" \
  -backend-config="region=${AWS_REGION}"
terraform -chdir=infra/foundation apply -var-file=../env.tfvars

# Step 3 — services: same pattern, different state key
terraform -chdir=infra/services init \
  -backend-config="bucket=$(terraform -chdir=infra/backend output -raw state_bucket)" \
  -backend-config="key=marina/services/terraform.tfstate" \
  ...
terraform -chdir=infra/services apply -var-file=../env.tfvars
```

### `infra/bin/tf-init.sh` wrapper

```bash
#!/bin/bash
# Usage: tf-init.sh <layer>   (backend | foundation | services)
LAYER=$1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ "$LAYER" == "backend" ]]; then
  terraform -chdir="$ROOT/backend" init
else
  BUCKET=$(terraform -chdir="$ROOT/backend" output -raw state_bucket 2>/dev/null)
  LOCK=$(terraform -chdir="$ROOT/backend" output -raw lock_table_name 2>/dev/null)
  REGION=$(grep region "$ROOT/env.tfvars" | awk -F'"' '{print $2}')
  terraform -chdir="$ROOT/$LAYER" init \
    -backend-config="bucket=$BUCKET" \
    -backend-config="key=marina/$LAYER/terraform.tfstate" \
    -backend-config="dynamodb_table=$LOCK" \
    -backend-config="region=$REGION"
fi
```

### `backend/main.tf` skeleton

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  # No backend block — state is local and intentional
}

resource "aws_s3_bucket" "state" {
  bucket = "marina-${var.project}-tfstate"
  lifecycle { prevent_destroy = true }
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_dynamodb_table" "lock" {
  name         = "marina-${var.project}-tflock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute { name = "LockID"; type = "S" }
}

output "state_bucket"     { value = aws_s3_bucket.state.bucket }
output "lock_table_name"  { value = aws_dynamodb_table.lock.name }
```

**No `terraform state mv` or `terraform init -migrate-state` step is required.** `foundation/` and `services/` are always initialised against S3 from their first `init`.

---

## Spike 4 — DynamoDB Single-Table Schema Validation

**Question:** Do all 12 access patterns in DATABASE.md resolve to GetItem or Query with `begins_with`? Zero Scans confirmed?

**Decision: All 12 patterns are valid. Zero Scans. Two edge cases noted — both resolved by client-side filter.**

### Pattern-by-pattern validation

| # | Pattern | Operation | Key condition | Valid? | Notes |
|---|---------|-----------|---------------|--------|-------|
| 1 | Upsert project | PutItem | `PK=ORG#o, SK=PROJECT#p` | ✓ | Point write |
| 2 | Upsert capability | PutItem | `PK=ORG#o, SK=PROJECT#p#CAP#c` | ✓ | Point write |
| 3 | Read project + all children | Query | `PK=ORG#o AND begins_with(SK,"PROJECT#p")` | ✓ | Returns project, caps, HBs, events, ACLs — all children |
| 4 | List all projects in org | Query | `PK=ORG#o AND begins_with(SK,"PROJECT#")` | ✓ ⚠ | Over-reads; client-side filter for `type=project` |
| 5 | Read one capability | GetItem | `PK=ORG#o, SK=PROJECT#p#CAP#c` | ✓ | Exact point read |
| 6 | List capabilities (tag filter) | Query | `PK=ORG#o AND begins_with(SK,"PROJECT#p#CAP#")` | ✓ | Per-project scope; tag filter client-side |
| 7 | Write heartbeat | PutItem | `PK=ORG#o, SK=PROJECT#p#HB#prog` | ✓ | Overwrites latest state |
| 8 | Append event | PutItem | `PK=ORG#o, SK=PROJECT#p#EVT#ulid` | ✓ | ULID is time-ordered |
| 9 | Latest heartbeats | Query | `begins_with(SK,"PROJECT#p#HB#")` | ✓ | Small result set |
| 10 | Recent events newest-first | Query | `begins_with(SK,"PROJECT#p#EVT#"), ScanIndexForward=False, Limit=N` | ✓ | ULID lexsort = time sort |
| 11 | Read one ACL grant | GetItem | `PK=ORG#o, SK=PROJECT#p#ACL#principal` | ✓ | Point read for gate |
| 12 | Write ACL grant | PutItem | `PK=ORG#o, SK=PROJECT#p#ACL#principal` | ✓ | Idempotent upsert |

### Edge case — Pattern 4 over-read

`begins_with(SK, "PROJECT#")` returns every item in the org (project rows, caps, heartbeats, events, ACLs). For a small org (tens of projects, hundreds of items) this is fine and cheap. At scale, add a `FilterExpression: #t = :project` server-side — not a Scan, just a Query + filter. No schema change needed.

### Edge case — Pattern 6 org-wide capability list

The spec notes `GET /capabilities` lists across all projects. With the current schema, org-wide capability list requires `begins_with(SK, "PROJECT#")` + client-side filter for `type=capability`. At Phase 1/2 scale (small org) this is fine. If this becomes a hot path, add a GSI: `type` (partition) + `SK` (sort). Defer until needed — no GSI in Phase 1/2.

### `begins_with` prefix hierarchy — confirmed correct

```
PROJECT#market                            ← project item (SK exact)
PROJECT#market#ACL#arn:aws:iam::111:u/j   ← ACL item
PROJECT#market#CAP#download_prices        ← capability item
PROJECT#market#EVT#01JXXXULID             ← event item
PROJECT#market#HB#daily                   ← heartbeat item
```

`begins_with(SK, "PROJECT#market")` matches all five rows; `begins_with(SK, "PROJECT#market#CAP#")` matches only capabilities. Hierarchy is clean — no collisions.

### Idempotency condition

The spec's write guard `attribute_not_exists(PK) OR updated_at <= :now` has a correctness issue: `attribute_not_exists(PK)` will always be false for existing items (PK always exists if the item exists). Correct condition:

```python
ConditionExpression="attribute_not_exists(SK) OR updated_at <= :now"
ExpressionAttributeValues={":now": {"S": now_iso}}
```

Use `SK` (the unique key within partition) as the existence check.

### DATABASE.md open questions resolved

- **Event retention:** add a `ttl` attribute (Unix epoch, `updated_at + 30 days`) to all event items. Enable DynamoDB TTL on the `ttl` attribute. No cost; automatic cleanup.
- **Heartbeat history:** keep latest-only (`HB#{program}` overwrite) for Phase 1/2. Add `HB#{program}#{ulid}` variant only if debugging demands it — decide after first real incidents.

---

## Spike 5 — GitHub Actions OIDC → Org Member Accounts

**Question:** Can the CI/CD pipeline deploy to the Marina AWS account using OIDC without static credentials?

**Decision: Yes — standard OIDC pattern. No static keys. Repo-scoped trust policy.**

### Finding

GitHub Actions supports OIDC token exchange with AWS natively via `aws-actions/configure-aws-credentials`. The flow:

1. GitHub generates a short-lived OIDC JWT signed by `token.actions.githubusercontent.com`.
2. The `configure-aws-credentials` action exchanges it for temporary AWS credentials via `sts:AssumeRoleWithWebIdentity`.
3. The assumed role runs the deploy.

### Terraform — OIDC provider + deploy role

```hcl
# In foundation/ — created once

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

resource "aws_iam_role" "github_deploy" {
  name = "marina-github-deploy"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          # Scope to the marina repo only; restrict further to main branch for deploys
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/marina:ref:refs/heads/main"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "github_deploy" {
  role = aws_iam_role.github_deploy.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Lambda deploy
      { Effect = "Allow", Action = ["lambda:UpdateFunctionCode", "lambda:UpdateFunctionConfiguration",
          "lambda:PublishVersion", "lambda:GetFunction"], Resource = "arn:aws:lambda:${var.region}:*:function:marina-*" },
      # API Gateway read (Terraform plan needs describe)
      { Effect = "Allow", Action = ["apigateway:GET"], Resource = "*" },
      # S3 state bucket access (for Terraform remote state)
      { Effect = "Allow", Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
          Resource = ["arn:aws:s3:::marina-${var.project}-tfstate", "arn:aws:s3:::marina-${var.project}-tfstate/*"] },
      # DynamoDB lock table
      { Effect = "Allow", Action = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem"],
          Resource = "arn:aws:dynamodb:${var.region}:*:table/marina-${var.project}-tflock" }
    ]
  })
}
```

### `.github/workflows/deploy.yml`

```yaml
name: Deploy
on:
  push:
    branches: [main]

permissions:
  id-token: write   # required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ vars.AWS_ACCOUNT_ID }}:role/marina-github-deploy
          aws-region: ${{ vars.AWS_REGION }}

      - name: Terraform init + apply (services)
        run: |
          bash infra/bin/tf-init.sh services
          terraform -chdir=infra/services apply -auto-approve -var-file=../env.tfvars
```

### CI-only workflow (`ci.yml`)

```yaml
name: CI
on: [push, pull_request]

permissions:
  id-token: write
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ vars.AWS_ACCOUNT_ID }}:role/marina-github-ci
          aws-region: ${{ vars.AWS_REGION }}
      - run: uv run pytest tests/ -v
```

Add a separate `marina-github-ci` role with read-only + moto-backed test permissions (no deploy actions).

**Confirmed: no static keys. No `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` in GitHub secrets.**

---

## Spike 6 — `marina` Library Distribution via `uv`

**Question:** Does `uv add git+https://.../marina-lib.git@vX.Y.Z` pin cleanly? What is the repo name and tagging flow?

**Decision: Yes, pins cleanly. Repo name: `marina-lib`. Tagging: `vMAJOR.MINOR.PATCH` on main.**

### Finding

`uv` resolves a Git+tag reference to the exact commit SHA behind the tag and records both the tag and SHA in `uv.lock`. This means:

- The lock file is reproducible: any `uv sync` on any machine resolves the same commit.
- A tag can be moved (mutable) but the lock file holds the SHA — consumers are protected.
- `uv add` can be re-run with a new tag to upgrade: `uv add git+https://github.com/org/marina-lib.git@v1.1.0` rewrites the lock entry.

### Verified `uv.lock` entry shape

```toml
[[package]]
name = "marina"
version = "1.0.0"
source = { git = "https://github.com/org/marina-lib.git", tag = "v1.0.0", rev = "a3f2c1d..." }
```

The `rev` field is the pinned commit SHA — immutable even if the tag moves.

### Repo name

**`marina-lib`** — kebab-case, distinct from the Marina application repo. Installed package name: `marina` (in `pyproject.toml`: `name = "marina"`). Import: `import marina` or `from marina import catalog`.

### Release tagging flow

```bash
# In marina-lib repo
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# In a consumer project
uv add git+https://github.com/org/marina-lib.git@v1.0.0
# → updates uv.lock with new SHA; commit uv.lock
```

### `marina-lib/pyproject.toml` skeleton

```toml
[project]
name = "marina"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "boto3>=1.34",
    "botocore>=1.34",
]

[project.optional-dependencies]
dev = ["moto[s3,dynamodb,sqs]>=5.0", "pytest>=8.0", "ruff>=0.4"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Version bump flow (consumer)

```bash
# Bump marina-lib version: tag + push in marina-lib repo
# In each consumer:
uv add git+https://github.com/org/marina-lib.git@v1.1.0
git add uv.lock pyproject.toml
git commit -m "bump marina-lib to v1.1.0"
```

No `uv.lock` divergence between machines — `uv sync` always resolves to the pinned SHA.

### FEATURE-MARINA-LIB.md open question resolved

- No raw escape hatch — keep the boundary pure. Any unwrapped need is a signal to add a proper method.
- Spike confirmed: `uv add git+...@tag` is the canonical install and upgrade path. Repo name settled as `marina-lib`.

---

## Summary Decision Table

| Spike | Decision |
|-------|----------|
| 1 — IAM/SigV4 cross-network | HTTP API v2 + `AWS_IAM` authoriser + per-member invoke role (Org perimeter); no IP restriction, no resource policy, REST v1 rejected |
| 2 — Repo→capability binding | GitHub API token check at onboard-time; gate caches ACL 5-min in-process TTL |
| 3 — Terraform bootstrap | `backend/` stays local-state; `foundation/`+`services/` init directly to S3 |
| 4 — DynamoDB schema | All 12 patterns valid; zero scans; fix `attribute_not_exists(SK)` condition; add TTL on events |
| 5 — GitHub Actions OIDC | OIDC provider + repo-scoped trust policy; no static keys |
| 6 — uv library distribution | `marina-lib` repo; `vMAJOR.MINOR.PATCH` tags; `uv add git+...@tag` pins to SHA in lock |

## Open Questions Resolved in Specs

| Spec file | Question resolved |
|-----------|------------------|
| ARCHITECTURE.md | No IP allow-list or VPC endpoint needed (Spike 1) |
| ARCHITECTURE.md | Gate caches ACL 5-min in-process (Spike 2) |
| DATABASE.md | Event TTL: 30-day `ttl` attribute; heartbeats: latest-only for Phase 1/2 (Spike 4) |
| FEATURE-ACCESS-CONTROL.md | GitHub token check at onboard; nightly re-sync; admin-only `POST /onboard` (Spike 2) |
| FEATURE-MARINA-LIB.md | No escape hatch; `uv add git+...@tag` confirmed (Spike 6) |
