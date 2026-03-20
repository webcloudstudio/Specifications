#!/usr/bin/env python3
# CommandCenter Operation
# Name: Build Documentation
# Category: maintenance
"""
Build doc/index.html — single-page documentation for the Prototyper system.
Also rebuilds root index.html (redirect) and per-project index.html viewers.

Layout: sidebar (dark chrome) + content (light).
Default view: Workflow pipeline.
Sidebar: Workflow (+ step sub-items) | Workflow Scripts | Setup A Project | Current Projects
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

# Scripts that appear in the sidebar as Workflow Scripts (in this order)
WF_SCRIPTS = ['create_spec.sh', 'validate.sh', 'convert.sh', 'build.sh', 'generate_prompt.sh']

# Scripts that appear as indented children of another script in Other Scripts
SCRIPT_CHILDREN = {
    'build_documentation.sh': ['build_documentation.py'],
}

# Human-readable descriptions override auto-detected ones
SCRIPT_DESCRIPTIONS = {
    'create_spec.sh':          'Scaffold a new spec directory from templates',
    'validate.sh':             'Check a spec directory for required files, naming, and completeness',
    'convert.sh':              'Generate an AI expansion prompt from concise spec files',
    'build.sh':                'Tag the commit and generate a build prompt for an AI agent',
    'generate_prompt.sh':      'Generate a build prompt without creating a git tag (legacy)',
    'test.sh':                 'Run self-tests on the specification system',
    'build_documentation.py':  'Build this documentation page (doc/index.html)',
    'build_documentation.sh':  'Wrapper — runs build_documentation.py with the slate theme',
}

GUIDE_ORDER = ['SPECIFICATION-PROCESS', 'PROJECT-SETUP', 'PROMOTE']
GUIDE_TITLES = {
    'SPECIFICATION-PROCESS': 'Specification Process',
    'PROJECT-SETUP':         'Project Creation',
    'PROMOTE':               'Promote',
}

# Scripts whose usage block is always shown (no expand toggle)
ALWAYS_EXPANDED = {'test.sh'}


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
                            # Preserve indentation — lstrip('#') only, not .strip()
                            detail_lines.append(line.lstrip('#'))
                    else:
                        in_header = False
                # Python docstring
                if line.startswith('"""') and not desc:
                    inline = line.strip('"""').strip()
                    desc = inline if inline else (lines[i + 1].strip() if i + 1 < len(lines) else '')
            label = cc_name or path.stem.replace('_', ' ').title()
            if not desc and detail_lines:
                desc = detail_lines[0].strip()
            details = '\n'.join(detail_lines).strip()
            desc = SCRIPT_DESCRIPTIONS.get(path.name, desc or label)
            scripts.append({
                'file': path.name, 'label': label,
                'desc': desc,
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
        })
    return projects


# ── Discover guides ───────────────────────────────────────────────────────────

def discover_guides():
    found = {f.stem: f for f in DOC_DIR.glob('*.md')}
    guides = []
    for key in GUIDE_ORDER:
        if key in found:
            title = GUIDE_TITLES.get(key, key.replace('-', ' ').replace('_', ' ').title())
            guides.append({'key': key, 'title': title, 'content': found[key].read_text(encoding='utf-8')})
    for key, f in sorted(found.items()):
        if key not in GUIDE_ORDER:
            title = GUIDE_TITLES.get(key, key.replace('-', ' ').replace('_', ' ').title())
            guides.append({'key': key, 'title': title, 'content': f.read_text(encoding='utf-8')})
    return guides


# ── Generate per-project and root index.html files ───────────────────────────

