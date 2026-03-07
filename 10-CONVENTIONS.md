# Conventions & Supporting Modules

## CLAUDE.md Convention (`claude_convention.py`)

Defines a standard structure for project CLAUDE.md files and provides parsing/stubbing utilities.

### Standard Sections (in order)

1. `## Project Overview` — What the project does
2. `## Architecture` — Tech stack, key files, patterns
3. `## Dev Commands` — Bash commands to run the project
4. `## Service Endpoints` — URLs: `- Label: https://url`
5. `## Bookmarks` — Grouped links: `### Group` then `- [Title](URL)`

### Section Rename Map

Variant headings automatically renamed to standard:
- `## Commands` / `## Development Commands` / `## Build Commands` → `## Dev Commands`
- `## Overview` / `## Project Purpose` → `## Project Overview`
- `## Stack` → `## Architecture`

### Functions

- `resolve_claude_file(path)` — Returns `(filepath, content)`. Follows `@agents.md` redirects (CLAUDE.md containing just `@agents.md` reads that file instead).
- `parse_claude_md(content)` — Extracts:
  - `endpoints`: list of `{label, url}` from `## Service Endpoints` section
  - `bookmarks`: dict of `{group: [{title, url}]}` from `## Bookmarks` section
- `rename_sections(content)` — Replaces variant headings with standard names
- `generate_stubs(content)` — Appends missing standard sections with TODO placeholders
- `stub_project_claude(path)` — Creates or updates CLAUDE.md with stubs. Handles `@agents.md` redirects.

## Project Type Registry (`models.py`)

```python
PROJECT_TYPES = {
    'software': {
        'label': 'Software',
        'detail_template': 'types/_software_detail.html',
        'row_template': 'types/_software_row.html',
        'fields': ['tech_stack', 'port', 'remote_url', 'railway_id', 'website_url'],
        'default_ops': {
            'flask':  [('Start Server', 'local', 'flask run --port {port}', True)],
            'django': [('Start Server', 'local', 'python manage.py runserver {port}', True)],
            'node':   [('Start Dev', 'local', 'npm run dev', False)],
            'astro':  [('Start Dev', 'local', 'npm run dev', False)],
            'bash':   [('Run Script', 'local', './start.sh', False)],
        },
    },
    'book': {
        'label': 'Book',
        'detail_template': 'types/_book_detail.html',
        'row_template': 'types/_book_row.html',
        'fields': [],
        'default_ops': {},
    },
}
```

To add a new project type:
1. Add entry to `PROJECT_TYPES` dict
2. Create `types/_newtype_row.html` (include `_project_standard_columns.html`)
3. Create `types/_newtype_detail.html` (extend `base.html`)

## Usage Analyzer (`usage_analyzer.py`)

Reads Claude Code session JSONL files from `~/.claude/projects/**/*.jsonl` and generates interactive HTML reports.

### Data Collection
- Scans all `.jsonl` files in `.claude/projects/` recursively
- Filters by date range (last N days)
- Extracts usage data: input_tokens, output_tokens, cache_read, cache_creation
- Groups by: day, project, tool

### Report Output
- Summary cards: total consumed, input, output, messages, weekly budget %
- Daily bar chart (Plotly)
- Project breakdown horizontal bar chart
- Tool usage bar chart
- Outlier detection: flags requests > 2 standard deviations above mean

### CLI Usage
```bash
python usage_analyzer.py --days 30 -o report.html --outliers
```

### Flask Integration
```python
report_html = usage_analyzer.generate_report(days_back=7, flag_outliers=False)
```

## Workflow States

Configurable via `workflow.json` at project root:

```json
{
  "workflow_states": [
    {"key": "todo",       "label": "TODO",       "color": "#fdab3d"},
    {"key": "developing", "label": "DEVELOPING",  "color": "#0073ea"},
    {"key": "good",       "label": "GOOD",        "color": "#00c875"}
  ]
}
```

Falls back to built-in defaults if file doesn't exist or can't be parsed. States are displayed as colored badges and selectable via dropdowns.

## CommandCenter Operation Header Format

Bash scripts in project `bin/` directories can register as Command Center operations:

```bash
#!/bin/bash
# CommandCenter Operation
# Name: Service Start
# Port: 8000

# ... script body ...
```

Required:
- `# CommandCenter Operation` marker (exact match)
- `# Name: {name}` — display name in UI

Optional:
- `# Port: {number}` — default port number

Scanner reads first 20 lines of each `bin/*.sh` file looking for this header.

## Project Naming Convention

Directory names are converted to display titles:
- `HerpesHearts` → `Herpes Hearts` (CamelCase split)
- `My_Github` → `My Github` (underscore to space)
- `commandcenter` → `Commandcenter` (capitalize first word)

Implemented in `scanner.camel_to_title()`.

## Metadata Files Convention

### Links.md (per project)
```markdown
| Label | URL |
|-------|-----|
| Local Dev | http://localhost:8000 |
| Production | https://example.com |
```

### git_homepage.md (per project)
```markdown
| Field | Value |
|-------|-------|
| Title | My Project Title |
| Description | Project description here |
| Card Type | Software |
| Card URL | https://example.com |
| Tags | tag1, tag2, tag3 |
| Show on Homepage | true |
```

Both use markdown table format. Parsed by scanner at startup.
