# Risk Hypothesis

Create a risk only when it has a changed location, a causal chain, and a practical verification action. Otherwise, write a non-blocking suggestion.

```yaml
id: R-01
changed_location: ui/src/...:line
attribution: new-by-diff | existing-defect-exposed-by-diff
causal_chain: <change → condition → observable impact>
trigger: <minimal data, account, and user action>
expected: <correct behavior>
suspected_actual: <failure to prove or disprove>
verification: <command or browser steps>
minimum_impact_scope: <changed page and required representative consumer>
knowledge_relation: current | superseded | proposal | legacy | none
knowledge_sources: []
if_unverified: <blocker and next action>
```
