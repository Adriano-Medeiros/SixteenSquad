"""Validação estática, somente leitura, usando Python 3.11+ e biblioteca padrão."""
from contextlib import contextmanager, ExitStack
from pathlib import Path
import html
import json
import os
import re
import stat
import sys
import tomllib
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).absolute().parents[1]
MAX_TEXT_BYTES = 2 * 1024 * 1024
REQUIRED = ("name", "description", "developer_instructions")
LIMITS = ("Validação estática; YAML restrito a name/description com strings JSON; "
          "links Markdown inline/referência e âncoras comuns, não todo CommonMark/HTML; "
          "não prova reconhecimento nativo, comportamento ou ausência de todo segredo.")


def local_path(target, base=""):
    """Normalização lexical: nunca consulta existência nem resolve o caminho."""
    target = target.replace("\\", "/")
    if (target.startswith("/") or ":" in target
            or any(ord(c) < 32 or ord(c) == 127 for c in target)):
        raise ValueError("caminho absoluto, UNC, dispositivo ou caractere proibido")
    parts = base.split("/") if base else []
    for part in target.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                raise ValueError("caminho sai do Starter")
            parts.pop()
            continue
        if (part.endswith((".", " ")) or any(c in part for c in '<>"|?*')
                or re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part)):
            raise ValueError("nome de caminho ambíguo ou reservado")
        parts.append(part)
    return "/".join(parts)


@contextmanager
def open_checked(path, parent_fd=None):
    """Abrir o objeto sem seguir links; pais permanecem abertos no chamador.

    Windows: OPEN_REPARSE_POINT, sem compartilhamento de escrita/exclusão,
    conserva os pais abertos. POSIX: descritor relativo com O_NOFOLLOW.
    Não é sandbox contra administrador ou modificação do próprio validador.
    """
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        import msvcrt
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                           wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)
        create.restype = wintypes.HANDLE
        handle = create(str(path), 0x80000000, 1, None, 3, 0x02200000, None)
        if handle == wintypes.HANDLE(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
        except BaseException:
            close = kernel.CloseHandle
            close.argtypes = (wintypes.HANDLE,)
            close(handle)
            raise
    else:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
    try:
        info = os.fstat(fd)
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("link simbólico/junction/reparse point recusado")
        if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
            raise ValueError("objeto não é arquivo regular nem diretório")
        if stat.S_ISREG(info.st_mode) and info.st_nlink > 1:
            raise ValueError("arquivo com hard links recusado")
        yield fd, info
    finally:
        os.close(fd)


def inventory(root, errors):
    """Snapshot seguro. Links documentais não disparam operações de IO."""
    entries, texts = {}, {}
    root = Path(os.path.abspath(root))  # lexical; não usar resolve()
    if str(root).startswith(("\\\\", "//")):
        errors.append("Raiz UNC/dispositivo recusada")
        return entries, texts

    def visit(path, relative, fd, info):
        if stat.S_ISDIR(info.st_mode):
            entries[relative] = "directory"
            for name in sorted(os.listdir(path if os.name == "nt" else fd)):
                rel = relative + "/" + name if relative else name
                try:
                    if local_path(name) != name:
                        raise ValueError("nome de entrada ambíguo")
                    with open_checked(path / name if os.name == "nt" else name, fd) as child:
                        visit(path / name, rel, *child)
                except (OSError, ValueError, UnicodeError, RecursionError) as exc:
                    errors.append(f"{rel}: leitura recusada: {exc}")
        else:
            entries[relative] = "file"
            if path.suffix.lower() in {".md", ".toml"}:
                with os.fdopen(os.dup(fd), "rb") as stream:
                    data = stream.read(MAX_TEXT_BYTES + 1)
                if len(data) > MAX_TEXT_BYTES:
                    raise ValueError("texto excede limite de 2 MiB")
                texts[relative] = data.decode("utf-8")

    try:
        with ExitStack() as stack:
            fd, info = stack.enter_context(open_checked(root.anchor))
            current = Path(root.anchor)
            for part in root.parts[1:]:
                current /= part
                fd, info = stack.enter_context(open_checked(current if os.name == "nt" else part, fd))
            if not stat.S_ISDIR(info.st_mode):
                raise ValueError("raiz não é diretório")
            visit(root, "", fd, info)
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        errors.append(f"Inventário indisponível: {exc}")
    return entries, texts


def prose(text, inline=True):
    """Excluir exemplos de código e comentários antes de interpretar links."""
    result, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        if not line.startswith(("    ", "\t")):
            result.append(line)
    value = re.sub(r"<!--.*?-->", "", "\n".join(result), flags=re.S)
    return re.sub(r"(`+)(?!`)(.*?)(?<!`)\1(?!`)", "", value, flags=re.S) if inline else value


def destination(value):
    value = value.strip()
    if value.startswith("<"):
        end = value.find(">")
        if end < 0:
            raise ValueError("destino <...> incompleto")
        target, tail = value[1:end], value[end + 1:].strip()
    else:
        match = re.match(r"(?:\\.|[^\s])+", value)
        target = match[0] if match else ""
        tail = value[len(target):].strip()
    if tail and not re.fullmatch(r'"[^"\n]*"|\x27[^\x27\n]*\x27|\([^\n]*\)', tail):
        raise ValueError("destino/título Markdown inválido")
    return html.unescape(re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])", r"\1", target))


