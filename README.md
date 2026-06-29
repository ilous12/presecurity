# presecurity

![presecurity logo](assets/presecurity-logo.png)

presecurity is a Markdown-first security review plugin for coding agents.
It helps Claude Code and Codex read a codebase, reason about security intent,
produce reviewable artifacts, and apply tiered fixes with safe-only behavior by
default.

The product shape is intentionally close to Codex Security's public artifact
model, but smaller and local-first:

```text
read -> analyze -> report -> autofix -> rescan
```

## Installation

Repository:

```text
https://github.com/ilous12/presecurity
```

Claude Code:

```text
/plugin marketplace add https://github.com/ilous12/presecurity
/plugin install presecurity@presecurity-marketplace
```

Claude Desktop:

1. Open Claude Desktop.
2. Open the Customize menu in the left sidebar.
3. Open the Plugins tab.
4. In Personal plugins, click `+` and choose Add marketplace.
5. Choose Add from a repository.
6. Enter `https://github.com/ilous12/presecurity`.
7. Install `presecurity`.
8. Start a new chat or Cowork task.
9. Run `/presecurity scan`.

Claude Desktop can also install a custom plugin file if you package and share
one separately. For repository-based installation, use the marketplace flow
above so updates can be synced from GitHub.

Codex CLI:

```text
codex plugin marketplace add ilous12/presecurity --ref main --sparse .agents/plugins --sparse plugins/codex/presecurity
codex plugin add presecurity@presecurity
```

Codex Desktop:

1. Open Codex settings.
2. Open Plugins.
3. Add marketplace source `ilous12/presecurity`.
4. Install `presecurity`.
5. Start a new thread.
6. Run `@presecurity scan`.

## Product Contract

presecurity is not a traditional rule-only scanner. The plugin instructions
ask the host coding agent to inspect code intent, trust boundaries, attacker
inputs, sensitive sinks, evidence, counterevidence, proof gaps, and safe fix
eligibility.

The project minimizes Python and shell. The implementation contract lives in
Markdown so agent hosts can execute the workflow directly from the command or
skill instructions.

User-facing plugin output follows the current host/user language setting:
English settings show English command help, progress, and summaries; Korean
settings show Korean command help, progress, and summaries. Artifact schemas,
JSON keys, file names, command names, finding IDs, and code identifiers stay
stable.

## Supported Inputs

presecurity must support general-purpose codebases. Initial analysis coverage
includes:

- Web: JavaScript, TypeScript, React, Next.js, Vue, Svelte
- Backend: Node.js, Python, Java, Kotlin, Go, Ruby, PHP
- Mobile: Java, Kotlin, Swift, Objective-C, Dart, plist
- Native: C, C++
- Config: JSON, YAML, XML, plist, Dockerfile, Terraform, Gradle, Maven,
  GitHub Actions, CI configuration
- Package metadata: npm, pnpm, yarn, pip, Poetry, Gradle, Maven, pub,
  CocoaPods, SwiftPM

Git is optional. When Git is unavailable, presecurity treats the target as a
local folder snapshot and identifies the run by scan id, timestamp, root path,
and file hashes.

## Commands

Claude Code:

```text
/presecurity
/presecurity scan
/presecurity autofix
/presecurity autofix safe
/presecurity autofix review-required
/presecurity autofix blocked
/presecurity doctor
/presecurity cleanup
```

Codex:

```text
@presecurity
@presecurity scan
@presecurity autofix
@presecurity autofix safe
@presecurity autofix review-required
@presecurity autofix blocked
@presecurity doctor
@presecurity cleanup
```

The `$presecurity` skill is also available for natural-language invocation in
Codex.

Default command behavior:

```text
show available commands only
```

Claude uses `/presecurity`; Codex uses `@presecurity`. The command by itself
does not start a scan. Use `/presecurity scan` in Claude or
`@presecurity scan` in Codex to run:

```text
read -> analyze -> report
```

A scan is not complete until `report.md` and the structured JSON artifacts are
written.

During a scan, the screen should show progress only. It should not show
`Wrote ...`, `Created ...`, file paths, detailed findings, evidence, attack
paths, or remediation notes while artifacts are being written. Those details
belong in `report.md` and JSON artifacts. After the scan completes, the agent
should print only a compact summary: artifact directory, severity totals, top
findings, safe autofix count, review-required count, blocked count, recommended
autofix command, and limitations.

Autofix behavior:

```text
read latest artifacts -> apply safe-only fixes -> rescan -> update report
```

Command completion depends on the host. Claude exposes `/presecurity`; Codex
exposes `@presecurity`. Both provide the argument hint
`scan|autofix [safe|review-required|blocked]|doctor|cleanup` for hosts that
surface command arguments.

