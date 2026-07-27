# Know All Agent Integration

Use Know All Agent as the project-cognition layer. Collab remains the review orchestrator and owns
diff scope, hypotheses, static checks, browser execution, findings, and the final report.

## Start the knowledge gate

After collecting the requirement facts and the reviewed revision, but before broad code context:

1. Resolve `project_id` from the Know All Agent project registry.
2. When requirement or acceptance text exists, call:

```text
review_requirement(project_id, requirement_input, title, description)
```

Retain its `task_id`, `project_revision`, and `recalled_knowledge`.

3. For a diff-only review, call:

```text
recall_project_knowledge(project_id, query)
```

Build `query` from the changed paths, symbols, module, and changed behavior. Do not create a
requirement task when there is no requirement.

4. After minimal code context, make one additional targeted recall only when the diff exposes a
module or behavior absent from the first query.

Do not call Know All Agent's `verify-project-change` Skill. It is another orchestrator and would
duplicate Collab's static and browser verification.

## Consume returned knowledge

Classify every recalled item by its returned status:

- `current`: current project baseline;
- `superseded`: historical wording that must not override the current rule;
- `proposal`: unconfirmed knowledge;
- `legacy`: migration or investigation evidence.

Current code is implementation evidence, not automatic business truth. When a proposed requirement
or diff repeats a superseded rule, lead with the conflict against the current rule.

Bind the knowledge result to the reviewed revision. If `project_revision` differs from the reviewed
revision, refresh the call or mark historical compatibility unverified.

## Degrade safely

If the tools are unavailable, the project is unregistered, or recall fails:

- continue the diff review;
- record `projectKnowledge.status: unavailable` and the reason;
- set `historicalCompatibility: unverified`;
- do not claim the change is compatible with project history.

Do not search plugin installation folders or hard-code another developer's filesystem path.

## Persist material evidence

When `review_requirement` returned a task:

1. Call `add_investigation_evidence` only for evidence that changes the conclusion, such as a
   decisive code contract, Git fact, API observation, or browser result.
2. Validate the Collab machine report first.
3. Then call `complete_requirement_review` with:
   - `historical_conflicts`;
   - `superseded_rules`;
   - `affected_areas`;
   - `omitted_scenarios`;
   - `product_questions`;
   - `risks`;
   - `unresolved`.

Do not promote newly inferred facts into canonical knowledge. Route durable corrections through
Know All Agent's knowledge-maintenance workflow.

## Machine report

Always include:

```json
{
  "projectKnowledge": {
    "provider": "know-all-agent",
    "status": "used",
    "mode": "requirement_review",
    "projectId": "auto-ops",
    "projectRevision": "<revision returned by Know All Agent>",
    "reviewedRevision": "<review baseline revision>",
    "taskId": "<durable task id>",
    "historicalCompatibility": "verified",
    "currentRules": [],
    "supersededRules": [],
    "sources": [],
    "unresolved": []
  }
}
```

Allowed `status` values are `used`, `unavailable`, and `not_applicable`. Allowed compatibility
values are `verified`, `conflict`, `unverified`, and `not_applicable`.
