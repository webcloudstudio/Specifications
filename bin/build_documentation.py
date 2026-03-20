#!/usr/bin/env python3
"""
Build doc/index.html — polished single-page documentation for the Specifications repo.
"""
import html as h
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DOC_DIR = PROJECT_DIR / "doc"

SKIP_DIRS = {'archive', 'bin', 'doc', 'GLOBAL_RULES', 'logs', 'venv', '__pycache__', '.git'}

STATUS_COLORS = {
    'IDEA': '#94a3b8', 'PROTOTYPE': '#fdab3d', 'ACTIVE': '#0073ea',
    'PRODUCTION': '#00c875', 'ARCHIVED': '#4a5568',
}

# ── SVG graphics ─────────────────────────────────────────────────────────────

HERO_SVG = '''<svg class="hero-bg" viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="hg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="var(--c-accent)" stop-opacity=".12"/>
      <stop offset="100%" stop-color="var(--c-accent)" stop-opacity=".03"/>
    </linearGradient>
  </defs>
  <rect width="800" height="200" fill="url(#hg)"/>
  <circle cx="680" cy="40" r="80" fill="var(--c-accent)" opacity=".06"/>
  <circle cx="740" cy="120" r="50" fill="var(--c-accent)" opacity=".04"/>
  <circle cx="60" cy="160" r="60" fill="var(--c-accent)" opacity=".05"/>
  <path d="M0 180 Q200 140 400 160 T800 130 L800 200 L0 200Z" fill="var(--c-accent)" opacity=".04"/>
</svg>'''

STEP_ICONS = [
    # 1: scaffold
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
    # 2: edit
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
    # 3: validate
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
    # 4: convert
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>',
    # 5: build
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    # 6: promote
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>',
]

FILE_ICONS = {
    'METADATA': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="12" y2="17"/></svg>',
    'README': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
    'INTENT': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    'ARCHITECTURE': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v3"/><line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/></svg>',
    'DATABASE': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    'UI': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    'SCREEN': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    'FEATURE': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
}


# ── Discovery ────────────────────────────────────────────────────────────────

def read_meta(path):
    fields = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
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
        meta = entry / "METADATA.md"
        if not meta.exists():
            continue
        fields = read_meta(meta)
        if fields.get('type', '').lower() in ('build', 'build-artifact'):
            continue
        md_files = sorted(
            [f.name for f in entry.iterdir()
             if f.suffix == '.md' and not f.name.startswith('PROPOSED') and not f.name.startswith('UNUSED')],
            key=lambda n: (0 if n == 'METADATA.md' else 1, n)
        )
        if md_files:
            projects.append((entry.name, fields.get('display_name', entry.name),
                             fields.get('status', ''), fields.get('short_description', ''),
                             fields.get('stack', ''), md_files))
    return projects


# ── HTML generation ──────────────────────────────────────────────────────────

def file_icon(fname):
    name = fname.replace('.md', '')
    if name.startswith('SCREEN-'): return FILE_ICONS['SCREEN']
    if name.startswith('FEATURE-'): return FILE_ICONS['FEATURE']
    return FILE_ICONS.get(name, FILE_ICONS['README'])


def file_label(fname):
    name = fname.replace('.md', '')
    if name.startswith('SCREEN-'): return 'Screen: ' + name[7:]
    if name.startswith('FEATURE-'): return 'Feature: ' + name[8:]
    return {'METADATA': 'Metadata', 'README': 'Overview', 'INTENT': 'Intent',
            'ARCHITECTURE': 'Architecture', 'DATABASE': 'Database', 'UI': 'UI Standards',
            }.get(name, name.replace('_', ' ').replace('-', ' ').title())


