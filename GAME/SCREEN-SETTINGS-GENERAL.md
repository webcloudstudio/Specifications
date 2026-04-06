# Screen: General Settings

**Version:** 20260326 V1
**Description:** Specification for the General Settings screen — application-level configuration

## Menu Navigation

`Settings / General`

## Route

```
GET  /settings/general
POST /settings/general
```

Sub-bar is active when any `/settings/*` route is loaded. General is the default sub-tab.

## Layout

Single-column centered form, max-width 600px. Card (`cc-card`) per logical group. Save and Cancel at the bottom.

```
┌─────────────────────────────────────────────────┐
│  General Settings                               │
│  ─────────────────────────────────────────────  │
│                                                 │
│  Application Name                               │
│  [ Command Center                             ] │
│  The name displayed in the upper-left corner    │
│                                                 │
│  Homepage URL                                   │
│  [ https://webcloudstudio.github.io           ] │
│  Your live homepage URL (shown on Homepage)     │
│                                                 │
│  [Save Settings]  [Cancel]                      │
└─────────────────────────────────────────────────┘
```

## Fields

| Field | Key | Type | Default | Description shown below field |
|-------|-----|------|---------|-------------------------------|
| Application Name | `app_name` | Text input | `Command Center` | The name displayed in the upper-left corner of the application |
| Homepage URL | `homepage_url` | URL input | `` | Your live homepage URL (shown on Homepage) |

Fields are populated from the `settings` table on page load. All values are optional — saving an empty field stores an empty string (not NULL).

## Buttons

| Button | Behaviour |
|--------|-----------|
| `Save Settings` (primary) | `POST /settings/general` with all field values; flashes "Settings saved." on success; page reloads |
| `Cancel` (outline) | Navigates back (browser history); no writes |

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (all keys) | `settings` table (UPDATE value WHERE key = ?) |

No full-page reload on save — HTMX `hx-post` replaces the form fragment; success flash rendered inline above the form.

## Effect of Settings

| Key | Where used |
|-----|-----------|
| `app_name` | Top-bar brand label (replaces `Command Center` / `cc-brand` text) |
| `homepage_url` | Homepage screen — live site link; shown next to the Publish button |

## Open Questions

- Should additional settings (polling interval, PROJECTS_DIR, SPECIFICATIONS_PATH) be editable here, or remain `.env`-only? Path-level settings (`PROJECTS_DIR`, `SPECIFICATIONS_PATH`) remain `.env`-only — changing them requires a restart and the risk of misconfiguration is high. Operational settings (polling interval, app branding) belong here.
- Should `app_name` changes take effect immediately? Yes — the server reads the `settings` table on each request for the brand label. No restart required.
