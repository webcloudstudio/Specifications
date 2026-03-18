#!/usr/bin/env python3
"""
verify.py — CLAUDE_RULES Compliance Checker

Scans a projects root directory and reports compliance with CLAUDE_RULES.md
per project, calibrated to each project's declared status.

Usage:
    python3 verify.py --projects /path/to/projects
    python3 verify.py --projects /path/to/projects --json
    python3 verify.py --projects /path/to/projects --project MyProject
    python3 verify.py --projects /path/to/projects --min-status ACTIVE

Exit code: 0 if all checked projects pass, 1 if any fail.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Status levels — ordered by strictness
# ---------------------------------------------------------------------------

STATUS_ORDER = ["IDEA", "PROTOTYPE", "ACTIVE", "PRODUCTION", "ARCHIVED"]

# Rules required at each level (cumulative — each level includes all prior)
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
    ],
    "ACTIVE": [
        "metadata_has_port",
        "metadata_has_stack",
        "stack_components_have_files",
        "metadata_has_tags",
        "has_bin_dir",
        "has_start_script",
        "start_script_has_commandcenter_header",
        "scripts_have_preamble",
        "scripts_emit_game_status",
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

# Rules skipped for ARCHIVED projects (only basic metadata checked)
ARCHIVED_RULES = ["has_metadata", "metadata_has_name", "metadata_has_status", "metadata_status_valid"]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    rule: str
    passed: bool
    message: str = ""


@dataclass
class ProjectReport:
    name: str
    path: str
    status: str
    expected_level: str
    checks: list = field(default_factory=list)

    @property
    def passed(self):
        return all(c.passed for c in self.checks)

    @property
    def fail_count(self):
        return sum(1 for c in self.checks if not c.passed)

    @property
    def pass_count(self):
        return sum(1 for c in self.checks if c.passed)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_file(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except (OSError, IOError):
        return None


def parse_metadata(project_path: str) -> dict:
    """Parse METADATA.md into a flat dict. Handles simple key: value lines."""
    content = read_file(os.path.join(project_path, "METADATA.md"))
    if not content:
        return {}
    result = {}
    current_key = None
    link_lines = []
    in_links = False

    for line in content.splitlines():
        if in_links:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                if ":" in line and line[0].isalpha():
                    # New top-level key — end links section
                    in_links = False
                    result["links"] = link_lines
                    current_key = None
                else:
                    link_lines.append(stripped)
                    continue
            else:
                continue

        m = re.match(r'^(\w[\w_]*)\s*:\s*(.*)', line)
        if m:
            key = m.group(1).lower()
            val = m.group(2).strip()
            if key == "links":
                in_links = True
                link_lines = []
            else:
                result[key] = val
                current_key = key

    if in_links:
        result["links"] = link_lines

    return result


def get_bin_scripts(project_path: str) -> list:
    bin_dir = os.path.join(project_path, "bin")
    if not os.path.isdir(bin_dir):
        return []
    scripts = []
    for f in os.listdir(bin_dir):
        if f.endswith(".sh") or f.endswith(".py"):
            scripts.append(os.path.join(bin_dir, f))
    return scripts


def script_has_commandcenter_header(script_path: str) -> bool:
    content = read_file(script_path)
    if not content:
        return False
    lines = content.splitlines()[:20]
    return any("CommandCenter Operation" in line for line in lines)


def get_registered_scripts(project_path: str) -> list:
    """Return scripts that have a CommandCenter Operation header."""
    return [s for s in get_bin_scripts(project_path) if script_has_commandcenter_header(s)]


def git_status(project_path: str) -> dict:
    result = {"initialized": False, "has_remote": False, "dirty": False}
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=project_path, capture_output=True, timeout=5
        )
        if r.returncode != 0:
            return result
        result["initialized"] = True

        r = subprocess.run(
            ["git", "remote"], cwd=project_path, capture_output=True, timeout=5
        )
        result["has_remote"] = bool(r.stdout.strip())

        r = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path, capture_output=True, timeout=5
        )
        result["dirty"] = bool(r.stdout.strip())
    except Exception:
        pass
    return result


# ---------------------------------------------------------------------------
# Individual rule checks
# ---------------------------------------------------------------------------

def get_agent_context(project_path: str) -> str:
    """Read CLAUDE.md; if it's an @AGENTS.md pointer, read AGENTS.md instead."""
    claude_md = read_file(os.path.join(project_path, "CLAUDE.md")) or ""
    if claude_md.strip() == "@AGENTS.md":
        return read_file(os.path.join(project_path, "AGENTS.md")) or ""
    return claude_md


