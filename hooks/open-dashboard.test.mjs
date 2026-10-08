import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { browserCommand, dashboardUrls, recentlyOpened, safeUrl, toolOf, urlToOpen } from './open-dashboard.mjs';

const connectionUrl = 'https://app.hegl.ai/o/org-1/agents/a-1/build/connections';
const mcpText = (data) => [{ type: 'text', text: JSON.stringify(data, null, 2) }];

test('names the tool for the plugin server and a hand-registered one', () => {
  assert.equal(toolOf('mcp__plugin_hegl_hegl__request_connection'), 'request_connection');
  assert.equal(toolOf('mcp__hegl__request_connection'), 'request_connection');
  assert.equal(toolOf('mcp__other__request_connection'), null);
});

test('finds dashboardUrl in JSON text blocks and in structured content', () => {
  const data = { requestConnection: { connectionRequirement: { dashboardUrl: connectionUrl }, errors: [] } };
  assert.deepEqual(dashboardUrls(mcpText(data)), [connectionUrl]);
  assert.deepEqual(dashboardUrls({ structuredContent: data }), [connectionUrl]);
});

test('reads the single text block Claude Code passes for an MCP result', () => {
  const response = { type: 'text', text: JSON.stringify({ requestConfig: { configRequirement: { dashboardUrl: connectionUrl } } }) };
  assert.equal(urlToOpen({ tool_name: 'mcp__plugin_hegl_hegl__request_config', tool_response: response }), connectionUrl);
});

test('opens for a tool that hands the user a step, not for a read', () => {
  const response = mcpText({ requestConnection: { connectionRequirement: { dashboardUrl: connectionUrl } } });
  assert.equal(urlToOpen({ tool_name: 'mcp__plugin_hegl_hegl__request_connection', tool_response: response }), connectionUrl);
  assert.equal(urlToOpen({ tool_name: 'mcp__plugin_hegl_hegl__get_agent', tool_response: response }), null);
});

test('opens the plans page when a build is refused for want of a plan', () => {
  const response = { type: 'text', text: 'Choose a plan to build agents: https://app.hegl.ai/o/org-1/billing/plans' };
  assert.equal(urlToOpen({ tool_name: 'mcp__plugin_hegl_hegl__create_agent', tool_response: response }),
    'https://app.hegl.ai/o/org-1/billing/plans');
  assert.equal(urlToOpen({ tool_name: 'mcp__plugin_hegl_hegl__create_agent', hook_event_name: 'PostToolUseFailure',
    error: 'Choose a plan to build agents: https://app.hegl.ai/o/org-1/billing/plans' }), 'https://app.hegl.ai/o/org-1/billing/plans');
});

test('opens only https, or http on localhost for a development host', () => {
  assert.equal(safeUrl('https://app.hegl.ai/x'), 'https://app.hegl.ai/x');
  assert.equal(safeUrl('http://localhost:3000/x'), 'http://localhost:3000/x');
  assert.equal(safeUrl('http://evil.example/x'), null);
  assert.equal(safeUrl('file:///etc/passwd'), null);
  assert.equal(safeUrl('javascript:alert(1)'), null);
});

test('opens the same URL once in ten minutes', () => {
  const state = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'hegl-hook-')), 'state.json');
  assert.equal(recentlyOpened(state, connectionUrl, 0), false);
  assert.equal(recentlyOpened(state, connectionUrl, 60_000), true);
  assert.equal(recentlyOpened(state, connectionUrl, 11 * 60_000), false);
});

test('keeps the opened URL out of the state file, since a request link is a credential', () => {
  const state = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'hegl-hook-')), 'state.json');
  recentlyOpened(state, 'https://app.hegl.ai/requests/secret-token', 0);
  assert.equal(fs.readFileSync(state, 'utf8').includes('secret-token'), false);
});

test('uses the platform opener, and none without a display or in CI', () => {
  assert.deepEqual(browserCommand('darwin', {}), ['open']);
  assert.deepEqual(browserCommand('win32', {}), ['cmd', '/c', 'start', '""']);
  assert.deepEqual(browserCommand('linux', { DISPLAY: ':0' }), ['xdg-open']);
  assert.equal(browserCommand('linux', {}), null);
  assert.equal(browserCommand('darwin', { CI: 'true' }), null);
  assert.equal(browserCommand('darwin', { HEGL_NO_BROWSER: '1' }), null);
});
