# The Contract

**spec_v4 · 2026-03-11**

---

## What Is a Contract?

A contract is a file a project provides. It has a defined format. The platform reads it.
In exchange, the project gains a platform capability.

No code change to the platform is needed. The project adds the file; the platform
discovers it on the next scan.

Contracts are committed to git. They are readable by humans and AI agents. They do not
depend on the platform being running.

---

## Contract 1: The Operations Contract

**File:** `bin/<name>.sh` (or any script in the `bin/` directory)
**What you get:** A clickable button in the dashboard that runs the script

The script must contain a declaration block in its first 20 lines:

```
# CommandCenter Operation
# Name: Service Start
# Port: 3000
```

- `Name` is required. It becomes the button label.
- `Port` is optional. Declaring it enables health monitoring for that port.

A project can have any number of scripts in `bin/`. Each one that has this block
becomes a separate button. See **OPERATIONS.md** for what else scripts should expose.

---

## Contract 2: The Portfolio Contract

**File:** `git_homepage.md` at the project root
**What you get:** A card on the published portfolio site

```yaml
---
Title: My Project
Description: What this project does in one or two sentences.
Tags: web, tool, open-source
Image: images/my-project.webp
Show on Homepage: true
---
```

- `Show on Homepage: false` hides the project from the portfolio without removing the file.
- Tags appear as badges on the card.
- Image is optional; a default is used if omitted.

---

## Contract 3: The AI Context Contract

**File:** `CLAUDE.md` at the project root
**What you get:** Populated links and endpoints in the dashboard; correct AI behavior in sessions

```markdown
# My Project
One paragraph description of what this project is.

## Dev Commands
How to start, stop, test, build.

## Service Endpoints
- Local: http://localhost:3000

## Bookmarks
### Useful Links
- [Production Site](https://...)
```

The platform reads the `Service Endpoints` and `Bookmarks` sections and surfaces them
as quick links. The AI agent reads the whole file as its working context for this project.

See **PERSISTENCE.md** for how `CLAUDE.md` is also used to store project metadata.

---

## Contract 4: The Stack Contract

**File:** `STACK.yaml` at the project root
**What you get:** Stack badges in the dashboard; governance rule checking

```yaml
language: Python
framework: Flask
requires:
  - git
  - venv
```

The platform reads `language` and `framework` for display. The `requires` list is
checked on scan — missing items are flagged as compliance gaps.

---

## Contract 5: The Links Contract

**File:** `Links.md` at the project root
**What you get:** A quick-links panel in the project detail view

```markdown
| Name | URL | Notes |
|------|-----|-------|
| Production | https://... | Live site |
| Docs | https://... | API docs |
```

Every row in the table becomes a link in the UI. No additional setup.

---

## The Full Picture

A project that implements all five contracts is fully governed:

| Capability | Requires |
|-----------|---------|
| Operation buttons in dashboard | Contract 1 (bin/ header) |
| Portfolio card published | Contract 2 (git_homepage.md) |
| Endpoint links in dashboard | Contract 3 (CLAUDE.md) |
| AI agent working context | Contract 3 (CLAUDE.md) |
| Stack compliance checking | Contract 4 (STACK.yaml) |
| Quick-links panel | Contract 5 (Links.md) |
| Health monitoring | Contract 1 + Port declared |

A project missing a contract is not broken. It simply does not have that capability in
the platform. The dashboard reports what is missing.

---

## Contracts Are Not Required by the Platform

A project with no contracts at all will still appear in the dashboard — just as a name
with no buttons, no links, and a list of compliance gaps. The developer adds contracts
when they want the capability. The platform never blocks a project for non-compliance.
