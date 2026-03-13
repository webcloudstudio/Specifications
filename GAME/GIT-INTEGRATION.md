# Git Integration

**Read-only git status display.** Surfaces each project's git state in the dashboard. Never modifies git.

---

## Capabilities

- Per-project: branch, uncommitted changes count, unpushed commits count, last commit message
- Governance checklist: initialized, remote configured, not persistently dirty
- Status read during each discovery scan

## Governance Rules (advisory, not blocking)

- Git must be initialized
- A remote must be configured
- Working tree should not be dirty for extended periods

## Data Flow

| Reads From | Writes To |
|------------|-----------|
| Filesystem git state | CONTROL-PANEL (git status display) |
| | PROJECT-DISCOVERY (compliance flags) |
