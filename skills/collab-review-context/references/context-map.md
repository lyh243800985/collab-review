# Context Map

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
  conventions: []
excluded:
  - <area not needed for this diff>
unknowns:
  - <business rule or environment fact not evidenced>
```
