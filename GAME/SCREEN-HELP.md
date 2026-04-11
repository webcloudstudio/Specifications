# Screen: Help

| Field | Value |
|-------|-------|
| Version | 20260407 V1 |
| Route | `GET /help` |
| Parent | — |
| Main Menu | Help [right] |
| Sub Menu | — |
| Tab Order | — |

Documentation viewer. Renders `docs/index.html` in-page when available; friendly fallback when not built.

## Layout

Full-viewport content area. No max-width cap — the embedded documentation fills the space.

### When `docs/index.html` exists

Renders `docs/index.html` inside a full-height `<iframe>` that fills the content area below the top bar.

```
┌──────────────────────────────────────────────────────────┐
│  [top bar / nav]                                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   <iframe src="/docs/index.html" ...>                    │
│   (full-height, no border, no padding)                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

The iframe src is served via a proxy route (`GET /docs/<path>`) so the file is accessible without a separate static server.

### When `docs/index.html` does not exist

Centered message in the content area:

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   📖  Documentation not built                            │
│                                                          │
│   Run the following command in the Specifications        │
│   repository to generate documentation:                  │
│                                                          │
│   bash bin/build_documentation.sh                        │
│                                                          │
│   Then restart or rescan to make it available here.      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

Message is muted text, centered, with the command in a monospace code block.

## Detection

The server checks for the existence of `docs/index.html` relative to `SPECIFICATIONS_PATH` (or the app root if `SPECIFICATIONS_PATH` is not set) on each request to `/help`. No caching — if the file appears after a build it is immediately available.

## Data Flow

| Reads | Writes |
|-------|--------|
| `docs/index.html` existence check (filesystem) | None |
| `docs/index.html` content (served via proxy route) | None |

Static content. No database reads or writes.

## Open Questions

- Should the Help tab indicate (e.g., dot indicator) when docs have not been built?
- Should an "Open in new tab" button be shown alongside the iframe for easier reading?
