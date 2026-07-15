# Static Verification

Inspect `ui/package.json` and the changed module before choosing checks. Prefer targeted existing tests; otherwise use only applicable, non-mutating analysis commands. Never run `npm run build`, `vite build`, or equivalent build commands. The current `npm run lint` script includes automatic fixers, so do not invoke it during review; use its underlying tools without `--fix` and only for changed files.

Record command, working directory, exit status, relevant output, and attribution. Missing typecheck or test infrastructure is **not verified**, not a pass. Passing static checks do not prove UI behavior.

```yaml
check: <non-mutating targeted lint or test command>
workdir: ui
purpose: <hypothesis or baseline verification>
result: pass | fail | blocked | not-applicable
exit_code: <number or n/a>
evidence: <salient output or artifact location>
attribution: diff-related | environment/tooling | unknown
```
