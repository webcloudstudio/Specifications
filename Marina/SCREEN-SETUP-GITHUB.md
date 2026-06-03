# Screen: Setup — GitHub

| Field | Value |
|-------|-------|
| Version | 20260603 V8 |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Register your Scan Sources to share Git Projects. |
| Route | `GET /setup/github` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | GitHub |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | GitHub credential configuration and scan source management. Verify CLI authentication, check SSH connectivity, and configure which GitHub accounts and git URLs to scan repositories from. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/github |

## Header KPIs

Left column of the page header. Component type: **Status Light** (`mn-hdr-light`).

| State | Light | Condition |
|-------|-------|-----------|
| ✅ | `mn-hdr-light--ok` (green) | `gh auth status` ✅ AND SSH ✅ AND ≥1 source in `github_sources` |
| ⚠️ | `mn-hdr-light--warn` (amber) | ≥1 source configured BUT auth ❌ or SSH ❌ |
| ❌ | `mn-hdr-light--error` (red) | No sources configured OR `gh auth status` completely missing |

## Unconfigured State

If `gh auth status` fails and no sources are configured, the page opens with all cards in ❌ state and a banner:

```
┌──────────────────────────────────────────────────────────────┐
│  ❌  GitHub is not configured.                               │
│     Complete the steps below to enable repository access     │
│     and project downloads.                                   │
└──────────────────────────────────────────────────────────────┘
```

## Layout

Single-column, max-width 900px, centered. Three `mn-card` sections: Authentication, SSH, Source Accounts.

```
┌──────────────────────────────────────────────────────────────┐
│  🔐  AUTHENTICATION (GitHub CLI)                             │
│  ───────────────────────────────────────────────────────── │
│  Status:  ❌  Not authenticated                             │
│                                                              │
│  Steps:                                                      │
│  1. Open a terminal                                          │
│  2. Run:  gh auth login                                      │
│  3. Choose GitHub.com → HTTPS → Yes (store credentials)     │
│  4. Complete browser OAuth flow                              │
│  5. Return here and click Re-check                           │
│                              [Re-check Auth]                 │
├──────────────────────────────────────────────────────────────┤
│  🔑  SSH KEY (for private repo cloning)                      │
│  ───────────────────────────────────────────────────────── │
│  Status:  ❌  No SSH key found                               │
│                                                              │
│  Steps:                                                      │
│  1. Generate a key: ssh-keygen -t ed25519 -C "you@email"    │
│  2. Copy key: cat ~/.ssh/id_ed25519.pub                      │
│  3. Add to GitHub: github.com → Settings → SSH keys          │
│  4. Test: ssh -T git@github.com                              │
│  5. Return here and click Re-check                           │
│                                                              │
│  Alternative: use HTTPS with gh auth login (no SSH needed).  │
│                              [Re-check SSH]                  │
├──────────────────────────────────────────────────────────────┤
│  📦  SCAN SOURCES                                            │
│  ───────────────────────────────────────────────────────── │
│  GitHub accounts, organisations, or git URLs to scan.        │
│  The Git Scan tab fetches repos from all sources listed here.│
│                                                              │
│  ┌──────────────────────────────────┬────────┬────────────┐  │
│  │ Source                           │ Type   │ Actions    │  │
│  ├──────────────────────────────────┼────────┼────────────┤  │
│  │ webcloudstudio                   │ User   │ [Remove]   │  │
│  │ my-org                           │ Org    │ [Remove]   │  │
│  │ https://github.com/other/repo    │ URL    │ [Remove]   │  │
│  ├──────────────────────────────────┼────────┼────────────┤  │
│  │ [ github username, org, or URL ] │        │ [Add]      │  │
│  └──────────────────────────────────┴────────┴────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Collapsible Card Behaviour

Every card is collapsible via Bootstrap 5 collapse. The card header acts as the toggle.

| Rule | Detail |
|------|--------|
| Start expanded | Card status is not OK |
| Start collapsed | Card status is OK |
| Collapsed header | Shows a `✅ OK` badge so the status is visible without expanding |

Status criteria per card:

| Card | OK when |
|------|---------|
| AUTHENTICATION | `gh auth status` exits 0 |
| SSH KEY | `ssh -T git@github.com` returns `Hi {user}` |
| SCAN SOURCES | ≥1 source in `github_sources` |

## AUTHENTICATION Card

Shows the result of `gh auth status` (run server-side). Displays:
- ✅ — `Authenticated as: {github_username}` (from `gh auth status --show-token` output)
- ❌ — `Not authenticated` + step-by-step guide

`[Re-check Auth]` button triggers `POST /api/setup/github/check-auth` and updates the card in place.

When ❌: the step-by-step guide is shown expanded. When ✅: guide is collapsed (hidden by default, expandable via `Show steps again` link). The authenticated identity is shown when ✅: `Authenticated as: {user}` (parsed from `gh auth status` output).

**Install instruction (Ubuntu / WSL2):** The guide must show `sudo apt install gh` as the first step before `gh auth login`. Do not show brew or other package managers.

## SSH Card

Shows the result of `ssh -T git@github.com` (run server-side, exits 1 = authenticated, exits 255 = no connection).

- ✅ — `SSH authenticated to GitHub` (exit code 1, message contains `Hi {user}`)
- ❌ — `No SSH connection` + step-by-step guide + HTTPS alternative note

`[Re-check SSH]` button triggers `POST /api/setup/github/check-ssh` and updates the card in place.

HTTPS alternative block (shown when SSH is ❌):

> **Using HTTPS instead of SSH**
> If you prefer not to set up SSH keys, `gh auth login` with HTTPS stores credentials for `git clone`. Downloads on the Repositories tab will use HTTPS clones automatically when SSH is unavailable.

## SCAN SOURCES Card

Lists the scan sources the Git Scan tab will pull repositories from. A source can be a GitHub username, a GitHub organisation, or any HTTPS git URL (e.g. `https://github.com/other/repo`).

