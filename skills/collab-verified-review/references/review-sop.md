# Verified Diff Review SOP

## Two-phase control

The first review turn is **identify and report only**. It may read code, tickets, design sources, interface contracts, and execute non-mutating checks. It must not edit product code, tests, configuration, or external systems.

After presenting prioritized findings, review coverage, checks run, and proposed smallest fix scopes, wait for the user's explicit approval. Only then enter fix and regression work. Approval for one item does not authorize changes for other findings or suggestions.

## Scope rule

A risk item must have a changed location and a causal chain from the diff to the impact. Other files or pages may be inspected only to prove that chain. Unrelated defects are non-blocking suggestions.

## Result classes

1. **Verified defect:** reproducible failure or failing check, with evidence.
2. **Verified pass:** the stated check or interaction completed as expected.
3. **Unverified risk:** plausible diff-linked hypothesis that could not be run; state the blocker.
4. **Open question or suggestion:** missing business decision, architecture choice, or unrelated observation; do not block on it.

## Evidence standard

Record the command or browser steps, environment, expected and actual result, and an artifact or log reference where available. Screenshots alone establish visual state, not request or permission behavior.

State the layers inspected and those not inspected. Consider the relevant subset of: requirement and acceptance rules, current and superseded project knowledge, route/state/permission flow, UI/Figma, shared component contracts, API/backend contracts, static analysis, and runtime interaction. An uninspected layer is not a pass.

At the Code Review gate, invoke Know All Agent explicitly. A requirement-backed review uses
`review_requirement`; a diff-only review uses `recall_project_knowledge`. If project knowledge is
unavailable, continue the diff review but classify historical compatibility as unverified.

## Execution constraints

- Do not run build or compilation commands as a review check.
- Do not run a command with automatic fix behavior unless the user explicitly requests mutations.
- Use the bundled CDP Bridge for authenticated Chrome verification and address every page by explicit `tab_id`.
- Parallelize independent tabs only. Keep dependent interactions within a tab serial, and never migrate a failed task to another tab implicitly.
- Use a purpose-built Figma MCP for design-source inspection. Do not treat a rendered web preview as structured Figma evidence.
- If CDP initialization fails, run the bundled doctor and classify the UI run as blocked before modifying browser tooling.
- Report connection, command delivery, visible behavior, network result, and recovery independently. Success at one layer does not prove the others.

## Priority

- P0/P1: verified functional, data, security, authorization, or severe performance regression.
- P2: verified user-experience or engineering defect with material impact.
- P3: optional maintainability or style suggestion.

## Optimization suggestions

Keep optimization suggestions separate from defects and risks. Classify them by robustness, extensibility, readability, maintainability, or testability; explain the benefit and state that they require separate approval.
