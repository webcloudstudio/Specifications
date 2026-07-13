# Screen: Setup — Summary

| Field | Value |
|-------|-------|
| Version | 20260603 V7 |
| Header Background | `mn-hdr-bg--summary` |
| Header Help Text | Marina setup overview. |
| Route | `GET /setup/summary`, `GET /setup` (redirect), `GET /` (redirect) |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Summary · default |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Marina welcome and registration overview. Guides the user from local directory setup through repository discovery and project registration. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/summary, GET /setup, GET / |

## Layout

Single-column, max-width 900px, centered. Page header followed by an optional amber Setup Required Banner, then one `mn-card`: SETUP STATUS.

```
┌────────────────────────────────────────────────────────────┐
│  [KPI left]          ⚓  Marina          [spacer right]    │
│  (dark header — see UI-GENERAL Page Header)                │
├────────────────────────────────────────────────────────────┤
│  Welcome to Marina — register repositories, discover their │
│  capabilities, and explore your projects.                 │
├────────────────────────────────────────────────────────────┤
│  GET STARTED                                               │
│  ──────────────────────────────────────────────────────── │
│  1  Projects Directory       [ Configure ]                │
│  2  Discover Local Projects  [ Discover ]                 │
│  3  Repository Sources       [ Configure ]                │
│  4  Available Repositories   [ View ]                     │
│  5  Managed Projects         [ Explore ]                  │
│  6  Capabilities             [ Explore ]                  │
└────────────────────────────────────────────────────────────┘
```

## Welcome State

The first visit explains Marina in one sentence and presents the shortest useful path:

1. Set or confirm `PROJECTS_DIR`.
2. Discover existing local git repositories.
3. Optionally configure GitHub sources and clone repositories.
4. Review repository identity and register selected projects.
5. Open the Project Explorer and capability catalog.

Cloud/AWS setup is secondary and must not block local registration, discovery, or exploration.

## Header KPIs

Left column of the page header. Component type: **All-Good Indicator** (`mn-hdr-allgood`).

| State | Display | Condition |
|-------|---------|-----------|
| ✅ | `bi-check-circle-fill` + "Projects ready" (teal) | Directory configured and at least one managed project |
| ⚠️ | `bi-exclamation-triangle-fill` + "Registration in progress" (amber) | Candidates exist but registration is incomplete |
| ❌ | `bi-exclamation-triangle-fill` + "Start by choosing Projects Directory" (red) | Directory is not configured |

N = count of rows that are ❌ or ⚠️. Updated via HTMX on page load and on `[↻ Refresh All]`.

## Page Header

Standard page header per UI-GENERAL. Icon: `bi-house-fill`. Title: `Marina` (no sub-page suffix). Description block (right): `Marina setup overview.`

## Setup Required Banner

Amber banner shown below the page header when any **critical** row is ❌. Critical rows: AWS, GitHub, Projects Directory. The banner is dismissed automatically when all critical rows reach ✅.

```
⚠  Setup incomplete — configure all items to activate cloud sync and GitHub features.
```

## GET STARTED Card

One row per tab (excluding Summary). Table columns: **Icon**, **Status Icon**, **Tab Name**, **Status Text**, **Detail / Action**.

### Row Definitions

Each row is an onboarding action or project capability. Cloud and Terraform status may be shown in a
secondary Integration Status card but do not gate the initial local product.

| # | Step | Row Label | ✅ when | ⚠️ when | ❌ when |
|---|-----|------|-----------|---------|---------|--------|
| 1 | Projects Directory | `PROJECTS_DIR` exists and is readable | Path configured but unreadable | Not configured |
| 2 | Local Discovery | At least one repository candidate scanned | Scan complete with zero candidates | Never scanned or scan failed |
| 3 | Repository Sources | GitHub/source configuration is available | Sources configured but unavailable | No source configured; local discovery remains available |
| 4 | Registration | At least one project is managed | Candidates await registration | No candidates |
| 5 | Explorer | Project Explorer has current discovery data | Data is stale or warnings exist | No managed projects |

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
| `settings` table (`app_name`, `marina_org`) | `settings` table via `/api/setup/config` (Projects Dir inline save) |
| `platform_stats` (`last_scan`, `github_repo_count`) | None |
| `PROJECTS_DIR`, `MARINA_API_URL` (env) | None |
| `github_repos` table (`is_downloaded` count) | None |
| `user_profile` table (`email`) | None |
| `gh auth status`, `ssh -T git@github.com` exit codes | None |
| HTTP GET `MARINA_API_URL` (endpoint reachability ping) | None |

## Open Questions

- Should the summary auto-refresh status rows on a timer, or only on page load? V1: page load only; add a `[↻ Refresh All]` button for manual re-check.
- Should the Terraform endpoint reachability check have a timeout? V1: 5-second timeout; show ⚠️ `Timeout` if exceeded.
