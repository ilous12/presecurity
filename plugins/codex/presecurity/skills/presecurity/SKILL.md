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
   `bash <installed-plugin-root>/bin/run-presecurity.sh --root "$PWD" <command>`.
3. If the repository package is installed in the environment, `python3 -m presecurity --root "$PWD" <command>` is also valid.
4. Run `init` for initialization.
5. Run `scan` to create or refresh
   `.presecurity/scan-plan.json`.
6. Run `autofix` to apply safe deterministic fixes from
   the current plan.
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

For autofix, report:

- fixes applied
- skipped items and why
- remaining findings after rescan

For doctor, report:

- environment status
- whether `.presecurity/` has been initialized
- missing files or tools
