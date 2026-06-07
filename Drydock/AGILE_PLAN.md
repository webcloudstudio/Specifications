# AGILE_PLAN: Drydock
spec:       Drydock
target:     
plan_hash:  9647bd88eab5
spec_commit: 833556623b028c22747217f9385c5f5f5099818f
updated:    2026-06-07T18:26:08


## story 1: AGENT_RULES rename and constitution export
summary:     Rename CLAUDE_RULES.md to AGENT_RULES.md throughout the pipeline and emit a Spec Kit-compatible constitution.md as a rendered derivative.
description: Update bin/summarize_rules.sh, bin/ProjectUpdate.sh, bin/ProjectInitialize.sh, bin/project_manager.py, and all AGENTS.md references to use AGENT_RULES.md. The BUSINESS_RULES.md → summarize → AGENT_RULES.md pipeline stays as the single source. Add a second output step to bin/summarize_rules.sh that renders AGENT_RULES.md into a Spec Kit nine-article constitution.md shape, writing it alongside AGENT_RULES.md. Syntax-aware marker injection must survive the rename.
inputs:      INTENT.md, IDEAS.md
kind:        python
evidence:    STEP_S1_AGENT_RULES_RENAME.md
state:       pending

## story 2: speckit_export adapter
summary:     Build bin/speckit_export.sh that renders a Prototyper spec directory into the Spec Kit layout.
description: Create bin/speckit_export.sh (with a supporting Python module bin/speckit_export.py) that reads a Prototyper specification directory and writes Spec Kit-compatible output files: constitution.md (from AGENT_RULES.md), spec.md (merged from ARCHITECTURE.md + FUNCTIONALITY.md), plan.md (from BUILD_PLAN.md), and tasks.md (from AGILE_PLAN.md). Output goes to a .speckit/ subdirectory of the target or a path argument. Depends on the adapter direction questionnaire decision.
inputs:      INTENT.md, IDEAS.md
kind:        python
evidence:    STEP_S2_SPECKIT_EXPORT.md
state:       pending

## story 3: speckit_import adapter
summary:     Build bin/speckit_import.sh that ingests a Spec Kit project into typed Prototyper spec files.
description: Create bin/speckit_import.sh (with bin/speckit_import.py) that reads a Spec Kit project directory containing constitution.md, spec.md, plan.md, and tasks.md and writes a minimal Prototyper spec directory: AGENT_RULES.md (from constitution.md), ARCHITECTURE.md (from spec.md), AGILE_PLAN.md or BUILD_PLAN.md (from plan.md/tasks.md), and a METADATA.md with fields inferred from spec.md frontmatter. The result must pass bin/validate.sh. Depends on the adapter direction questionnaire decision and story 2 design.
inputs:      INTENT.md, IDEAS.md, STEP_S2_SPECKIT_EXPORT.md
kind:        python
evidence:    STEP_S3_SPECKIT_IMPORT.md
state:       pending

## story 4: command surface shim
summary:     Add a thin slash-command shim delegating /specify, /plan, /tasks, /implement, /analyze, and /clarify to existing bin/ scripts.
description: Create .claude/skills/ entries for each command. Each shim resolves the current project's spec directory from METADATA.md and calls the appropriate bin/ script: /specify → bin/validate.sh, /plan → bin/build_plan.sh summary, /tasks → bin/build_plan.sh --analysis, /implement → bin/oneshot_phased.sh, /analyze → bin/spec_iterate.sh, /clarify → interactive Open Questions prompt. No new logic lives in the shims. Write COMMANDS.md documenting the full surface with argument mapping. Command names are subject to the questionnaire decision.
inputs:      INTENT.md, IDEAS.md
kind:        python
evidence:    STEP_S4_COMMAND_SURFACE.md
state:       pending

## story 5: Console governance over Spec Kit tasks.md
summary:     Extend console_sync.py to render a Spec Kit tasks.md as a Console sign-off board, independent of AGILE_PLAN.md.
description: Add a speckit mode to bin/console_sync.py (invoked with a --speckit flag or detected from file presence) that reads a Spec Kit tasks.md markdown task list and writes Console-compatible tickets.json and console.json. Task checkboxes map to ticket state; unchecked → pending, checked → done. Wire the call into oneshot.sh for Spec Kit projects, or document the standalone call sequence. The console.json must be re-deliverable into the target directory on build without losing sign-off state.
inputs:      INTENT.md, IDEAS.md
kind:        python
evidence:    STEP_S5_CONSOLE_SPECKIT.md
state:       pending

## story 6: A/B comparative build harness
summary:     Build bin/ab_build.sh, a driver that runs Framework 1 (OpenAI Codex) and Framework 2 (Anthropic Claude) over the same plan and records parallel build outputs.
description: Create bin/ab_build.sh that accepts ProjectName and TargetDir, clones the target to two sibling directories (TargetDir_openai, TargetDir_claude), and calls bin/oneshot_phased.sh against each using an engine selector (env var or flag). The driver runs both engines to completion, waits, and records engine name, timing, phase count, and exit code per run to data/ab_runs.jsonl. Engines must not share mutable state. Exact engine integration depends on the A/B harness questionnaire decision.
inputs:      INTENT.md, IDEAS.md
kind:        python
evidence:    STEP_S6_AB_HARNESS.md
state:       pending

