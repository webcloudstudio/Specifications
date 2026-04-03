# Step 5 — Automate

Let the AI identify specification gaps and generate focused iteration prompts
without manual analysis.

## Gap Analysis

`spec_iterate.sh` compares your specification files against the prototype, scores
quality across seven dimensions, and produces a focused prompt targeting the
highest-priority gaps:

```bash
bash bin/spec_iterate.sh MyProject
```

**Writes:**
- `REFERENCE_GAPS.md` — updated gap list with priorities
- `SPEC_SCORECARD.md` — quality rating across seven dimensions
- `SPEC_ITERATION.md` — focused prompt for 1–2 gaps

Feed `SPEC_ITERATION.md` back into the build pipeline to close the gaps automatically.

## Scorecard

`scorecard.sh` measures how well the prototype code matches the specification:

```bash
bash bin/scorecard.sh MyProject
```

Produces `SCORECARD.md` — a checklist of KPIs tracking specification-to-code alignment.
Use it to find drift before it accumulates.

## The Loop

The automation cycle: score the specification, identify gaps, generate a focused prompt,
build, score again. Each pass closes 1–2 gaps. Low-touch — review the output, not the process.
