#!/usr/bin/env python3
# CommandCenter Operation
# Name: Build Project Docs
# Category: maintenance
"""
Assemble docs/index.html from DOC-*.md content files and bin/ script headers.
Called by document.sh after AI content generation is complete.

Reads DOC-*.md from the target project's docs/ directory, discovers bin/ scripts
with CommandCenter headers, and produces a single-page documentation app matching
the Prototyper docs look and feel (sidebar, nav sections, man-pages, marked.js).
"""
import argparse
import html as _html
import json
import re
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent


# ── Metadata ────────────────────────────────────────────────────────────────

def read_meta(meta_path):
    """Parse METADATA.md key:value pairs."""
    fields = {}
    if meta_path.exists():
        for line in meta_path.read_text(encoding='utf-8').splitlines():
            if ':' in line and not line.startswith('#'):
                k, v = line.split(':', 1)
                fields[k.strip()] = v.strip()
    return fields


# ── Guide discovery ─────────────────────────────────────────────────────────

GUIDE_ORDER = ['OVERVIEW', 'SCREENS', 'FEATURES', 'ARCHITECTURE', 'DATABASE', 'FLOWS']

GUIDE_TITLES = {
    'OVERVIEW': 'Overview',
    'SCREENS': 'Screens',
    'FEATURES': 'Features',
    'ARCHITECTURE': 'Architecture',
    'DATABASE': 'Database',
    'FLOWS': 'Flows',
}

GUIDE_SECTIONS = {
    'OVERVIEW': 'OVERVIEW',
    'SCREENS': 'SCREENS',
    'FEATURES': 'FEATURES',
    'ARCHITECTURE': 'SYSTEM',
    'DATABASE': 'SYSTEM',
    'FLOWS': 'SYSTEM',
}


def discover_guides(docs_dir):
    """Read DOC-*.md files, return ordered list of {key, title, content}."""
    found = {}
    for f in docs_dir.glob('DOC-*.md'):
        key = f.stem[4:]  # Strip DOC- prefix
        found[key] = f

    guides = []
    for key in GUIDE_ORDER:
        if key in found:
            title = GUIDE_TITLES.get(key, key.replace('-', ' ').title())
            content = found[key].read_text(encoding='utf-8')
            guides.append({'key': key, 'title': title, 'content': content})

    # Any extra DOC files not in the standard order
    for key, f in sorted(found.items()):
        if key not in GUIDE_ORDER:
            title = GUIDE_TITLES.get(key, key.replace('-', ' ').title())
            content = f.read_text(encoding='utf-8')
            guides.append({'key': key, 'title': title, 'content': content})

    return guides


# ── Script discovery ────────────────────────────────────────────────────────

def _parse_script_sections(details):
    """Parse script header comment text into named sections for man-page rendering."""
    sections = {}
    cur = '_desc'
    buf = []
    for line in details.splitlines():
        s = line.strip()
        if re.match(r'^[A-Z][a-zA-Z ]{1,18}:$', s):
            sections[cur] = '\n'.join(buf).strip()
            cur = s[:-1]
            buf = []
        else:
            buf.append(s)
    sections[cur] = '\n'.join(buf).strip()
    return sections


