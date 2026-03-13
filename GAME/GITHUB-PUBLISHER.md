# GitHub Publisher

**Portfolio site generator.** Builds and publishes a static GitHub Pages portfolio from METADATA.md across all projects.

---

## Capabilities

- One-click rebuild of portfolio site
- Local preview server
- One-click push to GitHub Pages
- Site-wide branding config (name, tagline, home page text)
- Per-project show/hide via `show_on_homepage` in METADATA.md
- Documentation links when `docs/index.html` exists

## How It Works

1. Read site branding from platform config
2. Scan projects for METADATA.md where `show_on_homepage: true`
3. Parse card fields (title, description, tags, image)
4. Generate static site (card grid, home page, resume page)
5. Build and serve locally or publish

## Screens

**Publisher Dashboard:**
- Build: Rebuild button, last build time, error output
- Preview: Start/stop local server, preview URL
- Publish: Push button, last publish time, live site link

## Data Flow

| Reads From | Writes To |
|------------|-----------|
| PROJECT-DISCOVERY (METADATA.md data) | Static site files |
| Site branding config | Published portfolio (git push) |
| Project docs/ directories | |
