# Screen: Portfolio

**Portfolio site management.** Builds and publishes a static GitHub Pages portfolio from METADATA.md.

---

## NOTE - THE CORRECT PAGE LAYOUT IS BELOW - THE ADDITIONAL FIELDS ON THE CURRENT LAYOUT ARE NOT NEEDED

## Layout

Three sections: Build, Preview, Push/Publish, Homepage.

## Build Section

- Rebuild button
- Last build timestamp and status
- Error output if build failed in a panel below clearly labeled as such

## Preview Section

- Clicking the button will Start or stop local preview server (start if it is not running)
- Preview URL Button under the Above always

## Publish Section

- Push to GitHub Pages button
- Last publish timestamp

## Homepage
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