def check(rule: str, project_path: str, metadata: dict, scripts: list, registered: list) -> CheckResult:
    claude_md = get_agent_context(project_path)

    # -- IDEA level --
    if rule == "has_metadata":
        exists = os.path.isfile(os.path.join(project_path, "METADATA.md"))
        return CheckResult(rule, exists, "" if exists else "METADATA.md not found")

    if rule == "metadata_has_name":
        ok = bool(metadata.get("name"))
        return CheckResult(rule, ok, "" if ok else "METADATA.md missing 'name' field")

    if rule == "metadata_has_status":
        ok = bool(metadata.get("status"))
        return CheckResult(rule, ok, "" if ok else "METADATA.md missing 'status' field")

    if rule == "metadata_status_valid":
        status = metadata.get("status", "").upper()
        ok = status in STATUS_ORDER
        return CheckResult(rule, ok, "" if ok else f"Invalid status '{status}'. Use: {', '.join(STATUS_ORDER)}")

    # -- PROTOTYPE level --
    if rule == "metadata_has_title":
        ok = bool(metadata.get("title"))
        return CheckResult(rule, ok, "" if ok else "METADATA.md missing 'title' field")

    if rule == "metadata_has_description":
        ok = bool(metadata.get("description"))
        return CheckResult(rule, ok, "" if ok else "METADATA.md missing 'description' field")

    if rule == "has_claude_md":
        ok = os.path.isfile(os.path.join(project_path, "CLAUDE.md"))
        return CheckResult(rule, ok, "" if ok else "CLAUDE.md not found")

    if rule == "claude_md_has_dev_commands":
        ok = bool(re.search(r'^## Dev Commands', claude_md, re.MULTILINE | re.IGNORECASE))
        return CheckResult(rule, ok, "" if ok else "AGENTS.md (or CLAUDE.md) missing '## Dev Commands' section")

    # -- ACTIVE level --
    if rule == "metadata_has_port":
        ok = bool(metadata.get("port"))
        return CheckResult(rule, ok, "" if ok else "METADATA.md missing 'port' field")

    if rule == "metadata_has_stack":
        ok = bool(metadata.get("stack"))
        return CheckResult(rule, ok, "" if ok else "METADATA.md missing 'stack' field")

    if rule == "stack_components_have_files":
        stack_val = metadata.get("stack", "")
        if not stack_val:
            return CheckResult(rule, False, "No stack field to validate")
        # Find the GLOBAL_RULES/stack/ directory relative to this script
        spec_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        stack_dir = os.path.join(spec_root, "GLOBAL_RULES", "stack")
        if not os.path.isdir(stack_dir):
            # Try finding it relative to project's parent
            stack_dir = os.path.join(os.path.dirname(project_path), "Specifications", "GLOBAL_RULES", "stack")
        components = [c.strip() for c in stack_val.split("/") if c.strip()]
        missing = []
        for comp in components:
            # Case-insensitive match: "Bootstrap5" -> "bootstrap5.md"
            stack_file = os.path.join(stack_dir, comp.lower() + ".md")
            if not os.path.isfile(stack_file):
                missing.append(f"{comp} (expected GLOBAL_RULES/stack/{comp.lower()}.md)")
        ok = not missing
        return CheckResult(rule, ok, "" if ok else f"Stack components without stack files: {', '.join(missing)}")

    if rule == "metadata_has_tags":
        ok = bool(metadata.get("tags"))
        return CheckResult(rule, ok, "" if ok else "METADATA.md missing 'tags' field")

    if rule == "has_bin_dir":
        ok = os.path.isdir(os.path.join(project_path, "bin"))
        return CheckResult(rule, ok, "" if ok else "No bin/ directory")

    if rule == "has_start_script":
        ok = os.path.isfile(os.path.join(project_path, "bin", "start.sh"))
        return CheckResult(rule, ok, "" if ok else "bin/start.sh not found")

    if rule == "start_script_has_commandcenter_header":
        path = os.path.join(project_path, "bin", "start.sh")
        ok = script_has_commandcenter_header(path)
        return CheckResult(rule, ok, "" if ok else "bin/start.sh missing CommandCenter Operation header")

    if rule == "scripts_have_preamble":
        PREAMBLE = "set -euo pipefail"
        missing = []
        for s in registered:
            content = read_file(s) or ""
            if PREAMBLE not in content:
                missing.append(os.path.basename(s))
        ok = not missing
        return CheckResult(rule, ok, "" if ok else f"Missing preamble in: {', '.join(missing)}")

    if rule == "scripts_emit_game_status":
        missing = []
        for s in registered:
            content = read_file(s) or ""
            # Accept [$PROJECT_NAME], [GAME], or any [$name] pattern
            if not re.search(r'\[[\w$_]+\]\s*(Starting|Started|Stopped|Error|Service)', content):
                missing.append(os.path.basename(s))
        ok = not missing
        return CheckResult(rule, ok, "" if ok else f"No status messages ([$PROJECT_NAME] Starting/Stopped) in: {', '.join(missing)}")

    if rule == "scripts_have_logging":
        missing = []
        for s in registered:
            content = read_file(s) or ""
            if "tee -a" not in content and "LOG_FILE" not in content:
                missing.append(os.path.basename(s))
        ok = not missing
        return CheckResult(rule, ok, "" if ok else f"No log file setup in: {', '.join(missing)}")

    if rule == "claude_md_has_endpoints":
        ok = bool(re.search(r'^## Service Endpoints', claude_md, re.MULTILINE | re.IGNORECASE))
        return CheckResult(rule, ok, "" if ok else "AGENTS.md (or CLAUDE.md) missing '## Service Endpoints' section")

    if rule == "claude_md_has_bookmarks":
        ok = bool(re.search(r'^## Bookmarks', claude_md, re.MULTILINE | re.IGNORECASE))
        return CheckResult(rule, ok, "" if ok else "AGENTS.md (or CLAUDE.md) missing '## Bookmarks' section")

    # -- PRODUCTION level --
    if rule == "has_env_example_or_no_env_needed":
        has_env_example = os.path.isfile(os.path.join(project_path, ".env.example"))
        # If project has a .env or mentions env vars in CLAUDE.md, we expect .env.example
        has_env = os.path.isfile(os.path.join(project_path, ".env"))
        mentions_env = "env" in claude_md.lower() or bool(metadata.get("env_vars"))
        if has_env or mentions_env:
            ok = has_env_example
            return CheckResult(rule, ok, "" if ok else ".env.example required (project uses environment variables)")
        return CheckResult(rule, True, "no env vars detected")

    if rule == "health_endpoint_declared":
        has_health_in_metadata = bool(metadata.get("health"))
        has_health_in_scripts = any(
            "# Health:" in (read_file(s) or "")
            for s in registered
        )
        ok = has_health_in_metadata or has_health_in_scripts
        return CheckResult(rule, ok, "" if ok else "No health endpoint declared (add 'health: /health' to METADATA.md or '# Health: /path' to bin/start.sh)")

    if rule == "git_initialized":
        ok = git_status(project_path).get("initialized", False)
        return CheckResult(rule, ok, "" if ok else "Git not initialized")

    if rule == "git_has_remote":
        ok = git_status(project_path).get("has_remote", False)
        return CheckResult(rule, ok, "" if ok else "No git remote configured")

    if rule == "git_not_dirty":
        dirty = git_status(project_path).get("dirty", False)
        return CheckResult(rule, not dirty, "" if not dirty else "Working tree has uncommitted changes")

    if rule == "no_env_committed":
        env_path = os.path.join(project_path, ".env")
        if not os.path.isfile(env_path):
            return CheckResult(rule, True, "")
        try:
            r = subprocess.run(
                ["git", "ls-files", ".env"],
                cwd=project_path, capture_output=True, timeout=5
            )
            committed = bool(r.stdout.strip())
            return CheckResult(rule, not committed, "" if not committed else ".env file is committed to git — contains secrets?")
        except Exception:
            return CheckResult(rule, True, "could not check")

    if rule == "start_script_has_sigterm_trap":
        path = os.path.join(project_path, "bin", "start.sh")
        content = read_file(path) or ""
        ok = "trap" in content and "SIGTERM" in content
        return CheckResult(rule, ok, "" if ok else "bin/start.sh missing SIGTERM trap for clean shutdown")

    return CheckResult(rule, False, f"Unknown rule: {rule}")


