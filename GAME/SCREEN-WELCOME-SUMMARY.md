# Screen: Welcome — Summary

| Field | Value |
|-------|-------|
| Version | 20260407 V1 |
| Route | `GET /welcome/summary`, `GET /welcome` (redirect) |
| Parent | — |
| Main Menu | Welcome |
| Sub Menu | Summary · default |
| Tab Order | 1: Summary · 2: Prototypes · 3: Projects |

Read-only health and configuration overview. Default landing screen for the application.

## Layout

Single-column, max-width 900px, centered. No form inputs — all writes go through Settings.

```
┌────────────────────────────────────────────┐
│         ██ WELCOME TO PROTOTYPER ██        │
│      Your local prototype operations hub   │
├────────────────────────────────────────────┤
│  🟢 START HERE                             │
│  ─────────────────────────────────────────│
│  ✅ Application Name      My Prototyper    │
│  ✅ Projects Directory    /home/user/...   │
│  ⚠️  Specifications Path  (default)        │
│  📌 Startup Scan          12 Projects, 4 Prototypes │
│  ⚠️  Homepage URL         (not set)        │
│  ❌ GitHub SSH            No key found     │
└────────────────────────────────────────────┘
```

## Welcome Banner

Full-width hero. Dark surface. Centered text: headline `Welcome to Prototyper` (32px bold accent) + subheadline `Your local prototype operations hub` (muted 16px). No actions.

## START HERE Card

Highlighted `cc-card`. Each row: icon + label + current value. Rows with ❌/⚠️ show inline fix instructions and a link to the relevant settings page.

| Icon | Meaning |
|------|---------|
| ✅ | Configured and accessible |
| ⚠️ | Set but may need attention |
| ❌ | Missing or inaccessible |
| 📌 | Informational |

| # | Item | Key | Status logic | Fix link |
|---|------|-----|-------------|----------|
| 1 | Application Name | `app_name` (settings) | ✅ if custom; ⚠️ if still default `Command Center` | Settings → General |
| 2 | Projects Directory | `PROJECTS_DIR` (env) | ✅ if path exists; ❌ if missing | Set in `.env`, restart |
| 3 | Specifications Path | `SPECIFICATIONS_PATH` (env) | ✅ if path exists; ⚠️ if using default | Set in `.env` if default is wrong |
| 4 | Startup Scan | backend metric | 📌 always shown | "Discovered N Projects and N Prototypes" |
| 5 | Homepage URL | `homepage_url` (settings) | ✅ if valid `https://` URL; ⚠️ if empty | Settings → General |
| 6 | GitHub SSH | runtime check | ✅ if `ssh -T git@github.com` exits 1 (authed); ❌ if exits 255 | GitHub SSH key setup guide |

When SSH is ❌, a collapsible "Alternatives" block shows: HTTPS credential store, GitHub CLI (`gh auth login`). Collapsed when SSH is ✅.

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (`app_name`, `homepage_url`) | None |
| `PROJECTS_DIR`, `SPECIFICATIONS_PATH` (env) | None |
| Startup scan counts | None |
| `ssh -T git@github.com` exit code | None |

## Open Questions

- Should the SSH check run on page load or be an explicit "Check" button to avoid startup delay?
- Should Summary show the application version or last-restart timestamp?
