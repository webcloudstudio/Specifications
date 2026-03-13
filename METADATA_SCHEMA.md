# Project Metadata Schema

**Version**: 1.0 | **Updated**: 2026-03-13

A comprehensive metadata database schema for projects, including technical and non-technical features. This schema can be used for orchestration, discovery, planning, and asset management across a portfolio of projects.

---

# Overview

Metadata is distributed across multiple locations in a project:

- **README.md** — Human-readable overview, quick start, and context-aware metadata
- **STACK.yaml** — Technology selections, configuration, directory structure
- **CLAUDE.md** — Development workflow, coding standards, team conventions
- **git_homepage.md** — Portfolio card metadata (for publishing)
- **bin/ script headers** — Operation metadata (purpose, required environment, etc.)
- **Database tables** — Runtime metadata (status, logs, relationships)

This schema documents all standard metadata fields and where they appear.

---

# Section 1: Project Identity & Context

## Basic Information

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **project.name** | string | STACK.yaml | ✓ | `AlexaPrototypeOne` |
| **project.title** | string | STACK.yaml, README.md | ✓ | `Alexa Prototype One — Voice Command Router` |
| **project.description** | string (long) | STACK.yaml, README.md | ✓ | `Routes Alexa voice commands through AWS Lambda...` |
| **project.purpose** | string (short) | README.md | ✓ | `Routes voice commands to configurable local workflows` |
| **project.status** | enum | README.md, git_homepage.md | ✓ | `active`, `paused`, `archived`, `prototype` |
| **project.version** | string | README.md | ✗ | `2.0`, `v1.2.3` |
| **project.updated** | ISO date | README.md | ✓ | `2026-03-11` |

## Portfolio/Publishing Metadata

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **card.title** | string | git_homepage.md, projects table | ✓ | `Alexa Prototype One` |
| **card.description** | string | git_homepage.md, projects table | ✓ | `Voice-driven workflow router` |
| **card.tags** | array[string] | git_homepage.md, projects table | ✓ | `[aws, python, voice, automation]` |
| **card.type** | enum | git_homepage.md, projects table | ✓ | `software`, `book`, `tool`, `research` |
| **card.url** | URL | git_homepage.md, projects table | ✓ | `https://github.com/user/alexa-prototype` |
| **card.image** | URL | git_homepage.md | ✗ | `images/alexa-screenshot.png` |
| **card.status** | enum | git_homepage.md | ✓ | `shipped`, `in-progress`, `beta`, `planning` |

---

# Section 2: Technical Stack & Architecture

## Language & Runtime

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **tech.language** | string | STACK.yaml | ✓ | `python`, `javascript`, `go` |
| **tech.language_version** | string | STACK.yaml | ✗ | `3.12`, `18.0` |
| **tech.framework** | string | STACK.yaml | ✗ | `flask`, `django`, `react` |
| **tech.framework_version** | string | STACK.yaml | ✗ | `2.3.0` |
| **tech.database** | string | STACK.yaml | ✗ | `sqlite`, `postgres` |
| **tech.frontend** | string | STACK.yaml | ✗ | `bootstrap5`, `tailwind` |
| **tech.runtime_env** | array[string] | STACK.yaml, README.md | ✗ | `[python3.12, nodejs18, docker]` |

## Cloud & Infrastructure

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **cloud.provider** | array[enum] | STACK.yaml | ✗ | `[aws, gcp, azure]` |
| **cloud.services** | array[string] | STACK.yaml | ✗ | `[lambda, sqs, api-gateway, rds]` |
| **cloud.region** | string | STACK.yaml, env config | ✗ | `us-east-1` |
| **cloud.requires_auth** | boolean | README.md | ✗ | `true` |
| **hosting.type** | enum | STACK.yaml | ✗ | `serverless`, `container`, `vm`, `static` |
| **hosting.port** | integer | STACK.yaml | ✗ | `5001`, `3000` |

