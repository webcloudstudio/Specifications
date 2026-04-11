# Screen: Welcome

**Description:** Landing screen with three sub-tabs: Summary (read-only health/config overview), Prototypes (searchable list), and Projects (searchable list).

## Menu Navigation

Main Menu: Welcome
Sub Menu: Summary (Default)

## Routes

```
GET /welcome              → redirects to /welcome/summary
GET /welcome/summary      Default sub-tab. Read-only configuration health view.
GET /welcome/prototypes   Searchable prototype list.
GET /welcome/projects     Searchable project list.
```

The app root (`/`) redirects to `/welcome/summary` when no other default is set.

---

## Welcome Sub-Bar

Visible only when `Welcome` is the active top-level tab. Three tabs:

| Tab | Route | Default |
|-----|-------|---------|
| Summary | `/welcome/summary` | Yes |
| Prototypes | `/welcome/prototypes` | No |
| Projects | `/welcome/projects` | No |

---

## Sub-Tab: Summary

Single-column read-only view. Max-width 900px, centered. No form inputs — use Settings (`/settings/general`) to change values.

### Welcome Banner

Full-width hero at top. Dark surface (`--cc-surface`). Centered text.

| Element | Content |
|---------|---------|
| Headline | `Welcome to Prototyper` — 32px, bold, accent color |
| Subheadline | `Your local prototype operations hub` — muted, 16px |

No buttons or actions in the banner. Visual only.

### START HERE Card

Card (`cc-card`) highlighted with an accent background. Purpose: verify configuration is complete and healthy.

#### Card Header

`START HERE` — large, bold, accent color, green circle indicator (●).

#### Checklist Items

Each item is a read-only row: icon + label + current value/description. Items with a problem show a link to the relevant settings page.

Status icon pattern:

| Icon | Meaning |
|------|---------|
| ✅ | Configured and accessible |
| ⚠️ | Set but may need attention |
| ❌ | Missing or inaccessible — action required |
| 📌 | Informational |

**Configuration items:**

| # | Item | Key | Status logic | Instructions when not set |
|---|------|-----|-------------|--------------------------|
| 1 | Application Name | `app_name` (settings table) | ✅ if set and not the default `Command Center`; ⚠️ if still default | "Set a custom name in [Settings → General](/settings/general)" |
| 2 | Projects Directory | `PROJECTS_DIR` (env) | ✅ if path exists and is readable; ❌ if missing or inaccessible | "Set `PROJECTS_DIR` in `.env` and restart the server" |
| 3 | Specifications Path | `SPECIFICATIONS_PATH` (env) | ✅ if path exists and is readable; ⚠️ if not set (defaults to `../Specifications`) | "Set `SPECIFICATIONS_PATH` in `.env` if the default is wrong" |
| 4 | Startup Scan | backend metric | 📌 | "Discovered {N} Projects and {N} Prototypes" — always shown, green |
| 5 | Homepage URL | `homepage_url` (settings table) | ✅ if a valid `https://` URL is stored; ⚠️ if empty | "Set your GitHub Pages URL in [Settings → General](/settings/general)" |
| 6 | GitHub SSH | runtime check | ✅ if `ssh -T git@github.com` exits with code 1 (authenticated); ❌ if exits 255 (no key/timeout) | "No SSH key found for GitHub. [How to set up SSH keys →](https://docs.github.com/authentication/connecting-to-github-with-ssh)" |

Each ❌ or ⚠️ row renders instructions inline below the value, including a link to the relevant fix. ✅ rows show only the current value.

#### GitHub Connectivity Note

Below the SSH row, if SSH is ❌, show a collapsible "Alternatives" block:

> **Other ways to push commits:**
> - HTTPS with a stored credential (`git credential-store` or macOS Keychain)
> - GitHub CLI: run `gh auth login` to authenticate via browser

Collapsed by default when SSH is ✅.

### Layout ASCII

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
│       → Set in Settings / General          │
│  ❌ GitHub SSH            No key found     │
│       → How to set up SSH keys             │
└────────────────────────────────────────────┘
```

## Data Flow — Summary

| Reads | Writes |
|-------|--------|
| `settings` table (`app_name`, `homepage_url`) | None |
| `PROJECTS_DIR`, `SPECIFICATIONS_PATH` from env | None |
| Startup scan metrics (project + prototype counts) | None |
| `ssh -T git@github.com` exit code (runtime check) | None |

Summary is fully read-only. All writes go through `Settings / General`.

---

## Sub-Tab: Prototypes

Simple searchable pane. No action buttons. Full-width, no max-width cap.

### Layout

```
┌────────────────────────────────────────────┐
│  [🔍 Search prototypes...               ]  │
│  ──────────────────────────────────────── │
│  PROTOTYPE  MyApp       dev   My app desc  │
│  IDEA       NewThing    dev   New idea     │
│  ACTIVE     CoreService prod  Core service │
│  ...                                       │
└────────────────────────────────────────────┘
```

### List

One row per prototype from `GET /api/prototypes`. Columns:

| Column | Source | Notes |
|--------|--------|-------|
| Status badge | `METADATA.md → status` | Colored pill per UI-GENERAL status colors |
| Name | `METADATA.md → display_name` | Plain text, no link |
| Namespace | `METADATA.md → namespace` | Muted, omit if empty |
| Short description | `METADATA.md → short_description` | Truncate at 80 chars |

Sorted by name by default.

### Search

Single text input above the list. Client-side. Filters on any visible field: name, status, namespace, short_description. Case-insensitive substring match. No round-trip.

### Empty State

If no prototypes found:

> *No prototypes found. Configure `SPECIFICATIONS_PATH` in `.env`.*

---

## Sub-Tab: Projects

Identical layout and behavior to the Prototypes sub-tab, applied to discovered projects.

### List

One row per project from `GET /api/projects` (or the scanner results). Columns:

| Column | Source | Notes |
|--------|--------|-------|
| Status badge | `projects.status` | Colored pill per UI-GENERAL status colors |
| Name | `projects.display_name` | Plain text, no link |
| Namespace | `projects.namespace` | Muted, omit if `development` |
| Short description | `projects.short_description` | Truncate at 80 chars |

### Search

Same as Prototypes: single text input, client-side, any-field substring match.

### Empty State

If no projects found:

> *No projects found. Configure `PROJECTS_DIR` in `.env`.*

---

## Open Questions

- Should the SSH check run on page load or be an explicit "Check" button (to avoid startup delay)?
- Should Summary show the Prototyper version or last-restart timestamp?
