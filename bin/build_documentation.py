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


# ── Discover scripts ──────────────────────────────────────────────────────────

def discover_scripts():
    scripts = []
    for ext in ('*.sh', '*.py'):
        for path in sorted(BIN_DIR.glob(ext)):
            lines = path.read_text(encoding='utf-8', errors='replace').splitlines()[:25]
            cc_name = category = desc = ''
            for i, line in enumerate(lines):
                if line.startswith('# Name:'):
                    cc_name = line.split(':', 1)[1].strip()
                elif line.startswith('# Category:'):
                    category = line.split(':', 1)[1].strip()
                elif line.startswith('"""') and not desc:
                    inline = line.strip('"""').strip()
                    desc = inline if inline else (lines[i + 1].strip() if i + 1 < len(lines) else '')
            label = cc_name or path.stem.replace('_', ' ').title()
            scripts.append({
                'file': path.name, 'label': label,
                'category': category or 'maintenance',
                'desc': desc or label,
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
    guides = []
    for f in sorted(DOC_DIR.glob('*.md')):
        title = f.stem.replace('-', ' ').replace('_', ' ').title()
        guides.append({'key': f.stem, 'title': title, 'content': f.read_text(encoding='utf-8')})
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

    script_nav = ''
    scripts_html = ''
    cat_order = ['spec-workflow', 'project-management', 'maintenance']
    for cat in cat_order:
        items = grouped.get(cat)
        if not items:
            continue
        label = SCRIPT_CATEGORIES.get(cat, cat.title())
        anchor = f'cat-{cat}'
        script_nav += f'  <a class="sn" data-sec="scripts" onclick="show(\'scripts\'); scrollAnchor(\'{anchor}\')">{label}</a>\n'
        rows = ''.join(
            f'<tr><td><code>{h.escape(s["file"])}</code></td><td>{h.escape(s["desc"])}</td></tr>\n'
            for s in items
        )
        scripts_html += f'<h3 id="{anchor}" class="cat-label">{label}</h3>\n<table class="ref-table">{rows}</table>\n'

    # ── Workflow ──────────────────────────────────────────────────────────────
    wf_steps = [
        (1, 'bin/create_spec.sh &lt;Project&gt; &ldquo;description&rdquo;', 'Scaffold spec directory from templates'),
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

    # ── Overview guide links ──────────────────────────────────────────────────
    ov_guide_links = ''
    for g in guides:
        ov_guide_links += f'      <a class="ov-link" onclick="showGuide(\'{g["key"]}\')">{h.escape(g["title"])} &rarr;</a>\n'

    # ── Projects sidebar ──────────────────────────────────────────────────────
    proj_nav = ''
    for p in projects:
        color = STATUS_COLORS.get(p['status'], '#94a3b8')
        dot = f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:{color};flex-shrink:0"></span>'
        proj_nav += f'  <a class="sn sn-proj" href="../{p["name"]}/index.html" target="_blank">{dot}&nbsp;{h.escape(p["display"])}</a>\n'

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
.sidebar-header p  {{ color: var(--c-side-link); font-size: 11px; margin-top: 2px;
  opacity: .8; text-transform: uppercase; letter-spacing: .5px; }}

.nav-section {{ font-size: 9.5px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; color: var(--c-side-section);
  padding: 10px 16px 3px; }}
.nav-sep {{ border-top: 1px solid var(--c-side-border); margin: 6px 0; }}

.sn {{ display: flex; align-items: center; gap: 6px; padding: 5px 16px;
  font-size: 13px; color: var(--c-side-link); cursor: pointer;
  border-left: 3px solid transparent; text-decoration: none;
  transition: color .1s, background .1s, border-color .1s; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; }}
.sn:hover {{ color: #fff; background: rgba(255,255,255,.05); border-left-color: var(--c-accent); }}
.sn.active {{ color: var(--c-accent); border-left-color: var(--c-accent); background: rgba(44,182,125,.06); }}
.sn-proj {{ font-size: 12.5px; }}

/* ── Content ── */
main {{ flex: 1; overflow-y: auto; padding: 28px 36px 48px; }}
.content-section {{ display: none; max-width: 840px; }}
.content-section.active {{ display: block; }}

/* ── Overview ── */
.ov-title {{ font-size: 26px; font-weight: 700; color: var(--c-h1);
  border-bottom: 2px solid var(--c-h1-border); padding-bottom: 6px; margin-bottom: 6px; }}
.ov-sub {{ font-size: 14px; color: var(--c-h3); margin-bottom: 22px; }}
.ov-h {{ font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px;
  color: var(--c-h3); margin-bottom: 8px; }}
.pipeline {{ display: flex; align-items: center; gap: 0; margin-bottom: 22px; flex-wrap: wrap; }}
.pip-step {{ background: var(--c-side-bg); border: 1px solid var(--c-side-border);
  border-radius: 4px; padding: 7px 12px; text-align: center; }}
.pip-step .pn {{ font-size: 10px; color: var(--c-accent); font-weight: 700; display: block; }}
.pip-step .pl {{ font-size: 12px; color: #fff; font-weight: 600; white-space: nowrap; }}
.pip-step .pc {{ font-size: 10.5px; color: var(--c-side-section); font-family: 'Cascadia Code', Consolas, monospace; }}
.pip-arr {{ color: var(--c-side-section); padding: 0 6px; font-size: 16px; }}
.ov-links {{ display: flex; gap: 10px; flex-wrap: wrap; }}
.ov-link {{ display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px;
  background: var(--c-side-bg); border: 1px solid var(--c-side-border); border-radius: 4px;
  color: var(--c-accent); font-size: 13px; font-weight: 600; text-decoration: none;
  cursor: pointer; transition: border-color .1s; }}
.ov-link:hover {{ border-color: var(--c-accent); }}

/* ── Rendered markdown ── */
.md h1 {{ font-size: 22px; font-weight: 700; color: var(--c-h1);
  border-bottom: 2px solid var(--c-h1-border); padding-bottom: 5px; margin: 24px 0 10px; }}
.md h1:first-child {{ margin-top: 0; }}
.md h2 {{ font-size: 17px; font-weight: 600; color: var(--c-h2);
  border-bottom: 1px solid var(--c-h2-border); padding-bottom: 3px; margin: 18px 0 8px; }}
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
  color: var(--c-h3); margin: 18px 0 4px; padding-bottom: 3px;
  border-bottom: 1px solid var(--c-td-border); }}
.cat-label:first-child {{ margin-top: 0; }}
.ref-table {{ width: 100%; border-collapse: collapse; margin-bottom: 4px; font-size: 13.5px; }}
.ref-table td {{ padding: 4px 8px; border-bottom: 1px solid var(--c-td-border); vertical-align: top; }}
.ref-table tr:last-child td {{ border-bottom: none; }}
.ref-table tr:nth-child(even) td {{ background: var(--c-tr-alt); }}
.ref-table td:first-child {{ width: 1%; white-space: nowrap; padding-right: 18px; }}
.ref-table td:last-child {{ color: var(--c-h3); }}
.ref-table code {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px;
  color: var(--c-code-text); background: var(--c-code-bg); padding: 1px 4px; border-radius: 3px; }}

/* ── Workflow ── */
.wf-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
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
    <p>Specification System</p>
  </div>

  <div class="nav-sep"></div>
  <a class="sn" data-sec="overview" onclick="show('overview')">Overview</a>

  <div class="nav-sep"></div>
  <div class="nav-section">Guides</div>
{guide_nav}
  <div class="nav-sep"></div>
  <div class="nav-section">Reference</div>
{script_nav}  <a class="sn" data-sec="workflow" onclick="show('workflow')">Workflow</a>

  <div class="nav-sep"></div>
  <div class="nav-section">Projects</div>
{proj_nav}
</nav>

<main>

  <!-- ── Overview ─────────────────────────────── -->
  <div id="overview" class="content-section active">
    <p class="ov-title">Prototyper</p>
    <p class="ov-sub">A specification pipeline for AI-assisted software development.</p>

    <p class="ov-h">The Pipeline</p>
    <div class="pipeline">
      <div class="pip-step"><span class="pn">1</span><span class="pl">Create</span><span class="pc">create_spec.sh</span></div>
      <span class="pip-arr">&#8594;</span>
      <div class="pip-step"><span class="pn">2</span><span class="pl">Validate</span><span class="pc">validate.sh</span></div>
      <span class="pip-arr">&#8594;</span>
      <div class="pip-step"><span class="pn">3</span><span class="pl">Edit</span><span class="pc">spec files</span></div>
      <span class="pip-arr">&#8594;</span>
      <div class="pip-step"><span class="pn">4</span><span class="pl">Convert</span><span class="pc">convert.sh</span></div>
      <span class="pip-arr">&#8594;</span>
      <div class="pip-step"><span class="pn">5</span><span class="pl">Build</span><span class="pc">build.sh</span></div>
    </div>

    <p class="ov-h">Read the guides</p>
    <div class="ov-links">
{ov_guide_links}    </div>
  </div>

  <!-- ── Guide viewer ──────────────────────────── -->
  <div id="guide" class="content-section">
    <div id="guide-content" class="md"></div>
  </div>

  <!-- ── Scripts ───────────────────────────────── -->
  <div id="scripts" class="content-section">
    <h2>Scripts</h2>
    {scripts_html}
  </div>

  <!-- ── Workflow ──────────────────────────────── -->
  <div id="workflow" class="content-section">
    <h2>Workflow</h2>
    <table class="wf-table">
      <thead><tr><th>#</th><th>Command</th><th>Purpose</th></tr></thead>
      <tbody>{wf_rows}</tbody>
    </table>
    <p class="note">Each <code>build.sh</code> run creates a git tag: <code>build/PROJECT/YYYY-MM-DD.N</code><br>
    Diff between builds: <code>git diff build/GAME/2026-03-19.1..build/GAME/2026-03-20.1 -- GAME/</code></p>
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
  // Mark the specific guide link active
  document.querySelectorAll('.sn').forEach(a => a.classList.remove('active'));
  var link = document.querySelector('[data-key="' + key + '"]');
  if (link) link.classList.add('active');
  document.getElementById('main') && (document.querySelector('main').scrollTop = 0);
}}

function scrollAnchor(id) {{
  var el = document.getElementById(id);
  if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
}}

// Init from hash
(function() {{
  var hash = location.hash.replace('#', '') || 'overview';
  if (hash.startsWith('guide-')) {{
    showGuide(hash.replace('guide-', ''));
  }} else if (document.getElementById(hash)) {{
    show(hash);
  }} else {{
    // default: load first guide
    {f"showGuide('{default_guide}');" if default_guide else "show('overview');"}
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
