from io import BytesIO
import io
import json
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
import unittest
import zipfile

from celine.documents import DocumentInspector


class DocumentInspectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inspector = DocumentInspector()

    def test_reads_tgz_json_in_memory(self) -> None:
        stream = BytesIO()
        content = json.dumps({"texto": "coeso em português"}).encode()
        with tarfile.open(fileobj=stream, mode="w:gz") as archive:
            info = tarfile.TarInfo("pasta/texto.json")
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
        result = self.inspector.inspect("documentos.tgz", stream.getvalue())
        self.assertEqual(result["documents"][0]["content"]["texto"], "coeso em português")

    def test_rejects_archive_path_traversal(self) -> None:
        stream = BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("../fora.json", "{}")
        with self.assertRaisesRegex(ValueError, "caminho inseguro"):
            self.inspector.inspect("documentos.zip", stream.getvalue())

    def test_reads_python_source_as_text(self) -> None:
        result = self.inspector.inspect("modulo.py", b"def resposta():\n    return 42\n")
        artifact = result["artifacts"][0]
        self.assertEqual(artifact["kind"], "text")
        self.assertIn("def resposta", artifact["text"])

    def test_inspects_dll_as_binary_without_executing_it(self) -> None:
        result = self.inspector.inspect("biblioteca.dll", b"MZ\x00\x01binario")
        artifact = result["artifacts"][0]
        self.assertEqual(artifact["kind"], "binary")
        self.assertTrue(artifact["portable_executable"])
        self.assertEqual(result["execution"], "never")

    def test_inspect_path_expands_home_and_reads_existing_file(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "dados.json"
            path.write_text('{"ok": true}', encoding="utf-8")
            result = self.inspector.inspect_path(path)
        self.assertTrue(result["documents"][0]["content"]["ok"])

    def test_inspect_path_explains_missing_placeholder_file(self) -> None:
        with self.assertRaisesRegex(ValueError, "caminho real"):
            self.inspector.inspect_path("documentos.tgz")


if __name__ == "__main__":
    unittest.main()
