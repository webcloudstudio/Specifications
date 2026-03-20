#!/usr/bin/env python3
# CommandCenter Operation
# Name: Build Documentation
# Category: maintenance
"""
Build doc/index.html — specification system documentation.

Sections: Projects (default) | Scripts | Workflow | Guides
"""
import html as h
import json
import sys
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
    'spec-workflow': 'Spec Workflow',
    'project-management': 'Project Management',
    'maintenance': 'Maintenance',
}


# ── Discover scripts ──────────────────────────────────────────────────────────

def discover_scripts():
    """Read bin/ scripts and extract name, category, description from headers."""
    scripts = []
    for ext in ('*.sh', '*.py'):
        for path in sorted(BIN_DIR.glob(ext)):
            lines = path.read_text(encoding='utf-8', errors='replace').splitlines()[:25]
            cc_name = ''
            category = ''
            desc = ''
            for i, line in enumerate(lines):
                if line.startswith('# Name:'):
                    cc_name = line.split(':', 1)[1].strip()
                elif line.startswith('# Category:'):
                    category = line.split(':', 1)[1].strip()
                elif line.startswith('"""') and not desc:
                    # inline or next-line docstring
                    inline = line.strip('"""').strip()
                    if inline:
                        desc = inline
                    elif i + 1 < len(lines):
                        desc = lines[i + 1].strip()
            label = cc_name or path.stem.replace('_', ' ').title()
            if not desc:
                desc = label
            scripts.append({
                'file': path.name,
                'label': label,
                'category': category or 'maintenance',
                'desc': desc,
            })
    return scripts


# ── Discover projects ─────────────────────────────────────────────────────────

def read_meta_fields(meta_path):
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
        if not entry.is_dir():
            continue
        if entry.name.startswith('.') or entry.name.startswith('Proposed'):
            continue
        if entry.name in SKIP_DIRS:
            continue
        meta_path = entry / 'METADATA.md'
        if not meta_path.exists():
            continue
        fields = read_meta_fields(meta_path)
        if fields.get('type', '').lower() in ('build', 'build-artifact'):
            continue
        projects.append({
            'name': entry.name,
            'display': fields.get('display_name') or fields.get('name') or entry.name,
            'status': fields.get('status', ''),
            'desc': fields.get('short_description', ''),
            'stack': fields.get('stack', ''),
            'port': fields.get('port', ''),
            'tags': fields.get('tags', ''),
        })
    return projects


# ── Discover guides ───────────────────────────────────────────────────────────

def discover_guides():
    guides = []
    for f in sorted(DOC_DIR.glob('*.md')):
        title = f.stem.replace('-', ' ').replace('_', ' ').title()
        guides.append({
            'key': f.stem,
            'title': title,
            'content': f.read_text(encoding='utf-8'),
        })
    return guides


# ── Build HTML ────────────────────────────────────────────────────────────────

