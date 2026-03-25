# Patch: 002 — Implement two-tier navigation bar
**Type:** patch
**Scope:** Base template, all screens, UI-GENERAL.md nav patterns

## Intent
The navigation bar has been redesigned as two tiers. The top bar is always visible with top-level tabs (Projects, Processes, Monitoring, Workflow, Publisher, Catalog). A project sub-bar appears only when Projects is the active top-level item, showing Dashboard and Configuration tabs plus the filter button on the right.

## Changes Required
- Top bar: tabs are Projects, Processes, Monitoring, Workflow, Publisher, Catalog (Configuration is removed from top level)
- Project sub-bar: renders below top bar only when Projects is active; contains Dashboard tab (links to `/`), Configuration tab (links to `/project-config`), and filter button (right side)
- Filter button moves from section header to the project sub-bar right side
- All SCREEN-DEFAULT-based screens (Dashboard, Configuration) render inside the Projects context with sub-bar visible
- Screens outside Projects context (Monitoring, Processes, Publisher, Workflow, Catalog) render top bar only, no sub-bar
- Brand click navigates to Dashboard (`/`)
- Documentation button opens `docs/index.html` in new tab

## Open Questions
None.
