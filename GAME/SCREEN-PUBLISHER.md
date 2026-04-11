# Screen: Publisher

**Description:** Portfolio site management. Builds and publishes a static GitHub Pages portfolio from project METADATA.md fields. Shows editable project cards for homepage inclusion.

## Menu Navigation

Main Menu: Publisher

## Route

```
GET /publisher
POST /publisher/build
POST /publisher/publish
POST /publisher/{project_id}/card
```

## Layout

Three sections stacked vertically: Build & Publish Controls, Publishing Config, and Project Cards.

### Section 1: Build & Publish Controls

Top section with status and action buttons.

| Element | Content |
|---------|---------|
| Description | "Build and publish a portfolio site from your projects." |
| Build button | "Rebuild" — triggers POST `/publisher/build` |
| Build status | Last build timestamp and status (success/error) |
| Error output | Collapse/expand panel showing build errors (shown only on failure) |
| Preview button | "Preview" — opens portfolio preview URL in new tab |
| Publish button | "Publish" — triggers POST `/publisher/publish`, pushes to GitHub Pages |
| Publish status | Last publish timestamp |
| Homepage link | "View Live" — opens production portfolio URL in new tab |

### Section 2: Publishing Config

Configuration fields for portfolio publishing:

| Field | Type | Source | Editable |
|-------|------|--------|----------|
| Publish location | URL input | `.env` or config | No (informational only) |
| Site title | Text input | `config/site_config.md` | Yes, POST on change |

### Section 3: Project Cards

Table of projects with editable homepage card fields. Only projects where `show_on_homepage = true` are shown. Prototypes are NOT shown on this page.

**Table columns:**

| Column | Source | Editable | Behavior |
|--------|--------|----------|----------|
| Status badge | `projects.status` | No | Colored pill: IDEA/PROTOTYPE/ACTIVE/PRODUCTION |
| Project name | `display_name` | No | Clickable → project detail |
| Include in homepage | `show_on_homepage` | Yes | Checkbox toggle |
| Card title | `card_title` (fallback: `display_name`) | Yes | Inline edit → save |
| Card description | `card_desc` (fallback: `short_description`) | Yes | Inline edit → save |
| Card tags | `card_tags` (fallback: `tags`) | Yes | Inline edit (comma-separated) → save |
| Card image | `card_image` (fallback: `logo`) | Yes | Inline edit (URL) → save |

Checkbox and inline fields send HTMX POST requests to `/publisher/{project_id}/card` with field updates. Server writes updated fields to METADATA.md.

**Sorting:** Alphabetical by display_name.

**Filtering:** Show/hide archived projects toggle (default: show active + prototype only).

## How It Works

1. Scan all projects where `show_on_homepage = true`
2. Parse card fields: `card_title` (fallback: `display_name`), `card_desc` (fallback: `short_description`), `card_tags` (fallback: `tags`), `card_image` (fallback: `logo`)
3. If project has `docs/index.html`, add documentation link to card
4. Generate static site from card fields + site branding
5. Serve locally or push to GitHub Pages

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Rebuild | Click button | POST `/publisher/build`, regenerates site |
| Edit card field | Click inline text | Allows edit, saves on blur or Enter → POST `/publisher/{project_id}/card` |
| Toggle homepage | Checkbox | POST `/publisher/{project_id}/card` with `show_on_homepage` flag |
| Publish | Click button | POST `/publisher/publish`, pushes to GitHub Pages |
| View live | Click link | Opens production URL in new tab |
| View preview | Click button | Opens localhost preview URL in new tab |

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` table (card fields, show_on_homepage) | `projects.card_title`, `card_desc`, `card_tags`, `card_image` |
| `settings` table (site config) | `settings` table (site config) |
| Project `doc/` directories | Static site output files |
| | GitHub Pages branch (git push) |
| | METADATA.md (card fields) |

## Open Questions

- Should the preview section show a card grid preview inline, or only via the external URL? External URL only — the preview server runs at a known port; inline iframe adds unnecessary complexity.
- Should editing card fields automatically trigger a rebuild, or require manual rebuild? Manual rebuild required — changes to card fields don't immediately rebuild the site. User clicks Rebuild after editing.
