# UI Evidence

Verify one diff-linked hypothesis through the running application with the available browser MCP. Use a Figma MCP for supplied Figma URLs or nodes. Do not use the Codex Chrome plugin.

Confirm route, role, test data, and environment first. If the required MCP cannot access the page or authenticated session, record that blocker and request an approved alternative; do not silently switch browser mechanisms. Do not mutate production data without explicit authorization. Exercise the smallest relevant interaction state, capture screenshots for visible failures, and retain console/network/trace evidence when exposed by the MCP. A blocked run never confirms a defect.

```yaml
hypothesis: R-01
environment: <local/test URL>
tool: <browser MCP name>
figma_reference: <MCP frame/node reference or not-applicable>
account_or_role: <authorized test role>
preconditions: <test data and state>
steps: [<action>]
expected: <behavior>
actual: <behavior>
result: reproduced | not-reproduced | blocked
evidence:
  screenshot: <path or none>
  trace_or_har: <path or none>
  console: <message or none>
  network: <request/result metadata or none>
scope: <why these pages establish diff impact>
```
