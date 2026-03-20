#!/bin/bash
# Rebuilds index.html files in the Specifications directory.
# Generates:
#   - Specifications/index.html (FOUNDATION + PROJECT links)
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
    """Parse key: value fields from METADATA.md."""
    fields = {}
    if os.path.isfile(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as mf:
            for line in mf:
                if ':' in line and not line.startswith('#'):
                    k, v = line.split(':', 1)
                    fields[k.strip()] = v.strip()
    return fields


def is_project_dir(entry):
    """True if directory is a real project spec (has METADATA.md, not a build artifact)."""
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
    # Skip build pipeline artifact directories
    fields = read_meta_fields(meta)
    if fields.get('type', '').lower() in ('build', 'build-artifact'):
        return False
    return True


def generate_root_index():
    """Generate the root Specifications/index.html."""

    # Foundation docs: .md files at root (not README, not TODO)
    foundation_files = sorted([
        f for f in os.listdir('.')
        if f.endswith('.md') and os.path.isfile(f)
        and f not in ['README.md', 'TODO.md']
    ])

    foundation_docs = {}
    for fname in foundation_files:
        with open(fname, 'r', encoding='utf-8') as f:
            foundation_docs[fname.replace('.md', '')] = f.read()

    # Find project directories
    projects = []
    for entry in sorted(os.listdir('.')):
        if not is_project_dir(entry):
            continue
        fpath = os.path.join('.', entry)
        fields = read_meta_fields(os.path.join(fpath, 'METADATA.md'))
        display = fields.get('display_name') or fields.get('name') or entry.replace('_', ' ')
        status = fields.get('status', '')
        desc = fields.get('short_description', '')
        md_files = [f for f in os.listdir(fpath)
                    if f.endswith('.md')
                    and not f.startswith('PROPOSED')
                    and not f.startswith('UNUSED')]
        projects.append({
            'name': entry, 'display_name': display,
            'status': status, 'description': desc,
            'md_count': len(md_files),
        })

    # DOCS JS for foundation content
    docs_js = "const DOCS = {\n"
    for key, text in foundation_docs.items():
        docs_js += f"  {json.dumps(key)}: {json.dumps(text)},\n"
    docs_js += "};"

    html_template = open('_root_index_template.html', 'r', encoding='utf-8').read()

    # Foundation sidebar nav
    foundation_nav = ""
    for key in foundation_docs:
        label = key.replace('_', ' ').replace('-', ' ').title()
        foundation_nav += f'      <a class="nav-item" onclick="showDoc(\'{key}\')">{label}</a>\n'

    # Foundation cards
    foundation_cards = ""
    for key, text in foundation_docs.items():
        label = key.replace('_', ' ').replace('-', ' ').title()
        lines = [l.strip() for l in text.split('\n')
                 if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('<!--')]
        desc = lines[0][:120] if lines else 'Foundation document'
        desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc)
        desc = re.sub(r'\*([^*]+)\*', r'\1', desc)
        desc = html_mod.escape(desc)
        foundation_cards += f'''      <div class="card" onclick="showDoc('{key}')">
        <h3>{label}</h3>
        <p>{desc}</p>
      </div>\n'''

    # Project sidebar nav
    project_nav = ""
    for proj in projects:
        project_nav += f'      <a href="{proj["name"]}/index.html" class="nav-item">{proj["display_name"]}</a>\n'

    # Project cards with status badges
    project_cards = ""
    for proj in projects:
        color = STATUS_COLORS.get(proj['status'], '#94a3b8')
        badge = ''
        if proj['status']:
            badge = f'<span class="badge" style="background:{color}">{proj["status"]}</span>'
        desc = html_mod.escape(proj['description']) if proj['description'] else f'{proj["md_count"]} specification files'
        project_cards += f'''      <a href="{proj["name"]}/index.html" class="card" style="text-decoration:none">
        <h3>{proj["display_name"]}</h3>
        <p>{desc}</p>
        {badge}
      </a>\n'''

    html = html_template
    html = html.replace('<!-- FOUNDATION_NAV -->', foundation_nav)
    html = html.replace('<!-- FOUNDATION_CARDS -->', foundation_cards)
    html = html.replace('<!-- PROJECT_LINKS -->', project_nav)
    html = html.replace('<!-- PROJECT_CARDS -->', project_cards)
    html = html.replace('const DOCS = {};', docs_js)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated Specifications/index.html with {len(foundation_docs)} foundation docs + {len(projects)} projects")
    return projects


def generate_project_index(project_name):
    """Generate a per-project index.html with grouped file navigation."""
    project_dir = os.path.join('.', project_name)

    # Read .md files, skip PROPOSED/UNUSED
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
    display_name = fields.get('display_name') or fields.get('name') or project_name.replace('_', ' ')

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
