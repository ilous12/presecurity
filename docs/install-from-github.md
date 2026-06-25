# Install from GitHub

presecurity is distributed as a GitHub-hosted plugin marketplace repository for
Claude Code and Codex Desktop.

Repository:

```text
https://github.com/ilous12/presecurity
```

## Claude Code

Add this repository as a Claude plugin marketplace:

```text
/plugin marketplace add https://github.com/ilous12/presecurity
```

Then install the plugin from that marketplace:

```text
/plugin install presecurity@presecurity-marketplace
```

After installation, use:

```text
/presecurity init
/presecurity scan
/presecurity autofix
```

The Claude marketplace definition lives at `.claude-plugin/marketplace.json`.

## Codex Desktop / Codex CLI

Codex can read this repository as a repo marketplace because it contains
`.agents/plugins/marketplace.json`.

CLI flow:

```bash
codex plugin marketplace add \
  ilous12/presecurity \
  --ref main \
  --sparse .agents/plugins \
  --sparse plugins/codex/presecurity

codex plugin add presecurity@presecurity
```

Desktop flow:

1. Open Codex settings.
2. Open Plugins.
3. Add marketplace source `ilous12/presecurity`.
4. Install `presecurity`.
5. Start a new thread and invoke `/presecurity init`, `/presecurity scan`, or
   `/presecurity autofix`.

## No separate scanner install

Both plugin packages include a bundled copy of the Python scanner under
`bin/presecurity`. The host plugin runner sets `PYTHONPATH` to that bundled
engine before running commands.
