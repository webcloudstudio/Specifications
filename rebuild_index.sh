#!/bin/bash
# Rebuilds index.html files in the Specifications directory.
# Generates:
#   - Specifications/index.html (FOUNDATION + PROJECT links)
#   - Specifications/PROJECT/index.html (per-project spec viewer)
# Run this any time a .md file changes.
# Usage: bash rebuild_index.sh (from any directory)

set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

python3 - <<'PYEOF'
import html as html_mod
import json
import os
import re

def generate_root_index():
    """Generate the root Specifications/index.html with FOUNDATION + PROJECT links."""

    # Read foundation docs
    # Discover foundation docs: any .md file at root (not in subdirs)
    foundation_files = sorted([
        f for f in os.listdir('.')
        if f.endswith('.md') and os.path.isfile(f)
        and f not in ['README.md', 'TODO.md']
    ])

    foundation_docs = {}
    for fname in foundation_files:
        fpath = os.path.join('.', fname)
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                doc_key = fname.replace('.md', '')
                foundation_docs[doc_key] = f.read()

    # Find project directories (skip hidden, stack, etc.)
    projects = []
    for entry in sorted(os.listdir('.')):
        fpath = os.path.join('.', entry)
        if os.path.isdir(fpath) and not entry.startswith('.'):
            # Only include dirs that have .md files
            md_files = [f for f in os.listdir(fpath) if f.endswith('.md')]
            if md_files and entry not in ['__pycache__', '.git', 'venv', 'archive', 'stack']:
                # Try to read display_name or name from METADATA.md
                meta_path = os.path.join(fpath, 'METADATA.md')
                display = None
                if os.path.isfile(meta_path):
                    meta_fields = {}
                    with open(meta_path, 'r') as mf:
                        for line in mf:
                            if ':' in line and not line.startswith('#'):
                                k, v = line.split(':', 1)
                                meta_fields[k.strip()] = v.strip()
                    display = meta_fields.get('display_name') or meta_fields.get('name') or None
                if not display:
                    display = entry.replace('_', ' ')
                projects.append({
                    'name': entry,
                    'display_name': display,
                    'md_count': len(md_files)
                })

    # Generate DOCS JS object
    docs_js = "const DOCS = {\n"
    for key, text in foundation_docs.items():
        docs_js += f"  {json.dumps(key)}: {json.dumps(text)},\n"
    docs_js += "};"

    # Read the HTML template
    html_template = open('_root_index_template.html', 'r', encoding='utf-8').read()

    # Generate foundation nav items (sidebar)
    foundation_nav_html = ""
    for key in foundation_docs:
        display = key.replace('_', ' ').replace('-', ' ').title()
        foundation_nav_html += f'      <a class="nav-item" onclick="showDoc(\'{key}\')">{display}</a>\n'

    # Generate foundation cards (home panel)
    foundation_cards_html = ""
    for key, text in foundation_docs.items():
        display = key.replace('_', ' ').replace('-', ' ').title()
        # Extract first paragraph as description (strip markdown formatting)
        lines = [l.strip() for l in text.split('\n') if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('<!--')]
        desc = lines[0][:120] if lines else 'Foundation document'
        desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc)  # strip bold
        desc = re.sub(r'\*([^*]+)\*', r'\1', desc)  # strip italic
        desc = html_mod.escape(desc)
        foundation_cards_html += f'''      <div class="card" onclick="showDoc('{key}')">
        <h3>{display}</h3>
        <p>{desc}</p>
        <span class="tag foundation">Foundation</span>
      </div>\n'''

    # Generate project links (sidebar)
    project_nav_html = ""
    for proj in projects:
        project_nav_html += f'      <a href="{proj["name"]}/index.html" class="nav-item">{proj["display_name"]}</a>\n'

    # Generate project cards (home panel)
    project_cards_html = ""
    for proj in projects:
        project_cards_html += f'''      <a href="{proj["name"]}/index.html" class="card" style="text-decoration:none;">
        <h3>{proj["display_name"]}</h3>
        <p>{proj["md_count"]} specification files</p>
        <span class="tag feature">Project</span>
      </a>\n'''

    # Replace placeholders
    html = html_template.replace('<!-- FOUNDATION_NAV -->', foundation_nav_html)
    html = html.replace('<!-- FOUNDATION_CARDS -->', foundation_cards_html)
    html = html.replace('<!-- PROJECT_LINKS -->', project_nav_html)
    html = html.replace('<!-- PROJECT_CARDS -->', project_cards_html)
    html = html.replace('const DOCS = {};', docs_js)

    # Write root index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated Specifications/index.html with {len(foundation_docs)} foundation docs + {len(projects)} projects")
    return projects

def generate_project_index(project_name):
    """Generate a per-project index.html."""

    project_dir = os.path.join('.', project_name)

    # Read all .md files in the project directory
    docs = {}
    for fname in sorted(os.listdir(project_dir)):
        if fname.endswith('.md'):
            fpath = os.path.join(project_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                doc_key = fname.replace('.md', '')
                docs[doc_key] = f.read()

    # Generate DOCS JS object
    docs_js = "const DOCS = {\n"
    for key, text in docs.items():
        docs_js += f"  {json.dumps(key)}: {json.dumps(text)},\n"
    docs_js += "};"

    # Read project template
    html_template = open('_project_index_template.html', 'r', encoding='utf-8').read()

    # Try to read display_name or name from METADATA.md
    display_name = None
    meta_path = os.path.join(project_dir, 'METADATA.md')
    if os.path.isfile(meta_path):
        meta_fields = {}
        with open(meta_path, 'r') as mf:
            for line in mf:
                if ':' in line and not line.startswith('#'):
                    k, v = line.split(':', 1)
                    meta_fields[k.strip()] = v.strip()
        display_name = meta_fields.get('display_name') or meta_fields.get('name') or None
    if not display_name:
        display_name = project_name.replace('_', ' ')
    html = html_template.replace('<!-- PROJECT_NAME -->', display_name)
    html = html.replace('const DOCS = {};', docs_js)

    # Write project index.html
    output_path = os.path.join(project_dir, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated {project_name}/index.html with {len(docs)} docs")

# Generate root index
projects = generate_root_index()

# Generate per-project indices
for proj in projects:
    generate_project_index(proj['name'])

print("\nAll index.html files generated successfully!")
PYEOF
