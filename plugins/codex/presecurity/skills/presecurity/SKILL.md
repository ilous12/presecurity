---
name: presecurity
description: Use when the user asks to run presecurity, scan a codebase for security, produce presecurity artifacts, or apply presecurity tiered autofixes.
---

# presecurity

presecurity is a Markdown-first security review plugin. Execute this workflow
directly by reading files, writing artifacts, and applying tiered fixes with
safe-only behavior by default.

## Operating Contract

`/presecurity` with no arguments is help-only. Show the available command list
and stop. Do not scan unless the user invokes `/presecurity scan` or explicitly
asks to scan through `$presecurity`.

Scan workflow:

```text
read -> analyze -> report
```

Do not stop after analysis. A scan is complete only after `report.md`,
`findings.json`, `coverage.json`, and the rest of the artifact bundle are
written.

Autofix workflow:

```text
read latest artifacts -> classify fixes -> apply safe-only fixes -> rescan -> update report
```

Git is optional. If Git is unavailable, treat the target as a local directory
snapshot. Do not require commit hashes, branches, pull requests, or history.

## Display Language

Before showing command menus, progress, summaries, doctor output, cleanup
output, or autofix results, detect the host/user language setting and respond in
that language:

- English setting: display user-facing text in English.
- Korean setting: display user-facing text in Korean.

If the host language setting is unavailable, infer the language from the user's
current request. Keep artifact schemas, JSON keys, file names, command names,
finding IDs, and code identifiers unchanged.

## Screen Output Contract

During scan execution, show only short progress updates on screen. Do not
stream detailed analysis, raw findings, file-by-file notes, chain-of-thought,
patch suggestions, or file write logs while the scan is running.

Suppress operational logs such as `Wrote ...`, `Created ...`, `Updated ...`,
artifact file paths, and per-file completion messages. Write artifacts silently.

Use only concise progress lines like these:

```text
presecurity: reading files...
presecurity: analyzing trust boundaries...
presecurity: writing report...
```

For Korean display settings, localize the status text while keeping the
`presecurity:` prefix:

```text
presecurity: 파일 읽는 중...
presecurity: 신뢰 경계 분석 중...
presecurity: 리포트 작성 중...
```

When the scan completes, show only a compact result summary:

- artifact directory
- total findings by severity
- top findings by title and severity
- safe autofix candidates count
- review-required count
- blocked count
- proof gaps and limitations

Keep detailed evidence, attack paths, and remediation notes in `report.md` and
the JSON artifacts instead of printing them to the chat.

## Invocation Forms

Use this skill for:

- `Use $presecurity to review this repository.`
- `Use $presecurity to scan this folder.`
- `Use $presecurity to apply tiered autofixes.`
- `/presecurity` to show commands only
- `/presecurity scan`
- `/presecurity autofix`
- `/presecurity autofix safe`
- `/presecurity autofix review-required`
- `/presecurity autofix blocked`
- `/presecurity doctor`
- `/presecurity cleanup`

## Target Resolution

1. Use the current workspace as the target unless the user provides a path.
2. Exclude dependency/build/cache folders:
   - `.git`
   - `.presecurity`
   - `node_modules`
   - `.venv`
   - `venv`
   - `dist`
   - `build`
   - `coverage`
   - `.gradle`
   - `DerivedData`
   - `Pods`
   - `.dart_tool`
3. Include source-like and config-like files across general codebases:
   - JavaScript, TypeScript, JSX, TSX
   - Python
   - Java, Kotlin
   - Swift, Objective-C
   - Dart
   - Go
   - Ruby
   - PHP
   - C, C++
   - JSON, YAML, XML, plist
   - Dockerfile
   - Terraform
   - Gradle, Maven
   - GitHub Actions and CI configuration

## Artifact Directory

Create artifacts under:

```text
.presecurity/scans/scan-YYYYMMDD-HHMMSS/
```

Required files:

- `scan-manifest.json`
- `repository-map.json`
- `threat-model.json`
- `findings.json`
- `coverage.json`
- `report.md`

Autofix additionally writes:

- `fix-plan.json`
- `autofix-result.json`

## Read Phase

Build `scan-manifest.json` and `repository-map.json`.

`scan-manifest.json` must include:

- `schemaVersion`
- `scanId`
- `tool`
- `mode`
- `target.type`
- `target.rootPath`
- `sourceSnapshot.createdAt`
- `sourceSnapshot.fileCount`
- `sourceSnapshot.hashAlgorithm`
- `languages`
- `artifactPaths`
- `limitations`

`repository-map.json` must include:

- files reviewed
- languages and frameworks
- entrypoint candidates
- untrusted input candidates
- trust boundary hints
- sensitive sink candidates
- dependency files
- configuration files
- skipped files with reasons

## Analyze Phase

Build `threat-model.json` and `findings.json`.

Analyze code intent first:

- who controls the input
- where the input flows
- what trust or auth boundary is crossed
- which sensitive sink or privileged operation is reached
- what realistic impact follows
- what evidence supports the claim
- what counterevidence weakens the claim
- what proof gap remains

Threat model fields:

- `assets`
- `entrypoints`
- `untrustedInputs`
- `trustBoundaries`
- `authAssumptions`
- `sensitiveDataPaths`
- `priorityReviewAreas`

Finding fields:

- `id`
- `title`
- `category`
- `severity`
- `confidence`
- `reachability`
- `exploitability`
- `businessImpact`
- `files`
- `attackPath`
- `evidence`
- `counterEvidence`
- `proofGap`
- `recommendation`
- `autofix`

## Threat Categories

Assign one primary category:

