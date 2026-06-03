# Screen: Setup — Terraform

| Field | Value |
|-------|-------|
| Version | 20260603 V6 |
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

## Page Header

Standard page header per UI-GENERAL. Icon: Simple Icons `terraform`. Title: `Marina` (always centered). Right column description block:

> Provisions API Gateway · Lambda · DynamoDB · IAM · CloudWatch Logs.  
> `MARINA_API_URL` is the only output Marina needs.

## Layout

Single-column, max-width 900px, centered. Three `mn-card` sections: Terraform CLI, Commands to Run, Marina API Endpoint.

```
┌──────────────────────────────────────────────────────────────┐
│  🔧  TERRAFORM CLI                                            │
│  ─────────────────────────────────────────────────────────  │
│  Status:  ✅  v1.7.5 installed              [↻ Re-check]     │
│                                                              │
│  Not installed? Run this in a terminal:                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  sudo apt-get update && ...                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                       [📋 Copy install cmd]  │
├──────────────────────────────────────────────────────────────┤
│  ▶  COMMANDS TO RUN                             [📋 Copy]    │
│  ─────────────────────────────────────────────────────────  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  cd infra/foundation && terraform init               │   │
│  │  terraform plan -var="org={marina_org}"              │   │
│  │  terraform apply -var="org={marina_org}"             │   │
│  │  terraform output api_url                            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ⚠️  Apply creates real AWS resources in your account.       │
├──────────────────────────────────────────────────────────────┤
│  🌐  MARINA API ENDPOINT                                     │
│  ─────────────────────────────────────────────────────────  │
│  MARINA_API_URL                                              │
│  [ https://abc123.execute-api.us-east-1.amazonaws.com    ]  │
│                                                              │
│  ✅  Endpoint reachable              [↻ Verify Endpoint]     │
└──────────────────────────────────────────────────────────────┘
```

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

Read-only reference card. Single dark code block containing all four commands. One `[📋 Copy]` icon button in the top-right corner of the block copies all commands to the clipboard as a single string (newline-separated). The copy icon uses `bi-clipboard` styled as a ghost icon button matching the Re-check (`bi-arrow-clockwise`) button style.

The `{marina_org}` placeholder is replaced at render time with the live `settings.marina_org` value. If `marina_org` is not set, the placeholder is left as `{marina_org}` and a hint is shown beneath the block: "Set Marina Org on the AWS tab first."

```
cd infra/foundation && terraform init
terraform plan -var="org={marina_org}"
terraform apply -var="org={marina_org}"
terraform output api_url
```

Static note below the block: `⚠️ Apply creates real AWS resources in your account and may incur costs.`

The code block uses the same dark syntax style as the Terraform CLI install block: dark background (`#1e1e1e`), monospace font, near-white text, 0.85rem, with a thin border. The copy icon is positioned `top: 0.5rem; right: 0.5rem` inside the block container.

## MARINA API ENDPOINT Card

Inline-editable field for `MARINA_API_URL`. The user pastes the value from `terraform output api_url`.

| Element | Behaviour |
|---------|-----------|
| Input field | Inline-editable. Tab-out / blur triggers `POST /api/setup/config` with `key=MARINA_API_URL`. |
| Auto-set on page load | On page load, if `MARINA_API_URL` is not set, Marina silently runs `terraform output api_url` (subprocess, 5-second timeout). If it returns a valid HTTPS URL, the field is auto-populated, saved via `/api/setup/terraform/auto-read-url`, and a toast confirms "MARINA_API_URL set from Terraform output." No user action required. |
| `[↻ Verify Endpoint]` | Calls `POST /api/setup/terraform/verify-endpoint`. Marina pings the URL with a 5-second timeout. Returns ✅ reachable or ❌ unreachable with HTTP status or timeout reason. |
| Status line | Updated by verify: `✅ Endpoint reachable` / `⚠️ Timeout` / `❌ {HTTP error}` |

The field is always visible. If `MARINA_API_URL` is not set and auto-set fails (no Terraform state), the field is empty with placeholder text `https://xxxxxxxx.execute-api.{region}.amazonaws.com`. `MARINA_API_URL` is stored in the `settings` table — no restart required.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/api/setup/terraform/status` | — | JSON: `{ terraform_version, api_url, endpoint_reachable }` |
| GET | `/api/setup/terraform/check-cli` | — | JSON: `{ installed: bool, version: str }` |
| POST | `/api/setup/terraform/verify-endpoint` | — | HTML fragment: endpoint status line |
| POST | `/api/setup/terraform/auto-read-url` | — | Toast + field HTML fragment (auto-set from `terraform output api_url`) |
| POST | `/api/setup/config` | `key`, `value` | Toast fragment (MARINA_API_URL inline save) |

The old `install`, `init`, `plan`, `apply`, `save-env`, and `logs` endpoints are removed — Terraform is no longer executed server-side.

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings.marina_org` | `settings` table via `/api/setup/config` or `/api/setup/terraform/auto-read-url` |
| `MARINA_API_URL` (settings table, `.env` fallback) | `settings` table (`MARINA_API_URL`) |
| `terraform version` (subprocess, read-only) | None |
| `terraform output api_url` (subprocess, page load auto-set) | None |
| HTTP GET `MARINA_API_URL` (reachability ping only) | None |

## Open Questions

- Should `MARINA_API_URL` be stored in the `settings` table (persisted across restarts) rather than only in `.env`? V1: store in `settings` table — avoids requiring a Marina restart to pick up the value. `.env` still accepted on startup as a fallback.
- Should the verify endpoint check return the Marina health payload, or just HTTP 200? V1: any 2xx response counts as reachable.
