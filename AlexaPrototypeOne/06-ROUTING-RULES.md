# 06 — Routing Rules

Routing rules are the core configuration object. Each rule maps a keyword pattern
to a destination. The daemon evaluates incoming utterances against all enabled rules
and dispatches to the first match.

---

## Keyword Matching Algorithm

The daemon calls `match_rule(utterance, rules)` on every SQS message:

```python
def match_rule(utterance: str, rules: list[dict]) -> dict | None:
    """
    Returns the first enabled rule whose keyword matches the utterance,
    ordered by priority ASC (lower integer = higher priority).
    Returns None if no rule matches.
    """
    text = utterance.strip().lower()
    for rule in sorted(rules, key=lambda r: r['priority']):
        if not rule['enabled']:
            continue
        kw = rule['keyword'].lower()
        match_type = rule['match_type']
        if match_type == 'exact' and text == kw:
            return rule
        elif match_type == 'contains' and kw in text:
            return rule
        elif match_type == 'startswith' and text.startswith(kw):
            return rule
    return None
```

**Only the first matching rule is dispatched.** If you need fan-out (one utterance
triggers multiple rules), add a `fan_out: true` flag to STACK.yaml — not in scope
for v1. Use `priority` to control which rule wins when multiple would match.

**Rules are re-read from SQLite on every poll cycle** — no in-memory cache.
This means routing changes take effect within one poll interval without a daemon restart.

---

## Match Types

| match_type | Behavior | Example keyword | Matches |
|------------|----------|-----------------|---------|
| `exact` | Full string equality (stripped, lowercased) | `end` | "end", "END", " end " |
| `contains` | Substring present anywhere | `book idea` | "add book idea", "this is a book idea about python" |
| `startswith` | Utterance begins with keyword | `note` | "note remember to call Alex", "note meeting summary" |

---

## Destination Types

### 1. `game_ticket`

Creates a ticket in the GAME Command Center via its API.

```json
{
  "project_keyword": "GAME",
  "auto_approve": false,
  "priority": "medium",
  "tags": ["voice", "alexa"]
}
```

- `project_keyword` (required): GAME project name to file the ticket under
- `auto_approve` (optional, default false): if true, auto-approve after creation
- `priority` (optional, default "medium"): ticket priority
- `tags` (optional): list of tags to apply

Dispatch: `POST {GAME_API_URL}/api/project/{project_keyword}/ticket/create`
with `{title: utterance, description: utterance, tags: [...], priority: priority}`

---

### 2. `file_append`

Appends a formatted line to a local file. Creates file and parent directories
if they don't exist.

```json
{
  "path": "data/ideas/book.txt",
  "format": "[{timestamp}] {utterance}\n"
}
```

- `path` (required): file path relative to project root
- `format` (required): format string using Python `.format()` syntax

**Format string variables:**

| Variable | Value |
|----------|-------|
| `{utterance}` | Full raw utterance text |
| `{timestamp}` | ISO-8601 datetime, UTC, e.g. `2026-03-11T14:23:01Z` |
| `{date}` | Date only, e.g. `2026-03-11` |
| `{keyword}` | Matched keyword from the rule |
| `{message_id}` | SQS message ID |

Example output line: `[2026-03-11T14:23:01Z] add dark mode to login screen`

---

### 3. `api_endpoint`

HTTP POST (or GET) to any URL. Useful for webhooks, local services, or IFTTT.

```json
{
  "url": "http://localhost:5001/api/ingest",
  "method": "POST",
  "headers": {"Authorization": "Bearer token"},
  "body_template": "{\"text\": \"{utterance}\", \"source\": \"alexa\"}"
}
```

- `url` (required): full URL
- `method` (optional, default "POST"): HTTP method
- `headers` (optional): dict of extra headers. `Content-Type: application/json` is always sent.
- `body_template` (optional): JSON string with `{utterance}` substitution. If omitted,
  sends the full SQS message envelope as JSON body.

Dispatch timeout: 10 seconds. On timeout, mark `status='failed'`, log error, do not delete from SQS.

---

### 4. `run_script`

Runs a local shell script or Python file. The utterance is passed as `$1`
(argv[1]) and also via `ALEXA_UTTERANCE` environment variable.

```json
{
  "script": "bin/process-idea.sh",
  "timeout": 30,
  "cwd": null
}
```

- `script` (required): path relative to project root
- `timeout` (optional, default 30): seconds before SIGTERM
- `cwd` (optional): working directory override; defaults to project root

The daemon calls: `subprocess.run([script, utterance], timeout=timeout, capture_output=True)`

stdout/stderr is captured and stored in `message_log.result` as JSON:
`{"stdout": "...", "stderr": "...", "returncode": 0}`

Non-zero returncode = dispatch failure; retry logic applies.

---

### 5. `slack_webhook`

Posts a formatted message to a Slack incoming webhook.

```json
{
  "webhook_url": "https://hooks.slack.com/services/T.../B.../...",
  "channel": "#voice-log",
  "username": "Alexa",
  "icon_emoji": ":microphone:",
  "template": "*{keyword}*: {utterance}"
}
```

- `webhook_url` (required): Slack incoming webhook URL
- `channel` (optional): override channel
- `username` (optional): display name
- `icon_emoji` (optional): emoji icon
- `template` (optional, default "`{utterance}`"): message text template

---

## Special Destination: `session_close`

Not a real destination — a sentinel value handled entirely within the daemon.
When matched, the daemon:
1. Deletes the message from SQS
2. Logs a `session_close` event to audit_log
3. Does NOT dispatch externally
4. The Lambda has already told Alexa to close the session via `shouldEndSession: true`

---

## Priority and Conflict Resolution

| Priority value | Meaning |
|---------------|---------|
| 0–49 | High priority — always evaluated first |
| 50–99 | Normal priority |
| 100+ | Low priority / fallback rules |

**Default seed rules all use priority 100.** If a user adds a more specific rule
(e.g. `"book idea for work"` as `exact`), give it a lower priority integer so it
wins over the broader `"book idea"` `contains` rule.

---

## Config UI Integration

See 08-CONFIG-UI.md for the routing rules management screens. The UI provides:
- List view of all rules (sortable by priority)
- Create / edit / delete forms
- Toggle enabled/disabled per rule without deleting
- Test a rule: enter sample utterance text, see which rule would match
