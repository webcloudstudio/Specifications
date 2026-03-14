#!/usr/bin/env python3
# CommandCenter Operation
# Category: maintenance
"""
Distribute CLAUDE_RULES.md to every project that has a CLAUDE.md.

For each project under ../../projects/:
  - If CLAUDE.md is a bare redirect (@AGENTS.md), update AGENTS.md instead.
  - Remove any existing CLAUDE_RULES_START...CLAUDE_RULES_END block (inclusive).
  - Append the current CLAUDE_RULES.md content.
  - Write the file only when content actually changed.

Usage:
    python3 bin/distribute_claude_rules.py [--dry-run]
"""

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SPEC_DIR = SCRIPT_DIR.parent
PROJECTS_DIR = SPEC_DIR.parent

RULES_FILE = SPEC_DIR / "CLAUDE_RULES.md"
MARKER_START = "# CLAUDE_RULES_START"
MARKER_END = "# CLAUDE_RULES_END"


def strip_rules_block(text: str) -> str:
    """Remove the CLAUDE_RULES_START...CLAUDE_RULES_END block inclusive."""
    lines = text.splitlines(keepends=True)
    result = []
    in_block = False
    for line in lines:
        stripped = line.strip()
        if stripped == MARKER_START:
            in_block = True
        if not in_block:
            result.append(line)
        if in_block and stripped == MARKER_END:
            in_block = False
    return "".join(result)


def resolve_target(project_dir: Path, claude_md: Path) -> Path | None:
    """Return the file to update: AGENTS.md if CLAUDE.md is a redirect, else CLAUDE.md."""
    content = claude_md.read_text(encoding="utf-8").strip()
    if content == "@AGENTS.md":
        target = project_dir / "AGENTS.md"
        if not target.exists():
            return None  # redirect target missing
        return target
    return claude_md


def main() -> int:
    parser = argparse.ArgumentParser(description="Distribute CLAUDE_RULES.md to all projects.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")
    args = parser.parse_args()

    if not RULES_FILE.exists():
        print(f"ERROR: Rules file not found: {RULES_FILE}", file=sys.stderr)
        return 1

    rules_content = RULES_FILE.read_text(encoding="utf-8")
    if not rules_content.endswith("\n"):
        rules_content += "\n"

    updated = []
    unchanged = []
    skipped = []
    errors = []

    for claude_md in sorted(PROJECTS_DIR.glob("*/CLAUDE.md")):
        project = claude_md.parent
        name = project.name
        try:
            target = resolve_target(project, claude_md)
            if target is None:
                skipped.append(f"{name}: CLAUDE.md redirects to missing AGENTS.md")
                continue

            original = target.read_text(encoding="utf-8")
            stripped = strip_rules_block(original).rstrip("\n")
            new_content = stripped + "\n" + rules_content

            if new_content == original:
                unchanged.append(name)
                continue

            label = f"{name}/{target.name}"
            if args.dry_run:
                updated.append(f"{label} (dry-run)")
            else:
                target.write_text(new_content, encoding="utf-8")
                updated.append(label)

        except Exception as exc:
            errors.append(f"{name}: {exc}")

    print(
        f"\nDistribute CLAUDE_RULES — "
        f"{len(updated)} updated, {len(unchanged)} unchanged, "
        f"{len(skipped)} skipped, {len(errors)} errors"
    )
    for msg in updated:
        print(f"  ✓ {msg}")
    for msg in skipped:
        print(f"  · {msg}")
    for msg in errors:
        print(f"  ✗ {msg}", file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
