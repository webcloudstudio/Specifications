#!/usr/bin/env python3
# CommandCenter Operation
# Name: Build Documentation
# Category: maintenance
"""
Build docs/index.html — single-page documentation for the Prototyper system.
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
DOC_DIR = PROJECT_DIR / "docs"
BIN_DIR = PROJECT_DIR / "bin"

SKIP_DIRS = {
    '__pycache__', '.git', 'venv', 'archive', 'stack', 'bin', 'templates',
    'docs', 'logs', 'data', 'RulesEngine',
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
    'spec_iterate.sh':             'AI-powered spec gap analysis — updates REFERENCE_GAPS.md, writes SPEC_SCORECARD.md (7-dimension quality rating) and SPEC_ITERATION.md (focused prompt targeting 1–2 highest-priority gaps)',
    'summarize_rules.sh': 'Generate prompt to regenerate CLAUDE_RULES.md from BUSINESS_RULES.md',
    'test.sh':                 'Run self-tests on the specification system',
    'build_documentation.py':  'Build this documentation page (docs/index.html)',
    'build_documentation.sh':  'Wrapper — runs build_documentation.py with the slate theme',
    'ProjectValidate.sh':      'Verify a promoted code project against CLAUDE_RULES compliance — shows pass/fail by level',
    'ProjectUpdate.sh':        'Update a promoted project with latest CLAUDE_RULES and templates',
    'decompose.sh':             'Reverse-engineer an existing project into specification files',
    'scorecard.sh':             'Generate SCORECARD.md — specification-to-code alignment checklist',
    'update_reference_gaps.sh': 'Update REFERENCE_GAPS.md from specification vs prototype comparison',
}

GUIDE_ORDER = ['SETUP', 'ONESHOT', 'ITERATE', 'MERGE', 'AUTOMATE', 'ENGINEERING-RULES', 'CREATE-IMAGE', 'SDD-SPECIFICATIONS']
GUIDE_TITLES = {
    'SETUP':                 'Step 1 — Setup',
    'ONESHOT':               'Step 2 — OneShot',
    'ITERATE':               'Step 3 — Iterate',
    'MERGE':                 'Step 4 — Merge',
    'AUTOMATE':              'Step 5 — Automate',
    'ENGINEERING-RULES':     'Engineering Rules',
    'CREATE-IMAGE':          'Create Image',
    'SDD-SPECIFICATIONS':    'SDD — Specifications',
}
RULES_ENGINE_DIR = PROJECT_DIR / "RulesEngine"
GUIDE_EXTRA = {}

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
                 '<meta http-equiv="refresh" content="0; url=docs/index.html">\n'
                 '<title>Prototyper — Redirecting...</title>\n</head>\n<body>\n'
                 '<p>Redirecting to <a href="docs/index.html">Prototyper Documentation</a>...</p>\n'
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

        # Also write into docs/projects/<name>/ so docs/ is fully portable (self-contained)
        portable_html = page_html.replace('../docs/styles/', '../../styles/')
        proj_doc_dir = DOC_DIR / 'projects' / entry.name
        proj_doc_dir.mkdir(parents=True, exist_ok=True)
        (proj_doc_dir / 'index.html').write_text(portable_html, encoding='utf-8')
        print(f'  Generated docs/projects/{entry.name}/index.html (portable copy)')


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

    # ── Sidebar: steps with sub-items ──────────────────────────────────────
    # (guide_key, label, [(sub_label, 'script'|'guide', target), ...])
    STEP_NAV = [
        ('SETUP',    'Step 1 — Setup',    [('setup.sh',             'script', 'setup.sh'),
                                            ('decompose.sh',        'script', 'decompose.sh'),
                                            ('validate.sh',         'script', 'validate.sh'),
                                            ('Create Image',        'guide',  'CREATE-IMAGE')]),
        ('ONESHOT',  'Step 2 — OneShot',  [('oneshot.sh',          'script', 'oneshot.sh'),
                                            ('convert.sh',          'script', 'convert.sh')]),
        ('ITERATE',  'Step 3 — Iterate',  [('iterate.sh',          'script', 'iterate.sh'),
                                            ('tran_logger.sh',      'script', 'tran_logger.sh')]),
        ('MERGE',    'Step 4 — Merge',    [('merge.sh',            'script', 'merge.sh'),
                                            ('ProjectValidate.sh',  'script', 'ProjectValidate.sh'),
                                            ('ProjectUpdate.sh',    'script', 'ProjectUpdate.sh')]),
        ('AUTOMATE', 'Step 5 — Automate', [('spec_iterate.sh',     'script', 'spec_iterate.sh'),
                                            ('scorecard.sh',        'script', 'scorecard.sh')]),
    ]

    # Warn if STEP_NAV references a script not found in bin/ (catches renames)
    scripts_found = {s['file'] for s in scripts}
    for _, _, subs in STEP_NAV:
        for sub_label, sub_type, sub_target in subs:
            if sub_type == 'script' and sub_target not in scripts_found:
                print(f"  WARNING: nav references '{sub_target}' — not found in bin/ (renamed?)")

    step_nav = ''
    for guide_key, label, subs in STEP_NAV:
        step_nav += f'  <a class="sn" data-key="{h.escape(guide_key)}" onclick="showGuide(\'{guide_key}\')">{h.escape(label)}</a>\n'
        for sub_label, sub_type, sub_target in subs:
            if sub_type == 'script':
                step_nav += f'  <a class="sn-sub" data-script="{h.escape(sub_target)}" onclick="showScript(\'{sub_target}\')">{h.escape(sub_label)}</a>\n'
            else:
                step_nav += f'  <a class="sn-sub" data-key="{h.escape(sub_target)}" onclick="showGuide(\'{sub_target}\')">{h.escape(sub_label)}</a>\n'
    step_nav += '  <div class="nav-sep"></div>\n'
    step_nav += f'  <a class="sn" data-key="ENGINEERING-RULES" onclick="showGuide(\'ENGINEERING-RULES\')">Engineering Rules</a>\n'
    step_nav += f'  <a class="sn-sub" data-script="summarize_rules.sh" onclick="showScript(\'summarize_rules.sh\')">summarize_rules.sh</a>\n'
    step_nav += f'  <a class="sn" data-key="SDD-SPECIFICATIONS" onclick="showGuide(\'SDD-SPECIFICATIONS\')">SDD — Specifications</a>\n'

    # ── Sidebar: project links ────────────────────────────────────────────────
    proj_nav = ''
    for p in projects:
        url = f'projects/{p["name"]}/index.html'
        proj_nav += (f'  <a class="sn" data-project="{h.escape(p["name"])}" '
                     f'onclick="showProject(\'{h.escape(p["name"])}\', \'{url}\')">'
                     f'{h.escape(p["display"])}</a>\n')

    workflow_maps_js = (
        'const WORKFLOW_GUIDE_MAP = {\n'
        '  "SETUP": [0],\n'
        '  "ONESHOT": [0],\n'
        '  "ITERATE": [1],\n'
        '  "MERGE": [1],\n'
        '  "AUTOMATE": [3],\n'
        '  "ENGINEERING-RULES": [2],\n'
        '};'
    )

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
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script src="workflows.js"></script>
<script>mermaid.initialize({{ startOnLoad:false, theme:'neutral', flowchart:{{curve:'linear',nodeSpacing:40,rankSpacing:35,padding:16}} }});</script>
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
  line-height: 1.55; color: var(--c-text);
  background: var(--c-bg); }}
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

/* ── Workflow section heading ── */
.wf-section-h {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px;
  color: var(--c-h3); margin: 20px 0 8px; padding-bottom: 3px;
  border-bottom: 1px solid var(--c-td-border); }}
.wf-section-h:first-child {{ margin-top: 0; }}

section h2 {{ font-size: 18px; font-weight: 700; color: var(--c-h1);
  border-bottom: 2px solid var(--c-h1-border); padding-bottom: 4px; margin-bottom: 12px; }}
/* ── Workflow section heading ── (kept for wf-section-h) */
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
    <div id="wf-main"></div>
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
{workflow_maps_js}
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

function renderGuideWorkflows(idxs) {{
  if (!idxs || !idxs.length || !window.WORKFLOWS || !window.renderWorkflowDiagram) return '';
  var parts = idxs.map(function(i) {{
    return window.renderWorkflowDiagram(window.WORKFLOWS[i]);
  }});
  return parts.join('');
}}

function runMermaid(container) {{
  if (window.mermaid) {{
    var nodes = Array.from(container.querySelectorAll('.mermaid:not([data-processed])'));
    if (nodes.length) window.mermaid.run({{ nodes: nodes }});
  }}
}}

function showGuide(key) {{
  var content = GUIDES[key];
  if (!content) return;
  var meta = GUIDES_META[key] || {{}};
  var wfIdxs = WORKFLOW_GUIDE_MAP[key] || [];
  var guideEl = document.getElementById('guide-content');
  var diagramHtml = renderGuideWorkflows(wfIdxs);
  guideEl.innerHTML = diagramHtml + marked.parse(content);
  show('guide');
  clearActive();
  var el = document.querySelector('[data-key="' + key + '"]');
  if (el) el.classList.add('active');
  runMermaid(guideEl);
}}

function esc(t) {{ return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}

// Map script header section names to standard man-page section names
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

  var html = '<div class="sd-man">';

  // Man-page header bar
  html += '<div class="sd-man-header">';
  html += '<span class="sd-man-header-left">' + esc(basename) + '(1)</span>';
  html += '<span class="sd-man-header-right">Prototyper Manual</span>';
  html += '</div>';

  // NAME
  html += '<div class="sd-sec">NAME</div>';
  html += '<div class="sd-body"><span class="sd-name-line">' + esc(file) + '</span>';
  if (desc) html += ' <span class="sd-name-dash">&mdash; ' + esc(desc) + '</span>';
  html += '</div>';

  // SYNOPSIS
  var syn = secs['Usage'] || secs['Synopsis'] || '';
  if (syn) {{
    html += '<div class="sd-sec">SYNOPSIS</div><div class="sd-body">';
    syn.split('\\n').forEach(function(line) {{
      if (line.trim()) html += '<code class="sd-cmd">' + esc(line.trim()) + '</code>';
    }});
    html += '</div>';
  }}

  // DESCRIPTION (combine _desc + any sections mapped to DESCRIPTION)
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

  // Remaining sections in man-page order
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

  // Any unmapped sections
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

  // Man-page footer bar
  html += '<div class="sd-footer">';
  html += '<span>Prototyper</span>';
  html += '<span>bin/' + esc(file) + '</span>';
  html += '</div>';

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
  var wfMain = document.getElementById('wf-main');
  if (wfMain && window.renderAllWorkflows) window.renderAllWorkflows(wfMain);
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
