# Feature: Project Metadata Standards

**spec_v3 · 2026-03-10**

---

## Purpose

Project Metadata Standards define the plain text file contracts that projects use to
describe themselves to GAME and to the AI development environment. These files are the
primary interface between a project and the platform — no central database registration
required.

---

## User Interactions

- Project maintainers edit plain text files in their project directories
- GAME reads these files on each scan with no additional steps
- The UI reflects the content of these files (endpoints, links, card metadata)
- Missing or malformed files are reported as compliance warnings in CONTROL-PANEL

---

## UI Screens

No dedicated UI screen — this is a contract specification.

Metadata is surfaced through CONTROL-PANEL (links, bookmarks, type-specific info)
and GITHUB-PUBLISHER (portfolio cards).

---

## Inputs & Outputs

- **Inputs:**
  - File contents from project directories
- **Outputs:**
  - Project metadata consumed by CONTROL-PANEL, GITHUB-PUBLISHER, and GIT-INTEGRATION

---

## Interfaces With

- PROJECT-DISCOVERY: reads all metadata files during scan
- CONTROL-PANEL: displays endpoints, bookmarks, and links from metadata
- GITHUB-PUBLISHER: reads git_homepage.md and git_site_config.md for portfolio
- CONFIGURATION-MANAGEMENT: reads CLAUDE.md structure for AI config generation

---

## Contracts

### CLAUDE.md — AI Context File

**Location:** Project root (`CLAUDE.md`)
**Purpose:** Provides context to the AI assistant about this project.
**Authority:** Primary source for stack info, commands, endpoints, bookmarks.

Standard sections (parsed by GAME):

```markdown
# [Project Title]
[One or two paragraph description]

## Dev Commands
[Commands to start, stop, test, build — fenced code block or bullet list]

## Service Endpoints
[URLs where the service runs locally]
- Local: http://localhost:PORT

## Bookmarks
### [Category]
- [Link Name](URL)

## Architecture
[Free-form description of the project structure]
```

Variant section headings are normalized to standard names on read.
Sections missing from a project's CLAUDE.md are noted as compliance gaps.
GAME can generate a stub CLAUDE.md for projects that don't have one.

---

### git_homepage.md — Portfolio Card File

**Location:** Project root (`git_homepage.md`)
**Purpose:** Defines the project's card on the GitHub Pages portfolio.
**Format:** YAML frontmatter; body is unused.

```yaml
---
Title: Project Display Name
Description: One to two sentence description of what the project does.
Tags: tag1, tag2, tag3
Image: images/project-name.webp
Show on Homepage: true
---
```

| Field | Required | Notes |
|-------|----------|-------|
| Title | Yes | Display name on portfolio card |
| Description | Yes | Shown under the title on the card |
| Tags | No | Comma-separated; shown as badges on the card |
| Image | No | Relative path to image in portfolio static directory |
| Show on Homepage | Yes | `true` = include in published portfolio |

---

### Links.md — Project URL Directory

**Location:** Project root (`Links.md`)
**Purpose:** A curated list of URLs related to the project (production, staging, docs, etc.)
**Format:** Markdown table

```markdown
| Name | URL | Notes |
|------|-----|-------|
| Production | https://... | Live site |
| Staging | https://... | For testing |
| Docs | https://... | API documentation |
```

All rows are surfaced as quick links in the CONTROL-PANEL project detail view.

---

### git_site_config.md — Portfolio Site Branding

**Location:** GAME project root (`git_site_config.md`)
**Purpose:** Controls site-wide branding for the GitHub Pages portfolio.
**Format:** YAML frontmatter + markdown body (home page content).

```yaml
---
site_name: "Your Name"
site_tagline: "One-line tagline"
github_url: "https://github.com/yourname"
theme: "dark"
---

# Welcome

Home page body content in markdown.
```

Full field reference: see GITHUB-PUBLISHER.

---

## File Precedence

When the same information exists in multiple places, precedence is:

1. git_homepage.md frontmatter (for portfolio card fields)
2. CLAUDE.md sections (for endpoints, bookmarks, stack info)
3. PROJECT-DISCOVERY computed values (directory name → display title)

---

## Out of Scope

- bin/ script headers → SERVICE-SCRIPT-STANDARDS
- Tag colors → TAG-MANAGEMENT
- AI configuration profiles → CONFIGURATION-MANAGEMENT
