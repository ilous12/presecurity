# presecurity development TODO

This TODO assumes a Markdown-first plugin. The agent host reads the
command/skill contract and performs repository inspection, artifact writing,
and tiered autofix edits directly.

## Design Baseline

```text
read -> analyze -> report -> autofix -> rescan
```

presecurity borrows Codex Security's public artifact model:

- `scan-manifest.json`
- `scan-summary.json`
- `repository-map.json`
- `threat-model.json`
- `findings.json`
- `coverage.json`
- `validation/<finding-id>.json`
- `patches/<finding-id>.patch.md`
- `report.md`
- `fix-plan.json`
- `autofix-result.json`

`scan` always means read, analyze, and report. A scan is incomplete if
`report.md` is missing.

Git is optional. Without Git, use a sealed local snapshot:

- scan id
- timestamp
- root path
- include/exclude policy
- file hashes
- artifact directory

## Phase 1. Markdown Plugin Foundation

1. Keep one Claude command at
   `plugins/claude/presecurity/commands/presecurity.md`.
2. Keep one Codex command at
   `plugins/codex/presecurity/commands/presecurity.md`.
3. Keep one Codex skill at
   `plugins/codex/presecurity/skills/presecurity/SKILL.md`.
4. Keep plugin packages free of bundled runtime runners.
5. Update plugin manifests so the product is described as agent-driven,
   Markdown-first, and local-first.
6. Keep marketplace files for GitHub installation.
7. Document that the host agent performs file reads, artifact writes, and
   tiered autofix edits directly.

Acceptance:

- No tracked language runtime package or plugin `bin/` runtime.
- Claude and Codex instructions describe the same artifact contract.
- README explains the current product shape.

## Phase 2. Artifact Contract

1. Define `.presecurity/scans/scan-YYYYMMDD-HHMMSS/`.
2. Define `scan-manifest.json` fields:
   - `schemaVersion`
   - `scanId`
   - `tool`
   - `mode`
   - `target`
   - `sourceSnapshot`
   - `languages`
   - `artifactPaths`
   - `limitations`
3. Define `scan-summary.json` fields:
   - `status`
   - `coverageTotals`
   - `severityTotals`
   - `measuredRiskDistribution`
   - `topMaterialRisks`
   - `remediationPriorityQueue`
   - `deferredLowSignalCandidates`
   - `artifactIndex`
4. Define `repository-map.json` fields:
   - `files`
   - `frameworks`
   - `entrypoints`
   - `trustBoundaryHints`
   - `sensitiveSinks`
   - `dependencyFiles`
   - `configurationFiles`
5. Define `threat-model.json` fields:
   - `assets`
   - `entrypoints`
   - `untrustedInputs`
   - `trustBoundaries`
   - `authAssumptions`
   - `sensitiveDataPaths`
   - `priorityReviewAreas`
   - `scopedOutAreas`
6. Define `findings.json` fields:
   - `id`
   - `title`
   - `category`
   - `threatScore`
   - `likelihood`
   - `impact`
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
7. Define `validation/<finding-id>.json` fields:
   - `validationStatus`
   - `reproductionOrStrongestExploitCheck`
   - `legitimateBehaviorChecks`
   - `nearbyBypassChecks`
   - `evidence`
   - `counterEvidence`
   - `remainingProofGap`
   - `reviewerDecisionNeeded`
8. Define `patches/<finding-id>.patch.md` sections:
   - root-cause remediation approach
   - expected diff summary
   - regression or verification plan
   - residual risk
   - rollback notes
9. Define `coverage.json` fields:
   - `reviewedFiles`
   - `skippedFiles`
   - `deferredSurfaces`
   - `deferredSignals`
   - `limitations`
   - `proofGaps`
10. Define `fix-plan.json` fields:
   - `mode`
   - `items`
   - `safeCount`
   - `reviewRequiredCount`
   - `blockedCount`
11. Define `autofix-result.json` fields:
   - `applied`
   - `skipped`
   - `rescanSummary`
   - `remainingFindings`

Acceptance:

- A scan can be reviewed from artifacts alone.
- Every scan writes `report.md` automatically.
- Every material finding has measured threat score, evidence,
  counterevidence, validation status, and proof gap fields.
