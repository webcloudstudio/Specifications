# Screen: Welcome

**Description:** Landing screen shown when the user first enters the application. START HERE checklist, project discovery overview, and help resources.

## Menu Navigation

`Projects / Welcome`

## Route

```
GET /welcome   (default — also served at GET /)
```

The app root (`/`) redirects to `/welcome` when no other default is set.

## Layout

Single-column centered content, max-width 900px, padded. Four stacked sections:

```
┌────────────────────────────────────────────┐
│                                            │
│         ██ WELCOME TO PROTOTYPER ██        │
│      Your local prototype operations hub   │
│                                            │
├────────────────────────────────────────────┤
│  🟢 START HERE                             │
│  ─────────────────────────────────────────│
│  [checklist with status indicators]        │
├────────────────────────────────────────────┤
│  📁 Project Discovery                      │
│  ─────────────────────────────────────────│
│  XX Projects | XX Prototypes               │
│  [Alphabetical list of projects]           │
├────────────────────────────────────────────┤
│  ❓ Service Help                           │
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

## START HERE Card

Card (`cc-card`) highlighted with an accent background color. Purpose: quick checklist to verify the application is properly configured.

### Card Header

`START HERE` — large, bold, highlighted in accent color with a green circle indicator (●).

### Checklist Items

Four checklist items with status indicators. Status icons use a stoplight pattern:

| Item | Status Source | Icon | Description |
|------|---------------|------|-------------|
| PROJECTS_DIR | Environment config | ✅/⚠️/❌ | Shows the configured directory path. Displays directory value inline. Green if accessible, amber if not found, red if missing. |
| Startup Scan | Backend metric | ✅ | Displays: "Startup Scan Detected {count} Projects and {count} Prototypes" — produced by the startup scanner on app initialization. Green check always (informational, not a failure condition). |
| Ready to Use | Derived state | ✅ | "Application ready" — shown when scan has completed and projects list is populated. Green check. |
| Next Steps | — | 📌 | "Use the Projects tab above or Rescan to update" — informational only, not a failure state. |

Each item is a row with icon + label + value/description. Use emoji or Font Awesome icons for stoplight effect (● red, ⚠️ amber, ✅ green).

### Content Layout

Displayed as a vertical checklist. Not a form—purely informational with read-only values.

## Project Discovery Card

Card (`cc-card`) below the START HERE section. Purpose: show project discovery overview and list all discovered projects.

### Card Header

`Project Discovery` with a folder icon (📁).

### Summary Line

Two-column summary: `XX Projects | XX Prototypes` — count of discovered projects and prototypes from the startup scan.

### Project List

One-column alphabetical list of project names below the summary. Each project name is clickable and links to `/project/{id}` for detail view.

Example:
```
Analytics
Dashboard
DataPipeline
MLExperiment
WebApp
```

List is sorted alphabetically. One project per row. Space reserved for future KPI columns (do not implement yet).

## Service Help Links Card

Card below the project discovery card. Purpose: quick links to commonly needed external help pages.

### Card Header

`Help & Resources` with a question-mark icon (❓).

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
| `projects` table (count + list) | None |
| Startup scan metrics | |

Reads from backend: project count, project list, prototype count, PROJECTS_DIR value from env.

## Open Questions

- Should the welcome banner display the logged-in username (if auth is added later)?
- Should the START HERE checklist be collapsible once all items are green?
- Should the help links be editable from the Settings screen?
