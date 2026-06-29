# Install from GitHub

presecurity is distributed as a GitHub-hosted plugin marketplace repository for
Claude Code and Codex.

Repository:

```text
https://github.com/ilous12/presecurity
```

## Claude Code

Add this repository as a Claude plugin marketplace:

```text
/plugin marketplace add https://github.com/ilous12/presecurity
```

Install the plugin:

```text
/plugin install presecurity@presecurity-marketplace
```

Use:

```text
/presecurity
/presecurity scan
/presecurity autofix
/presecurity doctor
/presecurity cleanup
```

`/presecurity scan` automatically generates `report.md` and the structured
JSON artifact bundle.

The Claude marketplace definition lives at `.claude-plugin/marketplace.json`.

## Codex

Codex can read this repository as a repo marketplace because it contains
`.agents/plugins/marketplace.json`.

CLI flow:

```text
codex plugin marketplace add ilous12/presecurity --ref main --sparse .agents/plugins --sparse plugins/codex/presecurity
codex plugin add presecurity@presecurity
```

Desktop flow:

1. Open Codex settings.
2. Open Plugins.
3. Add marketplace source `ilous12/presecurity`.
4. Install `presecurity`.
5. Start a new thread.
6. Ask Codex to use `$presecurity`.

## Runtime Model

presecurity is Markdown-first. The command and skill files define the workflow,
artifact contract, threat taxonomy, and safe autofix policy for the host agent.
