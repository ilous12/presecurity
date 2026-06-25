# presecurity development plan

## Target

Build an internal GitHub-installable security plugin for Claude Code and Codex
Desktop. The plugin should scan code produced or modified during agent workflows,
list security findings, estimate impact, produce a fix plan, and apply only safe
deterministic fixes.

The active delivery scope is Phase 1, Phase 2, and Phase 3.

## Phase 1. Installable plugin foundation

Goal: employees can install presecurity from GitHub and run the same command
contract in Claude Code and Codex.

Deliverables:

- GitHub-hosted Claude marketplace at `.claude-plugin/marketplace.json`.
- GitHub-hosted Codex marketplace at `.agents/plugins/marketplace.json`.
- Bundled scanner inside both plugin packages.
- `/presecurity init`, `/presecurity scan`, `/presecurity autofix`, and
  `/presecurity cleanup` instructions.
- `docs/install-from-github.md`.
- Plugin validation in local verification.

Acceptance:

- Claude plugin validates.
- Codex plugin validates.
- Bundled runner works without installing the scanner as a separate package.
- README has GitHub installation instructions.

## Phase 2. Popular platform rule engine

Goal: cover high-signal risks across popular FE, BE, and infra stacks.

Initial supported platform families:

- FE: React, Next.js, Vue, Svelte, browser DOM.
- BE: Node.js, Express, NestJS, Python, Django, FastAPI, Flask, Java, Spring,
  Go, Ruby on Rails, PHP/Laravel.
- Infra: Docker, Kubernetes, Terraform, GitHub Actions.

Rule categories:

- OWASP A01 Broken Access Control.
- OWASP A02 Cryptographic Failures.
- OWASP A03 Injection.
- OWASP A05 Security Misconfiguration.
- OWASP A07 Identification and Authentication Failures.
- OWASP A08 Software and Data Integrity Failures.
- OWASP A10 Server-Side Request Forgery.

Acceptance:

- Rules map to OWASP category, severity, confidence, platform, impact, and
  recommendation.
- Scan output includes an ordered remediation plan.
- High-risk examples are covered by tests.

## Phase 3. Diff intent analysis

Goal: scan should explain what changed and what security-sensitive areas appear
to be affected, even before deep LLM review is added.

Deliverables:

- Git diff parser.
- Changed file summary.
- Added/removed line count.
- Security hints for auth, API routes, database access, outbound HTTP, file
  system access, shell execution, rendered HTML, CI/CD, and infrastructure.
- `intent` section in `.presecurity/scan-plan.json`.
- `--base <git-ref>` option for scan.

Acceptance:

- `scan` includes an intent summary when git diff is available.
- `scan --base <ref>` changes the diff base.
- Tests cover diff parsing and hint classification.

## Test plan

### Unit tests

- Rule matching for Python, JavaScript/TypeScript, Java, Go, Ruby, PHP, YAML,
  HCL, and Dockerfile examples.
- Intent parser for git unified diffs.
- Autofix transforms.
- State file creation.

### CLI tests

- `init` creates `.presecurity/config.json`, `history.jsonl`, and
  `scan-plan.json`.
- `scan` writes findings and intent to `scan-plan.json`.
- `scan --base HEAD` accepts a git base argument.
- `autofix` applies safe fixes and rescans.
- `cleanup` removes `.presecurity`.

### Plugin tests

- Claude bundled runner executes `init` and `scan`.
- Codex bundled runner executes `init` and `scan`.
- Claude plugin manifest validates.
- Codex plugin manifest validates.

### Regression tests

- Every new safe autofix gets a before/after test.
- Every high-risk rule gets at least one vulnerable fixture test.
- Any intentional vulnerable test fixture must use `presecurity: ignore` when
  it appears in scanner source or test source.
