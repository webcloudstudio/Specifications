# Feature: Portfolio Publishing

**Version:** 20260320 V1  
**Description:** Spec for the Portfolio Publishing feature

Builds a static portfolio site from project metadata and publishes to GitHub Pages.

## Build

**Trigger:** User clicks Rebuild on Publisher screen.

1. Query projects WHERE card_show=true
2. For each: resolve card fields with fallback chain (card_title→display_name, card_desc→short_description, card_image→logo, card_tags→tags)
3. Check for doc/index.html → add documentation link if exists
4. Generate card HTML fragments
5. Load config/site_config.md (YAML frontmatter for branding, markdown body for home page)
6. Assemble static site: card grid + home page
7. Write output files

## Publish

**Trigger:** User clicks Publish on Publisher screen.

1. Execute PushAndPublish.sh
2. Git add, commit, push to GitHub Pages branch

## Reads

`projects` table (card fields), config/site_config.md, doc/ directories, static/images/

## Writes

Static site output files, GitHub Pages branch

## Open Questions

- Preview generated site inline before publishing?
- Custom domain support?
