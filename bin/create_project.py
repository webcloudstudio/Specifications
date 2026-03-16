#!/usr/bin/env python3
# CommandCenter Operation
# Category: maintenance
"""
Create a new project conforming to CLAUDE_RULES standards, or update existing
set-up projects with the latest rules and templates.

A project is considered "set up" if its effective rules file (AGENTS.md, or
CLAUDE.md when not a redirect) contains the CLAUDE_RULES_START marker.
Projects without that marker are in the idea phase and are skipped by --update.

Usage:
    python3 bin/create_project.py <name>                    # Create new project
    python3 bin/create_project.py <name> --dry-run          # Preview creation
    python3 bin/create_project.py --update                  # Update all set-up projects
    python3 bin/create_project.py --update --project <name> # Update one project
    python3 bin/create_project.py --update --dry-run        # Preview updates
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SPEC_DIR = SCRIPT_DIR.parent
PROJECTS_DIR = SPEC_DIR.parent
TEMPLATES_DIR = SPEC_DIR / "templates"
RULES_FILE = SPEC_DIR / "CLAUDE_RULES.md"

MARKER_START = "# CLAUDE_RULES_START"
MARKER_END = "# CLAUDE_RULES_END"
METADATA_HEADING = "# AUTHORITATIVE PROJECT METADATA - THE FIELDS IN THIS FILE SHOULD BE CURRENT"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_rules_content() -> str:
    if not RULES_FILE.exists():
        print(f"ERROR: CLAUDE_RULES.md not found: {RULES_FILE}", file=sys.stderr)
        sys.exit(1)
    content = RULES_FILE.read_text(encoding="utf-8")
    return content if content.endswith("\n") else content + "\n"


def strip_rules_block(text: str) -> str:
    """Remove existing CLAUDE_RULES_START...CLAUDE_RULES_END block inclusive."""
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


def effective_rules_file(project_dir: Path):
    """Return the file that holds CLAUDE_RULES (AGENTS.md if CLAUDE.md is a redirect)."""
    claude_md = project_dir / "CLAUDE.md"
    if not claude_md.exists():
        return None
    content = claude_md.read_text(encoding="utf-8").strip()
    if content == "@AGENTS.md":
        agents = project_dir / "AGENTS.md"
        return agents if agents.exists() else None
    return claude_md


def is_setup(project_dir: Path) -> bool:
    """Return True if the project has CLAUDE_RULES_START in its rules file."""
    target = effective_rules_file(project_dir)
    if not target:
        return False
    return MARKER_START in target.read_text(encoding="utf-8")


def inject_rules(target: Path, rules: str) -> bool:
    """Strip old block and append fresh rules. Returns True if file changed."""
    original = target.read_text(encoding="utf-8")
    stripped = strip_rules_block(original).rstrip("\n")
    new_content = stripped + "\n" + rules
    if new_content == original:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def derive_display_name(name: str) -> str:
    if re.fullmatch(r"[A-Z0-9]+", name):
        return name
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)
    return spaced.replace("_", " ").replace("-", " ")


def copy_template(name: str, dest: Path) -> bool:
    """Copy a template file to dest. Returns True if dest changed."""
    src = TEMPLATES_DIR / name
    if not src.exists():
        return False
    new = src.read_text(encoding="utf-8")
    if dest.exists() and dest.read_text(encoding="utf-8") == new:
        return False
    dest.write_text(new, encoding="utf-8")
    dest.chmod(0o755)
    return True


def get_git_remote_url(project_dir: Path) -> str:
    """Return the full HTTPS URL of the git remote origin, or empty string."""
    try:
        url = subprocess.check_output(
            ["git", "-C", str(project_dir), "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return _normalize_git_url(url)
    except subprocess.CalledProcessError:
        return ""


def _normalize_git_url(url: str) -> str:
    """Convert SSH or git: URL to HTTPS for presentation."""
    # git@github.com:user/repo.git → https://github.com/user/repo
    if url.startswith("git@"):
        url = url[4:]                    # remove "git@"
        url = url.replace(":", "/", 1)  # first : → /
        url = "https://" + url
    if url.endswith(".git"):
        url = url[:-4]
    return url


def update_metadata_fields(meta_path: Path, updates: dict) -> bool:
    """Update specific fields in METADATA.md and bump 'updated' timestamp.

    Preserves the heading line and all other fields. Returns True if changed.
    """
    content = meta_path.read_text(encoding="utf-8")
    updates = {**updates, "updated": now_ts()}

    lines = content.splitlines()
    result = []
    applied = set()

    for line in lines:
        matched = False
        for key, val in updates.items():
            if line.startswith(f"{key}:"):
                result.append(f"{key}: {val}")
                applied.add(key)
                matched = True
                break
        if not matched:
            result.append(line)

    # Append any fields not already in the file
    for key, val in updates.items():
        if key not in applied and val:
            result.append(f"{key}: {val}")

    new_content = "\n".join(result) + "\n"
    if new_content == content:
        return False
    meta_path.write_text(new_content, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_project(name: str, dry_run: bool) -> None:
    project_dir = PROJECTS_DIR / name
    if project_dir.exists():
        print(f"ERROR: {project_dir} already exists.", file=sys.stderr)
        print("Use --update --project <name> to refresh an existing project.", file=sys.stderr)
        sys.exit(1)

    rules = get_rules_content()
    display = derive_display_name(name)
    today = datetime.now().strftime("%Y-%m-%d")

    if dry_run:
        print(f"[dry-run] Would create: {project_dir}")
        print(f"  Directories: bin/ logs/ data/ tests/")
        print(f"  Files: METADATA.md CLAUDE.md AGENTS.md .env.sample .gitignore")
        print(f"  Templates: bin/common.sh bin/common.py")
        return

    # Directories
    for sub in ["bin", "logs", "data", "tests"]:
        (project_dir / sub).mkdir(parents=True, exist_ok=True)

    # .gitignore
    gitignore_src = SPEC_DIR / ".gitignore"
    if gitignore_src.exists():
        (project_dir / ".gitignore").write_text(
            gitignore_src.read_text(encoding="utf-8"), encoding="utf-8"
        )

    # METADATA.md — git_repo left blank until git remote is added
    (project_dir / "METADATA.md").write_text(
        f"{METADATA_HEADING}\n\n"
        f"name: {name}\n"
        f"display_name: {display}\n"
        f"git_repo: \n"
        f"port: \n"
        f"short_description: \n"
        f"health: /health\n"
        f"version: {today}.1\n"
        f"updated: {now_ts()}\n",
        encoding="utf-8",
    )

    # CLAUDE.md
    (project_dir / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")

    # AGENTS.md — starter sections then CLAUDE_RULES
    agents_starter = (
        f"# AGENTS.md — {display}\n\n"
        f"## Dev Commands\n"
        f"- Start: `./bin/start.sh`\n"
        f"- Stop: `./bin/stop.sh`\n"
        f"- Test: `./bin/test.sh`\n\n"
        f"## Service Endpoints\n"
        f"- Local: http://localhost:PORT\n\n"
        f"## Bookmarks\n"
        f"- [Documentation](doc/index.html)\n\n"
    )
    (project_dir / "AGENTS.md").write_text(agents_starter + rules, encoding="utf-8")

    # bin/common.sh and bin/common.py from templates
    copy_template("common.sh", project_dir / "bin" / "common.sh")
    copy_template("common.py", project_dir / "bin" / "common.py")

    # .env.sample
    (project_dir / ".env.sample").write_text("# Required environment variables\n", encoding="utf-8")

    # Placeholder keeps for gitignored dirs
    for sub in ["logs", "data"]:
        (project_dir / sub / ".gitkeep").touch()

    print(f"Created: {project_dir}")
    print(f"  Next steps:")
    print(f"    1. Fill in METADATA.md (port, short_description)")
    print(f"    2. Create bin/start.sh, bin/stop.sh, bin/test.sh")
    print(f"    3. Run: git init && git remote add origin <url> && git add -A && git commit -m 'Initial scaffold'")
    print(f"    4. Re-run: python3 bin/create_project.py --update --project {name}  (fills git_repo URL)")


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_projects(project_filter, dry_run: bool) -> None:
    """Update all set-up projects with latest CLAUDE_RULES, templates, and git_repo."""
    rules = get_rules_content()

    candidates = sorted(
        d for d in PROJECTS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
        and d.name not in ("__pycache__", "venv", "node_modules")
        and d != SPEC_DIR  # never update the Specifications source repo itself
    )
    if project_filter:
        candidates = [d for d in candidates if d.name == project_filter]
        if not candidates:
            print(f"ERROR: project '{project_filter}' not found in {PROJECTS_DIR}", file=sys.stderr)
            sys.exit(1)

    updated = []
    skipped = []
    errors = []

    for project_dir in candidates:
        name = project_dir.name
        if not is_setup(project_dir):
            skipped.append(f"{name} (no CLAUDE_RULES_START — idea phase)")
            continue
        try:
            target = effective_rules_file(project_dir)
            if not target:
                skipped.append(f"{name} (no effective rules file)")
                continue

            changed = False
            if not dry_run:
                changed = inject_rules(target, rules)

                for tmpl_name in ("common.sh", "common.py"):
                    dest = project_dir / "bin" / tmpl_name
                    if dest.exists() and copy_template(tmpl_name, dest):
                        changed = True

                # Verify/update git_repo in METADATA.md
                meta = project_dir / "METADATA.md"
                if meta.exists():
                    git_url = get_git_remote_url(project_dir)
                    if git_url:
                        current = ""
                        for line in meta.read_text(encoding="utf-8").splitlines():
                            if line.startswith("git_repo:"):
                                current = line[9:].strip()
                                break
                        if current != git_url:
                            if update_metadata_fields(meta, {"git_repo": git_url}):
                                changed = True
                    elif changed:
                        # Rules or templates changed — bump updated timestamp
                        update_metadata_fields(meta, {})
            else:
                changed = True  # show as would-update in dry-run

            (updated if changed else skipped).append(name + ("" if changed else " (unchanged)"))
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    dry = " (dry-run)" if dry_run else ""
    print(f"\nUpdate projects{dry} — {len(updated)} updated, {len(skipped)} skipped, {len(errors)} errors")
    for n in updated:
        print(f"  ✓ {n}")
    for n in skipped:
        print(f"  · {n}")
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)

    if errors:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create or update projects conforming to CLAUDE_RULES standards."
    )
    parser.add_argument("name", nargs="?", help="Project name to create")
    parser.add_argument("--update", action="store_true",
                        help="Update all set-up projects with latest rules and templates")
    parser.add_argument("--project", metavar="NAME",
                        help="With --update, target a specific project by name")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if args.update:
        update_projects(args.project, args.dry_run)
    elif args.name:
        create_project(args.name, args.dry_run)
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
