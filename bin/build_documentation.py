#!/usr/bin/env python3
"""
Build doc/index.html — single-page documentation for the Specifications repo.

Renders the workflow (SPECIFICATION-PROCESS.md), setup guide (PROJECT-SETUP.md),
and links to discovered project spec directories.
"""
import html as html_lib
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DOC_DIR = PROJECT_DIR / "doc"

SKIP_DIRS = {
    'archive', 'bin', 'doc', 'GLOBAL_RULES', 'logs', 'venv',
    '__pycache__', '.git',
}

STATUS_COLORS = {
    'IDEA': '#94a3b8', 'PROTOTYPE': '#fdab3d', 'ACTIVE': '#0073ea',
    'PRODUCTION': '#00c875', 'ARCHIVED': '#4a5568',
}


def read_meta(path):
    """Parse key: value fields from a METADATA.md file."""
    fields = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
            if ':' in line and not line.startswith('#'):
                k, v = line.split(':', 1)
                fields[k.strip()] = v.strip()
    return fields


def discover_projects():
    """Find real project spec directories (not build artifacts, proposed, etc.)."""
    projects = []
    for entry in sorted(PROJECT_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith('.') or entry.name.startswith('Proposed'):
            continue
        if entry.name in SKIP_DIRS:
            continue
        meta = entry / "METADATA.md"
        if not meta.exists():
            continue
        fields = read_meta(meta)
        # Skip build pipeline artifacts
        if fields.get('type', '').lower() in ('build', 'build-artifact'):
            continue
        display = fields.get('display_name', entry.name)
        status = fields.get('status', '')
        desc = fields.get('short_description', '')
        md_files = sorted(
            [f.name for f in entry.iterdir()
             if f.suffix == '.md'
             and not f.name.startswith('PROPOSED')
             and not f.name.startswith('UNUSED')],
            key=lambda n: (0 if n == 'METADATA.md' else 1, n)
        )
        if md_files:
            projects.append((entry.name, display, status, desc, md_files))
    return projects


# ── Markdown → HTML ──────────────────────────────────────────────────────────

def inline(text):
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for p in parts:
        if p.startswith('`') and p.endswith('`') and len(p) > 2:
            out.append(f'<code>{html_lib.escape(p[1:-1])}</code>')
        else:
            p = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p)
            p = re.sub(r'(?<!\w)\*([^*\n]+?)\*(?!\w)', r'<em>\1</em>', p)
            p = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                       lambda m: f'<a href="{html_lib.escape(m.group(2))}">{m.group(1)}</a>', p)
            out.append(p)
    return ''.join(out)


def md_to_html(text):
    lines = text.splitlines()
    out = []
    i = 0
    in_list = None
    para = []

    def flush():
        nonlocal para
        if para:
            out.append(f'<p>{inline(" ".join(para))}</p>')
            para = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f'</{in_list}>')
            in_list = None

    while i < len(lines):
        line = lines[i]
        if line.startswith('```'):
            flush(); close_list(); i += 1
            code = []
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i]); i += 1
            i += 1
            out.append(f'<pre><code>{html_lib.escape(chr(10).join(code))}</code></pre>')
            continue
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            flush(); close_list()
            out.append(f'<h{len(m.group(1))}>{inline(m.group(2).strip())}</h{len(m.group(1))}>')
            i += 1; continue
        if re.match(r'^(?:---+|\*\*\*+|___+)\s*$', line):
            flush(); close_list(); out.append('<hr>'); i += 1; continue
        if line.lstrip().startswith('|') and '|' in line:
            flush(); close_list()
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                rows.append(lines[i]); i += 1
            if len(rows) >= 2:
                cells = lambda r: [c.strip() for c in r.strip().strip('|').split('|')]
                out.append('<table><thead><tr>')
                for h in cells(rows[0]):
                    out.append(f'<th>{inline(h)}</th>')
                out.append('</tr></thead><tbody>')
                for row in rows[2:]:
                    if re.match(r'^[\s|:-]+$', row): continue
                    out.append('<tr>')
                    for c in cells(row):
                        out.append(f'<td>{inline(c)}</td>')
                    out.append('</tr>')
                out.append('</tbody></table>')
            continue
        if line.startswith('>'):
            flush(); close_list()
            out.append(f'<blockquote><p>{inline(line[1:].strip())}</p></blockquote>')
            i += 1; continue
        m = re.match(r'^[-*+]\s+(.*)', line)
        if m:
            flush()
            if in_list != 'ul': close_list(); out.append('<ul>'); in_list = 'ul'
            out.append(f'<li>{inline(m.group(1))}</li>'); i += 1; continue
        m = re.match(r'^\d+\.\s+(.*)', line)
        if m:
            flush()
            if in_list != 'ol': close_list(); out.append('<ol>'); in_list = 'ol'
            out.append(f'<li>{inline(m.group(1))}</li>'); i += 1; continue
        if line.strip() == '':
            flush(); close_list(); i += 1; continue
        close_list(); para.append(line); i += 1

    flush(); close_list()
    return '\n'.join(out)


# ── HTML assembly ────────────────────────────────────────────────────────────

