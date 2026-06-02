# Screen: Setup — Terraform

| Field | Value |
|-------|-------|
| Version | 20260602 V5 |
| Header Background | `mn-hdr-bg--cloud` |
| Route | `GET /setup/terraform` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Terraform |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Terraform reference and verification screen. Shows what Terraform provisions, lists the commands to run, and verifies the Marina API endpoint after deployment. Does not execute Terraform — the user runs commands in a terminal. |
| Depends On | UI-GENERAL.md, SCREEN-SETUP-AWS.md |
| Provides | GET /setup/terraform |

## Header KPIs

Left column of the page header. Component type: **Status Light** (`mn-hdr-light`).

| State | Light | Condition |
|-------|-------|-----------|
| ✅ | `mn-hdr-light--ok` (green) | `MARINA_API_URL` set AND endpoint reachable |
| ⚠️ | `mn-hdr-light--warn` (amber) | `MARINA_API_URL` set BUT endpoint not responding |
| ❌ | `mn-hdr-light--error` (red) | `MARINA_API_URL` not set |

## What Terraform Provisions

Terraform creates the Marina AWS plane — the cloud-side infrastructure that stores and synchronises your project data. The user runs Terraform once from a terminal; Marina does not execute it.

### Resources Created

| Resource | Description |
|----------|-------------|
| API Gateway (REST) | HTTPS endpoint for all Marina cloud operations. Its URL becomes `MARINA_API_URL`. |
| Lambda functions | Serverless handlers for project sync, status updates, and cloud queries. |
| DynamoDB tables | Project data store, partitioned by `marina_org`. All project records live here. |
| IAM roles & policies | Least-privilege execution roles for the Lambda functions. |
| CloudWatch log groups | Lambda execution logs, retained 14 days. |

### Environment Variable Set by Terraform

| Variable | Source | Purpose |
|----------|--------|---------|
| `MARINA_API_URL` | `terraform output api_url` after apply | The API Gateway endpoint Marina calls for all cloud operations. Set in `.env`. |

`MARINA_API_URL` is the only variable Marina needs from the Terraform output. Every cloud sync and project status call goes to this URL.

## Layout

Single-column, max-width 900px, centered. Five `mn-card` sections: What Terraform Provisions, Prerequisites, Terraform CLI, Commands to Run, Marina API Endpoint.

```
┌──────────────────────────────────────────────────────────────┐
│  ☁  WHAT TERRAFORM PROVISIONS                                │
│  ─────────────────────────────────────────────────────────  │
│  Terraform creates the Marina AWS plane in your account.     │
│  Resources: API Gateway · Lambda · DynamoDB · IAM · Logs     │
│  After apply: copy MARINA_API_URL from the output.           │
├──────────────────────────────────────────────────────────────┤
│  🏗  PREREQUISITES                                            │
│  ─────────────────────────────────────────────────────────  │
│  ✅  Python AWS Connectivity   arn:aws:iam::111:user/ed      │
│  ✅  Marina Org                marina                        │
│  ✅  Infra path                infra/foundation              │
├──────────────────────────────────────────────────────────────┤
│  🔧  TERRAFORM CLI                                            │
│  ─────────────────────────────────────────────────────────  │
│  Status:  ✅  v1.7.5 installed              [↻ Re-check]     │
│                                                              │
│  Not installed? Run this in a terminal:                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  sudo apt-get update && sudo apt-get install -y \    │   │
│  │      gnupg software-properties-common curl &&  \    │   │
│  │  curl -fsSL https://apt.releases.hashicorp.com/gpg \ │  │
│  │      | sudo gpg --dearmor -o \                       │   │
│  │      /usr/share/keyrings/hashicorp-archive-keyring.gpg \ │
│  │  && echo "deb [signed-by=...] ..." | \               │   │
│  │      sudo tee /etc/apt/sources.list.d/hashicorp.list  │  │
│  │  && sudo apt-get update && \                         │   │
│  │      sudo apt-get install -y terraform               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                       [📋 Copy install cmd]  │
├──────────────────────────────────────────────────────────────┤
│  ▶  COMMANDS TO RUN                                          │
│  ─────────────────────────────────────────────────────────  │
│  Run these three commands in a terminal from the Marina      │
│  project directory. After apply, copy the api_url value      │
│  shown in the output.                                        │
│                                                              │
│  1. cd infra/foundation && terraform init                    │
│                                       [📋 Copy]              │
│  2. terraform plan -var="org={marina_org}"                   │
│                                       [📋 Copy]              │
│  3. terraform apply -var="org={marina_org}"                  │
│                                       [📋 Copy]              │
│  4. terraform output api_url        ← copy this value        │
│                                       [📋 Copy]              │
│                                                              │
│  After step 4: paste the URL into the field below.          │
├──────────────────────────────────────────────────────────────┤
│  🌐  MARINA API ENDPOINT                                     │
│  ─────────────────────────────────────────────────────────  │
│  MARINA_API_URL                                              │
│  [ https://abc123.execute-api.us-east-1.amazonaws.com    ]  │
│                                                              │
│  ✅  Endpoint reachable              [↻ Verify Endpoint]     │
│  (Saved to .env — Marina restart required to take effect)   │
└──────────────────────────────────────────────────────────────┘
```