def discover_scripts(bin_dir):
    """Extract CommandCenter headers from bin/ scripts in the target project."""
    if not bin_dir.exists():
        return []
    scripts = []
    for ext in ('*.sh', '*.py'):
        for path in sorted(bin_dir.glob(ext)):
            text = path.read_text(encoding='utf-8', errors='replace')
            lines = text.splitlines()[:50]
            cc_name = category = desc = ''
            detail_lines = []
            in_header = False
            for i, line in enumerate(lines):
                stripped = line.lstrip('#').strip()
                if 'CommandCenter Operation' in line:
                    in_header = True
                    continue
                if in_header:
                    if line.startswith('#') or line == '':
                        if line.startswith('# Name:'):
                            cc_name = line.split(':', 1)[1].strip()
                        elif line.startswith('# Category:'):
                            category = line.split(':', 1)[1].strip()
                        elif line.startswith('#') and stripped:
                            detail_lines.append(line.lstrip('#'))
                    else:
                        in_header = False
                if line.startswith('"""') and not desc:
                    inline = line.strip('"""').strip()
                    desc = inline if inline else (lines[i + 1].strip() if i + 1 < len(lines) else '')

            if not cc_name and not detail_lines:
                continue  # Not a CommandCenter script

            label = cc_name or path.stem.replace('_', ' ').title()
            if not desc and detail_lines:
                desc = detail_lines[0].strip()
            details = '\n'.join(detail_lines).strip()
            scripts.append({
                'file': path.name,
                'label': label,
                'desc': desc,
                'category': category,
                'details': details,
                'sections': _parse_script_sections(details),
            })
    return scripts


# ── Sub-item extraction ─────────────────────────────────────────────────────

def extract_sub_items(content):
    """Extract H2 headings from DOC markdown to create sidebar sub-items."""
    items = []
    for m in re.finditer(r'^## (.+)$', content, re.MULTILINE):
        title = m.group(1).strip()
        # Create an anchor-safe id
        anchor = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        items.append({'title': title, 'anchor': anchor})
    return items


# ── HTML generation ─────────────────────────────────────────────────────────

def build_sidebar(metadata, guides, scripts):
    """Generate sidebar HTML."""
    display_name = metadata.get('display_name') or metadata.get('name', 'Project')
    icon = metadata.get('icon', '📋')

    parts = []

    # Sidebar header
    parts.append(f'''  <div class="sidebar-header" onclick="showGuide('OVERVIEW')">
    <span class="sidebar-icon">{_html.escape(icon)}</span>
    <h1>{_html.escape(display_name)}</h1>
  </div>''')

    # Group guides by section
    current_section = None
    for g in guides:
        section = GUIDE_SECTIONS.get(g['key'], 'OTHER')
        if section != current_section:
            if current_section is not None:
                parts.append('  <div class="nav-sep"></div>')
            parts.append(f'  <div class="nav-section">{_html.escape(section)}</div>')
            current_section = section

        key = g['key']
        title = g['title']
        parts.append(
            f'  <a class="sn" data-key="{_html.escape(key)}" '
            f'onclick="showGuide(\'{_html.escape(key)}\')">{_html.escape(title)}</a>'
        )

        # Sub-items from H2 headings (only for SCREENS, FEATURES)
        if key in ('SCREENS', 'FEATURES'):
            sub_items = extract_sub_items(g['content'])
            for item in sub_items:
                parts.append(
                    f'  <a class="sn-sub" data-key="{_html.escape(key)}" '
                    f'onclick="showGuideSection(\'{_html.escape(key)}\', '
                    f'\'{_html.escape(item["anchor"])}\');">'
                    f'{_html.escape(item["title"])}</a>'
                )

    # Operations section
    if scripts:
        parts.append('  <div class="nav-sep"></div>')
        parts.append('  <div class="nav-section">OPERATIONS</div>')
        for s in scripts:
            parts.append(
                f'  <a class="sn" data-script="{_html.escape(s["file"])}" '
                f'onclick="showScript(\'{_html.escape(s["file"])}\')">'
                f'{_html.escape(s["file"])}</a>'
            )

    return '\n'.join(parts)


