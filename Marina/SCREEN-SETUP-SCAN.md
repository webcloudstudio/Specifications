# Screen: Setup — Scan

| Field | Value |
|-------|-------|
| Version | 20260601 V1 |
| Route | `GET /setup/scan` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Scan |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Scans GitHub and the local projects directory to reconcile what is available in the cloud vs what is on disk. Displays project counts by status and triggers a fresh sync. Unlocked after GitHub setup is complete. |
| Depends On | UI-GENERAL.md, SCREEN-SETUP-GITHUB.md |
| Provides | GET /setup/scan |

## Purpose

Consolidates the SCAN STATUS block (moved from `/setup/summary`) and the Fetch action (moved from `/setup/repositories`) into a dedicated screen. After a scan, `/setup/repositories` reflects the updated data. This screen is the single entry point for refreshing the GitHub repo list.

## Prerequisites

- GitHub must be configured (GitHub Auth ✅ and GitHub SSH ✅) — enforced by the setup gate.
- If unconfigured, a notice panel is shown with a link to `/setup/github`.

## Layout

Single-column, max-width 900px, centered. Two `mn-card` sections: Scan Control, Scan Status.

```
┌──────────────────────────────────────────────────────────────┐
│  🔍  SCAN CONTROL                                            │
│  ─────────────────────────────────────────────────────────  │
│  Fetches your GitHub repository list and reconciles it       │
│  with projects on disk in PROJECTS_DIR.                      │
│                                                              │
│  Last scan:  2026-05-29 06:05  (3 days ago)                 │
│                                  [🔄 Scan Now]              │
│                                                              │
│  ✅  Scan complete — 42 repositories found                   │
├──────────────────────────────────────────────────────────────┤
│  📡  SCAN STATUS                                             │
│  ─────────────────────────────────────────────────────────  │
│  📌  Projects in GitHub Repo        42                       │
│  📌  Projects Downloaded            18                       │
│       ✅  Active                     9                       │
│       ⚠️   Prototype                  6                       │
│       📌  Archived                   3                       │
│  📌  Projects NOT Downloaded        24                       │
│  📌  Catalog Last Published          2026-05-29 06:05        │
└──────────────────────────────────────────────────────────────┘
```

## SCAN CONTROL Card

| Element | Behaviour |
|---------|-----------|
| Last scan timestamp | Read from `platform_stats.last_scan`. Shows relative time alongside absolute. `—` if never scanned. |
| `[🔄 Scan Now]` | Calls `POST /api/repositories/sync`. Spinner while running. On completion: updates Last scan and refreshes the SCAN STATUS card inline via HTMX. |

The button is enabled at all times when GitHub is configured. Re-scanning is always safe.

## SCAN STATUS Card

Read-only informational card. Data sourced from `platform_stats` and `github_repos` tables, populated at startup and after a Scan. Identical content to the SCAN STATUS card that was on `/setup/summary` (moved here; removed from Summary).

| # | Item | Source |
|---|------|--------|
| 1 | Projects in GitHub Repo | `platform_stats.github_repo_count` |
| 2 | Projects Downloaded | Count of directories in `PROJECTS_DIR` with `METADATA.md` |
| 3–N | Projects by status | One row per distinct `status` value in `METADATA.md` files |
| N+1 | Projects NOT Downloaded | `github_repo_count` − downloaded count |
| N+2 | Catalog Last Published | `platform_stats.catalog_last_published` — `—` if never published |

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/repositories/sync` | — | Updated SCAN STATUS card HTML fragment |
| GET | `/api/setup/scan/status` | — | JSON: `{ last_scan, repo_count, downloaded_count, by_status, not_downloaded, last_published }` |

## Data Flow

| Reads | Writes |
|-------|--------|
| `platform_stats` table | `platform_stats.last_scan` (on sync) |
| `github_repos` table | `github_repos` table (upsert on sync) |
| `PROJECTS_DIR` (env) | None |
| `settings.github_username` | None |

## Open Questions

- Should a scheduled auto-scan run at Marina startup? V1: startup populates data if `github_repos` is empty; manual scan otherwise.
- Should scan results show a diff (new/removed repos since last scan)? V2.
