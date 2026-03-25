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
import re as _re
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DOC_DIR = PROJECT_DIR / "doc"
BIN_DIR = PROJECT_DIR / "bin"

SKIP_DIRS = {
    '__pycache__', '.git', 'venv', 'archive', 'stack', 'bin', 'templates',
    'doc', 'logs', 'data', 'RulesEngine',
}

# Scripts that appear in the sidebar as Workflow Scripts (in this order)
WF_SCRIPTS = ['setup.sh', 'validate.sh', 'oneshot.sh']

# Scripts that appear as indented children of another script in Other Scripts
SCRIPT_CHILDREN = {
    'build_documentation.sh': ['build_documentation.py'],
}

# Human-readable descriptions override auto-detected ones
SCRIPT_DESCRIPTIONS = {
    'setup.sh':                'Scaffold a new Specifications directory from templates (or update existing)',
    'validate.sh':             'Check a Specifications directory for required files, naming, and completeness',
    'convert.sh':              'Generate an AI expansion prompt from concise Specification files — optional intermediate step',
    'oneshot.sh':              'Validate Specifications, detect mode, generate AI build prompt (bootstrap or feature branch)',
    'iterate.sh':              'Generate an iteration prompt from pending CHANGE tickets and new specification files — validates each item before implementation',
    'tran_logger.sh':              'Read the session transaction log, extract bugs and ideas, write to IDEAS.md and ACCEPTANCE_CRITERIA.md',
    'summarize_rules.sh': 'Generate prompt to regenerate CLAUDE_RULES.md from BUSINESS_RULES.md',
    'test.sh':                 'Run self-tests on the specification system',
    'build_documentation.py':  'Build this documentation page (doc/index.html)',
    'build_documentation.sh':  'Wrapper — runs build_documentation.py with the slate theme',
    'ProjectValidate.sh':      'Verify a promoted code project against CLAUDE_RULES compliance — shows pass/fail by level',
    'ProjectUpdate.sh':        'Update a promoted project with latest CLAUDE_RULES and templates',
}

GUIDE_ORDER = ['PROTOTYPE-PROCESS', 'PROJECT-SETUP', 'ITERATION-PROCESS', 'PROMOTE', 'CREATE-IMAGE', 'ENGINEERING-RULES', 'SDD-SPECIFICATIONS', 'FEATURES']
GUIDE_TITLES = {
    'PROTOTYPE-PROCESS':     'Prototype Process Spec',
    'PROJECT-SETUP':         'Project Creation',
    'ITERATION-PROCESS':     'Iteration Process',
    'PROMOTE':               'Step 6 — Promote',
    'CREATE-IMAGE':          'Create Image',
    'ENGINEERING-RULES':     'Engineering Rules Framework',
    'SDD-SPECIFICATIONS':    'SDD — Specifications',
    'FEATURES':              'Features',
}
RULES_ENGINE_DIR = PROJECT_DIR / "RulesEngine"
GUIDE_EXTRA = {
    'PROTOTYPE-PROCESS': RULES_ENGINE_DIR / 'PROTOTYPE_PROCESS.md',
}

# Scripts hidden from the scripts list (generate_*.py are per-project image generators)
SCRIPTS_HIDDEN = set()  # pattern-filtered below: any generate_*.py is hidden