def file_label(fname):
    name = fname.replace('.md', '')
    if name.startswith('SCREEN-'): return 'Screen: ' + name[7:]
    if name.startswith('FEATURE-'): return 'Feature: ' + name[8:]
    labels = {
        'METADATA': 'Metadata', 'README': 'Overview', 'INTENT': 'Intent',
        'ARCHITECTURE': 'Architecture', 'DATABASE': 'Database', 'UI': 'UI Standards',
    }
    return labels.get(name, name.replace('_', ' ').replace('-', ' ').title())


def build_sidebar(projects):
    s = [
        '<nav class="gem-sidebar-panel">',
        '<div class="gem-toc-title">Specifications</div>',
        '<div class="gem-toc-subtitle">Spec-Driven Build System</div>',
        '<div class="gem-toc-section">Documentation</div>',
        '<a href="#workflow">Workflow</a>',
        '<a href="#setup">Project Setup</a>',
    ]
    if projects:
        s.append('<div class="gem-toc-section">Projects</div>')
        for slug, display, status, desc, _ in projects:
            s.append(f'<a href="../{html_lib.escape(slug)}/index.html">{html_lib.escape(display)}</a>')
    s.append('</nav>')
    return '\n'.join(s)


def build_project_card(slug, display, status, desc, md_files):
    color = STATUS_COLORS.get(status, '#94a3b8')
    badge = f'<span class="spec-status" style="background:{color}">{html_lib.escape(status)}</span>' if status else ''
    desc_html = f'<p class="spec-card-desc">{html_lib.escape(desc)}</p>' if desc else ''
    pills = ' '.join(
        f'<span class="spec-file-pill">{html_lib.escape(file_label(f))}</span>'
        for f in md_files
    )
    return f'''<a href="../{html_lib.escape(slug)}/index.html" class="spec-project-card">
<div class="spec-card-header"><span class="spec-card-name">{html_lib.escape(display)}</span>{badge}</div>
{desc_html}
<div class="spec-file-list">{pills}</div>
</a>'''


def build_page(sidebar, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Specifications — Documentation</title>
<link rel="stylesheet" type="text/css" href="styles/gem.css">
<style>
.spec-intro {{ color: var(--c-h3); font-size: 15px; margin: 0 0 24px 0; line-height: 1.6; }}
.spec-projects {{ display: grid; grid-template-columns: 1fr; gap: 16px; margin: 16px 0 28px; }}
.spec-project-card {{
  display: block; background: #fff; border: 1px solid var(--c-td-border);
  border-radius: 8px; padding: 18px 20px; text-decoration: none;
  transition: border-color .15s, box-shadow .15s; cursor: pointer;
}}
.spec-project-card:hover {{
  border-color: var(--c-accent);
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
}}
.spec-card-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }}
.spec-card-name {{ font-size: 17px; font-weight: 700; color: var(--c-h1); }}
.spec-status {{
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  font-size: 10px; font-weight: 600; color: #fff;
}}
.spec-card-desc {{ font-size: 13px; color: var(--c-h3); margin: 0 0 8px; line-height: 1.5; }}
.spec-file-list {{ display: flex; flex-wrap: wrap; gap: 5px; }}
.spec-file-pill {{
  background: var(--c-code-bg); color: var(--c-code-text);
  font-size: 11px; padding: 2px 8px; border-radius: 10px;
  border: 1px solid var(--c-td-border);
}}
.spec-divider {{
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; color: var(--c-h3); margin: 28px 0 10px;
  padding-bottom: 4px; border-bottom: 1px solid var(--c-td-border);
}}
</style>
</head>
<body class="gem-page">
{sidebar}
<main class="gem-content-panel">
{body}
<div class="gem-page-footer">Copyright &copy; 2026 Ed Barlow / SQL Technologies. All rights reserved.</div>
</main>
</body>
</html>"""


def main():
    DOC_DIR.mkdir(exist_ok=True)
    projects = discover_projects()
    body = []

    # Intro
    body.append('<h1>Specifications</h1>')
    body.append('<p class="spec-intro">Write concise markdown specs. '
                'Expand them with AI. Build the application in one shot. '
                'Iterate by editing specs and rebuilding.</p>')

    # Workflow
    process_path = DOC_DIR / "SPECIFICATION-PROCESS.md"
    if process_path.exists():
        body.append(f'<section id="workflow">\n{md_to_html(process_path.read_text(encoding="utf-8", errors="replace"))}\n</section>')
        print(f"  [ok] SPECIFICATION-PROCESS.md")

    # Setup
    setup_path = DOC_DIR / "PROJECT-SETUP.md"
    if setup_path.exists():
        body.append(f'<section id="setup">\n{md_to_html(setup_path.read_text(encoding="utf-8", errors="replace"))}\n</section>')
        print(f"  [ok] PROJECT-SETUP.md")

    # Projects
    if projects:
        body.append('<div class="spec-divider">Projects</div>')
        body.append('<div class="spec-projects">')
        for slug, display, status, desc, md_files in projects:
            body.append(build_project_card(slug, display, status, desc, md_files))
            print(f"  [ok] {slug}/ ({len(md_files)} files)")
        body.append('</div>')

    sidebar = build_sidebar(projects)
    out_path = DOC_DIR / "index.html"
    out_path.write_text(build_page(sidebar, '\n\n'.join(body)), encoding='utf-8')
    print(f"\nWrote {out_path}  ({out_path.stat().st_size // 1024} KB)")


if __name__ == '__main__':
    main()
