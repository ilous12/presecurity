# presecurity development plan

## Product goal

Build a Claude Code and Codex Desktop marketplace plugin that detects security
issues while people use coding agents, creates a remediation plan, and safely
autofixes low-risk findings.

## Reference model

presecurity follows the same broad pattern as Anthropic's `security-guidance`:

1. Fast local pattern checks for known-dangerous APIs.
2. Diff-aware review before the agent declares work complete.
3. Commit/push review for broader context.
4. Project-local policy and history.

The first implementation keeps the scanner deterministic and local. LLM review
and commit hooks are planned as the next layer after the core command loop is
stable.

## Command contract

### `/presecurity init`

Creates `.presecurity/` and the initial management files.

### `/presecurity scan`

Scans the repository, lists all findings, records impact, and writes a sequential
fix plan to `.presecurity/scan-plan.json`.

### `/presecurity autofix`

Reads the current fix plan, applies safe deterministic fixes in order, rescans,
and records the result in `.presecurity/history.jsonl`.

### Plugin deletion

The scanner provides `presecurity cleanup` to delete `.presecurity/`. If a host
marketplace exposes uninstall hooks, the Claude/Codex adapters should call that
command on uninstall. Until then, plugin docs must expose `/presecurity cleanup`
or the direct CLI cleanup command as the fallback.

## Milestones

1. Repository and shared scanner MVP.
2. Claude plugin package with command and hook skeleton.
3. Codex plugin package with skill wrapper.
4. OWASP Top 10 mapping and 20 platform coverage metadata.
5. LLM diff review and agentic context review.
6. Marketplace polish: icon, screenshots, privacy policy, validation CI.

