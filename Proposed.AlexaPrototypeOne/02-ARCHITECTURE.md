# 02 — Architecture

---

## System Diagram

```
┌─── AWS Boundary ──────────────────────────────────────────────┐
│                                                                 │
│   Alexa Device                                                  │
│       │ (speech → ASK cloud STT)                               │
│       ▼                                                         │
│   Alexa Skill (ASK)                                             │
│       │ IntentRequest / VoiceCommandIntent                      │
│       ▼                                                         │
│   AWS Lambda  ──► Amazon SQS Queue                             │
│   (validates,      (durable, always on,                        │
│    enqueues,        messages persist when                      │
│    responds         daemon is offline)                         │
│    "Got it")                                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─── Local Machine ───────────────────────────────────────────────┐
│                                                                  │
│   Python Daemon (daemon.py)                                      │
│       │ polls SQS every N seconds (boto3 long poll)             │
│       │ reads routing_rules from SQLite                         │
│       │ matches utterance → rule                                │
│       │                                                         │
│       ├──► game_ticket  ──► POST localhost:5001/api/ticket      │
│       ├──► file_append  ──► data/ideas/book.txt                 │
│       ├──► api_endpoint ──► any HTTP endpoint                   │
│       ├──► run_script   ──► bin/my-script.sh                    │
│       ├──► slack_webhook──► Slack                               │
│       └──► pending_confirm (held until UI approval)             │
│                                                                  │
│   Flask Config UI (app.py, port 5002)                            │
│       - Routing rules CRUD                                       │
│       - Message history                                          │
│       - Pending confirmations                                    │
│       - Daemon status                                            │
│                                                                  │
│   SQLite Database (data/alexa.db)                               │
│       - routing_rules                                            │
│       - message_log                                              │
│       - confirmations                                            │
│       - audit_log                                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Two Boundaries, Four Components

### Cloud Components (AWS-managed, always available)

**1. Alexa Skill (ASK)**
- Handles speech-to-text via AWS ASK cloud infrastructure
- Sends `IntentRequest` to Lambda with structured JSON
- One intent: `VoiceCommandIntent` with `AMAZON.SearchQuery` slot captures full utterance
- No local hosting required; configured in Alexa Developer Console
- Lambda must respond within 8 seconds (timeout constraint)

**2. AWS Lambda**
- Validates Alexa skill ID, extracts utterance, writes SQS message, returns "Got it."
- Stateless — no database, no routing logic
- ~200ms execution time; well within 8s Alexa deadline
- Costs: free tier covers personal use indefinitely

**3. Amazon SQS Queue**
- Durable message store that bridges cloud and local
- **Store-and-forward**: if daemon is offline, messages accumulate in queue (up to 4 days retention)
- Standard queue (not FIFO) — at-least-once delivery
- Dead letter queue (DLQ) after 3 failed receive attempts
- Long polling reduces API calls and cost

### Local Components (developer machine, started on demand)

**4. Python Daemon (daemon.py)**
- Polls SQS every 5 seconds (configurable)
- Matches utterances against `routing_rules` table
- Dispatches to 5 destination types
- Handles confirmations, retries, and failure states
- PID file at `data/daemon.pid`

**5. Flask Config UI (app.py, port 5002)**
- Routing rules management
- Message history and audit log viewer
- Pending confirmations queue with approve/reject
- No voice processing — display-only interface

---

## Key Design Decisions

### Why Lambda, not Flask-as-Alexa-endpoint

Alexa Skills require an HTTPS endpoint with a valid TLS certificate accessible
from the internet. A local Flask server is not directly accessible. Options are:

1. **Lambda** (chosen) — native AWS, zero infrastructure, free tier sufficient
2. **ngrok** — tunnels localhost to HTTPS URL; works for development but not production

The v2 architecture uses Lambda for production and ngrok for local development testing
of the Lambda code itself. The Flask UI at port 5002 never receives Alexa requests.

### Why SQS, not direct webhook to Flask

Direct webhook (Lambda → POST to localhost) would require:
- The local machine to be publicly reachable (ngrok or port forwarding)
- The Flask server to always be running
- Complex retry logic if Flask is down

SQS solves all three: Lambda and daemon are fully decoupled, the local machine needs
no inbound connectivity, and messages wait in the queue indefinitely.

### Why SQLite routing rules, not hardcoded intents

Hardcoded Alexa intents (CommandIntent, IdeaIntent, etc.) require redeploying the
Lambda + rebuilding the Alexa interaction model for every new keyword. SQLite routing
rules require only a database row insert — no deployment, no restart.

### Outbox Pattern

The `message_log` table implements the distributed systems "outbox pattern":
messages are recorded to the local database atomically with SQS receipt, and
only deleted from SQS after confirmed successful dispatch. This guarantees
at-least-once delivery to destinations.

---

## Failure Modes

| Failure | Behavior |
|---------|----------|
| Daemon offline | SQS retains messages up to 4 days; daemon drains queue on restart |
| Destination unreachable | Dispatch fails; SQS re-delivers after visibility timeout; retried up to 3 times |
| Lambda error (SQS send fails) | Alexa hears "Something went wrong"; no message recorded |
| SQLite locked | daemon retries via Python sqlite3 retry; Flask returns 503 |
| SQS DLQ threshold reached | Message moves to DLQ; visible in AWS console; not retried automatically |

---

## Local Development Flow

```
1. Create AWS resources:   SQS queue + Lambda function (see 10-AWS-SETUP.md)
2. Configure .env:         AWS credentials + SQS_QUEUE_URL + ALEXA_SKILL_ID
3. Initialize DB:          python init_db.py
4. Start Flask UI:         bin/start.sh         (port 5002)
5. Start daemon:           bin/start-daemon.sh  (background process)
6. Test Lambda:            aws lambda invoke ... (with test event JSON)
7. Watch queue drain:      check GET /api/messages in the UI
```

No ngrok required for the normal dev loop — test Lambda directly with `aws lambda invoke`.
ngrok is only needed if you want to test with a physical Alexa device.
