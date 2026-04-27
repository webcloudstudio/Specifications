# Screen: Welcome — Summary

| Field | Value |
|-------|-------|
| Version | 20260426 V3 |
| Route | `GET /welcome/summary`, `GET /welcome` (redirect) |
| Parent | — |
| Main Menu | Welcome |
| Sub Menu | Summary · default |
| Tab Order | 1: Summary · 2: Prototypes · 3: Projects |
| Description | Inline-editable configuration overview and health check. Default landing screen for the application. |
| Depends On  | UI-GENERAL.md |

## Layout

Single-column, max-width 900px, centered. Settings-backed fields are inline-editable in the Value column; env-backed and computed fields are read-only.

```
┌────────────────────────────────────────────┐
│           ██ My Prototyper ██              │
│   Please set up the system before proceeding. │
├────────────────────────────────────────────┤
│  🟢 CHECKLIST                              │
│  ─────────────────────────────────────────│
│  ✅ Application Name      [My Prototyper ▏]│
│  ✅ Application Version   2026-03-20.1     │
│  ✅ Projects Directory    /home/user/...   │
│  ⚠️  Specifications Path  (default)        │
│  ⚠️  Homepage URL         [(not set)      ▏]│
│  ❌ GitHub SSH            No key found     │
├────────────────────────────────────────────┤
│  📊 STARTUP SCAN                           │
│  ─────────────────────────────────────────│
│  📌 Projects in GitHub Repo   42           │
│  📌 Projects Downloaded       18           │
│      ✅ Active                 9           │
│      ⚠️  Prototype              6           │
│      📌 Archived               3           │
│  📌 Projects NOT Downloaded   24           │
└────────────────────────────────────────────┘
```

## Page Title

The HTML `<title>` and any visible page-level heading (outside the banner) use the `app_name` setting. Updates immediately when `app_name` is saved via `/api/welcome/config`.

## Welcome Banner

Full-width hero. Dark surface. Centered text.

- Headline: the current value of `app_name` (32px bold accent). Updates in-place when `app_name` is saved without a page reload.
- Subheadline: `Please set up the system before proceeding.` (muted 16px) — shown only when any checklist field is unset or in a warning/error state.

## CHECKLIST Card

Highlighted `cc-card`. Table columns: **Icon**, **Key**, **Value**, **Description**.

**Editability rule:** The Value cell is inline-editable only for settings-backed fields (`app_name`, `homepage_url`). All other rows are read-only — the Value cell is plain text with no input affordance.

Clicking or tabbing into an editable Value cell activates an `<input>` styled inline (no visible border until focused, cursor appears). Tabbing out or losing focus triggers a `POST /api/welcome/config` with `key` and `value`. The server validates and returns an updated icon fragment; the icon updates in-place without a page reload.

| Icon | Meaning |
|------|---------|
| ✅ | Configured and accessible |
| ⚠️ | Set but may need attention |
| ❌ | Missing or inaccessible |
| 📌 | Informational |

| # | Item | Key | Description column text | Status logic | Value Editable |
|---|------|-----|------------------------|-------------|----------------|
| 1 | Application Name | `app_name` (settings) | Custom display name for this installation | ✅ if custom; ⚠️ if still default `Command Center` | **Yes** |
| 2 | Application Version | `version` (METADATA.md) | Version of this installation | 📌 always shown | No — read from METADATA.md |
| 3 | Projects Directory | `PROJECTS_DIR` (env) | Directory containing your GitHub projects | ✅ if path exists; ❌ if missing | No — set in `.env`, restart |
| 4 | Specifications Path | `SPECIFICATIONS_PATH` (env) | Directory containing specification files | ✅ if path exists; ⚠️ if using default | No — set in `.env` if default is wrong |
| 5 | Homepage URL | `homepage_url` (settings) | Portfolio URL — the public homepage for your projects (`HOME_PAGE_URL`) | ✅ if valid `https://` URL; ⚠️ if empty | **Yes** |
| 6 | GitHub SSH | runtime check | GitHub SSH key status | ✅ if `ssh -T git@github.com` exits 1 (authed); ❌ if exits 255 | No — not configurable here |

When SSH is ❌, a collapsible "Alternatives" block shows: HTTPS credential store, GitHub CLI (`gh auth login`). Collapsed when SSH is ✅.

## STARTUP SCAN Card

Separate `cc-card` below CHECKLIST. All rows are read-only (📌 informational). Data is populated at application startup and stored in the database.

| # | Item | Source | Description |
|---|------|--------|-------------|
| 1 | Projects in GitHub Repo | `platform_stats.github_repo_count` | Total repos in the configured GitHub account; populated by startup scan via GitHub API |
| 2 | Projects Downloaded | `platform_stats.scan_projects_total` | Projects present in `PROJECTS_DIR` |
| 3 | Projects — `<State>` | `platform_stats.projects_by_state_*` | One row per distinct status value (Active, Prototype, Archived, etc.) |
| 4 | Projects NOT Downloaded | Derived: row 1 − row 2 | Projects found in GitHub but absent from `PROJECTS_DIR`; computed at render time |

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/welcome/config` | `key`, `value` | Icon HTML fragment (`✅` / `⚠️`) for the updated row + updated banner headline if `key` is `app_name` |

Allowed keys: `app_name`, `homepage_url`. Any other key returns 400.

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (`app_name`, `homepage_url`) | `settings` table (`app_name`, `homepage_url`) via `/api/welcome/config` |
| `PROJECTS_DIR`, `SPECIFICATIONS_PATH` (env) | None |
| `version` from METADATA.md | None |
| `platform_stats` table (`github_repo_count`, `scan_projects_total`, `projects_by_state_*`, `scan_last_completed`) | None |
| `ssh -T git@github.com` exit code | None |

## Open Questions
- None.