WORKFLOW_STEPS = [
    ("Create", "bin/create_spec.sh MyProject", "Scaffolds a spec directory with all template files"),
    ("Edit", "Edit files in MyProject/", "Fill in INTENT, ARCHITECTURE, add SCREEN and FEATURE files"),
    ("Validate", "bin/validate.sh MyProject", "Checks required files, naming, fields. Exit 0 = ready"),
    ("Convert", "bin/convert.sh MyProject", "Generates expansion prompt for AI agent"),
    ("Build", "bin/build.sh MyProject", "Tags commit, generates complete build prompt"),
    ("Promote", "Copy to own repo", "Spec directory becomes the project's documentation"),
]

FILE_REF = [
    ("Required", [
        ("METADATA.md", "Project identity: name, status, description"),
        ("README.md", "One-line project description"),
        ("INTENT.md", "Why this project exists, scope boundaries"),
        ("ARCHITECTURE.md", "Modules, routes, directory layout"),
    ]),
    ("Conditional", [
        ("DATABASE.md", "Tables and columns (if project has a DB)"),
        ("UI.md", "Shared UI patterns (if project has a UI)"),
        ("SCREEN-{Name}.md", "Per-screen: route, layout, interactions"),
        ("FEATURE-{Name}.md", "Cross-cutting behavior: trigger, sequence"),
    ]),
]


def build_page(projects):
    # ── Sidebar ──
    sidebar = f'''<nav class="gem-sidebar-panel">
<div class="gem-toc-title">Specifications</div>
<div class="gem-toc-subtitle">Spec-Driven Build System</div>
<div class="gem-toc-section">Documentation</div>
<a href="#workflow">Workflow</a>
<a href="#files">File Reference</a>
<a href="#conventions">Conventions</a>
{"".join(f'<div class="gem-toc-section">Projects</div>' + "".join(f'<a href="../{h.escape(slug)}/index.html">{h.escape(display)}</a>' for slug, display, *_ in projects) if projects else "")}
</nav>'''

    # ── Hero banner ──
    hero = f'''<div class="hero">
{HERO_SVG}
<div class="hero-content">
<h1>Specifications</h1>
<p>Write concise markdown specs. Expand them with AI.<br>Build the application in one shot.</p>
</div>
</div>'''

    # ── Workflow steps ──
    steps_html = '<section id="workflow"><h2>Workflow</h2>\n<div class="steps">\n'
    for i, (label, cmd, desc) in enumerate(WORKFLOW_STEPS):
        icon = STEP_ICONS[i] if i < len(STEP_ICONS) else ''
        steps_html += f'''<div class="step">
<div class="step-num">{i+1}</div>
<div class="step-icon">{icon}</div>
<div class="step-body">
<div class="step-label">{h.escape(label)}</div>
<code class="step-cmd">{h.escape(cmd)}</code>
<div class="step-desc">{h.escape(desc)}</div>
</div>
</div>\n'''
    steps_html += '</div>\n'
    steps_html += '<p class="step-note">After a build, iterate: edit specs &rarr; validate &rarr; build. '
    steps_html += 'Each build creates an annotated git tag that permanently records the spec state.</p>\n'
    steps_html += '</section>'

    # ── File reference ──
    files_html = '<section id="files"><h2>File Reference</h2>\n'
    for group_label, files in FILE_REF:
        files_html += f'<div class="file-group-label">{h.escape(group_label)}</div>\n'
        files_html += '<div class="file-grid">\n'
        for fname, fdesc in files:
            icon = file_icon(fname)
            files_html += f'''<div class="file-card">
<div class="file-card-icon">{icon}</div>
<div class="file-card-body">
<div class="file-card-name">{h.escape(fname)}</div>
<div class="file-card-desc">{h.escape(fdesc)}</div>
</div>
</div>\n'''
        files_html += '</div>\n'
    files_html += '</section>'

    # ── Conventions ──
    conv_html = '''<section id="conventions"><h2>Conventions</h2>
<div class="conv-grid">
<div class="conv-item">
<div class="conv-title">Open Questions</div>
<div class="conv-body">All spec files except README, METADATA, INTENT end with <code>## Open Questions</code></div>
</div>
<div class="conv-item">
<div class="conv-title">Naming</div>
<div class="conv-body">Uppercase with hyphens: <code>SCREEN-Dashboard.md</code>, <code>FEATURE-Scan.md</code></div>
</div>
<div class="conv-item">
<div class="conv-title">Concise Specs</div>
<div class="conv-body">Write tables and bullets. CONVERT.md rules expand them during conversion.</div>
</div>
<div class="conv-item">
<div class="conv-title">Stack Patterns</div>
<div class="conv-body"><code>GLOBAL_RULES/stack/</code> has technology patterns &mdash; don&rsquo;t repeat in specs.</div>
</div>
</div>
</section>'''

    # ── Projects ──
    proj_html = ''
    if projects:
        proj_html = '<section id="projects"><h2>Projects</h2>\n<div class="proj-grid">\n'
        for slug, display, status, desc, stack, md_files in projects:
            color = STATUS_COLORS.get(status, '#94a3b8')
            badge = f'<span class="proj-status" style="background:{color}">{h.escape(status)}</span>' if status else ''
            stack_html = f'<div class="proj-stack">{h.escape(stack)}</div>' if stack else ''
            pills = ' '.join(f'<span class="file-pill">{h.escape(file_label(f))}</span>' for f in md_files)
            proj_html += f'''<a href="../{h.escape(slug)}/index.html" class="proj-card">
<div class="proj-header"><span class="proj-name">{h.escape(display)}</span>{badge}</div>
<div class="proj-desc">{h.escape(desc)}</div>
{stack_html}
<div class="proj-files">{pills}</div>
</a>\n'''
        proj_html += '</div>\n</section>'

    # ── Footer ──
    footer = '<div class="gem-page-footer">Copyright &copy; 2026 Ed Barlow / SQL Technologies. All rights reserved.</div>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Specifications</title>
