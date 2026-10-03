/**
 * Hegl plugin for OpenCode: registers skills/ and the Hegl MCP server.
 * V1 (opencode): named export HeglPlugin with a config hook.
 * V2 (opencode 2.0.4+): default export { id, setup }.
 */
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
export const SKILLS_DIR = path.resolve(here, '../../skills');
export const MCP_SERVER = { type: 'remote', url: 'https://app.hegl.ai/mcp', enabled: true };

export function applyConfig(config) {
  // V2 hands over a flat skills array and an unverified config shape; setup() serves V2.
  if (Array.isArray(config.skills)) return;
  config.skills = config.skills || {};
  config.skills.paths = config.skills.paths || [];
  if (!config.skills.paths.includes(SKILLS_DIR)) config.skills.paths.push(SKILLS_DIR);
  config.mcp = config.mcp || {};
  if (!config.mcp.hegl) config.mcp.hegl = { ...MCP_SERVER };
}

export const HeglPlugin = async () => ({
  config: async (config) => { applyConfig(config); },
});

const extractAndStripFrontmatter = (content) => {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) return { frontmatter: {}, content };
  const frontmatter = {};
  let lastKey = null;
  for (const rawLine of match[1].split('\n')) {
    const line = rawLine.replace(/\r$/, '');
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0 && !/^\s/.test(line)) {
      const key = line.slice(0, colonIdx).trim();
      const value = line.slice(colonIdx + 1).trim();
      frontmatter[key] = /^(>[+-]?|\|[+-]?)$/.test(value) ? '' : value;
      lastKey = key;
    } else if (lastKey !== null && line.trim() !== '') {
      frontmatter[lastKey] = `${frontmatter[lastKey]} ${line.trim()}`.trim();
    }
  }
  for (const key of Object.keys(frontmatter)) {
    frontmatter[key] = frontmatter[key].replace(/^(["'])([\s\S]*)\1$/, '$2');
  }
  return { frontmatter, content: match[2] };
};

const readSkills = (dir) => {
  if (!fs.existsSync(dir)) return [];
  const skills = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name.startsWith('.')) continue;
    const skillPath = path.join(dir, entry.name, 'SKILL.md');
    if (!fs.existsSync(skillPath)) continue;
    try {
      const { frontmatter, content } = extractAndStripFrontmatter(fs.readFileSync(skillPath, 'utf8'));
      skills.push({
        id: entry.name,
        name: frontmatter.name || entry.name,
        ...(frontmatter.description ? { description: frontmatter.description } : {}),
        path: skillPath,
        content,
      });
    } catch (err) {
      console.error(`[hegl] skill "${entry.name}" unreadable, skipping:`, err);
    }
  }
  return skills;
};

export const createSetup = (skillsDir) => async function setup(ctx) {
  // V1 also calls default.setup with a ctx lacking the skill domain; HeglPlugin serves V1.
  if (!ctx || !ctx.skill || typeof ctx.skill.transform !== 'function') return;
  try {
    const skills = readSkills(skillsDir);
    await ctx.skill.transform((draft) => {
      // A throw escaping this callback makes the V2 host disable the whole plugin.
      for (const skill of skills) {
        try {
          draft.add(skill);
        } catch (err) {
          console.error(`[hegl] skill "${skill.id}" rejected by host, skipping:`, err);
        }
      }
    });
  } catch (err) {
    console.error('[hegl] skill registration failed:', err);
  }
};

export default {
  id: 'hegl',
  server: HeglPlugin,
  setup: createSetup(SKILLS_DIR),
};
