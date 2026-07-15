---
name: collab-review-hypothesis
description: Turn observations from an auto-ops frontend code diff into small, falsifiable regression hypotheses and focused verification plans. Use after inspecting a diff when suspected correctness, UI, permission, state, performance, or cross-page effects must be tied to the change before being reported as risks.
---

# Review Hypotheses

Convert code observations into tests of change-induced behavior. A hypothesis is not a defect report.

## Admission test

Create a risk hypothesis only if all three are present:

1. A precise changed location in the diff.
2. A causal chain from that modification to a user, data, security, or performance outcome.
3. A practical verification action and an observable expected result.

If the chain is missing, classify the item as a non-blocking suggestion. If existing code becomes faulty only under the changed behavior, call it **existing defect exposed by this diff** and preserve both facts.

## Write each hypothesis

Follow [risk-hypothesis.md](references/risk-hypothesis.md). Keep the verification path minimal: changed page first, then only representative dependent pages needed to establish impact.

Prioritize functional, data, permission, and severe performance consequences above architecture or style. Do not convert a preference for a refactor into a P0–P2 finding.
