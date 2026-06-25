---
name: presecurity
description: Use when the user invokes /presecurity init, /presecurity scan, /presecurity autofix, /presecurity cleanup, or /presecurity doctor.
---

# presecurity

Use this skill when the user asks for:

- `/presecurity init`
- `/presecurity scan`
- `/presecurity autofix`
- `/presecurity cleanup`
- `/presecurity doctor`

## Workflow

1. Treat the current workspace as the project root unless the user provides a
   different path.
2. Prefer the bundled plugin runner when available:
   `<installed-plugin-root>/bin/run-presecurity.sh --root . <command>`.
   Run it directly from the project root. Do not prefix it with `bash` and do
   not use `$PWD`.
3. If the repository package is installed in the environment, `python3 -m presecurity --root . <command>` is also valid.
4. Run `init` for initialization.
5. Run `scan` to create or refresh
   `.presecurity/scan-plan.json`.
6. Run `autofix` to rescan, discard stale or false-positive plan items, and
   apply every remaining planned fix.
   Do not stop because an item has no narrow deterministic fixer label; continue
   with automatic source edits.
7. Run `cleanup` when plugin state should be removed.
8. Run `doctor` when the user wants to check install/runtime/project state.

## Reporting

For scan results, summarize:

- critical/high findings first
- OWASP category
- impacted file and line
- diff intent summary and security-relevant changed areas
- whether autofix is available
- planned order of remediation

Do not show false-positive candidates and do not create a separate
false-positive section. If a finding is filtered by the scanner, omit it
entirely from the user-facing response. If you conclude a recorded finding is a
false positive, omit it from the response instead of asking the user to handle
it.

For autofix, report:

- fixes applied
- remaining findings after rescan

If findings remain after the bundled `autofix` command, inspect
`.presecurity/scan-plan.json`, edit the affected files yourself, and rerun
`scan`/`autofix` until the plan is exhausted or a non-recoverable tooling error
occurs. Do not ask which item to fix first.

For doctor, report:

- environment status
- whether `.presecurity/` has been initialized
- missing files or tools
