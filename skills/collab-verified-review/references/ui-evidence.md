# Browser and UI Evidence

Use runtime evidence to falsify a concrete, diff-linked hypothesis. The default browser path is the bundled CDP Bridge because it reuses the user's authenticated Chrome state and addresses tabs explicitly.

## Fast path

1. Require a `collab-review-reachability` plan containing the full URL, target state, fixture identity, evidence, budget, and stop conditions. Normal interaction requires `readiness: ready`.
2. Run `scripts/doctor.py` only when the bridge is unavailable or setup is uncertain.
3. Create a named Chrome tab group for the review and create one inactive tab per independent route or state chain.
4. Bind every command to an explicit `tab_id`. Different tabs may run in parallel; interactions within one tab remain serial.
5. In the first probe, batch the exact business control, required data count, runtime flags, permission state, and visible interface errors. Default exact waits to 5 seconds.
6. If a planned stop condition is present, return `blocked` immediately. Do not explore other records or routes.
7. Exercise the smallest relevant interaction within the route budget, normally 120 seconds.
8. Capture the post-action DOM state and, when relevant, screenshot, console, and network evidence.
9. Compare the conclusion against DOM and screenshot facts before returning.
10. Close disposable tabs or rename the group to indicate completion when the user wants to inspect the scene.

## Evidence rules

- A screenshot proves visible state; it does not prove request success, authorization, or persistence.
- A click ACK proves command delivery, not business success. Verify the resulting DOM, request, download, navigation, toast, or data state.
- An ACK timeout is an unknown outcome. Inspect side effects before retrying so a real action is not executed twice.
- A blocked run never confirms a defect. Record the blocker and the next smallest verification action.
- Tool or connection failures are reported separately from product failures.
- Do not silently switch to another tab, role, route, browser surface, or test fixture.

Use Chrome DevTools MCP only when the hypothesis needs low-level protocol evidence unavailable through CDP Bridge. Use an isolated Playwright/browser session only as a last resort when authenticated Chrome state is unnecessary.

```yaml
hypothesis: R-01
reachability_plan: <plan id or path>
environment: <local/test URL>
tab_id: <explicit Chrome tab id>
figma_reference: <file/node reference or not-applicable>
account_or_role: <authorized test role>
preconditions: <test data and state>
steps: [<action>]
expected: <behavior>
actual: <behavior>
result: reproduced | not-reproduced | blocked
evidence:
  screenshot: <path or none>
  console: <message or none>
  network: <request/result metadata or none>
  dom: <selector/state/value or none>
scope: <why this route and state establish diff impact>
timing:
  readiness_probe_ms: <milliseconds>
  interaction_ms: <milliseconds>
  total_ms: <milliseconds>
stop_condition_triggered: <condition or none>
```
