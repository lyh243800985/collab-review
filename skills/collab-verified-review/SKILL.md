---
name: collab-verified-review
description: Orchestrate an evidence-driven code diff review for the current auto-ops frontend. Use when asked to review a PR, branch, patch, or code diff and the review should validate suspected regressions with project checks or real UI behavior rather than only comment on code style.
---

# Verified Diff Review

Run a scoped, two-phase review of the supplied diff. Treat it as a change review, not a whole-repository audit.

Read [review-sop.md](references/review-sop.md) before reviewing. This is the only user-facing entry point; use the internal playbooks below as needed.

## Phase 1 — Identify and report (default first turn)

1. Obtain the target diff and the associated requirement or ticket. State the base revision if known.
2. Build only the minimum context needed to interpret that diff. Use [context-map.md](references/context-map.md).
3. Inspect the relevant layers and state both coverage and exclusions: requirement and acceptance behavior; UI/Figma; route, state, permission and data flow; shared component/API contracts; backend endpoint or interface contract when the diff depends on one; and scoped static checks. Do not claim an unavailable layer was checked.
4. Turn observations into falsifiable hypotheses. Use [risk-hypothesis.md](references/risk-hypothesis.md). Reject hypotheses without a diff-to-impact causal chain as non-blocking suggestions.
5. Run only applicable, non-mutating static checks, following [static-verification.md](references/static-verification.md). Never run a build as part of review. For UI or interaction risks, prepare and run an MCP-first browser verification plan using [ui-evidence.md](references/ui-evidence.md). Expand only to prove a diff-linked impact.
6. Report every identified item using [report-template.md](references/report-template.md): verified defects first, then unverified diff-linked risks, then verified passes. List optimization suggestions separately for robustness, extensibility, readability, maintainability, and testability. State the validation performed and blocked validation.
7. End Phase 1 by asking for a decision. Recommend the smallest fix scope, but **do not edit product code, tests, configuration, or external systems** unless the user explicitly approves a specified fix scope.

## Phase 2 — Fix and regression (only after explicit approval)

1. Restate the approved items and excluded items before editing.
2. Make the smallest approved code change. Do not silently fix suggestions or risks outside approval.
3. Run proportionate regression checks, including the affected interaction path when available. Never run a build as a review check.
4. Report changed files, actual verification evidence, remaining blockers, and any item deferred by the user.

## Boundaries

- Do not turn unrelated legacy defects, style preferences, or broad refactors into review risks.
- Do not invent business rules. Record missing requirements as an open question.
- Do not claim a UI verification ran unless its actual steps and evidence are available.
- Prefer purpose-built browser and Figma MCP tools. Do not use the Codex Chrome plugin as the default or fallback in this environment.
- Ask for direction before an action that mutates production data or external systems.
- Treat an interface or backend contract that is absent, undocumented, or unverified as an open question or unverified risk, not permission to infer a frontend implementation.
