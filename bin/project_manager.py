#!/usr/bin/env python3
"""
project_manager.py — Verify and update promoted code projects.

A "project" is a codebase promoted to its own git repository.
A "prototype" is a spec directory inside Specifications/ — not a project.

Usage:
    python3 bin/project_manager.py verify <project> [--verbose]
    python3 bin/project_manager.py update <project> [--dry-run]

<project> may be an absolute path or a project name under the projects root
(the parent directory of this Specifications repo).
"""

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (all derived from this script's location)
# ---------------------------------------------------------------------------

SCRIPT_DIR   = Path(__file__).resolve().parent
SPEC_DIR     = SCRIPT_DIR.parent                       # Specifications/
PROJECTS_DIR = SPEC_DIR.parent                         # projects/
RULES_FILE   = SPEC_DIR / "RulesEngine" / "CLAUDE_RULES.md"
TEMPLATES_DIR = SPEC_DIR / "RulesEngine" / "templates"
STACK_DIR    = SPEC_DIR / "RulesEngine" / "stack"

MARKER_START = "# CLAUDE_RULES_START"
MARKER_END   = "# CLAUDE_RULES_END"

# ---------------------------------------------------------------------------
# Status levels — ordered by strictness
# ---------------------------------------------------------------------------

STATUS_ORDER = ["IDEA", "PROTOTYPE", "ACTIVE", "PRODUCTION", "ARCHIVED"]

RULES_BY_LEVEL = {
    "IDEA": [
        "has_metadata",
        "metadata_has_name",
        "metadata_has_status",
        "metadata_status_valid",
    ],
    "PROTOTYPE": [
        "metadata_has_title",
        "metadata_has_description",
        "has_claude_md",
        "claude_md_has_dev_commands",
        "has_root_index_html",
    ],
    "ACTIVE": [
        "metadata_has_port",
        "metadata_has_stack",
        "stack_components_have_files",
        "metadata_has_tags",
        "has_bin_dir",
        "has_start_script",
        "has_test_script",
        "start_script_has_commandcenter_header",
        "scripts_have_preamble",
        "scripts_emit_status",
        "scripts_have_logging",
        "claude_md_has_endpoints",
        "claude_md_has_bookmarks",
    ],
    "PRODUCTION": [
        "has_env_example_or_no_env_needed",
        "health_endpoint_declared",
        "git_initialized",
        "git_has_remote",
        "git_not_dirty",
        "no_env_committed",
        "start_script_has_sigterm_trap",
    ],
}

ARCHIVED_RULES = ["has_metadata", "metadata_has_name", "metadata_has_status", "metadata_status_valid"]

METADATA_FIELD_DEFAULTS = {
    "status":         "IDEA",
    "health":         "/health",
    "desired_state":  "on-demand",
    "namespace":      "development",
    "show_on_homepage": "false",
}

# ---------------------------------------------------------------------------
# ANSI colors
# ---------------------------------------------------------------------------

RESET  = "\033[0m"
GREEN  = "\033[32m"
RED    = "\033[31m"
YELLOW = "\033[33m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def resolve_project(arg: str) -> Path:
    p = Path(arg)
    if p.is_absolute():
        if p.is_dir():
            return p.resolve()
        print(f"ERROR: path not found: {arg}", file=sys.stderr)
        sys.exit(1)
    candidate = PROJECTS_DIR / arg
    if candidate.is_dir():
        return candidate.resolve()
    print(f"ERROR: project '{arg}' not found in {PROJECTS_DIR}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def read_file(path) -> str | None:
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def parse_metadata(project_path: Path) -> dict:
    content = read_file(project_path / "METADATA.md")
    if not content:
        return {}
    result = {}
    for line in content.splitlines():
        m = re.match(r'^([a-zA-Z][a-zA-Z0-9_]*)\s*:\s*(.*)', line)
        if m:
            result[m.group(1).lower()] = m.group(2).strip()
    return result


def get_bin_scripts(project_path: Path) -> list:
    bin_dir = project_path / "bin"
    if not bin_dir.is_dir():
        return []
    return [f for f in bin_dir.iterdir() if f.suffix in (".sh", ".py")]


def script_has_commandcenter_header(path: Path) -> bool:
    content = read_file(path)
    if not content:
        return False
    return any("CommandCenter Operation" in line for line in content.splitlines()[:20])


def get_registered_scripts(project_path: Path) -> list:
    return [s for s in get_bin_scripts(project_path) if script_has_commandcenter_header(s)]


def get_agent_context(project_path: Path) -> str:
    claude_md = read_file(project_path / "CLAUDE.md") or ""
    if claude_md.strip() == "@AGENTS.md":
        return read_file(project_path / "AGENTS.md") or ""
    return claude_md


def git_info(project_path: Path) -> dict:
    result = {"initialized": False, "has_remote": False, "dirty": False, "remote_url": ""}
    try:
        r = subprocess.run(["git", "rev-parse", "--git-dir"],
                           cwd=project_path, capture_output=True, timeout=5)
        if r.returncode != 0:
            return result
        result["initialized"] = True

        r = subprocess.run(["git", "remote"], cwd=project_path, capture_output=True, timeout=5)
        result["has_remote"] = bool(r.stdout.strip())

        if result["has_remote"]:
            r = subprocess.run(["git", "remote", "get-url", "origin"],
                               cwd=project_path, capture_output=True, timeout=5, text=True)
            if r.returncode == 0:
                url = r.stdout.strip()
                if url.startswith("git@"):
                    url = "https://" + url[4:].replace(":", "/", 1)
                if url.endswith(".git"):
                    url = url[:-4]
                result["remote_url"] = url

        r = subprocess.run(["git", "status", "--porcelain"],
                           cwd=project_path, capture_output=True, timeout=5)
        result["dirty"] = bool(r.stdout.strip())
    except Exception:
        pass
    return result


# ---------------------------------------------------------------------------
# Compliance rule checks
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    rule: str
    passed: bool
    message: str = ""


def check(rule: str, project_path: Path, metadata: dict,
          scripts: list, registered: list) -> CheckResult:
    agent_ctx = get_agent_context(project_path)

    if rule == "has_metadata":
        ok = (project_path / "METADATA.md").is_file()
        return CheckResult(rule, ok, "" if ok else "METADATA.md not found")

    if rule == "metadata_has_name":
        ok = bool(metadata.get("name"))
        return CheckResult(rule, ok, "" if ok else "missing 'name' field")

    if rule == "metadata_has_status":
        ok = bool(metadata.get("status"))
        return CheckResult(rule, ok, "" if ok else "missing 'status' field")

    if rule == "metadata_status_valid":
        status = metadata.get("status", "").upper()
        ok = status in STATUS_ORDER
        return CheckResult(rule, ok, "" if ok else f"invalid status '{status}'")

    if rule == "metadata_has_title":
        ok = bool(metadata.get("title") or metadata.get("display_name"))
        return CheckResult(rule, ok, "" if ok else "missing 'title' or 'display_name' field")

    if rule == "metadata_has_description":
        ok = bool(metadata.get("short_description") or metadata.get("description"))
        return CheckResult(rule, ok, "" if ok else "missing 'short_description' or 'description' field")

    if rule == "has_claude_md":
        ok = (project_path / "CLAUDE.md").is_file()
        return CheckResult(rule, ok, "" if ok else "CLAUDE.md not found")

    if rule == "claude_md_has_dev_commands":
        ok = bool(re.search(r'^## Dev Commands', agent_ctx, re.MULTILINE | re.IGNORECASE))
        return CheckResult(rule, ok, "" if ok else "AGENTS.md missing '## Dev Commands' section")

    if rule == "has_root_index_html":
        ok = (project_path / "index.html").is_file()
        return CheckResult(rule, ok, "" if ok else "index.html not found")

    if rule == "metadata_has_port":
        ok = bool(metadata.get("port"))
        return CheckResult(rule, ok, "" if ok else "missing 'port' field")

    if rule == "metadata_has_stack":
        ok = bool(metadata.get("stack"))
        return CheckResult(rule, ok, "" if ok else "missing 'stack' field")

    if rule == "stack_components_have_files":
        stack_val = metadata.get("stack", "")
        if not stack_val:
            return CheckResult(rule, False, "no stack field to validate")
        components = [c.strip() for c in stack_val.split("/") if c.strip()]
        missing = [c for c in components if not (STACK_DIR / (c.lower() + ".md")).is_file()]
        ok = not missing
        return CheckResult(rule, ok, "" if ok else f"no stack file for: {', '.join(missing)}")

    if rule == "metadata_has_tags":
        ok = bool(metadata.get("tags"))
        return CheckResult(rule, ok, "" if ok else "missing 'tags' field")

    if rule == "has_bin_dir":
        ok = (project_path / "bin").is_dir()
        return CheckResult(rule, ok, "" if ok else "no bin/ directory")

    if rule == "has_start_script":
        ok = (project_path / "bin" / "start.sh").is_file()
        return CheckResult(rule, ok, "" if ok else "bin/start.sh not found")

    if rule == "start_script_has_commandcenter_header":
        ok = script_has_commandcenter_header(project_path / "bin" / "start.sh")
        return CheckResult(rule, ok, "" if ok else "bin/start.sh missing CommandCenter Operation header")

    if rule == "scripts_have_preamble":
        missing = [s.name for s in registered
                   if "set -euo pipefail" not in (read_file(s) or "")]
        ok = not missing
        return CheckResult(rule, ok, "" if ok else f"missing preamble: {', '.join(missing)}")

    if rule == "scripts_emit_status":
        missing = [s.name for s in registered
                   if not re.search(r'\[[\w$_]+\]\s*(Starting|Started|Stopped|Error|Service)',
                                    read_file(s) or "")]
        ok = not missing
        return CheckResult(rule, ok, "" if ok else f"no status messages in: {', '.join(missing)}")

    if rule == "scripts_have_logging":
        missing = [s.name for s in registered
                   if "tee -a" not in (read_file(s) or "") and "LOG_FILE" not in (read_file(s) or "")]
        ok = not missing
        return CheckResult(rule, ok, "" if ok else f"no logging in: {', '.join(missing)}")

    if rule == "claude_md_has_endpoints":
        ok = bool(re.search(r'^## Service Endpoints', agent_ctx, re.MULTILINE | re.IGNORECASE))
        return CheckResult(rule, ok, "" if ok else "AGENTS.md missing '## Service Endpoints' section")

    if rule == "claude_md_has_bookmarks":
        ok = bool(re.search(r'^## Bookmarks', agent_ctx, re.MULTILINE | re.IGNORECASE))
        return CheckResult(rule, ok, "" if ok else "AGENTS.md missing '## Bookmarks' section")

    if rule == "has_env_example_or_no_env_needed":
        has_env = (project_path / ".env").is_file()
        mentions_env = "env" in agent_ctx.lower() or bool(metadata.get("env_vars"))
        if has_env or mentions_env:
            ok = (project_path / ".env.example").is_file() or (project_path / ".env.sample").is_file()
            return CheckResult(rule, ok, "" if ok else ".env.example required (project uses env vars)")
        return CheckResult(rule, True, "")

    if rule == "health_endpoint_declared":
        has_health = bool(metadata.get("health")) or any(
            "# Health:" in (read_file(s) or "") for s in registered
        )
        return CheckResult(rule, has_health, "" if has_health else
                           "no health endpoint (add 'health: /health' to METADATA.md)")

    if rule == "git_initialized":
        ok = git_info(project_path).get("initialized", False)
        return CheckResult(rule, ok, "" if ok else "git not initialized")

    if rule == "git_has_remote":
        ok = git_info(project_path).get("has_remote", False)
        return CheckResult(rule, ok, "" if ok else "no git remote")

    if rule == "git_not_dirty":
        dirty = git_info(project_path).get("dirty", False)
        return CheckResult(rule, not dirty, "" if not dirty else "uncommitted changes")

    if rule == "no_env_committed":
        env_path = project_path / ".env"
        if not env_path.is_file():
            return CheckResult(rule, True, "")
        try:
            r = subprocess.run(["git", "ls-files", ".env"],
                               cwd=project_path, capture_output=True, timeout=5)
            committed = bool(r.stdout.strip())
            return CheckResult(rule, not committed, "" if not committed else ".env committed to git")
        except Exception:
            return CheckResult(rule, True, "could not check")

    if rule == "has_test_script":
        ok = (project_path / "bin" / "test.sh").is_file()
        return CheckResult(rule, ok, "" if ok else "bin/test.sh not found")

    if rule == "start_script_has_sigterm_trap":
        content = read_file(project_path / "bin" / "start.sh") or ""
        ok = "trap" in content and "SIGTERM" in content
        return CheckResult(rule, ok, "" if ok else "bin/start.sh missing SIGTERM trap")

    return CheckResult(rule, False, f"unknown rule: {rule}")


def get_applicable_rules(status: str) -> list:
    if status == "ARCHIVED":
        return ARCHIVED_RULES
    rules = []
    for level in STATUS_ORDER:
        if level == "ARCHIVED":
            continue
        rules.extend(RULES_BY_LEVEL.get(level, []))
        if level == status:
            break
    return rules


def get_next_level(status: str) -> str | None:
    if status in ("ARCHIVED", "PRODUCTION"):
        return None
    idx = STATUS_ORDER.index(status) if status in STATUS_ORDER else 0
    for level in STATUS_ORDER[idx + 1:]:
        if level != "ARCHIVED":
            return level
    return None


# ---------------------------------------------------------------------------
# verify command
# ---------------------------------------------------------------------------

def cmd_verify(project_path: Path, verbose: bool) -> int:
    name     = project_path.name
    metadata = parse_metadata(project_path)
    status   = metadata.get("status", "IDEA").upper()
    if status not in STATUS_ORDER:
        status = "IDEA"

    scripts    = get_bin_scripts(project_path)
    registered = get_registered_scripts(project_path)

    print(f"\n{BOLD}ProjectValidate:{RESET} {name}")
    print(f"  Path:   {project_path}")
    print(f"  Status: {CYAN}{BOLD}{status}{RESET}  ← you are here")

    # Collect all checks for current level
    applicable_rules = get_applicable_rules(status)
    checks_by_level: dict[str, list] = {}
    for rule in applicable_rules:
        # Find which level owns this rule
        for level in STATUS_ORDER:
            if rule in RULES_BY_LEVEL.get(level, []):
                checks_by_level.setdefault(level, [])
                checks_by_level[level].append(check(rule, project_path, metadata, scripts, registered))
                break

    errors = 0
    for level in STATUS_ORDER:
        if level not in checks_by_level:
            continue
        level_checks = checks_by_level[level]
        level_errors = sum(1 for c in level_checks if not c.passed)
        print(f"\n  {BOLD}{level}{RESET}")
        for c in level_checks:
            if c.passed:
                if verbose:
                    print(f"    {GREEN}✓{RESET}  {DIM}{c.rule}{RESET}")
            else:
                msg = f"  — {c.message}" if c.message else ""
                print(f"    {RED}✗{RESET}  {c.rule}{msg}")
                errors += 1

    # Next level preview
    next_level = get_next_level(status)
    if next_level and next_level in RULES_BY_LEVEL:
        print(f"\n  {DIM}{next_level} (next — not yet required){RESET}")
        for rule in RULES_BY_LEVEL[next_level]:
            r = check(rule, project_path, metadata, scripts, registered)
            icon = f"{GREEN}✓{RESET}" if r.passed else f"{YELLOW}?{RESET}"
            print(f"    {icon}  {DIM}{rule}{RESET}")

    print(f"\n{'─' * 45}")
    if errors:
        print(f"RESULT: {RED}FAIL{RESET}  {errors} error{'s' if errors != 1 else ''}")
        return 1
    else:
        print(f"RESULT: {GREEN}PASS{RESET}")
        return 0


# ---------------------------------------------------------------------------
# update command
# ---------------------------------------------------------------------------

def strip_rules_block(text: str) -> str:
    lines = text.splitlines(keepends=True)
    result, in_block = [], False
    for line in lines:
        stripped = line.strip()
        if stripped == MARKER_START:
            in_block = True
        if not in_block:
            result.append(line)
        if in_block and stripped == MARKER_END:
            in_block = False
    return "".join(result)


def effective_rules_file(project_path: Path) -> Path | None:
    claude_md = project_path / "CLAUDE.md"
    if not claude_md.exists():
        return None
    content = claude_md.read_text(encoding="utf-8").strip()
    if content == "@AGENTS.md":
        agents = project_path / "AGENTS.md"
        return agents if agents.exists() else None
    return claude_md


def is_setup(project_path: Path) -> bool:
    target = effective_rules_file(project_path)
    if not target:
        return False
    return MARKER_START in target.read_text(encoding="utf-8")


def copy_template(name: str, dest: Path, dry_run: bool) -> str:
    """Copy template to dest. Returns 'updated', 'unchanged', or 'missing' (template not found)."""
    src = TEMPLATES_DIR / name
    if not src.exists():
        return "missing"
    new = src.read_text(encoding="utf-8")
    if dest.exists() and dest.read_text(encoding="utf-8") == new:
        return "unchanged"
    if not dry_run:
        dest.write_text(new, encoding="utf-8")
        dest.chmod(0o755)
    return "updated"


def add_missing_metadata_defaults(meta_path: Path, dry_run: bool) -> list:
    """Add missing default fields to METADATA.md. Returns list of fields added."""
    content = meta_path.read_text(encoding="utf-8")
    existing_keys = set()
    for line in content.splitlines():
        m = re.match(r'^([a-zA-Z][a-zA-Z0-9_]*)\s*:', line)
        if m:
            existing_keys.add(m.group(1).lower())

    added = []
    new_lines = []
    for key, default in METADATA_FIELD_DEFAULTS.items():
        if key not in existing_keys:
            new_lines.append(f"{key}: {default}")
            added.append(key)

    if added and not dry_run:
        new_content = content.rstrip("\n") + "\n" + "\n".join(new_lines) + "\n"
        meta_path.write_text(new_content, encoding="utf-8")
    return added


def cmd_update(project_path: Path, dry_run: bool) -> int:
    name = project_path.name

    print(f"\n{BOLD}ProjectUpdate:{RESET} {name}")
    print(f"  Path:   {project_path}")
    if dry_run:
        print(f"  {YELLOW}dry-run — no files will be written{RESET}")

    if not is_setup(project_path):
        print(f"\n  {RED}✗{RESET}  Not a set-up project (CLAUDE_RULES_START marker missing)")
        print(f"      Run: python3 {SCRIPT_DIR.name}/create_project.py to scaffold first.")
        return 1

    if not RULES_FILE.exists():
        print(f"\n  {RED}✗{RESET}  CLAUDE_RULES.md not found at {RULES_FILE}", file=sys.stderr)
        return 1

    rules = RULES_FILE.read_text(encoding="utf-8")
    if not rules.endswith("\n"):
        rules += "\n"

    changes = 0
    log_lines = []

    def log(icon, label, note):
        nonlocal changes
        if icon == "✓":
            changes += 1
        color = GREEN if icon == "✓" else DIM
        log_lines.append(f"  {color}{icon}{RESET}  {label:<22}  {note}")

    # --- Inject CLAUDE_RULES into AGENTS.md ---
    claude_md = project_path / "CLAUDE.md"
    claude_content = claude_md.read_text(encoding="utf-8").strip() if claude_md.exists() else ""
    agents_md = project_path / "AGENTS.md"

    if claude_content == "@AGENTS.md":
        original = agents_md.read_text(encoding="utf-8")
        stripped  = strip_rules_block(original).rstrip("\n")
        new_content = stripped + "\n" + rules
        if new_content != original:
            if not dry_run:
                agents_md.write_text(new_content, encoding="utf-8")
            log("✓", "AGENTS.md", "rules injected")
        else:
            log("·", "AGENTS.md", "unchanged")
    else:
        # Legacy: migrate inline CLAUDE.md rules → AGENTS.md
        original = claude_md.read_text(encoding="utf-8")
        pre_rules = strip_rules_block(original).rstrip("\n")
        new_agents = pre_rules + "\n" + rules
        if not agents_md.exists() or agents_md.read_text(encoding="utf-8") != new_agents:
            if not dry_run:
                agents_md.write_text(new_agents, encoding="utf-8")
                claude_md.write_text("@AGENTS.md\n", encoding="utf-8")
            log("✓", "AGENTS.md", "migrated from CLAUDE.md (rules injected)")
        else:
            log("·", "AGENTS.md", "unchanged")

    # --- Templates ---
    for tmpl_name, dest_rel in [
        ("common.sh", "bin/common.sh"),
        ("common.py", "bin/common.py"),
        ("index.html", "index.html"),
    ]:
        dest = project_path / dest_rel
        result = copy_template(tmpl_name, dest, dry_run)
        if result == "updated":
            log("✓", dest_rel, "updated")
        elif result == "unchanged":
            log("·", dest_rel, "unchanged")
        else:
            log("·", dest_rel, f"skipped (template {tmpl_name} not found)")

    # --- METADATA: update git_repo ---
    meta_path = project_path / "METADATA.md"
    if meta_path.exists():
        gi = git_info(project_path)
        if gi.get("remote_url"):
            content = meta_path.read_text(encoding="utf-8")
            current_repo = ""
            for line in content.splitlines():
                if line.startswith("git_repo:"):
                    current_repo = line[9:].strip()
                    break
            if current_repo != gi["remote_url"]:
                if not dry_run:
                    new_lines = []
                    updated = False
                    for line in content.splitlines():
                        if line.startswith("git_repo:"):
                            new_lines.append(f"git_repo: {gi['remote_url']}")
                            updated = True
                        else:
                            new_lines.append(line)
                    if not updated:
                        new_lines.append(f"git_repo: {gi['remote_url']}")
                    meta_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                log("✓", "METADATA.md", f"git_repo → {gi['remote_url']}")
            else:
                log("·", "METADATA.md", "git_repo unchanged")

        # --- METADATA: add missing defaults ---
        added = add_missing_metadata_defaults(meta_path, dry_run)
        if added:
            log("✓", "METADATA.md", f"added defaults: {', '.join(added)}")

    # --- Print log ---
    print()
    for line in log_lines:
        print(line)

    print(f"\n{'─' * 45}")
    if dry_run:
        print(f"RESULT: {YELLOW}dry-run{RESET}  {changes} would change")
    else:
        print(f"RESULT: {changes} change{'s' if changes != 1 else ''}")
    return 0


# ---------------------------------------------------------------------------
# promote command
# ---------------------------------------------------------------------------

def cmd_promote(project_path: Path, dry_run: bool) -> int:
    """Promote a _Build prototype to the project directory and commit."""
    name     = project_path.name
    metadata = parse_metadata(project_path)

    proj_type = metadata.get("type", "")
    git_repo  = metadata.get("git_repo", "")

    print(f"\n{BOLD}Promote:{RESET} {name}")
    print(f"  Spec:   {project_path}")
    if dry_run:
        print(f"  {YELLOW}dry-run — no files will be written{RESET}")

    if proj_type and proj_type != "oneshot":
        print(f"  {YELLOW}WARNING:{RESET} type is '{proj_type}', expected 'oneshot'")
    elif not proj_type:
        print(f"  {YELLOW}WARNING:{RESET} type field not set in METADATA.md")

    # Gate: git_repo must look like a real path or URL (contains a slash)
    if not git_repo or "/" not in git_repo:
        print(f"\n  {RED}✗{RESET}  git_repo not set or not a valid path/URL")
        print(f"      Set 'git_repo: https://github.com/user/{name}.git' in METADATA.md")
        return 1

    build_path  = PROJECTS_DIR / f"{name}_Build"
    target_path = PROJECTS_DIR / name

    # Gate: _Build must exist
    if not build_path.is_dir():
        print(f"\n  {RED}✗{RESET}  Build directory not found: {build_path}")
        print(f"      Run oneshot.sh and build with an AI agent first.")
        return 1

    log_lines = []
    staged_files: list[str] = []

    def log(icon, label):
        color = GREEN if icon == "✓" else DIM
        log_lines.append(f"  {color}{icon}{RESET}  {label}")

    # Initialize target git repo if needed
    if not target_path.exists():
        if not dry_run:
            target_path.mkdir(parents=True)
            subprocess.run(["git", "init"], cwd=target_path,
                           check=True, capture_output=True)
            subprocess.run(["git", "remote", "add", "origin", git_repo],
                           cwd=target_path, check=True, capture_output=True)
        log("✓", f"Initialized {target_path.name}/ (git init + remote add origin {git_repo})")

    if dry_run:
        print(f"\n  Would rsync: {build_path.name}/ → {target_path.name}/")
    else:
        # rsync _Build/ → target/
        r = subprocess.run(
            ["rsync", "-a", "--delete", "--exclude=.git",
             f"{build_path}/", f"{target_path}/"],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            print(f"\n  {RED}✗{RESET}  rsync failed: {r.stderr.strip()}")
            return 1

        # Find latest oneshot tag for commit message
        latest_tag = ""
        try:
            r2 = subprocess.run(
                ["git", "tag", "-l", f"oneshot/{name}/*", "--sort=-version:refname"],
                cwd=SPEC_DIR, capture_output=True, text=True, timeout=5
            )
            tags = r2.stdout.strip().splitlines()
            if tags:
                latest_tag = tags[0]
        except Exception:
            pass

        commit_msg = f"Promote: {name} from {latest_tag}" if latest_tag else f"Promote: {name}"

        subprocess.run(["git", "add", "-A"], cwd=target_path,
                       check=True, capture_output=True)
        r3 = subprocess.run(["git", "diff", "--cached", "--name-only"],
                             cwd=target_path, capture_output=True, text=True)
        staged_files = [f for f in r3.stdout.strip().splitlines() if f]

        if staged_files:
            subprocess.run(["git", "commit", "-m", commit_msg],
                           cwd=target_path, check=True, capture_output=True)
            for f in staged_files[:20]:
                log("✓", f)
            if len(staged_files) > 20:
                log("·", f"... and {len(staged_files) - 20} more files")
        else:
            log("·", "No changes to commit")

    print()
    for line in log_lines:
        print(line)

    print(f"\n{'─' * 45}")
    if dry_run:
        print(f"RESULT: {YELLOW}dry-run{RESET}  would sync {build_path.name}/ → {target_path.name}/")
    else:
        n = len(staged_files)
        print(f"RESULT: {n} file{'s' if n != 1 else ''} changed — push with: git -C {target_path} push")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify, update, and promote code projects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
commands:
  verify   Check a project against CLAUDE_RULES compliance criteria.
           Shows pass/fail per rule, grouped by level, with next-level preview.
  update   Inject latest CLAUDE_RULES.md, copy templates, update METADATA.md.
           Project must already be set up (CLAUDE_RULES_START marker required).
  promote  Sync a _Build prototype to the project directory and git commit.
           Spec METADATA.md must have git_repo: set and type: oneshot.

examples:
  python3 bin/project_manager.py verify MyProject
  python3 bin/project_manager.py verify /abs/path/to/MyProject --verbose
  python3 bin/project_manager.py update MyProject --dry-run
  python3 bin/project_manager.py update /abs/path/to/MyProject
  python3 bin/project_manager.py promote MyProject
  python3 bin/project_manager.py promote MyProject --dry-run
"""
    )
    parser.add_argument("command", choices=["verify", "update", "promote"])
    parser.add_argument("project", help="Project name or absolute path")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="(verify) Show passing checks too")
    parser.add_argument("--dry-run", action="store_true",
                        help="(update/promote) Preview changes without writing")
    args = parser.parse_args()

    if args.command == "promote":
        # promote reads the spec directory (inside Specifications/), not the code project
        spec_path = SPEC_DIR / args.project
        if not spec_path.is_dir():
            print(f"ERROR: spec '{args.project}' not found in {SPEC_DIR}", file=sys.stderr)
            sys.exit(1)
        return cmd_promote(spec_path, args.dry_run)

    project_path = resolve_project(args.project)

    if args.command == "verify":
        return cmd_verify(project_path, args.verbose)
    else:
        return cmd_update(project_path, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
