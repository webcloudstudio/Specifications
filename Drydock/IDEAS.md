# Drydock — Ideas & Published Backlog

This is the published roadmap. Any item here becomes buildable by authoring a `FEATURE-*.md`
(with a paired `*-AC.md` for acceptance criteria) and running `bash bin/build_plan.sh Drydock` to
fold it into the next build as a phase. Adding a ticket is: add a file, run the plan.

## Conformance (near term)

- **Constitution conformance.** Rename `CLAUDE_RULES.md` → `AGENT_RULES.md` (agent-agnostic) and
  emit it into Spec Kit's `.specify/memory/constitution.md` shape. Keep the generation pipeline
  (`BUSINESS_RULES.md` → summarize) as the single source.
- **Bidirectional artifact adapter.** `speckit_export` renders a spec directory into the Spec Kit
  layout; `speckit_import` ingests a Spec Kit project into typed spec files.
- **Command surface.** A thin slash-command shim — `/specify`, `/plan`, `/tasks`, `/implement`,
  `/analyze`, `/clarify` — that delegates to the existing scripts.
- **Console governance over Spec Kit.** Extend `console_sync.py` to render a Spec Kit `tasks.md`,
  so the Console is a sign-off board over any Spec Kit project, not only an AGILE_PLAN.

## Multi-Engine & Benchmarking (the refinement loop)

- **Comparative builds (A/B by engine).** One driver runs the same plan through **LLM Framework 1
  (OpenAI Codex)** and **LLM Framework 2 (Anthropic Claude)**, producing two builds from one
  specification.
- **`how_good_is_my_implementation`.** A benchmarking harness that scores each build against the
  specification's acceptance criteria and the Dependency Staleness Check, then emits a comparative
  scorecard: which engine, which phase, which AC passed.
- **Process refinement from evidence.** Feed the scorecard back into the prompt and stack rules —
  refine the *process*, not a single build, using measured differences between engines.

## Publishing

- **The Prototyper white paper.** Branded HTML + PDF: comparison to Spec Kit / Tessl / Kiro, what the
  engine does, the Drydock build walkthrough. First public release.
- **Console screenshots and a video introduction.** Capture the board at each step; record a short
  walkthrough as the framework's introduction.
- **Roadmap publication.** Publish this backlog and its build status as a living artifact.

## Stretch

- **Spec Registry interop (Tessl-style).** Treat stack files as versioned, shareable usage specs.
- **Hooks and steering (Kiro-style).** Map Kiro steering files and event hooks onto AGENT_RULES and
  the existing CommandCenter operations.
