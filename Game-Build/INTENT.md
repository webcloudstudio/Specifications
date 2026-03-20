# Intent

**Version:** 20260320 V1
**Description:** Project intent: why it exists, who it serves, and scope

A solo practitioner or small team managing multiple AI-built projects needs one methodology. If your projects have custom capabilities then it is difficult to manage. Projects become easier to manage when they are standard in format.

GAME is the dashboard that discovers, monitors, and operates projects that follow the standard. It scans project directories, reads METADATA.md and bin/ script headers, and presents a unified operations interface.

## Core Principle

**Contract-earns-capability.** Add the file, the platform discovers the capability:

| File Added | Capability Earned |
|------------|-------------------|
| METADATA.md | Project appears in dashboard |
| AGENTS.md | Bookmarks, endpoints, dev commands extracted |
| bin/start.sh with header | Start button appears |
| bin/daily.sh with `# Schedule:` | Daily automation registered |
| doc/index.html | Documentation link appears |
| health: /health in METADATA | Health monitoring enabled |
| port: NNNN in METADATA | Service monitoring + heartbeat enabled |
| show_on_homepage: true | Portfolio card generated |

## What This Is Not

- Not a CI/CD pipeline — it's an operations dashboard
- Not a deployment tool — it runs local dev services
- Not a project management tool — the workflow/tickets are lightweight helpers, not JIRA
