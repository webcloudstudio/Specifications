# Stack Configuration for Alexa Prototype One
#
# This file declares which technology stack files to include when building
# or reviewing this project. Each key maps to a file in PROJECT/stack/.
#
# File mapping:
#   language: python        → stack/python.md
#   framework: flask        → stack/flask.md
#   database: sqlite        → stack/sqlite.md
#   frontend: bootstrap5    → stack/bootstrap5.md
#
# stack/common.md is ALWAYS included regardless of selections.
#
# AWS services (stub stack files — see stack/aws-*.md):
#   aws-lambda              → stack/aws-lambda.md
#   aws-sqs                 → stack/aws-sqs.md
#   alexa-skills-kit        → stack/alexa-skills-kit.md

# --- Technology Stack ---

language: python
framework: flask
database: sqlite
frontend: bootstrap5

# AWS services (additional — not auto-mapped by validate.sh but referenced in specs)
aws_services:
  - aws-lambda          # Lambda function receives Alexa intents, enqueues to SQS
  - aws-sqs             # Durable message store between Lambda and local daemon
  - alexa-skills-kit    # Alexa Skill configuration and interaction model

# --- Project Configuration ---

project:
  name: AlexaPrototypeOne
  title: "Alexa Prototype One — Voice Command Router"
  description: >
    Routes Alexa voice commands through AWS Lambda + SQS to a local Python
    daemon that dispatches messages to configurable destinations. Includes a
    standalone Flask UI for managing routing rules and confirming flagged commands.

  # Port for the local Flask config UI
  port: 5002

  # Python virtual environment
  venv: true

# --- Custom Stack Rules ---

stack_rules:
  require_git: true
  require_bin_scripts:
    - start.sh           # Start Flask config UI (port 5002)
    - stop.sh            # Stop Flask config UI
    - start-daemon.sh    # Start SQS polling daemon
    - stop-daemon.sh     # Stop SQS polling daemon
  require_claude_md: true
  require_git_homepage_md: true
  logging:
    style: python
    output: data/logs/

# --- Standard Directories ---

directories:
  data: data
  logs: data/logs
  backups: data/backups
  tests: tests
  static: static
  templates: templates
  scripts: bin
  docs: docs

# --- Environment Variables ---

env:
  required:
    - AWS_ACCESS_KEY_ID       # AWS credentials for SQS access
    - AWS_SECRET_ACCESS_KEY
    - AWS_REGION              # e.g. us-east-1
    - SQS_QUEUE_URL           # Full SQS queue URL
    - ALEXA_SKILL_ID          # Alexa skill application ID (for Lambda validation)
  optional:
    - SECRET_KEY              # Flask secret key (defaults to dev key)
    - DAEMON_POLL_INTERVAL    # Seconds between SQS polls (default: 5)
    - GAME_API_URL            # GAME Command Center URL (default: http://localhost:5001)
    - GAME_API_KEY            # API key for GAME integration
    - FLASK_DEBUG             # Enable Flask debug mode

# --- Database ---

database_config:
  path: data/alexa.db
  wal_mode: true
  foreign_keys: true

# --- Lambda Function ---

lambda_config:
  function_name: alexa-prototype-handler
  runtime: python3.12
  timeout_seconds: 5
  memory_mb: 128
  handler: lambda_function.lambda_handler

# --- SQS Queue ---

sqs_config:
  queue_name: alexa-prototype-queue
  dlq_name: alexa-prototype-dlq
  visibility_timeout_seconds: 30
  message_retention_days: 4
  max_receive_count: 3       # Failures before DLQ

# --- Specification Files ---

specs:
  - 01-OVERVIEW.md
  - 02-ARCHITECTURE.md
  - 03-DATABASE.md
  - 04-LAMBDA-SKILL.md
  - 05-DAEMON.md
  - 06-ROUTING-RULES.md
  - 07-CONFIRMATION-FLOW.md
  - 08-CONFIG-UI.md
  - 09-API.md
  - 10-AWS-SETUP.md
  - 11-STARTUP.md
