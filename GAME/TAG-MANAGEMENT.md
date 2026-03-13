# Feature: Tag Management

**spec_v4 · 2026-03-11**

---

## Purpose

Lightweight visual grouping for projects. Tags have user-defined colors. A project
can have multiple tags. The project list is filterable by tag.

---

## What the User Can Do

- Assign tags to projects from the dashboard
- Create tags on the fly while tagging
- Edit tag names and colors
- Delete tags
- Filter the project list by one or more tags

---

## Screens

### Tag Badges (inline, Control Panel)

Colored badge per tag on each project row. Click to filter by that tag.
"+" to add a tag → dropdown of existing tags + "New tag" option.

### Tag Management (settings section)

List of all tags. Per row: color swatch, name, project count, edit, delete.
New Tag form: name + color picker. Inline edit.

---

## Persistence

Tag color definitions are stored in a user-editable JSON file in the platform's data
directory. This file is committed to the platform's git repository.

```json
{
  "active": "#4caf50",
  "paused": "#ff9800",
  "published": "#2196f3"
}
```

Tag-to-project assignments are stored in the platform database. They may optionally
be imported from the `Tags` field in a project's `git_homepage.md`.

---

## Out of Scope

- Portfolio card tags → those are in git_homepage.md; separate from dashboard tags
- Hierarchical tags → flat only
