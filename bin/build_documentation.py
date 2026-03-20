#!/usr/bin/env python3
# CommandCenter Operation
# Name: Build Documentation
# Category: maintenance
"""
Build doc/index.html — specification system documentation.

Generates a tabbed single-page site with:
  - Workflow: the spec pipeline commands
  - File Architecture: what goes in a spec directory, linked to templates
  - Scripts: every bin/ script with its purpose
"""
import html as h
import os
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DOC_DIR = PROJECT_DIR / "doc"
BIN_DIR = PROJECT_DIR / "bin"
TEMPLATE_DIR = PROJECT_DIR / "GLOBAL_RULES" / "spec_template"

# ── SVG hero: colored block mosaic ──────────────────────────────────────────

HERO_SVG = '''<svg class="hero-mosaic" viewBox="0 0 800 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="100" height="48" rx="4" fill="#2CB67D" opacity=".18"/>
  <rect x="108" y="0" width="64" height="48" rx="4" fill="#E8A838" opacity=".15"/>
  <rect x="180" y="0" width="88" height="48" rx="4" fill="#7B61FF" opacity=".12"/>
  <rect x="276" y="0" width="52" height="48" rx="4" fill="#FF6B6B" opacity=".14"/>
  <rect x="336" y="0" width="76" height="48" rx="4" fill="#4DA8FF" opacity=".12"/>
  <rect x="420" y="0" width="96" height="48" rx="4" fill="#2CB67D" opacity=".10"/>
  <rect x="524" y="0" width="60" height="48" rx="4" fill="#E8A838" opacity=".12"/>
  <rect x="592" y="0" width="80" height="48" rx="4" fill="#7B61FF" opacity=".10"/>
  <rect x="680" y="0" width="120" height="48" rx="4" fill="#4DA8FF" opacity=".14"/>
  <rect x="0" y="52" width="72" height="48" rx="4" fill="#FF6B6B" opacity=".10"/>
  <rect x="80" y="52" width="108" height="48" rx="4" fill="#4DA8FF" opacity=".12"/>
  <rect x="196" y="52" width="56" height="48" rx="4" fill="#2CB67D" opacity=".15"/>
  <rect x="260" y="52" width="92" height="48" rx="4" fill="#E8A838" opacity=".10"/>
  <rect x="360" y="52" width="68" height="48" rx="4" fill="#7B61FF" opacity=".14"/>
  <rect x="436" y="52" width="84" height="48" rx="4" fill="#FF6B6B" opacity=".12"/>
  <rect x="528" y="52" width="100" height="48" rx="4" fill="#2CB67D" opacity=".12"/>
  <rect x="636" y="52" width="76" height="48" rx="4" fill="#4DA8FF" opacity=".10"/>
  <rect x="720" y="52" width="80" height="48" rx="4" fill="#E8A838" opacity=".14"/>
</svg>'''


# ── SVG icons ────────────────────────────────────────────────────────────────

ICONS = {
    'scaffold': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
    'check': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
    'convert': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>',
    'bolt': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    'test': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
    'doc': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    'clipboard': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="12" y2="17"/></svg>',
    'book': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
    'target': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    'box': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v3"/></svg>',
    'db': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    'monitor': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    'flag': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>',
    'upload': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
    'refresh': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>',
    'terminal': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>',
    'grid': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>',
}


# ── Discover scripts ─────────────────────────────────────────────────────────

def discover_scripts():
    """Read all bin/ scripts and extract name + description from headers."""
    scripts = []
    for ext in ('*.sh', '*.py'):
        for path in sorted(BIN_DIR.glob(ext)):
            name = path.name
            lines = path.read_text(encoding='utf-8', errors='replace').splitlines()[:20]
            # Extract CommandCenter Name or first comment description
            cc_name = ''
            desc = ''
            for line in lines:
                if line.startswith('# Name:'):
                    cc_name = line.split(':', 1)[1].strip()
                elif line.startswith('#') and not cc_name and not line.startswith('#!') \
                        and 'CommandCenter' not in line and 'Category:' not in line:
                    candidate = line.lstrip('# ').strip()
                    if candidate and len(candidate) > 10 and not desc:
                        desc = candidate
                elif line.startswith('"""') and not desc:
                    # Python docstring
                    doc = line.strip('"""').strip()
                    if not doc and len(lines) > lines.index(line) + 1:
                        doc = lines[lines.index(line) + 1].strip()
                    if doc:
                        desc = doc
            if not desc and cc_name:
                desc = cc_name
            if not desc:
                desc = name
            scripts.append((name, cc_name or name.replace('.sh', '').replace('.py', '').replace('_', ' ').title(), desc))
    return scripts


