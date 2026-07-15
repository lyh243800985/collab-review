# UI Evidence

Verify one diff-linked hypothesis through the running application. Prefer the in-app Browser for an isolated session. Use the Chrome plugin when the hypothesis depends on existing Chrome tabs, login state, profile data, or extensions. Use a purpose-built Figma tool for supplied Figma URLs or nodes.

Confirm route, role, test data, and environment first. State which browser surface was selected and why. If the selected surface cannot access the page or authenticated session, record the blocker; do not silently switch browser mechanisms or edit plugin files. Do not mutate production data without explicit authorization. Exercise the smallest relevant interaction state, capture screenshots for visible failures, and retain console/network/trace evidence when exposed by the selected surface. A blocked run never confirms a defect.

For Chrome, follow the installed Chrome skill and its Node REPL API. Name the session before opening or claiming tabs, claim only an exact item returned by `openTabs()`, reuse the claimed tab, and call `tabs.finalize(...)` as the final Chrome action. If initialization reports a process-shim conflict, consult [the local compatibility record](../../../docs/chrome-plugin-process-shim-compatibility.md); any plugin-cache edit requires explicit approval. Record normal operation and recovery-after-interruption as separate results.

```yaml
hypothesis: R-01
environment: <local/test URL>
tool: <in-app Browser | Chrome plugin | other approved browser surface>
selection_reason: <why this surface is required>
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
connection:
  initial: passed | failed | not-applicable
  repeated_operations: passed | failed | not-applicable
  interruption_recovery: passed | failed | not-tested
  finalized: true | false | not-applicable
```
