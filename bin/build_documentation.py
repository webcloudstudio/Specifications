#!/usr/bin/env python3
"""
Build doc/index.html from Specifications repository content.

Auto-discovers:
  - Foundation docs from GLOBAL_RULES/ (CLAUDE_RULES.md, CONVERT.md, DOCUMENTATION_BRANDING.md)
  - Process docs from doc/ (*.md files)
  - Project spec directories (any dir with METADATA.md)

Renders in the GEM single-page layout with hero cards for Foundation rules.
Theme controlled by doc/styles/themes/ — see build_documentation.sh.
"""
import html as html_lib
import os
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DOC_DIR = PROJECT_DIR / "doc"

# ── Foundation docs (big hero cards at the top) ──────────────────────────────
FOUNDATION_DOCS = [
    ("claude-rules",  "GLOBAL_RULES/CLAUDE_RULES.md",            "Claude Rules",
     "Agent behavior contract — injected into every project's AGENTS.md"),
    ("convert-rules", "GLOBAL_RULES/CONVERT.md",                  "Conversion Rules",
     "How concise specs expand into detailed implementation-ready specifications"),
    ("doc-branding",  "GLOBAL_RULES/DOCUMENTATION_BRANDING.md",   "Documentation Branding",
     "Theme system, color families, typography, and page structure standards"),
]

# ── Process docs from doc/ ───────────────────────────────────────────────────
PROCESS_DOCS = [
    ("spec-process",  "doc/SPECIFICATION-PROCESS.md",  "Specification Process",
     "Pipeline, state machine, build tags, git strategy, and file contract"),
    ("project-setup", "doc/PROJECT-SETUP.md",          "Project Setup Guide",
     "Required files, templates, and conventions for new spec directories"),
]


# ── Auto-discover project spec directories ───────────────────────────────────
def discover_projects():
    """Find directories with METADATA.md, return list of (slug, display_name, file_list)."""
    skip = {'archive', 'bin', 'doc', 'GLOBAL_RULES', 'logs', 'venv',
            '__pycache__', '.git', 'Proposed.AlexaPrototypeOne'}
    projects = []
    for entry in sorted(PROJECT_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith('.') or entry.name in skip:
            continue
        meta = entry / "METADATA.md"
        if not meta.exists():
            continue
        # Parse display_name from METADATA.md
        display = entry.name
        for line in meta.read_text(encoding='utf-8', errors='replace').splitlines():
            if line.startswith('display_name:'):
                display = line.split(':', 1)[1].strip()
                break
        # Collect .md files (sorted, METADATA first, then alpha)
        md_files = sorted(
            [f.name for f in entry.iterdir() if f.suffix == '.md'],
            key=lambda n: (0 if n == 'METADATA.md' else 1, n)
        )
        if md_files:
            projects.append((entry.name, display, md_files))
    return projects


# ── Markdown → HTML converter ────────────────────────────────────────────────

def apply_inline(text):
    """Apply inline markdown: bold, italic, inline code, links."""
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for part in parts:
        if part.startswith('`') and part.endswith('`') and len(part) > 2:
            out.append(f'<code>{html_lib.escape(part[1:-1])}</code>')
        else:
            part = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', part)
            part = re.sub(r'__(.+?)__', r'<strong>\1</strong>', part)
            part = re.sub(r'(?<!\w)\*([^*\n]+?)\*(?!\w)', r'<em>\1</em>', part)
            part = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                          lambda m: f'<a href="{html_lib.escape(m.group(2))}">{m.group(1)}</a>',
                          part)
            out.append(part)
    return ''.join(out)


