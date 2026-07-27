---
name: collab-review-report
description: Produce an evidence-based review report for an auto-ops frontend code diff. Use after static or browser verification to separate verified regressions from unverified risks, unrelated suggestions, and human decisions without expanding the scope of the submitted change.
---

# Verified Review Report

Write a report whose organization reflects evidence, not the order of files in the diff.

Read [report-template.md](references/report-template.md) and use its four result classes exactly.

## Findings

For every risk item, include priority, changed location, causal chain, trigger condition, scope, evidence, and a proportionate suggested fix. A cross-file finding requires proof that this diff caused or exposed the behavior.

Do not assign P0–P2 to an unverified hypothesis or an unrelated pre-existing problem. A recommendation may point out an unrelated issue, but must say it is non-blocking and outside the current diff scope.

## Completion standard

State which project knowledge was recalled, which checks and pages were actually run, what was not
run, and why. When Know All Agent was unavailable, mark historical compatibility unverified instead
of treating code as the rule. Close with open questions that need human product or architecture
decisions.
