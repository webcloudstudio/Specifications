# Global Rules

Standards distributed to all projects. Changes here propagate via `bin/update_projects.sh`.

| File | Purpose | Distributed To |
|------|---------|----------------|
| `CLAUDE_RULES.md` | Agent behavior contract | Injected into each project's AGENTS.md |
| `DOCUMENTATION_BRANDING.md` | Documentation theming, color system, typography | Referenced by build_documentation scripts |
| `templates/common.sh` | Bash script infrastructure | Copied to each project's `bin/common.sh` |
| `templates/common.py` | Python script infrastructure | Copied to each project's `bin/common.py` |
| `stack/*.md` | Prescriptive tech patterns per technology | Used by `generate_prompt.sh` for build prompts |
| `gitignore` | Standard .gitignore | Copied to new projects on creation |

**After any change:** run `bash bin/update_projects.sh` from the Specifications root.
