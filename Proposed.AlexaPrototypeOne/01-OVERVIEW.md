# 01 — Overview

---

## Purpose

Alexa Prototype One routes voice commands spoken to an Alexa device into
configurable local workflows. Speak a keyword phrase and a message is
dispatched to a destination: a local file, a GAME ticket, a webhook, a script,
or a Slack channel.

The system has two halves:

- **Cloud half (AWS):** Alexa Skill + Lambda + SQS. Always on. Receives voice
  and stores messages durably until the local machine is ready to process them.

- **Local half:** A Python polling daemon reads routing rules from SQLite,
  dispatches messages to destinations. A Flask UI at port 5002 lets you manage
  routing rules and approve flagged commands.

---

## Core User Flow

```
1. User says:  "Alexa, open command center"
               "book idea about recursive data structures"
               (session ends)

2. AWS:        Lambda enqueues {"keyword_raw": "book idea about recursive data structures", ...}
               to SQS queue

3. Local:      Daemon polls SQS, finds message
               Matches routing rule: keyword="book idea", destination=file_append
               Appends "[2026-03-11T14:23Z] book idea about recursive data structures"
               to data/ideas/book.txt
               Deletes message from SQS

4. User:       Sees entry in data/ideas/book.txt
               Config UI at localhost:5002 shows message as 'completed'
```

---

## Destination Types

| Type | What it does | Example keyword |
|------|-------------|-----------------|
| `file_append` | Append text to a local file | "book idea", "note" |
| `game_ticket` | Create a ticket in GAME | "game ticket" |
| `api_endpoint` | POST to any HTTP endpoint | "deploy request" |
| `run_script` | Run a local shell/Python script | "process log" |
| `slack_webhook` | Post to Slack channel | "team note" |

All routing rules are user-configured in the Flask UI — no code change or
Lambda redeployment needed to add a new keyword.

---

## Offline Tolerance

If the local daemon is stopped:
- Alexa still responds "Got it." — Lambda and SQS remain operational
- Messages accumulate in SQS (retained up to 4 days)
- When the daemon restarts, it drains the backlog in order

This is the core architectural guarantee: voice commands are never lost due to
the local machine being offline or restarting.

---

## Confirmation

Some routing rules are flagged `requires_confirmation`. These messages are held
in a "pending approval" state and shown prominently in the config UI. The user
approves or rejects before dispatch occurs. Useful for destructive operations
(deploy scripts, deletes) where you want a human checkpoint.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Voice input | Amazon Alexa Skills Kit (ASK) |
| Cloud receiver | AWS Lambda (Python 3.12) |
| Message queue | Amazon SQS |
| Routing engine | Python daemon (boto3 + SQLite) |
| Config UI | Python Flask + Bootstrap 5 + HTMX |
| Database | SQLite (data/alexa.db) |

See STACK.yaml for full configuration.

---

## Success Criteria

- Voice command appears in config UI within 10 seconds of being spoken
- Messages are not lost when daemon is offline (tested by stopping daemon, speaking, restarting)
- A new routing rule (new keyword + destination) can be added via the UI without any code change
- Destinations can be offline — file append always works; API endpoints retry up to 3 times
- Confirmations appear at the top of the UI and block dispatch until approved or rejected
- All dispatches are recorded in message_log with full audit trail
