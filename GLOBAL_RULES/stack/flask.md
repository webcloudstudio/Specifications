# Flask Best Practices

**Version:** 20260320 V1  
**Description:** Flask web framework patterns: routes, blueprints, templates, and error handling

Technology reference for Flask web applications. This file does not change between projects.

Prerequisites: `stack/common.md`, `stack/python.md`

---

## 1. Application Factory

**Rule**: Use a `create_app()` factory function. Initialize extensions and register blueprints inside it.

```python
# app.py
from flask import Flask

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or 'config.DevConfig')

    # Initialize database
    from db import init_db
    with app.app_context():
        init_db()

    # Register routes
    from routes import bp
    app.register_blueprint(bp)

    # Register error handlers
    from errors import register_error_handlers
    register_error_handlers(app)

    # Startup validation
    from startup import validate_startup
    validate_startup(app)

    return app

if __name__ == '__main__':
    import os
    app = create_app()
    app.run(port=int(os.environ.get('APP_PORT', 5001)))
```

**Why**: Factory pattern enables creating multiple app instances with different configs — essential for testing. Deferred imports prevent circular dependencies.

---

## 2. Blueprints and Route Organization

**Rule**: Keep route handlers thin. Extract business logic into separate modules. Group related routes with Blueprints.

```python
# routes.py
from flask import Blueprint, render_template, request, jsonify
import ops

bp = Blueprint('main', __name__)

@bp.route('/projects')
def projects_list():
    projects = ops.get_all_projects()
    return render_template('projects.html', projects=projects)

@bp.route('/api/project/<int:project_id>/start', methods=['POST'])
def start_project(project_id):
    result = ops.start_service(project_id)  # Logic in ops.py, not here
    return jsonify(result)
```

```python
# ops.py — business logic, no Flask imports needed
from db import get_db

def get_all_projects():
    db = get_db()
    return db.execute('SELECT * FROM projects ORDER BY title').fetchall()

def start_service(project_id):
    ...
    return {'status': 'started', 'pid': pid}
```

Rules:
- Route handlers do: parse request, call business logic, return response
- Route handlers don't: contain SQL, file I/O, subprocess calls, or complex logic
- One Blueprint per feature area for larger apps
- API routes return JSON; page routes return rendered templates

**Why**: Thin routes are testable and readable. Business logic in separate modules can be reused without Flask context.

---

## 3. Error Handling

**Rule**: Register Flask error handlers for 404/500. Return JSON for API routes, HTML for page routes. Never expose stack traces.

```python
# errors.py
from flask import render_template, jsonify, request

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error('Internal error: %s', e, exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error('Unhandled exception: %s', e, exc_info=True)
        return render_template('500.html'), 500
```

**Why**: Dual response format (JSON/HTML) keeps API clients and browsers happy.

---

## 4. Templates (Jinja2)

**Rule**: Use template inheritance with `base.html`. Prefix partials with `_`. Keep logic out of templates.

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block head %}{% endblock %}
</head>
<body>
    {% include '_nav.html' %}
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    {% block scripts %}{% endblock %}
</body>
</html>
```

```html
<!-- templates/projects.html -->
{% extends 'base.html' %}
{% block title %}Projects{% endblock %}
{% block content %}
  <h1>Projects</h1>
  {% for p in projects %}
    {% include 'types/_project_row.html' %}
  {% endfor %}
{% endblock %}
```

Rules:
- All pages extend `base.html`
- Partials prefixed with `_` (e.g., `_nav.html`, `_project_row.html`)
- Type-specific partials in `templates/types/`
- No Python logic in templates — pass ready-to-render data from routes
- Use `url_for('static', filename=...)` for all static file references
- Auto-escaping is enabled by default — don't disable it

**Why**: Template inheritance eliminates duplication. Partial naming conventions make includes discoverable.

---

## 5. Context Processors

**Rule**: Use context processors to inject global data into all templates.

```python
@app.context_processor
def inject_globals():
    return {
        'app_name': app.config.get('APP_NAME', 'My App'),
        'running_count': ops.get_running_count(),
    }
