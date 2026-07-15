---
name: collab-ui-verify
description: Verify an auto-ops frontend diff hypothesis through real browser interaction and retain reproducible evidence. Use for changed Vue/cwui UI, routes, forms, tables, dialogs, permissions, request flows, shared UI utilities, or supplied Figma links when a code-only review cannot establish whether a regression occurs. Prefer the in-app Browser and purpose-built Figma tools; use the Chrome plugin when existing Chrome tabs, login state, profile data, or extensions are required.
---

# UI Evidence Verification

Prove or disprove one diff-linked hypothesis through the running application. Prefer the in-app Browser for navigation, interaction, screenshots, console, and network evidence. Use the Chrome plugin through its documented Node REPL client when verification depends on the user's existing Chrome state. Use only the browser API exposed by the selected skill.

## Before interacting

1. Confirm the route, account/permission, test data, and environment needed for the hypothesis.
2. State the minimal steps, expected behavior, and observations to capture.
3. If a Figma URL or node is supplied, read it with the Figma MCP before comparing design or interaction details.
4. Select Chrome only when existing tabs, authentication, profile data, or extensions materially affect the hypothesis. State the selection reason.
5. If the selected browser surface is unavailable or cannot access the required session, record the blocker. Do not silently switch surfaces or edit plugin files. Do not create, delete, or alter production data without explicit authorization.
6. When Chrome initialization fails with a process-shim error, consult [the local compatibility record](../../docs/chrome-plugin-process-shim-compatibility.md). Plugin-cache edits require explicit user approval.

## Execute and retain evidence

1. Exercise the changed path and the smallest relevant interaction state: loading, empty, error, cancellation, duplicate submission, or permission denial when relevant.
2. For a suspected shared-component regression, test only the changed page plus a representative consumer necessary to prove the causal chain.
3. Capture a screenshot for visible failures. Capture console errors, relevant request/response metadata, and trace/HAR when the selected MCP exposes them and retention is permitted.
4. Record exact steps and the result: reproduced, not-reproduced, or blocked. A blocked run is not a defect confirmation.
5. For Chrome, name the session before opening or claiming tabs, claim only a tab returned by `openTabs()`, reuse the same binding, and call `tabs.finalize(...)` as the final Chrome action.
6. Record initial connection, repeated DOM/screenshot operations, and recovery after interruption separately. Do not call the connection stable when only the initial path passed.

Use [ui-evidence.md](references/ui-evidence.md). Do not claim design or UI-spec noncompliance from source inspection alone when the page can be run.
