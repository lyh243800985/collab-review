---
name: collab-static-verify
description: Run and interpret scoped, non-mutating static verification for an auto-ops frontend diff, including available lint checks and targeted tests. Use when a review hypothesis needs repository evidence from non-browser checks or when a change review must distinguish code failures from unavailable tooling. Never use this skill to run a build.
---

# Static Verification

Run the smallest applicable existing checks, capture their actual result, and separate environment failures from change failures.

## Procedure

1. Inspect `ui/package.json` and the changed module for supported commands before choosing checks.
2. Prefer a targeted existing test if present. Otherwise run only a non-mutating lint or analysis command relevant to the modified code. Do not run `npm run build`, `vite build`, or any equivalent command.
3. Record command, working directory, exit status, relevant output, duration if material, and whether the failure can be attributed to the diff.
4. Do not run repository scripts that include `--fix` unless the user explicitly requests file changes. In this project, inspect `npm run lint` before use because it invokes fixers; prefer its underlying non-fixing tools with changed-file paths.
5. Do not call a missing typecheck, test suite, or unavailable dependency a pass. Mark it **not verified** with its reason.

Use [verification-record.md](references/verification-record.md). Static checks can confirm or refute a hypothesis, but passing checks do not prove UI behavior.
