# Alexa Prototype One — Voice Command Router

**Status**: Specification v2 | **Updated**: 2026-03-11

Routes Alexa voice commands through AWS Lambda + SQS to a local Python daemon that dispatches messages to configurable destinations. Includes a standalone Flask UI for managing routing rules and confirming flagged commands.

---

# Catalog

| File | Description |
|------|-------------|
| `01-OVERVIEW.md` | Purpose, core user flow, destination types, offline tolerance, confirmation flow, tech stack overview |
| `02-ARCHITECTURE.md` | System design, component interactions, data flow diagrams, state management |
| `03-DATABASE.md` | SQLite schema, tables, relationships, migrations, backup strategy |
| `04-LAMBDA-SKILL.md` | AWS Lambda function, Alexa Skill Kit interaction model, intent handling |
| `05-DAEMON.md` | Local SQS polling daemon, message processing loop, retry logic, process lifecycle |
| `06-ROUTING-RULES.md` | Routing table schema, keyword matching, rule priorities, destination configuration |
| `07-CONFIRMATION-FLOW.md` | Approval workflow for flagged commands, UI integration, audit trail |
| `08-CONFIG-UI.md` | Flask web interface, dashboard, rule management, Bootstrap 5 + HTMX components |
| `09-API.md` | REST API endpoints for programmatic rule management, integrations |
| `10-AWS-SETUP.md` | Step-by-step AWS account setup, Lambda deployment, SQS queue creation, IAM policies |
| `11-STARTUP.md` | Application startup validation, environment checks, initialization sequence |
| `STACK.yaml` | Technology selections, project config, environment variables, database/Lambda/SQS configuration |

---

# Stacks

## Selected Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.12 | Server-side implementation, daemon, Lambda function |
| **Framework** | Flask | Config UI web framework (port 5002) |
| **Database** | SQLite | Local routing rules and audit log storage |
| **Frontend** | Bootstrap 5 | Responsive UI components, dark theme |
| **Voice Platform** | Amazon Alexa Skills Kit (ASK) | Voice input and intent routing |
| **Cloud Queue** | AWS SQS | Durable message storage between Lambda and daemon |
| **Cloud Compute** | AWS Lambda | Handles Alexa intents, enqueues to SQS |

## When to Use Each Stack

| Technology | When to Use |
|-----------|----------|
| **Flask** | Building the local configuration dashboard and API |
| **SQLite** | Storing routing rules offline, audit trail, configuration |
| **AWS Lambda** | Processing Alexa intents in the cloud, staying responsive |
| **AWS SQS** | Ensuring messages survive daemon downtime, reliable queueing |
| **Bootstrap 5** | Building a responsive, professional-looking configuration UI |

---

# Prerequisites

## System Requirements

- **Python 3.12+** — Lambda and daemon run on Python 3.12
- **AWS Account** — Lambda, SQS, API Gateway setup
- **Local Linux/macOS/WSL** — Daemon must run on the machine hosting local destinations
- **Git** — For version control and configuration management

## Python Dependencies

```
flask==2.3.0
boto3==1.26.0
python-dotenv==1.0.0
PyYAML==6.0
```

Install via: `pip install -r requirements.txt`

## AWS Credentials & Configuration

| Variable | Required | Purpose |
|----------|----------|---------|
| `AWS_ACCESS_KEY_ID` | **Yes** | AWS authentication for SQS access |
| `AWS_SECRET_ACCESS_KEY` | **Yes** | AWS authentication for SQS access |
| `AWS_REGION` | **Yes** | AWS region (e.g., `us-east-1`) |
| `SQS_QUEUE_URL` | **Yes** | Full SQS queue URL from AWS Console |
| `ALEXA_SKILL_ID` | **Yes** | Alexa Skill application ID for Lambda validation |

## Optional Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | `alexa-dev-key` | Flask session encryption key |
| `DAEMON_POLL_INTERVAL` | `5` | Seconds between SQS polls |
| `GAME_API_URL` | `http://localhost:5001` | GAME system URL (for ticket creation) |
| `GAME_API_KEY` | *(none)* | API key for GAME integration |
| `FLASK_DEBUG` | *(unset)* | Enable Flask debug mode and auto-reload |

## AWS Resources

Before deployment, you must create:

1. **IAM User or Role** with SQS permissions (see `10-AWS-SETUP.md`)
2. **SQS Queue** named `alexa-prototype-queue` (4-day retention, DLQ configured)
3. **Lambda Function** with Python 3.12 runtime
4. **Alexa Developer Account** with a custom skill created

---

# Usage

## Starting the System

```bash
# Terminal 1: Start the local Flask configuration UI
./bin/start.sh          # Runs on http://localhost:5002

# Terminal 2: Start the SQS polling daemon
./bin/start-daemon.sh   # Polls SQS every 5 seconds (configurable)
```

## Stopping the System

```bash
./bin/stop.sh           # Stop Flask UI
./bin/stop-daemon.sh    # Stop polling daemon
```

## Configuration

All routing rules are managed through the Flask web UI at `http://localhost:5002`:
- Add keywords and assign destinations
- Enable/disable rules
- Flag rules requiring confirmation
- Review audit trail of processed messages

No code changes or Lambda redeployment required.

---

# Architecture at a Glance

```
┌─────────────────────────────────────┐
│ User speaks to Alexa device         │
└────────────────┬────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ AWS Lambda    │
         │ (Python 3.12) │
         └───────┬───────┘
                 │ enqueue
                 ▼
         ┌───────────────┐
         │  SQS Queue    │
         └───────┬───────┘
                 │ poll (every 5s)
                 ▼
      ┌─────────────────────┐
      │ Local Python Daemon │
      │  (message loop)     │
      └─────────┬───────────┘
                │
        ┌───────┴────────┬────────────┐
        ▼                ▼            ▼
    ┌────────┐     ┌──────────┐  ┌────────┐
    │ File   │     │ GAME API │  │ Webhook│
    │ Append │     │ Endpoint │  │  Call  │
    └────────┘     └──────────┘  └────────┘
```

---

# Reliability Guarantees

- **Offline Tolerance**: If daemon stops, Alexa still responds and messages queue in SQS (4-day retention)
- **No Message Loss**: SQS keeps messages until daemon confirms processing
- **Confirmation Workflow**: Destructive operations can require approval before dispatch
- **Audit Trail**: All messages logged to `message_log` table with timestamps and results

---

# Next Steps

1. Review `02-ARCHITECTURE.md` for system design
2. Follow `10-AWS-SETUP.md` to configure AWS resources
3. Run `11-STARTUP.md` validation checklist before going live
4. Configure routing rules in the Flask UI (no code changes needed)
