---
description: presecurity 초기화, 스캔, 자동수정, 정리, 진단을 실행합니다
argument-hint: "init|scan|autofix|cleanup|doctor"
---

# /presecurity

Run the requested presecurity action for the current project.

Supported forms:

- `/presecurity init`
- `/presecurity scan`
- `/presecurity autofix`
- `/presecurity cleanup`
- `/presecurity doctor`

When invoked:

1. Identify the current project root.
2. Run `bash "${CLAUDE_PLUGIN_ROOT}/bin/run-presecurity.sh" --root "$PWD" <action>` from that root.
3. For `scan`, read `.presecurity/scan-plan.json` and summarize the impact,
   highest-risk findings, diff intent summary, and proposed fix order. Do not
   display false-positive candidates.
4. For `autofix`, run the bundled autofix command, rescan, then automatically
   edit any remaining findings from `.presecurity/scan-plan.json` without asking
   the user which item to fix first.
5. For `cleanup`, remove `.presecurity/` state files.
6. For `doctor`, report environment and project-state checks.

If `${CLAUDE_PLUGIN_ROOT}` is unavailable, locate the installed presecurity plugin
directory and run its bundled `bin/run-presecurity.sh`.
