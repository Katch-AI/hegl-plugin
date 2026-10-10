# Hegl plugin

Build, measure and improve [Hegl](https://hegl.ai) agents from your own coding harness. The plugin registers the Hegl MCP server (`https://app.hegl.ai/mcp`) and the skills Hegl's hosted coding agent works from. Sign-in happens in your browser on first use; a new email gets a link to create an account. Whenever a step needs you (connecting an account, filling a form, publishing), the right dashboard page opens in your browser: in Claude Code a hook does it (set `HEGL_NO_BROWSER=1` to turn that off), elsewhere the skills ask your coding agent to.

## Install

**Claude Code**

```
/plugin marketplace add Katch-AI/hegl-plugin
/plugin install hegl
```

**Codex**

Add the marketplace from the shell, then install from `/plugins`: `codex plugin marketplace add Katch-AI/hegl-plugin`. On first use Codex asks you to authorize `hegl` through the browser.

Alternatively, add it to `~/.codex/config.toml`:

```toml
[marketplaces.hegl]
source_type = "git"
source = "https://github.com/Katch-AI/hegl-plugin"
```

**OpenCode**

See [.opencode/INSTALL.md](.opencode/INSTALL.md).

## What you get

- The `hegl` MCP server: every operation the hosted coding agent can perform, as tools, acting as you.
- Fifteen skills: `hegl` (start here), `build`, `feedback`, `fix-errors`, `building-the-automation`, `implementing-decision-boxes`, `linking-to-the-dashboard`, `platform-api`, `activepieces`, `fetching-data-via-pieces`, `calling-custom-apis`, `composing-email-html`, `rendering-templates`, `mermaid`, `asciidoc`.

Start with "list my Hegl organizations" and go from there.

## Commands

In Claude Code, three of the skills are commands. Each takes an optional agent name.

```
/hegl:build [agent]        start building an agent, or pick up where the build stopped
/hegl:feedback [agent]     see what people complained about and improve the agent on it
/hegl:fix-errors [agent]   find out why runs are failing and fix it
```

In Codex and OpenCode, ask in words ("fix the errors on my agent") and the same skill loads.

## Developing against another Hegl host

The plugin points at production. To use a development host, register the server by hand (`claude mcp add --transport http hegl https://<host>/mcp`) and disable the plugin's server, or edit `.mcp.json` in a local checkout installed from a path.

## License

MIT.