def md_to_html(text):
    """Convert Markdown text to an HTML fragment."""
    text = re.sub(r'<!--\s*CLAUDE_RULES_(?:START|END)[^>]*-->', '', text)
    text = re.sub(r'^#\s+CLAUDE_RULES_(?:START|END)\s*$', '', text, flags=re.MULTILINE)

    lines = text.splitlines()
    out = []
    i = 0
    list_stack = []
    para = []

    def flush_para():
        nonlocal para
        if para:
            content = ' '.join(para).strip()
            if content:
                out.append(f'<p>{apply_inline(content)}</p>')
            para = []

    def close_lists():
        while list_stack:
            out.append(f'</{list_stack.pop()}>')

    while i < len(lines):
        line = lines[i]

        if line.startswith('```'):
            flush_para(); close_lists()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1
            out.append(f'<pre><code>{html_lib.escape(chr(10).join(code_lines))}</code></pre>')
            continue

        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            flush_para(); close_lists()
            level = len(m.group(1))
            raw = m.group(2).strip()
            slug = re.sub(r'[^\w-]', '-', raw.lower()).strip('-')
            out.append(f'<h{level} id="{html_lib.escape(slug)}">{apply_inline(raw)}</h{level}>')
            i += 1; continue

        if re.match(r'^(?:---+|\*\*\*+|___+)\s*$', line):
            flush_para(); close_lists()
            out.append('<hr>')
            i += 1; continue

        if line.lstrip().startswith('|') and '|' in line:
            flush_para(); close_lists()
            table_lines = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                table_lines.append(lines[i]); i += 1
            def parse_cells(row):
                return [c.strip() for c in row.strip().strip('|').split('|')]
            if len(table_lines) >= 2:
                headers = parse_cells(table_lines[0])
                body_rows = [r for r in table_lines[2:] if not re.match(r'^[\s|:-]+$', r)]
                out.append('<table><thead><tr>')
                for h in headers:
                    out.append(f'<th>{apply_inline(h)}</th>')
                out.append('</tr></thead><tbody>')
                for row in body_rows:
                    out.append('<tr>')
                    for cell in parse_cells(row):
                        out.append(f'<td>{apply_inline(cell)}</td>')
                    out.append('</tr>')
                out.append('</tbody></table>')
            continue

        if line.startswith('>'):
            flush_para(); close_lists()
            content = apply_inline(line[1:].strip())
            out.append(f'<blockquote><p>{content}</p></blockquote>')
            i += 1; continue

        m = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if m:
            flush_para()
            depth = len(m.group(1)) // 2
            while len(list_stack) > depth + 1:
                out.append(f'</{list_stack.pop()}>')
            if len(list_stack) <= depth:
                out.append('<ul>'); list_stack.append('ul')
            out.append(f'<li>{apply_inline(m.group(2))}</li>')
            i += 1; continue

        m = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if m:
            flush_para()
            depth = len(m.group(1)) // 2
            while len(list_stack) > depth + 1:
                out.append(f'</{list_stack.pop()}>')
            if len(list_stack) <= depth:
                out.append('<ol>'); list_stack.append('ol')
            out.append(f'<li>{apply_inline(m.group(2))}</li>')
            i += 1; continue

        if line.strip() == '':
            flush_para(); close_lists()
            i += 1; continue

        close_lists()
        para.append(line)
        i += 1

    flush_para(); close_lists()
    return '\n'.join(out)


# ── HTML builder ─────────────────────────────────────────────────────────────

def build_sidebar(foundation, process, projects):
    parts = [
        '<nav class="gem-sidebar-panel">',
        '<div class="gem-toc-title">Specifications</div>',
        '<div class="gem-toc-subtitle">Platform Standards &amp; Project Specs</div>',
        '',
        '<div class="gem-toc-section">Foundation</div>',
    ]
    for anchor, _, label, _ in foundation:
        parts.append(f'<a href="#{html_lib.escape(anchor)}">{html_lib.escape(label)}</a>')

    parts.append('<div class="gem-toc-section">Process</div>')
    for anchor, _, label, _ in process:
        parts.append(f'<a href="#{html_lib.escape(anchor)}">{html_lib.escape(label)}</a>')

    for slug, display, md_files in projects:
        # Use slug if display_name duplicates exist, or always show slug for clarity
        sidebar_title = f"{display} ({slug})" if slug != display else display
        parts.append(f'<div class="gem-toc-section">{html_lib.escape(sidebar_title)}</div>')
        for fname in md_files:
            anchor = f"{slug}--{fname.replace('.md', '').lower()}"
            sidebar_label = fname.replace('.md', '').replace('-', ' ').replace('_', ' ')
            if sidebar_label == 'METADATA':
                sidebar_label = 'Metadata'
            elif sidebar_label == 'README':
                sidebar_label = 'Overview'
            elif sidebar_label == 'INTENT':
                sidebar_label = 'Intent'
            elif sidebar_label.startswith('SCREEN '):
                sidebar_label = sidebar_label.replace('SCREEN ', 'Screen: ')
            elif sidebar_label.startswith('FEATURE '):
                sidebar_label = sidebar_label.replace('FEATURE ', 'Feature: ')
            parts.append(f'<a href="#{html_lib.escape(anchor)}">{html_lib.escape(sidebar_label)}</a>')

    parts.append('</nav>')
    return '\n'.join(parts)


def build_hero_cards(items, section_id):
    """Build big accent-colored hero cards for foundation/process docs."""
    cards = []
    for anchor, _, label, desc in items:
        cards.append(f'''<a href="#{html_lib.escape(anchor)}" class="spec-hero-card">
<div class="spec-hero-label">{html_lib.escape(label)}</div>
<div class="spec-hero-desc">{html_lib.escape(desc)}</div>
</a>''')
    return f'<div class="spec-hero-grid" id="{section_id}">{"".join(cards)}</div>'


def build_project_cards(projects):
    """Build smaller project cards."""
    cards = []
    for slug, display, md_files in projects:
        anchor = f"{slug}--{md_files[0].replace('.md', '').lower()}"
        count = len(md_files)
        label = f"{display} ({slug})" if slug != display else display
        cards.append(f'''<a href="#{html_lib.escape(anchor)}" class="spec-project-card">
<div class="spec-project-label">{html_lib.escape(label)}</div>
<div class="spec-project-desc">{count} specification files</div>
</a>''')
    return f'<div class="spec-project-grid">{"".join(cards)}</div>'


