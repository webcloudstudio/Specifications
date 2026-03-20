#!/usr/bin/env python3
"""
Build doc/index.html — a single-page documentation site for the Specifications repo.

Reads doc/SPECIFICATION-PROCESS.md and doc/PROJECT-SETUP.md, discovers project spec
directories, and produces a clean sidebar+content page using the existing theme CSS.
"""
import html as html_lib
import os
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DOC_DIR = PROJECT_DIR / "doc"

SKIP_DIRS = {
    'archive', 'bin', 'doc', 'GLOBAL_RULES', 'logs', 'venv',
    '__pycache__', '.git',
}


def discover_projects():
    """Find directories with METADATA.md. Skip Proposed.* and archive dirs."""
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
        display = entry.name
        status = ""
        for line in meta.read_text(encoding='utf-8', errors='replace').splitlines():
            if line.startswith('display_name:'):
                display = line.split(':', 1)[1].strip()
            if line.startswith('status:'):
                status = line.split(':', 1)[1].strip()
        md_files = sorted(
            [f.name for f in entry.iterdir()
             if f.suffix == '.md'
             and not f.name.startswith('PROPOSED')
             and not f.name.startswith('UNUSED')],
            key=lambda n: (0 if n == 'METADATA.md' else 1, n)
        )
        if md_files:
            projects.append((entry.name, display, status, md_files))
    return projects


# ── Markdown → HTML ──────────────────────────────────────────────────────────

def inline(text):
    """Bold, italic, inline code, links."""
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
    """Minimal markdown to HTML. Handles headings, tables, code blocks, lists, paragraphs."""
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

        # Code block
        if line.startswith('```'):
            flush(); close_list()
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i]); i += 1
            i += 1
            out.append(f'<pre><code>{html_lib.escape(chr(10).join(code))}</code></pre>')
            continue

        # Heading
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            flush(); close_list()
            lvl = len(m.group(1))
            raw = m.group(2).strip()
            out.append(f'<h{lvl}>{inline(raw)}</h{lvl}>')
            i += 1; continue

        # HR
        if re.match(r'^(?:---+|\*\*\*+|___+)\s*$', line):
            flush(); close_list()
            out.append('<hr>')
            i += 1; continue

        # Table
        if line.lstrip().startswith('|') and '|' in line:
            flush(); close_list()
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                rows.append(lines[i]); i += 1
            if len(rows) >= 2:
                cells = lambda r: [c.strip() for c in r.strip().strip('|').split('|')]
                hdrs = cells(rows[0])
                out.append('<table><thead><tr>')
                for h in hdrs:
                    out.append(f'<th>{inline(h)}</th>')
                out.append('</tr></thead><tbody>')
                for row in rows[2:]:
                    if re.match(r'^[\s|:-]+$', row):
                        continue
                    out.append('<tr>')
                    for c in cells(row):
                        out.append(f'<td>{inline(c)}</td>')
                    out.append('</tr>')
                out.append('</tbody></table>')
            continue

        # Blockquote
        if line.startswith('>'):
            flush(); close_list()
            out.append(f'<blockquote><p>{inline(line[1:].strip())}</p></blockquote>')
            i += 1; continue

        # Unordered list
        m = re.match(r'^[-*+]\s+(.*)', line)
        if m:
            flush()
            if in_list != 'ul':
                close_list()
                out.append('<ul>'); in_list = 'ul'
            out.append(f'<li>{inline(m.group(1))}</li>')
            i += 1; continue

        # Ordered list
        m = re.match(r'^\d+\.\s+(.*)', line)
        if m:
            flush()
            if in_list != 'ol':
                close_list()
                out.append('<ol>'); in_list = 'ol'
            out.append(f'<li>{inline(m.group(1))}</li>')
            i += 1; continue

        # Blank
        if line.strip() == '':
            flush(); close_list()
            i += 1; continue

        # Paragraph text
        close_list()
        para.append(line)
        i += 1

    flush(); close_list()
    return '\n'.join(out)


# ── HTML assembly ────────────────────────────────────────────────────────────