- `findings.json` defaults to critical/high/meaningful medium findings.
- Low/info/speculative observations are deferred into coverage/report
  limitations unless they materially change risk.
- Every unsafe or ambiguous remediation is marked `review-required` or
  `blocked`.

## Phase 3. General Codebase Coverage

1. Add analysis guidance for Web:
   - JavaScript
   - TypeScript
   - React
   - Next.js
   - Vue
   - Svelte
2. Add analysis guidance for Backend:
   - Node.js
   - Python
   - Java
   - Kotlin
   - Go
   - Ruby
   - PHP
3. Add analysis guidance for Mobile:
   - Java
   - Kotlin
   - Swift
   - Objective-C
   - Dart
   - plist
4. Add analysis guidance for Native:
   - C
   - C++
5. Add analysis guidance for Config and supply chain:
   - JSON
   - YAML
   - XML
   - Dockerfile
   - Terraform
   - Gradle
   - Maven
   - GitHub Actions
   - CI configuration

Acceptance:

- The command/skill tells the agent what to inspect for each platform family.
- Python and shell are not required as implementation languages.

## Phase 4. Threat Taxonomy

Implement review guidance for:

1. Injection
2. Broken Authentication
3. Broken Authorization
4. SSRF / Unsafe Network
5. Secret Exposure
6. Insecure Storage
7. Crypto Misuse
8. Deserialization
9. Path / File Access
10. XSS / HTML Injection
11. WebView / Client Bridge
12. Deep Link / Intent
13. Insecure Config
14. Supply Chain
15. CI/CD / Build Script
16. Business Logic
17. Multi-Tenant Isolation
18. Logging / Error Leak
19. Race / TOCTOU
20. Resource Abuse
21. Native / Memory Safety
22. AI Agent / Tool Risk

Acceptance:

- Findings map to exactly one primary threat category.
- Secondary categories may be added only when they clarify remediation.

## Phase 5. Tiered Autofix

1. Classify every finding as `safe`, `review-required`, or `blocked`.
2. Default `/presecurity autofix` and `/presecurity autofix safe` apply only
   `safe` fixes.
3. `/presecurity autofix review-required` applies `safe` fixes first, then
   `review-required` fixes.
4. `/presecurity autofix blocked` applies `safe` fixes first, then
   `review-required` fixes, then `blocked` fixes.
5. Keep edits minimal and deterministic.
6. Apply root-cause fixes only; do not apply partial mitigations.
7. Apply one fix at a time, check impact, then continue iterating.
8. Write `autofix-result.json`.
9. Rescan the changed files or the whole target.
10. Update `report.md` with before/after status.

Acceptance:

- Policy-dependent or blocked fixes are applied only when the user invokes the
  matching explicit autofix mode.
- Every applied fix names exact files and changed intent.
- No applied fix is reported as `partially mitigated`; unresolved policy gaps
  stay unresolved.
- SSRF fixes use allowlists or central outbound policy, not blocklist-only
  hardening.
- Remaining findings are reported after rescan.

## Phase 6. Verification

1. Run `git status --short` when Git exists, only to show changed files.
2. Validate JSON artifacts with the host's available JSON parser.
3. Re-open `report.md` and verify required sections exist.
4. For autofix, inspect the working tree diff if Git exists.
5. If no Git exists, list changed files from `autofix-result.json`.

Acceptance:

- Final response includes artifact directory.
- Final response includes applied fixes and remaining risks.
- Final response includes validation gaps.

## Phase 7. Fixture Corpus

1. Maintain intentionally vulnerable examples under `examples/`.
2. Keep one small fixture per supported language or framework family.
3. Document the expected primary threat category in `examples/README.md`.
4. Use examples for plugin development scans:
   - `examples`
   - `examples/web`
   - `examples/backend`
   - `examples/mobile`
   - `examples/native`
   - `examples/config`
5. Do not add shell-based exploit runners.
6. Do not require dependencies to install or apps to boot.
7. Prefer short source files whose vulnerable intent is obvious to a reviewer.

Acceptance:

- CI verifies all required fixture paths exist.
- The fixture matrix covers Web, Backend, Mobile, Native, and Config.
- Each fixture maps to one primary presecurity threat category.
