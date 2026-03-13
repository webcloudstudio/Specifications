# Feature: Configuration Management

**spec_v4 · 2026-03-11**

---

## Purpose

Manages the AI assistant's working configuration. The user selects a profile; the
platform deploys it to the AI's config directory. Past deployments are versioned in
git so any configuration can be rolled back.

---

## What the User Can Do

- Select a configuration profile and deploy it
- Preview what a profile will change before deploying
- Roll back to a previous deployment
- Create and edit profiles
- Generate a project-specific AI context file from a profile

---

## Screens

### Configuration Page

Three sections:

**Active Profile:** Current profile name and deploy time. Deploy button per profile.
Diff view showing what will change.

**Profile Library:** List of profiles with names and descriptions. Edit and New buttons.

**Deployment History:** Table of past deployments with rollback button per row.

---

## How It Works

1. User selects a profile
2. Platform generates config files from the YAML profile
3. Generated files are written to a staging directory (committed to git)
4. Files are copied from staging to the AI assistant's live config directory

Rollback: copy staged files from a past deployment back to live config. Record the
rollback as a new staging commit.

---

## Persistence

**Profiles** are stored as YAML files in the platform's `config_engine/profiles/`
directory. Committed to git.

**Staged configs** are stored in `config_engine/staged/`. Committed to git after each
deployment. This git history is the rollback store.

**Live configs** are written to the AI assistant's config directory (outside this
repo). Not committed.

---

## Out of Scope

- Managing CLAUDE.md in individual projects → that is the project's own contract file
- Per-project AI sessions → external
