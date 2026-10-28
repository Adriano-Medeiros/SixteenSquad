#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { lstat, mkdir, open, readFile, readdir, rmdir, rm } from 'node:fs/promises';
import { dirname, isAbsolute, join, parse, resolve, sep, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline/promises';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const payload = join(root, 'payload');
const LIMIT_BYTES = 2 * 1024 * 1024;
const permitted = name => name === 'AGENTS.md' || /^\.codex\/agents\/ag(?:0[2-9]|1[0-6])_[a-z0-9_]+\.toml$/.test(name) || /^\.agents\/skills\/ss-[a-z0-9-]+\/SKILL\.md$/.test(name) || /^templates\/(SPEC|PLAN|TASK)\.md$/.test(name);
const sha = data => createHash('sha256').update(data).digest('hex');

async function statOrNull(p) {
  try { return await lstat(p); } catch(e) { if (e.code === 'ENOENT') return null; throw e; }
}
async function assertSafeDirectory(p) {
  const full = resolve(p);
  if (process.platform === 'win32' && full.startsWith('\\\\')) throw new Error('Destino UNC não é aceito.');
  const base = parse(full).root;
  const segments = full.substring(base.length).split(sep).filter(Boolean);
  let next = base;
  for (const segment of segments) {
    next = join(next, segment);
    const st = await statOrNull(next);
    if (st && (!st.isDirectory() || st.isSymbolicLink())) throw new Error(`Caminho inseguro: ${next}`);
  }
  return full;
}
async function readPackage() {
  const raw = JSON.parse(await readFile(join(payload, 'manifest.json'), 'utf8'));
  if (raw.schema !== 1 || !Array.isArray(raw.files) || raw.files.length !== 35) throw new Error('Manifesto inválido ou incompleto.');
  const seen = new Set();
  const entries = [];
  let profiles=0, skills=0, templates=0, total=0;
  for (const entry of raw.files) {
    const name = entry.path;
    if (typeof name !== 'string' || !permitted(name) || seen.has(name.toLowerCase()) || !Number.isSafeInteger(entry.size) || entry.size < 0 || entry.size > LIMIT_BYTES || !/^[a-f0-9]{64}$/.test(entry.sha256)) throw new Error(`Entrada não permitida no manifesto: ${String(name)}`);
    seen.add(name.toLowerCase());
    if(name.startsWith('.codex/')) profiles++;
    if(name.startsWith('.agents/')) skills++;
    if(name.startsWith('templates/')) templates++;
    total += entry.size;
    const src = join(payload, ...name.split('/'));
    const st = await lstat(src);
    if (!st.isFile() || st.isSymbolicLink() || st.size !== entry.size) throw new Error(`Arquivo ausente ou inválido: ${name}`);
    const content = await readFile(src);
    if (sha(content) !== entry.sha256) throw new Error(`Hash do pacote divergente: ${name}`);
    entries.push({ name, content, hash: entry.sha256 });
  }
  if (profiles !== 15 || skills !== 16 || templates !== 3 || !seen.has('agents.md') || total > 8 * 1024 * 1024) throw new Error('Composição inesperada do Starter.');
  return entries.sort((a,b)=>a.name.localeCompare(b.name));
}
async function preflight(dest, files) {
  await assertSafeDirectory(dest);
  const pending=[], identical=[], conflicts=[];
  for(const item of files) {
    const file = join(dest, ...item.name.split('/'));
    await assertSafeDirectory(dirname(file));
    const st=await statOrNull(file);
    if (!st) pending.push(item);
    else if(!st.isFile() || st.isSymbolicLink()) conflicts.push(item.name);
    else {
      const data = await readFile(file);
      if(sha(data) === item.hash) identical.push(item);
      else conflicts.push(item.name);
    }
  }
  return {pending,identical,conflicts};
}
async function ensureDirs(dest, dirs) {
  const base=parse(dest).root;
  const parts=dest.substring(base.length).split(sep).filter(Boolean);
  let path=base;
  for(const part of parts) {
    path=join(path,part);
    const st=await statOrNull(path);
    if (!st) { await mkdir(path); dirs.push(path); }
    else if(!st.isDirectory() || st.isSymbolicLink()) throw new Error(`Diretório inválido: ${path}`);
  }
}
async function install(dest, items) {
  const createdFiles=[], createdDirs=[];
  try {
    await ensureDirs(dest, createdDirs);
    for(const item of items) {
      const target=join(dest, ...item.name.split('/'));
      await ensureDirs(dirname(target), createdDirs);
      const out=await open(target, 'wx', 0o600); // exclusive creation; never overwrite
      createdFiles.push(target);
      try { await out.writeFile(item.content); } finally { await out.close(); }
    }
  } catch (e) {
    for(const f of createdFiles.reverse()) { try { await rm(f); } catch { console.error(`Aviso: não consegui reverter ${f}`); } }
    for(const d of createdDirs.reverse()) { try { await rmdir(d); } catch {} }
    throw e;
  }
}
function usage() {
  console.log('Uso:\n  npx sixteensquad@latest install starter [CAMINHO] [--preview]\n\nSem CAMINHO, instala na pasta atual.\n--preview: exibe o plano sem alterar arquivos.');
}
async function main(argv) {
  if (argv.length === 0 || argv.includes('--help') || argv.includes('-h')) { usage(); return; }
  const [cmd,target,...rest]=argv;
  if(cmd!=='install' || target!=='starter') throw new Error('Comando desconhecido. Use: install starter [CAMINHO] [--preview]');
  const preview=rest.includes('--preview');
  const other=rest.filter(x=>x!=='--preview');
  if(other.length>1 || (other.length===1 && other[0].startsWith('-'))) throw new Error('Parâmetros inválidos.');
  const dest=await assertSafeDirectory(other.length?other[0]:process.cwd());
  const items=await readPackage();
  const {pending,identical,conflicts}=await preflight(dest, items);
  console.log(`SixteenSquad Starter | Destino: ${dest}`);
  console.log(`35 arquivos: ${pending.length} novos, ${identical.length} idênticos, ${conflicts.length} conflitos.`);
  for(const item of pending) console.log(`  + ${item.name}`);
  for(const name of conflicts) console.error(`  ! CONFLITO: ${name}`);
  if (conflicts.length) throw new Error('Conflitos encontrados. Nada foi instalado; compare os arquivos antes de tentar novamente.');
  if (preview) { console.log('Prévia finalizada; nenhuma alteração.'); return; }
  if(!pending.length) { console.log('Starter já está instalado nesta versão.'); return; }
  if(!process.stdin.isTTY) throw new Error('Confirmação interativa requer terminal. Nenhuma alteração.');
  const rl=createInterface({input:process.stdin,output:process.stdout});
  let answer;
  try { answer=await rl.question('Instalar esses arquivos? [s/N] '); } finally { rl.close(); }
  if(!/^(s|sim)$/i.test(answer.trim())) { console.log('Instalação cancelada.'); return; }
  const rechecked=await preflight(dest,items);
  if (rechecked.conflicts.length) throw new Error('Arquivos mudaram antes da cópia; instalação cancelada.');
  await install(dest,rechecked.pending);
  console.log(`Instalação concluída: ${rechecked.pending.length} arquivos. Abra o projeto no Codex.`);
}
main(process.argv.slice(2)).catch(e => { console.error(`SixteenSquad: ${e.message}`); process.exitCode=1; });
