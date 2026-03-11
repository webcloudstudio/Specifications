# 08 — Configuration UI

Standalone Flask application at port 5002. Provides routing rules management,
message history, and confirmation approvals. It is NOT embedded in GAME — it
runs as an independent service. The Flask UI and the daemon share the same
SQLite database but are separate processes.

---

## Pages and Routes

### Dashboard — `GET /`

The homepage. Shows live operational status at a glance.

**Sections (top to bottom):**

1. **Pending Confirmations** (shown only if count > 0)
   - Orange/warning highlight
   - Table: Utterance | Rule | Time Ago | Destination | Approve | Reject
   - HTMX: approve/reject update row in-place, decrement counter

2. **Queue Stats** (4 stat cards)
   - SQS Depth: `GET /api/queue/depth` (boto3 ApproximateNumberOfMessages)
   - Messages Today: count from message_log
   - Completed Today: count where status='completed'
   - Failed / Pending: counts

3. **Daemon Status**
   - Green "Running" or red "Stopped" badge
   - Based on PID file + process check (see `GET /api/daemon/status`)

4. **Recent Messages** (last 20)
   - Table: Time | Utterance (truncated 60 chars) | Matched Rule | Status badge | Destination
   - Status badge colors: received=blue, dispatching=yellow, completed=green, failed=red, pending_confirm=orange

Auto-refreshes via HTMX `hx-trigger="every 10s"` on the stats and recent messages sections.

---

### Routing Rules — `GET /rules`

Full list of all routing_rules rows.

**Table columns:**
- Priority (sortable)
- Keyword
- Match Type badge (exact / contains / startswith)
- Destination Type
- Destination Summary (first 40 chars of config)
- Confirm? (checkbox icon)
- Enabled (toggle, HTMX inline update)
- Actions: Edit | Delete

**"New Rule" button** links to `GET /rules/new`.

---

### New Rule — `GET /rules/new`, `POST /rules`

Form fields:
- Keyword (text input)
- Match Type (select: contains / exact / startswith)
- Priority (number, default 100)
- Destination Type (select: game_ticket / file_append / api_endpoint / run_script / slack_webhook)
- Destination Config (textarea, JSON — hints shown below field for selected type)
- Requires Confirmation (checkbox)
- Description (text input, optional)
- Enabled (checkbox, default checked)

On POST: validate JSON in destination_config; return form with errors inline if invalid.
On success: redirect to `GET /rules`.

---

### Edit Rule — `GET /rules/<id>/edit`, `POST /rules/<id>`

Same form as New Rule, pre-populated. POST updates the row and redirects to `GET /rules`.

---

### Delete Rule — `POST /rules/<id>/delete`

Soft-confirm via Bootstrap modal (client-side JS). On confirm: delete row, redirect to `GET /rules`.
If the rule has associated message_log rows, set `matched_rule_id = NULL` (FK SET NULL).

---

### Message History — `GET /messages`

Paginated log of all messages. Default: 50 per page, most recent first.

**Filter bar:**
- Status: All / received / dispatching / completed / failed / pending_confirm / rejected
- Date range: today / last 7 days / custom
- Search: utterance text (LIKE match)

**Table columns:**
- Time (relative + full on hover)
- Utterance (full text)
- Status badge
- Rule matched (or "No rule")
- Destination
- Retry count (if > 0)
- Detail link → `GET /messages/<id>`

---

### Message Detail — `GET /messages/<id>`

Full record for one message:
- All `message_log` fields
- Associated confirmation record (if any)
- Audit log entries for this message (chronological)
- Raw SQS message body

---

### Test Rule — `GET /rules/test` (HTMX fragment endpoint)

Utility: enter an utterance, see which rule would match.

```
GET /rules/test?utterance=book+idea+about+python
→ Returns HTML fragment: "Matched: 'book idea' (contains) → file_append: data/ideas/book.txt"
  or "No rule matched."
```

Used inline in the Rules list page via HTMX.

---

## Templates

```
templates/
├── base.html                # Bootstrap5 dark theme, nav, HTMX CDN
├── dashboard.html           # extends base.html
├── rules/
│   ├── list.html
│   ├── form.html            # shared for new + edit
│   └── _rule_row.html       # HTMX partial for enabled toggle
├── messages/
│   ├── list.html
│   └── detail.html
└── partials/
    ├── _pending_confirmations.html  # HTMX auto-refresh target
    ├── _queue_stats.html            # HTMX auto-refresh target
    └── _recent_messages.html        # HTMX auto-refresh target
```

`base.html` includes:
- Bootstrap 5 CSS (CDN, dark theme via `data-bs-theme="dark"`)
- Bootstrap 5 JS bundle (CDN)
- HTMX (CDN, `hx-boost="true"` on body)
- Nav links: Dashboard | Rules | Messages

---

## HTMX Patterns

**Auto-refresh stats:**
```html
<div id="queue-stats"
     hx-get="/partials/queue-stats"
     hx-trigger="every 10s"
     hx-swap="outerHTML">
  ...current stats...
</div>
```

**Inline confirmation approve:**
```html
<button hx-post="/api/confirmations/{{ conf.id }}/approve"
        hx-target="#conf-row-{{ conf.id }}"
        hx-swap="outerHTML swap:0.5s"
        class="btn btn-sm btn-success">Approve</button>
```

**Enabled toggle:**
```html
<input type="checkbox" {{ 'checked' if rule.enabled }}
       hx-post="/api/rules/{{ rule.id }}/toggle"
       hx-swap="none">
```

---

## Flask Structure

```python
# app.py
from flask import Flask
from routes.dashboard import bp as dashboard_bp
from routes.rules import bp as rules_bp
from routes.messages import bp as messages_bp
from routes.api import bp as api_bp
from db import init_db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-me')
    with app.app_context():
        init_db()
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(rules_bp, url_prefix='/rules')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(api_bp, url_prefix='/api')
    return app
```

---

## Design System

Follows `stack/bootstrap5.md`. Key choices:
- `data-bs-theme="dark"` on `<html>`
- Primary color for actions: `btn-primary`
- Status badges: use `bg-success`, `bg-warning`, `bg-danger`, `bg-secondary`, `bg-info`
- Confirmation section: `border border-warning rounded p-3 mb-4`
- Stat cards: 4-column Bootstrap grid, `card` component with large number in `card-body`