## Dependencies & Requirements

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **deps.runtime** | array[string] | STACK.yaml, requirements.txt | ✗ | `[flask, boto3, sqlalchemy]` |
| **deps.dev** | array[string] | STACK.yaml | ✗ | `[pytest, black, mypy]` |
| **deps.system** | array[string] | README.md | ✗ | `[git, bash, python3.12]` |
| **deps.optional** | array[string] | README.md | ✗ | `[postgresql, redis, node]` |

## Configuration

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **env.required** | array[string] | STACK.yaml, README.md | ✓ | `[AWS_ACCESS_KEY_ID, SQS_QUEUE_URL]` |
| **env.optional** | array[string] | STACK.yaml, README.md | ✗ | `[FLASK_DEBUG, SECRET_KEY]` |
| **config.venv** | boolean | STACK.yaml | ✗ | `true` |
| **config.venv_path** | string | STACK.yaml, CLAUDE.md | ✗ | `venv` |
| **config.docker** | boolean | STACK.yaml | ✗ | `false` |

---

# Section 3: Project Structure & Organization

## Directory Layout

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **dirs.data** | string (relative path) | STACK.yaml | ✗ | `data` |
| **dirs.logs** | string | STACK.yaml | ✗ | `data/logs` |
| **dirs.tests** | string | STACK.yaml | ✗ | `tests` |
| **dirs.static** | string | STACK.yaml | ✗ | `static` |
| **dirs.templates** | string | STACK.yaml | ✗ | `templates` |
| **dirs.docs** | string | STACK.yaml | ✗ | `docs` |
| **dirs.scripts** | string | STACK.yaml | ✗ | `bin` |

## Files & Conventions

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **conventions.git** | boolean | STACK.yaml | ✗ | `true` |
| **conventions.claude_md** | boolean | STACK.yaml | ✗ | `true` |
| **conventions.git_homepage** | boolean | STACK.yaml | ✗ | `true` |
| **conventions.readme_md** | boolean | STACK.yaml | ✗ | `true` |
| **conventions.scripts_required** | array[string] | STACK.yaml | ✗ | `[start.sh, stop.sh]` |

---

# Section 4: Capabilities & Features

## Functional Features

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **features.voice_input** | boolean | README.md | ✗ | `true` |
| **features.real_time_data** | boolean | README.md | ✗ | `true` |
| **features.background_jobs** | boolean | README.md | ✗ | `true` |
| **features.webhooks** | boolean | README.md | ✗ | `true` |
| **features.file_operations** | boolean | README.md | ✗ | `true` |
| **features.api_integration** | boolean | README.md | ✗ | `true` |
| **features.offline_capable** | boolean | README.md | ✗ | `true` |

## Quality & Reliability

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **quality.has_tests** | boolean | CLAUDE.md, test/ dir | ✗ | `true` |
| **quality.test_coverage** | percentage | README.md | ✗ | `85%` |
| **quality.code_review** | boolean | CLAUDE.md | ✗ | `true` |
| **reliability.uptime_sla** | enum | README.md | ✗ | `99.99%`, `best-effort` |
| **reliability.backup_enabled** | boolean | STACK.yaml | ✗ | `true` |
| **reliability.audit_logging** | boolean | STACK.yaml | ✗ | `true` |

---

# Section 5: Development & Operations

## Development Workflow

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **dev.language** | string | CLAUDE.md | ✓ | `python`, `javascript` |
| **dev.editor_config** | boolean | CLAUDE.md | ✗ | `true` |
| **dev.linter** | string | CLAUDE.md | ✗ | `black`, `eslint` |
| **dev.type_checker** | string | CLAUDE.md | ✗ | `mypy` |
| **dev.formatter** | string | CLAUDE.md | ✗ | `black` |
| **dev.test_framework** | string | CLAUDE.md | ✗ | `pytest` |
| **dev.git_workflow** | enum | CLAUDE.md | ✗ | `trunk-based`, `feature-branch`, `gitflow` |

