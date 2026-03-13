# Control Panel

**The main dashboard.** Shows every project with status, operations, and metadata. All common actions happen here.

---

## Capabilities

- Project list with status badges, tags, stack, and running indicator
- One-click operation buttons per project (from bin/ headers)
- Inline workflow state and type editing
- Filter by state, type, or tag
- Quick links from CLAUDE.md bookmarks
- Running process count in nav bar
- Rescan trigger

## Screens

**Projects List:** Full-width table. One row per project. Columns: name, type/state badges, tags, stack, running indicator, operation buttons, quick links.

**Project Detail:** Single-project view with all operations, endpoints, bookmarks, git status, and CLAUDE.md content.

**Nav Bar:** Running process count. Link to Process Monitor.

## Data Flow

| Reads From | Writes To |
|------------|-----------|
| PROJECT-DISCOVERY (project records) | OPERATIONS-ENGINE (launch requests) |
| OPERATIONS-ENGINE (run status) | Workflow state store (state changes) |
| PROCESS-MONITOR (running count) | Project type store (type changes) |
| TAG-MANAGEMENT (tags + colors) | |
