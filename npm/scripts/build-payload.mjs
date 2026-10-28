#!/usr/bin/env node
// Build the npm payload from the canonical project-local starter/, never from an old ZIP.
import { createHash } from 'node:crypto';
import { readFile, readdir, lstat, mkdir, rm, writeFile, copyFile } from 'node:fs/promises';
import { dirname, join, resolve, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
const base = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repo = resolve(base, '..');
const starter = join(repo, 'starter');
const payload = join(base, 'payload');

const strictFiles = ['AGENTS.md', 'templates/SPEC.md', 'templates/PLAN.md', 'templates/TASK.md'];
async function collect(dir, filenameRe) {
  const dirs = await readdir(join(starter, dir), { withFileTypes: true });
  return dirs.filter(e => e.isFile() && filenameRe.test(e.name)).map(e => `${dir}/${e.name}`);
}
async function collectSkills() {
  const dirs = await readdir(join(starter, '.agents/skills'), { withFileTypes: true });
  const result = [];
  for (const item of dirs) {
    if (!item.isDirectory() || !/^ss-[a-z0-9-]+$/.test(item.name)) continue;
    result.push(`.agents/skills/${item.name}/SKILL.md`);
  }
  return result;
}
const profiles = await collect('.codex/agents', /^ag(?:0[2-9]|1[0-6])_[a-z0-9_]+\.toml$/);
const skills = await collectSkills();
if (profiles.length !== 15 || skills.length !== 16) {
  throw new Error(`Starter incompleto: ${profiles.length} perfis TOML e ${skills.length} skills; esperados 15/16.`);
}
const files = [...strictFiles, ...profiles, ...skills].sort();
if (files.length !== 35 || new Set(files.map(s => s.toLowerCase())).size !== 35) {
  throw new Error('Esperados exatamente 35 caminhos distintos no pacote.');
}
const manifest = { schema: 1, product: 'SixteenSquad Starter', files: [] };
let totalBytes = 0;
const staged = [];
for (const name of files) {
  const file = join(starter, ...name.split('/'));
  const info = await lstat(file);
  if (!info.isFile() || info.isSymbolicLink() || info.nlink > 1) {
    throw new Error(`Arquivo não regular ou com links: ${name}`);
  }
  const data = await readFile(file);
  totalBytes += data.length;
  if (data.length > 2 * 1024 * 1024 || totalBytes > 8 * 1024 * 1024) {
    throw new Error(`Starter excede o limite de tamanho: ${name}`);
  }
  staged.push({ name, data });
  manifest.files.push({ path: name, size: data.length, sha256: createHash('sha256').update(data).digest('hex') });
}
await rm(payload, { recursive: true, force: true });
await mkdir(payload, { recursive: true });
for (const { name, data } of staged) {
  const output = join(payload, ...name.split('/'));
  await mkdir(dirname(output), { recursive: true });
  await writeFile(output, data, { flag: 'wx' });
}
await writeFile(join(payload, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' });
console.log(`Payload preparado a partir de ${relative(repo, starter)}: 35 arquivos, ${totalBytes} bytes.`);
