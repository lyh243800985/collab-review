---
name: collab-review-reachability
description: Trace a diff-linked frontend control or state through Vue render guards, computed state, permissions, route parameters, runtime configuration, API fields, and interaction prerequisites to produce an executable browser verification plan. Use after review hypotheses and before browser verification when Codex must determine which data makes a button, dialog, row, tab, or state appear instead of exploring the page by trial and error.
---

# Review State Reachability

Compile a browser hypothesis into a reachable UI state before opening the browser. This skill plans verification; it does not execute browser actions.

## Trace the target state

1. Start from the changed control or observable state named by the hypothesis.
2. Trace template guards, computed values, refs/Vuex state, permissions, route/query values, runtime configuration, API response fields, and prerequisite interactions.
3. Record the exact predicate required from each dependency. Do not stop at names such as `canShowButton`; trace how the value is produced.
4. Separate proven repository facts from environment facts and unknown backend behavior.
5. Stop expanding when every condition is either satisfiable, blocked, or explicitly unknown.

## Resolve test data

Prefer data sources in this order:

1. A stable fixture or identifier supplied by the user or repository.
2. A read-only API query using predicates derived from code.
3. A list page with an exact existing filter.
4. A single bounded browser probe.

Do not browse multiple records by trial and error. Do not create, edit, submit, or delete data merely to make a state reachable without explicit authorization and a recovery plan.

## Decide readiness

Read [reachability-plan.md](references/reachability-plan.md) and produce one plan for every browser hypothesis.

- `ready`: all required conditions and a safe fixture are known.
- `probe`: one bounded read-only observation can resolve the remaining condition.
- `blocked`: required data, permission, configuration, backend capability, or safe authority is unavailable.
- `not_applicable`: the hypothesis can be settled statically and does not need a browser.

Only `ready` plans enter normal browser interaction. A `probe` plan gets one bounded probe and must then become `ready` or `blocked`.

## Browser handoff

The handoff must contain the full URL, explicit target, fixture identity, ordered state chain, exact expected observation, evidence type, safe-action boundary, per-wait limit, total route budget, and stop conditions. Never hand the browser worker a request such as “open the page and investigate.”

When the page contradicts the plan, the browser worker may adjust a selector or one navigation step. A changed business condition, missing fixture, new route, or new hypothesis returns to this skill for replanning.
