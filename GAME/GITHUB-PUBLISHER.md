# Feature: GitHub Publisher

**spec_v4 · 2026-03-11**

---

## Purpose

Generates and publishes a professional portfolio website to GitHub Pages from the
metadata already in each project's `git_homepage.md`. No manual content management.

---

## What the User Can Do

- Rebuild the portfolio site with one click
- Preview it locally before publishing
- Push it live with one click
- Configure site-wide branding (name, tagline, home page text)
- Show or hide individual projects from the portfolio

---

## Screens

### Publisher Dashboard

Three sections:

**Build:** Rebuild button, last build timestamp and status, error output if failed.

**Preview:** Start/stop local preview server, preview URL when running.

**Publish:** Push to GitHub Pages button, last publish time, link to live site.

---

## How It Works

1. Read site branding from `git_site_config.md` in the platform's own directory
2. Scan all projects for `git_homepage.md` where `Show on Homepage: true`
3. For each: parse card fields, resolve image paths
4. Generate static site source files:
   - Site config
   - Projects page (card grid)
   - Home page (branding + markdown body)
   - Resume page (from static CV file)
5. Build the static site
6. Preview or publish

---

## Persistence

**Site branding** is stored in `git_site_config.md` at the platform root.
**Project card data** is stored in each project's `git_homepage.md`.

Neither file is owned by the platform. The user edits them directly; the publisher reads them.

---

## Contracts Used

- **Portfolio Contract** (THE-CONTRACT.md §2): reads `git_homepage.md` from every project
- **AI Context Contract** (THE-CONTRACT.md §3): `git_site_config.md` follows similar frontmatter conventions

---

## Data In / Out

**Reads:** git_homepage.md from all projects, git_site_config.md, card images, CV source file

**Writes:** Static site source files, built site, published site (git push)

---

## Out of Scope

- Editing card content directly in the UI → edit git_homepage.md in the project
- Dynamic (server-rendered) portfolio → static only
- Custom page templates beyond home/projects/resume → not planned