| ID | Category |
| --- | --- |
| T01 | Injection |
| T02 | Broken Authentication |
| T03 | Broken Authorization |
| T04 | SSRF / Unsafe Network |
| T05 | Secret Exposure |
| T06 | Insecure Storage |
| T07 | Crypto Misuse |
| T08 | Deserialization |
| T09 | Path / File Access |
| T10 | XSS / HTML Injection |
| T11 | WebView / Client Bridge |
| T12 | Deep Link / Intent |
| T13 | Insecure Config |
| T14 | Supply Chain |
| T15 | CI/CD / Build Script |
| T16 | Business Logic |
| T17 | Multi-Tenant Isolation |
| T18 | Logging / Error Leak |
| T19 | Race / TOCTOU |
| T20 | Resource Abuse |
| T21 | Native / Memory Safety |
| T22 | AI Agent / Tool Risk |

## Severity Model

- `critical`: RCE, full auth bypass, broad secret/data exfiltration, payment or
  tenant takeover.
- `high`: exploitable injection, SSRF, privilege escalation, account takeover,
  sensitive token exposure.
- `medium`: conditional exploitability, scoped data exposure, insecure config,
  weak storage, partial authorization gap.
- `low`: hardening issue or difficult exploit path.
- `info`: review signal without a confirmed vulnerability.

Always separate:

- `severity`
- `confidence`
- `reachability`
- `exploitability`
- `businessImpact`

## Report Phase

Build `coverage.json` and `report.md`.

`coverage.json` must include:

- `reviewedFiles`
- `skippedFiles`
- `deferredSurfaces`
- `limitations`
- `proofGaps`

`report.md` must include:

1. Summary
2. Target and snapshot
3. Coverage and limitations
4. Threat model summary
5. Findings by severity
6. Finding details
7. Safe autofix candidates
8. Review-required remediations
9. Blocked or deferred areas

This report step is mandatory for every scan.

## Autofix Policy

Classify each finding:

- `safe`: narrow deterministic change with low behavior risk.
- `review-required`: security policy or business intent decision needed.
- `blocked`: intent unclear or fix is too broad.

Autofix modes:

- `/presecurity autofix`: same as `/presecurity autofix safe`.
- `/presecurity autofix safe`: process only `safe` fixes.
- `/presecurity autofix review-required`: process `safe` fixes first, then
  `review-required` fixes.
- `/presecurity autofix blocked`: process `safe` fixes first, then
  `review-required` fixes, then `blocked` fixes.

Processing rules:

1. Process one risk tier at a time in this order: `safe`,
   `review-required`, `blocked`.
2. Within each tier, apply one fix at a time.
3. Apply root-cause fixes only. Do not apply partial mitigations, temporary
   hardening, or "best effort" patches that leave the original attack class
   materially reachable.
4. After each fix, run the smallest meaningful impact check: inspect the diff,
   rescan changed files when possible, and update the finding status.
5. Continue iterating within the current tier until no eligible finding remains
   or an impact check fails.
6. Move to the next tier only when the current tier is clean.
7. Stop immediately on behavior ambiguity, failed impact checks, broad
   unrelated diffs, or destructive/irreversible changes.

Default behavior is safe-only. Never apply `review-required` or `blocked`
findings unless the user explicitly invoked the matching autofix mode.

Root-cause requirements:

- A finding is fixed only when the vulnerable data flow or missing policy is
  removed at its source or enforced at the correct trust boundary.
- Do not report `partially mitigated` as an applied fix. If only partial
  mitigation is possible, leave the finding unresolved and report the required
  policy input.
- Do not replace allowlist requirements with blocklists. Blocklists for private
  IPs, metadata hosts, loopback, link-local ranges, non-standard IP notation,
  or IPv6 variants are defense-in-depth only and do not close SSRF by
  themselves.
- For SSRF, the preferred review-required fix is a positive allowlist of
  approved destinations, protocols, and ports, or a centrally enforced outbound
  gateway policy. If allowed destinations are unknown, do not edit application
  code; update the report with the missing policy decision.
- For authorization, tenant isolation, payment, workflow, and state-transition
  issues, patch the source-of-truth policy check. Do not add local route-only
  guards when shared services or downstream entrypoints can still bypass them.

Safe examples:

- `yaml.load(...)` to `yaml.safe_load(...)` when call shape is simple.
- `debug=True` to `debug=False` in production-like app entry points.
- `verify=False` to `verify=True` when no local/test guard exists.
- unsafe plain DOM assignment to text assignment when no HTML intent exists.
- clearly accidental hardcoded credential-like value to empty placeholder plus
  report recommendation.

Review-required examples:

- authz model changes
- payment or tenant logic changes
- approved URL allowlist or outbound gateway policy design
- Android cleartext or iOS ATS policy tightening
- crypto migration that affects stored data compatibility

## Autofix Workflow

1. Read latest `.presecurity/scans/*/findings.json`.
2. Write `fix-plan.json`.
3. Apply the selected autofix tier sequence using the smallest edit possible.
4. Write `autofix-result.json` with exact changed files and skipped items.
5. Rescan changed files or the full target.
6. Update `report.md` with fixed, remaining, and deferred findings.

## Doctor

For doctor requests, verify:

- required plugin Markdown files exist
- target root is readable
- artifact directory can be created
- no bundled runtime runner is required
- Git status is available only if Git exists

## Cleanup

For cleanup requests, remove only `.presecurity/` from the target root.

## Final Response

Report:

- artifact directory
- total findings by severity
- applied fixes by tier
- review-required findings
- blocked findings
- proof gaps and limitations
