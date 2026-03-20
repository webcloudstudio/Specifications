#!/usr/bin/env python3
# CommandCenter Operation
# Name: Build Documentation
# Category: maintenance
"""
Build doc/index.html — single-page documentation for the Prototyper system.

Layout: sidebar (dark chrome) + content (light).
Default view: Specification Process guide.
Sidebar: Overview | Guides | Reference | Projects
"""
import html as h
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DOC_DIR = PROJECT_DIR / "doc"
BIN_DIR = PROJECT_DIR / "bin"

SKIP_DIRS = {
    '__pycache__', '.git', 'venv', 'archive', 'stack', 'bin', 'templates',
    'doc', 'logs', 'GLOBAL_RULES',
}
STATUS_COLORS = {
    'IDEA': '#94a3b8', 'PROTOTYPE': '#fdab3d', 'ACTIVE': '#0073ea',
    'PRODUCTION': '#00c875', 'ARCHIVED': '#4a5568',
}
SCRIPT_CATEGORIES = {
    'spec-workflow':       'Spec Workflow',
    'project-management':  'Project Management',
    'maintenance':         'Maintenance',
}

GUIDE_ORDER = ['SPECIFICATION-PROCESS', 'PROJECT-SETUP']
GUIDE_TITLES = {
    'SPECIFICATION-PROCESS': 'Specification Process',
    'PROJECT-SETUP': 'Setup a Project',
}


# ── Discover scripts ──────────────────────────────────────────────────────────

def discover_scripts():
    """Extract name, category, one-line desc, and full usage block from script headers."""
    scripts = []
    for ext in ('*.sh', '*.py'):
        for path in sorted(BIN_DIR.glob(ext)):
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
                            detail_lines.append(stripped)
                    else:
                        in_header = False
                # Python docstring
                if line.startswith('"""') and not desc:
                    inline = line.strip('"""').strip()
                    desc = inline if inline else (lines[i + 1].strip() if i + 1 < len(lines) else '')
            label = cc_name or path.stem.replace('_', ' ').title()
            if not desc and detail_lines:
                desc = detail_lines[0]
            details = '\n'.join(l for l in detail_lines if l).strip()
            scripts.append({
                'file': path.name, 'label': label,
                'category': category or 'maintenance',
                'desc': desc or label,
                'details': details,
            })
    return scripts


# ── Discover projects ─────────────────────────────────────────────────────────

def read_meta(meta_path):
    fields = {}
    if meta_path.exists():
        for line in meta_path.read_text(encoding='utf-8').splitlines():
            if ':' in line and not line.startswith('#'):
                k, v = line.split(':', 1)
                fields[k.strip()] = v.strip()
    return fields