STATUS_COLORS = {
    'IDEA': '#94a3b8', 'PROTOTYPE': '#fdab3d', 'ACTIVE': '#0073ea',
    'PRODUCTION': '#00c875', 'ARCHIVED': '#4a5568',
}


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
        for slug, display, status, _ in projects:
            label = f"{display} ({slug})" if slug.lower() != display.lower() else display
            s.append(f'<a href="#project-{html_lib.escape(slug)}">{html_lib.escape(label)}</a>')
    s.append('</nav>')
    return '\n'.join(s)


def file_label(fname):
    """SCREEN-Dashboard.md → Screen: Dashboard, etc."""
    name = fname.replace('.md', '')
    if name.startswith('SCREEN-'):
        return 'Screen: ' + name[7:]
    if name.startswith('FEATURE-'):
        return 'Feature: ' + name[8:]
    labels = {
        'METADATA': 'Metadata', 'README': 'Overview', 'INTENT': 'Intent',
        'ARCHITECTURE': 'Architecture', 'DATABASE': 'Database', 'UI': 'UI Standards',
    }
    if name in labels:
        return labels[name]
    # Clean up underscores/hyphens for display
    return name.replace('_', ' ').replace('-', ' ').title()


def build_project_section(slug, display, status, md_files):
    label = f"{display} ({slug})" if slug.lower() != display.lower() else display
    color = STATUS_COLORS.get(status, '#94a3b8')
    badge = f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;margin-left:8px">{html_lib.escape(status)}</span>' if status else ''

    parts = [f'<section id="project-{html_lib.escape(slug)}">']
    parts.append(f'<h2>{html_lib.escape(label)}{badge}</h2>')

    # Read short_description from METADATA
    meta_path = PROJECT_DIR / slug / "METADATA.md"
    if meta_path.exists():
        for line in meta_path.read_text(encoding='utf-8', errors='replace').splitlines():
            if line.startswith('short_description:'):
                desc = line.split(':', 1)[1].strip()
                if desc:
                    parts.append(f'<p>{html_lib.escape(desc)}</p>')
                break

    # File list as compact pills
    pills = []
    for fname in md_files:
        pills.append(f'<span class="spec-file-pill">{html_lib.escape(file_label(fname))}</span>')
    parts.append(f'<div class="spec-file-list">{" ".join(pills)}</div>')
    parts.append('</section>')
    return '\n'.join(parts)


def build_page(sidebar, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Specifications</title>
<link rel="stylesheet" type="text/css" href="styles/gem.css">
<style>
.spec-file-list {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 16px 0; }}
.spec-file-pill {{
  background: var(--c-code-bg); color: var(--c-code-text);
  font-size: 12px; padding: 3px 10px; border-radius: 12px;
  border: 1px solid var(--c-td-border); font-family: 'Segoe UI', Arial, sans-serif;
}}
.spec-intro {{ color: var(--c-h3); font-size: 15px; margin: 0 0 20px 0; line-height: 1.6; }}
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

    # ── Intro ──
    body.append('<h1>Specifications</h1>')
    body.append('<p class="spec-intro">Write concise markdown specs. '
                'Expand them with AI. Build the application in one shot. '
                'Iterate by editing specs and rebuilding.</p>')

    # ── Workflow ──
    process_path = DOC_DIR / "SPECIFICATION-PROCESS.md"
    if process_path.exists():
        text = process_path.read_text(encoding='utf-8', errors='replace')
        body.append(f'<section id="workflow">\n{md_to_html(text)}\n</section>')
        print(f"  [ok] SPECIFICATION-PROCESS.md")

    # ── Setup ──
    setup_path = DOC_DIR / "PROJECT-SETUP.md"
    if setup_path.exists():
        text = setup_path.read_text(encoding='utf-8', errors='replace')
        body.append(f'<section id="setup">\n{md_to_html(text)}\n</section>')
        print(f"  [ok] PROJECT-SETUP.md")

    # ── Projects ──
    for slug, display, status, md_files in projects:
        body.append(build_project_section(slug, display, status, md_files))
        print(f"  [ok] {slug}/ ({len(md_files)} files)")

    sidebar = build_sidebar(projects)
    out_path = DOC_DIR / "index.html"
    out_path.write_text(build_page(sidebar, '\n\n'.join(body)), encoding='utf-8')
    print(f"\nWrote {out_path}  ({out_path.stat().st_size // 1024} KB)")


if __name__ == '__main__':
    main()