| Element | Behaviour |
|---------|-----------|
| Source list | Rows from `github_sources` table. Each row: source value, type (User / Org / URL), Remove button. |
| Add input | Text field accepting a GitHub username, org name, or HTTPS git URL. `[Add]` calls `POST /api/setup/github/sources`. Type is auto-detected: URL if the value contains `://`; otherwise Marina attempts to resolve it via the GitHub API to distinguish User from Org. Unresolvable values are saved as type `Unknown`. |
| Remove | `DELETE /api/setup/github/sources/{id}`. Confirmation prompt if source has repos in `github_repos`. |
| Default | On first run, Marina reads the upstream remote URL from the local git repository (`git remote get-url origin`), extracts the owner, and seeds it as the initial source. |

Type detection rules:

| Input | Detected Type |
|-------|--------------|
| Contains `://` (e.g. `https://github.com/org/repo`) | URL |
| GitHub API `/users/{name}` returns `type: User` | User |
| GitHub API `/users/{name}` returns `type: Organization` | Org |
| API unreachable or 404 | Unknown |

Source type determines how the Git Scan fetches repos:
- **User / Org** — calls the GitHub API: `GET /users/{name}/repos` or `GET /orgs/{name}/repos`
- **URL** — treats the URL as a single repository to clone/track directly; no API listing

Source rows determine the columns on the Git Scan tab — one column per source, plus an "Other" column.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/setup/github/check-auth` | — | Auth card HTML fragment (✅ or ❌) |
| POST | `/api/setup/github/check-ssh` | — | SSH card HTML fragment (✅ or ❌) |
| POST | `/api/setup/github/sources` | `source` | Updated source list fragment |
| DELETE | `/api/setup/github/sources/{id}` | — | Updated source list fragment |

The `/api/setup/config` endpoint is not used by this screen. `github_username` is not stored or required — authenticated identity is read from `gh auth status` output only.

## Data Flow

| Reads | Writes |
|-------|--------|
| `github_sources` table | `github_sources` table (add/remove) |
| `gh auth status` (subprocess) | None |
| `ssh -T git@github.com` (subprocess) | None |
| GitHub API `/users/{name}` (type detection on add) | None |

## Open Questions

- Should HTTPS clone be auto-selected when SSH is unavailable? V1: the Download action on the Repositories tab prefers SSH but falls back to HTTPS automatically when `ssh -T git@github.com` fails.
- Should this screen support GitHub Enterprise Server hostnames? V1: github.com only.
