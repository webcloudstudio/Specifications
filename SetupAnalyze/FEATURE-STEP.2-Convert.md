# FEATURE: LLM Conversion Agent

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Build a prompt from .imported source files + SPECIFICATION_CONTRACT and call claude -p to generate conformed output files. |
| Phase       | 2 |

## Trigger

Called by `bin/analyze_spec.sh` after STEP.1 completes (at least one `.imported` file exists).

## Prompt Assembly

The prompt sent to `claude -p` contains, in order:
1. `prompts/analyze_ingest.md` — conversion instructions: what conformed files to produce, how to split content, naming rules, header format requirements.
2. `RulesEngine/SPECIFICATION_CONTRACT.md` — the full contract (authoritative output rules).
3. Each `*.imported` file in the spec directory, labeled with its original filename.

The agent is instructed to:
- Write each output file in its own fenced code block labeled with the filename (e.g. ` ```METADATA.md `).
- Follow SPECIFICATION_CONTRACT.md file-type header format for each file.
- Apply STEP naming convention: `FEATURE-STEP.N-Name.md` (STEP in the middle of the filename).
- Include `## Open Questions` at the bottom of each spec file where appropriate.
- NOT invent details that are not derivable from the source — use placeholder text and flag it as a question instead.

## Output Parsing

`analyze_spec.sh` parses the LLM response:
- Extracts each fenced block labeled with a filename.
- Writes the block content to `$SPECS_DIR/$ProjectName/<filename>`.
- Skips any file that already exists and is conformed (no overwrite without --force).

## Success Criteria

- At minimum: METADATA.md, INTENT.md, ARCHITECTURE.md, FUNCTIONALITY.md are written.
- FEATURE-STEP.*.md files are created for each major phase or feature described in the source.
- DATABASE.md is written if the source contains schema or data model content.
- All output files have the correct SPECIFICATION_CONTRACT header format.
- `bash bin/validate.sh <ProjectName>` exits 0 or produces a low gap-count scorecard.

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| `claude` not on PATH | Error: "claude CLI not found. Install claude-code to use --analyze." |
| LLM produces no fenced blocks | Error: print raw output + "Analyze failed: no files extracted from agent response." |
| Output file write fails | Print warning per file; continue with remaining files. |

## Quality Metrics

- At least 4 conformed files produced per analyze run on a non-trivial source.
- Validate scorecard ≥ 5/7 dimensions passing after conversion.

## Open Questions

- Should the prompt use `claude -p` with streaming, or pipe to a temp file first? (Consistent with spec_iterate.sh pattern → use `claude -p`.)
- Should DATABASE.md generation require explicit database content, or should the agent infer schema from narrative descriptions?
- What is the max token budget for the SPECIFICATION_CONTRACT section? Consider using `CLAUDE_RULES_compact.md` if budget is tight.