# ---------------------------------------------------------------------------
# Project checker
# ---------------------------------------------------------------------------

def get_applicable_rules(status: str) -> list:
    status = status.upper()
    if status == "ARCHIVED":
        return ARCHIVED_RULES
    if status not in STATUS_ORDER:
        return RULES_BY_LEVEL["IDEA"]

    rules = []
    for level in STATUS_ORDER:
        rules.extend(RULES_BY_LEVEL.get(level, []))
        if level == status:
            break
    return rules


def check_project(project_path: str) -> ProjectReport:
    name = os.path.basename(project_path)
    metadata = parse_metadata(project_path)
    status = metadata.get("status", "IDEA").upper()
    if status not in STATUS_ORDER:
        status = "IDEA"

    scripts = get_bin_scripts(project_path)
    registered = get_registered_scripts(project_path)
    applicable_rules = get_applicable_rules(status)

    report = ProjectReport(
        name=name,
        path=project_path,
        status=status,
        expected_level=status,
    )

    for rule in applicable_rules:
        result = check(rule, project_path, metadata, scripts, registered)
        report.checks.append(result)

    return report


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
DIM = "\033[2m"


def print_report(reports: list, verbose: bool = False):
    total_projects = len(reports)
    passing = sum(1 for r in reports if r.passed)
    failing = total_projects - passing

    print(f"\n{BOLD}CLAUDE_RULES Compliance Report{RESET}")
    print(f"Projects scanned: {total_projects}  |  Passing: {GREEN}{passing}{RESET}  |  Failing: {RED}{failing}{RESET}\n")

    for report in sorted(reports, key=lambda r: (r.passed, r.name)):
        status_color = GREEN if report.passed else RED
        icon = "✓" if report.passed else "✗"
        fail_str = f"  {RED}({report.fail_count} failed){RESET}" if report.fail_count else ""
        print(f"  {status_color}{icon}{RESET} {BOLD}{report.name}{RESET}  [{DIM}{report.status}{RESET}]{fail_str}")

        if not report.passed or verbose:
            for c in report.checks:
                if not c.passed:
                    print(f"      {RED}✗{RESET} {c.rule}: {c.message}")
                elif verbose:
                    print(f"      {GREEN}✓{RESET} {DIM}{c.rule}{RESET}")

    print()
    return failing == 0