def build_page(scripts, projects, guides):

    # ── Projects section ──────────────────────────────────────────────────────
    proj_cards = ''
    proj_sidebar = ''
    for proj in projects:
        color = STATUS_COLORS.get(proj['status'], '#94a3b8')
        badge = f'<span class="badge" style="background:{color}">{proj["status"]}</span>' if proj['status'] else ''
        meta_items = []
        if proj['stack']:
            meta_items.append(h.escape(proj['stack']))
        if proj['port']:
            meta_items.append('Port ' + h.escape(proj['port']))
        if proj['tags']:
            meta_items.append(h.escape(proj['tags']))
        meta_row = (' &nbsp;·&nbsp; '.join(meta_items)) if meta_items else ''
        desc = h.escape(proj['desc']) if proj['desc'] else ''
        proj_sidebar += f'<a class="sl" href="../{proj["name"]}/index.html" target="_blank">{h.escape(proj["display"])}</a>\n'
        proj_cards += f'''<div class="proj-card">
  <div class="proj-head">
    <a href="../{proj["name"]}/index.html" target="_blank" class="proj-name">{h.escape(proj["display"])}</a>
    {badge}
  </div>
  {f'<div class="proj-desc">{desc}</div>' if desc else ''}
  {f'<div class="proj-meta">{meta_row}</div>' if meta_row else ''}
  <a class="proj-link" href="../{proj["name"]}/index.html" target="_blank">View Specs &rarr;</a>
</div>\n'''

    # ── Scripts section ───────────────────────────────────────────────────────
    grouped = {}
    for s in scripts:
        grouped.setdefault(s['category'], []).append(s)

    cat_order = ['spec-workflow', 'project-management', 'maintenance']
    # add any unknown categories
    for cat in grouped:
        if cat not in cat_order:
            cat_order.append(cat)

    scripts_html = ''
    scripts_sidebar = ''
    for cat in cat_order:
        items = grouped.get(cat)
        if not items:
            continue
        cat_label = SCRIPT_CATEGORIES.get(cat, cat.replace('-', ' ').title())
        anchor = f'cat-{cat}'
        scripts_sidebar += f'<a class="sl" onclick="scrollTo(\'{anchor}\')">{cat_label}</a>\n'
        rows = ''
        for s in items:
            rows += f'<tr><td><code>{h.escape(s["file"])}</code></td><td>{h.escape(s["desc"])}</td></tr>\n'
        scripts_html += f'<h3 id="{anchor}" class="cat-head">{cat_label}</h3>\n<table class="sc-table">{rows}</table>\n'

    # ── Workflow section ──────────────────────────────────────────────────────
    wf_steps = [
        ('create_spec', 'bin/create_spec.sh &lt;Project&gt; &ldquo;description&rdquo;', 'Scaffold spec directory from templates'),
        ('validate', 'bin/validate.sh &lt;Project&gt;', 'Check required files, naming, and fields'),
        ('edit', '(edit spec files)', 'Write concise specs: tables, bullets, short sections'),
        ('convert', 'bin/convert.sh &lt;Project&gt; &gt; prompt.md', 'Generate AI expansion prompt'),
        ('build', 'bin/build.sh &lt;Project&gt; &gt; prompt.md', 'Tag commit and generate complete build prompt'),
    ]
    pipe_boxes = ''
    n = len(wf_steps)
    bw, bh, gap = 130, 50, 22
    total_w = n * bw + (n - 1) * gap
    for i, (key, cmd, desc) in enumerate(wf_steps):
        x = i * (bw + gap)
        is_edit = key == 'edit'
        fill = '#1e2329' if not is_edit else '#181c22'
        stroke = '#2CB67D' if not is_edit else '#4a5568'
        label = key.replace('_', ' ').title()
        pipe_boxes += f'<rect x="{x}" y="5" width="{bw}" height="{bh}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
        pipe_boxes += f'<text x="{x+bw//2}" y="26" text-anchor="middle" fill="{"#2CB67D" if not is_edit else "#6b7280"}" font-size="11" font-weight="700">{label}</text>\n'
        if i < n - 1:
            ax = x + bw
            pipe_boxes += f'<line x1="{ax}" y1="{5+bh//2}" x2="{ax+gap-4}" y2="{5+bh//2}" stroke="#4a5568" stroke-width="1.5"/>\n'
            pipe_boxes += f'<polygon points="{ax+gap-4},{5+bh//2-4} {ax+gap},{5+bh//2} {ax+gap-4},{5+bh//2+4}" fill="#4a5568"/>\n'

    wf_table = ''
    for i, (key, cmd, desc) in enumerate(wf_steps):
        if key == 'edit':
            wf_table += f'<tr class="wf-edit"><td class="wf-n">—</td><td class="wf-cmd">{cmd}</td><td class="wf-desc">{desc}</td></tr>\n'
        else:
            wf_table += f'<tr><td class="wf-n">{i+1}</td><td class="wf-cmd"><code>{cmd}</code></td><td class="wf-desc">{desc}</td></tr>\n'

    workflow_html = f'''<svg viewBox="0 0 {total_w} 60" xmlns="http://www.w3.org/2000/svg" class="wf-svg">
{pipe_boxes}
</svg>
<table class="wf-table">
<thead><tr><th>#</th><th>Command</th><th>Purpose</th></tr></thead>
<tbody>{wf_table}</tbody>
</table>
<p class="note">Each <code>build.sh</code> run creates an annotated git tag. Diff between builds:
<code>git diff build/GAME/2026-03-19.1..build/GAME/2026-03-20.1 -- GAME/</code></p>'''

    # ── Guides section ────────────────────────────────────────────────────────
    guides_js = 'const GUIDES = {\n'
    guides_nav = ''
    guides_cards = ''
    for g in guides:
        guides_js += f'  {json.dumps(g["key"])}: {json.dumps(g["content"])},\n'
        guides_nav += f'<a class="sl" data-guide="{h.escape(g["key"])}" onclick="showGuide(\'{g["key"]}\')">{h.escape(g["title"])}</a>\n'
        guides_cards += f'<div class="guide-card" id="g-{g["key"]}" onclick="showGuide(\'{g["key"]}\')"><div class="guide-title">{h.escape(g["title"])}</div></div>\n'
    guides_js += '};'

    # ── Sidebars per section ──────────────────────────────────────────────────
    sidebars_js = json.dumps({
        'projects': proj_sidebar,
        'scripts': scripts_sidebar,
        'workflow': '',
        'guides': guides_nav,
    })

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prototyper</title>
<link rel="stylesheet" href="styles/gem.css">
<style>
*, *::before, *::after {{ box-sizing: border-box; }}
body {{ display: flex; flex-direction: column; height: 100vh; margin: 0; overflow: hidden;
  font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; line-height: 1.5;
  background: var(--c-bg); color: var(--c-text); }}

