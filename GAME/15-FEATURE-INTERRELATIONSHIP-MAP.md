# Feature Interrelationship Map

**Dependency graph.** Which features produce data that others consume.

---

## Core Chain: File → Button → Process → Health

```
bin/start.sh with CommandCenter header
  → SERVICE-SCRIPT-STANDARDS (defines format)
  → PROJECT-DISCOVERY (reads header, registers operation)
  → CONTROL-PANEL (renders button)
  → OPERATIONS-ENGINE (launches script)
  → PROCESS-MONITOR (streams log)
  → MONITORING-HEARTBEATS (polls health)
```

## Portfolio Chain: Metadata → Card → Publish

```
METADATA.md with show_on_homepage: true
  → PROJECT-DISCOVERY (reads on scan)
  → GITHUB-PUBLISHER (builds card)
  → User clicks Rebuild → static site
  → User clicks Publish → GitHub Pages
```

## AI Workflow Chain: Ticket → Build → Review

```
IDEA → PROPOSED (add plan) → READY (add criteria)
  → IN DEVELOPMENT (AI session)
  → TESTING (human validates)
  → DONE (or rework → READY/PROPOSED)
```

## Dependency Table

| Feature | Reads From | Writes To |
|---------|------------|-----------|
| SERVICE-SCRIPT-STANDARDS | bin/ files | Operation registry → DISCOVERY |
| PROJECT-METADATA-STANDARDS | METADATA.md, CLAUDE.md | Parsed metadata → DISCOVERY |
| PROJECT-DISCOVERY | Filesystem, standards, git | Project store → PANEL, ENGINE, PUBLISHER |
| CONTROL-PANEL | DISCOVERY, ENGINE, MONITOR, TAGS | Launch requests → ENGINE, state changes |
| OPERATIONS-ENGINE | PANEL (requests), DISCOVERY (registry) | Process handle → MONITOR, run records |
| PROCESS-MONITOR | ENGINE (handles), log files | Stop signals, status → PANEL nav bar |
| WORKFLOW-STATES | User input, USAGE-ANALYTICS | Ticket state → PANEL |
| GITHUB-PUBLISHER | DISCOVERY (metadata), docs/ dirs | Published portfolio |
| TAG-MANAGEMENT | User input, METADATA.md | Tags + colors → PANEL |
| CONFIGURATION-MANAGEMENT | Profile YAML, CLAUDE.md | AI config files |
| USAGE-ANALYTICS | AI session JSONL logs | Usage summary → PANEL nav bar |
| GIT-INTEGRATION | Filesystem git state | Git status → PANEL, compliance flags |
| MONITORING-HEARTBEATS | Declared ports, running processes | Health status → PANEL, alerts |

## Implementation Priority

1. Standards (contracts, no code)
2. PROJECT-DISCOVERY (foundation)
3. CONTROL-PANEL + OPERATIONS-ENGINE + PROCESS-MONITOR (core loop)
4. GIT-INTEGRATION + TAG-MANAGEMENT + USAGE-ANALYTICS (enrichment)
5. GITHUB-PUBLISHER + CONFIGURATION-MANAGEMENT (pipelines)
6. WORKFLOW-STATES (complex lifecycle)
7. MONITORING-HEARTBEATS (polling daemon)
