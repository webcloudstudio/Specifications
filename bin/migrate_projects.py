#!/usr/bin/env python3
# CommandCenter Operation
# Category: maintenance
"""
Migrate METADATA.md files across all projects to conform to the CLAUDE_RULES standard.

For each project under ../../projects/ that has a METADATA.md:
  - Parse existing key: value fields, preserving the title heading and Links section.
  - Pull missing or corrupt values from git_homepage.md when available.
  - Add missing fields with sensible defaults (never overwriting valid values).
  - Write back in canonical field order only when content changed.

Fields pulled from git_homepage.md (markdown table):
  Title           → title, display_name (if display_name missing)
  Description     → short_description, description
  Card Image      → image  (URL trimmed to images/Filename.webp)
  Tags            → tags
  Show on Homepage → show_on_homepage

Usage:
    python3 bin/migrate_projects.py [--dry-run] [--project NAME]
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SPEC_DIR = SCRIPT_DIR.parent
PROJECTS_DIR = SPEC_DIR.parent

# Canonical field order per CLAUDE_RULES METADATA standard
CANONICAL_FIELDS = [
    "name",
    "display_name",
    "title",
    "git_repo",
    "short_description",
    "port",
    "status",
    "version",
    "updated",
    "stack",
    "image",
    "health",
    "show_on_homepage",
    "tags",
    "desired_state",
    "namespace",
    "description",
]

# Defaults for fields that should always be present
FIELD_DEFAULTS: dict[str, str] = {
    "status": "IDEA",
    "health": "/health",
    "desired_state": "on-demand",
    "namespace": "development",
    "show_on_homepage": "false",
}

_KEY_RE = re.compile(r"^([a-z][a-z0-9_]*):\s*(.*)", re.IGNORECASE)
_TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def is_corrupt(value: str) -> bool:
    """Return True if a field value is missing, blank, or clearly junk."""
    if not value or not value.strip():
        return True
    v = value.strip()
    # Headings accidentally pasted as values, e.g. "# GitHub Homepage Card Configuration"
    if v.startswith("#"):
        return True
    return False


def derive_display_name(name: str) -> str:
    """Derive a human-readable display_name from a machine name per CLAUDE_RULES spec.

    GAME      → GAME   (all-caps preserved)
    MyProject → My Project   (CamelCase split)
    my_proj   → my proj   (underscores/hyphens → spaces)
    """
    if re.fullmatch(r"[A-Z0-9]+", name):
        return name  # all-caps, keep as-is
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)  # CamelCase → spaces
    spaced = spaced.replace("_", " ").replace("-", " ")
    return spaced


def image_path_from_url(url: str) -> str:
    """Extract a relative image path from an absolute URL.

    https://raw.githubusercontent.com/.../images/Foo.webp → images/Foo.webp
    """
    if "/images/" in url:
        return "images/" + url.split("/images/")[-1]
    return url


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_metadata(text: str) -> tuple[str, str, dict[str, str], list[str], str]:
    """Parse METADATA.md into its structural parts.

    Returns:
        title_line   — the leading '# Name' heading (may be empty)
        description  — free-text paragraph before the first key:value line
        fields       — ordered dict of key → value
        field_order  — list of keys in the order they appeared
        footer       — everything from the first '## ' section to end of file
    """
    lines = text.splitlines()
    title_line = ""
    description_lines: list[str] = []
    fields: dict[str, str] = {}
    field_order: list[str] = []
    footer_lines: list[str] = []

    i = 0
    if lines and lines[0].startswith("# "):
        title_line = lines[0].rstrip()
        i = 1

    in_footer = False
    found_first_field = False

    for line in lines[i:]:
        s = line.rstrip()

        if s.startswith("## "):
            in_footer = True

        if in_footer:
            footer_lines.append(s)
            continue

        m = _KEY_RE.match(s)
        if m:
            key = m.group(1).lower()
            val = m.group(2).strip()
            found_first_field = True
            if key not in fields:
                field_order.append(key)
            fields[key] = val
        elif not found_first_field and s and not s.startswith("#"):
            description_lines.append(s)
        # else: blank lines and stray headings are dropped from preamble

    description = "\n".join(description_lines).strip()
    footer = "\n".join(footer_lines)
    return title_line, description, fields, field_order, footer


def parse_git_homepage(text: str) -> dict[str, str]:
    """Parse the markdown table in git_homepage.md into a plain dict."""
    result: dict[str, str] = {}
    for line in text.splitlines():
        m = _TABLE_ROW_RE.match(line)
        if not m:
            continue
        field = m.group(1).strip()
        value = m.group(2).strip()
        # Skip header / separator rows
        if not field or field.startswith("-") or field.startswith(":"):
            continue
        if not value or value.startswith("-") or value.startswith(":"):
            continue
        if field.lower() == "field":
            continue
        result[field] = value
    return result


# ---------------------------------------------------------------------------
# Field population
# ---------------------------------------------------------------------------


def ensure_fields(
    fields: dict[str, str],
    field_order: list[str],
    project_dir: Path,
    homepage: dict[str, str],
) -> bool:
    """Fill missing or corrupt fields in-place. Returns True if anything changed."""
    changed = False

    def set_field(key: str, value: str) -> None:
        """Write a field only when the current value is corrupt/missing."""
        nonlocal changed
        if is_corrupt(value):
            return
        if is_corrupt(fields.get(key, "")):
            fields[key] = value
            if key not in field_order:
                field_order.append(key)
            changed = True

    name = fields.get("name", "") or project_dir.name

    # --- Identity ---
    set_field("name", name)
    set_field("git_repo", name)

    if is_corrupt(fields.get("display_name", "")):
        # Prefer homepage Title for display_name derivation; fall back to name
        hp_title = homepage.get("Title", "")
        set_field("display_name", hp_title if hp_title else derive_display_name(name))

    # --- Fields from git_homepage.md ---
    if homepage:
        hp_title = homepage.get("Title", "")
        hp_desc = homepage.get("Description", "")
        hp_tags = homepage.get("Tags", "")
        hp_show = homepage.get("Show on Homepage", "")
        hp_image = homepage.get("Card Image", "")

        if hp_title:
            set_field("title", hp_title)
        if hp_desc:
            set_field("short_description", hp_desc)
            set_field("description", hp_desc)
        if hp_tags:
            set_field("tags", hp_tags)
        if hp_show:
            set_field("show_on_homepage", hp_show.lower())
        if hp_image:
            set_field("image", image_path_from_url(hp_image))

    # --- Scalar defaults ---
    for key, default in FIELD_DEFAULTS.items():
        set_field(key, default)

    # --- Auto-generated timestamps (only when truly absent) ---
    today = datetime.now().strftime("%Y-%m-%d")
    now_ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not fields.get("version"):
        fields["version"] = f"{today}.1"
        if "version" not in field_order:
            field_order.append("version")
        changed = True

    if not fields.get("updated"):
        fields["updated"] = now_ts
        if "updated" not in field_order:
            field_order.append("updated")
        changed = True

    return changed


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------


def build_metadata(
    title_line: str,
    description: str,
    fields: dict[str, str],
    footer: str,
) -> str:
    """Reconstruct METADATA.md in canonical field order."""
    lines: list[str] = []

    if title_line:
        lines.append(title_line)
    lines.append("")

    if description:
        lines.append(description)
        lines.append("")

    # Canonical fields first
    for key in CANONICAL_FIELDS:
        if key in fields:
            lines.append(f"{key}: {fields[key]}")

    # Any extra fields not in the canonical list (preserve them)
    for key, val in fields.items():
        if key not in CANONICAL_FIELDS:
            lines.append(f"{key}: {val}")

    if footer:
        lines.append("")
        lines.append(footer)

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def process_project(project_dir: Path, dry_run: bool) -> str:
    """Process a single project. Returns 'updated', 'unchanged', or raises."""
    meta_path = project_dir / "METADATA.md"
    original = meta_path.read_text(encoding="utf-8")

    title_line, description, fields, field_order, footer = parse_metadata(original)

    homepage: dict[str, str] = {}
    hp_path = project_dir / "git_homepage.md"
    if hp_path.exists():
        homepage = parse_git_homepage(hp_path.read_text(encoding="utf-8"))

    changed = ensure_fields(fields, field_order, project_dir, homepage)
    if not changed:
        return "unchanged"

    new_content = build_metadata(title_line, description, fields, footer)
    if not dry_run:
        meta_path.write_text(new_content, encoding="utf-8")
    return "updated"


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate METADATA.md files to CLAUDE_RULES standard.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")
    parser.add_argument("--project", metavar="NAME", help="Migrate only this project.")
    args = parser.parse_args()

    updated: list[str] = []
    unchanged: list[str] = []
    errors: list[str] = []

    candidates = sorted(PROJECTS_DIR.glob("*/METADATA.md"))
    if args.project:
        candidates = [p for p in candidates if p.parent.name == args.project]
        if not candidates:
            print(f"ERROR: project '{args.project}' not found.", file=sys.stderr)
            return 1

    for meta_path in candidates:
        project_dir = meta_path.parent
        name = project_dir.name
        try:
            result = process_project(project_dir, dry_run=args.dry_run)
            (updated if result == "updated" else unchanged).append(name)
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    dry = " (dry-run)" if args.dry_run else ""
    print(
        f"\nMigrate METADATA{dry} — "
        f"{len(updated)} updated, {len(unchanged)} unchanged, {len(errors)} errors"
    )
    for name in updated:
        print(f"  ✓ {name}")
    for name in unchanged:
        print(f"  · {name}")
    for err in errors:
        print(f"  ✗ {err}", file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
