# Screen: Publisher

**Portfolio site management.** Builds and publishes a static GitHub Pages portfolio from METADATA.md.

---

## Layout

Three sections: Build, Preview, Publish.

## Build Section

- Rebuild button
- Last build timestamp and status
- Error output if build failed

## Preview Section

- Start/stop local preview server
- Preview URL when running

## Publish Section

- Push to GitHub Pages button
- Last publish timestamp
- Link to live site

## How It Works

1. Scan all projects for METADATA.md where `show_on_homepage: true`
2. Parse card fields: `title`, `short_description`, `tags`, `image`
3. If project has `doc/index.html`, add documentation link to card
4. Generate static site: card grid, home page, resume page
5. Build and serve locally or push to GitHub Pages

## Data Flow

| Reads | Writes |
|-------|--------|
| METADATA.md from all projects | Static site files |
| Site branding config | Published portfolio (git push) |
| Project doc/ directories | |