def discover_projects():
    projects = []
    for entry in sorted(PROJECT_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith('.') or entry.name.startswith('Proposed'):
            continue
        if entry.name in SKIP_DIRS:
            continue
        meta_path = entry / 'METADATA.md'
        if not meta_path.exists():
            continue
        fields = read_meta(meta_path)
        if fields.get('type', '').lower() in ('build', 'build-artifact'):
            continue
        projects.append({
            'name': entry.name,
            'display': fields.get('display_name') or fields.get('name') or entry.name,
            'status': fields.get('status', ''),
            'desc': fields.get('short_description', ''),
            'stack': fields.get('stack', ''),
            'port': fields.get('port', ''),
        })
    return projects


# ── Discover guides ───────────────────────────────────────────────────────────

def discover_guides():
    found = {f.stem: f for f in DOC_DIR.glob('*.md')}
    guides = []
    # Emit in defined order first, then any extras
    for key in GUIDE_ORDER:
        if key in found:
            title = GUIDE_TITLES.get(key, key.replace('-', ' ').replace('_', ' ').title())
            guides.append({'key': key, 'title': title, 'content': found[key].read_text(encoding='utf-8')})
    for key, f in sorted(found.items()):
        if key not in GUIDE_ORDER:
            title = GUIDE_TITLES.get(key, key.replace('-', ' ').replace('_', ' ').title())
            guides.append({'key': key, 'title': title, 'content': f.read_text(encoding='utf-8')})
    return guides


# ── Build HTML ────────────────────────────────────────────────────────────────

def build_page(scripts, projects, guides):

    # ── Guide nav + JS data ───────────────────────────────────────────────────
    guides_js = 'const GUIDES = {\n'
    guide_nav = ''
    for g in guides:
        guides_js += f'  {json.dumps(g["key"])}: {json.dumps(g["content"])},\n'
        guide_nav += f'  <a class="sn" data-sec="guide" data-key="{g["key"]}" onclick="showGuide(\'{g["key"]}\')">{h.escape(g["title"])}</a>\n'
    guides_js += '};'

    # ── Script table ──────────────────────────────────────────────────────────
    grouped = {}
    for s in scripts:
        grouped.setdefault(s['category'], []).append(s)

    scripts_html = ''
    cat_order = ['spec-workflow', 'project-management', 'maintenance']
    for cat in cat_order:
        items = grouped.get(cat)
        if not items:
            continue
        label = SCRIPT_CATEGORIES.get(cat, cat.title())
        anchor = f'cat-{cat}'
        entries = ''
        for s in items:
            sid = s['file'].replace('.', '-')
            detail_html = ''
            if s.get('details'):
                detail_html = f'<div class="sc-detail" id="sd-{sid}"><pre>{h.escape(s["details"])}</pre></div>'
                toggle = f'<span class="sc-toggle" onclick="toggleDetail(\'{sid}\')" title="Show usage">&#9656;</span>'
            else:
                toggle = ''
            entries += (
                f'<div class="sc-entry">'
                f'<div class="sc-head">{toggle}<code class="sc-name">{h.escape(s["file"])}</code>'
                f'<span class="sc-desc">{h.escape(s["desc"])}</span></div>'
                f'{detail_html}</div>\n'
            )
        scripts_html += f'<h3 id="{anchor}" class="cat-label">{label}</h3>\n<div class="sc-group">{entries}</div>\n'

    # ── Workflow steps ────────────────────────────────────────────────────────
    wf_steps = [
        (1, 'bin/create_spec.sh &lt;Project&gt;',                           'Scaffold spec directory from templates'),
        (2, 'bin/validate.sh &lt;Project&gt;',                               'Check required files, naming, fields'),
        (3, '(edit spec files)',                                              'Write concise specs: INTENT, ARCHITECTURE, SCREEN-*, FEATURE-*'),
        (4, 'bin/convert.sh &lt;Project&gt; &gt; prompt.md',                 'Generate AI expansion prompt — feed to AI agent'),
        (5, 'bin/build.sh &lt;Project&gt; &gt; prompt.md',                   'Tag commit, generate build prompt — feed to AI agent'),
    ]
    wf_rows = ''
    for n, cmd, desc in wf_steps:
        num_cell = f'<td class="wn">{n}</td>'
        if n == 3:
            wf_rows += f'<tr class="wedit"><td class="wn">—</td><td class="wcmd">{cmd}</td><td class="wdesc">{desc}</td></tr>\n'
        else:
            wf_rows += f'<tr>{num_cell}<td class="wcmd"><code>{cmd}</code></td><td class="wdesc">{desc}</td></tr>\n'

    # ── Projects sidebar ──────────────────────────────────────────────────────
    proj_nav = ''
    for p in projects:
        proj_nav += f'  <a class="sn" href="../{p["name"]}/index.html" target="_blank">{h.escape(p["display"])}</a>\n'

    # default: first guide key (or empty)
    default_guide = guides[0]['key'] if guides else ''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prototyper — Documentation</title>
<link rel="stylesheet" href="styles/gem.css">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{ display: flex; height: 100vh; overflow: hidden;
  background: var(--c-bg); color: var(--c-text);
  font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif; font-size: 15px; line-height: 1.7; }}