## WHAT TERRAFORM PROVISIONS Card

Static informational card. Always expanded, no collapse. Shows the resource table and the `MARINA_API_URL` explanation. No interactive elements.

Purpose: orient the user before they run anything. They should understand what they are about to provision and why `MARINA_API_URL` is the key output.

## PREREQUISITES Card

Checks readiness before the user runs Terraform.

| # | Check | Source | If ❌ |
|---|-------|--------|-------|
| 1 | Python AWS Connectivity | `platform_stats.python_aws_ok = 1` | Link to AWS tab |
| 2 | Marina Org | `settings.marina_org` non-empty | Link to AWS tab |
| 3 | Infra path | `infra/foundation/` exists | Static hint: `infra/foundation/ not found in Marina project root` |

No step-gating on this screen — prerequisites are informational only. The user runs Terraform from a terminal regardless of what this card shows.

## TERRAFORM CLI Card

Verify-only. Marina cannot install Terraform (requires sudo). The card:

- Runs `terraform version` via `GET /api/setup/terraform/check-cli` on page load.
- Shows: `✅ {version} installed` or `❌ Not installed`.
- `[↻ Re-check]` re-runs the check after the user installs.
- Static read-only code block: the full HashiCorp APT install command for Ubuntu/WSL2, with a `[📋 Copy install cmd]` button.
- No install button. No server-side sudo execution.

Install command shown verbatim (user copies and runs in a terminal):
```
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common curl
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y terraform
```

## COMMANDS TO RUN Card

Read-only reference card. Shows the four terminal commands the user must run, in order. Each line has a `[📋 Copy]` button that copies only that command to the clipboard.

The `{marina_org}` placeholder in the copy text is replaced at render time with the live `settings.marina_org` value. If `marina_org` is not set, the placeholder is left as `{marina_org}` and a hint is shown: "Set Marina Org on the AWS tab first."

Commands:

| # | Command | Description |
|---|---------|-------------|
| 1 | `cd infra/foundation && terraform init` | Download providers and initialise the working directory |
| 2 | `terraform plan -var="org={marina_org}"` | Preview changes — review before applying |
| 3 | `terraform apply -var="org={marina_org}"` | Provision AWS resources (creates real resources in your account) |
| 4 | `terraform output api_url` | Print the API Gateway URL — paste this into the field below |

Static note below command 3: `⚠️ Apply creates real AWS resources in your account and may incur costs.`

## MARINA API ENDPOINT Card

Inline-editable field for `MARINA_API_URL`. The user pastes the value from `terraform output api_url`.

| Element | Behaviour |
|---------|-----------|
| Input field | Inline-editable. Tab-out / blur triggers `POST /api/setup/config` with `key=MARINA_API_URL`. |
| `[↻ Verify Endpoint]` | Calls `POST /api/setup/terraform/verify-endpoint`. Marina pings the URL with a 5-second timeout. Returns ✅ reachable or ❌ unreachable with HTTP status or timeout reason. |
| Status line | Updated by verify: `✅ Endpoint reachable` / `⚠️ Timeout` / `❌ {HTTP error}` |
| Restart note | Static: "Marina requires a restart after `.env` is updated for the new URL to take effect." |

The field is always visible. If `MARINA_API_URL` is not set, the field is empty with placeholder text `https://xxxxxxxx.execute-api.{region}.amazonaws.com`.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/api/setup/terraform/status` | — | JSON: `{ terraform_version, api_url, endpoint_reachable }` |
| GET | `/api/setup/terraform/check-cli` | — | JSON: `{ installed: bool, version: str }` |
| POST | `/api/setup/terraform/verify-endpoint` | — | HTML fragment: endpoint status line |
| POST | `/api/setup/config` | `key`, `value` | Toast fragment (MARINA_API_URL inline save) |

The old `install`, `init`, `plan`, `apply`, `save-env`, and `logs` endpoints are removed — Terraform is no longer executed server-side.

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings.marina_org` | `settings` table via `/api/setup/config` (`MARINA_API_URL`) |
| `MARINA_API_URL` (env / settings) | None |
| `platform_stats.python_aws_ok` | None |
| `terraform version` (subprocess, read-only) | None |
| HTTP GET `MARINA_API_URL` (reachability ping only) | None |

## Open Questions

- Should `MARINA_API_URL` be stored in the `settings` table (persisted across restarts) rather than only in `.env`? V1: store in `settings` table — avoids requiring a Marina restart to pick up the value. `.env` still accepted on startup as a fallback.
- Should the verify endpoint check return the Marina health payload, or just HTTP 200? V1: any 2xx response counts as reachable.
