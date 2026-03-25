# Screen: Welcome

**Version:** 20260324 V1
**Description:** Landing screen shown when the user first enters the application. Welcome banner, Git SSH setup guide, and links to service help pages.

## Menu Navigation

Top-level tab in the navigation bar: `Welcome` — leftmost tab, always present. This is the default route.

## Route

```
GET /welcome   (default — also served at GET /)
```

The app root (`/`) redirects to `/welcome` when no other default is set.

## Layout

Single-column centered content, max-width 900px, padded. Three stacked sections:

```
┌────────────────────────────────────────────┐
│                                            │
│         ██ WELCOME TO PROTOTYPER ██        │
│      Your local prototype operations hub   │
│                                            │
├────────────────────────────────────────────┤
│  Git SSH Setup                             │
│  ─────────────────────────────────────────│
│  [setup instructions + link]               │
├────────────────────────────────────────────┤
│  Service Help                              │
│  ─────────────────────────────────────────│
│  [help page links]                         │
└────────────────────────────────────────────┘
```

## Welcome Banner

Full-width hero section at top of page. Dark surface (`--cc-surface`), large centered text.

| Element | Content |
|---------|---------|
| Headline | `Welcome to Prototyper` — large (32px), bold, accent color |
| Subheadline | `Your local prototype operations hub` — muted, 16px |
| Decoration | Subtle horizontal rule below subheadline |

No buttons or actions in the banner. Visual only.

## Git SSH Setup Card

Card (`cc-card`) below the banner. Purpose: guide the user to establish SSH connectivity to GitHub (or their Git host) so prototype operations (clone, push, pull) work correctly.

### Card Header

`Git SSH Setup` with a key icon.

### Content

Short checklist layout. Steps are displayed as numbered items, not a wall of text.

| Step | Instruction |
|------|-------------|
| 1 | Check for existing SSH key: `ls ~/.ssh/id_ed25519.pub` |
| 2 | If missing, generate one: `ssh-keygen -t ed25519 -C "your@email.com"` |
| 3 | Copy your public key: `cat ~/.ssh/id_ed25519.pub` |
| 4 | Add the key to your Git host's SSH keys page (link below) |
| 5 | Test connectivity: `ssh -T git@github.com` |

Code snippets rendered in monospace inline code style (not a full log block).

### Link

Single prominent button/link below the steps:

| Label | Target | Style |
|-------|--------|-------|
| `Add SSH Key on GitHub →` | `https://github.com/settings/keys` | Outline button, opens new tab |

Note: link text and target can be updated in a future iteration to support GitLab or other hosts.

### Status indicator (future)

Space reserved at bottom of card for a future SSH connectivity status indicator (e.g. `ssh -T git@github.com` result). Not implemented in V1 — leave a placeholder comment in template.

## Service Help Links Card

Card below the Git setup card. Purpose: quick links to commonly needed external help pages.

### Card Header

`Help & Resources` with a question-mark icon.

### Links

Displayed as a grid of link buttons (2-column on desktop, 1-column on narrow).

| Label | Destination | Notes |
|-------|-------------|-------|
| GitHub Docs | `https://docs.github.com` | Opens new tab |
| SSH Troubleshooting | `https://docs.github.com/en/authentication/troubleshooting-ssh` | Opens new tab |
| Flask Documentation | `https://flask.palletsprojects.com` | Opens new tab |
| Bootstrap 5 Docs | `https://getbootstrap.com/docs/5.3` | Opens new tab |

All links open in a new tab. Cards are static — no data fetch required.

## Data Flow

| Reads | Writes |
|-------|--------|
| None — static content | None |

No API calls. Screen is fully static HTML rendered by the server template.

## Open Questions

- Should the welcome banner display the logged-in username (if auth is added later)?
- Should the Git host URL be configurable in `.env` to support GitLab/Bitbucket?
- Should V2 add a live SSH connectivity check that pings `ssh -T git@github.com` and shows pass/fail inline?
- Should the help links be editable from the Settings screen?
