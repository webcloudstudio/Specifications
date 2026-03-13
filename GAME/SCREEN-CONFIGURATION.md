# Screen: Configuration

**AI assistant config profile management.** Deploy profiles, preview diffs, roll back.

---

## Layout

Three sections: Active Profile, Profile Library, Deployment History.

## Active Profile

- Current profile name and deploy time
- Diff preview showing what will change
- Deploy button per profile

## Profile Library

- List of profiles with names and descriptions
- Edit and New buttons

## Deployment History

- Table of past deployments
- Rollback button per row

## How It Works

1. User selects a profile (YAML file in `config_engine/profiles/`)
2. Platform generates config files from profile
3. Files written to `config_engine/staged/` (committed to git — this is the rollback store)
4. Files copied to AI assistant's live config directory

Rollback: copy staged files from a past git commit back to live config.

## Data Flow

| Reads | Writes |
|-------|--------|
| Profile YAML files | Staged configs (git committed) |
| AGENTS.md from projects | AI assistant live config |