def print_json_report(reports: list):
    output = []
    for r in reports:
        output.append({
            "project": r.name,
            "status": r.status,
            "passed": r.passed,
            "pass_count": r.pass_count,
            "fail_count": r.fail_count,
            "checks": [{"rule": c.rule, "passed": c.passed, "message": c.message} for c in r.checks],
        })
    print(json.dumps(output, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="CLAUDE_RULES compliance checker")
    parser.add_argument("--projects", required=True, help="Root directory containing project subdirectories")
    parser.add_argument("--project", help="Check a single project by name")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all checks, not just failures")
    parser.add_argument("--min-status", help="Only check projects at or above this status level (e.g. ACTIVE)")
    args = parser.parse_args()

    projects_root = os.path.abspath(args.projects)
    if not os.path.isdir(projects_root):
        print(f"Error: {projects_root} is not a directory", file=sys.stderr)
        sys.exit(2)

    # Find project directories
    candidates = []
    for entry in sorted(os.listdir(projects_root)):
        path = os.path.join(projects_root, entry)
        if os.path.isdir(path) and not entry.startswith(".") and entry not in ("__pycache__", "venv", "node_modules"):
            candidates.append(path)

    if args.project:
        candidates = [c for c in candidates if os.path.basename(c) == args.project]
        if not candidates:
            print(f"Error: project '{args.project}' not found in {projects_root}", file=sys.stderr)
            sys.exit(2)

    # Filter by min-status
    if args.min_status:
        min_level = args.min_status.upper()
        if min_level not in STATUS_ORDER:
            print(f"Error: invalid --min-status '{min_level}'. Use: {', '.join(STATUS_ORDER)}", file=sys.stderr)
            sys.exit(2)
        min_idx = STATUS_ORDER.index(min_level)
        filtered = []
        for path in candidates:
            meta = parse_metadata(path)
            status = meta.get("status", "IDEA").upper()
            if status in STATUS_ORDER and STATUS_ORDER.index(status) >= min_idx:
                filtered.append(path)
        candidates = filtered

    if not candidates:
        print("No projects matched the criteria.")
        sys.exit(0)

    reports = [check_project(path) for path in candidates]

    if args.json:
        print_json_report(reports)
        sys.exit(0 if all(r.passed for r in reports) else 1)
    else:
        passed = print_report(reports, verbose=args.verbose)
        sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
