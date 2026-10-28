import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
const cli = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'bin', 'cli.mjs');
const names = [
  'AGENTS.md', ...Array.from({ length: 15 }, (_,i) => `.codex/agents/ag${String(i+2).padStart(2,'0')}_fixture.toml`),
  ...Array.from({ length: 16 }, (_,i) => `.agents/skills/ss-test-${i+1}/SKILL.md`),
  'templates/SPEC.md','templates/PLAN.md','templates/TASK.md'
];
const hash = b => createHash('sha256').update(b).digest('hex');
async function fixture(t) {
  const root = await mkdtemp(join(tmpdir(), 'sixteensquad-npx-test-'));
  t.after(() => rm(root, { recursive:true, force:true }));
  const bin=join(root,'bin');
  const payload=join(root,'payload');
  await mkdir(bin);await mkdir(payload);
  const data = await readFile(cli);await writeFile(join(bin,'cli.mjs'),data);
  const files=[];
  for(const name of names) {
    const bytes=Buffer.from('TEST:' + name);
    const file=join(payload,...name.split('/'));
    await mkdir(dirname(file),{recursive:true});await writeFile(file,bytes);
    files.push({path:name,size:bytes.length,sha256:hash(bytes)});
  }
  await writeFile(join(payload,'manifest.json'),JSON.stringify({schema:1,product:'SixteenSquad Starter',files}));
  return {root,payload};
}
function run(root,args=[],cwd) { return spawnSync(process.execPath,[join(root,'bin','cli.mjs'),...args],{cwd,encoding:'utf8',timeout:10000}); }
test('help exibe os comandos do README', async t => {
  const {root}=await fixture(t);const res=run(root,['--help']);assert.equal(res.status,0);assert.match(res.stdout,/install starter/);
});
test('prévia no diretório atual com espaços, sem escrever', async t=>{
  const {root}=await fixture(t);const target=join(root,'projeto com espaços');await mkdir(target);
  const res=run(root,['install','starter','--preview'],target);
  assert.equal(res.status,0,res.stderr);assert.match(res.stdout,/35 arquivos: 35 novos/);
  await assert.rejects(readFile(join(target,'AGENTS.md')),{code:'ENOENT'});
});
test('prévia no destino absoluto explícito', async t=>{
  const {root}=await fixture(t);const target=join(root,'outro-projeto');
  const res=run(root,['install','starter',target,'--preview']);assert.equal(res.status,0,res.stderr);
});
test('conflito recusa sobrescrita e não instala nada', async t=>{
  const {root}=await fixture(t);const target=join(root,'project');await mkdir(target);
  await writeFile(join(target,'AGENTS.md'),'CUSTOM');
  const res=run(root,['install','starter',target,'--preview']);
  assert.equal(res.status,1);assert.match(res.stderr,/CONFLITO|Conflitos encontrados/);
  assert.equal(await readFile(join(target,'AGENTS.md'),'utf8'),'CUSTOM');
  await assert.rejects(readFile(join(target,'templates','SPEC.md')),{code:'ENOENT'});
});
test('arquivos idênticos são contados separadamente', async t=>{
  const {root}=await fixture(t);const target=join(root,'project');await mkdir(target);
  await writeFile(join(target,'AGENTS.md'),'TEST:AGENTS.md');
  const res=run(root,['install','starter',target,'--preview']);assert.equal(res.status,0,res.stderr);
  assert.match(res.stdout,/35 arquivos: 34 novos, 1 idênticos/);
});
test('não aceita argumentos desconhecidos', async t=>{
  const {root}=await fixture(t);const res=run(root,['install','starter','--delete']);assert.equal(res.status,1);
});
test('não aceita conteúdo de pacote alterado',async t=>{
  const {root,payload}=await fixture(t);await writeFile(join(payload,'AGENTS.md'),'X'.repeat('TEST:AGENTS.md'.length));
  const res=run(root,['install','starter','--preview']);assert.equal(res.status,1);
  assert.match(res.stderr,/hash.*divergente/i);
});
test('não aceita path traversal no manifesto',async t=>{
  const {root,payload}=await fixture(t);const manifestPath=join(payload,'manifest.json');
  const data=JSON.parse(await readFile(manifestPath,'utf8'));data.files[0].path='../escape';await writeFile(manifestPath,JSON.stringify(data));
  const res=run(root,['install','starter','--preview']);assert.equal(res.status,1);
});
test('interrompe sem terminal interativo antes da cópia', async t=>{
  const {root}=await fixture(t);const target=join(root,'project');
  const res=run(root,['install','starter',target]);assert.equal(res.status,1);
  assert.match(res.stderr,/Confirmação interativa/);
  await assert.rejects(readFile(join(target,'AGENTS.md')),{code:'ENOENT'});
});
test('recusa destino com symlink no caminho', async t=>{
  const {root}=await fixture(t);const dest=join(root,'outside');await mkdir(dest);
  const link=join(root,'shortcut');try { await symlink(dest,link,'dir'); } catch(e) { if (['EPERM','EACCES','ENOSYS'].includes(e.code)) { t.skip('Permissão para symlink indisponível');return; } throw e; }
  const res=run(root,['install','starter',join(link,'project'),'--preview']);assert.equal(res.status,1);
  assert.match(res.stderr,/Caminho inseguro/);
});