## Artifacts

Every completed scan writes a self-contained artifact bundle:

```text
.presecurity/
  scans/
    scan-YYYYMMDD-HHMMSS/
      scan-manifest.json
      scan-summary.json
      repository-map.json
      threat-model.json
      findings.json
      coverage.json
      validation/
        F-001.json
      patches/
        F-001.patch.md
      report.md
```

Autofix additionally writes:

```text
      fix-plan.json
      autofix-result.json
```

Required meanings:

- `scan-manifest.json`: target, scan id, snapshot identity, language summary,
  artifact paths, and limitations.
- `scan-summary.json`: executive scan result with status, coverage totals,
  severity totals, measured risk distribution, top material risks, and
  remediation priority.
- `repository-map.json`: files, frameworks, entry points, dependencies, config
  surfaces, and sensitive sinks.
- `threat-model.json`: assets, entry points, trust boundaries, auth
  assumptions, sensitive data paths, review priorities, and scoped-out areas.
- `findings.json`: high-signal findings only. Each finding records measured
  threat score, severity, likelihood, impact, confidence, reachability,
  exploitability, business impact, evidence, counterevidence, proof gaps, and
  remediation guidance.
- `validation/<finding-id>.json`: validation evidence for each material
  finding, including attempted reproduction, strongest feasible exploit check,
  legitimate-behavior checks, nearby bypass checks, and remaining proof gap.
- `patches/<finding-id>.patch.md`: root-cause patch proposal for each accepted
  or fixable finding, including rationale, diff summary, regression evidence,
  rollback notes, and residual risk.
- `coverage.json`: reviewed files, skipped files, deferred surfaces,
  unverified claims, low-signal/deferred candidates, and limitations.
- `report.md`: portable human-readable report generated by every scan.
- `fix-plan.json`: safe/review-required/blocked fix classification.
- `autofix-result.json`: exact changes applied and rescan result.

## Threat Scoring

presecurity should focus on real, material security risk. It should not fill
the report with theoretical, low-impact, or unverified issues.

Each finding must include a measured threat score:

```text
threatScore = likelihood x impact x reachability x exploitability x confidence
```

Use normalized `0.0` to `1.0` factors and map the result to severity:

| Severity | Threat Score | Meaning |
| --- | --- | --- |
| `critical` | `>= 0.80` | Systemic compromise, tenant/data takeover, RCE, or critical secret exposure |
| `high` | `>= 0.60` | Realistic exploit path with high security or business impact |
| `medium` | `>= 0.35` | Plausible exploit path with scoped or conditional impact |
| `low` | `>= 0.15` | Hardening issue or weak exploit path |
| `info` | `< 0.15` | Context signal, not a confirmed vulnerability |

`findings.json` should include only `critical`, `high`, and meaningful
`medium` findings by default. Low/info signals, speculative concerns, and
missing-context notes belong in `coverage.json.deferredSignals` or
`report.md` limitations unless they materially change risk.

Professional analysis must prioritize:

- attacker-controlled entry point to sensitive sink
- crossed trust/auth/tenant boundary
- realistic exploit preconditions
- business or data impact
- validation evidence and counterevidence
- root-cause remediation and residual risk

## Threat Categories

presecurity focuses on code-level intent and exploit paths, not isolated
function names. Findings should map to one of these categories:

| ID | Category | Review Focus |
| --- | --- | --- |
| T01 | Injection | SQL, command, NoSQL, LDAP, template, eval, expression injection |
| T02 | Broken Authentication | Login, session, token, password, MFA, refresh rotation |
| T03 | Broken Authorization | Role, owner, tenant, resource, admin-only action checks |
| T04 | SSRF / Unsafe Network | User-controlled URL, redirect, internal IP, metadata endpoint |
| T05 | Secret Exposure | API keys, tokens, certificates, client secrets, checked-in creds |
| T06 | Insecure Storage | Plain local storage of tokens, PII, secrets, private files |
| T07 | Crypto Misuse | Weak algorithm, hardcoded key, static IV, custom crypto |
| T08 | Deserialization | Untrusted pickle, YAML, Java serialization, PHP/Ruby marshal |
| T09 | Path / File Access | Traversal, unsafe upload/extract/delete, arbitrary file IO |
| T10 | XSS / HTML Injection | DOM sinks, template output, unsafe markdown/HTML rendering |
| T11 | WebView / Client Bridge | JavaScript bridge, platform channel, untrusted content |
| T12 | Deep Link / Intent | Unsafe intent extras, schemes, universal links, exported actions |
| T13 | Insecure Config | Debug, cleartext, CORS wildcard, ATS exception, permissive policy |
| T14 | Supply Chain | Dependency confusion, lockfile risk, script hooks, unsafe packages |
| T15 | CI/CD / Build Script | Secret logging, untrusted PR execution, unsigned release paths |
| T16 | Business Logic | Payment, quota, coupon, state transition, workflow bypass |
| T17 | Multi-Tenant Isolation | Missing tenant filters, cross-org access, shared object leakage |
| T18 | Logging / Error Leak | Token, PII, stack trace, internal URL, sensitive debug output |
| T19 | Race / TOCTOU | Check/use split, replay, double submit, stale authorization |
| T20 | Resource Abuse | Rate limit gaps, zip bombs, unbounded upload, memory/CPU pressure |
| T21 | Native / Memory Safety | Buffer overflow, UAF, format string, unsafe pointer, integer overflow |
| T22 | AI Agent / Tool Risk | Prompt/tool injection, overbroad file/network/shell authority |

