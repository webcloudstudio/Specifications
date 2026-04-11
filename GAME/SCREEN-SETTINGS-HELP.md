# Screen: Help (Settings)

| Field | Value |
|-------|-------|
| Version | 20260407 V1 |
| Route | `GET /settings/help` |
| Parent | — |
| Main Menu | Settings [right] |
| Sub Menu | Help |
| Tab Order | 1: General · 2: Tags · 3: Voice · 4: Voice Docs · 5: Help |
| Description | Application help and documentation within the Settings sub-bar. |

## Layout

Single-column centered content, max-width 900px, padded. Sections stacked vertically.

```
┌─────────────────────────────────────────────┐
│  Help & Documentation                       │
│  ─────────────────────────────────────────  │
│                                             │
│  [Help section content]                     │
│                                             │
└─────────────────────────────────────────────┘
```

## Content Sections

### Getting Started

Brief introduction to Prototyper and its key features:
- Automatic project discovery from PROJECTS_DIR
- Running operations (scripts) from projects
- Monitoring project health and status
- Publishing portfolio sites

### Key Concepts

| Concept | Description |
|---------|-------------|
| Projects | Discovered repositories containing METADATA.md and bin/ scripts |
| Prototypes | Specification directories in the Specifications repository |
| Operations | Executable scripts with CommandCenter headers, auto-discovered and launchable |
| Health | Periodic checks of project status via HTTP or TCP |
| Workflow | Custom workflow types for batch operations |

### FAQ

Common questions and answers:
- How are projects discovered?
- How do I add a new project?
- How do I create an operation?
- How do I publish to the portfolio?
- How do I monitor project health?
- How do I configure settings?

### External Resources

Links to official documentation:

| Resource | URL |
|----------|-----|
| Prototyper Workflow Guide | `../doc/index.html` |
| GitHub Docs | `https://docs.github.com` |
| Flask Documentation | `https://flask.palletsprojects.com` |
| Bootstrap 5 Docs | `https://getbootstrap.com/docs/5.3` |

## Data Flow

| Reads | Writes |
|-------|--------|
| None — static content | None |

This is a static information page. No data reads or writes.

## Open Questions

- Should the FAQ be searchable?
- Should help content be editable from the admin interface?
- Should the Help page include a changelog or version history?
