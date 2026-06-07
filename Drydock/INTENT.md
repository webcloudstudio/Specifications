# INTENT: Drydock

| Field       | Value |
|-------------|-------|
| Version     | 20260607 V1 |
| Description | Make the Prototyper interoperable with GitHub Spec Kit and publish it, built with the Prototyper itself. |
| Status      | Defined — Iterating on Multiple Engines to Refine a Working Process |

## The Question

I built a Specification Driven Design platform — the Prototyper — independently and on my own. It
converges on GitHub Spec Kit, Tessl, and AWS Kiro. The question Drydock answers is:

> How do I make the Prototyper conformant with GitHub Spec Kit — speaking its vocabulary and
> exchanging its artifacts — without surrendering the engine that already does more, and publish the
> result as a portfolio asset?

A second question runs underneath the first: **which engine builds better from the same
specification?** Drydock is built and re-built by two interchangeable engines so the process can be
refined against evidence rather than taste:

- **LLM Framework 1** — OpenAI Codex
- **LLM Framework 2** — Anthropic Claude

The same specification, the same plan, two engines, one scorecard. The methodology is the product;
the engines are swappable parts.

## Goals

1. **Conformance, not migration.** The Prototyper emits and ingests Spec Kit artifacts
   (`constitution.md`, `spec.md`, `plan.md`, `tasks.md`) and answers to Spec Kit's command surface,
   while its own engine continues to drive the build.
2. **Keep the differentiators.** The dependency-graph phasing, the content-hash Dependency Staleness
   Check, the AGILE_PLAN ticket system, and the governance Console remain the engine — they are what
   the framework has that Spec Kit, Tessl, and Kiro do not.
3. **Eat the dog food.** Build the integration through the Prototyper's own pipeline so the
   directory transition — seed → plan → console → build → refine — is itself the demonstration.
4. **Publish.** Produce a branded white paper and documentation that present the framework and this
   build as the first public release.

## Constraints

- Spec-first: never edit generated code directly; edit the specification and re-apply.
- Adapter, not rewrite: Spec Kit is a boundary layer over the existing engine, never a replacement
  for it.
- Engine-agnostic harness: the A/B comparison must run either engine from one driver.
- Do not build (oneshot) yet — plan and review first.

## Success Criteria

- A Spec Kit user, on any supported agent, can read a Prototyper project; the Prototyper can ingest
  a Spec Kit project.
- The Console renders a Spec Kit `tasks.md` as a sign-off board.
- A documented A/B build run produces a comparative scorecard between Framework 1 and Framework 2.
- The white paper and documentation are published.

## Open Questions

- **Constitution mapping.** Does `AGENT_RULES.md` (renamed from `CLAUDE_RULES.md`) render cleanly
  into Spec Kit's nine-article `constitution.md` shape, and back? Which articles do we adopt, and
  where do we deliberately diverge? *(Findings belong in `FEATURE-Constitution-Conformance.md`.)*
- **Adapter direction.** Export-only first, or bidirectional export/import from day one? What is the
  smallest export that makes a project readable by another agent? *(Findings: `FEATURE-Artifact-Adapter.md`.)*
- **Command surface.** Which command names do we expose — bare `/specify` or namespaced
  `/speckit.*` — and how thin can the delegation shim be over the existing scripts? *(Findings: `FEATURE-Command-Surface.md`.)*
- **Syntax-aware, compact injection.** How much does a compacted agent reduce the injected rules
  footprint per project, and does syntax-aware marker injection survive the rename to `AGENT_RULES`?
  *(Findings: `FEATURE-Constitution-Conformance.md`.)*
- **A/B harness.** What is the minimal driver that runs Framework 1 and Framework 2 over the same
  plan and emits `how_good_is_my_implementation` scores? *(Findings: `FEATURE-Comparative-Build.md`.)*
- **Console from specifications.** Can the Console read a `console.json` generated directly in the
  specification directory before any build exists, and be re-delivered into the target on build?
  *(Findings: `FEATURE-Console-Governance.md`.)*