def generate_indexes():
    """Rebuild root index.html (redirect) and per-project index.html viewers."""
    # Root redirect
    root_html = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
                 '<meta http-equiv="refresh" content="0; url=doc/index.html">\n'
                 '<title>Prototyper — Redirecting...</title>\n</head>\n<body>\n'
                 '<p>Redirecting to <a href="doc/index.html">Prototyper Documentation</a>...</p>\n'
                 '</body>\n</html>')
    (PROJECT_DIR / 'index.html').write_text(root_html, encoding='utf-8')
    print('  Generated index.html (redirect)')

    template_path = PROJECT_DIR / '_project_index_template.html'
    if not template_path.exists():
        print('  Skipping project viewers: _project_index_template.html not found')
        return
    template = template_path.read_text(encoding='utf-8')

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

        docs = {}
        for md_file in sorted(entry.glob('*.md')):
            if md_file.stem.startswith('PROPOSED') or md_file.stem.startswith('UNUSED'):
                continue
            docs[md_file.stem] = md_file.read_text(encoding='utf-8')

        docs_js = 'const DOCS = {\n' + ''.join(
            f'  {json.dumps(k)}: {json.dumps(v)},\n' for k, v in docs.items()
        ) + '};'

        display_name = fields.get('display_name') or fields.get('name') or entry.name
        page_html = template.replace('<!-- PROJECT_NAME -->', display_name)
        page_html = page_html.replace('const DOCS = {};', docs_js)
        (entry / 'index.html').write_text(page_html, encoding='utf-8')
        print(f'  Generated {entry.name}/index.html ({len(docs)} docs)')


# ── Build HTML ────────────────────────────────────────────────────────────────

