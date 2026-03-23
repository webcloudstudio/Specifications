# Gap Analysis Prompt

You are performing a gap analysis for a oneshot-built prototype. Compare the prototype code against:
1. The specification files (authoritative — what SHOULD exist)
2. The reference implementation (informational — what DOES exist in a mature version)

## Your Task

1. Read the current `REFERENCE_GAPS.md` in the specification directory
2. Read the prototype's `routes.py`, `STUBS.md`, and key Python modules
3. Read the reference implementation's `routes.py` for feature comparison
4. Update `REFERENCE_GAPS.md` with:
   - New gaps discovered (features in spec or reference not in prototype)
   - Gaps that have been closed (check the box, note the date)
   - Priority adjustments based on what you observe
5. Keep the existing format: sections by spec filename, checkboxes, priority levels

## Rules

- DO NOT modify the reference implementation (read-only)
- DO NOT modify the prototype code (this is analysis only)
- DO update `REFERENCE_GAPS.md` in the specification directory
- Preserve existing checked items in the Closed section
- Use the priority scale: P0 (critical) → P10 (backlog)

## Output

After updating REFERENCE_GAPS.md, print a summary:

```
--- Gap Analysis Complete ---
Open gaps: N
Closed gaps: N
New gaps found: N
Priority breakdown: P0=N, P1=N, P2=N, P3=N
```
