# Screen: Setup — GitHub

| Field | Value |
|-------|-------|
| Version | 20260602 V4 |
| Header Background | `mn-hdr-bg--git` |
| Route | `GET /setup/github` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | GitHub |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | GitHub credential configuration and scan source management. Set GitHub username, verify CLI authentication, check SSH connectivity, and configure which GitHub accounts to scan repositories from. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/github |

## Header KPIs

Left column of the page header. Component type: **Status Light** (`mn-hdr-light`).

| State | Light | Condition |
|-------|-------|-----------|
| ✅ | `mn-hdr-light--ok` (green) | `github_username` set AND `gh auth status` ✅ AND SSH ✅ |
| ⚠️ | `mn-hdr-light--warn` (amber) | `github_username` set BUT auth ❌ or SSH ❌ |
| ❌ | `mn-hdr-light--error` (red) | `github_username` not set |

## Unconfigured State

If `github_username` is not set and `gh auth status` fails, the page opens with all three cards in ❌ state and a prominent banner:

```
┌──────────────────────────────────────────────────────────────┐
│  ❌  GitHub is not configured.                               │
│     Complete the three steps below to enable repository      │
│     access and project downloads.                            │
└──────────────────────────────────────────────────────────────┘
```

## Layout

Single-column, max-width 900px, centered. Four `mn-card` sections stacked vertically: Username, Authentication, SSH, Source Accounts.

```
┌──────────────────────────────────────────────────────────────┐
│  👤  GITHUB USERNAME                                         │
│  ───────────────────────────────────────────────────────── │
│  GitHub Username   [ edbarlow                           ▏ ] │
│  ─────────────────────────────────────────────────────────  │
│  ✅  Username saved.                                         │
├──────────────────────────────────────────────────────────────┤
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
│  📦  SOURCE ACCOUNTS                                         │
│  ───────────────────────────────────────────────────────── │
│  GitHub accounts and organisations to scan for repositories. │
│  The Git Scan tab fetches repos from all sources listed here.│
│                                                              │
│  ┌─────────────────┬────────┬──────────────────────────────┐ │
│  │ Account         │ Type   │ Actions                      │ │
│  ├─────────────────┼────────┼──────────────────────────────┤ │
│  │ webcloudstudio  │ User   │ [Remove]                     │ │
│  ├─────────────────┼────────┼──────────────────────────────┤ │
│  │ [ Add account ] │        │ [Add]                        │ │
│  └─────────────────┴────────┴──────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## GITHUB USERNAME Card

Single inline-editable field. Tab-out triggers save via `POST /api/setup/config` with `key=github_username`.

- ✅ after save if non-empty.
- ❌ if empty.

**Auto-derive:** On page load, if `github_username` is not set, Marina reads the upstream remote URL from the local git repository (`git remote get-url origin`) and extracts the username. Parsed value is pre-filled into the field (not saved until user tabs out or edits).

## AUTHENTICATION Card

Shows the result of `gh auth status` (run server-side). Displays:
- ✅ — `Authenticated as: {github_username}` (from `gh auth status --show-token` output)
- ❌ — `Not authenticated` + step-by-step guide

`[Re-check Auth]` button triggers `POST /api/setup/github/check-auth` and updates the card in place.

When ❌: the step-by-step guide is shown expanded. When ✅: guide is collapsed (hidden by default, expandable via `Show steps again` link).

**Install instruction (Ubuntu / WSL2):** The guide must show `sudo apt install gh` as the first step before `gh auth login`. Do not show brew or other package managers.

## SSH Card

Shows the result of `ssh -T git@github.com` (run server-side, exits 1 = authenticated, exits 255 = no connection).

- ✅ — `SSH authenticated to GitHub` (exit code 1, message contains `Hi {user}`)
- ❌ — `No SSH connection` + step-by-step guide + HTTPS alternative note

`[Re-check SSH]` button triggers `POST /api/setup/github/check-ssh` and updates the card in place.

HTTPS alternative block (shown when SSH is ❌):

> **Using HTTPS instead of SSH**
> If you prefer not to set up SSH keys, `gh auth login` with HTTPS stores credentials for `git clone`. Downloads on the Repositories tab will use HTTPS clones automatically when SSH is unavailable.

## SOURCE ACCOUNTS Card

Lists the GitHub accounts and organisations that the Git Scan will fetch repositories from. The authenticated user's account is always available; additional accounts are managed here.

| Element | Behaviour |
|---------|-----------|
| Account list | Rows from `github_sources` table. Each row: account name, type (User/Org), Remove button. |
| Add input | Text field + `[Add]` button. Calls `POST /api/setup/github/sources`. Validates the account exists on GitHub before saving. |
| Remove | `DELETE /api/setup/github/sources/{account}`. Confirmation prompt if source has repos in `github_repos`. |
| Default | `webcloudstudio` is seeded as the default source on first run if the authenticated user is `webcloudstudio`. Otherwise the authenticated GitHub username is used as the initial source. |

Source accounts determine the columns on the Git Scan tab — one column per source, plus an "Other" column for projects without a GitHub repo.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/setup/github/check-auth` | — | Auth card HTML fragment (✅ or ❌) |
| POST | `/api/setup/github/check-ssh` | — | SSH card HTML fragment (✅ or ❌) |
| POST | `/api/setup/github/sources` | `account` | Updated source list fragment |
| DELETE | `/api/setup/github/sources/{account}` | — | Updated source list fragment |
| POST | `/api/setup/config` | `key`, `value` | Icon fragment (shared with Summary) |

## Data Flow

| Reads | Writes |
|-------|--------|
| `settings` table (`github_username`) | `settings` table via `/api/setup/config` |
| `github_sources` table | `github_sources` table (add/remove) |
| `gh auth status` exit code (subprocess) | None |
| `ssh -T git@github.com` exit code (subprocess) | None |

## Open Questions

- Should HTTPS clone be auto-selected when SSH is unavailable? V1: the Download action on the Repositories tab prefers SSH but falls back to HTTPS automatically when `ssh -T git@github.com` fails.
- Should this screen support GitHub Enterprise Server hostnames? V1: github.com only.
