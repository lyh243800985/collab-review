# UI Evidence Record

```yaml
hypothesis: R-01
environment: <local/test URL>
tool: <in-app Browser | Chrome plugin | other approved browser surface>
selection_reason: <why this surface is required>
figma_reference: <MCP frame/node reference or not-applicable>
account_or_role: <authorized test role>
preconditions: <test data and state>
steps:
  - <action>
expected: <behavior>
actual: <behavior>
result: reproduced | not-reproduced | blocked
evidence:
  screenshot: <path or none>
  trace_or_har: <path or none>
  console: <relevant message or none>
  network: <request/result metadata or none>
scope: <why these pages establish diff impact>
connection:
  initial: passed | failed | not-applicable
  repeated_operations: passed | failed | not-applicable
  interruption_recovery: passed | failed | not-tested
  finalized: true | false | not-applicable
```
