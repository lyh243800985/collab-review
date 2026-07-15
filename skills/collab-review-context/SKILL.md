---
name: collab-review-context
description: Build the minimum sufficient context for an auto-ops frontend code diff review. Use when reviewing a change and needing to identify its direct route, Vue component, API, state, permission, cwui, or similar-implementation dependencies without loading the entire repository.
---

# Review Context

Create a small, traceable context map for the current diff. This skill selects context; it does not read the whole repository.

## Read in levels

1. **L0 — change:** diff, changed files, linked requirement, and declared behavior.
2. **L1 — direct dependencies:** changed component or utility, route entry, directly called API, local/Vuex state, permission guard, and nearest comparable implementation.
3. **L2 — causal expansion:** read a representative consumer only when a changed shared component, request utility, route, state, or permission path could regress it.
4. **L3 — ambiguity only:** inspect history or broader conventions only when L0–L2 cannot establish the contract.

For this project, start from `ui/`. It is Vue 2 + Vue Router + Vuex and uses `@canway/cw-magic-vue`. Do not assume typecheck or automated UI tests exist without first finding them. Build commands are outside this review workflow.

## Required output

Use [context-map.md](references/context-map.md). Include what was read, why it was read, what was deliberately excluded, and facts not supported by repository evidence.

Stop expanding when the direct behavior and a minimal affected path are understood. An unrelated issue found while reading is a suggestion, not a risk item.
