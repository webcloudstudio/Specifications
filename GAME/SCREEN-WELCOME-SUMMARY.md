# Screen: Welcome — Summary

| Field | Value |
|-------|-------|
| Version | 20260426 V2 |
| Route | `GET /welcome/summary`, `GET /welcome` (redirect) |
| Parent | — |
| Main Menu | Welcome |
| Sub Menu | Summary · default |
| Tab Order | 1: Summary · 2: Prototypes · 3: Projects |
| Description | Inline-editable configuration overview and health check. Default landing screen for the application. |
| Depends On  | UI-GENERAL.md |

## Layout

Single-column, max-width 900px, centered. Settings-backed fields are inline-editable; env-backed fields require `.env` editing.

```
┌────────────────────────────────────────────┐
│           ██ YOUR COMMAND CENTER ██        │
│   Please set up the system before proceeding. │
├────────────────────────────────────────────┤
│  🟢 START HERE                             │
│  ─────────────────────────────────────────│
│  ✅ Application Name      [My Prototyper ▏]  │
│  ✅ Projects Directory    /home/user/...   │
│  ⚠️  Specifications Path  (default)        │
│  📌 Startup Scan          12 Projects, 4 Prototypes │
│  ⚠️  Homepage URL         [(not set)      ▏]│
│  ❌ GitHub SSH            No key found     │
└────────────────────────────────────────────┘
```

## Welcome Banner

Full-width hero. Dark surface. Centered text: headline `Your Command Center` (32px bold accent) + subheadline `Please set up the system before proceeding.` (muted 16px). No actions.

## START HERE Card

Highlighted `cc-card`. Table columns: **Icon**, **Key**, **Value**, **Description**. The icon column reflects the current validity state.

Settings-backed fields (app_name, homepage_url) are inline-editable in the Value column:
- Clicking or tabbing into the value cell activates an `<input>` styled inline (no visible border until focused, cursor appears).
- Tabbing out or losing focus triggers a `POST /api/welcome/config` with `key` and `value`.
- The server validates the new value and returns an updated icon fragment; the icon updates in-place without a page reload.

Env-backed fields (PROJECTS_DIR, SPECIFICATIONS_PATH) and informational rows (Startup Scan, GitHub SSH) display the value as plain text in the Value column.

The Description column contains the human-friendly description followed by the environment variable or settings key name in parentheses — for example: `Directory where project specification files are stored (SPECIFICATIONS_PATH)` or `Your portfolio URL — the public homepage for your projects (HOME_PAGE_URL)`. Informational rows without a configurable key omit the parenthetical. Fix instructions for non-editable fields appear beneath the description text in muted style.

| Icon | Meaning |
|------|---------|
| ✅ | Configured and accessible |
| ⚠️ | Set but may need attention |
| ❌ | Missing or inaccessible |
| 📌 | Informational |

| # | Item | Key | Description column text | Status logic | Editable |
|---|------|-----|------------------------|-------------|---------|
| 1 | Application Name | `app_name` (settings) | Custom name for this installation (app_name) | ✅ if custom; ⚠️ if still default `Command Center` | Yes |
| 2 | Projects Directory | `PROJECTS_DIR` (env) | Root directory containing all your managed projects (PROJECTS_DIR) | ✅ if path exists; ❌ if missing | No — fix: Set in `.env`, restart |
| 3 | Specifications Path | `SPECIFICATIONS_PATH` (env) | Directory where project specification files are stored (SPECIFICATIONS_PATH) | ✅ if path exists; ⚠️ if using default | No — fix: Set in `.env` if default is wrong |
| 4 | Startup Scan | backend metric | Summary of projects and prototypes found at last startup | 📌 always shown | No |
| 5 | Homepage URL | `homepage_url` (settings) | Your portfolio URL — the public homepage for your projects (HOME_PAGE_URL) | ✅ if valid `https://` URL; ⚠️ if empty | Yes |
| 6 | GitHub SSH | runtime check | GitHub SSH key authenticated for read/write repository access | ✅ if `ssh -T git@github.com` exits 1 (authed); ❌ if exits 255 | No — fix: GitHub SSH key setup guide |

When SSH is ❌, a collapsible "Alternatives" block shows: HTTPS credential store, GitHub CLI (`gh auth login`). Collapsed when SSH is ✅.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/welcome/config` | `key`, `value` | Icon HTML fragment (`✅` / `⚠️`) for the updated row |

Allowed keys: `app_name`, `homepage_url`. Any other key returns 400.

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (`app_name`, `homepage_url`) | `settings` table (`app_name`, `homepage_url`) via `/api/welcome/config` |
| `PROJECTS_DIR`, `SPECIFICATIONS_PATH` (env) | None |
| Startup scan counts | None |
| `ssh -T git@github.com` exit code | None |

## Open Questions

- Should the SSH check run on page load or be an explicit "Check" button to avoid startup delay?
	No - Do the check on application startup and store it as a persistence
- Should Summary show the application version or last-restart timestamp?
