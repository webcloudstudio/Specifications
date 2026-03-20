# Screen: Configuration

Edit project metadata across all projects in a single list.

## Route

```
GET /project-config
```

## Layout

Project list using Standard Row Header. Each row has editable fields.

## Columns

| Column | Content |
|--------|---------|
| Status + Name | Standard Row Header |
| Configuration | Editable fields (see below) |

## Configuration Fields

| Field | Label | Source | Input |
|-------|-------|--------|-------|
| Port | `port:` | projects.port | number |
| Show on homepage | `show:` | projects.card_show | checkbox |
| Tags | `tags:` | projects.tags | text |

Fields persist on change per DATABASE.md rules. Each field saves independently — no Save button.

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Edit field | Change input value | POST update → DB + METADATA.md sync |
| Open full editor | Click cog icon | Full METADATA.md field editor |

## Open Questions

- Add more inline fields (status, namespace, desired_state)?
- Should cog icon open a modal or navigate to a detail page?
