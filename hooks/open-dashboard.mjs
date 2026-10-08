#!/usr/bin/env node
/**
 * Claude Code PostToolUse hook: when a hegl tool starts a step only the user can take
 * (make a connection, fill a config form, review and publish a run), open the
 * result's dashboardUrl in their browser so nobody copies a link by hand.
 * Read-only tools never open anything; the same URL opens at most once in 10 minutes.
 */
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const OPENING_TOOLS = ['create_agent', 'request_connection', 'request_config', 'finish_improvement_run'];
const REOPEN_AFTER_MS = 10 * 60 * 1000;

export function toolOf(toolName = '') {
  const match = toolName.match(/^mcp__(?:plugin_hegl_)?hegl__(.+)$/);
  return match ? match[1] : null;
}

/** Every dashboardUrl in a tool response, wherever it sits: objects, arrays, or JSON text blocks. */
export function dashboardUrls(value, found = []) {
  if (typeof value === 'string') {
    const text = value.trim();
    if (text.startsWith('{') || text.startsWith('[')) {
      try { dashboardUrls(JSON.parse(text), found); } catch { /* plain text */ }
    }
  } else if (Array.isArray(value)) {
    value.forEach((item) => dashboardUrls(item, found));
  } else if (value && typeof value === 'object') {
    for (const [key, item] of Object.entries(value)) {
      if (key === 'dashboardUrl' && typeof item === 'string') found.push(item);
      else dashboardUrls(item, found);
    }
  }
  return found;
}

export function safeUrl(raw) {
  try {
    const url = new URL(raw);
    const local = ['localhost', '127.0.0.1'].includes(url.hostname);
    return url.protocol === 'https:' || (url.protocol === 'http:' && local) ? url.toString() : null;
  } catch {
    return null;
  }
}

/** The plans page a refusal points at ("Choose a plan to build agents: <url>"), if any. */
export function planUrl(value) {
  const match = JSON.stringify(value ?? '').match(/Choose a plan to build agents: (https?:\/\/[^\s"\\]+)/);
  return match ? match[1] : null;
}

/** The URL to open for this hook input, or null. */
export function urlToOpen(input) {
  const tool = toolOf(input.tool_name);
  if (!OPENING_TOOLS.includes(tool)) return null;
  const urls = [...dashboardUrls(input.tool_response), planUrl(input.tool_response ?? input.error)].map(safeUrl).filter(Boolean);
  return urls[0] ?? null;
}

export function recentlyOpened(statePath, url, now = Date.now()) {
  let state = {};
  try { state = JSON.parse(fs.readFileSync(statePath, 'utf8')); } catch { /* first run */ }
  const key = createHash('sha256').update(url).digest('hex');
  const fresh = typeof state[key] === "number" && now - state[key] < REOPEN_AFTER_MS;
  if (!fresh) {
    state[key] = now;
    try { fs.writeFileSync(statePath, JSON.stringify(state)); } catch { /* best effort */ }
  }
  return Boolean(fresh);
}

export function browserCommand(platform = process.platform, env = process.env) {
  if (env.HEGL_NO_BROWSER || env.CI) return null;
  if (platform === 'darwin') return ['open'];
  if (platform === 'win32') return ['cmd', '/c', 'start', '""'];
  return env.DISPLAY || env.WAYLAND_DISPLAY ? ['xdg-open'] : null;
}

async function main() {
  let raw = '';
  for await (const chunk of process.stdin) raw += chunk;
  const input = JSON.parse(raw || '{}');
  const url = urlToOpen(input);
  const command = browserCommand();
  if (!url || !command) return;

  const statePath = path.join(os.tmpdir(), `hegl-opened-${String(input.session_id || 'default').replace(/\W/g, '')}.json`);
  if (recentlyOpened(statePath, url)) return;

  const [bin, ...args] = command;
  spawn(bin, [...args, url], { detached: true, stdio: 'ignore' }).unref();
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: input.hook_event_name || 'PostToolUse',
      additionalContext: `The hegl plugin opened ${url} in the user's browser. Do not open it again; say in one line what to do there.`,
    },
  }));
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().catch(() => process.exit(0));
}
