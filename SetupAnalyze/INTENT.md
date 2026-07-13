# Intent: Setup Analyze

## Goals

- Add `--analyze` flag to `bin/setup.sh` that accepts a directory containing non-conformed or raw specification files and converts them into a fully conformed specification directory using an LLM agent.
- The agent reads `RulesEngine/SPECIFICATION_CONTRACT.md` as the governing contract for what the output must look like.
- The conversion must be simple and clear enough for novice users — errors and guidance should be human-readable, not technical.
- Save the ingestion format as a reusable template (in `setup.template` or similar) so future non-conformed formats can be ingested with minimal friction.
- Auto-trigger: when `setup.sh --create` detects a directory with the correct project name but wrong/non-conformed files (i.e. no METADATA.md or no INTENT.md), it should fall through to `--analyze` automatically.

## Constraints

- The contract location (`RulesEngine/SPECIFICATION_CONTRACT.md`) is authoritative. The AGENTS.md should document this location but NOT embed or duplicate the contract text.
- Original non-conformed files are preserved with a `.imported` postfix so they are not deleted and can be referenced. They are not processed again.
- The LLM agent produces conformed files but does not overwrite existing conformed files (same safety as `setup.sh --update`).
- Must work for novice users: the CLI help text and any error messages should be plain English with no assumed knowledge of the contract structure.

## Success Criteria

- Running `bash bin/setup.sh <ProjectName> --analyze` on a directory containing only `Initial_Spec.md` produces a complete conformed set of spec files (METADATA.md, INTENT.md, ARCHITECTURE.md, FUNCTIONALITY.md, and relevant FEATURE/DATABASE/SCREEN files).
- The original `Initial_Spec.md` is renamed to `Initial_Spec.md.imported`.
- Running `bash bin/validate.sh <ProjectName>` after analyze exits 0 or produces actionable gap output.
- A format template is saved for the ingested file type (keyed by heuristic: number of sections, presence of INTENT / PROJECT PLAN headings, etc.).
- A novice user can run the full flow — `setup.sh <name> --analyze` — with no prior knowledge of SPECIFICATION_CONTRACT.md.

## Open Questions

- Where exactly should the ingestion template be stored? Options: `RulesEngine/ingest_templates/`, `setup.template` file at Prototyper root, or a `prompts/analyze_ingest.md` prompt file.
- Should `--analyze` run `validate.sh` automatically at the end and print the scorecard, or leave that as a manual step?
- Should the agent be invoked via `claude -p` (same pattern as spec_iterate.sh) or a different mechanism?
- When a directory has SOME conformed files and SOME non-conformed, how does --analyze decide what to skip vs. regenerate?
