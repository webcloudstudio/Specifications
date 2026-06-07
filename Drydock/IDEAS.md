# Drydock — Ideas & Published Backlog

The detail behind `INTENT.md`. This is the published roadmap. Any item here becomes buildable by
authoring its specification files and running `bash bin/build_plan.sh Drydock` to fold it into the
next build. Adding a ticket is: add a file, run the plan.

## Goals

- **Conformance, not migration.** Emit and ingest Spec Kit artifacts (`constitution.md`, `spec.md`,
  `plan.md`, `tasks.md`) and answer to its command surface, while the existing engine drives the build.
- **Keep the differentiators.** Dependency-graph phasing, the Dependency Staleness Check, the
  AGILE_PLAN ticket system, and the governance Console remain the engine.
- **Eat the dog food.** Build the integration through the methodology itself.
- **Publish.** A branded white paper and documentation as the first public release.

## Constraints

- Specification first: never edit generated code directly; edit the specification and re-apply.
- Adapter, not rewrite: Spec Kit is a boundary layer over the engine, never a replacement.
- Engine-agnostic harness: the A/B comparison runs either engine from one driver.

## Success Criteria

- A Spec Kit user, on any supported agent, can read a Drydock project; Drydock can ingest a Spec Kit
  project.
- The Console renders a Spec Kit `tasks.md` as a sign-off board.
- A documented A/B build produces a comparative scorecard between the two engines.
- The white paper and documentation are published.

## The Two Engines

The same specification is built by two interchangeable engines so the *process* is refined against
evidence, not taste:

- **LLM Framework 1** — OpenAI Codex
- **LLM Framework 2** — Anthropic Claude

Same specification, same plan, two engines, one scorecard.

## Conformance Backlog

- **Constitution conformance.** Rename `CLAUDE_RULES.md` → `AGENT_RULES.md` (agent-agnostic) and
  emit it into Spec Kit's `constitution.md` shape, keeping the generation pipeline as the single
  source.
- **Bidirectional artifact adapter.** `speckit_export` renders a spec directory into the Spec Kit
  layout; `speckit_import` ingests a Spec Kit project into typed spec files.
- **Command surface.** A thin shim — `/specify`, `/plan`, `/tasks`, `/implement`, `/analyze`,
  `/clarify` — delegating to the existing scripts.
- **Console governance over Spec Kit.** Extend `console_sync.py` to render a Spec Kit `tasks.md`, so
  the Console is a sign-off board over any Spec Kit project.

## Multi-Engine & Benchmarking

- **Comparative builds (A/B by engine).** One driver runs the same plan through Framework 1 and
  Framework 2, producing two builds from one specification.
- **`how_good_is_my_implementation`.** A harness that scores each build against the specification's
  acceptance criteria and the Dependency Staleness Check, then emits a comparative scorecard.
- **Process refinement from evidence.** Feed the scorecard back into the prompt and stack rules.

## Publishing

- **The Drydock white paper.** Branded HTML + PDF: the methodology, then a comparison appendix.
- **Console screenshots and a video introduction.** Capture the board; record a short walkthrough.
- **Roadmap publication.** Publish this backlog and its build status as a living artifact.

## A Single Command

Wrap the scripts behind one entry point — `drydock <verb>` as a synonym layer:
`drydock new | intent | plan | build | oneshot | console | iterate | rules | validate`.

## Questions to Resolve

- Constitution mapping: which Spec Kit articles to adopt, and where to diverge.
- Adapter direction: export-only first, or bidirectional from the start.
- Command names: bare `/specify` or namespaced `/speckit.*`.
- Compact injection: how much a compacted agent reduces the injected rules footprint per project.
- A/B harness: the minimal driver that runs both engines over one plan.
- Console from specifications: rendering `console.json` in the spec directory before any build exists.

## Stretch

- **Spec Registry interop (Tessl-style).** Stack files as versioned, shareable usage specs.
- **Hooks and steering (Kiro-style).** Map steering files and event hooks onto agent rules and the
  existing CommandCenter operations.
