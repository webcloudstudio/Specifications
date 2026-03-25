# Patch: 003 — Create .env.sample configuration template
**Type:** patch
**Scope:** Project root (.env.sample file)

## Intent
The GAME prototype is missing a `.env.sample` file that documents required environment variables and their defaults. This is a standard Python/Flask project pattern that helps developers understand what configuration is needed and provides a reference for local setup.

## Changes Required
- Create `.env.sample` at project root with documented environment variables needed by Flask app and any services
- Include comments explaining purpose of each variable (e.g., FLASK_ENV, DATABASE_URL, SECRET_KEY, PROJECTS_DIR, etc.)
- Include reasonable defaults or examples

## Open Questions
None.