def build_page(metadata, guides, scripts, spec_name):
    """Assemble the full HTML document."""
    display_name = metadata.get('display_name') or metadata.get('name', 'Project')
    short_desc = metadata.get('short_description', '')
    stack = metadata.get('stack', '')
    status = metadata.get('status', '')
    version = metadata.get('version', '')

    now = datetime.now()
    gen_date = now.strftime('%Y-%m-%d %H:%M')
    gen_version = now.strftime('%Y%m%d') + '.1'

    sidebar_html = build_sidebar(metadata, guides, scripts)

    # Build GUIDES JS object
    guides_js_parts = []
    for g in guides:
        guides_js_parts.append(f'  {json.dumps(g["key"])}: {json.dumps(g["content"])}')
    guides_js = 'const GUIDES = {\n' + ',\n'.join(guides_js_parts) + '\n};'

    # Build SCRIPTS JS object
    scripts_js_parts = []
    for s in scripts:
        scripts_js_parts.append(
            f'  {json.dumps(s["file"])}: {json.dumps({"desc": s["desc"], "sections": s["sections"]})}'
        )
    scripts_js = 'const SCRIPTS = {\n' + ',\n'.join(scripts_js_parts) + '\n};'

    # Home content: project summary with metadata
    home_parts = []
    home_parts.append(f'<h2 style="font-size:22px;font-weight:700;color:var(--c-accent);'
                      f'border-bottom:2px solid var(--c-accent);padding-bottom:5px;margin:0 0 10px;">'
                      f'{_html.escape(display_name)}</h2>')
    if short_desc:
        home_parts.append(f'<p style="font-size:15px;margin:0 0 16px;color:var(--c-text);">'
                          f'{_html.escape(short_desc)}</p>')

    # Metadata badges
    badges = []
    if status:
        badges.append(f'<span class="badge">{_html.escape(status)}</span>')
    if stack:
        for comp in stack.split('/'):
            comp = comp.strip()
            if comp:
                badges.append(f'<span class="badge">{_html.escape(comp)}</span>')
    if version:
        badges.append(f'<span class="badge">v{_html.escape(version)}</span>')
    if badges:
        home_parts.append(f'<div style="margin:0 0 20px;display:flex;gap:6px;flex-wrap:wrap;">'
                          f'{"".join(badges)}</div>')

    # Stats
    screen_count = sum(1 for g in guides if g['key'] == 'SCREENS'
                       for _ in extract_sub_items(g['content']))
    feature_count = sum(1 for g in guides if g['key'] == 'FEATURES'
                        for _ in extract_sub_items(g['content']))
    op_count = len(scripts)

    stats = []
    if screen_count:
        stats.append(f'{screen_count} screen{"s" if screen_count != 1 else ""}')
    if feature_count:
        stats.append(f'{feature_count} feature{"s" if feature_count != 1 else ""}')
    if op_count:
        stats.append(f'{op_count} operation{"s" if op_count != 1 else ""}')
    if stats:
        home_parts.append(f'<p style="font-size:13px;color:var(--c-h3);margin:0 0 20px;">'
                          f'{" · ".join(stats)}</p>')

    # Overview content rendered via marked.js
    home_parts.append('<div id="home-overview" class="md"></div>')

    home_html = '\n'.join(home_parts)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html.escape(display_name)} — Documentation</title>
<link rel="stylesheet" href="styles/spec.css">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{ display: flex; flex-direction: column; height: 100vh; overflow: hidden;
  background: var(--c-bg); color: var(--c-text);
  font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif; font-size: 14px; line-height: 1.65; }}

.layout {{ display: flex; flex: 1; overflow: hidden; }}

.page-header {{ background: var(--c-topbar-bg); border-bottom: 1px solid var(--c-side-border); }}

/* ── Sidebar ── */
.sidebar {{ width: 220px; min-width: 220px; display: flex; flex-direction: column;
  background: var(--c-side-bg); border-right: 1px solid var(--c-side-border);
  overflow-y: auto; flex-shrink: 0; }}

.sidebar-header {{ background: var(--c-topbar-bg); padding: 6px 10px;
  flex-shrink: 0; cursor: pointer; display: flex; align-items: center; gap: 9px; }}
