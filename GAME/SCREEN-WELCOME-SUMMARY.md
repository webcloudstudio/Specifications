# Screen: Welcome — Summary

| Field | Value |
|-------|-------|
| Version | 20260510 V5 |
| Route | `GET /welcome/summary`, `GET /welcome` (redirect) |
| Parent | — |
| Main Menu | Welcome |
| Sub Menu | Summary · default |
| Tab Order | 1: Summary · 2: GitHub · 3: Projects |
| Description | First screen in the new-user onboarding flow. Configure core settings here before using the GitHub or Projects tabs. Inline-editable configuration overview and health check. Default landing screen for the application. |
| Depends On  | UI-GENERAL.md |
| Provides    | GET /welcome/summary, GET /welcome |

## Layout

Single-column, max-width 900px, centered. Settings-backed fields are inline-editable in the Value column; env-backed and computed fields are read-only.

```
┌────────────────────────────────────────────┐
│           ██ My Prototyper ██              │
│   ⚠ Complete setup to use GitHub & Projects │
├────────────────────────────────────────────┤
│  🟢 CHECKLIST                              │
│  ─────────────────────────────────────────│
│  ✅ Application Name      [My Prototyper ▏]│
│  ✅ Application Version   2026-03-20.1     │
│  ✅ Projects Directory    /home/user/...   │
│  ⚠️  Specifications Path  (default)        │
│  ⚠️  Homepage URL         [(not set)      ▏]│
│  ❌ GitHub Username       [(not set)      ▏]│
│  ❌ GitHub Auth           Not authenticated│
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

## Setup Required Banner

A prominent amber banner is shown at the top of the page content area (below the tab bar) when any **critical** field is missing or in ❌ state. Critical fields are: `PROJECTS_DIR`, `github_username`, GitHub Auth.

```
┌─────────────────────────────────────────────────────────┐
│  ⚠  Setup required — the GitHub and Projects tabs        │
│     will not function until the items below are          │
│     configured. See the checklist for details.           │
└─────────────────────────────────────────────────────────┘
```

This banner is dismissed automatically when all critical fields reach ✅ state (no page reload required — server-side fragment update after each save).

## CHECKLIST Card

Highlighted `cc-card`. Table columns: **Icon**, **Key**, **Value**, **Description**.

**Editability rule:** The Value cell is inline-editable only for settings-backed fields (`app_name`, `homepage_url`). All other rows are read-only — the Value cell is plain text with no input affordance.

Editable Value cells contain a standard `<input>` (1px solid `var(--cc-border)`, 4px radius, white background, 4px 8px padding) — always visibly styled as a text box, not hidden until clicked. On focus the border becomes `2px solid #0073ea`. Tabbing out or losing focus triggers a `POST /api/welcome/config` with `key` and `value`. The server validates and returns an updated icon fragment; the icon updates in-place without a page reload.

**Save feedback:** After every save attempt, a toast notification appears fixed top-right (green background, white text, 8px radius, z-index 1000). On success: "✓ Saved". On error: "✗ Failed — try again". The toast fades out after 2 seconds. The fetch must handle non-2xx responses and network errors, both showing the error toast.

| Icon | Meaning |
|------|---------|
| ✅ | Configured and accessible |
| ⚠️ | Set but may need attention |
| ❌ | Missing or inaccessible |
| 📌 | Informational |

| # | Item | Key | Description column text | Status logic | Value Editable |
|---|------|-----|------------------------|-------------|----------------|
| 1 | Application Name | `app_name` (settings) | The name of this installation | ✅ if custom; ⚠️ if still default `Command Center` | **Yes** |
| 2 | Application Version | `version` (METADATA.md) | Version of this installation | 📌 always shown | No — read from METADATA.md |
| 3 | Projects Directory | `PROJECTS_DIR` (env) | Folder containing your managed projects. Set `PROJECTS_DIR` in `.env` to override (.env) | ✅ if path exists; ❌ if missing | No — env var, restart required |
| 4 | Specifications Path | `SPECIFICATIONS_PATH` (env) | Folder containing specification files. Set `SPECIFICATIONS_PATH` in `.env` to override (.env) | ✅ if path exists; ⚠️ if using default | No — env var, restart required |
| 5 | Homepage URL | `homepage_url` (settings) | Your public portfolio URL | ✅ if valid `https://` URL; ⚠️ if empty | **Yes** |
| 6 | GitHub Username | `github_username` (settings) | Your GitHub account name. Used to identify your repos on the GitHub tab. | ✅ if non-empty; ❌ if empty | **Yes** |
| 7 | GitHub Auth | runtime check (`gh auth status`) | GitHub CLI authentication status. Run `gh auth login` in a terminal to authenticate. | ✅ if `gh auth status` exits 0 (shows authed user); ❌ if not authenticated | No — run `gh auth login` in terminal |
| 8 | GitHub SSH | runtime check | GitHub SSH connectivity for cloning private repos. | ✅ if `ssh -T git@github.com` exits 1 (authed); ❌ if exits 255 | No — not configurable here |

When GitHub Auth is ❌, an inline help block shows: `Run gh auth login in a terminal, then reload this page.`

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
| POST | `/api/welcome/config` | `key`, `value` | Icon HTML fragment (`✅` / `⚠️` / `❌`) for the updated row + updated banner headline if `key` is `app_name` + updated setup-required banner fragment |

Allowed keys: `app_name`, `homepage_url`, `github_username`. Any other key returns 400.

The response also includes a `setup_required` boolean in the JSON so the client can show or hide the Setup Required Banner without a page reload.

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (`app_name`, `homepage_url`, `github_username`) | `settings` table (`app_name`, `homepage_url`, `github_username`) via `/api/welcome/config` |
| `PROJECTS_DIR`, `SPECIFICATIONS_PATH` (env) | None |
| `version` from METADATA.md | None |
| `platform_stats` table (`github_repo_count`, `scan_projects_total`, `projects_by_state_*`, `scan_last_completed`) | None |
| `gh auth status` exit code | None |
| `ssh -T git@github.com` exit code | None |

## Open Questions
- None.
