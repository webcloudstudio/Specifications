#!/usr/bin/env python3
"""
Build doc/index.html from the Specifications markdown documents.

Reads CLAUDE_RULES.md and DOCUMENTATION_BRANDING.md from the project root,
converts each to HTML sections, and renders them in the GEM single-page layout.
"""
import html as html_lib
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DOC_DIR = PROJECT_DIR / "doc"

# Documents to include, in order: (anchor_id, filename, sidebar_label)
DOCUMENTS = [
    ("claude-rules",       "GLOBAL_RULES/CLAUDE_RULES.md",           "Claude Rules"),
    ("doc-branding",       "GLOBAL_RULES/DOCUMENTATION_BRANDING.md", "Documentation Branding"),
]


# ── Markdown → HTML converter ────────────────────────────────────────────────

def apply_inline(text: str) -> str:
    """Apply inline markdown: bold, italic, inline code, links."""
    # Inline code (protect first — no further substitution inside)
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for part in parts:
        if part.startswith('`') and part.endswith('`') and len(part) > 2:
            out.append(f'<code>{html_lib.escape(part[1:-1])}</code>')
        else:
            # Bold
            part = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', part)
            part = re.sub(r'__(.+?)__', r'<strong>\1</strong>', part)
            # Italic (only when not inside word boundary to avoid sp__who)
            part = re.sub(r'(?<!\w)\*([^*\n]+?)\*(?!\w)', r'<em>\1</em>', part)
            # Links
            part = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                          lambda m: f'<a href="{html_lib.escape(m.group(2))}">{m.group(1)}</a>',
                          part)
            out.append(part)
    return ''.join(out)


def md_to_html(text: str) -> str:
    """Convert Markdown text to an HTML fragment."""
    # Strip CLAUDE_RULES_START / CLAUDE_RULES_END markers (both HTML comment and heading forms)
    text = re.sub(r'<!--\s*CLAUDE_RULES_(?:START|END)[^>]*-->', '', text)
    text = re.sub(r'^#\s+CLAUDE_RULES_(?:START|END)\s*$', '', text, flags=re.MULTILINE)

    lines = text.splitlines()
    out: list[str] = []
    i = 0
    list_stack: list[str] = []
    para: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            content = ' '.join(para).strip()
            if content:
                out.append(f'<p>{apply_inline(content)}</p>')
            para = []

    def close_lists() -> None:
        while list_stack:
            out.append(f'</{list_stack.pop()}>')

    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.startswith('```'):
            flush_para()
            close_lists()
            i += 1
            code_lines: list[str] = []
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            out.append(f'<pre><code>{html_lib.escape(chr(10).join(code_lines))}</code></pre>')
            continue

        # ATX heading
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            flush_para()
            close_lists()
            level = len(m.group(1))
            raw = m.group(2).strip()
            slug = re.sub(r'[^\w-]', '-', raw.lower()).strip('-')
            out.append(f'<h{level} id="{html_lib.escape(slug)}">{apply_inline(raw)}</h{level}>')
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^(?:---+|\*\*\*+|___+)\s*$', line):
            flush_para()
            close_lists()
            out.append('<hr>')
            i += 1
            continue

        # Table (line starts with |)
        if line.lstrip().startswith('|') and '|' in line:
            flush_para()
            close_lists()
            table_lines: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                table_lines.append(lines[i])
                i += 1

            def parse_cells(row: str) -> list[str]:
                return [c.strip() for c in row.strip().strip('|').split('|')]

            if len(table_lines) >= 2:
                headers = parse_cells(table_lines[0])
                # table_lines[1] is the separator row (---)
                body_rows = [r for r in table_lines[2:] if not re.match(r'^[\s|:-]+$', r)]
                out.append('<table>')
                out.append('<thead><tr>')
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

        # Blockquote
        if line.startswith('>'):
            flush_para()
            close_lists()
            content = apply_inline(line[1:].strip())
            out.append(f'<blockquote><p>{content}</p></blockquote>')
            i += 1
            continue

        # Unordered list
        m = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if m:
            flush_para()
            depth = len(m.group(1)) // 2
            while len(list_stack) > depth + 1:
                out.append(f'</{list_stack.pop()}>')
            if len(list_stack) <= depth:
                out.append('<ul>')
                list_stack.append('ul')
            out.append(f'<li>{apply_inline(m.group(2))}</li>')
            i += 1
            continue

        # Ordered list
        m = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if m:
            flush_para()
            depth = len(m.group(1)) // 2
            while len(list_stack) > depth + 1:
                out.append(f'</{list_stack.pop()}>')
            if len(list_stack) <= depth:
                out.append('<ol>')
                list_stack.append('ol')
            out.append(f'<li>{apply_inline(m.group(2))}</li>')
            i += 1
            continue

        # Blank line
        if line.strip() == '':
            flush_para()
            close_lists()
            i += 1
            continue

        # Regular paragraph text — close lists first
        close_lists()
        para.append(line)
        i += 1

    flush_para()
    close_lists()
    return '\n'.join(out)


# ── HTML template ─────────────────────────────────────────────────────────────

def build_sidebar(doc_items: list[tuple[str, str]]) -> str:
    parts = [
        '<nav class="gem-sidebar-panel">',
        '<div class="gem-toc-title">Specifications</div>',
        '<div class="gem-toc-subtitle">Platform Standards &amp; Rules</div>',
        '<div class="gem-toc-section">Documents</div>',
    ]
    for anchor, label in doc_items:
        parts.append(f'<a href="#{html_lib.escape(anchor)}">{html_lib.escape(label)}</a>')
    parts.append('</nav>')
    return '\n'.join(parts)


def build_html(sidebar: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Specifications — Platform Standards &amp; Rules</title>
<link rel="stylesheet" type="text/css" href="styles/gem.css">
</head>
<body class="gem-page">
{sidebar}
<main class="gem-content-panel">
{body}
<div class="gem-page-footer">Copyright &copy; 2026 Ed Barlow / SQL Technologies. All rights reserved.</div>
</main>
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    DOC_DIR.mkdir(exist_ok=True)

    body_parts: list[str] = []
    sidebar_items: list[tuple[str, str]] = []

    for anchor, filename, label in DOCUMENTS:
        path = PROJECT_DIR / filename
        if not path.exists():
            print(f"  [skip] {filename} not found", file=sys.stderr)
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        fragment = md_to_html(text)
        body_parts.append(
            f'<section id="{html_lib.escape(anchor)}">\n{fragment}\n</section>'
        )
        sidebar_items.append((anchor, label))
        print(f"  [ok] {filename}")

    if not body_parts:
        print("No documents found — nothing to write.", file=sys.stderr)
        sys.exit(1)

    sidebar = build_sidebar(sidebar_items)
    out_path = DOC_DIR / "index.html"
    out_path.write_text(build_html(sidebar, '\n\n'.join(body_parts)), encoding='utf-8')
    print(f"\nWrote {out_path}  ({out_path.stat().st_size // 1024} KB)")


if __name__ == '__main__':
    main()
