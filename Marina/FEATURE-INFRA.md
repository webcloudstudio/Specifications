# FEATURE: Infrastructure (Terraform)

| Field       | Value |
|-------------|-------|
| Version     | 20260603 V1 |
| Description | The layered Terraform tree (`backend/`, `foundation/`, `services/`, `modules/`) that provisions Marina's entire AWS broadcast plane. This is real HCL, not a stub. |
| Depends On  | DATABASE.md, ARCHITECTURE.md |
| Provides    | — |

**Description:** Defines the concrete contents of every Terraform layer so an AI build produces working
HCL — `terraform init/plan/apply` must succeed against a real AWS account. Patterns (backend, naming,
tags, wrappers, bootstrap cycle) are in `stack/terraform.md`; this file specifies *what Marina
provisions*. The DynamoDB schema this provisions is in `DATABASE.md`; the Lambda handlers it wires are
the `src/` packages built by the `FEATURE-*` Lambda specs.

---

## Build Mandate

Every `.tf` file named below must contain working HashiCorp configuration — `resource`, `variable`,
`output`, `data`, and `terraform` blocks. Comment-only placeholder files are a build failure. After a
build, `terraform validate` must pass in each layer and `terraform fmt -check` must report no diffs.

## Shared Variables (every layer)

All three deployable layers (`foundation/`, `services/`, and the bootstrap `backend/`) declare the same
variable set in a `variables.tf`. There are **no defaults** — values come from `infra/env.tfvars`. The
literal error `Value for undeclared variable "org"` means this block is missing; it must exist in every
layer's root module.

```hcl
variable "project" { type = string }   # e.g. "marina" — feeds marina-{project}-{resource}
variable "org"     { type = string }   # owning org, applied as the Owner tag
variable "region"  { type = string }   # AWS region
variable "phase"   { type = string }   # build phase, applied as the Phase tag
```

Each layer defines `locals.marina_tags` (`Project`, `Owner`, `ManagedBy = "terraform"`, `Phase`) and
applies it to every taggable resource. All resource names derive from `marina-${var.project}-{resource}`
— no hardcoded names, regions, or account IDs (`stack/terraform.md` §4).

Provider versions are pinned in `required_providers` in every layer.

## Layer: `backend/` (one-shot bootstrap, LOCAL state)

`main.tf` + `variables.tf`. **No** `backend "s3"` block — this layer stays on local state permanently
(`stack/terraform.md` §3). Provisions the remote-state substrate the other layers depend on:

| Resource | Spec |
|----------|------|
| `aws_s3_bucket.tfstate` | `marina-${var.project}-tfstate`; versioning **enabled**; SSE (AES256) enabled; `aws_s3_bucket_public_access_block` blocking all four flags. |
| `aws_dynamodb_table.tflock` | `marina-${var.project}-tflock`; `PAY_PER_REQUEST`; hash key `LockID` (S). |

`outputs.tf`: `state_bucket`, `lock_table` (names, informational).

## Layer: `foundation/` (rare, gated apply — S3 backend from first init)

`backend.tf` (S3 backend → `foundation/terraform.tfstate` in the bootstrap bucket, DynamoDB lock),
`variables.tf`, `main.tf`, `outputs.tf`. Provisions durable state that routine deploys must never touch:

| Resource | Spec |
|----------|------|
| `aws_dynamodb_table.catalog` | The single-table catalog/state store from `DATABASE.md`. `PAY_PER_REQUEST`; PK/SK per `DATABASE.md`; any GSIs `DATABASE.md` declares; **TTL enabled on the `ttl` attribute** (expires heartbeat/event items). |
| `aws_sqs_queue.voice_dlq` | `marina-${var.project}-voice-dlq`. |
| `aws_sqs_queue.voice` | `marina-${var.project}-voice`; redrive policy → `voice_dlq`, `maxReceiveCount = 3`; `receive_wait_time_seconds = 20`; `visibility_timeout_seconds = 300`. |
| `aws_s3_bucket.voice` | VoiceForward audio blobs; versioned; public access blocked. |
| `aws_s3_bucket.share` | Per-user company share; public access blocked; per-user prefixes (no bucket policy granting cross-user access). |
| IAM / OIDC | GitHub Actions OIDC provider + a deploy role assumable by the repo (`stack/github-actions.md`); one execution role per Lambda is defined in `services/` (below). |

`outputs.tf`: `catalog_table_name`, `catalog_table_arn`, `voice_queue_url`, `voice_queue_arn`,
`voice_bucket`, `share_bucket`, `deploy_role_arn`.

## Layer: `services/` (rerun-anytime — applied on every deploy)

`backend.tf` (S3 backend → `services/terraform.tfstate`), `variables.tf`, `main.tf`, `outputs.tf`.
Reads foundation outputs via `data "terraform_remote_state" "foundation"` (same bucket,
`foundation/terraform.tfstate`). Uses the reusable modules in `modules/`.