def markdown_links(text, errors, source):
    text = prose(text)
    definitions = {}
    normalize = lambda label: " ".join(label.split()).casefold()
    def definition(match):
        try:
            definitions.setdefault(normalize(match[1]), destination(match[2]))
        except ValueError as exc:
            errors.append(f"{source}: {exc}")
        return ""
    text = re.sub(r"^ {0,3}\[([^]\n]+)\]:[ \t]*(.*)$", definition, text, flags=re.M)
    links, cursor = [], 0
    while True:
        match = re.search(r"(?<!\\)\[", text[cursor:])
        if not match:
            break
        start = cursor + match.start()
        depth, end = 1, start + 1
        while end < len(text) and depth:
            if text[end] == "\\":
                end += 2
                continue
            if text[end] == "[":
                depth += 1
            elif text[end] == "]":
                depth -= 1
            end += 1
        if depth:
            break
        label, cursor = text[start + 1:end - 1], start + 1
        if text[end:end + 1] == "(":
            depth, index, quoted = 1, end + 1, None
            while index < len(text) and depth:
                char = text[index]
                if char == "\\":
                    index += 2
                    continue
                if quoted:
                    if char == quoted:
                        quoted = None
                elif char == "<":
                    quoted = ">"
                elif char in "\"'" and (index == end + 1 or text[index - 1].isspace()):
                    quoted = char
                elif char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                index += 1
            if depth:
                errors.append(f"{source}: link Markdown incompleto próximo de {start}")
                continue
            try:
                links.append(destination(text[end + 1:index - 1]))
            except ValueError as exc:
                errors.append(f"{source}: {exc}")
            cursor = index
        elif text[end:end + 1] == "[":
            ref = re.match(r"\[([^]\n]*)\]", text[end:])
            if ref:
                key = normalize(ref[1] or label)
                if key in definitions:
                    links.append(definitions[key])
                else:
                    errors.append(f"{source}: referência Markdown indefinida: {key}")
                cursor = end + len(ref[0])
        elif normalize(label) in definitions:
            links.append(definitions[normalize(label)])
            cursor = end
    return links


def anchors(text):
    text = prose(text, inline=False)
    found = set(re.findall(r'\b(?:id|name)=["\x27]([^"\x27]+)["\x27]', text))
    titles = re.findall(r"^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", text, re.M)
    titles += re.findall(r"^([^\n]+)\n {0,3}(?:=+|-+)[ \t]*$", text, re.M)
    for title in titles:
        title = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", title)
        slug = re.sub(r"[^\w\- ]", "", html.unescape(title).lower()).replace(" ", "-")
        unique, number = slug, 0
        while unique in found:
            number += 1
            unique = f"{slug}-{number}"
        found.add(unique)
    return found


