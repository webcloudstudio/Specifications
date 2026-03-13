# Feature: Git Integration

**spec_v4 · 2026-03-11**

---

## Purpose

Surfaces each project's git status in the dashboard and flags projects that are not
following git conventions. The platform reads git state — it never modifies it.

---

## What the User Can Do

- See at a glance which projects have uncommitted changes
- See which projects have unpushed commits
- See current branch per project
- See whether git is initialized at all
- See governance compliance (git rules pass/fail)

---

## Screens

### Git Status (inline, Control Panel)

Per-project row:
- Git initialized: yes / no
- Current branch
- Uncommitted changes count
- Unpushed commits count
- Last commit message (truncated) and time

### Governance Checklist (within Project Detail)

Pass/fail list of git governance rules:
- Git initialized
- Remote configured
- No long-lived uncommitted changes
- Has pushed recently

---

## How It Works

Git status is read during each discovery scan by running standard git commands in each
project directory. The platform does not modify any project's git state.

---

## Governance Rules

Rules are advisory — they show warnings, they do not block anything.

Standard rules:
- Git must be initialized
- A remote must be configured
- Working tree should not be dirty for an extended period

Custom rules per project: [TBD] — may be declared in STACK.yaml.

---

## Out of Scope

- Performing git operations (commit, push, merge) on behalf of the user → not planned
- Branch management UI → not planned
- CI/CD pipeline integration → not planned
