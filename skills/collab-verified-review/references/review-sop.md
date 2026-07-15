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

State the layers inspected and those not inspected. Consider the relevant subset of: requirement and acceptance rules, route/state/permission flow, UI/Figma, shared component contracts, API/backend contracts, static analysis, and runtime interaction. An uninspected layer is not a pass.

## Execution constraints

- Do not run build or compilation commands as a review check.
- Do not run a command with automatic fix behavior unless the user explicitly requests mutations.
- Prefer the in-app Browser for isolated page verification and a purpose-built Figma tool for design-source inspection.
- Use the Chrome plugin when the hypothesis requires the user's existing Chrome tab, authenticated profile, or installed extensions. Follow the Chrome skill's Node REPL workflow, name the session, claim only a tab returned by `openTabs()`, and finalize the session after evidence collection.
- If Chrome initialization fails, classify the UI run as blocked before changing plugin files. Plugin-cache compatibility edits require explicit user approval and must follow [the recorded process-shim compatibility procedure](../../../docs/chrome-plugin-process-shim-compatibility.md).
- Report first connection, repeated DOM/screenshot operations, and interruption recovery independently. A successful initial connection does not prove recovery behavior.

## Priority

- P0/P1: verified functional, data, security, authorization, or severe performance regression.
- P2: verified user-experience or engineering defect with material impact.
- P3: optional maintainability or style suggestion.

## Optimization suggestions

Keep optimization suggestions separate from defects and risks. Classify them by robustness, extensibility, readability, maintainability, or testability; explain the benefit and state that they require separate approval.
