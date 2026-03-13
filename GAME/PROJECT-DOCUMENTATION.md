# Feature: Project Documentation

**spec_v4 · 2026-03-11**

---

## Purpose

Every project can publish a self-contained documentation site. When a project has a
`docs/` directory containing `index.html`, the platform automatically includes it in
the GitHub Pages portfolio build — copying it to a standard location where it can be
browsed without any server.

---

## What the User Can Do

- Browse any project's documentation at a stable URL on the portfolio site
- See a "Documentation ↗" link on the project's portfolio card (when docs exist)
- Regenerate a project's documentation by running `bin/build_documentation.sh`
- Update documentation content by editing markdown files and rebuilding

---

## Screens

### Portfolio Card (modified)

When a project has `docs/index.html`, the card on the projects page gains an additional
button: **Documentation ↗** — links to the docs URL on the portfolio site.

The existing "View Project ↗" button (from `card_url` in git_homepage.md) is unaffected.

---

## How It Works

During the portfolio rebuild (`bin/RebuildYourHomepage.sh`):

1. The publisher scans each project directory for `docs/index.html`
2. If found, the entire `docs/` directory is copied to `My_Github/public/project-docs/{project-name}/`
3. The project card is rendered with a Documentation link pointing to `/project-docs/{project-name}/`
4. The static site build includes the copied files as static assets

The documentation is served at:
```
https://{github-username}.github.io/project-docs/{project-name}/
```

---

## The Standard: Project Documentation Contract

**File:** `docs/index.html` at the project root
**What you get:** Documentation link on the portfolio card; documentation browsable on the live site

### Requirements

1. `docs/index.html` must exist and be a valid standalone HTML file
2. The file must work when opened directly (no server fetch required)
3. All assets (CSS, JS, images) must be embedded inline or relative-path referenced
   within the `docs/` directory — no external dependencies that won't resolve on GitHub Pages

### Generating docs/index.html

The standard mechanism is `bin/build_documentation.sh` — a CommandCenter Operation
that generates `docs/index.html` from the project's source documentation.

For GAME, `build_documentation.sh` calls `docs/rebuild_index.sh`, which embeds all
markdown specification files into a self-contained HTML viewer.

For other projects, `build_documentation.sh` might:
- Convert markdown files to a styled HTML page
- Package API documentation
- Render a project overview from CLAUDE.md + git_homepage.md

The implementation is the project's choice. The contract is only that
`docs/index.html` exists and works standalone.

### What build_documentation.sh Should Do

As a CommandCenter Operation, `bin/build_documentation.sh` must:

- Include the CommandCenter Operation header (see SERVICE-SCRIPT-STANDARDS / THE-CONTRACT §1)
- Emit `[GAME] Service Starting/Stopped` messages (see LOGGING.md)
- Write its output to `docs/index.html`
- Exit 0 on success, non-0 on failure

---

## Persistence

`docs/index.html` is committed to the project's git repository. It is both source
and output — the generated artifact is version-controlled alongside the markdown sources.

The `docs/` directory in `My_Github/public/project-docs/` is derived — it is
overwritten on every portfolio rebuild and should not be edited there directly.

---

## Data In / Out

**Inputs:**
- `docs/index.html` in each project directory (detected by publisher)

**Outputs:**
- `My_Github/public/project-docs/{name}/` — copied docs tree
- Documentation link on the portfolio card

---

## Contracts Used

- **Operations Contract** (THE-CONTRACT.md §1): `bin/build_documentation.sh` uses
  the CommandCenter header
- **Logging** (LOGGING.md): build script emits status messages
- **Portfolio Contract** (THE-CONTRACT.md §2): publisher reads project dirs during rebuild

---

## Out of Scope

- Hosting documentation separately from the GitHub Pages portfolio → not planned
- Auto-generating documentation without `build_documentation.sh` → always requires explicit build
- Documentation versioning → out of scope; git history of `docs/` serves this purpose
