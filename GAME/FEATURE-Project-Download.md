# FEATURE: Project-Download

| Field       | Value |
|-------------|-------|
| Version     | 20260510 V1 |
| Description | Clones a GitHub repository into PROJECTS_DIR, creates a minimal METADATA.md, and triggers a scan to register the project. Used by the Welcome — GitHub screen's Download button. |
| Depends On  | DATABASE-github-repos-001.md, FEATURE-SCANNER.md |
| Provides    | `POST /api/github/download` |

## What It Does

Project-Download is a single atomic operation: given a GitHub repo, clone it to disk and register it as a project.

1. Clone the repository into `PROJECTS_DIR/{repo_name}` using SSH (`ssh_url`) if GitHub SSH is ✅, or HTTPS (`clone_url`) otherwise.
2. Create a minimal `METADATA.md` in the cloned directory if one does not already exist:
   ```
   display_name: {repo_name title-cased}
   status: PROTOTYPE
   git_repo: {ssh_url}
   ```
3. Run `POST /api/scan` to register the project in the `projects` table and cross-link it in `github_repos`.
4. Return the updated row fragment to the caller (HTMX swap).

## API Endpoint

```
POST /api/github/download
```

**Request body (JSON):**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `repo_name` | string | Yes | Short repo name (e.g. `my-app`) |
| `clone_url` | string | Yes | HTTPS clone URL (fallback if SSH fails) |
| `ssh_url` | string | Yes | SSH clone URL (preferred) |

**Response:**

- 200: Updated table row HTML fragment. `is_downloaded` is now `1`. Status badge changes to `✅ Local`. Action changes to `Open ↗`.
- 409: `{"error": "already_exists"}` — directory already exists in `PROJECTS_DIR`.
- 500: `{"error": "clone_failed", "detail": "..."}` — git clone exited non-zero.

## Clone Strategy

| Condition | Clone method |
|-----------|-------------|
| `ssh -T git@github.com` exits 1 (SSH authed) | `git clone {ssh_url} {PROJECTS_DIR}/{repo_name}` |
| SSH not available | `git clone {clone_url} {PROJECTS_DIR}/{repo_name}` |

Timeout: 120 seconds. Long clones (large repos) stream progress via SSE if the client supports it; otherwise the button stays in the `Cloning…` spinner state until the response returns.

## Target Directory

Always: `{PROJECTS_DIR}/{repo_name}` where `PROJECTS_DIR` is the env var value. No subdirectory nesting. No configurable path.

If the target directory already exists, the operation returns 409 without cloning.

## METADATA.md Creation

A minimal `METADATA.md` is written only if one does not already exist. Fields written:

```markdown
display_name: {repo_name title-cased, hyphens replaced with spaces}
status: PROTOTYPE
git_repo: {ssh_url}
```

If `METADATA.md` already exists (e.g. repo already contained one), it is left unchanged.

## Scan Trigger

After a successful clone, calls `POST /api/scan` internally (server-side, not a browser request). This populates the `projects` row and runs the Phase 3 cross-link to set `github_repos.project_id` and `projects.github_repo_id`.

## Error Handling

| Condition | Response | UI behaviour |
|-----------|----------|-------------|
| `PROJECTS_DIR` not set | 500 with error | Button shows `Failed` + `Configure PROJECTS_DIR in .env` |
| Directory already exists | 409 | Button shows `Already downloaded` (muted), row status updates to `✅ Local` |
| `git clone` fails (auth, network, disk) | 500 with stderr detail | Button shows `Failed` + inline error text from stderr |
| Scan fails after clone | 200 (clone succeeded) | Row updates to `✅ Local`; scan error logged server-side, not surfaced to user |

## Feasibility Notes

- Operation is server-side only; no client-side git.
- SSH key must be configured for private repos. If SSH is unavailable, HTTPS clone is used — this may prompt for credentials interactively, which will hang. For HTTPS fallback to work, the `gh` credential helper must be configured (`gh auth setup-git`).
- Large repositories may exceed the 120-second timeout. V1 does not support resumable clones.

## Open Questions

- Should the download also run `setup.sh` if one exists in the spec directory for that project? V1: no — just clone and create minimal METADATA.md.
- Should there be progress streaming (SSE) for large clones? V1: spinner until complete.
- Should the feature support GitLab or Bitbucket URLs? V1: GitHub only.