```

**Why**: Avoids passing the same variables to every `render_template()` call.

---

## 6. HTMX Integration

**Rule**: Use HTMX for dynamic UI updates. Return HTML fragments from API endpoints. Use `HX-Trigger` headers for cross-component updates.

```python
@bp.route('/api/project/<int:project_id>/toggle', methods=['POST'])
def toggle_status(project_id):
    new_status = ops.toggle_status(project_id)
    project = ops.get_project(project_id)
    return render_template('types/_project_row.html', project=project)
```

```html
<button hx-post="/api/project/{{ p.id }}/toggle"
        hx-swap="outerHTML"
        hx-target="closest tr">
    Toggle
</button>
```

### OOB (Out-of-Band) Swaps

```python
html = render_template('types/_project_row.html', project=project)
html += render_template('_nav_badge.html', count=running_count)
response = make_response(html)
response.headers['HX-Trigger'] = 'projectUpdated'
return response
```

```html
<span id="running-badge" hx-swap-oob="true">{{ count }}</span>
```

**Why**: HTMX eliminates JavaScript for common interactions. HTML fragments are simpler than JSON APIs for server-rendered apps.

---

## 7. Testing with Flask Test Client

**Rule**: Test through the Flask test client. Use fixtures for app, client, and database.

```python
# tests/conftest.py
import pytest
from app import create_app
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    from db import get_db, init_db
    with app.app_context():
        init_db()
        yield get_db()
```

```python
# tests/test_routes.py
def test_projects_page(client):
    response = client.get('/projects')
    assert response.status_code == 200
    assert b'Projects' in response.data

def test_api_returns_json(client):
    response = client.get('/api/projects')
    assert response.content_type == 'application/json'

def test_htmx_endpoint(client):
    response = client.post('/api/project/1/toggle',
                          headers={'HX-Request': 'true'})
    assert response.status_code == 200
```

**Why**: Test client exercises the full stack without a running server.

---

## 8. Security

**Rule**: Set secure headers. Validate all input. Debug mode off in production.

```python
@app.after_request
def set_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response
```

Flask security checklist:
- Jinja2 auto-escaping enabled (default — don't disable)
- `SECRET_KEY` set from environment variable in production
- `secure_filename()` from werkzeug for file uploads
- Input validation on all form data (length, type, allowed values)
- Debug mode disabled in production (`FLASK_DEBUG=0`)

---

## 9. Health Check

**Rule**: Expose a `/health` endpoint that verifies database connectivity.

```python
@bp.route('/health')
def health():
    try:
        db = get_db()
        db.execute('SELECT 1')
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'detail': str(e)}), 500
```

---

## 10. Debug Mode and Reloading

**Rule**: Use Flask's debug mode in development only. Understand the reloader behavior.

```bash
# Development
FLASK_DEBUG=1 flask run --port 5001

# Production
gunicorn app:create_app()
```

Key behaviors in debug mode:
- **Auto-reloader**: Restarts server on Python file changes
- **Double startup**: `WERKZEUG_RUN_MAIN` check needed to avoid running startup code twice
- **Interactive debugger**: Shows in browser on errors (never expose in prod)

```python
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
    run_scanner()
```

---

## Standard bin/ Scripts for Flask

```bash
# bin/start.sh
#!/bin/bash
# CommandCenter Operation
# Name: Service Start
# Type: daemon
# Port: 5001

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source venv/bin/activate
FLASK_DEBUG=1 flask run --port 5001 2>&1
```

```bash
# bin/stop.sh
#!/bin/bash
# CommandCenter Operation
# Name: Service Stop
# Type: batch

pkill -f "flask run --port 5001" || echo "No Flask process found"
```

```bash
# bin/test.sh
#!/bin/bash
# CommandCenter Operation
# Name: Run Tests
# Type: batch

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source venv/bin/activate
python -m pytest tests/ -v 2>&1
```

---

## Summary Checklist

- [ ] Application factory with `create_app()`
- [ ] Blueprints with thin route handlers
- [ ] Error handlers for 404/500 (JSON + HTML)
- [ ] Template inheritance from `base.html`, partials prefixed with `_`
- [ ] Context processors for global template data
- [ ] HTMX for dynamic UI (HTML fragments, OOB swaps)
- [ ] Test client fixtures in conftest.py
- [ ] Secure headers and input validation
- [ ] `/health` endpoint
- [ ] Debug mode only in dev, `WERKZEUG_RUN_MAIN` guard
- [ ] Standard `bin/` scripts: start.sh, stop.sh, test.sh
