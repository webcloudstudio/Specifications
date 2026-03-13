# Specifications

Specification repository for AI-orchestrated projects. Defines platform capabilities, integration rules, and per-project specifications that an AI agent can build from.

## Structure

```
Specifications/
  FEATURES.md              Platform capabilities (what the system does)
  CLAUDE_RULES.md          Integration rules (how projects participate)
  verify.py                Compliance scanner
  rebuild_index.sh         Generate browsable documentation
  GAME/                    GAME project specification
  AlexaPrototypeOne/       Alexa project specification
  archive/                 Superseded documents
```

## Foundation Documents

**FEATURES.md** — All 24 platform features with status and completeness scores. Covers core platform, operations, observability, governance, publishing, configuration, and orchestration (Kubernetes-inspired).

**CLAUDE_RULES.md** — Concrete rules a project must follow to be discovered and integrated. Script headers, METADATA.md format, governance. If a project follows these rules, it works with the platform automatically.

## Projects

**GAME/** — Generic AI Management Environment. A Flask/SQLite dashboard that discovers local projects and provides operations, monitoring, publishing, and AI workflow management. This is the primary implementation of the features described in FEATURES.md.

**AlexaPrototypeOne/** — Alexa voice skill prototype. Separate specification, not currently editable.

## Usage

```bash
# Generate browsable documentation
bash rebuild_index.sh
# Open index.html in browser

# Validate project compliance
python3 verify.py --projects /path/to/projects

# Generate a build prompt for AI agent
bash generate-prompt.sh GAME > build-prompt.md
```

## Relationship Between Documents

```
FEATURES.md          What the platform should do (24 features)
    |
CLAUDE_RULES.md      Rules that make features work (scripts, metadata, governance)
    |
GAME/                How GAME implements the features (per-feature specs)
```

FEATURES defines capabilities. CLAUDE_RULES defines the contracts projects must follow. GAME specs describe how one specific application (the dashboard) implements those capabilities.
