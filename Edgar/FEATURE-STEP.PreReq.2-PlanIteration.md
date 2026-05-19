# FEATURE: Research and Plan Iteration

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Research comparables, iterate the full project plan, and get explicit author approval before any coding begins. |
| Phase       | PreReq |

## Purpose

The author explicitly requires a back-and-forth discussion before coding. This feature defines the research and conversation gate that must complete before STEP.1.

## Research Tasks

1. **Comparable products**: What do Calcbench, Sentieo, Visible Alpha, Intrinio, and other data providers offer for BDC/private credit analysis? What is free vs. paid?
2. **Is this a product?**: Is EDGAR-based private credit stress analysis already commercialized? If so, what is our differentiation (free, custom signals, on-machine learning)?
3. **On-machine LLM feasibility**: For the language-based signal scoring (hard-to-parse narrative), what is the realistic path for on-machine processing on a laptop? (ollama, llama.cpp, small models vs. API calls)
4. **Backtesting**: What data is needed to backtest the scoring system against known stress events (TCPC, BCRED, Ares, Apollo)? Is 8-quarter history sufficient?

## Discussion Gate

**The author must confirm the iterated plan before any STEP.1 through STEP.6 coding begins.**

The discussion should cover:
- Which library/API approach from PreReq 1 is approved
- Whether the 12-metric set is the right starting point or needs revision
- The learning loop design (LLM scores → JSONL rules → re-scoring) — is this the right architecture?
- Phase scope: what is in Phase 1 MVP vs. deferred to Phase 2/3?

## Output

- Updated INTENT.md (resolve open questions from PreReq 1 and this research)
- Updated ARCHITECTURE.md (reflect chosen library/API decisions)
- Updated BUILD_PLAN.md (phase assignments confirmed)

## Success Criteria

- Author has reviewed and approved the iterated plan in a conversation.
- All `## Open Questions` in INTENT.md and ARCHITECTURE.md are resolved or explicitly deferred.
- STEP.1 coding can begin with a clear, agreed scope.

## Open Questions

- No coding questions — this is a research and conversation milestone.
