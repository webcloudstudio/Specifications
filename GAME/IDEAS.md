# Ideas

**Version:** 20260323 V1
**Purpose:** Low-friction inbox for raw ideas. Process into specs, then delete.

> Format: One idea per bullet. No formatting required. Claude processes these into ACCEPTANCE_CRITERIA.md, REFERENCE_GAPS.md, or direct spec edits when told "process ideas" or "update the specification". Processed ideas are deleted from this file.

---

- AGENT_CHECK_BIN_FIRST: Before creating a new bin/ script, search existing scripts for overlapping functionality. If a new script is created, its CommandCenter header must be complete before the task is done. Source: Atlas "check manifest before writing new code." Add as behavioral rule in BUSINESS_RULES.md under Scripts + operating principle in AGENTS.md template.

- AGENT_GUARDRAILS_SECTION: AGENTS.md may include an optional `## Guardrails` section listing project-specific agent mistakes, irreversible operations (e.g. "never delete production rows without 3 confirmations"), and discovered API constraints. Updated as mistakes recur; cap at 15 items. Source: Atlas "Learned Behaviors" guardrails. Add rule to BUSINESS_RULES.md under AGENTS.md section; add stub to spec_template/.

- LEARNED_CONSTRAINTS_IN_SPEC: When a script or integration discovers a runtime constraint (rate limit, auth expiry, batch size, timeout), document it in the relevant FEATURE-*.md under a new `## Constraints` subsection. Spec stays a living record, not just an initial plan. Source: Atlas "fix and document" + ATLAS L-Link validation step. Add to ONESHOT_BUILD_RULES.md under FEATURE expansion rules + BUSINESS_RULES.md under a new Living Documentation section.

- PROJECT_MEMORY_MD: Code projects may optionally maintain MEMORY.md at project root — curated, committed (not gitignored) facts about domain, discovered behaviors, and persistent preferences. Sections: Facts, Preferences, Learned Behaviors. Agent reads it at session start alongside AGENTS.md. Distinct from Claude auto-memory (~/.claude) which is tool-scoped; this is project-truth readable by any agent. Source: Atlas memory/MEMORY.md (markdown tier only — skip SQLite/embeddings). Add optional rule to BUSINESS_RULES.md under Project Layout.

