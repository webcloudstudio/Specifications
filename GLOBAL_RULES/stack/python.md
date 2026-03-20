# Python Best Practices

**Version:** 20260320 V1  
**Description:** Python language conventions and patterns for spec-driven projects

Technology reference for Python development. Framework-agnostic — applies to any Python project. This file does not change between projects.

Prerequisite: `stack/common.md`

---

## 1. Configuration Management

**Rule**: Use environment variables loaded via `python-dotenv`. Never hardcode secrets, ports, or paths.

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-me')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'data/app.db')
    DEBUG = False

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    SECRET_KEY = os.environ['SECRET_KEY']  # Crash if missing in prod

class TestConfig(Config):
    DATABASE_PATH = ':memory:'
    TESTING = True
```

```bash
# .env
SECRET_KEY=your-secret-here
DATABASE_PATH=data/app.db
APP_PORT=5001
```

**Why**: Config classes make environment switching explicit. Crashing on missing secrets in prod prevents silent misconfiguration.

---

## 2. Logging

**Rule**: Use Python's `logging` module with named loggers, never `print()`. Configure formatters and handlers at startup.

```python
import logging
import os

def setup_logging(level=None):
    level = level or ('DEBUG' if os.getenv('APP_DEBUG') else 'INFO')

    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(console)

    # File handler
    os.makedirs('data/logs', exist_ok=True)
    file_handler = logging.FileHandler('data/logs/app.log')
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)
```

```python
# In any module
import logging
logger = logging.getLogger(__name__)

logger.info('Server starting on port %s', port)
logger.error('Failed to connect: %s', err)
```

**Why**: Named loggers trace messages to source modules. Structured format enables log parsing.

---

## 3. Environment Separation

**Rule**: Maintain distinct configs for dev/test/prod. Never run debug mode in production.

| Setting | Dev | Test | Prod |
|---------|-----|------|------|
| DEBUG | True | False | False |
| DATABASE | data/app.db | :memory: | data/app.db |
| SECRET_KEY | hardcoded default | hardcoded default | env var (required) |
| LOGGING | DEBUG | WARNING | INFO |

**Why**: Environment separation prevents dev shortcuts from reaching production.

---

## 4. Testing

**Rule**: Use `pytest` with fixtures. Isolate each test with a fresh database. Test at the boundary, not internals.

```python
# tests/conftest.py
import pytest

@pytest.fixture
def db():
    """Provide a clean in-memory database for each test."""
    from db import get_db, init_db
    init_db(':memory:')
    yield get_db()
```

```python
# tests/test_ops.py
def test_create_project(db):
    from ops import create_project
    project = create_project(db, title='Test')
    assert project is not None
    row = db.execute('SELECT * FROM projects WHERE title = ?', ('Test',)).fetchone()
    assert row is not None
```

**Why**: Fixtures ensure clean state per test. In-memory DB makes tests fast.

---

## 5. Security Basics

**Rule**: Validate all user input. Use parameterized queries exclusively. Never trust client data.

Checklist:
- Parameterized queries for all DB operations (`?` placeholders, never f-strings)
- `secure_filename()` for any file path from user input
- Length and type validation on inputs
- Secret key loaded from environment, not hardcoded in prod
- Never expose stack traces to end users

**Why**: These basics prevent the most common attack vectors with minimal effort.

---

## 6. Dependency Management

**Rule**: Pin exact versions in `requirements.txt`. Always use virtual environments. Keep dependencies minimal.

```bash
python -m venv venv
source venv/bin/activate
pip install flask python-dotenv
pip freeze > requirements.txt
```

```
# requirements.txt — pin exact versions
Flask==3.1.0
python-dotenv==1.0.1
```

Rules:
- One `requirements.txt` at project root
- Pin exact versions (`==`), not ranges
- `pip freeze > requirements.txt` after any install
- Keep it small — prefer stdlib over third-party
- `venv/` directory is always gitignored

**Why**: Pinned versions ensure reproducible builds. Fewer dependencies mean fewer security vulnerabilities.

---

## 7. Health Check and Startup Validation

**Rule**: Validate required config and DB connectivity at startup. Crash early on misconfiguration.

```python
def validate_startup():
    """Crash early if critical config is missing."""
    required_vars = ['PROJECTS_DIR']
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        raise RuntimeError(f'Missing required env vars: {", ".join(missing)}')

    from db import get_db
    try:
        get_db().execute('SELECT 1')
    except Exception as e:
        raise RuntimeError(f'Database not accessible: {e}')

    logger.info('Startup validation passed')
```

**Why**: Startup validation catches misconfigurations immediately rather than at first user request.

---

## 8. Project Directory Layout (Python-specific)

Python web projects extend the common layout:

```
project-name/
├── app.py              # Entry point / app factory
├── routes.py           # Route handlers
├── models.py           # Data models and type registries
├── db.py               # Database connection, schema, migrations
├── ops.py              # Business logic and operations
├── config.py           # Config classes (Dev/Prod/Test)
├── templates/          # Jinja2 or Django templates
│   ├── base.html
│   └── types/          # Type-specific partials
├── static/
│   ├── css/
│   └── js/
├── tests/
│   ├── conftest.py
│   └── test_*.py
├── bin/                # (from common.md)
├── data/               # (from common.md)
├── requirements.txt
├── .env
├── .gitignore
├── CLAUDE.md
└── Links.md
```

---

## Summary Checklist

- [ ] Config via env vars with `python-dotenv`, no hardcoded secrets
- [ ] Logging with named loggers, not `print()`
- [ ] Distinct dev/test/prod configs
- [ ] pytest with fixtures and isolated test DB
- [ ] Input validation, parameterized queries
- [ ] Pinned dependencies in requirements.txt, venv gitignored
- [ ] Startup validation for required config
