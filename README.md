# presecurity

presecurity is a lightweight security assistant for coding agents.

It provides a shared scanner and autofix engine for Claude Code and Codex Desktop
plugins. The first release focuses on OWASP Top 10 oriented, low-risk SAST checks
that fit naturally into agent workflows.

## Commands

Use the plugin command form inside an agent:

```text
/presecurity init
/presecurity scan
/presecurity autofix
```

You can also run the engine directly from this repository:

```bash
python3 -m presecurity init
python3 -m presecurity scan
python3 -m presecurity autofix
```

## State

`/presecurity init` creates a project-local hidden state directory:

```text
.presecurity/
  config.json
  history.jsonl
  scan-plan.json
```

`/presecurity scan` updates `scan-plan.json` with findings, impact, and an
ordered remediation plan.

`/presecurity autofix` applies only safe, deterministic fixes from the latest
plan, then rescans to confirm the remaining state.

## Current scope

- OWASP Top 10 mapped checks
- Popular FE/BE/infra platform patterns
- Safe autofix for a narrow set of mechanical issues
- Agent-friendly plan/history files
- Claude Code plugin skeleton
- Codex Desktop plugin skeleton

This is not a replacement for full SAST, DAST, dependency scanning, or manual
application security review.

