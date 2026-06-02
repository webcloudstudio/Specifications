# Screen: Setup — Terraform

| Field | Value |
|-------|-------|
| Version | 20260602 V3 |
| Route | `GET /setup/terraform` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Terraform |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Guided Terraform deployment for the Marina AWS plane. Terraform is used to configure AWS services dynamically. Runs init, plan, and apply steps sequentially, then captures the api_url output into .env. Includes log viewer and Marina API endpoint status. |
| Depends On | UI-GENERAL.md, SCREEN-SETUP-AWS.md |
| Provides | GET /setup/terraform |

## Header KPIs

Left column of the page header. Component type: **All-Good Indicator** (`mn-hdr-allgood`), scoped to AWS plane readiness.

| State | Display | Condition |
|-------|---------|-----------|
| ✅ | `bi-check-circle-fill` + "Deployed" (teal) | `MARINA_API_URL` set AND `endpoint_reachable = 1` |
| ⚠️ | `bi-exclamation-triangle-fill` + "Endpoint unreachable" (amber) | `MARINA_API_URL` set BUT `endpoint_reachable = 0` |
| ❌ | `bi-exclamation-triangle-fill` + "Not deployed" (red) | `MARINA_API_URL` not set |

## Purpose

> **Terraform is used to configure AWS services dynamically.** This screen provisions the Marina AWS plane — API Gateway, Lambda, DynamoDB — in your account without requiring any manual AWS console steps.

The `/setup/aws` page handles identity and Python connectivity. This screen **executes** the Terraform workflow: init → plan → apply. It surfaces real command output, tracks per-step status, and copies `MARINA_API_URL` into `.env` on completion. It also links back to `/setup/aws` for profile and org configuration.

## Prerequisites

Before this screen is actionable:
- Python AWS connectivity must pass (`platform_stats.python_aws_ok = 1`) — from the AWS tab
- `marina_org` must be set — from the AWS tab

The page renders with a warning panel if either prerequisite is unmet, with links to `/setup/aws`.

## Layout

Single-column, max-width 900px, centered. Six `mn-card` sections stacked vertically: Prerequisites, Terraform Install, Init, Plan, Apply, Marina API Endpoint.

```
┌──────────────────────────────────────────────────────────────┐
│  🏗  PREREQUISITES                                           │
│  ─────────────────────────────────────────────────────────  │
│  ✅  Python AWS Connectivity   arn:aws:iam::111:user/ed      │
│  ✅  Marina Org                marina                        │
│  ✅  Terraform CLI             v1.7.5                        │
│  ✅  Infra path                infra/foundation              │
├──────────────────────────────────────────────────────────────┤
│  🔧  TERRAFORM INSTALL                                       │
│  ─────────────────────────────────────────────────────────  │
│  Installs the Terraform CLI if not already present.         │
│  Current: ⚠️  Not installed                                 │
│                              [⬇ Install Terraform]          │
│  Output:  (streamed install log)                             │
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
├──────────────────────────────────────────────────────────────┤
│  🌐  MARINA API ENDPOINT                                     │
│  ─────────────────────────────────────────────────────────  │
│  Current value:  ✅  https://abc123.execute-api.us-east-1…  │
│  (Set MARINA_API_URL in .env — requires Marina restart)     │
│  [📋 Copy env line]                                          │
│                                                              │
│  📋  TERRAFORM LOGS  [▼ Show last 100 lines]                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  (collapsible log output from last terraform run)    │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## PREREQUISITES Card

Checks and displays readiness before any Terraform action is allowed.

| # | Check | Source | Required |
|---|-------|--------|----------|
| 1 | Python AWS Connectivity | `platform_stats.python_aws_ok` (set by AWS tab check-python) | Yes — blocks all steps |
| 2 | Marina Org | `settings.marina_org` | Yes — blocks Apply |
| 3 | Terraform CLI | `terraform version` subprocess | Yes — blocks Init/Plan/Apply (Install button available) |
| 4 | Infra path | Path `infra/foundation/` exists in Marina project root | Yes — blocks all steps |

If any required check is ❌, the affected step cards render as disabled with an inline hint linking to the corrective action.

## TERRAFORM INSTALL Card

Shown when `terraform version` exits non-zero (Terraform CLI not installed). Provides a one-click install path so the user does not need to open a terminal.

`[⬇ Install Terraform]` triggers `POST /api/setup/terraform/install`, which runs the HashiCorp APT install sequence for Ubuntu/WSL2:

```
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install -y terraform
```

- Output streams in a scrollable `<pre>` block.
- On exit 0: card shows `✅ Terraform {version} installed`; Install button replaced with `[↻ Re-check]`.
- On exit non-0: red banner with last 20 lines of output.
- After successful install, the PREREQUISITES card auto-refreshes to show `✅ Terraform CLI`.

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

## MARINA API ENDPOINT Card

Read-only display of the current `MARINA_API_URL` env var value. This is the output produced by Terraform Apply and must be saved to `.env` for Marina to reach the cloud plane.

| Element | Behaviour |
|---------|-----------|
| Status line | ✅ `{url}` if set; ⚠️ `(not set — run Apply first)` if empty |
| `[📋 Copy env line]` | Copies `MARINA_API_URL={url}` to clipboard |
| Reminder | Static note: "Marina requires a restart after `.env` is updated." |

This card is always visible (not collapsed), so the endpoint status is always apparent.

## TERRAFORM LOGS Section

A collapsible block within the MARINA API ENDPOINT card (or directly below Apply). Shows the last N lines of the combined Terraform output (init + plan + apply) from the most recent run.

| Element | Behaviour |
|---------|-----------|
| `[▼ Show last 100 lines]` toggle | Expands/collapses the log block. State preserved via Bootstrap collapse. |
| Log content | Scrollable `<pre>` (max-height 300px), monospace 13px. Read from `data/terraform.log` written by the subprocess runners. |
| Timestamp | Header line: `Last run: {timestamp}`. `—` if no run in this session. |

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/api/setup/terraform/status` | — | JSON: `{ init_ok, plan_ok, apply_ok, api_url, terraform_version }` |
| POST | `/api/setup/terraform/install` | — | Streamed text/plain output, then install result fragment |
| POST | `/api/setup/terraform/init` | — | Streamed text/plain output, then status fragment |
| POST | `/api/setup/terraform/plan` | — | Streamed text/plain output, then plan summary fragment |
| POST | `/api/setup/terraform/apply` | — | Streamed text/plain output, then apply result fragment |
| POST | `/api/setup/terraform/save-env` | `key`, `value` | ✅ confirmation fragment |
| GET | `/api/setup/terraform/logs` | — | HTML fragment: last 100 lines from `data/terraform.log` |

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
