# Screen: Configuration

## Purpose

Project-level configuration fields editable in a list view. Allows quick editing of port, homepage visibility, and tags across all projects without opening each project's detail page.

---

## Route

```
GET /project-config
```

No query parameters. Filter defaults to `normal`. Sort defaults to `name`.

---

## Instantiation

This screen is a SCREEN-DEFAULT instance with these parameters:

```
title:   Configuration
columns: Configuration
route:   /project-config
```

It inherits all layout rules, nav bar, filter button, sort behaviour, and fixed columns from SCREEN-DEFAULT.md. Only the middle column differs.

---

## Configuration Column — Field Spec

Each project row renders one cell containing three labelled fields. Fields save independently — no Save button exists.

| Field | Label | DB Column | METADATA.md Key | Input Type | Validation |
|-------|-------|-----------|-----------------|------------|------------|
| Port | `port:` | `projects.port` (INTEGER) | `port:` | `<input type="number">` | Integer > 1024; blank = null |
| Show | `show:` | `projects.card_show` (0/1) | `show_on_homepage:` | `<input type="checkbox">` | Boolean |
| Tags | `tags:` | `projects.tags` (TEXT) | `tags:` | `<input type="text">` | Comma-separated string; blank = null |

### Cell Layout

```
port:  [____]   show: [x]   tags: [__________________]
```

Compact single row. Labels are small/muted (`text-muted small`). Port input ~80px wide. Tags input fills remaining width. May wrap on narrow viewports.

---

## Persistence

### Trigger

| Input type | Save trigger |
|------------|-------------|
| `number`, `text` | `blur` (focus leaves the field) |
| `checkbox` | `change` (immediate on toggle) |

No debounce. No Save button. No confirmation.

### HTMX Contract

```
POST /api/project/{id}/update
Content-Type: application/x-www-form-urlencoded

field=<field_name>&<field_name>=<value>
```

| Field name | Form params sent |
|------------|-----------------|
| `port` | `field=port` + `port=<integer string>` |
| `card_show` | `field=card_show` + `card_show=on` (checked) or `card_show` omitted (unchecked) |
| `tags` | `field=tags` + `tags=<comma string>` |

Response: `HTTP 204 No Content` (empty body).

HTMX attributes:

```html
<!-- Number / text inputs -->
<input hx-post="/api/project/{id}/update"
       hx-trigger="blur"
       hx-vals='{"field": "<field_name>"}'
       hx-swap="none"
       name="<field_name>"
       value="...">

<!-- Checkbox -->
<input type="checkbox"
       hx-post="/api/project/{id}/update"
       hx-trigger="change"
       hx-include="[name='card_show_{id}']"
       hx-vals='{"field": "card_show"}'
       hx-swap="none"
       name="card_show">
```

`hx-swap="none"` — the 204 response carries no HTML; the input stays as-is after save.

### Dual-Write: DB + METADATA.md

Every save writes to both. See DATABASE.md — Source-of-Truth Model.

| Field | DB write | File write | Write method |
|-------|----------|------------|--------------|
| `port` | `UPDATE projects SET port = ?` | Patches `port:` line in `METADATA.md` | `_write_metadata_key_value(path, 'port', value)` — single-key patch |
| `card_show` | `UPDATE projects SET card_show = ?` | Rewrites all key-value fields in `METADATA.md` | `_write_metadata_md_fields(path, project)` — full file rewrite; emits `true`/`false` |
| `tags` | `UPDATE projects SET tags = ?` | Patches `tags:` line in `METADATA.md` | `_write_metadata_key_value(path, 'tags', value)` — single-key patch |

`card_show` uses full rewrite because `show_on_homepage:` must stay consistent with the other card fields written by `_write_metadata_md_fields`.

### Validation

| Condition | Behaviour |
|-----------|-----------|
| Port ≤ 1024 or non-integer | Silently ignore — no DB write, no file write |
| Port blank | Write `NULL` to DB; omit or clear `port:` in METADATA.md |
| Tags blank | Write `NULL` to DB; write empty string to `tags:` in METADATA.md |

Server-side only. No client-side validation messages on this screen.

---

## Data Access

- **Page render**: `db.get_all_projects()` + `db.get_all_operations_keyed()` — two queries, no file I/O.
- **Field save**: `POST /api/project/{id}/update` — writes DB + METADATA.md.
- No polling. No auto-refresh after save.

---

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects.port` | `projects.port` (DB) + `port:` in METADATA.md |
| `projects.card_show` | `projects.card_show` (DB) + `show_on_homepage:` in METADATA.md |
| `projects.tags` | `projects.tags` (DB) + `tags:` in METADATA.md |

Fixed columns (status badge, namespace badge, project name, settings cog) read the same sources as all SCREEN-DEFAULT instances.

---

## Open Questions

- **Validation UX**: Silent failure on bad port. A red input border and value restore would be cleaner — not yet designed.
- **Blank port**: Should clearing port remove the `port:` line from METADATA.md or write it empty? Currently undefined.
- **Tag autocomplete**: A `<datalist>` sourced from `data/tag_colors.json` would be consistent with tag usage elsewhere — roadmap item.
