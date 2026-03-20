# 11 — Startup Sequence

---

## Prerequisites

1. AWS resources created per 10-AWS-SETUP.md (Lambda, SQS queue, Alexa Skill)
2. `.env` file populated with all required environment variables
3. Python 3.12+, `venv` created:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### requirements.txt

```
flask>=3.0
python-dotenv>=1.0
boto3>=1.34
psutil>=5.9
```

---

## Step 1: Initialize Database

```bash
source venv/bin/activate
python init_db.py
```

`init_db.py` does:
1. Creates `data/` directory if missing
2. Creates all four tables (routing_rules, message_log, confirmations, audit_log)
3. Seeds default routing_rules if the table is empty
4. Idempotent — safe to run again; uses `CREATE TABLE IF NOT EXISTS`

Expected output:
```
Database initialized: data/alexa.db
Seeded 4 default routing rules.
```

If `data/alexa.db` already exists with rows, outputs:
```
Database initialized: data/alexa.db
Routing rules already seeded (4 rows) — skipping.
```

---

## Step 2: Start Flask Config UI

```bash
bin/start.sh
```

Flask starts at `http://localhost:5002`.

Startup validation in `create_app()`:
- Checks SQLite is readable (runs `SELECT 1`)
- Checks `.env` vars are loaded (warns but does not abort if AWS vars missing)
- Logs warning if `data/daemon.pid` does not exist (daemon not running)

---

## Step 3: Start Daemon

```bash
bin/start-daemon.sh
```

Daemon startup sequence:
1. Load `.env`
2. Write PID to `data/daemon.pid`
3. Call `init_db()` (idempotent)
4. Verify SQS connectivity:
   ```python
   sqs.get_queue_attributes(QueueUrl=QUEUE_URL,
                             AttributeNames=['ApproximateNumberOfMessages'])
   ```
   If SQS is unreachable, log error and exit with code 1.
5. Emit `[GAME] Service Started: SQS Daemon`
6. Begin poll loop

---

## Step 4: Deploy Lambda

```bash
cd lambda
zip lambda.zip lambda_function.py
aws lambda update-function-code \
    --function-name alexa-prototype-handler \
    --zip-file fileb://lambda.zip
```

Lambda is updated in ~5 seconds. No restart required — Lambda instances are replaced automatically.

---

## Full System Verification Test

```bash
# 1. Send a test message directly to Lambda (simulates Alexa)
aws lambda invoke \
    --function-name alexa-prototype-handler \
    --payload '{"session":{"sessionId":"test-1","application":{"applicationId":"YOUR_SKILL_ID"},"user":{"userId":"test-user"}},"context":{"System":{"device":{"deviceId":"test-device"}}},"request":{"type":"IntentRequest","intent":{"name":"VoiceCommandIntent","slots":{"utterance":{"name":"utterance","value":"book idea about testing the system"}}}}}' \
    /tmp/test_response.json

# 2. Verify Lambda response
cat /tmp/test_response.json
# Expected: {"response": {"outputSpeech": {"text": "Got it."}, ...}}

# 3. Wait one poll cycle (5 seconds), then check the UI
open http://localhost:5002
# Expected: recent messages shows "book idea about testing the system" with status 'completed'

# 4. Verify the file was written
cat data/ideas/book.txt
# Expected: [2026-03-11T...Z] book idea about testing the system
```

---

## Directory Layout (After Startup)

```
AlexaPrototypeOne/
├── app.py                    # Flask factory
├── daemon.py                 # SQS polling daemon
├── init_db.py                # Database initialization
├── schema.sql                # SQL DDL (imported by init_db.py)
├── db.py                     # get_db() context manager
├── dispatcher.py             # dispatch() by destination_type
├── routing.py                # match_rule(), load_rules()
├── confirmations.py          # handle_pending_confirmations(), auto_timeout_confirmations()
├── config.py                 # Config classes (DevConfig, ProdConfig)
├── routes/
│   ├── dashboard.py
│   ├── rules.py
│   ├── messages.py
│   └── api.py
├── templates/                # See 08-CONFIG-UI.md
├── static/                   # CSS overrides, any custom JS
├── lambda/
│   └── lambda_function.py    # Deployed to AWS Lambda
├── test_events/
│   └── voice_command.json    # Test event for lambda invoke
├── bin/
│   ├── start.sh              # Start Flask UI
│   ├── stop.sh               # Stop Flask UI
│   ├── start-daemon.sh       # Start polling daemon
│   └── stop-daemon.sh        # Stop polling daemon
├── data/                     # Gitignored
│   ├── alexa.db              # SQLite database
│   ├── daemon.pid            # Daemon PID file
│   ├── ideas/
│   │   └── book.txt          # file_append destination
│   ├── notes.txt             # file_append destination
│   └── logs/                 # bin/ script output logs
├── tests/
├── .env                      # Gitignored; see .env.example
├── .env.example              # Checked in; no real values
└── requirements.txt
```

---

## .env.example

```bash
# AWS Credentials (used by daemon + Flask UI; NOT Lambda — Lambda uses IAM role)
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=us-east-1

# SQS
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/alexa-prototype-queue

# Alexa Skill
ALEXA_SKILL_ID=amzn1.ask.skill.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Flask config UI
SECRET_KEY=change-me-in-production
FLASK_DEBUG=1

# Daemon
DAEMON_POLL_INTERVAL=5

# Optional: GAME integration
GAME_API_URL=http://localhost:5001
GAME_API_KEY=
```
