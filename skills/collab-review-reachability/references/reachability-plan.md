# State Reachability Plan

Generate this record before browser verification:

```yaml
hypothesis: R-01
target:
  control_or_state: <button, dialog, row, tab, message, or request>
  changed_location: <diff path:line>
render_conditions:
  - predicate: <exact condition>
    source: <template, computed, store, permission, route, config, or API>
    evidence: <path:line or contract>
    required_value: <value or shape>
    status: satisfied | unresolved | unavailable
data_profile:
  required_fields: {}
  account_or_role: <role or not-applicable>
  runtime_config: {}
  fixture_source: supplied | repository | read-only-api | filtered-list | bounded-probe | none
  fixture_id: <stable identifier or none>
interaction_prerequisites:
  - <ordered state transition required before the target appears>
readiness: ready | probe | blocked | not_applicable
blocker: <reason or none>
browser_plan:
  url: <complete URL>
  target: <exact text, role, selector, or request>
  steps: []
  expected: <single observable result>
  evidence: [dom, screenshot, network, console, navigation, download]
  safe_boundary: <last action allowed without mutating data>
  wait_limit_seconds: 5
  route_budget_seconds: 120
  stop_conditions: []
```
## Example

```yaml
hypothesis: R-03
target:
  control_or_state: 同步 CMDB 按钮可见
  changed_location: ui/src/.../detail.vue:99
render_conditions:
  - predicate: window.SHOW_IP_SCAN_SYNC_CMDB_BUTTON === "true"
    source: runtime config
    evidence: ui/src/.../detail.vue:99
    required_value: "true"
    status: unresolved
  - predicate: report detail route has a valid id
    source: route and detail API
    evidence: ui/src/.../detail.vue
    required_value: existing finished report id
    status: satisfied
data_profile:
  required_fields: { status: FINISHED }
  account_or_role: report viewer
  runtime_config: { SHOW_IP_SCAN_SYNC_CMDB_BUTTON: "true" }
  fixture_source: supplied
  fixture_id: 10448
interaction_prerequisites: []
readiness: blocked
blocker: connected environment exposes only the false configuration state
browser_plan:
  url: http://test.example/#/report/detail/10448
  target: 同步 CMDB
  steps: []
  expected: button is visible when the runtime flag is true
  evidence: [dom, screenshot]
  safe_boundary: read-only inspection
  wait_limit_seconds: 5
  route_budget_seconds: 30
  stop_conditions:
    - runtime flag is not true
```