EXTRA_CSS = """
<style>
/* ── Hero cards (Foundation / Process) ───────────────── */
.spec-hero-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin: 16px 0 32px 0;
}
.spec-hero-card {
  display: block;
  background: var(--c-side-bg);
  border: 2px solid var(--c-accent);
  border-radius: 8px;
  padding: 24px 20px;
  text-decoration: none !important;
  transition: background 0.15s, transform 0.1s;
  cursor: pointer;
}
.spec-hero-card:hover {
  background: var(--c-topbar-bg);
  transform: translateY(-2px);
}
.spec-hero-label {
  color: var(--c-accent);
  font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif;
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 8px;
}
.spec-hero-desc {
  color: var(--c-side-link);
  font-size: 13.5px;
  line-height: 1.5;
}

/* ── Section headers on the landing page ─────────────── */
.spec-section-header {
  font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--c-side-section);
  margin: 32px 0 8px 0;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--c-td-border);
}

/* ── Project cards (smaller) ─────────────────────────── */
.spec-project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
  margin: 12px 0 32px 0;
}
.spec-project-card {
  display: block;
  background: #FFFFFF;
  border: 1px solid var(--c-td-border);
  border-radius: 6px;
  padding: 16px;
  text-decoration: none !important;
  transition: border-color 0.15s, background 0.1s;
  cursor: pointer;
}
.spec-project-card:hover {
  border-color: var(--c-accent);
  background: var(--c-tr-hover);
}
.spec-project-label {
  color: var(--c-h1);
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
}
.spec-project-desc {
  color: var(--c-h3);
  font-size: 12px;
}

/* ── Landing intro ───────────────────────────────────── */
.spec-landing-intro {
  font-size: 15px;
  color: var(--c-h3);
  margin: 0 0 24px 0;
  line-height: 1.6;
}
</style>
"""


def build_html(sidebar, body, landing):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Specifications — Platform Standards &amp; Project Specs</title>
<link rel="stylesheet" type="text/css" href="styles/gem.css">
{EXTRA_CSS}
</head>
<body class="gem-page">
{sidebar}
<main class="gem-content-panel">
{landing}
{body}
<div class="gem-page-footer">Copyright &copy; 2026 Ed Barlow / SQL Technologies. All rights reserved.</div>
</main>
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    DOC_DIR.mkdir(exist_ok=True)

    projects = discover_projects()
    body_parts = []

    # ── Landing page (hero cards) ──
    landing_parts = [
        '<div id="landing">',
        '<h1>Specifications</h1>',
        '<p class="spec-landing-intro">Platform standards, specification methodology, '
        'and project specs. Foundation rules govern all projects. '
        'Process docs describe the spec-driven build system.</p>',
        '<div class="spec-section-header">Foundation</div>',
        build_hero_cards(FOUNDATION_DOCS, 'foundation-cards'),
        '<div class="spec-section-header">Process</div>',
        build_hero_cards(PROCESS_DOCS, 'process-cards'),
    ]
    if projects:
        landing_parts.append('<div class="spec-section-header">Project Specifications</div>')
        landing_parts.append(build_project_cards(projects))
    landing_parts.append('</div>')
    landing = '\n'.join(landing_parts)

    # ── Foundation docs ──
    for anchor, filename, label, _ in FOUNDATION_DOCS:
        path = PROJECT_DIR / filename
        if not path.exists():
            print(f"  [skip] {filename} not found", file=sys.stderr)
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        fragment = md_to_html(text)
        body_parts.append(f'<section id="{html_lib.escape(anchor)}">\n{fragment}\n</section>')
        print(f"  [ok] {filename}")

    # ── Process docs ──
    for anchor, filename, label, _ in PROCESS_DOCS:
        path = PROJECT_DIR / filename
        if not path.exists():
            print(f"  [skip] {filename} not found", file=sys.stderr)
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        fragment = md_to_html(text)
        body_parts.append(f'<section id="{html_lib.escape(anchor)}">\n{fragment}\n</section>')
        print(f"  [ok] {filename}")

    # ── Project spec docs ──
    for slug, display, md_files in projects:
        for fname in md_files:
            anchor = f"{slug}--{fname.replace('.md', '').lower()}"
            path = PROJECT_DIR / slug / fname
            if not path.exists():
                continue
            text = path.read_text(encoding='utf-8', errors='replace')
            fragment = md_to_html(text)
            body_parts.append(f'<section id="{html_lib.escape(anchor)}">\n{fragment}\n</section>')
        print(f"  [ok] {slug}/ ({len(md_files)} files)")

    if not body_parts:
        print("No documents found — nothing to write.", file=sys.stderr)
        sys.exit(1)

    sidebar = build_sidebar(FOUNDATION_DOCS, PROCESS_DOCS, projects)
    out_path = DOC_DIR / "index.html"
    out_path.write_text(
        build_html(sidebar, '\n\n'.join(body_parts), landing),
        encoding='utf-8'
    )
    print(f"\nWrote {out_path}  ({out_path.stat().st_size // 1024} KB)")


if __name__ == '__main__':
    main()
