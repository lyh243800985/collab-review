---
name: collab-ui-verify
description: Verify an auto-ops frontend diff hypothesis through real browser interaction and retain reproducible evidence. Use for changed Vue/cwui UI, routes, forms, tables, dialogs, permissions, request flows, shared UI utilities, or supplied Figma links when a code-only review cannot establish whether a regression occurs.
---

# UI Evidence Verification

Prove or disprove one diff-linked hypothesis through the running application. Use the plugin's CDP Bridge to reuse the user's authenticated Chrome session and bind all work to an explicit `tab_id`.

## Before interacting

1. Require a `collab-review-reachability` plan. Do not start normal interaction unless its readiness is `ready`.
2. For a `probe` plan, perform its single bounded read-only probe, then return for replanning as `ready` or `blocked`.
3. Confirm the complete URL, explicit target, account/permission, fixture identity, environment, expected state, safe boundary, time budget, and stop conditions.
4. If Figma is supplied, read the relevant node through the Figma MCP before comparing design behavior.
5. Create or reuse an isolated review tab group. Different tabs may run in parallel; dependent actions within one tab stay serial.
6. Avoid final submit or destructive actions unless explicitly authorized and backed by recoverable test data.
7. If CDP is unavailable, run the plugin doctor and report the run as blocked; do not silently switch tabs or browser profiles.

## Execute and retain evidence

1. Exercise only the smallest state chain needed for the hypothesis.
2. Use one exact readiness probe per tab and batch independent DOM facts where possible. Default each exact wait to at most 5 seconds and each route chain to at most 120 seconds unless the plan justifies another budget.
3. On a stop condition, mark the path blocked immediately; do not search other records, routes, roles, or controls by trial and error.
4. Capture visible state and relevant DOM, console, request, response, download, or navigation evidence.
5. Treat click acknowledgement, rendered UI, and business request result as separate facts.
6. If a command times out, inspect side effects before retrying; an unknown outcome is not a failed click.
7. Record reproduced, not-reproduced, or blocked. A blocked run cannot confirm a defect.
8. Before returning, compare the textual conclusion with DOM and screenshot facts; unresolved contradictions are `blocked`, not a pass or defect.

Use [ui-evidence.md](references/ui-evidence.md). A selector or one navigation step may be adjusted in place; changed business conditions, missing data, new routes, or new hypotheses must return to reachability planning. Do not claim UI or design noncompliance from source inspection alone when the page can be executed.
