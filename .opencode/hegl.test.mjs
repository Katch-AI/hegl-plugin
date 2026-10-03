import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import v2Plugin, { HeglPlugin, SKILLS_DIR, createSetup } from './plugins/hegl.js';

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

test('config hook leaves a V2-shaped config untouched', async () => {
  const plugin = await HeglPlugin({});
  const config = { skills: [] };
  await plugin.config(config);
  assert.deepEqual(config, { skills: [] });
});

test('default skills dir is ../../skills relative to the plugin file', () => {
  assert.equal(SKILLS_DIR, skillsDir);
  assert.equal(v2Plugin.id, 'hegl');
});

const makeSkillsDir = (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'hegl-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
};

const writeSkill = (dir, name, text) => {
  fs.mkdirSync(path.join(dir, name));
  fs.writeFileSync(path.join(dir, name, 'SKILL.md'), text);
};

const recordingCtx = () => {
  const added = [];
  const ctx = { skill: { transform: async (fn) => fn({ add: (s) => added.push(s) }) } };
  return { ctx, added };
};

test('V2 setup registers each SKILL.md through ctx.skill.transform', async (t) => {
  const dir = makeSkillsDir(t);
  writeSkill(dir, 'alpha', '---\nname: alpha\ndescription: Use when testing\n---\nBody\n');
  const { ctx, added } = recordingCtx();
  await createSetup(dir)(ctx);
  assert.deepEqual(added, [{
    id: 'alpha',
    name: 'alpha',
    description: 'Use when testing',
    path: path.join(dir, 'alpha', 'SKILL.md'),
    content: 'Body\n',
  }]);
});

test('V2 setup skips an unreadable SKILL.md and keeps the rest', async (t) => {
  const dir = makeSkillsDir(t);
  writeSkill(dir, 'good', '---\nname: good\n---\nOk\n');
  fs.mkdirSync(path.join(dir, 'bad', 'SKILL.md'), { recursive: true });
  t.mock.method(console, 'error', () => {});
  const { ctx, added } = recordingCtx();
  await createSetup(dir)(ctx);
  assert.deepEqual(added.map((s) => s.id), ['good']);
});

test('V2 setup returns before touching a V1-shaped ctx', async (t) => {
  const errors = t.mock.method(console, 'error', () => {});
  await v2Plugin.setup({});
  await v2Plugin.setup({ skill: {} });
  assert.equal(errors.mock.callCount(), 0);
});
