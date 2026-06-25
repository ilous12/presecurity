---
description: Initialize, scan, or autofix security issues with presecurity
argument-hint: "init|scan|autofix|cleanup"
---

# /presecurity

Run the requested presecurity action for the current project.

Supported forms:

- `/presecurity init`
- `/presecurity scan`
- `/presecurity scan --base <git-ref>`
- `/presecurity autofix`
- `/presecurity cleanup`

When invoked:

1. Identify the current project root.
2. Run `bash "${CLAUDE_PLUGIN_ROOT}/bin/run-presecurity.sh" --root "$PWD" <action>` from that root.
3. For `scan`, read `.presecurity/scan-plan.json` and summarize the impact,
   highest-risk findings, diff intent summary, and proposed fix order.
4. For `autofix`, apply safe fixes only, rescan, and report remaining manual
   review items.
5. For `cleanup`, remove `.presecurity/` state files.

If `${CLAUDE_PLUGIN_ROOT}` is unavailable, locate the installed presecurity plugin
directory and run its bundled `bin/run-presecurity.sh`.