| Resource | Spec |
|----------|------|
| `aws_apigatewayv2_api.http` | HTTP API, `marina-${var.project}-api`. |
| `aws_apigatewayv2_stage` | `$default`, auto-deploy, access logs to CloudWatch. |
| One Lambda per `src/` package | Via `module "lambda_fn"`: `runtime = python3.12`, `handler = handler.handler`, env vars `TABLE_NAME` (from foundation), `MARINA_ORG`, `LOG_LEVEL` (+ `QUEUE_URL`/`SHARE_BUCKET` where the function needs them); one execution role per function with least-privilege policy (see below). CloudWatch log group per function. |
| One route per endpoint | Via `module "http_route"`: `authorization_type = AWS_IAM`, `AWS_PROXY` integration → the owning Lambda. |

**Lambda → route → IAM policy matrix** (Phase 1 unless noted):

| Lambda (`marina-{project}-…`) | Routes | Least-privilege policy |
|------|--------|------------------------|
| `catalog-publish` | `POST /catalog` | `dynamodb:PutItem`/`UpdateItem` on catalog table ARN |
| `catalog-read` | `GET /catalog`, `GET /catalog/{project}` | `dynamodb:GetItem`+`Query` on catalog table ARN |
| `capabilities-read` | `GET /capabilities` | `dynamodb:GetItem`+`Query` on catalog table ARN |
| `report-ingest` | `POST /heartbeat`, `POST /events` | `dynamodb:PutItem`/`UpdateItem` on catalog table ARN |
| `health-read` | `GET /health/{project}` | `dynamodb:Query` on catalog table ARN |
| `queue-submit` (Phase 2) | `POST /queue/{queue}` | `sqs:SendMessage` on `marina-{project}-*` queue ARNs + `dynamodb:GetItem` on catalog table ARN (ACL read) |
| `share-index` (Phase 2) | `GET /share`, `POST /share` | `dynamodb:GetItem`+`PutItem` on catalog table ARN; share bucket read/write scoped to the caller prefix |

`outputs.tf`: **`api_url`** = the API Gateway invoke URL (`aws_apigatewayv2_api.http.api_endpoint` or
the stage URL). This is the single output Marina needs (`MARINA_API_URL`); it lives in **this layer**,
not in `foundation/`.

## Layer: `modules/`

| Module | Inputs | Creates |
|--------|--------|---------|
| `lambda_fn` | `name`, `source_dir`, `env`, `policy_json` | Lambda function (zip from `source_dir`), execution role, attached inline policy, CloudWatch log group. |
| `http_route` | `api_id`, `method`, `path`, `lambda_arn` | `aws_apigatewayv2_integration` (AWS_PROXY) + `aws_apigatewayv2_route` (`AWS_IAM` auth) + invoke permission. |

## `infra/env.tfvars` and the bin wrappers

`infra/env.tfvars` holds non-secret values for all layers: `project`, `org`, `region`, `phase`. It is
**not** auto-loaded by Terraform (only `terraform.tfvars` / `*.auto.tfvars` are), so every plan/apply
passes `-var-file=../env.tfvars`. The wrappers do this:

- `infra/bin/tf-init.sh <layer>` — `terraform init` (backend layers init against S3).
- `infra/bin/tf-plan.sh <layer>` — `cd <layer> && terraform plan -var-file=../env.tfvars -out=plan.out`.
- `infra/bin/tf-apply.sh <layer>` — applies `plan.out`.

Marina writes the live `settings.marina_org` into `infra/env.tfvars` (`org = "…"`) when the operator
sets it on the AWS tab, so the committed placeholder is replaced before apply. No secrets ever enter
`.tf` files or state (`stack/terraform.md` §5).

## Apply Order (what the Terraform screen documents)

```
cd infra
./bin/tf-init.sh backend    && ./bin/tf-apply.sh backend      # one-time bootstrap, local state
./bin/tf-init.sh foundation && ./bin/tf-apply.sh foundation   # rare; creates the catalog table
./bin/tf-init.sh services   && ./bin/tf-apply.sh services     # every deploy; creates the API
terraform -chdir=services output api_url                      # -> paste into Marina as MARINA_API_URL
```

## Test

`bin/test_infra.sh` — runs `terraform fmt -check` and `terraform validate` in `backend/`, `foundation/`,
and `services/`. Exits non-zero on any fmt diff or validation error. No AWS credentials required.

## Open Questions

- Should `services/` read the catalog table name from `terraform_remote_state.foundation` (chosen here)
  or reconstruct it from `marina-${var.project}-catalog`? V1: remote state — single source of truth,
  survives a naming-convention change. Reconstruction is the fallback if cross-layer state coupling
  becomes a problem.
- Should the GitHub OIDC provider live in `foundation/` (chosen) or a dedicated `iam/` layer? V1:
  `foundation/` — it changes as rarely as the roles it backs.
