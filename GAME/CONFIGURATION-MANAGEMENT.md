# Configuration Management

**AI assistant config profiles.** Select a profile, deploy it, roll back to any previous version.

---

## Capabilities

- Profile library (YAML files)
- Deploy with diff preview
- Deployment history in git
- One-click rollback to any prior deployment
- Generate project-specific AI context from profile

## How It Works

1. User selects a profile
2. Platform generates config files from YAML
3. Files written to staging directory (committed to git)
4. Files copied to AI assistant's live config directory

Rollback: copy staged files from a past commit back to live config.

## Persistence

- **Profiles:** `config_engine/profiles/*.yaml` (git committed)
- **Staged configs:** `config_engine/staged/` (git committed — this IS the rollback store)
- **Live configs:** AI assistant's config directory (outside this repo)
