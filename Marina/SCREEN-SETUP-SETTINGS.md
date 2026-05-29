# Screen: Setup — Settings

| Field | Value |
|-------|-------|
| Version | 20260529 V1 |
| Route | `GET /setup/settings`, `POST /setup/settings` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Settings |
| Tab Order | 1: Summary · 2: AWS · 3: GitHub · 4: Repositories · 5: Projects · 6: Settings |
| Description | Application-level configuration and user alert profile. Application name, theme, and user contact information for alert notifications. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/settings, POST /setup/settings |

## Layout

Single-column, max-width 600px, centered. Two `mn-card` sections: Application and Alert Profile.

```
┌──────────────────────────────────────────────────────────────┐
│  APPLICATION                                                 │
│  ──────────────────────────────────────────────────────── │
│  Application Name                                            │
│  [ Marina                                                  ] │
│  The name displayed in the nav brand (⚓ Marina)             │
│                                                              │
│  Theme                                                       │
│  ( ) Light  (●) Dark                                         │
│  [ROADMAP] Requires restart until settings-backed.          │
├──────────────────────────────────────────────────────────────┤
│  ALERT PROFILE                                               │
│  ──────────────────────────────────────────────────────── │
│  Email Address                                               │
│  [ ed@example.com                                          ] │
│  Receives alert notifications from Marina cloud triggers.    │
│                                                              │
│  Cell Phone (optional)                                       │
│  [ +1-555-555-5555                                         ] │
│  SMS alerts for critical events. Leave blank to disable SMS. │
│  Format: E.164 (e.g. +15555555555) or national (555-555-5555)│
│                                                              │
│  [Save Settings]  [Cancel]                                   │
└──────────────────────────────────────────────────────────────┘
```

## Fields

| Field | Key | Type | Default | Description |
|-------|-----|------|---------|-------------|
| Application Name | `app_name` (settings) | Text | `Marina` | Name shown in the nav brand label |
| Theme | `app_theme` (settings) | Radio: light/dark | `light` | UI colour scheme. Currently applied via `MARINA_THEME` in `.env`; this field writes it to the `settings` table. Requires restart until settings-backed rendering is implemented. |
| Email Address | `user_email` (user_profile) | Email | `` | Alert notification email address |
| Cell Phone | `user_cell` (user_profile) | Text | `` | SMS alert phone number. Optional. |

All fields are populated from the database on page load. Saving an empty field stores an empty string (not NULL).

## Validation

| Field | Rule |
|-------|------|
| `user_email` | If non-empty, must contain `@`. Server rejects obviously malformed addresses. Client-side warning before submit. |
| `user_cell` | Accepted formats: E.164 (`+15555555555`) or common national formats (stripped and normalised to E.164 on save). |
| `app_name` | Non-empty. Server rejects blank names. |

## Buttons

| Button | Behaviour |
|--------|-----------|
| `Save Settings` (primary) | `POST /setup/settings` with all field values. On success: flashes "Settings saved." and updates the nav brand label in place (no page reload). |
| `Cancel` (outline) | Navigates back (browser history); no writes. |

## Effect of Settings

| Key | Where used |
|-----|-----------|
| `app_name` | Nav brand label (`⚓ {app_name}`) — updates immediately on save |
| `app_theme` | UI colour scheme — requires restart until live switching is implemented |
| `user_email` | Alert Lambda functions and any future notification pipelines |
| `user_cell` | SMS alert functions (Phase 2 notification pipeline) |

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (`app_name`, `app_theme`) | `settings` table (UPDATE value WHERE key = ?) |
| `user_profile` table (`email`, `cell_phone`) | `user_profile` table (UPDATE on save) |

## Open Questions

- Should additional settings (polling interval, scan schedule) be editable here or remain in `.env`? Path-level settings stay `.env`-only. Operational settings (notification schedule, alert thresholds) belong here in V2.
- Should `app_name` changes take effect immediately in the nav without a page reload? Yes — server reads `settings` on each request. No restart required.
