---
name: collab-ui-verify
description: Verify an auto-ops frontend diff hypothesis through real browser interaction and retain reproducible evidence. Use for changed Vue/cwui UI, routes, forms, tables, dialogs, permissions, request flows, shared UI utilities, or supplied Figma links when a code-only review cannot establish whether a regression occurs. Prefer browser and Figma MCP tools; do not use the Codex Chrome plugin.
---

# UI Evidence Verification

Prove or disprove one diff-linked hypothesis through the running application. Use the available purpose-built browser MCP first for navigation, interaction, screenshots, console, and network evidence. Use Playwright only when it is explicitly available through MCP or the project already provides it. Do not use the Codex Chrome plugin.

## Before interacting

1. Confirm the route, account/permission, test data, and environment needed for the hypothesis.
2. State the minimal steps, expected behavior, and observations to capture.
3. If a Figma URL or node is supplied, read it with the Figma MCP before comparing design or interaction details.
4. If the needed MCP is unavailable or cannot access the authenticated session, record the blocker and request an approved alternative. Do not fall back to the Codex Chrome plugin. Do not create, delete, or alter production data without explicit authorization.

## Execute and retain evidence

1. Exercise the changed path and the smallest relevant interaction state: loading, empty, error, cancellation, duplicate submission, or permission denial when relevant.
2. For a suspected shared-component regression, test only the changed page plus a representative consumer necessary to prove the causal chain.
3. Capture a screenshot for visible failures. Capture console errors, relevant request/response metadata, and trace/HAR when the selected MCP exposes them and retention is permitted.
4. Record exact steps and the result: reproduced, not-reproduced, or blocked. A blocked run is not a defect confirmation.

Use [ui-evidence.md](references/ui-evidence.md). Do not claim design or UI-spec noncompliance from source inspection alone when the page can be run.