## Operations & Maintenance

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **ops.start_script** | string | STACK.yaml, bin/ | ✓ | `bin/start.sh` |
| **ops.stop_script** | string | STACK.yaml, bin/ | ✓ | `bin/stop.sh` |
| **ops.restart_required** | enum | README.md, bin/ headers | ✗ | `always`, `on-code-change`, `on-config-change`, `never` |
| **ops.logging.enabled** | boolean | STACK.yaml | ✓ | `true` |
| **ops.logging.style** | enum | STACK.yaml | ✓ | `python`, `javascript`, `structured` |
| **ops.logging.output** | string | STACK.yaml | ✓ | `data/logs/` |
| **ops.health_check** | string | README.md | ✗ | `http://localhost:5001/health` |
| **ops.monitoring** | string | README.md | ✗ | `prometheus`, `datadog` |

## Scripts & Automation

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **scripts[].name** | string | bin/ file header | ✓ | `start.sh`, `deploy.sh` |
| **scripts[].purpose** | string | bin/ file header | ✓ | `Start Flask configuration UI` |
| **scripts[].operation_type** | enum | bin/ file header | ✓ | `server`, `job`, `maintenance` |
| **scripts[].environment_required** | array[string] | bin/ file header | ✗ | `[AWS_ACCESS_KEY_ID]` |
| **scripts[].timeout_seconds** | integer | bin/ file header | ✗ | `300` |
| **scripts[].idempotent** | boolean | bin/ file header | ✗ | `true` |

---

# Section 6: Team & Collaboration

## Team Information

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **team.owner** | string | CLAUDE.md, git_homepage.md | ✗ | `john-doe` |
| **team.maintainers** | array[string] | CLAUDE.md | ✗ | `[alice, bob]` |
| **team.stakeholders** | array[string] | CLAUDE.md | ✗ | `[marketing, engineering]` |
| **team.contact_email** | string | README.md | ✗ | `support@example.com` |

## Documentation & Links

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **links.homepage** | URL | git_homepage.md | ✗ | `https://github.com/user/project` |
| **links.documentation** | URL | README.md | ✗ | `docs/` |
| **links.issues** | URL | README.md | ✗ | `https://github.com/user/project/issues` |
| **links.discussions** | URL | README.md | ✗ | Slack channel, forum URL |
| **links.wiki** | URL | README.md | ✗ | `https://wiki.example.com/projects/...` |

---

# Section 7: Business & Planning

## Project Status & Lifecycle

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **lifecycle.phase** | enum | git_homepage.md, CLAUDE.md | ✗ | `idea`, `planning`, `in-progress`, `beta`, `shipped`, `maintenance`, `archived` |
| **lifecycle.start_date** | ISO date | git_homepage.md | ✗ | `2026-01-15` |
| **lifecycle.target_launch** | ISO date | CLAUDE.md | ✗ | `2026-06-30` |
| **lifecycle.created_date** | ISO date | git metadata | ✗ | `2024-06-15` |
| **lifecycle.last_updated** | ISO date | README.md | ✓ | `2026-03-13` |
| **lifecycle.deprecation_date** | ISO date | CLAUDE.md | ✗ | `2027-01-01` |

## Business Metrics

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **metrics.priority** | enum | CLAUDE.md, git_homepage.md | ✗ | `critical`, `high`, `medium`, `low` |
| **metrics.effort_estimate** | string | CLAUDE.md | ✗ | `1-2 weeks`, `large` |
| **metrics.roe_estimate** | string | CLAUDE.md | ✗ | `high-value`, `strategic`, `maintenance` |
| **metrics.cost_to_maintain** | enum | CLAUDE.md | ✗ | `low`, `medium`, `high` |
| **metrics.strategic_alignment** | array[string] | CLAUDE.md | ✗ | `[portfolio, revenue, learning]` |