/* ── Top nav ── */
#topnav {{ display: flex; align-items: center; height: 40px; flex-shrink: 0;
  background: var(--c-topbar-bg); border-bottom: 1px solid var(--c-side-border); }}
.tn-brand {{ font-size: 13px; font-weight: 700; color: #fff; padding: 0 18px;
  height: 100%; display: flex; align-items: center; text-decoration: none;
  border-right: 1px solid var(--c-side-border); white-space: nowrap; }}
.tn-brand b {{ color: var(--c-accent); margin-right: 5px; }}
.tn-tabs {{ display: flex; height: 100%; }}
.tn-tab {{ padding: 0 16px; font-size: 12.5px; font-weight: 500; color: var(--c-side-link);
  display: flex; align-items: center; cursor: pointer; border-bottom: 2px solid transparent;
  transition: color .1s, border-color .1s; white-space: nowrap; }}
.tn-tab:hover {{ color: #fff; }}
.tn-tab.active {{ color: #fff; border-bottom-color: var(--c-accent); }}

/* ── Body row ── */
#body {{ display: flex; flex: 1; overflow: hidden; }}

/* ── Sidebar ── */
#sidebar {{ width: 175px; min-width: 175px; background: var(--c-side-bg);
  border-right: 1px solid var(--c-side-border); overflow-y: auto;
  padding: 6px 0; display: flex; flex-direction: column; }}
.sl {{ display: block; padding: 5px 14px; font-size: 12.5px; color: var(--c-side-link);
  cursor: pointer; border-left: 3px solid transparent; text-decoration: none;
  transition: all .1s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.sl:hover {{ color: #fff; background: rgba(255,255,255,.05); border-left-color: var(--c-accent); }}
.sl.active {{ color: var(--c-accent); border-left-color: var(--c-accent); }}

/* ── Main content ── */
#main {{ flex: 1; overflow-y: auto; padding: 18px 28px 36px; }}

section {{ display: none; max-width: 860px; }}
section.active {{ display: block; }}
section h2 {{ font-size: 17px; font-weight: 700; color: var(--c-h1);
  border-bottom: 2px solid var(--c-h1-border); padding-bottom: 3px; margin: 0 0 12px; }}

/* ── Projects ── */
#proj-list {{ display: flex; flex-direction: column; gap: 6px; }}
.proj-card {{ border: 1px solid var(--c-td-border); border-radius: 5px;
  padding: 10px 14px; background: var(--c-bg); }}
.proj-head {{ display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }}
.proj-name {{ font-size: 15px; font-weight: 700; color: var(--c-accent); text-decoration: none; }}
.proj-name:hover {{ text-decoration: underline; }}
.badge {{ padding: 1px 7px; border-radius: 3px; font-size: 10px;
  font-weight: 700; color: #fff; text-transform: uppercase; }}
.proj-desc {{ font-size: 13px; color: var(--c-text); margin-bottom: 3px; }}
.proj-meta {{ font-size: 11.5px; color: var(--c-h3); margin-bottom: 4px; }}
.proj-link {{ font-size: 12px; color: var(--c-accent); text-decoration: none; }}
.proj-link:hover {{ text-decoration: underline; }}

/* ── Scripts ── */
.cat-head {{ font-size: 13px; font-weight: 700; color: var(--c-h3); text-transform: uppercase;
  letter-spacing: .5px; margin: 14px 0 4px; padding-bottom: 2px;
  border-bottom: 1px solid var(--c-td-border); }}
.cat-head:first-child {{ margin-top: 0; }}
.sc-table {{ width: 100%; border-collapse: collapse; margin-bottom: 6px; }}
.sc-table td {{ padding: 4px 8px; font-size: 12.5px; border-bottom: 1px solid var(--c-td-border); }}
.sc-table tr:last-child td {{ border-bottom: none; }}
.sc-table td:first-child {{ white-space: nowrap; width: 1%; padding-right: 16px; }}
.sc-table code {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12px;
  color: var(--c-code-text); background: var(--c-code-bg); padding: 1px 4px; border-radius: 3px; }}
.sc-table td:last-child {{ color: var(--c-h3); }}

/* ── Workflow ── */
.wf-svg {{ width: 100%; height: auto; margin-bottom: 12px; display: block; }}
.wf-table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 10px; }}
.wf-table th {{ background: var(--c-th-bg); color: var(--c-th-text); padding: 5px 10px;
  text-align: left; font-weight: 600; font-size: 12px; }}
.wf-table td {{ padding: 5px 10px; border-bottom: 1px solid var(--c-td-border); }}
.wf-table tr:last-child td {{ border-bottom: none; }}
.wf-table .wf-n {{ color: var(--c-accent); font-weight: 700; width: 24px; }}
.wf-table .wf-cmd {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 11.5px; white-space: nowrap; }}
.wf-table .wf-cmd code {{ background: var(--c-code-bg); color: var(--c-code-text);
  padding: 1px 4px; border-radius: 3px; }}
.wf-table .wf-edit td {{ color: var(--c-h3); font-style: italic; }}
.wf-table .wf-desc {{ color: var(--c-h3); font-size: 12px; }}

/* ── Guides ── */
.guide-cards {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }}
.guide-card {{ border: 1px solid var(--c-td-border); border-radius: 5px; padding: 8px 14px;
  cursor: pointer; transition: border-color .1s; }}
.guide-card:hover {{ border-color: var(--c-accent); }}
.guide-card.active {{ border-color: var(--c-accent); background: var(--c-callout-bg); }}
.guide-title {{ font-size: 13px; font-weight: 600; color: var(--c-accent); }}
.guide-back {{ color: var(--c-accent); font-size: 12px; cursor: pointer; margin-bottom: 10px; display: inline-block; }}
.guide-back:hover {{ text-decoration: underline; }}

/* Rendered markdown */
.md h1 {{ font-size: 20px; font-weight: 700; color: var(--c-h1); border-bottom: 2px solid var(--c-h1-border); padding-bottom: 4px; margin: 20px 0 10px; }}
.md h2 {{ font-size: 16px; font-weight: 600; color: var(--c-h2); border-bottom: 1px solid var(--c-h2-border); padding-bottom: 3px; margin: 14px 0 7px; }}
.md h3 {{ font-size: 14px; font-weight: 600; color: var(--c-h3); margin: 10px 0 5px; }}
.md p {{ margin: 6px 0; line-height: 1.6; }}
.md ul, .md ol {{ margin: 5px 0 5px 18px; }}
.md li {{ margin: 2px 0; }}
.md table {{ border-collapse: collapse; margin: 8px 0; font-size: 13px; width: 100%; }}
.md th {{ background: var(--c-th-bg); color: var(--c-th-text); font-weight: 600; padding: 5px 10px; text-align: left; }}
.md td {{ padding: 4px 10px; border-bottom: 1px solid var(--c-td-border); }}
.md pre {{ background: var(--c-pre-bg); color: var(--c-pre-text); border: 1px solid var(--c-side-border); border-radius: 5px; padding: 10px 12px; overflow-x: auto; margin: 8px 0; font-size: 12px; }}
.md code {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12px; background: var(--c-code-bg); color: var(--c-code-text); padding: 1px 4px; border-radius: 3px; }}
.md pre code {{ background: none; padding: 0; }}
.md blockquote {{ border-left: 3px solid var(--c-accent); padding: 6px 12px; margin: 8px 0; background: var(--c-callout-bg); border-radius: 0 3px 3px 0; }}

.note {{ font-size: 12px; color: var(--c-h3); padding: 6px 10px; background: var(--c-callout-bg);
  border-left: 3px solid var(--c-accent); border-radius: 0 3px 3px 0; }}
.note code {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 11px;
  background: var(--c-code-bg); color: var(--c-code-text); padding: 1px 4px; border-radius: 3px; }}
</style>
</head>
<body>

<div id="topnav">
  <a class="tn-brand" href="#"><b>&#9654;</b>Prototyper</a>
  <div class="tn-tabs">
    <div class="tn-tab active" data-sec="projects" onclick="show('projects')">Projects</div>
    <div class="tn-tab" data-sec="scripts" onclick="show('scripts')">Scripts</div>
    <div class="tn-tab" data-sec="workflow" onclick="show('workflow')">Workflow</div>
    <div class="tn-tab" data-sec="guides" onclick="show('guides')">Guides</div>
  </div>
</div>

<div id="body">
  <div id="sidebar"></div>
  <div id="main">

    <section id="projects" class="active">
      <h2>Projects</h2>
      <div id="proj-list">
{proj_cards}      </div>
    </section>

    <section id="scripts">
      <h2>Scripts</h2>
      {scripts_html}
    </section>

    <section id="workflow">
      <h2>Workflow</h2>
      {workflow_html}
    </section>

    <section id="guides">
      <h2>Guides</h2>
      <div class="guide-cards" id="guide-cards">
{guides_cards}      </div>
      <div id="guide-viewer" style="display:none">
        <span class="guide-back" onclick="showGuideList()">&#8592; Back to guides</span>
        <div id="guide-content" class="md"></div>
      </div>
    </section>

  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
{guides_js}

const SIDEBARS = {sidebars_js};

marked.setOptions({{ gfm: true, breaks: false }});

function show(id) {{
  document.querySelectorAll('section').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.tn-tab').forEach(t => t.classList.remove('active'));
  var tab = document.querySelector('.tn-tab[data-sec="' + id + '"]');
  if (tab) tab.classList.add('active');
  // Update sidebar
  var sb = document.getElementById('sidebar');
  sb.innerHTML = SIDEBARS[id] || '';
  if (history.pushState) history.pushState(null, '', '#' + id);
}}

function scrollTo(id) {{
  var el = document.getElementById(id);
  if (el) {{ el.scrollIntoView({{ behavior: 'smooth', block: 'start' }}); }}
}}

function showGuide(key) {{
  var content = GUIDES[key];
  if (!content) return;
  document.getElementById('guide-cards').style.display = 'none';
  document.getElementById('guide-viewer').style.display = 'block';
  document.getElementById('guide-content').innerHTML = marked.parse(content);
  document.querySelectorAll('[data-guide]').forEach(a => a.classList.remove('active'));
  var a = document.querySelector('[data-guide="' + key + '"]');
  if (a) a.classList.add('active');
  document.getElementById('guide-cards').querySelectorAll('.guide-card').forEach(c => {{
    c.classList.toggle('active', c.id === 'g-' + key);
  }});
}}

function showGuideList() {{
  document.getElementById('guide-cards').style.display = 'flex';
  document.getElementById('guide-viewer').style.display = 'none';
}}

// Init sidebar and handle hash
(function() {{
  var id = (location.hash || '#projects').replace('#', '');
  if (!document.getElementById(id)) id = 'projects';
  show(id);
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
