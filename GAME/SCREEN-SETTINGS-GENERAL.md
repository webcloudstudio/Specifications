# Screen: General Settings

| Field | Value |
|-------|-------|
| Version | 20260326 V1 |
| Route | `GET /settings/general`, `POST /settings/general` |
| Parent | — |
| Main Menu | Settings [right] |
| Sub Menu | General · default |
| Tab Order | 1: General · 2: Tags · 3: Voice · 4: Voice Docs · 5: Help |
| Description | Application-level configuration — app name, homepage URL, and theme. |

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
│  [ https://username.github.io                 ] │
│  Your GitHub Pages URL (e.g. https://user.github.io) │
│                                                 │
│  ── GitHub Pages Setup ──────────────────────  │
│  (shown only when homepage_url is empty)        │
│  GitHub Pages format:                           │
│    User/org site:    https://{username}.github.io       │
│    Project site:     https://{username}.github.io/{repo}│
│  To enable: go to your GitHub repo → Settings  │
│  → Pages → Source: Deploy from branch (main)   │
│                                                 │
│  [Save Settings]  [Cancel]                      │
└─────────────────────────────────────────────────┘
```

## Fields

| Field | Key | Type | Default | Description shown below field |
|-------|-----|------|---------|-------------------------------|
| Application Name | `app_name` | Text input | `Command Center` | The name displayed in the upper-left corner of the application |
| Homepage URL | `homepage_url` | URL input | `` (empty) | Your GitHub Pages URL — must start with `https://`. Shown on the Homepage screen. |
| [ROADMAP] Theme | `app_theme` | Select | `light` | `light` \| `dark`. Currently set via `GAME_THEME` in `.env`; this field will write it to the `settings` table and apply without restart. |

Fields are populated from the `settings` table on page load. All values are optional — saving an empty field stores an empty string (not NULL).

### GitHub Pages Setup Assistant

Shown inline below the Homepage URL field **only when `homepage_url` is empty or not a valid `https://` URL**. Static instructional block, no interactivity required.

Content:

> **GitHub Pages URL format**
> - User/org site: `https://{username}.github.io`
> - Project site: `https://{username}.github.io/{repo-name}`
>
> To enable GitHub Pages: open your GitHub repo → **Settings** → **Pages** → set Source to *Deploy from branch* (main / root).
>
> Once enabled, paste the URL above and save.

When `homepage_url` is a valid `https://` URL, the setup assistant is hidden.

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
| `homepage_url` | Homepage screen — live site link shown next to the Publish button; also shown (read-only) on Welcome / Summary with ✅/⚠️ status |

## Validation

| Field | Rule |
|-------|------|
| `homepage_url` | If non-empty, must start with `https://`. Server rejects bare hostnames (e.g. `username.github.io` without scheme). Client-side warning shown before submit. |

## Open Questions

- Should additional settings (polling interval, PROJECTS_DIR, SPECIFICATIONS_PATH) be editable here, or remain `.env`-only? Path-level settings (`PROJECTS_DIR`, `SPECIFICATIONS_PATH`) remain `.env`-only — changing them requires a restart and the risk of misconfiguration is high. Operational settings (polling interval, app branding) belong here.
- Should `app_name` changes take effect immediately? Yes — the server reads the `settings` table on each request for the brand label. No restart required.
