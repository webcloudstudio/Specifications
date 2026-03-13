# Tag Management

**Lightweight visual grouping.** Tags from METADATA.md with user-defined colors. Filterable in the project list.

---

## Capabilities

- Assign tags to projects from dashboard
- Create tags on the fly
- Edit tag names and colors
- Delete tags
- Filter project list by one or more tags

## Screens

**Tag Badges (inline):** Colored badges per project. Click to filter. "+" to add.

**Tag Settings:** List of all tags with color swatch, name, project count, edit, delete.

## Persistence

- Tag colors: JSON file in platform data directory (git committed)
- Tag assignments: platform database, seeded from METADATA.md `tags:` field
