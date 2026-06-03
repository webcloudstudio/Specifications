# Screen: Setup — Settings

| Field | Value |
|-------|-------|
| Version | 20260603 V6 |
| Header Background | `mn-hdr-bg--settings` |
| Header Help Text | Configure application name, user email, and default settings. |
| Route | `GET /setup/settings` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Settings |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | All Marina configuration in one place: application settings, every .env variable, and the alert profile. All fields save on blur — no Save button. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/settings |

## Header KPIs

None. Left KPI column is an empty `<div>`.

## Layout

Single-column, max-width 700px, centered. Three `mn-card` sections: Application, Environment, Alert Profile.

```
┌──────────────────────────────────────────────────────────────┐
│  APPLICATION                                                 │
│  ─────────────────────────────────────────────────────────  │
│  Application Name                                            │
│  [ Marina                                                  ] │
│  Displayed in the nav brand (⚓ Marina).                     │
│                                                              │
│  Theme                                                       │
│  ( ) Light  (●) Dark                                         │
├──────────────────────────────────────────────────────────────┤
│  ENVIRONMENT                                                 │
│  ─────────────────────────────────────────────────────────  │
│  These variables are read from .env on startup. Editing here │
│  writes to the settings table, which takes priority over     │
│  .env. Variables marked ↺ require a Marina restart.         │
│                                                              │
│  PROJECTS_DIR                                                │
│  [ /home/ed/projects                                       ] │
│  Root directory scanned for GitHub-enabled projects.        │
│                                                              │
│  MARINA_API_URL                               ↺             │
│  [ https://abc123.execute-api.us-east-1.amazonaws.com     ] │
│  API Gateway endpoint. Set this after running Terraform.    │
│                                                              │
│  AWS_REGION                                   ↺             │
│  [ us-east-1                                               ] │
│  AWS region for boto3 and Terraform calls.                  │
│                                                              │
│  AWS_PROFILE                                  ↺             │
│  [ default                                                 ] │
│  Named AWS credentials profile (~/.aws/credentials).        │
│                                                              │
│  PORT                                         ↺             │
│  [ 8000                                                    ] │
│  Port Marina listens on. Requires restart to take effect.   │
├──────────────────────────────────────────────────────────────┤
│  ALERT PROFILE                                               │
│  ─────────────────────────────────────────────────────────  │
│  Email Address                                               │
│  [ ed@example.com                                          ] │
│  Alert notifications from Marina cloud triggers.            │
│                                                              │
│  Cell Phone (optional)                                       │
│  [ +1-555-555-5555                                         ] │
│  SMS alerts for critical events. Leave blank to disable.    │
│  Format: +15555555555 or 555-555-5555                        │
└──────────────────────────────────────────────────────────────┘
```

## Save Behaviour

Every field saves individually on blur (tab-out or click away). There is no Save button and no Cancel button.

On blur: `POST /api/setup/config` with `key` and `value`. Server writes to the `settings` table. The `settings` table takes priority over `.env` at runtime — no `.env` file is modified.

Toast notification on save:
- ✅ `{field label} saved.`
- ❌ `{field label}: {validation error}` (field re-focused)

For fields marked ↺ (restart required): after a successful save, an inline note appears below the field: `Marina restart required for this change to take effect.`

Theme toggle saves immediately on click (no blur needed).

## Fields

### APPLICATION Card

| Field | Key | Type | Default | Restart |
|-------|-----|------|---------|---------|
| Application Name | `app_name` (settings) | Text | `Marina` | No — nav brand updates live |
| Theme | `app_theme` (settings) | Toggle: light / dark | `dark` | No |

`app_name` change takes effect immediately: server reads `settings` on each request.

### ENVIRONMENT Card

All variables from the Marina `.env` file, sourced from `.env.sample`. Stored in the `settings` table under their exact env var name as the key.

| Variable | Key | Restart | Description |
|----------|-----|---------|-------------|
| `PROJECTS_DIR` | `PROJECTS_DIR` | No | Root path scanned for GitHub-enabled projects |
| `MARINA_API_URL` | `MARINA_API_URL` | Yes | API Gateway endpoint from Terraform output |
| `AWS_REGION` | `AWS_REGION` | Yes | AWS region for all boto3 and CLI calls |
| `AWS_PROFILE` | `AWS_PROFILE` | Yes | Named profile in `~/.aws/credentials` |
| `PORT` | `PORT` | Yes | Port Marina's Flask server listens on |

**Read priority:** Marina reads each variable from the `settings` table first; falls back to the `.env` file if the settings value is empty. This means values set here survive `.env` changes.

**Restart indicator (↺):** Shown as a small muted badge to the right of the field label for variables requiring restart. A restart note appears below the field after saving any ↺ variable.

**Empty fields:** An empty field means "use the `.env` value." Saving an empty value clears the settings-table override — the `.env` file value resumes.

### ALERT PROFILE Card

| Field | Key | Type | Restart |
|-------|-----|------|---------|
| Email Address | `user_email` (user_profile) | Email text | No |
| Cell Phone | `user_cell` (user_profile) | Text | No |

## Validation

| Field | Rule |
|-------|------|
| `app_name` | Non-empty. Server rejects blank. |
| `user_email` | If non-empty, must contain `@`. |
| `user_cell` | Normalised to E.164 on save. Accepts `+15555555555` or `555-555-5555`. |
| `PORT` | Integer 1024–65535. |
| `MARINA_API_URL` | If non-empty, must begin with `https://`. |
| `AWS_REGION` | If non-empty, must match `[a-z]{2}-[a-z]+-\d` (e.g. `us-east-1`). |

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/setup/settings` | — | Full page |
| POST | `/api/setup/config` | `key`, `value` | Toast fragment |

All fields share the single `/api/setup/config` endpoint. The `POST /setup/settings` form-submit endpoint is removed.

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (all keys) | `settings` table via `/api/setup/config` |
| `.env` file (fallback for empty settings keys) | None (`.env` is never written by this screen) |
| `user_profile` table (`email`, `cell_phone`) | `user_profile` table via `/api/setup/config` |

## Open Questions

- Should additional operational settings (scan schedule, alert thresholds, polling interval) appear here in V2? Yes — anything currently `.env`-only that needs operator control belongs here.
- Should there be a `[↺ Restart Marina]` button on this screen for convenience after changing ↺ fields? V2.
