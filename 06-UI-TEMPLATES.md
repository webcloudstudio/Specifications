# UI Templates & Layout

All templates use Jinja2 and extend `base.html`.

## base.html — Master Layout

### Structure
```
<html data-bs-theme="dark">
  <head>
    Bootstrap 5.3.3 CSS (CDN)
    style.css (local)
    HTMX 2.0.4 (CDN)
  </head>
  <body>
    <nav class="cc-nav">
      Brand: "⌘ {app_name}" (links to /)
      Tabs: Projects | Configuration | GIT-Homepage | Processes
      Hamburger (☰): Settings, Usage, Tags, Help
      Running Projects: green "● {title}" badges (linked to project detail)
    </nav>
    <main class="cc-main">
      Flash messages (Bootstrap alerts, dismissible)
      {% block content %}
    </main>
    CLAUDE.md Viewer Modal (#claudeModal)
    Command Output Modal (#opOutputModal)
    Bootstrap 5.3.3 JS (CDN)
    showOpModal event listener (opens output modal on HX-Trigger)
  </body>
</html>
```

### Modals

**CLAUDE.md Viewer** (`#claudeModal`): Large, scrollable modal. Content loaded via HTMX into `#claude-modal-body`. Shows project title, filename, and preformatted content.

**Command Output** (`#opOutputModal`): Large, scrollable modal. Content injected via OOB swap into `#op-output-body`. Triggered by `showOpModal` custom event from HTMX response header.

## list.html — Projects Tab

### Header
- Title: "Projects"
- Sort dropdown: Name / Status ↑ / Status ↓ (changes URL param)
- Refresh button: `POST /api/sync` then reload

### Content
- Empty state: "No projects found" with Refresh button
- Table: `<table class="project-table">` with type-specific row templates
- Each project renders via `{% include type_config.row_template %}`

## Type-Specific Row Templates

### _project_standard_columns.html (shared)

First 2 columns included by all row templates:

| Column | Width | Content |
|--------|-------|---------|
| Status | 120px | Workflow badge (`<span class="workflow-badge" style="background:{color}">{label}</span>`) |
| Name   | flex  | Type icon (📖/💻) + project title + RUNNING badge (if has_running) |

### _software_row.html / _book_row.html

Extends standard columns with:

| Column | Content |
|--------|---------|
| Port | Click-to-edit port number (HTMX inline edit) |
| Links | Links from Links.md as callout buttons, or server link from port |
| Local Ops | Operation buttons (op-btn--local/service) for category='local' |
| Remote Ops | Git Push button with unpushed count badge (hidden if count=0) |
| CLAUDE.md | Orange badge opening viewer modal (if has_claude) |
| Settings | ⚙️ gear icon linking to project detail page |

Book row differs: shows "Book" type badge instead of server link when no Links.md.

### Operation Button Behavior

**Local ops** (Start Server, etc.):
- Click → `POST /api/op/{id}/run` → button swaps to Stop button or shows output modal
- Stop → `POST /api/op/{id}/stop` → button swaps back to Start

**Remote ops** (Git Push):
- Only visible when `unpushed > 0`
- Shows red badge with unpushed count
- Click → executes as one-shot, shows output in modal

## _project_editor_row.html — Configuration Tab Row

| Column | Content |
|--------|---------|
| Status | Workflow badge |
| Name | Clickable type icon (toggles software↔book) + linked title |
| Workflow | Dropdown select (auto-saves on change, reloads page) |
| Publish | Checkbox for `card_show` (auto-saves via HTMX) |
| Settings | ⚙️ gear icon |

## Project Detail Pages

### _software_detail.html

Layout: 2-column (8/4 Bootstrap grid)

**Left column:**
- Back button
- Title + "Software" badge + unpushed count
- "Project Details" card: Title, Description, Tech Stack, Port, Remote URL (all auto-save on change via HTMX)

**Right column:**
- "Info" card: Directory, Git, Venv, Node, CLAUDE.md, Created date
- "Links" card (if Links.md exists): label + URL list

**Bottom (if server ops exist):**
- "Live Logs" card: Auto-refreshing log viewer (polls every 3s via HTMX)
- Dropdown to switch between multiple server ops
- Log content from `/api/op/{id}/logs`

### _book_detail.html

Simplified layout:
- Back button, title with 📖 icon
- "Configuration" card: Directory (read-only), Title, Description
- "Info" card: Git, CLAUDE.md, Created date

## publish.html — GIT-Homepage Tab

### Pipeline Buttons (horizontal row)
- **Rebuild** (blue): `⟳ Rebuild` — shows last click time, swaps to Stop when running
- **Preview** (green): `▶ Preview` — shows Preview link when running + Stop button
- **Push** (purple): `↑ Push` — shows last click time, swaps to Stop when running
- **Homepage** (purple): `🌐 Homepage` — links to production URL

### Content Area (70/30 grid)

**Left: Contents table** — All projects with:
- Workflow badge, type icon, title
- Card title, card type
- Publish checkbox (auto-saves via HTMX)
- Rows are clickable → updates Details sidebar

**Right: Details card** — Edit form for selected project:
- Card Title, Type, URL, Description, Tags, Show checkbox
- All fields auto-save on blur via HTMX
- JavaScript `switchToDetails(projectId)` updates form dynamically

### Auto-Refresh
- 1-second interval while any pipeline process is running
- Stops automatically when all processes complete

## processes.html — Processes Tab

### Running Processes Table
| Column | Content |
|--------|---------|
| Command | Truncated cmd (60 chars) in `<code>` |
| PID | Green colored |
| Started | Timestamp |
| Elapsed | Computed time string |
| Actions | Stop button (with confirm) + Log button |

### Completed Processes Table
| Column | Content |
|--------|---------|
| Command | Truncated cmd |
| Status | ✓ Done (green) / ✗ Error (red) |
| Completed | Timestamp |
| Actions | Log button |

### Log Viewer Modal
- Custom modal (not Bootstrap): fixed overlay with close button
- Fetches log via `fetch('/api/processes/log/{id}')` and displays in `<pre>`
- Green monospace text on dark background

### Auto-Refresh
- 3-second interval while running processes exist
- Checks `/api/processes/running` JSON endpoint
- Stops when no processes running

## settings.html
- Form: Application Name (text), Homepage URL (url)
- Save button + Cancel link
- Saves to Flask config (in-memory)

## tags.html
- Color legend: py (green), db (orange), ops (blue), fe (purple), sec (red), neutral (gray)
- Table: tag name, color dropdown + update button, delete button
- Add form: name input + color dropdown + Add button

## usage.html
- Time period selector: 7/14/30 days dropdown + Refresh button
- Report card: renders `usage_analyzer.generate_report()` HTML with Plotly charts

## help.html
- Bootstrap accordion with feature documentation sections:
  1. Processes Monitor
  2. Spawn Service
  3. Publish Pipeline
  4. Tags & Project Organization
- Pro Tips section at bottom
