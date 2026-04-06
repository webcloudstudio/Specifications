# Prototype Iteration Rules

**Version:** 20260323 V1
**Purpose:** Agent behavior rules for iterating oneshot-built prototypes. Injected by oneshot.sh into prototype AGENTS.md.

> These rules are ONLY active when working in a prototype directory built by oneshot.sh. They enable the specification feedback loop.

---

## When Working in This Prototype

### 1. Fix code, then fix the specification

After any code change that reveals a specification gap or defect, update the corresponding file in the Specifications directory in the same session.

- Defect found → fix code → add MUST statement to `ACCEPTANCE_CRITERIA.md` → update the target specification file
- Feature added → update or create the relevant `SCREEN-*.md` or `FUNCTIONALITY.md`
- Gap closed → check the box in `REFERENCE_GAPS.md`

### 2. Process IDEAS.md on request

When told "process ideas" or "update the specification":
1. Read `IDEAS.md` in the Specifications directory
2. For each idea, determine where it belongs:
   - Defect/constraint → `ACCEPTANCE_CRITERIA.md`
   - Missing feature → `REFERENCE_GAPS.md`
   - Specification clarification → direct edit to `SCREEN-*.md` or `FUNCTIONALITY.md`
3. Delete each processed idea from `IDEAS.md`
4. Commit with message: "Process ideas: [summary]"

### 3. Session summary

At the end of each session that modifies specification files, print a summary:

```
--- Specification Updates ---
ACCEPTANCE_CRITERIA.md: +2 criteria (Documentation Serving, Script Conventions)
REFERENCE_GAPS.md: 1 gap closed (Heartbeat Polling)
SCREEN-MONITORING.md: updated health table section
IDEAS.md: 3 ideas processed, 0 remaining
```

### 4. Never modify the reference implementation

The reference implementation directory (e.g., `../GAME/`) is **read-only**. Compare against it for guidance but never change it.

### 5. Documentation directory standard

All documentation MUST live in `docs/` (not `doc/`). There is no `doc/` directory. When creating or referencing documentation paths, always use `docs/`.

### 6. Line endings

All files in `bin/` MUST use Unix line endings (LF). No carriage returns (`\r`). This is a WSL environment where Windows line endings cause script failures.

### 7. Specification directory location

The specification files for this project are at: `../Specifications/{PROJECT_NAME}/`

Key files:
- `ACCEPTANCE_CRITERIA.md` — testable MUST/MUST NOT statements
- `REFERENCE_GAPS.md` — features not yet specified, by target file
- `IDEAS.md` — raw ideas inbox (process on request)
- `SCREEN-*.md`, `FUNCTIONALITY.md` — the actual specifications

### 8. Build reference tracking

When adding to `ACCEPTANCE_CRITERIA.md` or `REFERENCE_GAPS.md`, note the current oneshot tag in the `Build-ref:` header if it has changed since the file was last updated.

### 9. Capture before iterate

After any interactive session that modifies code, run from the Specifications directory:

```bash
bash bin/tran_logger.sh <PROJECT>
```

This reads the session log and produces CHANGE tickets, acceptance criteria, and ideas. Review the output, then run `iterate.sh` for the next formal apply. Do not start an iterate session without first running tran_logger.sh if you have done interactive prototype work since the last iterate.
