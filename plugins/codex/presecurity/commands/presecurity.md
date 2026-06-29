---
description: Scan a codebase, automatically generate a report, and apply tiered autofixes.
argument-hint: "scan|autofix [safe|review-required|blocked]|doctor|cleanup"
---

# /presecurity

presecurity is a Markdown-first security review command. Execute the workflow
directly as the coding agent: read files, reason about security intent, write
artifacts, and apply tiered fixes with safe-only behavior by default.

## Arguments

- no argument: show the available presecurity commands only. Do not scan.
- `scan`: read, analyze, and generate a complete report bundle.
- `autofix` or `autofix safe`: apply safe-only fixes from the latest scan.
- `autofix review-required`: apply safe fixes, then review-required fixes.
- `autofix blocked`: apply safe fixes, review-required fixes, then blocked
  fixes.
- `doctor`: verify plugin surfaces, required docs, fixture corpus, and artifact
  write access.
- `cleanup`: remove generated `.presecurity/` artifacts from the target root.

## Default Behavior

## Display Language

Before showing command menus, progress, summaries, doctor output, cleanup
output, or autofix results, detect the host/user language setting and respond in
that language:

- English setting: display user-facing text in English.
- Korean setting: display user-facing text in Korean.

If the host language setting is unavailable, infer the language from the user's
current request. Keep artifact schemas, JSON keys, file names, command names,
finding IDs, and code identifiers unchanged.

When the user invokes `/presecurity` with no arguments, show only this command
menu and stop:

```text
/presecurity scan      Read, analyze, and write report artifacts.
/presecurity autofix   Apply safe-only fixes.
/presecurity autofix safe
/presecurity autofix review-required
/presecurity autofix blocked
/presecurity doctor    Verify plugin surfaces and artifact write access.
/presecurity cleanup   Remove generated .presecurity artifacts.
```

Do not start a scan from `/presecurity` alone.

When the user invokes `/presecurity scan`, run:

```text
read -> analyze -> report
```

Do not stop after analysis. `/presecurity scan` is complete only after
`report.md` and the structured JSON artifacts are written.

## Screen Output

During `/presecurity scan`, show only short progress updates on screen. Do not
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

When the user invokes `/presecurity autofix` or `/presecurity autofix safe`,
run:

```text
read latest artifacts -> classify fixes -> apply safe-only fixes -> rescan -> update report
```

## Scope

Use the current project root unless the user provides a path.

Git is optional. If Git is unavailable, use a local folder snapshot identified
by scan id, timestamp, root path, and file hashes.

Exclude dependency, cache, generated, and artifact folders:

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

Support general codebases:

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

## Required Artifacts

Create:

```text
.presecurity/scans/scan-YYYYMMDD-HHMMSS/
  scan-manifest.json
  repository-map.json
  threat-model.json
  findings.json
  coverage.json
  report.md
```

Autofix also creates:

```text
fix-plan.json
autofix-result.json
```

## Read

Create `scan-manifest.json` with:

- schema version
- scan id
- target root
- snapshot timestamp
- file count
- hash algorithm
- detected languages
- artifact paths
- limitations

Create `repository-map.json` with:

- reviewed files
- skipped files and reasons
- detected frameworks
- entrypoint candidates
- untrusted input candidates
- trust boundary hints
- sensitive sinks
- dependency files
- configuration files

## Analyze

Create `threat-model.json` with:

- assets
- entrypoints
- untrusted inputs
- trust boundaries
- auth assumptions
- sensitive data paths
- priority review areas

Create `findings.json`. Each finding must include:

- id
- title
- category
- severity
- confidence
- reachability
- exploitability
- business impact
- file locations
- attack path
- evidence
- counterevidence
- proof gap
- recommendation
- autofix classification

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

## Report

Create `coverage.json` with:

- reviewed files
- skipped files
- deferred surfaces
- limitations
- proof gaps

Create `report.md` with:

1. Summary
2. Target and snapshot
3. Coverage and limitations
4. Threat model summary
5. Findings by severity
6. Finding details
7. Safe autofix candidates
8. Review-required remediations
9. Blocked or deferred areas

This report step is mandatory for `/presecurity scan`.

## Autofix

Classify every finding:

- `safe`: narrow deterministic fix with low behavior risk.
- `review-required`: security policy or business intent decision needed.
- `blocked`: unclear intent or broad change.

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

- `yaml.load(...)` to `yaml.safe_load(...)`
- `debug=True` to `debug=False`
- `verify=False` to `verify=True`
- unsafe plain DOM assignment to text assignment when HTML rendering is not
  intended
- clearly accidental hardcoded credential-like value to an empty placeholder
  plus report guidance

Review-required examples:

- authorization model changes
- payment or tenant isolation changes
- approved URL allowlist or outbound gateway policy design
- Android cleartext or iOS ATS policy changes
- crypto migrations that affect stored data compatibility

## Doctor

For `/presecurity doctor`, verify:

- this command file exists
- the `$presecurity` skill exists
- plugin manifests are valid JSON
- docs exist
- example fixtures exist
- the target root can write `.presecurity/`

Report failures with exact file paths and suggested fixes.