def build_page(scripts, projects, guides):

    # ── Guide JS data ──────────────────────────────────────────────────────────
    guides_js = 'const GUIDES = {\n'
    for g in guides:
        guides_js += f'  {json.dumps(g["key"])}: {json.dumps(g["content"])},\n'
    guides_js += '};'

    # ── Script JS data ─────────────────────────────────────────────────────────
    scripts_js = 'const SCRIPTS = {\n'
    for s in scripts:
        scripts_js += f'  {json.dumps(s["file"])}: {json.dumps({"desc": s["desc"], "details": s.get("details", "")})},\n'
    scripts_js += '};'

    # ── Separate workflow vs other scripts ────────────────────────────────────
    wf_set = set(WF_SCRIPTS)
    wf_order = {f: i for i, f in enumerate(WF_SCRIPTS)}
    wf_scripts = sorted([s for s in scripts if s['file'] in wf_set],
                        key=lambda s: wf_order.get(s['file'], 999))
    other_scripts = [s for s in scripts if s['file'] not in wf_set]

    # ── Sidebar: steps with sub-items (script or guide) ──────────────────────
    # Each entry: (step_num, label, [(sub_label, 'script'|'guide', target), ...])
    STEP_NAV = [
        (1, 'Step 1 — Create',   [('create_spec.sh',   'script', 'create_spec.sh')]),
        (2, 'Step 2 — Create',   [('Project Creation', 'guide',  'PROJECT-SETUP')]),
        (3, 'Step 3 — Validate', [('validate.sh',       'script', 'validate.sh')]),
        (4, 'Step 4 — Convert',  [('convert.sh',        'script', 'convert.sh')]),
        (5, 'Step 5 — Build',    [('build.sh',          'script', 'build.sh')]),
    ]
    step_nav = ''
    for num, label, subs in STEP_NAV:
        step_nav += f'  <a class="sn" data-step="{num}" onclick="showGuideStep(\'SPECIFICATION-PROCESS\', {num})">{h.escape(label)}</a>\n'
        for sub_label, sub_type, sub_target in subs:
            if sub_type == 'script':
                step_nav += f'  <a class="sn-sub" data-script="{h.escape(sub_target)}" onclick="showScript(\'{sub_target}\')">{h.escape(sub_label)}</a>\n'
            else:
                step_nav += f'  <a class="sn-sub" data-key="{h.escape(sub_target)}" onclick="showGuide(\'{sub_target}\')">{h.escape(sub_label)}</a>\n'
    step_nav += '  <div class="nav-sep"></div>\n'
    step_nav += f'  <a class="sn" data-key="PROMOTE" onclick="showGuide(\'PROMOTE\')">Promote</a>\n'

    # ── Sidebar: project links ────────────────────────────────────────────────
    proj_nav = ''
    for p in projects:
        url = f'../{p["name"]}/index.html'
        proj_nav += (f'  <a class="sn" data-project="{h.escape(p["name"])}" '
                     f'onclick="showProject(\'{h.escape(p["name"])}\', \'{url}\')">'
                     f'{h.escape(p["display"])}</a>\n')

    # ── Two-row workflow diagram ───────────────────────────────────────────────
    def wf_box(label, script='', path='', terminal=False):
        cls = 'wf-box wf-terminal' if terminal else 'wf-box'
        inner = f'<span class="wf-label">{h.escape(label)}</span>'
        if script:
            inner += f'<span class="wf-script">{h.escape(script)}</span>'
        if path:
            inner += f'<span class="wf-path">{h.escape(path)}</span>'
        return f'<div class="{cls}">{inner}</div>'

    ARR = '<span class="wf-arr">&#8594;</span>'
    DOWN = '<span class="wf-arr">&#8595;</span>'

    row1 = ARR.join([
        wf_box('Create', 'create_spec.sh', './<PROJECT>'),
        wf_box('Validate', 'validate.sh'),
        wf_box('Convert', 'convert.sh'),
        wf_box('Build', 'build.sh'),
        wf_box('PROTOTYPE', '', './<PROJECT>_build', terminal=True),
    ])
    row2 = ARR.join([
        wf_box('PROTOTYPE', terminal=True),
        wf_box('Promote', 'create_project.py'),
        wf_box('Project', '', '../<PROJECT>', terminal=True),
    ])

    wf_diagram = (f'<div class="wf-diagram">'
                  f'<div class="wf-row">{row1}</div>'
                  f'<div class="wf-row-r">{DOWN}</div>'
                  f'<div class="wf-row-r">{row2}</div>'
                  f'</div>')

    # ── Workflow steps table (Prototyper steps only) ───────────────────────────
    wf_step_data = [
        (1, 'bin/create_spec.sh &lt;Project&gt;', 'Scaffold spec directory from templates'),
        (2, 'bin/validate.sh &lt;Project&gt;', 'Check required files, naming, fields — exit 0 = ready'),
        (3, 'bin/convert.sh &lt;Project&gt; &gt; prompt.md', 'Expand to detailed specs with AI — optional'),
        (4, 'bin/build.sh &lt;Project&gt; &gt; prompt.md', 'Tag commit, generate build prompt — feed to AI agent'),
        (5, 'python3 bin/create_project.py &lt;Project&gt;', 'Scaffold code project — run from GAME/'),
    ]
    wf_rows = ''
    for n, cmd, desc in wf_step_data:
        wf_rows += f'<tr><td class="wn">{n}</td><td class="wcmd"><code>{cmd}</code></td><td class="wdesc">{desc}</td></tr>\n'

    # ── Other scripts (with child support) ───────────────────────────────────
    all_children = {c for kids in SCRIPT_CHILDREN.values() for c in kids}
    scripts_by_file = {s['file']: s for s in scripts}

    def sc_entry(s, child=False):
        sid = s['file'].replace('.', '-')
        always = s['file'] in ALWAYS_EXPANDED
        if s.get('details'):
            if always:
                detail = f'<div class="sc-detail-open"><pre>{h.escape(s["details"])}</pre></div>'
                toggle = ''
            else:
                detail = f'<div class="sc-detail" id="sd-{sid}"><pre>{h.escape(s["details"])}</pre></div>'
                toggle = f'<span class="sc-toggle" onclick="toggleDetail(\'{sid}\')" title="Show usage">&#9656;</span>'
        else:
            detail = toggle = ''
        extra = ' sc-child' if child else ''
        return (f'<div class="sc-entry{extra}"><div class="sc-head">{toggle}'
                f'<code class="sc-name">{h.escape(s["file"])}</code>'
                f'<span class="sc-desc">{h.escape(s["desc"])}</span></div>{detail}</div>\n')

    other_parts = []
    for s in other_scripts:
        if s['file'] in all_children:
            continue
        other_parts.append(sc_entry(s))
        for child_file in SCRIPT_CHILDREN.get(s['file'], []):
            if child_file in scripts_by_file:
                other_parts.append(sc_entry(scripts_by_file[child_file], child=True))
    other_html = f'<div class="sc-group">{"".join(other_parts)}</div>'

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
  font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif; font-size: 14px; line-height: 1.65; }}

