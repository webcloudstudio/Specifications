# Application Startup & Configuration

## Startup Sequence

```
app.py: create_app()
  1. Create Flask app
  2. Set config: SECRET_KEY, PROJECTS_DIR, PRODUCTION_URL, APP_NAME
  3. db.init_db()
     a. Create data/ directory if needed
     b. Execute SCHEMA (CREATE TABLE IF NOT EXISTS for all 3 tables)
     c. Run migrations (add missing columns)
  4. If WERKZEUG_RUN_MAIN == 'true' (avoids double-run in debug mode):
     a. scanner.cleanup_orphaned(PROJECTS_DIR) — remove stale DB entries
     b. scanner.scan_projects(PROJECTS_DIR) — discover and upsert all projects
  5. Register routes blueprint
  6. Return app
```

## Running the Server

```bash
# Set required env var
export PROJECTS_DIR=~/projects

# Activate virtual environment
source venv/bin/activate

# Run Flask (debug mode with auto-reload)
flask run --port 5001
```

Or directly:
```bash
python app.py  # Runs on 127.0.0.1:8080 in debug mode
```

## Flask Configuration

| Key | Source | Default |
|-----|--------|---------|
| `SECRET_KEY` | env `SECRET_KEY` | `cc-dev-key-change-in-prod` |
| `PROJECTS_DIR` | env `PROJECTS_DIR` | Parent of app directory |
| `PRODUCTION_URL` | env `PRODUCTION_URL` | `https://webcloudstudio.github.io` |
| `APP_NAME` | env `APP_NAME` | `Command Center` |

## Debug Mode Behavior

- Flask's debug reloader runs `create_app()` twice: once in the parent process, once in the reloader child
- Scanner only runs when `WERKZEUG_RUN_MAIN=true` (the reloader child) to avoid duplicate scans
- Auto-restart on Python file changes (but not template/CSS changes)

## Data Directory

`data/` is created automatically by `get_db()` if it doesn't exist. Contains:
- `cc.db` — SQLite database
- `logs/` — Process log files (created by ops.py and spawn.py)
- `tag_colors.json` — Tag color mappings (created by tags route)
- `publish_clicks.json` — Pipeline button click timestamps (created by publisher)

All items in `data/` should be gitignored.

## Blueprint Registration

All routes are in a single Blueprint named `'cc'` with `static_folder='static'`. This means:
- Static files served at `/static/style.css` via `url_for('cc.static', filename='style.css')`
- All route names prefixed with `cc.` (e.g., `url_for('cc.project_list')`)
