# Step 3 — Iterate

Apply targeted changes to an existing prototype without rebuilding from scratch.
Changes are authored as numbered ticket files in the specification directory.

## Ticket Files

Create numbered files describing each change:

| Pattern | Use |
|---------|-----|
| `SCREEN-NNN-{Name}.md` | New or revised screen |
| `FEATURE-NNN-{Name}.md` | New or revised feature |
| `PATCH-NNN-{Name}.md` | Bug fix or targeted correction |
| `AC-NNN-{Name}.md` | Acceptance criteria |

Numbers are 3-digit, zero-padded. Applied in order. Deleted by the AI after successful apply.

## Generate and Apply

```bash
bash bin/iterate.sh MyProject > MyProject/iterate-prompt.md
```

The AI validates each ticket before implementing. Underspecified items are rejected
with a reason — the file stays for your review.

## Capture Sessions

After any interactive Claude session, extract bugs and ideas automatically:

```bash
bash bin/tran_logger.sh MyProject
```

This reads the session log, analyses git history, and writes `PATCH-NNN-tl-*.md`
and `AC-NNN-tl-*.md` files ready for the next iteration.

## Principle

Changes flow through the specification, not through ad-hoc code edits.
The specification is the source of truth. Fix code, then fix the specification to match.
