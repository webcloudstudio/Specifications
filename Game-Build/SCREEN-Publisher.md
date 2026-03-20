# Screen: Publisher

Build and publish a static portfolio site from project metadata.

## Route

```
GET /publisher
```

## Layout

Two sections: project card preview list + action buttons.

## Project Cards

List of projects where card_show=true. Each shows:

| Field | Source |
|-------|--------|
| Title | card_title → fallback display_name |
| Description | card_desc → fallback short_description |
| Image | card_image → fallback logo |
| Tags | card_tags → fallback tags |
| Documentation link | Shown if has_docs=true |

## Actions

| Button | Effect |
|--------|--------|
| Rebuild | POST /publisher/build → regenerates static site from DB |
| Publish | POST /publisher/publish → pushes to GitHub Pages |
| Toggle project | POST /api/project/{id}/toggle-publish → include/exclude |

## Open Questions

- Preview the generated site inline or open in new tab?
- Config for site title, branding (currently config/site_config.md)?
