# Hegl plugin

Build, measure and improve [Hegl](https://hegl.ai) agents from your own coding harness. The plugin registers the Hegl MCP server (`https://app.hegl.ai/mcp`, login through your browser on first use) and the skills Hegl's hosted coding agent works from.

## Install

**Claude Code**

```
/plugin marketplace add Katch-AI/hegl-plugin
/plugin install hegl
```

**Codex**

Add the marketplace to `~/.codex/config.toml`, then install from `/plugins`:

```toml
[marketplaces.hegl]
source_type = "git"
source = "https://github.com/Katch-AI/hegl-plugin"
```

The same from the shell: `codex plugin marketplace add Katch-AI/hegl-plugin`. On first use Codex asks you to authorize `hegl` through the browser.

**OpenCode**

See [.opencode/INSTALL.md](.opencode/INSTALL.md).

## What you get

- The `hegl` MCP server: every operation the hosted coding agent can perform, as tools, acting as you.
- Eleven skills: `hegl` (start here), `building-the-automation`, `implementing-decision-boxes`, `platform-api`, `activepieces`, `fetching-data-via-pieces`, `calling-custom-apis`, `composing-email-html`, `rendering-templates`, `mermaid`, `asciidoc`.

Start with "list my Hegl organizations" and go from there.

## Developing against another Hegl host

The plugin points at production. To use a development host, register the server by hand (`claude mcp add --transport http hegl https://<host>/mcp`) and disable the plugin's server, or edit `.mcp.json` in a local checkout installed from a path.

## License

MIT.
