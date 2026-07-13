# Intent: Common.py Migration

## Goals

- Establish `common.py` as the primary shared runtime for all project scripts: if Python is available on the machine, scripts use `common.py`; otherwise they fall back to `common.sh`.
- Make `common.sh` a clone of `common.py` behavior — not a replacement, but a fallback for environments without Python. `common.sh` stays in every project but is explicitly marked as the Python-absent fallback.
- All `.sh` scripts that currently source `common.sh` should test for Python availability and delegate to `common.py` where the logic is complex or portable.
- Create `UpdateScripts/v1.01.sh` — a one-time migration script that loops through all projects in the `projects/` directory, replaces `common.sh` references with the new pattern, and validates conformance.
- Update `bin/ProjectUpdate.sh` and `bin/ProjectValidate.sh` to understand the new standard.
- Global rule: scripts are drivers, not engines. Python handles all computation; `.sh` scripts handle invocation/argument-parsing. Eventually every complex `.sh` script should have a `.bat` equivalent for Windows (but `.bat` files are NOT created now — the rule is established for future work).

## Constraints

- When replacing `common.sh` with `common.py` in a script: test for Python existence first. If `python3` is not found, fall back to `common.sh` (the clone).
- `common.sh` must be functionally equivalent to `common.py` for all behaviors that `.sh` scripts depend on.
- `.bat` files are NOT in scope for this migration — the global rule is documented but the files are not created.
- Long bash scripts are allowed ONLY if they are pure drivers (argument parsing, conditional dispatch). Computational logic belongs in Python.
- `ProjectValidate.sh` must gain a summary mode with color and metrics — this is a quality-of-life requirement for the author.

## Success Criteria

- A parity audit document exists confirming that `common.sh` and `common.py` behave identically for all behaviors used by existing `.sh` scripts.
- `UpdateScripts/v1.01.sh` successfully updates at least 3 test projects without breaking their functionality.
- `bin/ProjectValidate.sh` supports `--summary` mode that shows color-coded conformance metrics.
- `bin/ProjectValidate.sh` can classify `.sh` scripts by: uses common.sh, complexity (should move to Python), and ease to convert to `.bat`.
- The global rule (Python + Bash preferred; drivers only in Bash; two-version standard for multi-environment) is written into `RulesEngine/BUSINESS_RULES.md` and propagated to project AGENTS.md files.

## Open Questions

- Which specific behaviors of `common.sh` are NOT currently in `common.py`? (The parity audit in STEP.1 answers this.)
- Should `common.sh` actively check for Python and call `common.py` directly (via `exec python3 bin/common.py`), or should calling scripts check for Python and choose which file to source?
- For the `--summary` mode on ProjectValidate: what colorization library is acceptable in bash? (tput? ANSI codes directly? Consistent with existing bash tooling in Prototyper.)
- The `.bat` rule: should `BUSINESS_RULES.md` say "two-version requirement" for all scripts going forward, or only for scripts marked as cross-environment drivers?
