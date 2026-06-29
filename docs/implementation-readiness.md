# Implementation readiness

This document fixes the implementation shape before feature work continues.

## Non-Goals

- Do not build a SaaS dashboard.
- Do not require Git.
- Do not require a bundled language runtime.
- Do not require shell runners.
- Do not apply policy-dependent or broad patches unless the user explicitly
  invokes the matching autofix tier and impact checks pass.
- Do not claim runtime exploit reproduction unless it was actually performed.

## Required Shape

presecurity is a Markdown-first plugin. The core implementation lives in:

- `plugins/claude/presecurity/commands/presecurity.md`
- `plugins/codex/presecurity/commands/presecurity.md`
- `plugins/codex/presecurity/skills/presecurity/SKILL.md`
- `README.md`
- `docs/development-plan.md`
- `docs/supported-platforms.md`

The host agent reads those Markdown instructions and performs the workflow.

## Display Language

User-facing plugin output must follow the current host/user language setting.
English settings show English command menus, progress, summaries, doctor
output, cleanup output, and autofix results. Korean settings show the same
surfaces in Korean.

If the host language setting is unavailable, infer the language from the user's
current request. Artifact schemas, JSON keys, file names, command names,
finding IDs, and code identifiers remain stable.

## Workflow Contract

`/presecurity` without arguments is command-list only and must not scan.

```text
read -> analyze -> report -> autofix -> rescan
```

Read:

- identify target root
- build file inventory
- detect languages and frameworks
- collect entrypoints, trust boundaries, dependency files, config files, and
  sensitive sinks
- create a scan snapshot without requiring Git

Analyze:

- build a lightweight threat model
- identify realistic attack paths
- record evidence, counterevidence, and proof gaps
- classify severity, confidence, reachability, exploitability, and business
  impact

Report:

- write structured artifacts
- write a portable Markdown report
- include coverage and limitations before final claims

`scan` includes this report step automatically.

Screen output:

- while scanning, show only concise progress status
- do not print detailed findings, file-by-file notes, or patch suggestions
  before the report is complete
- do not print operational write logs such as `Wrote ...`, `Created ...`,
  artifact file paths, or per-file completion messages
- write artifacts silently
- after completion, print only a compact result summary
- after completion, recommend the highest needed autofix command from the
  latest safe/review-required/blocked counts
- keep detailed evidence, attack paths, proof gaps, and remediation guidance in
  `report.md` and JSON artifacts

Autofix:

- create a fix plan
- default to `safe` deterministic changes only
- `/presecurity autofix safe` processes only `safe`
- `/presecurity autofix review-required` processes `safe`, then
  `review-required`
- `/presecurity autofix blocked` processes `safe`, then `review-required`,
  then `blocked`
- scan summaries recommend `/presecurity autofix blocked` if any blocked
  items exist, else `/presecurity autofix review-required` if any
  review-required items exist, else `/presecurity autofix safe` if only safe
  items exist
- apply fixes sequentially and run an impact check after every individual fix
- stop on failed impact checks, destructive changes, broad unrelated diffs, or
  unresolved ambiguity
- apply root-cause fixes only; do not apply partial mitigations or report
  `partially mitigated` as a completed fix
- for SSRF, prefer a positive allowlist or centrally enforced outbound policy;
  blocklists for private IPs, metadata hosts, loopback, link-local ranges, or
  non-standard IP forms are defense-in-depth only
- if the required policy is unknown, leave the finding unresolved and report
  the missing policy decision instead of editing code

Rescan:

- inspect changed files
- update artifacts
- report fixed, remaining, and deferred items

## Artifact Directory

```text
.presecurity/scans/scan-YYYYMMDD-HHMMSS/
```

The scan directory is append-only for a completed scan. Autofix writes a new
result file and may write a new report in the same scan directory when the fix
belongs to that scan.

## Minimum Viable Completion

A working plugin run is complete when:

1. `.presecurity/scans/<scan-id>/scan-manifest.json` exists.
2. `.presecurity/scans/<scan-id>/scan-summary.json` exists.
3. `.presecurity/scans/<scan-id>/repository-map.json` exists.
4. `.presecurity/scans/<scan-id>/threat-model.json` exists.
5. `.presecurity/scans/<scan-id>/findings.json` exists.
6. `.presecurity/scans/<scan-id>/coverage.json` exists.
7. `.presecurity/scans/<scan-id>/report.md` exists.
8. Material findings have matching `validation/<finding-id>.json`.
9. Accepted or fixable findings have matching `patches/<finding-id>.patch.md`.
10. `/presecurity autofix` can create `fix-plan.json` and
   `autofix-result.json` without applying unsafe changes.

Findings are complete only when they include measured threat score,
likelihood, impact, reachability, exploitability, confidence, evidence,
counterevidence, validation status, and proof gap. Low/info/speculative
signals should be deferred rather than promoted into findings unless they
materially change real-world risk.

## Completion Evidence

Every final agent response after running presecurity should include:

- artifact directory path
- total material findings by severity
- measured risk distribution
- top remediation priorities
- recommended autofix command
- applied fixes by tier
- review-required items
- blocked items
- proof gaps and limitations