## Autofix Policy

presecurity applies only safe fixes by default. Higher-risk tiers require an
explicit autofix mode. Every finding receives an autofix status:

| Status | Meaning | Action |
| --- | --- | --- |
| `safe` | Narrow deterministic change with low behavior risk | Apply automatically |
| `review-required` | Security policy or business intent decision needed | Apply only with the host's `autofix review-required` command or higher |
| `blocked` | Intent unclear or fix is too broad | Apply only with the host's `autofix blocked` command |

Autofix modes:

| Claude command | Codex command | Risk tiers processed |
| --- | --- | --- |
| `/presecurity autofix` | `@presecurity autofix` | `safe` |
| `/presecurity autofix safe` | `@presecurity autofix safe` | `safe` |
| `/presecurity autofix review-required` | `@presecurity autofix review-required` | `safe` -> `review-required` |
| `/presecurity autofix blocked` | `@presecurity autofix blocked` | `safe` -> `review-required` -> `blocked` |

After every scan, recommend the highest needed autofix mode from the latest
artifact counts:

| Latest scan state | Claude recommendation | Codex recommendation |
| --- | --- | --- |
| Any `blocked` items exist | `/presecurity autofix blocked` | `@presecurity autofix blocked` |
| No `blocked`, any `review-required` items exist | `/presecurity autofix review-required` | `@presecurity autofix review-required` |
| Only `safe` items exist | `/presecurity autofix safe` | `@presecurity autofix safe` |
| No fixable items exist | No autofix recommended | No autofix recommended |

The recommendation is advisory. It must not apply fixes automatically after
`/presecurity scan` or `@presecurity scan`.

Every mode applies fixes sequentially. After each individual fix, presecurity
checks impact, rescans changed files when possible, updates the finding status,
and then continues. If an impact check fails or the diff becomes broad,
destructive, or ambiguous, the mode stops and reports the remaining items.

Autofix must address the root cause. It must not apply partial mitigations and
call them fixed. For example, SSRF fixes should use a positive allowlist of
approved destinations or a centrally enforced outbound policy; private-IP or
metadata-host blocklists are defense-in-depth only and must not replace the
allowlist. If the required business/security policy is unknown, presecurity
leaves the finding unresolved and reports the missing policy input.

Safe examples:

- `yaml.load(...)` -> `yaml.safe_load(...)` when imports and call shape are
  simple.
- `debug=True` -> `debug=False` in production-like app entry points.
- `verify=False` -> `verify=True` when no local/test guard exists.
- `innerHTML = plainValue` -> `textContent = plainValue` when no HTML rendering
  intent is present.
- Hardcoded credential-like values -> empty placeholder plus environment
  variable recommendation when the value is clearly synthetic or accidental.

Review-required examples:

- Replacing an authz model.
- Changing payment, tenant, or workflow state transitions.
- Designing the approved URL allowlist or outbound gateway policy.
- Tightening Android cleartext or iOS ATS exceptions.
- Replacing crypto used for compatibility with stored data.

## Documentation

- [Implementation readiness](docs/implementation-readiness.md)
- [Development TODO](docs/development-plan.md)
- [Supported platforms](docs/supported-platforms.md)
- [Example vulnerable fixtures](examples/README.md)

## Plugin Development Tests

The `examples/` folder contains intentionally vulnerable fixtures for every
supported platform family. Use it as the regression corpus for plugin behavior:

```text
Claude:
/presecurity scan examples
/presecurity scan examples/mobile/android-kotlin
/presecurity autofix

Codex:
@presecurity scan examples
@presecurity scan examples/mobile/android-kotlin
@presecurity autofix
```

The examples are not production samples. They exist to verify finding
categories, evidence quality, coverage artifacts, and tiered autofix behavior.