<link rel="stylesheet" type="text/css" href="styles/gem.css">
<style>
/* ── Hero ───────────────────────────── */
.hero {{
  position: relative; overflow: hidden;
  background: var(--c-side-bg); border: 1px solid var(--c-side-border);
  border-radius: 10px; margin-bottom: 32px;
}}
.hero-bg {{
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none;
}}
.hero-content {{
  position: relative; padding: 36px 32px 30px;
}}
.hero h1 {{
  color: #fff; font-size: 28px; margin: 0 0 8px; border: none;
  font-family: 'Segoe UI', Arial, sans-serif;
}}
.hero p {{
  color: var(--c-side-link); font-size: 15px; line-height: 1.6; margin: 0;
}}

/* ── Workflow steps ──────────────────── */
.steps {{ display: flex; flex-direction: column; gap: 0; margin: 16px 0; }}
.step {{
  display: flex; align-items: flex-start; gap: 14px;
  padding: 14px 0; border-bottom: 1px solid var(--c-td-border);
}}
.step:last-child {{ border-bottom: none; }}
.step-num {{
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--c-accent); color: var(--c-side-bg);
  font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 2px;
}}
.step-icon {{
  width: 22px; height: 22px; color: var(--c-h3); flex-shrink: 0; margin-top: 3px;
}}
.step-icon svg {{ width: 100%; height: 100%; }}
.step-body {{ flex: 1; }}
.step-label {{ font-weight: 700; color: var(--c-h1); font-size: 14px; margin-bottom: 2px; }}
.step-cmd {{
  font-family: 'Cascadia Code', Consolas, monospace; font-size: 12.5px;
  background: var(--c-code-bg); color: var(--c-code-text);
  padding: 2px 8px; border-radius: 4px; border: 1px solid var(--c-td-border);
  display: inline-block; margin-bottom: 3px;
}}
.step-desc {{ font-size: 13px; color: var(--c-h3); }}
.step-note {{
  font-size: 13px; color: var(--c-h3); margin-top: 12px;
  padding: 10px 14px; background: var(--c-callout-bg);
  border-left: 3px solid var(--c-accent); border-radius: 0 4px 4px 0;
}}

