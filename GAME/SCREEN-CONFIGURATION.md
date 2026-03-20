# Screen: Configuration

A Baseline screen for editing project metadata across all projects in a single list.

## Route

```
GET /project-config
```

## Columns

```
columns=Configuration
```

## Configuration Column

Three editable fields per project row:

| Field | Label | Source | Input |
|-------|-------|--------|-------|
| Port | `port:` | `projects.port` | number |
| Show on homepage | `show:` | `projects.card_show` | checkbox |
| Tags | `tags:` | `projects.tags` | text |

Fields persist on change per DATABASE.md rules. Each field saves independently — no Save button.
