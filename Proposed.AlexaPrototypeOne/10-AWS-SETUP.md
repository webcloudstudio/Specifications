# 10 — AWS Setup

Step-by-step instructions to create all required AWS resources.
Assumes an AWS account exists and `aws` CLI is configured with admin credentials locally.

---

## 1. Create SQS Queue

**AWS Console → SQS → Create Queue**

| Setting | Value |
|---------|-------|
| Type | Standard (not FIFO) |
| Name | `alexa-prototype-queue` |
| Visibility timeout | 30 seconds |
| Message retention | 4 days (345,600 seconds) |
| Maximum message size | 256 KB (default) |
| Receive message wait time | 20 seconds (enables long polling) |
| Dead-letter queue | Create new (see below) |

**Create DLQ first:**

| Setting | Value |
|---------|-------|
| Type | Standard |
| Name | `alexa-prototype-dlq` |
| Message retention | 14 days |

Then go back to creating `alexa-prototype-queue` and set:
- Dead-letter queue: `alexa-prototype-dlq`
- Maximum receives: `3`

**Copy the queue URL** (format: `https://sqs.{region}.amazonaws.com/{account-id}/alexa-prototype-queue`).
This becomes `SQS_QUEUE_URL` in your `.env` and Lambda environment variables.

---

## 2. Create Lambda Function

**AWS Console → Lambda → Create Function**

| Setting | Value |
|---------|-------|
| Function name | `alexa-prototype-handler` |
| Runtime | Python 3.12 |
| Architecture | x86_64 |
| Execution role | Create a new role with basic Lambda permissions |

After creation:

**Configuration → General configuration:**
- Timeout: 5 seconds
- Memory: 128 MB

**Configuration → Environment variables — add:**
| Key | Value |
|-----|-------|
| `AWS_REGION` | e.g. `us-east-1` |
| `SQS_QUEUE_URL` | The full queue URL from Step 1 |
| `ALEXA_SKILL_ID` | (fill in after Step 4 — come back to this) |

Note: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are NOT needed in Lambda —
the IAM execution role handles credentials.

---

## 3. Grant Lambda Permission to Write to SQS

**AWS Console → IAM → Roles → find the role Lambda created in Step 2**

Add an inline policy named `SQSSendMessage`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:{region}:{account-id}:alexa-prototype-queue"
    }
  ]
}
```

Replace `{region}` and `{account-id}` with your actual values.

---

## 4. Deploy Lambda Code

```bash
cd /path/to/AlexaPrototypeOne/lambda
zip lambda.zip lambda_function.py
aws lambda update-function-code \
    --function-name alexa-prototype-handler \
    --zip-file fileb://lambda.zip
```

---

## 5. Create Alexa Skill

**developer.amazon.com/alexa/console/ask → Create Skill**

| Setting | Value |
|---------|-------|
| Skill name | Command Center |
| Default language | English (US) |
| Model | Custom |
| Hosting | Provision your own (not Alexa-hosted) |
| Template | Start from scratch |

**Invocation Name:** `command center`
(User says: "Alexa, open command center")

### Build Interaction Model

**JSON editor tab → paste:**

```json
{
  "interactionModel": {
    "languageModel": {
      "invocationName": "command center",
      "intents": [
        {
          "name": "VoiceCommandIntent",
          "slots": [
            {"name": "utterance", "type": "AMAZON.SearchQuery"}
          ],
          "samples": [
            "{utterance}",
            "command {utterance}",
            "note {utterance}",
            "tell me {utterance}"
          ]
        },
        {"name": "AMAZON.StopIntent", "samples": []},
        {"name": "AMAZON.CancelIntent", "samples": []},
        {"name": "AMAZON.HelpIntent", "samples": []}
      ]
    }
  }
}
```

Click **Build Model** and wait for it to complete (~30 seconds).

### Set Endpoint

**Endpoint → AWS Lambda ARN**

Paste the Lambda function ARN from Step 2.
(Format: `arn:aws:lambda:{region}:{account-id}:function:alexa-prototype-handler`)

Click **Save Endpoints**.

**Copy the Skill ID** from the top of the page.
(Format: `amzn1.ask.skill.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

---

## 6. Grant Alexa Permission to Invoke Lambda

Run this in your AWS CLI:

```bash
aws lambda add-permission \
    --function-name alexa-prototype-handler \
    --statement-id alexa-trigger \
    --action lambda:InvokeFunction \
    --principal alexa-appkit.amazon.com \
    --event-source-token YOUR_SKILL_ID
```

Replace `YOUR_SKILL_ID` with the skill ID from Step 5.

---

## 7. Update Lambda Environment Variable

Go back to Lambda → Configuration → Environment variables.
Set `ALEXA_SKILL_ID` to the skill ID from Step 5.

---

## 8. Create Local .env File

```bash
# /mnt/c/Users/barlo/projects/AlexaPrototypeOne/.env

# AWS Credentials (for local daemon + Flask UI)
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=us-east-1

# SQS
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/alexa-prototype-queue

# Alexa Skill
ALEXA_SKILL_ID=amzn1.ask.skill.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Optional
SECRET_KEY=change-me-for-production
DAEMON_POLL_INTERVAL=5
GAME_API_URL=http://localhost:5001
GAME_API_KEY=
FLASK_DEBUG=1
```

The `.env` file is gitignored. Never commit it.

---

## 9. Verify End-to-End

```bash
# 1. Initialize database
source venv/bin/activate
python init_db.py

# 2. Test Lambda directly (no Alexa device needed)
aws lambda invoke \
    --function-name alexa-prototype-handler \
    --payload file://test_events/voice_command.json \
    /tmp/response.json
cat /tmp/response.json
# Expected: {"version": "1.0", "response": {"outputSpeech": {"type": "PlainText", "text": "Got it."}, ...}}

# 3. Check SQS for the message
aws sqs receive-message \
    --queue-url $SQS_QUEUE_URL \
    --attribute-names All

# 4. Start daemon + UI
bin/start-daemon.sh
bin/start.sh

# 5. Open dashboard
open http://localhost:5002
# Expected: message appears in Recent Messages with status 'completed'
```

---

## Estimated Cost (Personal Use)

| Service | Free Tier | Expected Usage | Cost |
|---------|-----------|----------------|------|
| Lambda | 1M requests/month | ~1,000/month | $0 |
| SQS | 1M requests/month | ~10,000/month | $0 |
| CloudWatch Logs | 5 GB/month | < 1 MB | $0 |

This project stays entirely within AWS Free Tier for personal use.
