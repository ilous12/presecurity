# Implementation readiness

This document fixes the implementation shape before feature work continues.

## Non-Goals

- Do not build a SaaS dashboard.
- Do not require Git.
- Do not require a bundled language runtime.
- Do not require shell runners.
- Do not auto-apply policy-dependent or broad patches.
- Do not claim runtime exploit reproduction unless it was actually performed.

## Required Shape

presecurity is a Markdown-first plugin. The core implementation lives in:

- `plugins/claude/presecurity/commands/presecurity.md`
- `plugins/codex/presecurity/skills/presecurity/SKILL.md`
- `README.md`
- `docs/development-plan.md`
- `docs/supported-platforms.md`

The host agent reads those Markdown instructions and performs the workflow.

## Workflow Contract

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
- after completion, print only a compact result summary
- keep detailed evidence, attack paths, proof gaps, and remediation guidance in
  `report.md` and JSON artifacts

Autofix:

- create a fix plan
- apply only `safe` deterministic changes
- leave `review-required` and `blocked` items untouched

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
2. `.presecurity/scans/<scan-id>/repository-map.json` exists.
3. `.presecurity/scans/<scan-id>/threat-model.json` exists.
4. `.presecurity/scans/<scan-id>/findings.json` exists.
5. `.presecurity/scans/<scan-id>/coverage.json` exists.
6. `.presecurity/scans/<scan-id>/report.md` exists.
7. `/presecurity autofix` can create `fix-plan.json` and
   `autofix-result.json` without applying unsafe changes.

## Completion Evidence

Every final agent response after running presecurity should include:

- artifact directory path
- total findings by severity
- safe fixes applied
- review-required items
- blocked items
- proof gaps and limitations