/* ── Sidebar ── */
.sidebar {{ width: 210px; min-width: 210px; display: flex; flex-direction: column;
  background: var(--c-side-bg); border-right: 1px solid var(--c-side-border);
  overflow-y: auto; flex-shrink: 0; }}

.sidebar-header {{ background: var(--c-topbar-bg); padding: 14px 16px 12px;
  border-bottom: 1px solid var(--c-side-border); }}
.sidebar-header h1 {{ color: #fff; font-size: 15px; font-weight: 600; line-height: 1.2; }}

.nav-section {{ font-size: 9.5px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; color: var(--c-side-section);
  padding: 10px 16px 3px; }}
.nav-sep {{ border-top: 1px solid var(--c-side-border); margin: 6px 0; }}

.sn {{ display: flex; align-items: center; padding: 5px 16px;
  font-size: 13px; font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif;
  color: #fff; cursor: pointer;
  border-left: 3px solid transparent; text-decoration: none;
  transition: background .1s, border-color .1s; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; }}
.sn:hover {{ background: rgba(255,255,255,.07); border-left-color: var(--c-accent); }}
.sn.active {{ color: var(--c-accent); border-left-color: var(--c-accent); background: rgba(44,182,125,.08); }}

/* ── Content ── */
main {{ flex: 1; overflow-y: auto; padding: 28px 36px 48px; }}
.content-section {{ display: none; max-width: 840px; }}
.content-section.active {{ display: block; }}

/* ── Pipeline ── */
.pipeline {{ display: flex; align-items: center; gap: 0; margin-bottom: 22px; flex-wrap: wrap; }}
.pip-step {{ background: var(--c-side-bg); border: 1px solid var(--c-side-border);
  border-radius: 4px; padding: 4px 11px; text-align: center; }}
.pip-step .pl {{ font-size: 12px; color: #fff; font-weight: 600; white-space: nowrap; display: block; }}
.pip-step .pc {{ font-size: 10.5px; color: var(--c-side-section);
  font-family: 'Cascadia Code', Consolas, monospace; display: block; }}
.pip-arr {{ color: var(--c-side-section); padding: 0 6px; font-size: 16px; }}

/* ── Rendered markdown ── */
.md h1 {{ font-size: 22px; font-weight: 700; color: var(--c-accent);
  border-bottom: 2px solid var(--c-accent); padding-bottom: 5px; margin: 24px 0 10px; }}
.md h1:first-child {{ margin-top: 0; }}
.md h2 {{ font-size: 15px; font-weight: 700; color: #fff;
  background: var(--c-side-bg); border-left: 3px solid var(--c-accent);
  padding: 6px 12px; margin: 20px 0 10px; border-radius: 0 4px 4px 0; }}
.md h3 {{ font-size: 15px; font-weight: 600; color: var(--c-h3); margin: 14px 0 6px; }}
.md p {{ margin: 8px 0; line-height: 1.7; }}
.md ul, .md ol {{ margin: 6px 0 6px 20px; }}
.md li {{ margin: 3px 0; }}
.md a {{ color: #1565C0; text-decoration: underline; }}
.md a:visited {{ color: #1565C0; }}
.md table {{ border-collapse: collapse; margin: 10px 0; font-size: 14px; width: 100%; }}
.md th {{ background: var(--c-th-bg); color: var(--c-th-text); font-weight: 600; padding: 6px 12px; text-align: left; }}
.md td {{ padding: 5px 12px; border-bottom: 1px solid var(--c-td-border); }}
.md tr:nth-child(even) td {{ background: var(--c-tr-alt); }}
.md pre {{ background: var(--c-pre-bg); color: var(--c-pre-text);
  border: 1px solid var(--c-side-border); border-radius: 4px;
  padding: 12px 14px; overflow-x: auto; margin: 10px 0;
  font-family: 'Cascadia Code', Consolas, monospace; font-size: 13px; line-height: 1.5; }}
.md code {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 13px;
  background: var(--c-code-bg); color: var(--c-code-text);
  padding: 1px 5px; border-radius: 3px; }}
.md pre code {{ background: none; padding: 0; color: inherit; }}
.md blockquote {{ border-left: 3px solid var(--c-accent); padding: 8px 14px;
  margin: 10px 0; background: var(--c-callout-bg); border-radius: 0 4px 4px 0; }}
.md hr {{ border: none; border-top: 1px solid var(--c-td-border); margin: 18px 0; }}

/* ── Scripts ── */
.cat-label {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px;
  color: var(--c-h3); margin: 22px 0 4px; padding-bottom: 3px;
  border-bottom: 1px solid var(--c-td-border); }}
.cat-label:first-child {{ margin-top: 0; }}
.sc-group {{ margin-bottom: 6px; }}
.sc-entry {{ border-bottom: 1px solid var(--c-td-border); }}
.sc-entry:last-child {{ border-bottom: none; }}
.sc-head {{ display: flex; align-items: baseline; gap: 10px; padding: 5px 4px; }}
.sc-toggle {{ color: var(--c-accent); cursor: pointer; font-size: 11px; flex-shrink: 0;
  width: 12px; user-select: none; }}
.sc-toggle:hover {{ color: var(--c-h1); }}
.sc-name {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px;
  color: var(--c-code-text); background: var(--c-code-bg); padding: 1px 5px;
  border-radius: 3px; white-space: nowrap; flex-shrink: 0; }}
.sc-desc {{ font-size: 12.5px; color: var(--c-h3); }}
.sc-detail {{ display: none; margin: 0 0 6px 22px; }}
.sc-detail pre {{ background: var(--c-pre-bg); color: var(--c-pre-text); font-size: 12px;
  font-family: 'Cascadia Code', Consolas, monospace; padding: 8px 12px;
  border-radius: 4px; line-height: 1.5; white-space: pre-wrap; }}

/* ── Workflow table ── */
.wf-section-h {{ font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px;
  color: var(--c-h3); margin: 22px 0 8px; }}
.wf-section-h:first-child {{ margin-top: 0; }}
.wf-table {{ width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 14px; }}
.wf-table th {{ background: var(--c-th-bg); color: var(--c-th-text); padding: 6px 10px;
  text-align: left; font-weight: 600; font-size: 12.5px; }}
.wf-table td {{ padding: 6px 10px; border-bottom: 1px solid var(--c-td-border); vertical-align: top; }}
.wf-table tr:last-child td {{ border-bottom: none; }}
.wn {{ width: 28px; color: var(--c-accent); font-weight: 700; }}
.wcmd {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px; white-space: nowrap; }}
.wcmd code {{ background: var(--c-code-bg); color: var(--c-code-text); padding: 1px 5px; border-radius: 3px; }}
.wedit td {{ color: var(--c-h3); font-style: italic; }}
.wdesc {{ color: var(--c-h3); font-size: 13px; }}
.note {{ font-size: 13px; color: var(--c-h3); padding: 8px 12px; margin-top: 12px;
  background: var(--c-callout-bg); border-left: 3px solid var(--c-accent); border-radius: 0 4px 4px 0; }}
.note code {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12px;
  background: var(--c-code-bg); color: var(--c-code-text); padding: 1px 4px; border-radius: 3px; }}

section h2 {{ font-size: 19px; font-weight: 700; color: var(--c-h1);
  border-bottom: 2px solid var(--c-h1-border); padding-bottom: 4px; margin-bottom: 12px; }}
</style>
</head>
<body>

<nav class="sidebar">
  <div class="sidebar-header">
    <h1>&#9654; Prototyper</h1>
  </div>

  <div class="nav-sep"></div>
{guide_nav}
  <a class="sn" data-sec="workflow" onclick="show('workflow')">Workflow</a>

  <div class="nav-sep"></div>
  <div class="nav-section">Current Projects</div>
{proj_nav}
</nav>

<main>

  <!-- ── Guide viewer ──────────────────────────── -->
  <div id="guide" class="content-section">
    <div id="guide-content" class="md"></div>
  </div>

  <!-- ── Workflow + Scripts ────────────────────── -->
  <div id="workflow" class="content-section">
    <p class="wf-section-h">The Pipeline</p>
    <div class="pipeline">
      <div class="pip-step"><span class="pl">Create</span><span class="pc">create_spec.sh</span></div>
      <span class="pip-arr">&#8594;</span>
      <div class="pip-step"><span class="pl">Validate</span><span class="pc">validate.sh</span></div>
      <span class="pip-arr">&#8594;</span>
      <div class="pip-step"><span class="pl">Edit</span><span class="pc">spec files</span></div>
      <span class="pip-arr">&#8594;</span>
      <div class="pip-step"><span class="pl">Convert</span><span class="pc">convert.sh</span></div>
      <span class="pip-arr">&#8594;</span>
      <div class="pip-step"><span class="pl">Build</span><span class="pc">build.sh</span></div>
    </div>

    <p class="wf-section-h">Steps</p>
    <table class="wf-table">
      <thead><tr><th>#</th><th>Command</th><th>Purpose</th></tr></thead>
      <tbody>{wf_rows}</tbody>
    </table>
    <p class="note">Each <code>build.sh</code> run creates a git tag: <code>build/PROJECT/YYYY-MM-DD.N</code><br>
    Diff between builds: <code>git diff build/GAME/2026-03-19.1..build/GAME/2026-03-20.1 -- GAME/</code></p>

    <p class="wf-section-h" style="margin-top:28px">Scripts</p>
    {scripts_html}
  </div>

</main>

<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
{guides_js}

marked.setOptions({{ gfm: true, breaks: false }});

function show(id) {{
  document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
  var sec = document.getElementById(id);
  if (sec) sec.classList.add('active');
  document.querySelectorAll('.sn').forEach(a => a.classList.remove('active'));
  document.querySelectorAll('[data-sec="' + id + '"]').forEach(a => a.classList.add('active'));
  if (history.pushState) history.pushState(null, '', '#' + id);
}}

function showGuide(key) {{
  var content = GUIDES[key];
  if (!content) return;
  document.getElementById('guide-content').innerHTML = marked.parse(content);
  show('guide');
  document.querySelectorAll('.sn').forEach(a => a.classList.remove('active'));
  var link = document.querySelector('[data-key="' + key + '"]');
  if (link) link.classList.add('active');
  document.querySelector('main').scrollTop = 0;
}}

function toggleDetail(sid) {{
  var el = document.getElementById('sd-' + sid);
  var toggle = el && el.previousElementSibling && el.previousElementSibling.querySelector('.sc-toggle');
  if (!el) return;
  var open = el.style.display === 'block';
  el.style.display = open ? 'none' : 'block';
  if (toggle) toggle.innerHTML = open ? '&#9656;' : '&#9662;';
}}

// Init from hash
(function() {{
  var hash = location.hash.replace('#', '');
  if (hash && hash !== 'guide' && document.getElementById(hash)) {{
    show(hash);
  }} else {{
    {f"showGuide('{default_guide}');" if default_guide else "show('workflow');"}
  }}
}})();
</script>
</body>
</html>'''


def main():
    DOC_DIR.mkdir(exist_ok=True)
    scripts = discover_scripts()
    projects = discover_projects()
    guides = discover_guides()
    print(f"  Found {len(scripts)} scripts, {len(projects)} projects, {len(guides)} guides")
    out_path = DOC_DIR / "index.html"
    out_path.write_text(build_page(scripts, projects, guides), encoding='utf-8')
    print(f"  Wrote {out_path}  ({out_path.stat().st_size // 1024} KB)")


if __name__ == '__main__':
    main()