/* ── Sidebar — invariant ── */
.sidebar {{ width: 220px; min-width: 220px; display: flex; flex-direction: column;
  background: var(--c-side-bg); border-right: 1px solid var(--c-side-border);
  overflow-y: auto; flex-shrink: 0; }}

.sidebar-header {{ background: var(--c-topbar-bg); padding: 8px 8px 6px;
  flex-shrink: 0; cursor: pointer; text-align: center; }}
.sidebar-header:hover {{ background: rgba(255,255,255,.04); }}
.sidebar-header h1 {{ color: #fff; font-size: 17px; font-weight: 700; line-height: 1; letter-spacing: .3px; }}

.nav-section {{ font-size: 9px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; color: var(--c-side-section); padding: 10px 16px 3px; }}
.nav-sep {{ border-top: 1px solid var(--c-side-border); margin: 5px 0; }}

/* Primary nav items */
.sn {{ display: block; padding: 5px 16px;
  font-size: 13px; font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif;
  color: #fff; cursor: pointer; border-left: 3px solid transparent;
  text-decoration: none; transition: background .1s, border-color .1s;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.sn:hover {{ background: rgba(255,255,255,.07); border-left-color: var(--c-accent); }}
.sn.active {{ color: var(--c-accent); border-left-color: var(--c-accent); background: rgba(44,182,125,.08); }}

/* Sub-nav items (steps under Workflow) */
.sn-sub {{ display: block; padding: 3px 16px 3px 28px;
  font-size: 11px; font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif;
  color: rgba(255,255,255,.8); cursor: pointer; border-left: 3px solid transparent;
  text-decoration: none; transition: background .1s, border-color .1s, color .1s;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.sn-sub:hover {{ color: #fff; background: rgba(255,255,255,.05); border-left-color: var(--c-accent); }}
.sn-sub.active {{ color: var(--c-accent); border-left-color: var(--c-accent); }}

/* ── Content ── */
main {{ flex: 1; overflow-y: auto; padding: 28px 36px 48px; position: relative; }}
main.project-mode {{ padding: 0; overflow: hidden; }}
.content-section {{ display: none; max-width: 860px; }}
.content-section.active {{ display: block; }}
#project {{ max-width: none; height: 100%; }}
#project.active {{ display: flex; }}
#project-frame {{ flex: 1; border: none; width: 100%; height: 100%; display: block; }}

/* ── Two-row workflow diagram ── */
.wf-diagram {{ display: flex; flex-direction: column; gap: 2px; margin-bottom: 20px; }}
.wf-row {{ display: flex; align-items: stretch; flex-wrap: nowrap; gap: 0; }}
.wf-row-r {{ display: flex; align-items: center; flex-wrap: nowrap; gap: 0; justify-content: flex-start; }}
.wf-box {{
  background: var(--c-side-bg); border: 1px solid var(--c-side-border);
  border-radius: 4px; padding: 5px 10px; text-align: center;
  display: inline-flex; flex-direction: column; gap: 2px; align-items: center; }}
.wf-terminal {{ border-color: var(--c-accent); background: #0a5c38; }}
.wf-label {{ font-size: 12px; color: #fff; font-weight: 700; white-space: nowrap; display: block; }}
.wf-script {{ font-size: 10px; color: #fff;
  font-family: 'Cascadia Code', Consolas, monospace; display: block; white-space: nowrap; }}
.wf-path {{ font-size: 9.5px; color: #fff;
  font-family: 'Cascadia Code', Consolas, monospace; display: block; white-space: nowrap; }}
.wf-arr {{ color: var(--c-side-section); padding: 0 5px; font-size: 14px; align-self: center;
  display: inline-block; }}

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
.md th {{ background: var(--c-th-bg); color: var(--c-th-text); font-weight: 600; padding: 5px 12px; text-align: left; }}
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
.sd-title {{ font-size: 18px; font-weight: 700; color: var(--c-h1); margin: 0 0 6px;
  font-family: 'Cascadia Code', Consolas, monospace; }}
.sd-desc-p {{ font-size: 14px; color: var(--c-h3); margin: 0 0 14px; }}
.sd-pre {{ background: var(--c-pre-bg); color: var(--c-pre-text); font-size: 12.5px;
  font-family: 'Cascadia Code', Consolas, monospace; padding: 12px 16px;
  border-radius: 4px; line-height: 1.5; white-space: pre;
  border: 1px solid var(--c-side-border); overflow-x: auto; }}
.sd-none {{ font-size: 13px; color: var(--c-h3); font-style: italic; }}

/* ── Scripts (expandable, for Other Scripts section) ── */
.sc-section-h {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px;
  color: var(--c-h3); margin: 22px 0 6px; padding-bottom: 3px;
  border-bottom: 1px solid var(--c-td-border); }}
.sc-group {{ margin-bottom: 6px; }}
.sc-entry {{ border-bottom: 1px solid var(--c-td-border); }}
.sc-entry:last-child {{ border-bottom: none; }}
.sc-child {{ padding-left: 16px; background: rgba(255,255,255,.02); }}
.sc-head {{ display: flex; align-items: baseline; gap: 10px; padding: 5px 4px; }}
.sc-toggle {{ color: var(--c-accent); cursor: pointer; font-size: 11px; flex-shrink: 0;
  width: 12px; user-select: none; }}
.sc-toggle:hover {{ color: var(--c-h1); }}
.sc-name {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px;
  color: var(--c-code-text); background: var(--c-code-bg); padding: 1px 5px;
  border-radius: 3px; white-space: nowrap; flex-shrink: 0; }}
.sc-desc {{ font-size: 12.5px; color: var(--c-h3); }}
.sc-detail {{ display: none; margin: 0 0 6px 22px; }}
.sc-detail-open {{ margin: 0 0 6px 0; }}
.sc-detail pre, .sc-detail-open pre {{ background: var(--c-pre-bg); color: var(--c-pre-text); font-size: 12px;
  font-family: 'Cascadia Code', Consolas, monospace; padding: 8px 12px;
  border-radius: 4px; line-height: 1.5; white-space: pre; overflow-x: auto; }}

/* ── Workflow table ── */
.wf-section-h {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px;
  color: var(--c-h3); margin: 20px 0 8px; padding-bottom: 3px;
  border-bottom: 1px solid var(--c-td-border); }}
.wf-section-h:first-child {{ margin-top: 0; }}
.wf-table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; margin-bottom: 14px; }}
.wf-table th {{ background: var(--c-th-bg); color: var(--c-th-text); padding: 5px 10px;
  text-align: left; font-weight: 600; font-size: 12px; }}
.wf-table td {{ padding: 5px 10px; border-bottom: 1px solid var(--c-td-border); vertical-align: top; }}
.wf-table tr:last-child td {{ border-bottom: none; }}
.wn {{ width: 24px; color: var(--c-accent); font-weight: 700; font-size: 12px; }}
.wcmd {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12px; white-space: nowrap; }}
.wcmd code {{ background: var(--c-code-bg); color: var(--c-code-text); padding: 1px 4px; border-radius: 3px; }}
.wdesc {{ color: var(--c-h3); font-size: 12.5px; }}
.note {{ font-size: 12.5px; color: var(--c-h3); padding: 7px 12px; margin-top: 10px;
  background: var(--c-callout-bg); border-left: 3px solid var(--c-accent); border-radius: 0 4px 4px 0; }}
.note code {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12px;
  background: var(--c-code-bg); color: var(--c-code-text); padding: 1px 4px; border-radius: 3px; }}

section h2 {{ font-size: 18px; font-weight: 700; color: var(--c-h1);
  border-bottom: 2px solid var(--c-h1-border); padding-bottom: 4px; margin-bottom: 12px; }}
</style>
</head>
<body>

<nav class="sidebar">
  <div class="sidebar-header" onclick="show('workflow')">
    <h1>&#9654; Prototyper</h1>
  </div>
{step_nav}
  <div class="nav-sep"></div>
  <div class="nav-section">Current Projects</div>
{proj_nav}
</nav>

<main>

  <!-- ── Workflow ──────────────────────────── -->
  <div id="workflow" class="content-section">
    <p class="wf-section-h">Workflows</p>
    {wf_diagram}

    <hr style="border:none;border-top:1px solid var(--c-td-border);margin:18px 0 14px;">
    <p class="wf-section-h">Administrator Scripts</p>
    {other_html}
  </div>

  <!-- ── Guide viewer ──────────────────────────── -->
  <div id="guide" class="content-section">
    <div id="guide-content" class="md"></div>
  </div>

  <!-- ── Script man page ───────────────────────── -->
  <div id="script-detail" class="content-section">
    <h2 id="sd-file" class="sd-title"></h2>
    <p id="sd-desc" class="sd-desc-p"></p>
    <hr style="border:none;border-top:1px solid var(--c-td-border);margin:0 0 14px;">
    <pre id="sd-usage" class="sd-pre"></pre>
  </div>

  <!-- ── Project viewer (iframe) ───────────────── -->
  <div id="project" class="content-section">
    <iframe id="project-frame" src="" title="Project viewer"></iframe>
  </div>

</main>

<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
{guides_js}
{scripts_js}

marked.setOptions({{ gfm: true, breaks: false }});

function clearActive() {{
  document.querySelectorAll('.sn, .sn-sub').forEach(a => a.classList.remove('active'));
}}

function show(id) {{
  document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
  var sec = document.getElementById(id);
  if (sec) sec.classList.add('active');
  document.querySelector('main').classList.toggle('project-mode', id === 'project');
  clearActive();
  document.querySelectorAll('[data-sec="' + id + '"]').forEach(a => a.classList.add('active'));
  if (id !== 'project') document.querySelector('main').scrollTop = 0;
}}

function showGuide(key) {{
  var content = GUIDES[key];
  if (!content) return;
  document.getElementById('guide-content').innerHTML = marked.parse(content);
  show('guide');
  clearActive();
  var el = document.querySelector('[data-key="' + key + '"]');
  if (el) el.classList.add('active');
}}

function showGuideStep(key, step) {{
  var content = GUIDES[key];
  if (!content) return;
  document.getElementById('guide-content').innerHTML = marked.parse(content);
  show('guide');
  clearActive();
  var el = document.querySelector('[data-step="' + step + '"]');
  if (el) el.classList.add('active');
  setTimeout(function() {{
    var headings = document.querySelectorAll('#guide-content h2, #guide-content h3');
    var label = 'Step ' + step;
    for (var i = 0; i < headings.length; i++) {{
      if (headings[i].textContent.trim().indexOf(label) === 0) {{
        headings[i].scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        break;
      }}
    }}
  }}, 80);
}}

function showScript(file) {{
  var s = SCRIPTS[file];
  document.getElementById('sd-file').textContent = file;
  document.getElementById('sd-desc').textContent = s ? s.desc : '';
  var pre = document.getElementById('sd-usage');
  if (s && s.details) {{
    pre.textContent = s.details;
    pre.className = 'sd-pre';
  }} else {{
    pre.textContent = '(no usage documentation available)';
    pre.className = 'sd-pre sd-none';
  }}
  show('script-detail');
  clearActive();
  var el = document.querySelector('[data-script="' + file + '"]');
  if (el) el.classList.add('active');
}}

function showProject(name, url) {{
  var frame = document.getElementById('project-frame');
  if (!frame.src || !frame.src.endsWith(url.replace('../', ''))) frame.src = url;
  show('project');
  clearActive();
  var el = document.querySelector('[data-project="' + name + '"]');
  if (el) el.classList.add('active');
}}

function toggleDetail(sid) {{
  var el = document.getElementById('sd-' + sid);
  var toggle = el && el.previousElementSibling && el.previousElementSibling.querySelector('.sc-toggle');
  if (!el) return;
  var open = el.style.display === 'block';
  el.style.display = open ? 'none' : 'block';
  if (toggle) toggle.innerHTML = open ? '&#9656;' : '&#9662;';
}}

(function() {{
  show('workflow');
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
    generate_indexes()


if __name__ == '__main__':
    main()
