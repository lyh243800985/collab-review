# Verified Diff Review Report

先按 `assets/example-review.json` 的结构保存机器可读 findings，再执行：

```powershell
py -3 <plugin-root>/scripts/validate_review.py <report.json>
```

只有校验通过后，才能将 `verified_defect` 呈现在人类可读报告中。UI、UX、Figma 或浏览器问题必须包含运行态或视觉证据；未完成验证的内容放入 `unverified_risk`。

```markdown
# Review: <change>

## Scope, coverage, and evidence
- Diff/base: ...
- Requirement evidence: ...
- Project knowledge: provider · project/revision · current/superseded rules · compatibility · sources · unresolved
- Browser reachability plans: hypothesis · target state · code-derived conditions · fixture · readiness · stop conditions
- Layers inspected: requirement | UI/Figma | route/state/permission | shared component/API contract | backend/interface contract | static checks | runtime interaction
- Checks and UI paths executed: ...
- Not run, excluded, or blocked: ...

## Verified defects
Priority · changed location · causal chain · trigger · impact · evidence · suggested fix

## Unverified diff-linked risks
- Hypothesis · blocker · next verification action

## Verified passes
- Hypothesis/check: ... Evidence: ...

## Non-blocking suggestions and open questions
- State whether unrelated to this diff or requires a human decision.

## Optimization suggestions (separate approval)
- Category: robustness | extensibility | readability | maintainability | testability
- Observation · benefit · smallest proposed scope

## Decision requested
- Recommended approved-fix scope: ...
- Deferred items: ...
- Do not edit until the user explicitly confirms the approved scope.
```