## story 7: implementation scoring (how_good_is_my_implementation)
summary:     Build bin/score_build.sh that scores a build against the specification's acceptance criteria and emits a comparative scorecard.
description: Create bin/score_build.sh that reads AGILE_PLAN.md for AC items, then for each assertion runs the corresponding pytest check and for each guardrail runs an LLM judge against the built code. Writes data/scorecard.json (per-AC pass/fail/skip with reason) and docs/scorecard.html. When called with two target directories, emits a side-by-side comparison table: AC text, pass/fail per engine, phase. The script must never mutate the directories it scores. Depends on story 6 for the two-directory call convention.
inputs:      INTENT.md, IDEAS.md, STEP_S6_AB_HARNESS.md
kind:        python
evidence:    STEP_S7_SCORING.md
state:       pending

## story 8: white paper and roadmap publication
summary:     Author and render the Prototyper white paper (HTML + PDF) and publish the Drydock backlog as a living roadmap artifact.
description: Author docs/whitepapers/prototyper.md covering: the framework's differentiators versus Spec Kit/Tessl/Kiro, the Drydock build walkthrough, and the A/B methodology. Run bin/build_whitepaper.sh to produce docs/prototyper.html and docs/prototyper.pdf. Extend bin/build_documentation.sh (or add bin/build_roadmap.sh) to render the Drydock IDEAS.md backlog into docs/roadmap.html with per-item build status derived from AGILE_PLAN.md state. Both artifacts must build without errors.
inputs:      INTENT.md, IDEAS.md
kind:        analysis
evidence:    STEP_S8_WHITEPAPER.md
state:       pending

## ac 1: AGENT_RULES.md is the only rules file injected by ProjectUpdate.sh; CLAUDE_RULES.md is no longer written or referenced in any injected project
parent:    story 1
origin:    dev
kind:      guardrail
state:     open

## ac 2: BUSINESS_RULES.md → bin/summarize_rules.sh pipeline produces a valid AGENT_RULES.md with an incremented version after the rename
parent:    story 1
origin:    dev
kind:      assertion
state:     open

## ac 3: constitution.md output contains all nine Spec Kit articles without raw Prototyper-internal content leaking into the article bodies
parent:    story 1
origin:    dev
kind:      guardrail
state:     open

## ac 4: bin/ProjectValidate.sh reports no CLAUDE_RULES references in any project that has been updated after story 1 is shipped
parent:    story 1
origin:    dev
kind:      assertion
state:     open

## ac 5: speckit_export writes constitution.md, spec.md, plan.md, and tasks.md to the output directory without error for a real Prototyper project
parent:    story 2
origin:    dev
kind:      assertion
state:     open

## ac 6: speckit_export is idempotent — running it twice on the same source produces identical output files
parent:    story 2
origin:    dev
kind:      guardrail
state:     open

## ac 7: speckit_import produces a spec directory that passes bin/validate.sh for a real Spec Kit project
parent:    story 3
origin:    dev
kind:      assertion
state:     open

## ac 8: speckit_import never overwrites an existing file in the destination without an explicit --force flag
parent:    story 3
origin:    dev
kind:      guardrail
state:     open

## ac 9: each command shim delegates to exactly one existing bin/ script with no logic added in the shim body
parent:    story 4
origin:    dev
kind:      guardrail
state:     open

## ac 10: COMMANDS.md documents every exposed command with its delegated script and argument mapping
parent:    story 4
origin:    dev
kind:      assertion
state:     open

## ac 11: Console renders a Spec Kit tasks.md with at least one ticket visible on the board in the correct column
parent:    story 5
origin:    dev
kind:      assertion
state:     open

## ac 12: a Console sign-off on a Spec Kit task is persisted to console_state.sqlite and reflected on board reload
parent:    story 5
origin:    dev
kind:      assertion
state:     open

## ac 13: the two build directories produced by ab_build.sh share no mutable state during or after the run
parent:    story 6
origin:    dev
kind:      guardrail
state:     open

## ac 14: ab_build.sh records engine name, wall-clock time, phase count, and exit code in data/ab_runs.jsonl for every run
parent:    story 6
origin:    dev
kind:      assertion
state:     open

## ac 15: score_build.sh emits scorecard.json with a pass/fail/skip result for every AC in AGILE_PLAN.md
parent:    story 7
origin:    dev
kind:      assertion
state:     open

## ac 16: score_build.sh never writes to or deletes files in the build directory it is scoring
parent:    story 7
origin:    dev
kind:      guardrail
state:     open

## ac 17: comparative scorecard shows AC text and pass/fail per engine side by side when two target directories are supplied
parent:    story 7
origin:    dev
kind:      assertion
state:     open

## ac 18: bin/build_whitepaper.sh renders prototyper.md to HTML and PDF without errors
parent:    story 8
origin:    dev
kind:      assertion
state:     open

## ac 19: roadmap page lists every backlog item with its current AGILE_PLAN.md state; the page rebuilds automatically when the plan changes
parent:    story 8
origin:    dev
kind:      assertion
state:     open
