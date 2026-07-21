# Browser and UI Evidence

Use runtime evidence to falsify a concrete, diff-linked hypothesis. The default browser path is the bundled CDP Bridge because it reuses the user's authenticated Chrome state and addresses tabs explicitly.

## Fast path

1. Confirm route, role, test data, viewport, and the exact expected state.
2. Run `scripts/doctor.py` only when the bridge is unavailable or setup is uncertain.
3. Create a named Chrome tab group for the review and create one inactive tab per independent route or state chain.
4. Bind every command to an explicit `tab_id`. Different tabs may run in parallel; interactions within one tab remain serial.
5. Wait for the exact business control to be visible and interactable. Do not use broad loading selectors or high-frequency polling.
6. Exercise the smallest relevant interaction. Avoid final submit, delete, publish, reservation, or other data-changing actions unless explicitly authorized and isolated.
7. Capture the post-action DOM state and, when relevant, screenshot, console, and network evidence.
8. Close disposable tabs or rename the group to indicate completion when the user wants to inspect the scene.

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
```
