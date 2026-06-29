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
6. Run `/presecurity scan`.

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
/presecurity
/presecurity scan
/presecurity autofix
/presecurity autofix safe
/presecurity autofix review-required
/presecurity autofix blocked
/presecurity doctor
/presecurity cleanup
```

The `$presecurity` skill is also available for natural-language invocation in
Codex.

Default `/presecurity` behavior:

```text
show available commands only
```

`/presecurity` by itself does not start a scan. Use `/presecurity scan` to run:

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
findings, safe autofix count, review-required count, blocked count, and
limitations.

`/presecurity autofix` behavior:

```text
read latest artifacts -> apply safe-only fixes -> rescan -> update report
```

Command completion depends on the host. The plugin exposes `/presecurity`
through `commands/presecurity.md` and provides the argument hint
`scan|autofix [safe|review-required|blocked]|doctor|cleanup` for hosts that
surface command arguments.

## Artifacts

Every completed scan writes a self-contained artifact bundle:

```text
.presecurity/
  scans/
    scan-YYYYMMDD-HHMMSS/
      scan-manifest.json
      repository-map.json
      threat-model.json
      findings.json
      coverage.json
      report.md
      fix-plan.json
      autofix-result.json
```

Required meanings:

- `scan-manifest.json`: target, scan id, snapshot identity, language summary,
  artifact paths, and limitations.
- `repository-map.json`: files, frameworks, entry points, dependencies, config
  surfaces, and sensitive sinks.
- `threat-model.json`: assets, entry points, trust boundaries, auth
  assumptions, sensitive data paths, and review priorities.
- `findings.json`: structured findings with severity, confidence,
  reachability, exploitability, business impact, evidence, counterevidence,
  proof gaps, and remediation guidance.
- `coverage.json`: reviewed files, skipped files, deferred surfaces,
  unverified claims, and limitations.
- `report.md`: portable human-readable report generated by every scan.
- `fix-plan.json`: safe/review-required/blocked fix classification.
- `autofix-result.json`: exact changes applied and rescan result.

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
| `review-required` | Security policy or business intent decision needed | Apply only with `/presecurity autofix review-required` or higher |
| `blocked` | Intent unclear or fix is too broad | Apply only with `/presecurity autofix blocked` |

Autofix modes:

| Command | Risk tiers processed |
| --- | --- |
| `/presecurity autofix` | `safe` |
| `/presecurity autofix safe` | `safe` |
| `/presecurity autofix review-required` | `safe` -> `review-required` |
| `/presecurity autofix blocked` | `safe` -> `review-required` -> `blocked` |

Every mode applies fixes sequentially. After each individual fix, presecurity
checks impact, rescans changed files when possible, updates the finding status,
and then continues. If an impact check fails or the diff becomes broad,
destructive, or ambiguous, the mode stops and reports the remaining items.

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
- Adding URL allowlists.
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
/presecurity scan examples
/presecurity scan examples/mobile/android-kotlin
/presecurity autofix
```

The examples are not production samples. They exist to verify finding
categories, evidence quality, coverage artifacts, and tiered autofix behavior.
