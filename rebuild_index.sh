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
import json
import os
import re

def generate_root_index():
    """Generate the root Specifications/index.html with FOUNDATION + PROJECT links."""

    # Read foundation docs
    foundation_files = [
        'CLAUDE_RULES.md',
        'FEATURES.md',
    ]

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
            if md_files and entry not in ['__pycache__', '.git', 'venv']:
                projects.append({
                    'name': entry,
                    'display_name': entry.replace('_', ' ').title(),
                    'md_count': len(md_files)
                })

    # Generate DOCS JS object
    docs_js = "const DOCS = {\n"
    for key, text in foundation_docs.items():
        docs_js += f"  {json.dumps(key)}: {json.dumps(text)},\n"
    docs_js += "};"

    # Read the HTML template
    html_template = open('_root_index_template.html', 'r', encoding='utf-8').read()

    # Generate project links
    project_links_html = ""
    for proj in projects:
        project_links_html += f'<a href="{proj["name"]}/index.html" class="project-link">{proj["display_name"]}</a>\n'

    # Replace placeholders
    html = html_template.replace('<!-- PROJECT_LINKS -->', project_links_html)
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

    # Replace placeholders
    display_name = project_name.replace('_', ' ').title()
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
