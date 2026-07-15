# Context Map

Read context in layers; never load the whole repository by default.

1. **Change:** diff, changed files, linked requirement, declared behavior.
2. **Direct dependency:** changed component or utility, route entry, API, local/Vuex state, permission, and closest comparable implementation.
3. **Causal expansion:** representative consumer only when a changed shared component, request utility, route, state, or permission path could regress it.
4. **Ambiguity:** history or broader conventions only when the contract remains unclear.

For auto-ops frontend, begin under `ui/`. It uses Vue 2, Vue Router, Vuex, and `@canway/cw-magic-vue`.

```yaml
review_target: <branch/commit/diff>
requirement: <ticket, text, or unknown>
changed_behavior: <facts only>
read:
  - path: <path>
    reason: <direct dependency or causal question>
direct_dependencies:
  route: []
  components: []
  api: []
  state: []
  permissions: []
excluded: []
unknowns: []
```