# ── Template links ───────────────────────────────────────────────────────────

def template_href(fname):
    """Return relative href to template file, or empty string if not found."""
    # fname like METADATA.md, ARCHITECTURE.md, SCREEN-Example.md
    tpl = TEMPLATE_DIR / fname
    if tpl.exists():
        return f'../../GLOBAL_RULES/spec_template/{fname}'
    return ''


# ── File architecture data ───────────────────────────────────────────────────

FILE_ARCH = [
    ('METADATA.md', 'clipboard', 'Project identity: name, status, description'),
    ('README.md', 'book', 'One-line project description'),
    ('INTENT.md', 'target', 'Why this project exists, scope boundaries'),
    ('ARCHITECTURE.md', 'box', 'Modules, routes, directory layout'),
    ('DATABASE.md', 'db', 'Tables and columns — delete if no database'),
    ('UI.md', 'monitor', 'Shared UI patterns — delete if no UI'),
    ('SCREEN-{Name}.md', 'monitor', 'Per-screen: route, layout, interactions'),
    ('FEATURE-{Name}.md', 'bolt', 'Cross-cutting behavior: trigger, sequence'),
]

WORKFLOW = [
    ('scaffold', 'bin/create_spec.sh MyProject "description"', 'Scaffold spec directory from templates'),
    ('check', 'bin/validate.sh MyProject', 'Check required files, naming, fields'),
    ('convert', 'bin/convert.sh MyProject > prompt.md', 'Generate expansion prompt for AI'),
    ('bolt', 'bin/build.sh MyProject > prompt.md', 'Tag commit and generate build prompt'),
    ('test', 'bin/test.sh', 'Run unit tests on the specification system'),
]


# ── Build HTML ───────────────────────────────────────────────────────────────

