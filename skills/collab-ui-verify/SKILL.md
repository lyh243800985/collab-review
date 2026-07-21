---
name: collab-ui-verify
description: Verify an auto-ops frontend diff hypothesis through real browser interaction and retain reproducible evidence. Use for changed Vue/cwui UI, routes, forms, tables, dialogs, permissions, request flows, shared UI utilities, or supplied Figma links when a code-only review cannot establish whether a regression occurs.
---

# UI Evidence Verification

Prove or disprove one diff-linked hypothesis through the running application. Use the plugin's CDP Bridge to reuse the user's authenticated Chrome session and bind all work to an explicit `tab_id`.

## Before interacting

1. Confirm route, account/permission, test data, environment, and expected state.
2. If Figma is supplied, read the relevant node through the Figma MCP before comparing design behavior.
3. Create or reuse an isolated review tab group. Different tabs may run in parallel; dependent actions within one tab stay serial.
4. Avoid final submit or destructive actions unless explicitly authorized and backed by recoverable test data.
5. If CDP is unavailable, run the plugin doctor and report the run as blocked; do not silently switch tabs or browser profiles.

## Execute and retain evidence

1. Exercise only the smallest state chain needed for the hypothesis.
2. Capture visible state and relevant DOM, console, request, response, download, or navigation evidence.
3. Treat click acknowledgement, rendered UI, and business request result as separate facts.
4. If a command times out, inspect side effects before retrying; an unknown outcome is not a failed click.
5. Record reproduced, not-reproduced, or blocked. A blocked run cannot confirm a defect.

Use [ui-evidence.md](references/ui-evidence.md). Do not claim UI or design noncompliance from source inspection alone when the page can be executed.
