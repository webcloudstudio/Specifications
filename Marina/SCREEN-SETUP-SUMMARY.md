# Screen: Setup — Summary

| Field | Value |
|-------|-------|
| Version | 20260602 V5 |
| Header Background | `mn-hdr-bg--summary` |
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
│  [KPI left]          ⚓  Marina          [spacer right]    │
│  (dark header — see UI-GENERAL Page Header)                │
├────────────────────────────────────────────────────────────┤
│  ⚠ Setup incomplete — configure all items before          │  ← amber, conditional
│    proceeding to cloud sync.                               │
├────────────────────────────────────────────────────────────┤
│  SETUP STATUS                                              │
│  ──────────────────────────────────────────────────────── │
│  [AWS icon]  ✅  AWS               Identity confirmed      │
│  [TF icon]   ❌  Terraform         Not deployed            │
│              Not deployed — run Terraform to provision.    │
│  [GH icon]   ✅  GitHub            Connected               │
│  [scan icon] ⚠️  Git Scan          Never scanned           │
│  [dir icon]  ❌  Projects Dir      Not set                 │
│              [ /home/ed/projects                        ]  │
│  [KB icon]   ✅  Repositories      12 available            │
│  [⚙ icon]   ✅  Settings          Configured              │
└────────────────────────────────────────────────────────────┘
```

## Header KPIs

Left column of the page header. Component type: **All-Good Indicator** (`mn-hdr-allgood`).

| State | Display | Condition |
|-------|---------|-----------|
| ✅ | `bi-check-circle-fill` + "All systems ready" (teal) | All 7 tab rows are ✅ |
| ⚠️ | `bi-exclamation-triangle-fill` + "N items need attention" (amber) | Any row is ⚠️ but none are ❌ |
| ❌ | `bi-exclamation-triangle-fill` + "N items need attention" (red) | Any row is ❌ |

N = count of rows that are ❌ or ⚠️. Updated via HTMX on page load and on `[↻ Refresh All]`.

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
- **Line 1:** `{icon}  {status-icon}  {Tab Name}    {Status Text}`
- **Line 2:** Detail text (muted, indented). Shown only when ❌ or ⚠️. For Projects Dir: replaces line 2 with the editable field (see below).

No "→ Go to {Tab}" link — navigation is handled by the sub-tab bar. Do not add per-row navigation links.

### Terraform Row

The Terraform row label is **"Terraform"**, matching the sub-tab name exactly.

Status text examples:
- ✅ `Endpoint reachable — https://abc123.execute-api.us-east-1.amazonaws.com`
- ⚠️ `MARINA_API_URL set but endpoint not responding`
- ❌ `Not deployed — run Terraform to provision the AWS plane`

### Projects Dir Row — Inline Editable Field

The Projects Dir row shows an always-visible inline-editable text input (no separate save button). It follows the standard Inline-Editable Fields pattern from UI-GENERAL: tab-out or blur triggers `POST /api/setup/config`.

```
[icon]  ❌  Projects Dir     Not set
            [ /home/ed/projects                        ]
```

On blur: `POST /api/setup/config` with `key=PROJECTS_DIR&value={path}`. Server writes the value and returns a toast notification. The field is always shown on this row so the user can update PROJECTS_DIR without navigating to another tab.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/api/setup/summary/status` | — | JSON: `{ rows: [{ tab, status, text, detail }] }` |
| POST | `/api/setup/config` | `key`, `value` | Toast fragment (Projects Dir inline save) |

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (`aws_profile`, `github_username`, `app_name`, `marina_org`) | `settings` table via `/api/setup/config` (Projects Dir inline save) |
| `platform_stats` (`python_aws_ok`, `last_scan`, `github_repo_count`) | None |
| `PROJECTS_DIR`, `MARINA_API_URL` (env) | None |
| `github_repos` table (`is_downloaded` count) | None |
| `user_profile` table (`email`) | None |
| `gh auth status`, `ssh -T git@github.com` exit codes | None |
| HTTP GET `MARINA_API_URL` (endpoint reachability ping) | None |

## Open Questions

- Should the summary auto-refresh status rows on a timer, or only on page load? V1: page load only; add a `[↻ Refresh All]` button for manual re-check.
- Should the Terraform endpoint reachability check have a timeout? V1: 5-second timeout; show ⚠️ `Timeout` if exceeded.
