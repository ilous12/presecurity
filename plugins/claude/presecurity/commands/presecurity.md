---
description: Scan a codebase, automatically generate a report, and safe-autofix security issues
argument-hint: "scan|autofix|doctor|cleanup"
---

# /presecurity

presecurity is a Markdown-first security review command. Execute the workflow
directly as the coding agent: read files, reason about security intent, write
artifacts, and apply only safe deterministic edits.

## Default Behavior

When the user invokes `/presecurity` or `/presecurity scan`, run:

```text
read -> analyze -> report
```

Do not stop after analysis. `/presecurity scan` must generate `report.md` and
the full structured artifact bundle before it is complete.

## Screen Output

During `/presecurity` and `/presecurity scan`, show only short progress
updates on screen. Do not stream detailed analysis, raw findings, file-by-file
notes, chain-of-thought, or patch suggestions while the scan is running.

Use concise progress lines such as:

```text
presecurity: reading files...
presecurity: analyzing trust boundaries...
presecurity: writing report...
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

When the user invokes `/presecurity autofix`, run:

```text
read latest artifacts -> classify fixes -> apply safe-only fixes -> rescan -> update report
```

## Scope

Use the current project root unless the user provides a path.

Git is optional. If Git is unavailable, use a local folder snapshot identified
by scan id, timestamp, root path, and file hashes.

Exclude:

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

Use one primary category:

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

Apply only `safe` fixes. Never apply `review-required` or `blocked` fixes.

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
- tenant or payment logic changes
- URL allowlist policy
- Android cleartext or iOS ATS tightening
- crypto migrations that affect stored data compatibility

After safe edits, rescan changed files or the full target and update the
artifact bundle.

## Doctor

Verify:

- plugin Markdown files exist
- target root is readable
- `.presecurity/scans/` can be created
- no bundled runtime runner is required
- Git is optional

## Cleanup

Remove only `.presecurity/` from the target root.

## Response

Always return:

- artifact directory
- findings by severity
- safe fixes applied
- review-required findings
- blocked findings
- proof gaps and limitations