def validate(root=ROOT):
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
        return condition
    entries, texts = inventory(root, errors)
    profiles = sorted(p for p in texts if re.fullmatch(r"\.codex/agents/[^/]+\.toml", p))
    skills = sorted(p for p in texts if re.fullmatch(r"\.agents/skills/[^/]+/SKILL\.md", p))
    check(len(profiles) == 15, f"Esperados 15 perfis; encontrados {len(profiles)}")
    check(len(skills) >= 16, f"Esperadas ao menos 16 skills; encontradas {len(skills)}")

    # A tabela existente é canônica; não duplicar o catálogo no código.
    roles, associations = {}, {}
    for row in texts.get("AGENTS.md", "").splitlines():
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if not cells or not re.fullmatch(r"AG-\d{2}", cells[0]):
            continue
        if not check(len(cells) == 4, f"{cells[0]}: linha da tabela inválida"):
            continue
        role, _, profile, skill_cell = cells
        refs = re.findall(r"\(\.agents/skills/([a-z0-9-]+)/SKILL\.md\)", skill_cell)
        if not check(len(refs) == 1, f"{role}: skill principal ambígua/ausente na tabela"):
            continue
        check(role not in roles, f"{role}: papel duplicado na tabela")
        roles[role] = refs[0]
        if role == "AG-01":
            check(profile == "Sessão principal", "AG-01 deve ser a sessão principal")
        else:
            profile = profile.strip("`")
            check(re.fullmatch(r"ag" + role[3:] + r"_[a-z0-9_]+", profile), f"{role}: perfil incorreto na tabela")
            check(profile not in associations, f"{role}: perfil duplicado na tabela")
            associations[profile] = refs[0]
    check(set(roles) == {f"AG-{n:02}" for n in range(1, 17)}, "Tabela deve cobrir AG-01 a AG-16")

    names = set()
    for path in profiles:
        try:
            data = tomllib.loads(texts[path])
        except (ValueError, RecursionError) as exc:
            errors.append(f"{path}: TOML inválido: {exc}")
            continue
        valid = True
        for key in REQUIRED:
            valid &= check(isinstance(data.get(key), str) and bool(data[key].strip()),
                           f"{path}: {key} vazio ou não textual")
        # Aceitar campos opcionais nativos; não espelhar todo o schema mutável.
        for key in ("model", "model_reasoning_effort"):
            if key in data:
                check(isinstance(data[key], str) and bool(data[key].strip()), f"{path}: {key} deve ser texto não vazio")
        if not valid:
            continue
        name = data["name"]
        check(name == Path(path).stem, f"{path}: nome diverge do arquivo")
        check(name not in names, f"{path}: nome duplicado")
        names.add(name)
        refs = re.findall(r"\.agents/skills/([a-z0-9-]+)/SKILL\.md", data["developer_instructions"])
        check(name in associations and refs == [associations.get(name)],
              f"{path}: associação principal diverge da tabela AGENTE → SKILL")
        check("AG-" + name[2:4] in data["developer_instructions"], f"{path}: papel não identificado")
    check(names == set(associations), "Perfis devem corresponder aos 15 especialistas da tabela")

    skill_names = set()
    for path in skills:
        rows = texts[path].splitlines()
        if not check(bool(rows) and rows[0] == "---" and "---" in rows[1:], f"{path}: front matter ausente/incompleto"):
            continue
        end = rows.index("---", 1)
        metadata = {}
        for row in rows[1:end]:
            key, sep, value = row.partition(":")
            check(sep and key in {"name", "description"}, f"{path}: chave YAML inválida")
            check(key not in metadata, f"{path}: chave YAML duplicada")
            try:
                parsed = json.loads(value.strip())
                if check(isinstance(parsed, str) and bool(parsed.strip()), f"{path}: valor YAML deve ser string não vazia"):
                    metadata[key] = parsed
            except (ValueError, RecursionError) as exc:
                errors.append(f"{path}: string YAML/JSON inválida: {exc}")
        check(set(metadata) == {"name", "description"}, f"{path}: metadados incompletos")
        name = metadata.get("name", "")
        check(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) and len(name) <= 64, f"{path}: nome inválido")
        check(name == Path(path).parent.name, f"{path}: nome diverge da pasta")
        check(name not in skill_names, f"{path}: nome duplicado")
        skill_names.add(name)
        check(len(metadata.get("description", "")) <= 1024, f"{path}: descrição inválida")
        body = "\n".join(rows[end + 1:])
        for heading in ("## Entradas", "## Procedimento", "## Saída e conclusão", "## Limites e referências"):
            check(heading in body, f"{path}: contrato sem {heading}")
        check(len(re.findall(r"^\d+\. ", body, re.M)) >= 3, f"{path}: procedimento insuficiente")
    check(set(roles.values()) <= skill_names, "Papel sem skill principal válida")
    for filename in ("AGENTS.md", "README.md", "templates/SPEC.md", "templates/PLAN.md", "templates/TASK.md"):
        check(filename in texts, f"Arquivo obrigatório ausente/ilegível: {filename}")

    link_count = 0
    for source, content in texts.items():
        if not source.lower().endswith(".md"):
            continue
        for target in markdown_links(content, errors, source):
            try:
                if any(ord(c) < 32 or ord(c) == 127 for c in target):
                    raise ValueError("caractere de controle no link")
                url = urlsplit(target)
                if url.scheme.lower() in {"http", "https", "mailto", "tel"}:
                    continue
                if url.scheme or url.netloc:
                    raise ValueError("esquema/UNC/caminho absoluto proibido")
                link_count += 1
                decoded = unquote(url.path, errors="strict")
                rel = local_path(decoded, source.rpartition("/")[0]) if decoded else source
                check(rel in entries, f"{source}: link inexistente: {target}")
                if url.fragment:
                    if rel.lower().endswith(".md") and rel in texts:
                        check(unquote(url.fragment, errors="strict") in anchors(texts[rel]), f"{source}: âncora inexistente: {target}")
                    else:
                        errors.append(f"{source}: âncora não verificável em alvo não Markdown: {target}")
            except (ValueError, UnicodeError) as exc:
                errors.append(f"{source}: link recusado {target!r}: {exc}")
    check(".codex/config.toml" not in entries, "Configuração de sessão não faz parte desta base")
    sensitive = re.compile(r"(?:sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
    for path, content in texts.items():
        check(not sensitive.search(content), f"{path}: padrão de credencial")
    return {"ok": not errors, "profiles": len(profiles), "skills": len(skills),
            "local_links": link_count, "errors": errors, "limits": LIMITS}


def main():
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
