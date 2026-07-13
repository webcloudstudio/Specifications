# Feature: Repository Scanner

| Field | Value |
|-------|-------|
| Version | 20260713 V2 |
| Description | Discovers local repositories, repository provenance, project metadata, git state, and callable-surface artifacts for registration and exploration. |
| Depends On | DATABASE.md, FEATURE-PROJECT-REGISTRATION.md, FEATURE-CAPABILITY-DISCOVERY.md |
| Provides | POST /api/projects/scan, POST /api/repositories/sync |

**Description:** The scanner is read-only. It creates candidate and registered project projections from
filesystem, metadata, documentation, git, GitHub cache, and capability artifacts. It does not execute
project scripts and does not decide whether a capability may be exposed or invoked.

## Trigger

- Application startup.
- Welcome → Discover Projects.
- Setup → Git Scan.
- Setup → Repositories sync or clone completion.
- Projects → Dashboard → Rescan.
- Project Detail → Rediscover Project.

## Scan Sequence

1. Resolve `PROJECTS_DIR`; fail with an actionable setup state if it is absent or unreadable.
2. Enumerate non-hidden child directories and identify git repositories.
3. Read git identity and state:
   - canonical repository root
   - `origin` and other remotes
   - remote host, owner, repository name
   - current and default branch
   - HEAD SHA and subject
   - HEAD author name, email, and timestamp
   - HEAD committer timestamp and commit age
   - working-tree status
   - staged, unstaged, and untracked file counts
   - ahead/behind counts where upstream is available
   - latest known remote push timestamp from the repository source cache
4. Parse `METADATA.md` and preserve unknown fields.
5. Parse `AGENTS.md` or `CLAUDE.md` structured sections.
6. Delegate callable-surface parsing to FEATURE-CAPABILITY-DISCOVERY.md.
7. Reconcile GitHub cache rows by normalized remote URL, never by repository name alone.
8. Upsert the candidate/registered project projection and discovery records.
9. Mark capabilities missing from the current scan as no longer current; retain history.
10. Return a scan summary with added, changed, removed, invalid, registered, and unregistered counts.

## Repository Eligibility

- A directory with `.git/` is a repository candidate, whether or not it has `METADATA.md`.
- A repository without a remote remains eligible for local registration and is marked `LOCAL_ONLY`.
- A non-Git directory is not a project candidate in the initial build.
- GitHub origin is not required; GitLab, Bitbucket, self-hosted Git, and local remotes are retained by host.
- Hidden directories and nested repositories are excluded unless explicitly configured.

## Git Evidence

The scanner records command results and normalized values. A failed optional git query produces `UNKNOWN`
and a warning rather than aborting the repository scan. Credentials and remote URLs containing embedded
secrets are redacted before storage and display.

## Reads

- `PROJECTS_DIR` filesystem.
- Repository git metadata and working tree.
- `METADATA.md`, `AGENTS.md`, `CLAUDE.md`, `bin/`, `.mcp.json`, and `mcp/` declarations.
- `github_sources` and `github_repos` cache.

## Writes

- `projects`, `project_sources`, `project_discovery_runs`, `project_capabilities`, and warnings.
- `github_repos` cross-links and `platform_stats` counters.
- Discovery events for material changes.

## Guardrails

- Never run a project operation while scanning.
- Never infer remote identity from a directory name when a git remote exists.
- Never overwrite user-managed namespace, tags, or registration state during a scan.
- Never delete historical discovery records.

## Open Questions

- None.
