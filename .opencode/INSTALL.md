# Installing the Hegl plugin for OpenCode

Add to `~/.config/opencode/opencode.json` (V1) or the V2 equivalent:

```json
{ "plugin": ["hegl@git+https://github.com/Katch-AI/hegl-plugin.git"] }
```

From a local checkout, use `"hegl@file:///absolute/path/to/hegl-plugin"` instead.

Restart OpenCode. The plugin registers the Hegl skills and the `hegl` MCP server
(`https://app.hegl.ai/mcp`); the first tool call opens the Hegl login.

OpenCode V2 gives plugins no way to add an MCP server, so V2 users add it to their config by hand:
`"mcp": { "hegl": { "type": "remote", "url": "https://app.hegl.ai/mcp", "enabled": true } }`

Verify: ask "What Hegl skills do you have?" and run `list_organizations`.