def _parse_script_sections(details):
    """Parse script header comment text into named sections for man page rendering.
    Returns dict with '_desc' for prose before first section header, plus named sections."""
    sections = {}
    cur = '_desc'
    buf = []
    for line in details.splitlines():
        s = line.strip()
        # Section header: Title Case word(s) ending with ':', short, no path chars
        if _re.match(r'^[A-Z][a-zA-Z ]{1,18}:$', s):
            sections[cur] = '\n'.join(buf).strip()
            cur = s[:-1]
            buf = []
        else:
            buf.append(s)
    sections[cur] = '\n'.join(buf).strip()
    return sections


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
                'sections': _parse_script_sections(details),
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
    # Source files are prefixed DOC- to avoid name collisions (e.g. DOC-ENGINEERING-RULES.md)
    found = {f.stem[4:]: f for f in DOC_DIR.glob('DOC-*.md')}
    # Also include spec files from RulesEngine/ registered in GUIDE_EXTRA
    for key, path in GUIDE_EXTRA.items():
        if path.exists():
            found[key] = path
    # Include Features.html
    features_path = DOC_DIR / 'Features.html'
    if features_path.exists():
        found['FEATURES'] = features_path
    guides = []
    for key in GUIDE_ORDER:
        if key in found:
            title = GUIDE_TITLES.get(key, key.replace('-', ' ').replace('_', ' ').title())
            content = found[key].read_text(encoding='utf-8')
            is_html = str(found[key]).endswith('.html')
            guides.append({'key': key, 'title': title, 'content': content, 'is_html': is_html})
    for key, f in sorted(found.items()):
        if key not in GUIDE_ORDER:
            title = GUIDE_TITLES.get(key, key.replace('-', ' ').replace('_', ' ').title())
            content = f.read_text(encoding='utf-8')
            is_html = str(f).endswith('.html')
            guides.append({'key': key, 'title': title, 'content': content, 'is_html': is_html})
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

    template_path = PROJECT_DIR / 'data' / '_project_index_template.html'
    if not template_path.exists():
        print('  Skipping project viewers: data/_project_index_template.html not found')
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

        # Also write into doc/projects/<name>/ so doc/ is fully portable (self-contained)
        portable_html = page_html.replace('../doc/styles/', '../../styles/')
        proj_doc_dir = DOC_DIR / 'projects' / entry.name
        proj_doc_dir.mkdir(parents=True, exist_ok=True)
        (proj_doc_dir / 'index.html').write_text(portable_html, encoding='utf-8')
        print(f'  Generated doc/projects/{entry.name}/index.html (portable copy)')


# ── Build HTML ────────────────────────────────────────────────────────────────