.sidebar-header:hover {{ opacity: .88; }}
.sidebar-icon {{ font-size: 28px; line-height: 1; flex-shrink: 0; }}
.sidebar-header h1 {{ color: #fff; font-size: 14px; font-weight: 700; line-height: 1.25; }}

.nav-section {{ font-size: 9px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; color: var(--c-side-section); padding: 10px 16px 3px; }}
.nav-sep {{ border-top: 1px solid var(--c-side-border); margin: 5px 0; }}

.sn {{ display: block; padding: 3px 16px;
  font-size: 13px; font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif;
  color: #fff; cursor: pointer; border-left: 3px solid transparent;
  text-decoration: none; transition: background .1s, border-color .1s;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.sn:hover {{ background: rgba(255,255,255,.07); border-left-color: var(--c-accent); }}
.sn.active {{ color: #fff; border-left-color: var(--c-accent); background: rgba(44,182,125,.12); }}

.sn-sub {{ display: block; padding: 2px 16px 2px 28px;
  font-size: 11px; font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif;
  color: rgba(255,255,255,.8); cursor: pointer; border-left: 3px solid transparent;
  text-decoration: none; transition: background .1s, border-color .1s, color .1s;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.sn-sub:hover {{ color: #fff; background: rgba(255,255,255,.05); border-left-color: var(--c-accent); }}
.sn-sub.active {{ color: var(--c-accent); border-left-color: var(--c-accent); }}

/* ── Content ── */
main {{ flex: 1; overflow-y: auto; padding: 28px 36px 48px; position: relative; }}
.content-section {{ display: none; max-width: 860px; }}
.content-section.active {{ display: block; }}

/* ── Badges ── */
.badge {{ display: inline-block; font-size: 11px; font-weight: 600;
  padding: 2px 8px; border-radius: 3px;
  background: var(--c-code-bg); color: var(--c-code-text);
  font-family: 'Cascadia Code', Consolas, monospace; }}

/* ── Rendered markdown ── */
.md h1 {{ font-size: 22px; font-weight: 700; color: var(--c-accent);
  border-bottom: 2px solid var(--c-accent); padding-bottom: 5px; margin: 24px 0 10px; }}
.md h1:first-child {{ margin-top: 0; }}
.md h2 {{ font-size: 14px; font-weight: 700; color: #fff;
  background: var(--c-side-bg); border-left: 3px solid var(--c-accent);
  padding: 5px 12px; margin: 18px 0 9px; border-radius: 0 4px 4px 0; }}
.md h3 {{ font-size: 14px; font-weight: 600; color: var(--c-h3); margin: 12px 0 5px; }}
.md p {{ margin: 7px 0; line-height: 1.65; }}
.md ul, .md ol {{ margin: 5px 0 5px 18px; }}
.md li {{ margin: 2px 0; }}
.md a {{ color: #1565C0; text-decoration: underline; }}
.md a:visited {{ color: #1565C0; }}
.md table {{ border-collapse: collapse; margin: 8px 0; font-size: 13px; width: 100%; }}
.md th {{ background: var(--c-th-bg); color: var(--c-th-text); font-weight: 500; font-size: 11px;
  letter-spacing: .3px; text-transform: uppercase; padding: 4px 12px; text-align: left; }}
.md td {{ padding: 4px 12px; border-bottom: 1px solid var(--c-td-border); }}
.md tr:nth-child(even) td {{ background: var(--c-tr-alt); }}
.md pre {{ background: var(--c-pre-bg); color: var(--c-pre-text);
  border: 1px solid var(--c-side-border); border-radius: 4px;
  padding: 10px 14px; overflow-x: auto; margin: 8px 0;
  font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px; line-height: 1.5; }}
.md code {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px;
  background: var(--c-code-bg); color: var(--c-code-text);
  padding: 1px 5px; border-radius: 3px; }}
.md pre code {{ background: none; padding: 0; color: inherit; }}
.md blockquote {{ border-left: 3px solid var(--c-accent); padding: 6px 14px;
  margin: 8px 0; background: var(--c-callout-bg); border-radius: 0 4px 4px 0; }}
.md hr {{ border: none; border-top: 1px solid var(--c-td-border); margin: 16px 0; }}

/* ── Script man page ── */
.sd-man {{ max-width: 740px; padding: 0;
  font-family: 'Cascadia Code', Consolas, 'Courier New', monospace; font-size: 13px;
  line-height: 1.55; color: var(--c-text); background: var(--c-bg); }}
.sd-man-header {{ display: flex; justify-content: space-between; align-items: baseline;
  padding: 8px 0; border-bottom: 1px solid var(--c-td-border); margin-bottom: 16px; }}
.sd-man-header-left {{ font-weight: 700; font-size: 13px; text-transform: uppercase; }}
.sd-man-header-right {{ font-size: 11px; color: var(--c-h3); }}
.sd-sec {{ font-size: 13px; font-weight: 700; color: var(--c-h1);
  margin: 22px 0 4px; padding: 0; text-transform: uppercase; letter-spacing: 0.5px; }}
.sd-sec:first-child {{ margin-top: 0; }}
.sd-body {{ padding-left: 28px; margin-bottom: 4px; }}
.sd-name-line {{ font-size: 14px; font-weight: 700; color: var(--c-accent); }}
.sd-name-dash {{ font-size: 13px; color: var(--c-text); font-weight: 400; }}
.sd-body p {{ margin: 3px 0 8px; color: var(--c-text); font-size: 13px; line-height: 1.6;
  font-family: 'Segoe UI', Arial, sans-serif; }}
.sd-cmd {{ display: block; font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px;
  color: var(--c-pre-text); background: var(--c-pre-bg); padding: 4px 10px; border-radius: 3px;
  margin: 3px 0; border-left: 3px solid var(--c-accent); }}
.sd-item {{ font-size: 13px; color: var(--c-text); padding: 2px 0; line-height: 1.55; }}
.sd-empty {{ font-size: 13px; color: var(--c-h3); font-style: italic; }}
.sd-footer {{ display: flex; justify-content: space-between; align-items: baseline;
  margin-top: 28px; padding-top: 8px; border-top: 1px solid var(--c-td-border);
  font-size: 11px; color: var(--c-h3); }}

/* ── Page footer ── */
.doc-footer {{ margin-top: 40px; padding-top: 12px; border-top: 1px solid var(--c-td-border);
  font-size: 11px; color: var(--c-h3); display: flex; justify-content: space-between; }}
</style>
</head>
<body>

<header class="page-header gem-header">
  <div class="gem-header-left">
    <span class="gem-header-logo">{_html.escape(display_name)}</span>
    <span class="gem-header-title">Documentation</span>
  </div>
  <nav class="gem-header-nav">
    <a href="index.html" style="border-bottom-color: var(--c-accent);">Documentation</a>
  </nav>
  <span class="gem-header-copyright"></span>
</header>

<div class="layout">

<nav class="sidebar">
{sidebar_html}
</nav>

<main>

  <!-- Home -->
  <div id="home" class="content-section active">
    {home_html}
    <div class="doc-footer">
      <span>Generated: {_html.escape(gen_date)} | Version: {_html.escape(gen_version)}</span>
      <span>Source: {_html.escape(spec_name)} specifications</span>
    </div>
  </div>

  <!-- Guide viewer -->
  <div id="guide" class="content-section">
    <div id="guide-content" class="md"></div>
    <div class="doc-footer">
      <span>Generated: {_html.escape(gen_date)} | Version: {_html.escape(gen_version)}</span>
      <span>Source: {_html.escape(spec_name)} specifications</span>
    </div>
  </div>

  <!-- Script man page -->
  <div id="script-detail" class="content-section">
    <div id="sd-content"></div>
  </div>

</main>

<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
{guides_js}

{scripts_js}

marked.setOptions({{ gfm: true, breaks: false }});

function clearActive() {{
  document.querySelectorAll('.sn, .sn-sub').forEach(function(a) {{ a.classList.remove('active'); }});
}}

function show(id) {{
  document.querySelectorAll('.content-section').forEach(function(s) {{ s.classList.remove('active'); }});
  var sec = document.getElementById(id);
  if (sec) sec.classList.add('active');
  clearActive();
  document.querySelector('main').scrollTop = 0;
}}

function showGuide(key) {{
  var content = GUIDES[key];
  if (!content) return;
  var guideEl = document.getElementById('guide-content');
  guideEl.innerHTML = marked.parse(content);
  show('guide');
  clearActive();
  document.querySelectorAll('[data-key="' + key + '"]').forEach(function(el) {{
    if (el.classList.contains('sn')) el.classList.add('active');
  }});
}}

function showGuideSection(key, anchor) {{
  showGuide(key);
  clearActive();
  document.querySelectorAll('[data-key="' + key + '"]').forEach(function(el) {{ el.classList.add('active'); }});
  // Scroll to the anchor
  setTimeout(function() {{
    var headings = document.querySelectorAll('#guide-content h2');
    for (var i = 0; i < headings.length; i++) {{
      var id = headings[i].textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      if (id === anchor) {{
        headings[i].scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        break;
      }}
    }}
  }}, 50);
}}

function esc(t) {{ return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}

var MAN_SECTION_MAP = {{
  'Arguments': 'OPTIONS', 'Options': 'OPTIONS', 'Flags': 'OPTIONS',
  'Exit codes': 'EXIT STATUS', 'Exit': 'EXIT STATUS',
  'Writes': 'FILES', 'Creates': 'FILES', 'Output': 'FILES', 'Reads': 'FILES',
  'Examples': 'EXAMPLES', 'Example': 'EXAMPLES',
  'Modes': 'MODES', 'Checks': 'DESCRIPTION', 'Workflow': 'DESCRIPTION',
  'Template source': 'SEE ALSO',
}};
var MAN_SECTION_ORDER = ['SYNOPSIS','DESCRIPTION','OPTIONS','MODES','FILES','EXAMPLES','EXIT STATUS','SEE ALSO'];

function showScript(file) {{
  var s = SCRIPTS[file] || {{}};
  var desc = s.desc || '';
  var secs = s.sections || {{}};
  var basename = file.replace(/\\..*$/, '').toUpperCase();
  var projectName = {json.dumps(display_name)};

  var html = '<div class="sd-man">';
  html += '<div class="sd-man-header">';
  html += '<span class="sd-man-header-left">' + esc(basename) + '(1)</span>';
  html += '<span class="sd-man-header-right">' + esc(projectName) + ' Manual</span>';
  html += '</div>';

  html += '<div class="sd-sec">NAME</div>';
  html += '<div class="sd-body"><span class="sd-name-line">' + esc(file) + '</span>';
  if (desc) html += ' <span class="sd-name-dash">&mdash; ' + esc(desc) + '</span>';
  html += '</div>';

  var syn = secs['Usage'] || secs['Synopsis'] || '';
  if (syn) {{
    html += '<div class="sd-sec">SYNOPSIS</div><div class="sd-body">';
    syn.split('\\n').forEach(function(line) {{
      if (line.trim()) html += '<code class="sd-cmd">' + esc(line.trim()) + '</code>';
    }});
    html += '</div>';
  }}

  var body = secs['_desc'] || '';
  var descExtra = [];
  Object.keys(secs).forEach(function(key) {{
    if (MAN_SECTION_MAP[key] === 'DESCRIPTION' && secs[key].trim()) descExtra.push(secs[key]);
  }});
  if (body || descExtra.length) {{
    html += '<div class="sd-sec">DESCRIPTION</div><div class="sd-body">';
    if (body) {{
      body.split('\\n\\n').forEach(function(para) {{
        var t = para.trim().replace(/\\n/g, ' ');
        if (t) html += '<p>' + esc(t) + '</p>';
      }});
    }}
    descExtra.forEach(function(extra) {{
      extra.split('\\n').forEach(function(line) {{
        if (line.trim()) html += '<div class="sd-item">' + esc(line.trim()) + '</div>';
      }});
    }});
    html += '</div>';
  }}

  var skip = {{'_desc':1,'Usage':1,'Synopsis':1}};
  var codeKeys = {{'EXAMPLES':1,'SYNOPSIS':1}};
  var rendered = {{'DESCRIPTION':1}};

  MAN_SECTION_ORDER.forEach(function(manKey) {{
    if (manKey === 'SYNOPSIS' || manKey === 'DESCRIPTION') return;
    var parts = [];
    Object.keys(secs).forEach(function(key) {{
      if (skip[key] || !secs[key].trim()) return;
      var mapped = MAN_SECTION_MAP[key] || key.toUpperCase();
      if (mapped === manKey) parts.push(secs[key]);
    }});
    if (!parts.length) return;
    rendered[manKey] = 1;
    html += '<div class="sd-sec">' + esc(manKey) + '</div><div class="sd-body">';
    parts.forEach(function(text) {{
      text.split('\\n').forEach(function(line) {{
        if (line.trim()) {{
          if (codeKeys[manKey]) html += '<code class="sd-cmd">' + esc(line.trim()) + '</code>';
          else html += '<div class="sd-item">' + esc(line.trim()) + '</div>';
        }}
      }});
    }});
    html += '</div>';
  }});

  Object.keys(secs).forEach(function(key) {{
    if (skip[key] || !secs[key].trim()) return;
    var mapped = MAN_SECTION_MAP[key] || key.toUpperCase();
    if (rendered[mapped]) return;
    rendered[mapped] = 1;
    html += '<div class="sd-sec">' + esc(mapped) + '</div><div class="sd-body">';
    secs[key].split('\\n').forEach(function(line) {{
      if (line.trim()) html += '<div class="sd-item">' + esc(line.trim()) + '</div>';
    }});
    html += '</div>';
  }});

  if (!desc && !syn && !body) html += '<div class="sd-empty">(no documentation available)</div>';

  html += '<div class="sd-footer">';
  html += '<span>' + esc(projectName) + '</span>';
  html += '<span>bin/' + esc(file) + '</span>';
  html += '</div>';

  html += '</div>';

  document.getElementById('sd-content').innerHTML = html;
  show('script-detail');
  clearActive();
  var el = document.querySelector('[data-script="' + file + '"]');
  if (el) el.classList.add('active');
}}

// Initialize: show home, render overview
(function() {{
  var overview = GUIDES['OVERVIEW'] || '';
  var el = document.getElementById('home-overview');
  if (el && overview) el.innerHTML = marked.parse(overview);
  show('home');
}})();
</script>

</div><!-- .layout -->
</body>
</html>'''


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Assemble project documentation HTML')
    parser.add_argument('--target', required=True, help='Target project directory')
    parser.add_argument('--theme', default='slate', help='Theme name')
    parser.add_argument('--spec-name', default='', help='Specification name for footer')
    args = parser.parse_args()

    target = Path(args.target)
    docs_dir = target / 'docs'
    bin_dir = target / 'bin'

    # Read metadata
    meta_path = target / 'METADATA.md'
    metadata = read_meta(meta_path)

    # Discover content and scripts
    guides = discover_guides(docs_dir)
    scripts = discover_scripts(bin_dir)

    if not guides:
        print('  WARNING: No DOC-*.md files found — generating empty documentation')

    spec_name = args.spec_name or metadata.get('name', target.name)

    # Build and write
    page_html = build_page(metadata, guides, scripts, spec_name)
    output_path = docs_dir / 'index.html'
    output_path.write_text(page_html, encoding='utf-8')
    print(f'  Generated: {output_path}')
    print(f'  Guides: {len(guides)}, Scripts: {len(scripts)}')


if __name__ == '__main__':
    main()
