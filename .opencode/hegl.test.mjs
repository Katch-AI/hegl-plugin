import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import plugin, { HeglPlugin } from './plugins/hegl.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const skillsDir = path.resolve(here, '../skills');

test('V1 config hook registers the skills dir and the remote MCP server', async () => {
  const plugin = await HeglPlugin({});
  const config = { mcp: { other: { type: 'local', command: ['x'] } } };
  await plugin.config(config);
  assert.deepEqual(config.skills.paths, [skillsDir]);
  assert.deepEqual(config.mcp.hegl, { type: 'remote', url: 'https://app.hegl.ai/mcp', enabled: true });
  assert.ok(config.mcp.other, 'keeps the user\'s own servers');
});

test('V1 config hook is idempotent', async () => {
  const plugin = await HeglPlugin({});
  const config = {};
  await plugin.config(config);
  await plugin.config(config);
  assert.equal(config.skills.paths.length, 1);
  assert.equal(Object.keys(config.mcp).length, 1);
});

test('V1 config hook does not override a user-defined hegl server', async () => {
  const plugin = await HeglPlugin({});
  const config = { mcp: { hegl: { type: 'remote', url: 'https://staging.example/mcp', enabled: true } } };
  await plugin.config(config);
  assert.equal(config.mcp.hegl.url, 'https://staging.example/mcp');
});

test('V2 setup registers each skills/*/SKILL.md through ctx.skill.transform', async (t) => {
  const fixtureDir = path.join(skillsDir, 'zz-test-fixture');
  fs.mkdirSync(fixtureDir);
  t.after(() => fs.rmSync(fixtureDir, { recursive: true, force: true }));
  fs.writeFileSync(path.join(fixtureDir, 'SKILL.md'), '---\nname: zz-test-fixture\ndescription: Use when testing\n---\nBody\n');
  const added = [];
  const ctx = { skill: { transform: async (fn) => fn({ add: (s) => added.push(s) }) } };
  await plugin.setup(ctx);
  assert.equal(plugin.id, 'hegl');
  assert.deepEqual(added.find((s) => s.id === 'zz-test-fixture'), {
    id: 'zz-test-fixture',
    name: 'zz-test-fixture',
    description: 'Use when testing',
    path: path.join(fixtureDir, 'SKILL.md'),
    content: 'Body\n',
  });
});

test('V2 setup returns quietly on a V1-shaped ctx', async () => {
  await plugin.setup({});
});