def build_page(scripts, projects, guides):

    # ── Guide JS data ──────────────────────────────────────────────────────────
    guides_js = 'const GUIDES = {\n'
    guides_meta_js = 'const GUIDES_META = {\n'
    for g in guides:
        guides_js += f'  {json.dumps(g["key"])}: {json.dumps(g["content"])},\n'
        guides_meta_js += f'  {json.dumps(g["key"])}: {json.dumps({"title": g["title"], "is_html": g.get("is_html", False)})},\n'
    guides_js += '};'
    guides_meta_js += '};'

    # ── Script JS data ─────────────────────────────────────────────────────────
    scripts_js = 'const SCRIPTS = {\n'
    for s in scripts:
        scripts_js += f'  {json.dumps(s["file"])}: {json.dumps({"desc": s["desc"], "sections": s.get("sections", {})})},\n'
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
        (1, 'Step 1 — Setup',    [('setup.sh',             'script', 'setup.sh'),
                                   ('Create Image (AI)',   'guide',  'CREATE-IMAGE')]),
        (2, 'Step 2 — Create',   [('Project Creation',    'guide',  'PROJECT-SETUP')]),
        (3, 'Step 3 — Validate', [('validate.sh',       'script', 'validate.sh')]),
        (4, 'Step 4 — OneShot',  [('oneshot.sh',        'script', 'oneshot.sh')]),
    ]

    # Warn if STEP_NAV references a script not found in bin/ (catches renames)
    scripts_found = {s['file'] for s in scripts}
    for _, _, subs in STEP_NAV:
        for sub_label, sub_type, sub_target in subs:
            if sub_type == 'script' and sub_target not in scripts_found:
                print(f"  WARNING: nav references '{sub_target}' — not found in bin/ (renamed?)")

    step_nav = ''
    for num, label, subs in STEP_NAV:
        step_nav += f'  <a class="sn" data-step="{num}" onclick="showGuideStep(\'PROTOTYPE-PROCESS\', {num})">{h.escape(label)}</a>\n'
        for sub_label, sub_type, sub_target in subs:
            if sub_type == 'script':
                step_nav += f'  <a class="sn-sub" data-script="{h.escape(sub_target)}" onclick="showScript(\'{sub_target}\')">{h.escape(sub_label)}</a>\n'
            else:
                step_nav += f'  <a class="sn-sub" data-key="{h.escape(sub_target)}" onclick="showGuide(\'{sub_target}\')">{h.escape(sub_label)}</a>\n'
    step_nav += f'  <a class="sn" data-key="ITERATION-PROCESS" onclick="showGuide(\'ITERATION-PROCESS\')">Step 5 — Iterate</a>\n'
    step_nav += f'  <a class="sn-sub" data-script="iterate.sh" onclick="showScript(\'iterate.sh\')">iterate.sh</a>\n'
    step_nav += f'  <a class="sn-sub" data-script="tran_logger.sh" onclick="showScript(\'tran_logger.sh\')">tran_logger.sh</a>\n'
    step_nav += f'  <a class="sn" data-step="6" onclick="showGuideStep(\'PROTOTYPE-PROCESS\', 6)">Step 6 — Promote</a>\n'
    step_nav += f'  <a class="sn-sub" data-key="PROMOTE" onclick="showGuide(\'PROMOTE\')">Promote / Merge</a>\n'
    step_nav += f'  <a class="sn-sub" data-script="ProjectValidate.sh" onclick="showScript(\'ProjectValidate.sh\')">ProjectValidate.sh</a>\n'
    step_nav += f'  <a class="sn-sub" data-script="ProjectUpdate.sh" onclick="showScript(\'ProjectUpdate.sh\')">ProjectUpdate.sh</a>\n'
    step_nav += '  <div class="nav-sep"></div>\n'
    step_nav += f'  <a class="sn" data-key="ENGINEERING-RULES" onclick="showGuide(\'ENGINEERING-RULES\')">Engineering Rules</a>\n'
    step_nav += f'  <a class="sn-sub" data-script="summarize_rules.sh" onclick="showScript(\'summarize_rules.sh\')">summarize_rules.sh</a>\n'
    step_nav += f'  <a class="sn-sub" data-key="FEATURES" onclick="showGuide(\'FEATURES\')">Features</a>\n'
    step_nav += f'  <a class="sn" data-key="SDD-SPECIFICATIONS" onclick="showGuide(\'SDD-SPECIFICATIONS\')">SDD — Specifications</a>\n'

    # ── Sidebar: project links ────────────────────────────────────────────────
    proj_nav = ''
    for p in projects:
        url = f'projects/{p["name"]}/index.html'
        proj_nav += (f'  <a class="sn" data-project="{h.escape(p["name"])}" '
                     f'onclick="showProject(\'{h.escape(p["name"])}\', \'{url}\')">'
                     f'{h.escape(p["display"])}</a>\n')

    # ── Two-row workflow diagram ───────────────────────────────────────────────
    def wf_box(label, script='', path='', terminal=False, ai=False, extra_label='', feature=''):
        cls = 'wf-box'
        if terminal: cls += ' wf-terminal'
        if ai:       cls += ' wf-ai'
        inner = f'<span class="wf-label">{h.escape(label)}</span>'
        if extra_label:
            inner += f'<span class="wf-label">{h.escape(extra_label)}</span>'
        if feature:
            inner += f'<span class="wf-script">Feature: {h.escape(feature)}</span>'
        if script:
            inner += f'<span class="wf-script">{h.escape(script)}</span>'
        if path:
            inner += f'<span class="wf-path">{h.escape(path)}</span>'
        return f'<div class="{cls}">{inner}</div>'

    ARR = '<span class="wf-arr">&#8594;</span>'

    AND = '<span style="color:#1E2328;font-weight:700;padding:0 8px;align-self:center;font-size:12px">and</span>'

    row1 = ARR.join([
        wf_box('Setup', 'setup.sh'),
        wf_box('Specifications', '', 'Specifications/<PROJECT>/', terminal=True),
        wf_box('Validate', 'validate.sh'),
        wf_box('OneShot', 'oneshot.sh'),
        wf_box('PROTOTYPE', feature='<name>', path='doc/SCORECARD.md', terminal=True),
    ])
    row2 = ARR.join([
        wf_box('PROTOTYPE', feature='<name>', path='doc/SCORECARD.md', terminal=True),
        wf_box('Iterate', 'iterate.sh'),
        wf_box('PROTOTYPE', feature='<name>', path='doc/SCORECARD.md', terminal=True),
        wf_box('Promote'),
        wf_box('Project', '', '../<PROJECT>', terminal=True),
    ])
    row_rules = ARR.join([
        wf_box('BUSINESS_RULES.md', '', 'RulesEngine/', terminal=True),
        wf_box('summarize_rules.sh', 'bin/summarize_rules.sh'),
        wf_box('CLAUDE_RULES.md', '', 'RulesEngine/', terminal=True),
        wf_box('ProjectUpdate.sh', 'ProjectUpdate.sh'),
        wf_box('Project', '', '../<PROJECT>', terminal=True),
        wf_box('ProjectValidate.sh', 'bin/ProjectValidate.sh'),
        wf_box('Project KPIs', terminal=True),
    ])

    iter_r1 = (wf_box('Specifications', '', 'Specifications/<PROJECT>/', terminal=True) + ARR +
               wf_box('oneshot.sh', 'bin/oneshot.sh <PROJECT>') + ARR +
               wf_box('PROTOTYPE', feature='<name>', path='doc/SCORECARD.md', terminal=True))
    iter_r2 = (wf_box('Edit spec files', '', 'Specifications/<PROJECT>/', terminal=True) + ARR +
               wf_box('iterate.sh', 'bin/iterate.sh <PROJECT>') + ARR +
               wf_box('PROTOTYPE', feature='<name>', terminal=True))

    wf_diagram = (f'<div class="wf-diagram">'
                  f'<p class="wf-section-h" style="margin:0 0 4px">Oneshot Rules</p>'
                  f'<div class="wf-row">{row1}</div>'
                  f'<div class="wf-row">{row2}</div>'
                  f'<p class="wf-section-h" style="margin:10px 0 4px">Business Rules</p>'
                  f'<div class="wf-row">{row_rules}</div>'
                  f'</div>')

    eng_row = ARR.join([
        wf_box('BUSINESS_RULES.md', '', 'RulesEngine/', terminal=True),
        wf_box('summarize_rules.sh', 'bin/summarize_rules.sh'),
        wf_box('CLAUDE_RULES.md', '', 'RulesEngine/', terminal=True),
    ])
    eng_diagram = (f'<div class="wf-diagram" style="margin-bottom:22px">'
                   f'<div class="wf-row">{eng_row}</div>'
                   f'</div>')

    iter_diagram = (f'<div class="wf-diagram" style="margin-bottom:22px">'
                    f'<div class="wf-row">{iter_r1}</div>'
                    f'<div class="wf-row">{iter_r2}</div>'
                    f'</div>')

    guide_diagrams_js = (f'const GUIDE_DIAGRAMS = {{\n'
                         f'  "ENGINEERING-RULES": {json.dumps(eng_diagram)},\n'
                         f'  "ITERATION-PROCESS": {json.dumps(iter_diagram)},\n'
                         f'}};')

    # ── Workflow steps table (Prototyper steps only) ───────────────────────────
    wf_step_data = [
        (1, 'bin/setup.sh &lt;Project&gt;', 'Scaffold Specifications directory from templates'),
        (2, 'bin/validate.sh &lt;Project&gt;', 'Check Specification files, naming, fields'),
        (3, 'bin/oneshot.sh &lt;Project&gt; &gt; prompt.md', 'Validate + detect mode + generate build prompt'),
    ]
    wf_rows = ''
    for n, cmd, desc in wf_step_data:
        wf_rows += f'<tr><td class="wn">{n}</td><td class="wcmd"><code>{cmd}</code></td><td class="wdesc">{desc}</td></tr>\n'

    # ── Other scripts (with child support) ───────────────────────────────────
    all_children = {c for kids in SCRIPT_CHILDREN.values() for c in kids}
    scripts_by_file = {s['file']: s for s in scripts}

    def sc_entry(s, child=False):
        detail = f'<div class="sc-detail-open"><pre>{h.escape(s["details"])}</pre></div>' if s.get('details') else ''
        extra = ' sc-child' if child else ''
        return (f'<div class="sc-entry{extra}"><div class="sc-head">'
                f'<code class="sc-name">{h.escape(s["file"])}</code>'
                f'<span class="sc-desc">{h.escape(s["desc"])}</span></div>{detail}</div>\n')

    other_parts = []
    for s in other_scripts:
        if s['file'] in all_children or s['file'] in SCRIPTS_HIDDEN or (s['file'].startswith('generate_') and s['file'].endswith('.py')):
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
<link rel="stylesheet" href="styles/spec.css">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{ display: flex; height: 100vh; overflow: hidden;
  background: var(--c-bg); color: var(--c-text);
  font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif; font-size: 14px; line-height: 1.65; }}

