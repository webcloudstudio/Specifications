# Feature: Homepage Publisher

**Version:** 20260331.1
**Description:** Template-based static site builder for the portfolio homepage. Replaces the Astro/npm pipeline with Jinja2 rendering to plain HTML.

---

## Architecture

```
SPECIFICATION/templates/    ← Specifications/GAME/templates/*.j2   (canonical source)
        ↓  sync on build (when SPECIFICATIONS_PATH is set)
TARGET/templates/           ← $PUBLISHER_TARGET/templates/*.j2     (working templates)
        ↓  homepage_build.sh renders with data
TARGET/publish/             ← $PUBLISHER_TARGET/publish/            (static HTML payload)
        ↓  homepage_publish.sh → git push origin main
GitHub Pages
```

- **No Astro, no npm** in this pipeline. All CSS lives in `base.html.j2`. Output is plain HTML.
- **PUBLISHER_TARGET** = configurable directory pointed at by the env var. Default: sibling `My_Github/`. Can be `GAME/site/` or any directory on install.
- **TARGET/publish/** is a subdirectory of the TARGET git repo. `homepage_publish.sh` commits and pushes from the TARGET root.

---

## Template Directory Structure

```
Specifications/GAME/templates/
├── base.html.j2        Full page shell: head, global CSS, nav, Mermaid CDN, footer
├── index.html.j2       Home page: name + home_html body
├── projects.html.j2    Projects grid: card grid from scanned METADATA.md
├── _card.html.j2       Single project card partial (included by projects.html.j2)
└── resume.html.j2      Resume page
```

Templates are installed to `TARGET/templates/` and render to `TARGET/publish/`:

| Template | Output path |
|----------|-------------|
| `index.html.j2` | `publish/index.html` |
| `projects.html.j2` | `publish/projects/index.html` |
| `resume.html.j2` | `publish/resume/index.html` |

---

## Jinja2 Variable Contract

### Shared context (passed to all templates)

```python
site = {
    "logo":             str,   # nav logo text, e.g. "Ed Barlow"
    "name":             str,   # h1 on home page, contact card name
    "email":            str,   # mailto link
    "phone":            str,   # display format, e.g. "(914) 837-4798"
    "phone_e164":       str,   # tel: link format, e.g. "+19148374798"
    "copyright":        str,   # footer text, e.g. "Web Cloud Studio — Ed Barlow"
    "section_title":    str,   # projects page h1
    "section_subtitle": str,   # projects page subheading; empty string if not set
    "home_html":        str,   # HTML rendered from site_config.md markdown body
}

base_path = str    # URL path prefix derived from GITHUB_PAGES_BASE_URL
                   # "https://example.github.io/sitename" → "/sitename"
                   # "" (empty string) for root-served sites or local preview
build_year = int   # datetime.now().year, used in footer
```

### projects.html.j2 additional context

```python
projects = [
    {
        "name":       str,   # project directory name, e.g. "GAME"
        "card_title": str,
        "card_desc":  str,   # may be empty string
        "card_url":   str,   # external/detail link; empty string if none
        "card_image": str,   # absolute path, e.g. "/sitename/images/GAME.webp"
        "docs_url":   str,   # absolute path to docs index; empty string if none
        "tags": [
            {
                "label": str,  # tag text
                "bg":    str,  # hex background color, e.g. "#22c55e18"
                "text":  str,  # hex text color, e.g. "#4ade80"
            },
        ],
    },
    ...
]
```

**Tags use inline styles, not CSS class names.** Template renders:
```html
<span class="tag" style="background:{{ tag.bg }};color:{{ tag.text }};">{{ tag.label }}</span>
```
This avoids the broken `tag--{dict}` class name bug present in the Astro pipeline where `tag_colors.json` values (dicts) were incorrectly used as class name strings.

### resume.html.j2 additional context

```python
resume_html = str   # HTML rendered from static/contents/Edward_Barlow.md
```

---

## Tag Color Resolution

The build script resolves tags at data-prep time, not in templates:

```python
def resolve_tag(label: str, tag_colors: dict) -> dict:
    """Returns {"label": label, "bg": "#hex", "text": "#hex"}.
    tag_colors keys are tag labels; values are {"bg": "#hex", "text": "#hex"} dicts.
    """
    for key, colors in tag_colors.items():
        if key.lower() == label.strip().lower():
            return {"label": label, "bg": colors["bg"], "text": colors["text"]}
    return {"label": label, "bg": "#64748b18", "text": "#94a3b8"}  # neutral fallback
```

---

## Script Specifications

### `bin/homepage_build.sh` (wrapper) + `bin/homepage_build.py` (logic)

**Inputs:**

| Source | Content |
|--------|---------|
| `config/site_config.md` | YAML frontmatter (branding) + Markdown body (bio HTML) |
| `$PROJECTS_DIR/*/METADATA.md` | One per project; scanned for `show_on_homepage: true` |
| `data/tag_colors.json` | Tag color definitions `{"tags": {"label": {"bg": "#hex", "text": "#hex"}}}` |
| `static/project_images/*.webp` | Card images |
| `static/diagrams/` | Diagram assets |
| `static/contents/Edward_Barlow.md` | Resume source |
| `$PUBLISHER_TARGET/templates/*.j2` | Jinja2 templates |

**Outputs:**

| Path | Content |
|------|---------|
| `$PUBLISHER_TARGET/publish/index.html` | Home page |
| `$PUBLISHER_TARGET/publish/projects/index.html` | Projects grid |
| `$PUBLISHER_TARGET/publish/resume/index.html` | Resume page |
| `$PUBLISHER_TARGET/publish/images/*.webp` | Card images (copied) |
| `$PUBLISHER_TARGET/publish/diagrams/` | Diagrams (copied) |
| `$PUBLISHER_TARGET/publish/project-docs/{name}/` | Per-project doc dirs (copied) |

**Build algorithm:**

```
Step 0: Template sync (optional)
  If $SPECIFICATIONS_PATH is set:
    Copy $SPECIFICATIONS_PATH/GAME/templates/*.j2 → $PUBLISHER_TARGET/templates/
  Else:
    Use $PUBLISHER_TARGET/templates/ as-is.
    Warn and abort if directory is missing or empty.

Step 1: Load site config
  Parse YAML frontmatter from config/site_config.md (apply _SITE_CONFIG_DEFAULTS for missing keys)
  Render Markdown body → site["home_html"] via markdown.markdown(body, extensions=["extra"])
  Derive base_path:
    Strip domain from GITHUB_PAGES_BASE_URL
    "https://example.github.io/sitename" → "/sitename"
    "" (empty) if GITHUB_PAGES_BASE_URL is unset or is a plain domain with no path

Step 2: Scan projects
  Load tag_colors from data/tag_colors.json (key: "tags")
  For each subdirectory of $PROJECTS_DIR (sorted alphabetically):
    Skip if no METADATA.md
    Parse METADATA.md key:value fields
    Skip if show_on_homepage != true (log: skipped)
    Resolve card_image URL:
      Bare filename → base_path + "/images/{filename}"
      {{PROJECT_NAME}} or raw.githubusercontent.com → base_path + "/images/{name}.webp"
      Already absolute URL → keep as-is
    Parse card_tags: comma-separated string or JSON array
    Resolve each tag label → {"label", "bg", "text"} via resolve_tag()
    Detect doc dir: check project/doc/index.html, doc/index.htm, docs/index.html, docs/index.htm
    Set docs_url = base_path + "/project-docs/{name}/index.html" if doc found; else ""
    Store _doc_src_dir for Step 5

Step 3: Render templates
  Load Jinja2 Environment:
    FileSystemLoader from $PUBLISHER_TARGET/templates/
    autoescape=False (content includes pre-rendered HTML)
  Build shared context: site=site_config, base_path=base_path, build_year=current_year
  Render index.html.j2    → publish/index.html        (shared context)
  Render projects.html.j2 → publish/projects/index.html (shared context + projects=[...])
  Render resume.html.j2   → publish/resume/index.html   (shared context + resume_html=...)
  Create parent directories as needed (os.makedirs exist_ok=True)

Step 4: Copy static assets
  static/project_images/*.webp → publish/images/
  static/diagrams/*            → publish/diagrams/
  static/contents/*.pdf        → publish/

Step 5: Copy project docs
  For each project card where _doc_src_dir is set:
    dst = $PUBLISHER_TARGET/publish/project-docs/{name}/
    Delete dst if exists (rmtree)
    Copy _doc_src_dir → dst (copytree)
    Rename index.htm → index.html at destination if needed

Step 6: Print summary
  List written files; print elapsed time; exit 0
```

**Python dependencies** (already in GAME venv): `jinja2`, `pyyaml`, `markdown`

---

### `bin/homepage_review.sh`

Serves `$PUBLISHER_TARGET/publish/` locally via Python's built-in HTTP server.

```bash
PREVIEW_PORT="${HOMEPAGE_PREVIEW_PORT:-4321}"
cd "$PUBLISHER_TARGET/publish"
python3 -m http.server "$PREVIEW_PORT"
```

**Local preview note:** `base_path` is derived from `GITHUB_PAGES_BASE_URL`. When that URL has a path prefix (e.g., `/webcloudstudio`), all nav links will 404 against a root-served local server.

**Workaround:** Before running review, rebuild with `GITHUB_PAGES_BASE_URL=http://localhost:4321` so `base_path` becomes empty and all links are root-relative. A `HOMEPAGE_PREVIEW_BASE_URL` env var can be added to override the base_path derivation for local preview without changing the production URL setting.

---

### `bin/homepage_publish.sh`

Commits and pushes `$PUBLISHER_TARGET` to GitHub Pages.

```bash
cd "$PUBLISHER_TARGET"
git add -A
git commit -m "Update homepage $(date '+%Y-%m-%d %H:%M')" || true
git push origin main
```

**Git convention:** remote `origin`, branch `main`. The timestamp in the commit message ensures sequential publishes always produce a non-empty commit.

**Precondition:** `$PUBLISHER_TARGET` must be a git repository with `origin` remote pointing to the GitHub Pages repo.

---

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `PUBLISHER_TARGET` | Yes | `$(dirname $GAME_DIR)/My_Github` | Path to the TARGET directory |
| `PROJECTS_DIR` | Yes | — | Path containing all project repos |
| `GITHUB_PAGES_BASE_URL` | No | `""` | Full URL; drives `base_path` derivation |
| `SPECIFICATIONS_PATH` | No | — | If set, templates are synced from spec on each build |
| `HOMEPAGE_PREVIEW_PORT` | No | `4321` | Port for `homepage_review.sh` |

---

## Deprecated Scripts

| Old script | Replaced by |
|-----------|-------------|
| `bin/RebuildYourHomepage.sh` | `bin/homepage_build.sh` |
| `bin/LocalPreview.sh` | `bin/homepage_review.sh` |
| `bin/PushAndPublish.sh` | `bin/homepage_publish.sh` |

The old scripts called `publisher.rebuild_pages()` which generated Astro `.astro` source files and required `npm run build`. The new scripts have no npm dependency.

---

## Data Sources (Resolved)

| Data | Source | Notes |
|------|--------|-------|
| Site branding & bio | `GAME/config/site_config.md` | YAML frontmatter + Markdown body. Stays in GAME project, not Specifications repo. |
| Tag colors | `GAME/data/tag_colors.json` | Resolved to inline style attributes at build time, not CSS classes |
| Image URLs | Derived at build time | `base_path + "/images/{name}.webp"` |
| Resume content | `GAME/static/contents/Edward_Barlow.md` | Rendered to HTML; injected as `resume_html` |

---

## Open Question

**publish/ git repository structure:**

- **Option A (default):** `publish/` is a subdirectory of `PUBLISHER_TARGET`. Commit and push happen at `PUBLISHER_TARGET` root. Lowest-friction migration — `My_Github/` already has the right git remote; `publish/` replaces the Astro `dist/` subdirectory.
- **Option B:** `publish/` is itself a standalone git repo with its own `origin` remote pointing directly to the GitHub Pages source. Cleaner separation; requires re-initializing a git repo in `publish/`.

Spec default: Option A. Document Option B as an advanced configuration in `.env.sample`.