## External Integrations

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **integrations[].service** | string | README.md, STACK.yaml | ✗ | `aws`, `slack`, `github` |
| **integrations[].required** | boolean | README.md | ✗ | `true` |
| **integrations[].authentication** | enum | README.md | ✗ | `api_key`, `oauth`, `credentials_file` |

---

# Section 8: Database & Data Management

## Database Configuration

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **database.type** | enum | STACK.yaml | ✗ | `sqlite`, `postgres`, `mysql` |
| **database.path** | string | STACK.yaml | ✗ | `data/cc.db` |
| **database.wal_mode** | boolean | STACK.yaml | ✗ | `true` |
| **database.foreign_keys** | boolean | STACK.yaml | ✗ | `true` |
| **database.backup_enabled** | boolean | STACK.yaml | ✗ | `true` |
| **database.backup_frequency** | enum | STACK.yaml | ✗ | `daily`, `weekly`, `on-write` |
| **database.retention_days** | integer | STACK.yaml | ✗ | `30` |

## Data & Privacy

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **data.user_data_stored** | boolean | README.md | ✗ | `false` |
| **data.personally_identifiable** | boolean | README.md | ✗ | `false` |
| **data.encryption_at_rest** | boolean | README.md | ✗ | `true` |
| **data.encryption_in_transit** | boolean | README.md | ✗ | `true` |
| **data.retention_policy** | string | README.md | ✗ | `30 days` |
| **data.gdpr_compliant** | boolean | README.md | ✗ | `true` |

---

# Section 9: Deployment & Distribution

## Build & Release

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **build.type** | enum | STACK.yaml | ✗ | `none`, `webpack`, `docker`, `native` |
| **build.output_dir** | string | STACK.yaml | ✗ | `dist/` |
| **build.cache_enabled** | boolean | STACK.yaml | ✗ | `true` |
| **release.versioning** | enum | CLAUDE.md | ✗ | `semver`, `calendar`, `rolling` |
| **release.changelog** | string | README.md | ✗ | `CHANGELOG.md` |
| **release.notes_template** | string | CLAUDE.md | ✗ | `release-template.md` |

## Distribution & Deployment

| Field | Type | Where Stored | Required | Example |
|-------|------|--------------|----------|---------|
| **distribution.type** | enum | STACK.yaml, README.md | ✗ | `github-pages`, `docker-hub`, `npm`, `pypi` |
| **distribution.channels** | array[string] | README.md | ✗ | `[github-pages, npm, docker]` |
| **deployment.environment** | enum | STACK.yaml | ✗ | `local`, `staging`, `production` |
| **deployment.method** | enum | STACK.yaml | ✗ | `git-push`, `docker-pull`, `manual` |
| **deployment.ci_cd_enabled** | boolean | STACK.yaml | ✗ | `true` |
| **deployment.ci_cd_platform** | enum | STACK.yaml | ✗ | `github-actions`, `gitlab-ci`, `circle-ci` |

---

# Complete Example: AlexaPrototypeOne