/* ── Sidebar — invariant ── */
.sidebar {{ width: 220px; min-width: 220px; display: flex; flex-direction: column;
  background: var(--c-side-bg); border-right: 1px solid var(--c-side-border);
  overflow-y: auto; flex-shrink: 0; }}

.sidebar-header {{ background: var(--c-topbar-bg); padding: 6px 10px;
  flex-shrink: 0; cursor: pointer; display: flex; align-items: center; gap: 9px; }}
.sidebar-header:hover {{ opacity: .88; }}
.sidebar-header img {{ width: 100px; height: 75px; object-fit: contain; display: block;
  flex-shrink: 0; border-radius: 3px; }}
.sidebar-header h1 {{ color: #fff; font-size: 15px; font-weight: 700; line-height: 1.2;
  letter-spacing: .4px; }}

.nav-section {{ font-size: 9px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; color: var(--c-side-section); padding: 10px 16px 3px; }}
.nav-sep {{ border-top: 1px solid var(--c-side-border); margin: 5px 0; }}

/* Primary nav items */
.sn {{ display: block; padding: 3px 16px;
  font-size: 13px; font-family: 'Segoe UI', 'Trebuchet MS', Arial, sans-serif;
  color: #fff; cursor: pointer; border-left: 3px solid transparent;
  text-decoration: none; transition: background .1s, border-color .1s;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.sn:hover {{ background: rgba(255,255,255,.07); border-left-color: var(--c-accent); }}
.sn.active {{ color: #fff; border-left-color: var(--c-accent); background: rgba(44,182,125,.12); }}

/* Sub-nav items (steps under Workflow) */
.sn-sub {{ display: block; padding: 2px 16px 2px 28px;
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
.wf-diagram {{ display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }}
.wf-row {{ display: flex; align-items: stretch; flex-wrap: nowrap; gap: 8px; }}
.wf-row-r {{ display: flex; align-items: center; flex-wrap: nowrap; gap: 8px; justify-content: flex-end; }}
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
.wf-arr {{ color: var(--c-accent); padding: 0 6px; font-size: 22px; font-weight: 700; align-self: center;
  display: inline-block; line-height: 1; }}
.wf-ai {{ border-style: dashed; border-color: #d4a017; background: #2a2000; }}
.wf-ai {{ border-style: dashed; border-color: #d4a017; background: #2a2000; }}

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
.sd-man {{ max-width: 700px; padding: 2px 0; }}
.sd-sec {{ font-size: 10.5px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;
  color: var(--c-accent); margin: 20px 0 6px; }}
.sd-sec:first-child {{ margin-top: 0; }}
.sd-body {{ padding-left: 22px; }}
.sd-name-line {{ font-size: 15px; font-weight: 700; color: var(--c-h1);
  font-family: 'Cascadia Code', Consolas, monospace; }}
.sd-name-dash {{ font-size: 14px; color: var(--c-h3); font-family: 'Segoe UI', Arial, sans-serif; font-weight: 400; }}
.sd-body p {{ margin: 0 0 7px; color: var(--c-text); font-size: 13px; line-height: 1.65;
  font-family: 'Segoe UI', Arial, sans-serif; }}
.sd-cmd {{ display: block; font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px;
  color: var(--c-pre-text); background: var(--c-pre-bg); padding: 5px 12px; border-radius: 3px;
  margin: 4px 0; border: 1px solid var(--c-side-border); }}
.sd-item {{ font-size: 12.5px; color: var(--c-text); padding: 2px 0;
  font-family: 'Cascadia Code', Consolas, monospace; }}
.sd-empty {{ font-size: 13px; color: var(--c-h3); font-style: italic; }}

/* ── Scripts (expandable, for Other Scripts section) ── */
.sc-section-h {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px;
  color: var(--c-h3); margin: 22px 0 6px; padding-bottom: 3px;
  border-bottom: 1px solid var(--c-td-border); }}
.sc-group {{ margin-bottom: 6px; }}
.sc-entry {{ border-bottom: 1px solid var(--c-td-border); }}
.sc-entry:last-child {{ border-bottom: none; }}
.sc-child {{ padding-left: 16px; background: rgba(255,255,255,.02); }}
.sc-head {{ display: flex; align-items: baseline; gap: 10px; padding: 5px 4px; }}
.sc-name {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px;
  color: var(--c-code-text); background: var(--c-code-bg); padding: 1px 5px;
  border-radius: 3px; white-space: nowrap; flex-shrink: 0; }}
.sc-desc {{ font-size: 12.5px; color: var(--c-h3); }}
.sc-detail-open {{ margin: 0 0 6px 0; }}
.sc-detail pre, .sc-detail-open pre {{ background: #F0EFEA; color: #2E3640; font-size: 12px;
  font-family: 'Cascadia Code', Consolas, monospace; padding: 8px 12px;
  border-radius: 4px; line-height: 1.5; white-space: pre; overflow-x: auto;
  border: 1px solid var(--c-td-border); }}

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
/* ── Process definitions ── */
.proc-defs {{ margin-bottom: 4px; }}
.proc-item {{ display: flex; gap: 12px; padding: 3px 0; border-bottom: 1px solid var(--c-td-border); align-items: baseline; }}
.proc-item:last-child {{ border-bottom: none; }}
.proc-term {{ font-size: 12px; font-weight: 700; color: #1E2328; white-space: nowrap; min-width: 110px; }}
.proc-def {{ font-size: 12.5px; color: var(--c-h3); }}
.proc-def code {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 11.5px;
  background: var(--c-code-bg); color: var(--c-code-text); padding: 1px 4px; border-radius: 3px; }}
/* ── Documentation guide list ── */
.doc-guide-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; margin-bottom: 14px; }}
.doc-guide-card {{ background: var(--c-side-bg); border: 1px solid var(--c-side-border); border-radius: 5px;
  padding: 12px 14px; cursor: pointer; transition: background .2s, border-color .2s; }}
.doc-guide-card:hover {{ background: rgba(255,255,255,.08); border-color: var(--c-accent); }}
.doc-guide-card-title {{ font-size: 13px; font-weight: 700; color: #fff; margin: 0 0 3px; }}
.doc-guide-card-desc {{ font-size: 11px; color: rgba(255,255,255,.7); }}
/* ── HTML content wrapper (for Features.html, etc.) ── */
#guide-content.html-content {{ background: #FAFBFC; color: #1B2434; padding: 20px; border-radius: 4px; }}
#guide-content.html-content * {{ box-sizing: border-box; }}
#guide-content.html-content body {{ height: auto !important; display: block !important; flex: none !important; padding: 0 !important; margin: 0 !important; max-width: none !important; }}
</style>
</head>
<body>

<nav class="sidebar">
  <div class="sidebar-header" onclick="show('workflow')">
    <img src="images/prototyper.webp" alt="Prototyper">
    <h1>Project<br>Prototyper</h1>
  </div>
{step_nav}
  <div class="nav-sep"></div>
  <div class="nav-section">Current Projects</div>
{proj_nav}
</nav>

<main>

  <!-- ── Workflow ──────────────────────────── -->
  <div id="workflow" class="content-section">
    {wf_diagram}

    <hr style="border:none;border-top:1px solid var(--c-td-border);margin:18px 0 14px;">
    <p class="wf-section-h">Dictionary</p>
    <div class="proc-defs">
      <div class="proc-item"><span class="proc-term">Specification</span><span class="proc-def">Markdown files in <code>Specifications/&lt;Name&gt;/</code> — concise tables and bullets defining what to build</span></div>
      <div class="proc-item"><span class="proc-term">Project</span><span class="proc-def">A live git repository with <code>METADATA.md</code>, conforming to platform standards, discovered by Prototyper</span></div>
      <div class="proc-item"><span class="proc-term">Prototype</span><span class="proc-def">A directory built by AI from the Specification — runnable and testable, iterated before merge</span></div>
      <div class="proc-item"><span class="proc-term">Feature Branch</span><span class="proc-def">Configured in <code>.env</code> as <code>BUILD_FEATURE_BRANCH_NAME=feature/name</code> — contains AI-built code pending merge</span></div>
      <div class="proc-item"><span class="proc-term">Build</span><span class="proc-def">Clones or fetches the project, creates the Feature Branch from base code, generates the AI build prompt</span></div>
      <div class="proc-item"><span class="proc-term">Merge</span><span class="proc-def">Squash-merges the Feature Branch into the base branch — triggered via Prototyper UI, hides all git from the user</span></div>
    </div>
  </div>

  <!-- ── Guide viewer ──────────────────────────── -->
  <div id="guide" class="content-section">
    <div id="guide-content" class="md"></div>
  </div>

  <!-- ── Script man page ───────────────────────── -->
  <div id="script-detail" class="content-section">
    <div id="sd-content"></div>
  </div>

  <!-- ── Project viewer (iframe) ───────────────── -->
  <div id="project" class="content-section">
    <iframe id="project-frame" src="" title="Project viewer"></iframe>
  </div>

</main>

<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
{guides_js}
{guides_meta_js}
{guide_diagrams_js}
{scripts_js}

marked.setOptions({{ gfm: true, breaks: false }});

// ── Initialize documentation guide list on page load ──
function initGuideList() {{
  var container = document.querySelector('.doc-guide-list');
  if (!container) return;
  // All guides are now in sidebar navigation, so Documentation section is empty
  // This function is kept for future reference docs
}}

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
  var meta = GUIDES_META[key] || {{}};
  var diagram = GUIDE_DIAGRAMS[key] || '';
  var guideEl = document.getElementById('guide-content');
  var htmlContent;
  if (meta.is_html) {{
    // HTML content (e.g., Features.html) — extract body and wrap
    var parser = new DOMParser();
    var doc = parser.parseFromString(content, 'text/html');
    var bodyContent = doc.body.innerHTML;
    htmlContent = diagram + bodyContent;
    guideEl.classList.add('html-content');
  }} else {{
    // Markdown content — parse and render
    htmlContent = diagram + marked.parse(content);
    guideEl.classList.remove('html-content');
  }}
  guideEl.innerHTML = htmlContent;
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

function esc(t) {{ return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}

function showScript(file) {{
  var s = SCRIPTS[file] || {{}};
  var desc = s.desc || '';
  var secs = s.sections || {{}};

  var html = '<div class="sd-man">';

  // NAME
  html += '<div class="sd-sec">Name</div>';
  html += '<div class="sd-body"><span class="sd-name-line">' + esc(file) + '</span>';
  if (desc) html += '<span class="sd-name-dash"> &mdash; ' + esc(desc) + '</span>';
  html += '</div>';

  // SYNOPSIS
  var syn = secs['Usage'] || secs['Synopsis'] || '';
  if (syn) {{
    html += '<div class="sd-sec">Synopsis</div><div class="sd-body">';
    syn.split('\\n').forEach(function(line) {{
      if (line.trim()) html += '<code class="sd-cmd">' + esc(line.trim()) + '</code>';
    }});
    html += '</div>';
  }}

  // DESCRIPTION
  var body = secs['_desc'] || '';
  if (body) {{
    html += '<div class="sd-sec">Description</div><div class="sd-body">';
    body.split('\\n\\n').forEach(function(para) {{
      var t = para.trim().replace(/\\n/g, ' ');
      if (t) html += '<p>' + esc(t) + '</p>';
    }});
    html += '</div>';
  }}

  // Additional sections (Writes, Options, Modes, Examples, etc.)
  var skip = {{'_desc':1,'Usage':1,'Synopsis':1}};
  var codeKeys = {{'Examples':1}};
  Object.keys(secs).forEach(function(key) {{
    if (skip[key] || !secs[key].trim()) return;
    html += '<div class="sd-sec">' + esc(key) + '</div><div class="sd-body">';
    secs[key].split('\\n').forEach(function(line) {{
      if (line.trim()) {{
        if (codeKeys[key]) html += '<code class="sd-cmd">' + esc(line.trim()) + '</code>';
        else html += '<div class="sd-item">' + esc(line.trim()) + '</div>';
      }}
    }});
    html += '</div>';
  }});

  if (!desc && !syn && !body) html += '<div class="sd-empty">(no documentation available)</div>';
  html += '</div>';

  document.getElementById('sd-content').innerHTML = html;
  show('script-detail');
  clearActive();
  var el = document.querySelector('[data-script="' + file + '"]');
  if (el) el.classList.add('active');
}}

function showProject(name, url) {{
  var frame = document.getElementById('project-frame');
  if (!frame.src || !frame.src.endsWith(url)) frame.src = url;
  show('project');
  clearActive();
  var el = document.querySelector('[data-project="' + name + '"]');
  if (el) el.classList.add('active');
}}

(function() {{
  initGuideList();
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
