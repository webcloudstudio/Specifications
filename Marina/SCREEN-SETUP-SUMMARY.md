# Screen: Setup — Summary

| Field | Value |
|-------|-------|
| Version | 20260602 V3 |
| Route | `GET /setup/summary`, `GET /setup` (redirect), `GET /` (redirect) |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Summary · default |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Marina setup overview. One row per tab showing each tab's final acceptance criteria. Default landing screen for the application. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/summary, GET /setup, GET / |

## Layout

Single-column, max-width 900px, centered. Page header followed by an optional amber Setup Required Banner, then one `mn-card`: SETUP STATUS.

```
┌────────────────────────────────────────────────────────────┐
│  🏠 Marina                    Marina setup overview.        │
│  (dark header — see UI-GENERAL Page Header)                │
├────────────────────────────────────────────────────────────┤
│  ⚠ Setup incomplete — configure all items before          │  ← amber, conditional
│    proceeding to cloud sync.                               │
├────────────────────────────────────────────────────────────┤
│  SETUP STATUS                                              │
│  ──────────────────────────────────────────────────────── │
│  [AWS icon]  ✅  AWS               Identity confirmed      │
│              → Go to AWS                                   │
│  [TF icon]   ❌  Terraform         Not deployed            │
│              AWS environment not yet configured.           │
│              → Go to Terraform                             │
│  [GH icon]   ✅  GitHub            Connected               │
│              → Go to GitHub                                │
│  [scan icon] ⚠️  Git Scan          Never scanned           │
│              → Go to Git Scan                              │
│  [dir icon]  ❌  Projects Dir      Not set                 │
│              [ /home/ed/projects           ] [Save to .env]│
│  [KB icon]   ✅  Repositories      12 available            │
│              → Go to Repositories                          │
│  [⚙ icon]   ✅  Settings          Configured              │
│              → Go to Settings                              │
└────────────────────────────────────────────────────────────┘
```

## Page Header

Standard page header per UI-GENERAL. Icon: `bi-house-fill`. Title: `Marina` (no sub-page suffix). Description block (right): `Marina setup overview.`

## Setup Required Banner

Amber banner shown below the page header when any **critical** row is ❌. Critical rows: AWS, GitHub, Projects Directory. The banner is dismissed automatically when all critical rows reach ✅.

```
⚠  Setup incomplete — configure all items to activate cloud sync and GitHub features.
```

## SETUP STATUS Card

One row per tab (excluding Summary). Table columns: **Icon**, **Status Icon**, **Tab Name**, **Status Text**, **Detail / Action**.

### Row Definitions

Each row shows the aggregate acceptance criteria for that tab. A row is ✅ only when all its criteria are met; ⚠️ when partially configured; ❌ when the minimum required state is not met.

| # | Tab | Icon | Row Label | ✅ when | ⚠️ when | ❌ when |
|---|-----|------|-----------|---------|---------|--------|
| 1 | AWS | Simple Icons `amazonaws` | AWS | `platform_stats.python_aws_ok = 1` AND `aws_profile` set | `aws_profile` set but connectivity not tested | `aws_profile` empty or IAM unreachable |
| 2 | Terraform | Simple Icons `terraform` | Terraform | `MARINA_API_URL` set AND endpoint reachable (200 response) | `MARINA_API_URL` set but endpoint not responding | Not deployed — `MARINA_API_URL` not set |
| 3 | GitHub | `bi-github` | GitHub | `github_username` set AND `gh auth status` ✅ AND SSH ✅ | `github_username` set but auth or SSH ❌ | `github_username` not set |
| 4 | Git Scan | `bi-arrow-clockwise` | Git Scan | `platform_stats.last_scan` set AND `github_repo_count > 0` | Scanned but `github_repo_count = 0` | Never scanned |
| 5 | Projects | `bi-kanban` | Projects Dir | `PROJECTS_DIR` set AND path exists | `PROJECTS_DIR` set but path not found | `PROJECTS_DIR` not set |
| 6 | Repositories | `bi-folder2-open` | Repositories | ≥1 repo with `is_downloaded = 1` | `github_repos` populated but none downloaded | `github_repos` empty or GitHub not configured |
| 7 | Settings | `bi-sliders2` | Settings | `app_name` non-empty AND `user_email` non-empty | `app_name` set but `user_email` empty | `app_name` empty |

### Row Layout

Each row is two lines:
- **Line 1:** `{icon}  {status-icon}  {Tab Name}    {Status Text}` — right edge: `→ Go to {Tab}` link (navigates to that tab's route)
- **Line 2:** Detail text (muted, indented). Shown only when ❌ or ⚠️. For Projects Dir: replaces line 2 with the editable field (see below).

The `→ Go to {Tab}` link is always shown (even ✅ rows) to allow easy navigation.

### Terraform Row — "AWS Environment Configured"

The Terraform row label on the Summary screen is displayed as **"AWS Environment Configured"** to communicate its meaning to a non-technical user. The link still reads `→ Go to Terraform`.

Status text examples:
- ✅ `Endpoint reachable — https://abc123.execute-api.us-east-1.amazonaws.com`
- ⚠️ `MARINA_API_URL set but endpoint not responding`
- ❌ `Not deployed — run Terraform to provision the AWS plane`

### Projects Dir Row — Editable .env Field

The Projects Dir row is the only row with an inline editable field. When PROJECTS_DIR is ❌ or ⚠️:

```
[icon]  ❌  Projects Dir     Not set
            [ /home/ed/projects                        ]  [Save to .env]
            ⚠ Saving writes PROJECTS_DIR to .env — Marina restart required.
```

`[Save to .env]` button class: `btn-mn-caution` (amber — writes to .env, requires restart).

On save: `POST /api/setup/env` with `key=PROJECTS_DIR&value={path}`. Server writes the value to `.env` and returns a ⚠️ inline notice: `Saved to .env — restart Marina for the change to take effect.`

The field is always shown on this row (not just when ❌) so the user can update PROJECTS_DIR without navigating to another tab.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/api/setup/summary/status` | — | JSON: `{ rows: [{ tab, status, text, detail }] }` |
| POST | `/api/setup/env` | `key`, `value` | Confirmation fragment with restart notice |

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (`aws_profile`, `github_username`, `app_name`, `marina_org`) | `.env` file via `/api/setup/env` (Projects Dir save only) |
| `platform_stats` (`python_aws_ok`, `last_scan`, `github_repo_count`) | None |
| `PROJECTS_DIR`, `MARINA_API_URL` (env) | None |
| `github_repos` table (`is_downloaded` count) | None |
| `user_profile` table (`email`) | None |
| `gh auth status`, `ssh -T git@github.com` exit codes | None |
| HTTP GET `MARINA_API_URL` (endpoint reachability ping) | None |

## Open Questions

- Should the summary auto-refresh status rows on a timer, or only on page load? V1: page load only; add a `[↻ Refresh All]` button for manual re-check.
- Should the Terraform endpoint reachability check have a timeout? V1: 5-second timeout; show ⚠️ `Timeout` if exceeded.
