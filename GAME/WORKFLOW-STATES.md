# Feature: Workflow States

**spec_v4 · 2026-03-11 · [ROADMAP]**

---

## Purpose

A structured lifecycle for feature development. Each feature ticket moves from first
idea to done, with the platform prompting the right activities at each stage and
preserving an audit trail of decisions and AI work.

---

## What the User Can Do

- Create feature tickets for any project
- Move tickets through states with a clear purpose at each step
- Attach notes, images, or audio to any ticket at any state
- See all tickets per project in the dashboard
- See tickets across all projects in a Kanban view

---

## The States

| State | What It Means |
|-------|--------------|
| IDEA | First capture — incomplete, not yet reviewed |
| PROPOSED | Has a summary and plan; ready for discussion |
| READY | Has acceptance criteria; scheduled for AI work |
| IN DEVELOPMENT | AI session is running or recently finished |
| TESTING | AI work complete; human validation in progress |
| DONE | Accepted and complete |

**Note:** The AI development session itself is not a state — it is work that happens
between READY and TESTING. The ticket enters IN DEVELOPMENT when work begins and moves
to TESTING when the session ends.

---

## State Transitions

```
IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE
                                  ↑              |
                               READY ←───────────┘  (rework: simple)
                             PROPOSED ←─────────────  (rework: redesign)
```

---

## Screens

### Tickets List (within Project Detail)

Compact list grouped by state. Per row: title, state badge, last updated. New Ticket button.

### Ticket Detail

- Title and description
- Attachments (notes, audio, images)
- Feature plan (appears at PROPOSED)
- Acceptance criteria (appears at READY)
- AI Transaction Log (read-only; populated after IN DEVELOPMENT)
- Test notes (appears at TESTING)
- State history timeline

### All-Projects Kanban (separate page)

Columns per state. Cards show project name and ticket title. Filter by project or tag.

---

## The AI Transaction Log

When AI development completes, a transaction log is written for the ticket.
This is the audit trail for AI-generated work.

**Required fields:**
- Acceptance Criteria: what was required
- Features Implemented: what was built
- Intent: why each major decision was made

This log is stored with the ticket. It enables human review, rollback understanding,
and resumption in a future session.

---

## Persistence

Ticket data is stored in the platform database. The transaction log may also be
committed to the project repository as a file for git-based traceability.

---

## Data In / Out

**Reads:** User input, USAGE-ANALYTICS (cost data for READY state scheduling)

**Writes:** Current ticket state → CONTROL-PANEL display

---

## Out of Scope

- Running the AI session → external tool (Claude Code or equivalent)
- Token cost tracking → USAGE-ANALYTICS
