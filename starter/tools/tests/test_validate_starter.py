"""Regressões com dados sintéticos; nenhuma consulta UNC ou credencial real."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

MODULE = Path(__file__).absolute().parents[1] / "validate_starter.py"
SPEC = importlib.util.spec_from_file_location("validate_starter", MODULE)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class StarterTests(unittest.TestCase):
    def setUp(self):
        # Dentro do escopo autorizado; alguns sandboxes Windows bloqueiam TEMP.
        self.temp = tempfile.TemporaryDirectory(prefix="ss-validator-", dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "starter"
        self.root.mkdir()
        self.outside = Path(self.temp.name) / "outside"
        self.outside.mkdir()
        self.sentinel = self.outside / "sentinel.md"
        self.sentinel.write_text("OUTSIDE_MUST_NOT_BE_READ", encoding="utf-8")
        table = ["# Coordenador", "| Papel | Especialidade | Perfil nativo | Skill principal |",
                 "|---|---|---|---|"]
        for number in range(1, 17):
            role, skill = f"AG-{number:02}", f"ss-test-{number:02}"
            name = f"ag{number:02}_test"
            profile = "Sessão principal" if number == 1 else f"`{name}`"
            table.append(f"| {role} | Teste | {profile} | [$test](.agents/skills/{skill}/SKILL.md) |")
            self.write(f".agents/skills/{skill}/SKILL.md", self.skill(skill))
            if number > 1:
                self.write(f".codex/agents/{name}.toml", self.profile(number))
        self.write("AGENTS.md", "\n".join(table))
        self.write("README.md", "# Guia\n[Coordenador](AGENTS.md)\n")
        for template in ("SPEC", "PLAN", "TASK"):
            self.write(f"templates/{template}.md", f"# {template}\n")

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def profile(self, number=2, **overrides):
        values = {"name": f"ag{number:02}_test", "description": "Acionar para revisão sintética.",
                  "developer_instructions": f"AG-{number:02}: ler .agents/skills/ss-test-{number:02}/SKILL.md"}
        values.update(overrides)
        # Valores JSON usados aqui também são TOML válidos para estes testes.
        return "\n".join(f"{key} = {json.dumps(value)}" for key, value in values.items()) + "\n"

    def skill(self, name="ss-test-02", description="Revisar dados sintéticos."):
        return (f"---\nname: {json.dumps(name)}\ndescription: {json.dumps(description)}\n---\n"
                "## Entradas\nDados.\n## Procedimento\n1. Ler.\n2. Conferir.\n3. Relatar.\n"
                "## Saída e conclusão\nResultado.\n## Limites e referências\nSomente sintéticos.\n")

    def result(self):
        result = validator.validate(self.root)
        self.assertEqual(json.loads(json.dumps(result)), result)
        return result

    def assertValid(self):
        result = self.result()
        self.assertTrue(result["ok"], result["errors"])
        return result

    def assertInvalid(self, expected):
        result = self.result()
        self.assertFalse(result["ok"])
        self.assertIn(expected, "\n".join(result["errors"]))
        return result

    def test_valid_starter(self):
        result = self.assertValid()
        self.assertEqual((result["profiles"], result["skills"]), (15, 16))

    def test_invalid_toml(self):
        self.write(".codex/agents/ag02_test.toml", 'name = "unterminated')
        self.assertInvalid("TOML inválido")

    def test_required_toml_types(self):
        for key in validator.REQUIRED:
            for value in ([], ["item"], 42, False):
                with self.subTest(key=key, value=value):
                    self.write(".codex/agents/ag02_test.toml", self.profile(**{key: value}))
                    self.assertInvalid(f"{key} vazio ou não textual")

    def test_toml_table_instead_of_name(self):
        self.write(".codex/agents/ag02_test.toml", '[name]\nvalue = "x"\n')
        self.assertInvalid("name vazio ou não textual")

    def test_missing_required_field(self):
        self.write(".codex/agents/ag02_test.toml", self.profile().replace('name = "ag02_test"\n', ""))
        self.assertInvalid("name vazio ou não textual")

    def test_optional_model_and_effort(self):
        self.write(".codex/agents/ag15_test.toml", self.profile(15, model="gpt-6-luna", model_reasoning_effort="high"))
        self.assertValid()

    def test_other_optional_native_field(self):
        self.write(".codex/agents/ag02_test.toml", self.profile(model_reasoning_summary="auto"))
        self.assertValid()

    def test_optional_fields_wrong_types(self):
        for key in ("model", "model_reasoning_effort"):
            for value in ([], 10, ""):
                with self.subTest(key=key, value=value):
                    self.write(".codex/agents/ag02_test.toml", self.profile(**{key: value}))
                    self.assertInvalid(f"{key} deve ser texto")

    def test_existing_but_wrong_principal_skill(self):
        self.write(".codex/agents/ag02_test.toml", self.profile().replace("ss-test-02", "ss-test-03"))
        self.assertInvalid("associação principal diverge")

    def test_missing_principal_skill(self):
        (self.root / ".agents/skills/ss-test-02/SKILL.md").unlink()
        self.assertInvalid("Papel sem skill principal válida")

    def test_wrong_table_role(self):
        path = self.root / "AGENTS.md"
        self.write("AGENTS.md", path.read_text(encoding="utf-8").replace("`ag02_test`", "`ag03_test`"))
        self.assertInvalid("AG-02: perfil incorreto")

    def test_yaml_description_with_dashes(self):
        self.write(".agents/skills/ss-test-02/SKILL.md", self.skill(description="Antes --- depois: validar."))
        self.assertValid()

    def test_invalid_yaml_quotes(self):
        self.write(".agents/skills/ss-test-02/SKILL.md", self.skill().replace('name: "ss-test-02"', 'name: "aberto'))
        self.assertInvalid("string YAML/JSON inválida")

    def test_yaml_wrong_types(self):
        for field in ("name", "description"):
            for value in ([], {}, 1, None, False):
                with self.subTest(field=field, value=value):
                    self.write(".agents/skills/ss-test-02/SKILL.md", self.skill(**{field: value}))
                    self.assertInvalid("valor YAML deve ser string")

    def test_yaml_duplicate_key(self):
        self.write(".agents/skills/ss-test-02/SKILL.md", self.skill().replace('name: "ss-test-02"', 'name: "ss-test-02"\nname: "ss-test-02"'))
        self.assertInvalid("chave YAML duplicada")

    def test_missing_front_matter_end(self):
        self.write(".agents/skills/ss-test-02/SKILL.md", self.skill().replace("\n---\n", "\n--\n"))
        self.assertInvalid("front matter ausente/incompleto")

    def test_inline_links_titles_and_parentheses(self):
        self.write("guide (new).md", "# Guia\n")
        self.write("README.md", '[a](AGENTS.md "Título")\n[b](<guide (new).md> "Guia")\n[c](guide%20(new).md)\n')
        self.assertValid()

    def test_reference_links(self):
        self.write("README.md", '[a][GUia]\n[guia][]\n[guia]\n[guia]: AGENTS.md "Título"\n')
        result = self.assertValid()
        self.assertEqual(result["local_links"], 19)

    def test_missing_reference(self):
        self.write("README.md", "[a][indefinido]\n")
        self.assertInvalid("referência Markdown indefinida")

    def test_reference_missing_file(self):
        self.write("README.md", "[a][ref]\n[ref]: missing.md\n")
        self.assertInvalid("link inexistente")

    def test_missing_inline_file(self):
        self.write("README.md", "[a](missing.md)\n")
        self.assertInvalid("link inexistente")

    def test_nested_link_label(self):
        self.write("README.md", "[a [b]](missing.md)\n")
        self.assertInvalid("link inexistente")

    def test_link_inside_literal_brackets(self):
        self.write("README.md", "[Consulte [guia](AGENTS.md).]\n")
        self.assertValid()
        self.write("README.md", "[Consulte [guia](missing.md).]\n")
        self.assertInvalid("link inexistente")

    def test_code_in_heading_anchor(self):
        self.write("README.md", "# Usar `Codex`\n[a](#usar-codex)\n")
        self.assertValid()

    def test_code_examples_not_links(self):
        self.write("README.md", '`[a](missing.md)`\n```md\n[a](missing.md)\n```\n    [a](missing.md)\n<!-- [a](missing.md) -->\n')
        self.assertValid()

    def test_network_urls_ignored_without_queries(self):
        self.write("README.md", '[e](https://example.invalid/a) [m](mailto:test@example.invalid) [t](tel:123)\n')
        with patch("socket.getaddrinfo", side_effect=AssertionError("network forbidden")):
            self.assertValid()

    def test_anchor_and_query(self):
        self.write("README.md", "# Guia\n[local](#guia) [outro](AGENTS.md?x=1#coordenador)\n")
        self.assertValid()

    def test_missing_anchor(self):
        self.write("README.md", "[a](AGENTS.md#nao-existe)\n")
        self.assertInvalid("âncora inexistente")

    def test_encoded_filename(self):
        self.write("a b#c.md", "# Guia\n")
        self.write("README.md", "[a](a%20b%23c.md)\n")
        self.assertValid()

    def test_parent_relative_within_root(self):
        self.write("templates/SPEC.md", "[a](../AGENTS.md)\n")
        self.assertValid()

    def test_unsafe_links_never_trigger_filesystem_queries(self):
        # Congela um inventário sintético; depois toda operação de IO é proibida.
        errors = []
        entries, texts = validator.inventory(self.root, errors)
        self.assertEqual(errors, [])
        unsafe = ("../outside/sentinel.md", "%2e%2e/outside/sentinel.md", "/outside/sentinel.md",
                  "C:/outside/sentinel.md", "C:outside.md", "//invalid-server/share/file.md",
                  r"\\invalid-server\share\file.md", "file:///C:/outside/sentinel.md",
                  "%5c%5cinvalid-server/share/file.md", "../outside/missing.md",
                  "%2e%2e%5coutside%5csentinel.md", "safe.md:stream", "NUL", "a/../../outside")
        for target in unsafe:
            with self.subTest(target=target):
                candidate = dict(texts, **{"README.md": f"[x]({target})\n"})
                with patch.object(validator, "inventory", return_value=(entries, candidate)), \
                        patch.object(Path, "exists", side_effect=AssertionError("exists forbidden")), \
                        patch.object(Path, "resolve", side_effect=AssertionError("resolve forbidden")), \
                        patch("os.stat", side_effect=AssertionError("stat forbidden")), \
                        patch("os.lstat", side_effect=AssertionError("lstat forbidden")), \
                        patch("os.open", side_effect=AssertionError("open forbidden")), \
                        patch("builtins.open", side_effect=AssertionError("read forbidden")), \
                        patch.object(validator, "open_checked", side_effect=AssertionError("native open forbidden")):
                    self.assertInvalid("link recusado")

    def test_unc_root_rejected_before_open(self):
        with patch.object(validator, "open_checked", side_effect=AssertionError("UNC queried")):
            result = validator.validate(r"\\invalid-server\share\starter")
        self.assertFalse(result["ok"])
        self.assertIn("UNC", "\n".join(result["errors"]))

    def assertExternalUnread(self, expected):
        # Detectar leitura pelo descritor do sentinela, mesmo através de um link.
        outside_id = os.stat(self.sentinel)
        actual_fdopen = os.fdopen
        def guarded(fd, *args, **kwargs):
            info = os.fstat(fd)
            if (info.st_dev, info.st_ino) == (outside_id.st_dev, outside_id.st_ino):
                os.close(fd)
                self.fail("tentativa de ler o sentinela externo")
            return actual_fdopen(fd, *args, **kwargs)
        with patch("os.fdopen", side_effect=guarded):
            result = self.assertInvalid(expected)
        self.assertNotIn("OUTSIDE_MUST_NOT_BE_READ", json.dumps(result))

    def make_symlink(self, target, link, directory=False):
        try:
            os.symlink(target, link, target_is_directory=directory)
        except OSError as exc:
            if getattr(exc, "winerror", None) in (5, 1314):
                self.skipTest(f"ambiente bloqueia symlink sintético: WinError {exc.winerror}")
            raise

    def test_external_file_symlink_not_read(self):
        self.make_symlink(self.sentinel, self.root / "linked.md")
        self.assertExternalUnread("linked.md: leitura recusada")

    def test_external_directory_symlink_not_traversed(self):
        self.make_symlink(self.outside, self.root / "linked", directory=True)
        self.assertExternalUnread("linked: leitura recusada")

    @unittest.skipUnless(os.name == "nt", "junction é específica de Windows")
    def test_external_junction_not_traversed(self):
        import _winapi
        link = self.root / "junction"
        try:
            _winapi.CreateJunction(str(self.outside), str(link))
        except PermissionError as exc:
            self.skipTest(f"ambiente bloqueia junction sintética: WinError {exc.winerror}")
        self.addCleanup(lambda: os.rmdir(link))
        self.assertExternalUnread("junction: leitura recusada")

    def test_hard_link_not_read(self):
        try:
            os.link(self.sentinel, self.root / "linked.md")
        except PermissionError as exc:
            self.skipTest(f"ambiente bloqueia hard link sintético: {exc}")
        self.assertExternalUnread("hard links recusado")

    def test_reparse_attribute_rejected_before_read_or_listing(self):
        # Simula o atributo devolvido pelo SO, não a decisão do validador.
        real_fstat = os.fstat
        for relative in ("README.md", "templates"):
            target = os.stat(self.root / relative)
            forbidden = (target.st_dev, target.st_ino)
            def marked(fd):
                info = real_fstat(fd)
                if (info.st_dev, info.st_ino) == forbidden:
                    return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400)
                return info
            real_fdopen, real_listdir = os.fdopen, os.listdir
            def no_read(fd, *args, **kwargs):
                info = real_fstat(fd)
                self.assertNotEqual((info.st_dev, info.st_ino), forbidden)
                return real_fdopen(fd, *args, **kwargs)
            def no_list(path):
                if isinstance(path, int):
                    info = real_fstat(path)
                    self.assertNotEqual((info.st_dev, info.st_ino), forbidden)
                else:
                    self.assertNotEqual(Path(path), self.root / relative)
                return real_listdir(path)
            with self.subTest(relative=relative), patch("os.fstat", side_effect=marked), \
                    patch("os.fdopen", side_effect=no_read), patch("os.listdir", side_effect=no_list):
                self.assertInvalid(f"{relative}: leitura recusada")

    def test_hardlink_count_rejected_before_read(self):
        target = os.stat(self.root / "README.md")
        real_fstat, real_fdopen = os.fstat, os.fdopen
        def marked(fd):
            info = real_fstat(fd)
            if (info.st_dev, info.st_ino) == (target.st_dev, target.st_ino):
                return SimpleNamespace(st_mode=info.st_mode, st_nlink=2)
            return info
        def no_read(fd, *args, **kwargs):
            info = real_fstat(fd)
            self.assertNotEqual((info.st_dev, info.st_ino), (target.st_dev, target.st_ino))
            return real_fdopen(fd, *args, **kwargs)
        with patch("os.fstat", side_effect=marked), patch("os.fdopen", side_effect=no_read):
            self.assertInvalid("hard links recusado")

    def test_invalid_utf8_reported(self):
        (self.root / "README.md").write_bytes(b"\xff\xfe")
        self.assertInvalid("leitura recusada")

    def test_read_limit(self):
        with patch.object(validator, "MAX_TEXT_BYTES", 4):
            self.assertInvalid("excede limite")

    def test_json_main_exit_codes(self):
        real_validate = validator.validate
        for valid in (True, False):
            if not valid:
                self.write(".codex/agents/ag02_test.toml", self.profile(name=[]))
                self.write(".agents/skills/ss-test-02/SKILL.md", self.skill(description={}))
            output = io.StringIO()
            with patch.object(validator, "validate", side_effect=lambda: real_validate(self.root)), redirect_stdout(output):
                code = validator.main()
            self.assertEqual(code, 0 if valid else 1)
            report = json.loads(output.getvalue())
            self.assertEqual(report["ok"], valid)
            if not valid:
                self.assertIn("name vazio ou não textual", "\n".join(report["errors"]))
                self.assertIn("valor YAML deve ser string", "\n".join(report["errors"]))


if __name__ == "__main__":
    unittest.main()
