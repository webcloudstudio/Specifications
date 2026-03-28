# Screen: Welcome

**Description:** Landing screen shown when the user first enters the application. Welcome banner and information about automatic project discovery.

## Menu Navigation

`Projects / Welcome`

## Route

```
GET /welcome   (default — also served at GET /)
```

The app root (`/`) redirects to `/welcome` when no other default is set.

## Layout

Single-column centered content, max-width 900px, padded. Two stacked sections:

```
┌────────────────────────────────────────────┐
│                                            │
│         ██ WELCOME TO PROTOTYPER ██        │
│      Your local prototype operations hub   │
│                                            │
├────────────────────────────────────────────┤
│  Project Discovery                         │
│  ─────────────────────────────────────────│
│  [projects directory info + scan details]  │
├────────────────────────────────────────────┤
│  Service Help                              │
│  ─────────────────────────────────────────│
│  [help page links]                         │
└────────────────────────────────────────────┘
```

## Welcome Banner

Full-width hero section at top of page. Dark surface (`--cc-surface`), large centered text.

| Element | Content |
|---------|---------|
| Headline | `Welcome to Prototyper` — large (32px), bold, accent color |
| Subheadline | `Your local prototype operations hub` — muted, 16px |
| Decoration | Subtle horizontal rule below subheadline |

No buttons or actions in the banner. Visual only.

## Project Discovery Card

Card (`cc-card`) below the banner. Purpose: inform the user about automatic project discovery and the projects directory structure.

### Card Header

`Project Discovery` with a folder icon.

### Content

Informational text layout explaining how project discovery works.

| Element | Content |
|---------|---------|
| Description | `Projects are automatically scanned on startup and when you request a rescan.` |
| Directory Info | `Projects are discovered from the directory configured in PROJECTS_DIR environment variable.` |
| What's Scanned | Listed as bullet points: METADATA.md for project identity, AGENTS.md for endpoints, bin/ directory for scripts |
| Note | `There is no need to add command center operations to project files — the scanner finds and indexes executable scripts automatically.` |

Use concise, scannable bullet points rather than prose paragraphs.

## Service Help Links Card

Card below the project discovery card. Purpose: quick links to commonly needed external help pages.

### Card Header

`Help & Resources` with a question-mark icon.

### Links

Displayed as a grid of link buttons (2-column on desktop, 1-column on narrow).

| Label | Destination | Notes |
|-------|-------------|-------|
| GitHub Docs | `https://docs.github.com` | Opens new tab |
| Flask Documentation | `https://flask.palletsprojects.com` | Opens new tab |
| Bootstrap 5 Docs | `https://getbootstrap.com/docs/5.3` | Opens new tab |
| Prototyper Workflow | `../doc/index.html` | Local documentation |

All links open in a new tab. Cards are static — no data fetch required.

## Data Flow

| Reads | Writes |
|-------|--------|
| None — static content | None |

No API calls. Screen is fully static HTML rendered by the server template.

## Open Questions

- Should the welcome banner display the logged-in username (if auth is added later)?
- Should the project discovery card show a live count of currently discovered projects?
- Should the help links be editable from the Settings screen?
