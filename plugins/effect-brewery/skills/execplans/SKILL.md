---
name: execplans
description: >-
  ExecPlan authoring and maintenance. Use this skill WHENEVER you need to create, update,
  or review an ExecPlan. Also use when the user asks to "write a plan", "create an ExecPlan",
  "design a feature", or mentions execution plans, design documents, or implementation specs.
  The full specification lives in references/PLANS.md — read it before writing any ExecPlan.
---

# ExecPlans

An ExecPlan is a self-contained design-and-implementation document that a coding agent (or a human novice) can follow to deliver a working feature or system change. ExecPlans are living documents — they are revised continuously as work proceeds, discoveries occur, and design decisions are finalized.

## When to Write an ExecPlan

Write an ExecPlan for complex features, significant refactors, or multi-step changes that benefit from an explicit execution narrative. Do not write one for typo fixes, small documentation edits, or single-file changes where the intent is obvious.

## Before You Start

Read the full ExecPlan specification in [references/PLANS.md](references/PLANS.md). That file is the authoritative source for all requirements, formatting rules, mandatory sections, and the skeleton template. Do not write an ExecPlan from memory — always re-read the spec first.

## Quick Reference

Every ExecPlan must include these mandatory sections:

1. **Purpose / Big Picture** — why the work matters, what someone gains after this change
2. **Progress** — checkbox list with timestamps (the only place checklists are allowed)
3. **Surprises & Discoveries** — unexpected behaviors, bugs, insights with evidence
4. **Decision Log** — every decision with rationale and date
5. **Outcomes & Retrospective** — achievements, gaps, lessons learned
6. **Context and Orientation** — current state as if the reader knows nothing
7. **Plan of Work** — sequence of edits and additions in prose
8. **Concrete Steps** — exact commands, working directories, expected output
9. **Validation and Acceptance** — how to test and observe success
10. **Idempotence and Recovery** — safe retry and rollback paths
11. **Artifacts and Notes** — important transcripts, diffs, snippets

## Non-Negotiable Requirements

- Every ExecPlan must cover the smallest coherent, focused (not necessarily full) vertical slice.
- Every ExecPlan must be architecturally sound — **never** operationally oversized (Ask: "Am I bundling unrelated concerns? Could this be done in one pass?").
- Every ExecPlan must be fully self-contained — all knowledge needed for a novice to succeed.
- Every ExecPlan must be verifiable — if it can not be deterministically verified, it's not an ExecPlan.
- Every ExecPlan must produce a demonstrably working behavior, not merely code changes.
- Every ExecPlan must define every term of art in plain language.
- Write in plain prose. Prefer sentences over lists. Checklists only in Progress.
- Anchor with observable outcomes — commands to run and outputs to expect.

## File Conventions

- Store ExecPlans in `docs/execplans/` at the repository root.
- Naming: `YYYYMMDD-<daily-counter>-<brief-description>.md` (e.g., `20260429-02-dual-writes.md` - always get the current date first (from the system)).

## Living Document Rules

- Update Progress at every stopping point.
- Record every design decision in the Decision Log with rationale.
- Capture surprises with evidence snippets.
- When you revise a plan, reflect changes across all sections.
- Write a note at the bottom of the plan describing each revision and why.
