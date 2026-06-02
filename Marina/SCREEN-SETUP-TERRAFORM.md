# Screen: Setup — Terraform

| Field | Value |
|-------|-------|
| Version | 20260601 V1 |
| Route | `GET /setup/terraform` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Terraform |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Guided Terraform deployment for the Marina AWS plane. Runs init, plan, and apply steps sequentially via the infra/foundation scripts, then captures the api_url output into .env. |
| Depends On | UI-GENERAL.md, SCREEN-SETUP-AWS.md |
| Provides | GET /setup/terraform |

## Purpose

The `/setup/aws` page documents the Terraform deployment steps as static instructions. This screen **executes** them: init → plan → apply. It surfaces real command output, tracks per-step status, and copies `MARINA_API_URL` into `.env` on completion. It also links back to `/setup/aws` for profile and org configuration.

## Prerequisites

Before this screen is actionable:
- AWS profile must be valid (`aws sts get-caller-identity` exits 0)
- `marina_org` must be set

The page renders with a warning panel if either prerequisite is unmet, with links to `/setup/aws`.

## Layout

Single-column, max-width 900px, centered. Four `mn-card` sections stacked vertically: Prerequisites, Init, Plan, Apply.

```
┌──────────────────────────────────────────────────────────────┐
│  🏗  PREREQUISITES                                           │
│  ─────────────────────────────────────────────────────────  │
│  ✅  AWS Identity    arn:aws:iam::111:user/ed                │
│  ✅  Marina Org      marina                                  │
│  ✅  Terraform CLI   v1.7.5                                  │
│  ✅  Infra path      infra/foundation                        │
├──────────────────────────────────────────────────────────────┤
│  1️⃣  TERRAFORM INIT                                          │
│  ─────────────────────────────────────────────────────────  │
│  Initialises the Terraform working directory and downloads   │
│  providers. Safe to re-run.                                  │
│                              [▶ Run Init]                    │
│  ✅  Completed — providers downloaded                        │
├──────────────────────────────────────────────────────────────┤
│  2️⃣  TERRAFORM PLAN                                          │
│  ─────────────────────────────────────────────────────────  │
│  Previews the changes Terraform will make. Review before     │
│  applying.                                                   │
│                              [▶ Run Plan]                    │
│  📋  Plan output (scrollable):                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Plan: 12 to add, 0 to change, 0 to destroy.         │   │
│  └──────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────┤
│  3️⃣  TERRAFORM APPLY                                         │
│  ─────────────────────────────────────────────────────────  │
│  Deploys the AWS plane. This creates real AWS resources.     │
│  Requires a confirmed plan (step 2).                         │
│  ⚠️  Resources will be created in your AWS account.         │
│                              [▶ Run Apply]                   │
│  ✅  Apply complete.                                         │
│  api_url = https://abc123.execute-api.us-east-1.amazonaws.com│
│                 [📋 Copy export line]  [💾 Save to .env]     │
└──────────────────────────────────────────────────────────────┘
```

## PREREQUISITES Card

Checks and displays readiness before any Terraform action is allowed.

| # | Check | Source | Required |
|---|-------|--------|----------|
| 1 | AWS Identity | `aws sts get-caller-identity` exit code | Yes — blocks all steps |
| 2 | Marina Org | `settings.marina_org` | Yes — blocks Apply |
| 3 | Terraform CLI | `terraform version` subprocess | Yes — blocks all steps |
| 4 | Infra path | Path `infra/foundation/` exists in Marina project root | Yes — blocks all steps |

If any required check is ❌, the affected step cards render as disabled with an inline hint linking to the corrective action.

## TERRAFORM INIT Card

Executes `infra/foundation/tf-init.sh` via `POST /api/setup/terraform/init`.

- `[▶ Run Init]` button triggers the call; disabled while running.
- Output streams into a scrollable `<pre>` block (HTMX `hx-swap="beforeend"`).
- On exit 0: card collapses to ✅ summary line; Init button replaced with `[↻ Re-run]`.
- On exit non-0: red banner with last 20 lines of output.
- Init step does not require plan or apply to be clean — always re-runnable.

## TERRAFORM PLAN Card

Executes `infra/foundation/tf-plan.sh` via `POST /api/setup/terraform/plan`.

- Requires Init completed (exit 0). Otherwise button is disabled.
- Passes `org` var: `-var="org={marina_org}"`.
- Streams output same as Init.
- On exit 0: output block collapses; shows summary line `Plan: N to add, M to change, P to destroy.` parsed from stdout.
- Stores plan result in session (`plan_ok = True`) to gate the Apply button.

## TERRAFORM APPLY Card

Executes `infra/foundation/tf-apply.sh` via `POST /api/setup/terraform/apply`.

- Requires Plan completed in the current session (`plan_ok = True`). Otherwise button disabled with hint.
- Warning banner: `⚠️ This will create real AWS resources in your account.`
- Auto-approve flag: `-auto-approve` — no interactive confirmation needed (Marina is local).
- On exit 0: parses `api_url` from Terraform outputs.
  - Displays the raw URL.
  - `[📋 Copy export line]`: copies `export MARINA_API_URL=<url>` to clipboard.
  - `[💾 Save to .env]`: writes `MARINA_API_URL=<url>` to `.env` and shows ✅ confirmation.
  - After Save: the `/setup/aws` API Endpoint card will show ✅ on next visit (env reloaded on restart).
- On exit non-0: red banner, last 40 lines of output.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/api/setup/terraform/status` | — | JSON: `{ init_ok, plan_ok, apply_ok, api_url }` |
| POST | `/api/setup/terraform/init` | — | Streamed text/plain output, then status fragment |
| POST | `/api/setup/terraform/plan` | — | Streamed text/plain output, then plan summary fragment |
| POST | `/api/setup/terraform/apply` | — | Streamed text/plain output, then apply result fragment |
| POST | `/api/setup/terraform/save-env` | `key`, `value` | ✅ confirmation fragment |

All POST endpoints run as background subprocesses. Output is streamed via chunked response. Marina must restart after `.env` is written for `MARINA_API_URL` to take effect.

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings.marina_org`, `settings.aws_profile` | `.env` file (Save to .env action only) |
| `AWS_REGION` (env) | None |
| `infra/foundation/tf-init.sh`, `tf-plan.sh`, `tf-apply.sh` | None |
| `terraform version` | None |

## Open Questions

- Should the Apply card require an explicit user acknowledgement checkbox before enabling the button? V1: warning banner only — no checkbox.
- Should Terraform state be stored in S3 (remote backend)? Infrastructure concern — out of scope for this screen. The screen only drives local execution.
- Should the page detect an existing deploy (Terraform state file) and show current resource status? V2.
