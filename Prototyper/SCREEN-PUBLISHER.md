# Screen: Portfolio

**Version:** 20260320 V1  
**Description:** Spec for the Portfolio screen

**Portfolio site management.** Builds and publishes a static GitHub Pages portfolio from project METADATA.md fields.

## Route

```
GET /publisher
```

## Layout

Four sections stacked vertically: Build, Preview, Publish, Homepage.

## Build Section

- Rebuild button
- Last build timestamp and status
- Error output panel below (clearly labeled, shown only on failure)

## Preview Section

- Start/Stop toggle button (starts local preview server if not running, stops if running)
- Preview URL button (always visible, opens localhost preview in new tab)

## Publish Section

- Push to GitHub Pages button
- Last publish timestamp

## Homepage Section

- Link to live site (opens in new tab)

## How It Works

1. Scan all projects where `show_on_homepage = true`
2. Parse card fields: `card_title` (fallback: `display_name`), `card_desc` (fallback: `short_description`), `card_tags` (fallback: `tags`), `card_image` (fallback: `logo`)
3. If project has `doc/index.html`, add documentation link to card
4. Generate static site from `config/site_config.md` branding
5. Serve locally or push to GitHub Pages

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Rebuild | Click button | POST `/publisher/build`, regenerates site |
| Toggle preview | Click button | Starts/stops local server |
| Publish | Click button | POST `/publisher/publish`, pushes to GitHub Pages |
| View live | Click link | Opens production URL in new tab |

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` table (card fields) | Static site output files |
| `config/site_config.md` | GitHub Pages branch (git push) |
| Project `doc/` directories | |

## Open Questions

- Should the preview section show a card grid preview inline, or only via the external URL?
