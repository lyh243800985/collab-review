# UI Evidence Record

```yaml
hypothesis: R-01
environment: <local/test URL>
tool: <browser MCP name>
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
```
