# Specification Driven Design

A methodology for building software from structured specifications using AI agents.

## Core Idea

You write concise specification files describing what to build. An opinionated
technology stack and business rules define how to build it. A script assembles
everything into a single prompt. The AI builds the application in one pass.

The specification directory is the source of truth. The code is a derived artifact.

## The Pipeline

```
Setup → OneShot → Iterate → Merge → Automate
```

1. **Setup** — Scaffold specification files from templates, or reverse-engineer an existing project
2. **OneShot** — Validate, assemble, and generate a complete AI build prompt
3. **Iterate** — Author change tickets, generate focused iteration prompts
4. **Merge** — Squash-merge the feature branch into the base branch
5. **Automate** — AI-scored gap analysis feeds back into the pipeline

## What Makes It Work

**Structured inputs.** Each file type has a defined format — tables and bullets, not prose.
The AI agent knows exactly what to expect.

**Opinionated stack.** Prescriptive patterns per technology (`flask.md`, `sqlite.md`, etc.)
eliminate ambiguity. The AI copies patterns, not interprets guidelines.

**Rules engine.** `CLAUDE_RULES.md` defines agent behavior across all projects — file
structure, naming, error handling, security. Every project gets the same contract.

**Traceability.** Every build is git-tagged. Specification diffs between builds show exactly
what changed and why. Scorecards track drift between specification and code.

## When to Use It

Best for small-to-medium applications built on a known stack. The methodology assumes
the AI can build the entire application from the specification in one pass, then
iterate on it through targeted tickets. Complex multi-service architectures or
unfamiliar technology stacks need a different approach.
