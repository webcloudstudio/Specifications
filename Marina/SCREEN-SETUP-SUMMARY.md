# Screen: Setup — Summary

| Field | Value |
|-------|-------|
| Version | 20260529 V1 |
| Route | `GET /setup/summary`, `GET /setup` (redirect), `GET /` (redirect) |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Summary · default |
| Tab Order | 1: Summary · 2: AWS · 3: GitHub · 4: Repositories · 5: Projects · 6: Settings |
| Description | First screen in the Marina setup flow. Configuration checklist with inline-editable fields and live health checks for AWS and GitHub. Default landing screen for the application. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/summary, GET /setup, GET / |

## Layout

Single-column, max-width 900px, centered. Two `mn-card` sections: CHECKLIST and SCAN STATUS.

```
┌────────────────────────────────────────────────────────────┐
│                  ⚓  Marina                                  │
│   ⚠ Complete setup to activate cloud sync                  │
├────────────────────────────────────────────────────────────┤
│  🟢 CHECKLIST                                              │
│  ──────────────────────────────────────────────────────── │
│  ✅  Application Name     [Marina                        ▏]│
│  ✅  User Email           [ed@example.com               ▏]│
│  ⚠️   User Cell Phone     [(not set)                    ▏]│
│  ✅  AWS Profile          [default                      ▏]│
│  ✅  AWS Region           us-east-1                       │
│  ❌  Marina Org           [(not set)                    ▏]│
│  ⚠️   Marina API Endpoint  (not deployed)                  │
│  ✅  AWS IAM Reachable    arn:aws:iam::111:user/ed         │
│  ❌  GitHub Username      [(not set)                    ▏]│
│  ❌  GitHub Auth          Not authenticated               │
│  ❌  GitHub SSH           No key found                    │
│  ✅  Projects Directory   /home/ed/projects               │
├────────────────────────────────────────────────────────────┤
│  📡  SCAN STATUS                                           │
│  ──────────────────────────────────────────────────────── │
│  📌  Projects in GitHub Repo    42                         │
│  📌  Projects Downloaded        18                         │
│       ✅  Active                 9                         │
│       ⚠️   Prototype              6                         │
│       📌  Archived               3                         │
│  📌  Projects NOT Downloaded    24                         │
│  📌  Catalog Last Published      2026-05-29 06:05           │
└────────────────────────────────────────────────────────────┘
```

## Welcome Banner

Full-width hero. Dark surface (`--mn-nav-bg`). Centered text.

- Headline: current value of `app_name` (32px bold teal accent). Updates in-place on save.
- Subheadline: `Configure Marina before proceeding.` (muted 16px) — shown only when any critical field is ❌.

## Setup Required Banner

Amber banner shown below the sub-bar when any **critical** field is ❌. Critical fields: `marina_org`, `github_username`, GitHub Auth.

```
┌──────────────────────────────────────────────────────────────┐
│  ⚠  Setup incomplete — AWS sync and GitHub features will not │
│     function until all critical items are configured.        │
└──────────────────────────────────────────────────────────────┘
```

Banner is dismissed automatically (server fragment update) when all critical fields reach ✅.

## CHECKLIST Card

Table columns: **Icon**, **Key**, **Value**, **Description**.

**Editability rule:** Settings-backed fields show an always-visible `<input>`. Env-backed and computed fields are plain text (no input affordance).

| # | Item | Key | Editable | Status Logic | Description column |
|---|------|-----|----------|-------------|-------------------|
| 1 | Application Name | `app_name` (settings) | Yes | ✅ if non-empty | Name shown in the nav brand |
| 2 | User Email | `user_email` (settings) | Yes | ✅ if valid email; ⚠️ if empty | Used for alert notifications |
| 3 | User Cell Phone | `user_cell` (settings) | Yes | ✅ if set; ⚠️ if empty | SMS alerts (optional) |
| 4 | AWS Profile | `aws_profile` (settings) | Yes | ✅ if non-empty | AWS credentials profile name (default: `default`) |
| 5 | AWS Region | `AWS_REGION` (env) | No | ✅ if set; ⚠️ if using default | Set `AWS_REGION` in `.env` |
| 6 | Marina Org | `marina_org` (settings) | Yes | ✅ if non-empty; ❌ if empty | DynamoDB partition key — your organisation slug |
| 7 | Marina API Endpoint | `MARINA_API_URL` (env) | No | ✅ if valid HTTPS URL; ⚠️ if empty | Set after Terraform deploy (`MARINA_API_URL` in `.env`). Configure on the AWS tab. |
| 8 | AWS IAM Reachable | runtime check | No | ✅ if `aws sts get-caller-identity` exits 0; ❌ if not | Shows calling ARN on success. Configure on the AWS tab. |
| 9 | GitHub Username | `github_username` (settings) | Yes | ✅ if non-empty; ❌ if empty | Your GitHub account name |
| 10 | GitHub Auth | runtime check (`gh auth status`) | No | ✅ if exits 0; ❌ if not | Run `gh auth login` in a terminal. Configure on the GitHub tab. |
| 11 | GitHub SSH | runtime check (`ssh -T git@github.com`) | No | ✅ if exits 1 (authed); ❌ if exits 255 | Required for private repo cloning. Configure on the GitHub tab. |
| 12 | Projects Directory | `PROJECTS_DIR` (env) | No | ✅ if path exists; ❌ if missing | Set `PROJECTS_DIR` in `.env` |

When GitHub Auth is ❌, inline help: `Run gh auth login in a terminal, then reload this page.`

When AWS IAM is ❌, inline help: `Configure AWS credentials — go to the AWS tab.`

When Marina Org is ❌, inline help: `Enter an organisation slug — used as the DynamoDB partition key (e.g. acme).`

## SCAN STATUS Card

Read-only informational card. All rows 📌. Data populated at startup and after manual rescans.

| # | Item | Source |
|---|------|--------|
| 1 | Projects in GitHub Repo | `platform_stats.github_repo_count` |
| 2 | Projects Downloaded | Count of directories in `PROJECTS_DIR` with `METADATA.md` |
| 3–N | Projects by status | One row per distinct `status` value |
| N+1 | Projects NOT Downloaded | `github_repo_count` − downloaded count |
| N+2 | Catalog Last Published | `platform_stats.catalog_last_published` — `—` if never published |

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/setup/config` | `key`, `value` | Icon fragment + banner fragment |
| GET | `/api/setup/health` | — | JSON: `{ aws: bool, github_auth: bool, github_ssh: bool }` |

Allowed `key` values for `/api/setup/config`: `app_name`, `user_email`, `user_cell`, `aws_profile`, `marina_org`, `github_username`. Any other key returns 400.

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (all config keys) | `settings` table via `/api/setup/config` |
| `user_profile` table (`email`, `cell_phone`) | `user_profile` table via `/api/setup/config` |
| `PROJECTS_DIR`, `MARINA_API_URL`, `AWS_REGION` (env) | None |
| `platform_stats` table | None |
| `aws sts get-caller-identity` exit code | None |
| `gh auth status` exit code | None |
| `ssh -T git@github.com` exit code | None |

## Open Questions

- Should the checklist run health checks on page load or only when the user clicks Refresh? V1: run on page load; add a Refresh button for manual re-check.
- Should `user_cell` validation enforce a format (E.164)? V1: store as-entered; validate format at alert send time.