/* ── File reference ──────────────────── */
.file-group-label {{
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; color: var(--c-h3); margin: 16px 0 8px;
}}
.file-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px; margin-bottom: 16px;
}}
.file-card {{
  display: flex; align-items: flex-start; gap: 12px;
  background: #fff; border: 1px solid var(--c-td-border); border-radius: 6px;
  padding: 12px 14px; transition: border-color .15s;
}}
.file-card:hover {{ border-color: var(--c-accent); }}
.file-card-icon {{ width: 20px; height: 20px; color: var(--c-accent); flex-shrink: 0; margin-top: 1px; }}
.file-card-icon svg {{ width: 100%; height: 100%; }}
.file-card-name {{ font-weight: 700; font-size: 13px; color: var(--c-h1); }}
.file-card-desc {{ font-size: 12px; color: var(--c-h3); margin-top: 1px; }}

/* ── Conventions ─────────────────────── */
.conv-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 10px; margin-top: 12px;
}}
.conv-item {{
  background: var(--c-callout-bg); border: 1px solid var(--c-callout-border);
  border-radius: 6px; padding: 12px 14px;
}}
.conv-title {{ font-weight: 700; font-size: 13px; color: var(--c-h2); margin-bottom: 3px; }}
.conv-body {{ font-size: 12.5px; color: var(--c-text); line-height: 1.5; }}
.conv-body code {{
  font-family: 'Cascadia Code', Consolas, monospace; font-size: 11.5px;
  background: var(--c-code-bg); color: var(--c-code-text);
  padding: 1px 4px; border-radius: 3px;
}}

/* ── Project cards ───────────────────── */
.proj-grid {{ display: flex; flex-direction: column; gap: 14px; margin-top: 12px; }}
.proj-card {{
  display: block; background: #fff; border: 1px solid var(--c-td-border);
  border-radius: 8px; padding: 18px 20px; text-decoration: none;
  transition: border-color .15s, box-shadow .15s;
}}
.proj-card:hover {{ border-color: var(--c-accent); box-shadow: 0 2px 12px rgba(0,0,0,.06); }}
.proj-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }}
.proj-name {{ font-size: 17px; font-weight: 700; color: var(--c-h1); }}
.proj-status {{
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  font-size: 10px; font-weight: 600; color: #fff;
}}
.proj-desc {{ font-size: 13px; color: var(--c-h3); margin-bottom: 6px; }}
.proj-stack {{ font-size: 11px; color: var(--c-h3); margin-bottom: 6px; font-style: italic; }}
.proj-files {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.file-pill {{
  background: var(--c-code-bg); color: var(--c-code-text);
  font-size: 10.5px; padding: 2px 7px; border-radius: 10px;
  border: 1px solid var(--c-td-border);
}}

/* ── Section headings ────────────────── */
section h2 {{
  font-size: 20px; color: var(--c-h1); font-weight: 700;
  border-bottom: 2px solid var(--c-h1-border); padding-bottom: 6px;
  margin: 28px 0 14px;
}}
</style>
</head>
<body class="gem-page">
{sidebar}
<main class="gem-content-panel">
{hero}
{steps_html}
{files_html}
{conv_html}
{proj_html}
{footer}
</main>
</body>
</html>'''


def main():
    DOC_DIR.mkdir(exist_ok=True)
    projects = discover_projects()
    for slug, display, *_ in projects:
        print(f"  [ok] {slug}/")
    out_path = DOC_DIR / "index.html"
    out_path.write_text(build_page(projects), encoding='utf-8')
    print(f"\nWrote {out_path}  ({out_path.stat().st_size // 1024} KB)")


if __name__ == '__main__':
    main()