def build_page(scripts):
    # ── Sidebar ──
    sidebar = f'''<nav class="side">
<div class="side-title">Specifications</div>
<div class="side-sub">Documentation</div>
<a class="side-link active" onclick="show('workflow')">Workflow</a>
<a class="side-link" onclick="show('files')">File Architecture</a>
<a class="side-link" onclick="show('scripts')">Scripts</a>
</nav>'''

    # ── Hero ──
    hero = f'''<div class="hero">
{HERO_SVG}
<div class="hero-text">
<h1>Specifications</h1>
<p>Write concise specs. Expand with AI. Build in one shot.</p>
</div>
</div>'''

    # ── Workflow ──
    steps = ''
    for i, (icon_key, cmd, desc) in enumerate(WORKFLOW):
        steps += f'''<div class="wf-row">
<span class="wf-num">{i+1}</span>
<span class="wf-icon">{ICONS[icon_key]}</span>
<code class="wf-cmd">{h.escape(cmd)}</code>
<span class="wf-desc">— {h.escape(desc)}</span>
</div>\n'''

    workflow_section = f'''<section id="workflow">
<h2>Workflow</h2>
<p class="section-intro">Each step has one command. Edit spec files between steps as needed.</p>
<div class="wf-list">{steps}</div>
<div class="wf-note">After a build, iterate: edit specs, re-validate, re-build.
Each build creates an annotated git tag that permanently records the spec state.</div>
</section>'''

    # ── File Architecture ──
    file_cards = ''
    for fname, icon_key, desc in FILE_ARCH:
        icon = ICONS.get(icon_key, '')
        href = template_href(fname)
        # For pattern names like SCREEN-{Name}.md, link to SCREEN-Example.md
        if '{Name}' in fname:
            example = fname.replace('{Name}', 'Example')
            href = template_href(example)
        if href:
            file_cards += f'''<a href="{href}" target="_blank" class="fc">
<div class="fc-icon">{icon}</div>
<div class="fc-body"><div class="fc-name">{h.escape(fname)}</div>
<div class="fc-desc">{h.escape(desc)}</div></div>
</a>\n'''
        else:
            file_cards += f'''<div class="fc">
<div class="fc-icon">{icon}</div>
<div class="fc-body"><div class="fc-name">{h.escape(fname)}</div>
<div class="fc-desc">{h.escape(desc)}</div></div>
</div>\n'''

    files_section = f'''<section id="files" style="display:none">
<h2>File Architecture</h2>
<p class="section-intro"><code>bin/create_spec.sh</code> generates all files from
<a href="../../GLOBAL_RULES/spec_template/" target="_blank">templates</a>.
Spec files end with <code>## Open Questions</code> (except README, METADATA, INTENT).
Names use <code>SCREEN-Name.md</code> / <code>FEATURE-Name.md</code> format.</p>
<div class="fc-grid">{file_cards}</div>
</section>'''

    # ── Scripts ──
    script_rows = ''
    for fname, label, desc in scripts:
        icon = ICONS.get('terminal', '')
        script_rows += f'''<div class="sc-row">
<span class="sc-icon">{icon}</span>
<code class="sc-name">{h.escape(fname)}</code>
<span class="sc-desc">{h.escape(desc)}</span>
</div>\n'''

    scripts_section = f'''<section id="scripts" style="display:none">
<h2>Scripts</h2>
<p class="section-intro">All scripts live in <code>bin/</code>. Spec workflow scripts take a project directory name as the first argument.</p>
<div class="sc-list">{script_rows}</div>
</section>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Specifications</title>
<link rel="stylesheet" type="text/css" href="styles/gem.css">
<style>
body {{ display: flex; height: 100vh; margin: 0; overflow: hidden;
  background: var(--c-bg); color: var(--c-text);
  font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; line-height: 1.6; }}

/* Sidebar */
.side {{ width: 220px; min-width: 220px; background: var(--c-side-bg);
  border-right: 1px solid var(--c-side-border); display: flex; flex-direction: column;
  overflow-y: auto; }}
.side-title {{ color: #fff; font-size: 15px; font-weight: 700; padding: 16px 16px 2px; }}
.side-sub {{ color: var(--c-side-section); font-size: 11px; padding: 0 16px 14px;
  border-bottom: 1px solid var(--c-side-border); }}
.side-link {{ display: block; padding: 8px 16px; font-size: 13.5px;
  color: var(--c-side-link); cursor: pointer; border-left: 3px solid transparent;
  transition: all .1s; text-decoration: none; }}
.side-link:first-of-type {{ margin-top: 12px; }}
.side-link:hover {{ color: #fff; background: rgba(255,255,255,.05); border-left-color: var(--c-accent); }}
.side-link.active {{ color: var(--c-accent); border-left-color: var(--c-accent); }}

/* Content */
main {{ flex: 1; overflow-y: auto; padding: 28px 36px 48px; max-width: 820px; }}

/* Hero */
.hero {{ position: relative; overflow: hidden; background: var(--c-side-bg);
  border: 1px solid var(--c-side-border); border-radius: 10px; margin-bottom: 28px; }}
.hero-mosaic {{ display: block; width: 100%; height: auto; }}
.hero-text {{ padding: 20px 28px 22px; }}
.hero h1 {{ color: #fff; font-size: 26px; margin: 0 0 4px; border: none; }}
.hero p {{ color: var(--c-side-link); font-size: 14px; margin: 0; }}

/* Section */
section h2 {{ font-size: 19px; color: var(--c-h1); font-weight: 700;
  border-bottom: 2px solid var(--c-h1-border); padding-bottom: 5px; margin: 0 0 10px; }}
.section-intro {{ font-size: 13.5px; color: var(--c-h3); margin: 0 0 16px; line-height: 1.55; }}
.section-intro code {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12px;
  background: var(--c-code-bg); color: var(--c-code-text); padding: 1px 5px; border-radius: 3px; }}
.section-intro a {{ color: var(--c-accent); }}

/* Workflow */
.wf-list {{ margin: 0 0 12px; }}
.wf-row {{ display: flex; align-items: center; gap: 10px; padding: 10px 0;
  border-bottom: 1px solid var(--c-td-border); }}
.wf-row:last-child {{ border-bottom: none; }}
.wf-num {{ width: 24px; height: 24px; border-radius: 50%; background: var(--c-accent);
  color: var(--c-side-bg); font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
.wf-icon {{ width: 18px; height: 18px; color: var(--c-h3); flex-shrink: 0; }}
.wf-icon svg {{ width: 100%; height: 100%; }}
.wf-cmd {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12px;
  background: var(--c-code-bg); color: var(--c-code-text);
  padding: 2px 7px; border-radius: 3px; white-space: nowrap; }}
.wf-desc {{ font-size: 13px; color: var(--c-h3); }}
.wf-note {{ font-size: 12.5px; color: var(--c-h3); padding: 8px 12px;
  background: var(--c-callout-bg); border-left: 3px solid var(--c-accent);
  border-radius: 0 4px 4px 0; margin-top: 4px; }}

/* File cards */
.fc-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 8px; }}
.fc {{ display: flex; align-items: flex-start; gap: 10px;
  background: #fff; border: 1px solid var(--c-td-border); border-radius: 6px;
  padding: 10px 12px; transition: border-color .15s; text-decoration: none; color: inherit; }}
.fc:hover {{ border-color: var(--c-accent); }}
a.fc {{ cursor: pointer; }}
.fc-icon {{ width: 18px; height: 18px; color: var(--c-accent); flex-shrink: 0; margin-top: 2px; }}
.fc-icon svg {{ width: 100%; height: 100%; }}
.fc-name {{ font-weight: 700; font-size: 13px; color: var(--c-h1); }}
.fc-desc {{ font-size: 12px; color: var(--c-h3); margin-top: 1px; }}

/* Scripts */
.sc-list {{ margin: 0; }}
.sc-row {{ display: flex; align-items: center; gap: 10px; padding: 8px 0;
  border-bottom: 1px solid var(--c-td-border); }}
.sc-row:last-child {{ border-bottom: none; }}
.sc-icon {{ width: 16px; height: 16px; color: var(--c-h3); flex-shrink: 0; }}
.sc-icon svg {{ width: 100%; height: 100%; }}
.sc-name {{ font-family: 'Cascadia Code', Consolas, monospace; font-size: 12px;
  background: var(--c-code-bg); color: var(--c-code-text);
  padding: 2px 7px; border-radius: 3px; white-space: nowrap; min-width: 180px; }}
.sc-desc {{ font-size: 12.5px; color: var(--c-h3); }}

.footer {{ margin-top: 36px; padding-top: 10px; border-top: 1px solid var(--c-td-border);
  color: var(--c-foot-text); font-size: 12px; text-align: center; }}
</style>
</head>
<body>
{sidebar}
<main>
{hero}
{workflow_section}
{files_section}
{scripts_section}
<div class="footer">Copyright &copy; 2026 Ed Barlow / SQL Technologies.</div>
</main>
<script>
function show(id) {{
  document.querySelectorAll('section').forEach(s => s.style.display = 'none');
  document.getElementById(id).style.display = 'block';
  document.querySelectorAll('.side-link').forEach(a => a.classList.remove('active'));
  document.querySelector('.side-link[onclick*="' + id + '"]').classList.add('active');
}}
</script>
</body>
</html>'''


def main():
    DOC_DIR.mkdir(exist_ok=True)
    scripts = discover_scripts()
    print(f"  Found {len(scripts)} scripts in bin/")
    out_path = DOC_DIR / "index.html"
    out_path.write_text(build_page(scripts), encoding='utf-8')
    print(f"  Wrote {out_path}  ({out_path.stat().st_size // 1024} KB)")


if __name__ == '__main__':
    main()