```yaml
# Project Identity
project:
  name: AlexaPrototypeOne
  title: "Alexa Prototype One — Voice Command Router"
  description: "Routes Alexa voice commands through AWS Lambda + SQS to a local Python daemon..."
  purpose: "Routes voice commands to configurable local workflows"
  status: active
  version: "2.0"
  updated: "2026-03-11"

# Card Metadata (for publishing)
card:
  title: "Alexa Prototype One"
  description: "Voice-driven workflow router"
  tags: ["aws", "python", "voice", "automation", "lambda", "sqs"]
  type: software
  url: "https://github.com/user/alexa-prototype"
  status: shipped

# Technical Stack
tech:
  language: python
  language_version: "3.12"
  framework: flask
  framework_version: "2.3.0"
  database: sqlite
  frontend: bootstrap5
  runtime_env: [python3.12, aws-cli]

# Cloud & Infrastructure
cloud:
  provider: [aws]
  services: [lambda, sqs, api-gateway]
  region: us-east-1
  requires_auth: true

hosting:
  type: hybrid  # Local daemon + serverless Lambda
  port: 5002

# Dependencies
deps:
  runtime: [flask, boto3, python-dotenv, PyYAML]
  dev: [pytest, black, mypy]
  system: [python3.12, git, bash]

# Configuration
env:
  required:
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_REGION
    - SQS_QUEUE_URL
    - ALEXA_SKILL_ID
  optional:
    - SECRET_KEY
    - DAEMON_POLL_INTERVAL
    - GAME_API_URL
    - GAME_API_KEY

config:
  venv: true
  venv_path: venv
  docker: false

# Directory Layout
dirs:
  data: data
  logs: data/logs
  tests: tests
  static: static
  templates: templates
  docs: docs
  scripts: bin

# Files & Conventions
conventions:
  git: true
  claude_md: true
  git_homepage: true
  readme_md: true
  scripts_required: [start.sh, stop.sh, start-daemon.sh, stop-daemon.sh]

# Features
features:
  voice_input: true
  real_time_data: true
  background_jobs: true
  webhooks: true
  file_operations: true
  api_integration: true
  offline_capable: true

# Quality
quality:
  has_tests: true
  test_coverage: "75%"
  code_review: true

# Reliability
reliability:
  uptime_sla: "best-effort"
  backup_enabled: true
  audit_logging: true

# Development
dev:
  language: python
  linter: black
  type_checker: mypy
  formatter: black
  test_framework: pytest
  git_workflow: trunk-based

# Operations
ops:
  start_script: bin/start.sh
  stop_script: bin/stop.sh
  restart_required: "on-code-change"
  logging:
    enabled: true
    style: python
    output: data/logs/
  health_check: "http://localhost:5002/health"

# Scripts
scripts:
  - name: start.sh
    purpose: "Start Flask configuration UI"
    operation_type: server
    environment_required: [FLASK_DEBUG]
    idempotent: false
  - name: start-daemon.sh
    purpose: "Start SQS polling daemon"
    operation_type: server
    environment_required: [AWS_ACCESS_KEY_ID, SQS_QUEUE_URL]
    idempotent: false

# Database
database:
  type: sqlite
  path: data/alexa.db
  wal_mode: true
  foreign_keys: true
  backup_enabled: true
  backup_frequency: "daily"

# Lifecycle
lifecycle:
  phase: shipped
  start_date: "2026-01-15"
  created_date: "2024-06-15"
  last_updated: "2026-03-13"

# Integrations
integrations:
  - service: aws
    required: true
    authentication: api_key
  - service: game-api
    required: false
    authentication: api_key

# Deployment
deployment:
  ci_cd_enabled: false
  deployment_method: manual
```

---

# Using This Schema

## For Orchestration Systems

Parse STACK.yaml, README.md, and CLAUDE.md to extract:
1. **Technology stack** — What to build with
2. **Operations** — What scripts are available
3. **Configuration** — What environment variables are needed
4. **Dependencies** — What services are required
5. **Lifecycle** — Project status and phase

## For AI Agents

Use metadata to:
1. **Generate context** — Create specific prompts per project
2. **Validate setup** — Ensure all required config is present
3. **Suggest improvements** — Based on tech stack and conventions
4. **Plan tasks** — Break down work based on architecture
5. **Test coverage** — Understand what's tested and what isn't

## For Portfolio Publishing

Use metadata to:
1. **Generate cards** — Title, description, image, tags, URL
2. **Sort projects** — By phase, priority, type
3. **Filter projects** — By technology, status, phase
4. **Generate homepage** — Automatically from git_homepage.md

---

# Extending the Schema

To add new fields:

1. **Identify the section** — Does it fit in an existing section?
2. **Define the field** — Type, where it's stored, required or optional
3. **Document it** — Add to this schema with example value
4. **Update projects** — Add the field to STACK.yaml, README.md, or CLAUDE.md
5. **Test parsing** — Ensure validation tools can extract it

---

# Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-13 | Initial schema for AlexaPrototypeOne and GAME projects |
