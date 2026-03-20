#!/bin/bash
# CommandCenter Operation
# Name: Rebuild Index
# Category: maintenance
#
# Rebuilds index.html files in the Specifications directory.
# Generates:
#   - Specifications/index.html (redirect to doc/index.html)
#   - Specifications/PROJECT/index.html (per-project spec viewer)
# Run this any time a .md file changes.
# Usage: bash bin/rebuild_index.sh (from any directory)

set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

python3 - <<'PYEOF'
import html as html_mod
import json
import os
import re

SKIP_DIRS = {
    '__pycache__', '.git', 'venv', 'archive', 'stack', 'bin', 'templates',
    'doc', 'logs', 'GLOBAL_RULES',
}

STATUS_COLORS = {
    'IDEA': '#94a3b8', 'PROTOTYPE': '#fdab3d', 'ACTIVE': '#0073ea',
    'PRODUCTION': '#00c875', 'ARCHIVED': '#4a5568',
}


def read_meta_fields(meta_path):
    fields = {}
    if os.path.isfile(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as mf:
            for line in mf:
                if ':' in line and not line.startswith('#'):
                    k, v = line.split(':', 1)
                    fields[k.strip()] = v.strip()
    return fields


def is_project_dir(entry):
    if entry.startswith('.') or entry.startswith('Proposed'):
        return False
    if entry in SKIP_DIRS:
        return False
    fpath = os.path.join('.', entry)
    if not os.path.isdir(fpath):
        return False
    meta = os.path.join(fpath, 'METADATA.md')
    if not os.path.isfile(meta):
        return False
    fields = read_meta_fields(meta)
    if fields.get('type', '').lower() in ('build', 'build-artifact'):
        return False
    return True


def generate_root_index():
    """Root index.html is a redirect to doc/index.html."""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url=doc/index.html">
<title>Prototyper — Redirecting...</title>
</head>
<body>
<p>Redirecting to <a href="doc/index.html">Prototyper Documentation</a>...</p>
</body>
</html>'''
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Generated Specifications/index.html (redirect to doc/index.html)")

    # Return project list for project index generation
    projects = []
    for entry in sorted(os.listdir('.')):
        if not is_project_dir(entry):
            continue
        fpath = os.path.join('.', entry)
        fields = read_meta_fields(os.path.join(fpath, 'METADATA.md'))
        display = fields.get('display_name') or fields.get('name') or entry
        projects.append({'name': entry, 'display_name': display})
    return projects


def generate_project_index(project_name):
    """Generate a per-project index.html with grouped file navigation."""
    project_dir = os.path.join('.', project_name)

    docs = {}
    for fname in sorted(os.listdir(project_dir)):
        if not fname.endswith('.md'):
            continue
        if fname.startswith('PROPOSED') or fname.startswith('UNUSED'):
            continue
        with open(os.path.join(project_dir, fname), 'r', encoding='utf-8') as f:
            docs[fname.replace('.md', '')] = f.read()

    docs_js = "const DOCS = {\n"
    for key, text in docs.items():
        docs_js += f"  {json.dumps(key)}: {json.dumps(text)},\n"
    docs_js += "};"

    html_template = open('_project_index_template.html', 'r', encoding='utf-8').read()

    fields = read_meta_fields(os.path.join(project_dir, 'METADATA.md'))
    display_name = fields.get('display_name') or fields.get('name') or project_name

    html = html_template.replace('<!-- PROJECT_NAME -->', display_name)
    html = html.replace('const DOCS = {};', docs_js)

    with open(os.path.join(project_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated {project_name}/index.html with {len(docs)} docs")


# Run
projects = generate_root_index()
for proj in projects:
    generate_project_index(proj['name'])
print("\nAll index.html files generated successfully!")
PYEOF
