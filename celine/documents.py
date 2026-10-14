"""Inspeção local, passiva e limitada de arquivos e pacotes compactados."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from io import BytesIO
import json
import mimetypes
from pathlib import Path, PurePosixPath
import stat
import tarfile
from typing import Any, Iterable
import zipfile


@dataclass(frozen=True)
class DocumentLimits:
    max_upload_bytes: int = 32 * 1024 * 1024
    max_entries: int = 200
    max_entry_bytes: int = 8 * 1024 * 1024
    max_total_uncompressed_bytes: int = 32 * 1024 * 1024
    max_text_characters: int = 1_000_000


class DocumentInspector:
    """Analisa qualquer arquivo sem executar, carregar ou persistir o conteúdo."""

    archive_extensions = (".zip", ".tgz", ".tar.gz")

    def __init__(self, limits: DocumentLimits | None = None) -> None:
        self.limits = limits or DocumentLimits()

    @staticmethod
    def _safe_name(name: str) -> str:
        normalized = name.replace("\\", "/")
        path = PurePosixPath(normalized)
        if (
            not normalized
            or normalized.startswith("/")
            or ".." in path.parts
            or path.is_absolute()
        ):
            raise ValueError("O arquivo compactado contém caminho inseguro.")
        return str(path)

    @staticmethod
    def _looks_like_text(raw: bytes) -> tuple[bool, str | None]:
        if b"\x00" in raw[:8192]:
            return False, None
        try:
            return True, raw.decode("utf-8")
        except UnicodeDecodeError:
            return False, None

    def _inspect_item(self, raw: bytes, name: str) -> dict[str, Any]:
        """Produz conteúdo textual ou metadados binários, sem executar o item."""

        media_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
        item: dict[str, Any] = {
            "name": name,
            "size_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "media_type": media_type,
        }
        if name.lower().endswith(".json"):
            try:
                item["content"] = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"JSON inválido: {name}.") from exc
            item["kind"] = "json"
            return item

        is_text, text = self._looks_like_text(raw)
        if is_text and text is not None:
            item["kind"] = "text"
            item["text"] = text[: self.limits.max_text_characters]
            item["text_truncated"] = len(text) > self.limits.max_text_characters
            return item

        item["kind"] = "binary"
        item["magic_hex"] = raw[:16].hex()
        item["portable_executable"] = raw.startswith(b"MZ")
        return item

    def _check_members(self, members: Iterable[tuple[str, int]]) -> None:
        total = 0
        count = 0
        for name, size in members:
            self._safe_name(name)
            count += 1
            total += size
            if count > self.limits.max_entries:
                raise ValueError("Arquivo compactado excede o limite de itens.")
            if size < 0 or size > self.limits.max_entry_bytes:
                raise ValueError(f"Item compactado excede o limite: {name}.")
            if total > self.limits.max_total_uncompressed_bytes:
                raise ValueError("Conteúdo descompactado excede o limite total.")

    def _inspect_zip(self, raw: bytes) -> list[dict[str, Any]]:
        try:
            with zipfile.ZipFile(BytesIO(raw)) as archive:
                all_infos = archive.infolist()
                self._check_members(
                    (item.filename, 0 if item.is_dir() else item.file_size)
                    for item in all_infos
                )
                infos = [item for item in all_infos if not item.is_dir()]
                if any(item.flag_bits & 0x1 for item in infos):
                    raise ValueError("Arquivos ZIP criptografados não são aceitos.")
                if any(stat.S_ISLNK(item.external_attr >> 16) for item in infos):
                    raise ValueError("Links simbólicos não são aceitos.")
                return [
                    self._inspect_item(
                        archive.read(item), self._safe_name(item.filename)
                    )
                    for item in infos
                ]
        except (zipfile.BadZipFile, RuntimeError) as exc:
            raise ValueError("Arquivo ZIP inválido.") from exc

    def _inspect_tgz(self, raw: bytes) -> list[dict[str, Any]]:
        try:
            with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as archive:
                members = archive.getmembers()
                if any(not (item.isfile() or item.isdir()) for item in members):
                    raise ValueError("Links e itens especiais não são aceitos.")
                self._check_members(
                    (item.name, item.size if item.isfile() else 0) for item in members
                )
                artifacts = []
                for item in (member for member in members if member.isfile()):
                    name = self._safe_name(item.name)
                    stream = archive.extractfile(item)
                    if stream is None:
                        raise ValueError(f"Não foi possível ler: {name}.")
                    artifacts.append(self._inspect_item(stream.read(), name))
                return artifacts
        except (tarfile.TarError, EOFError) as exc:
            raise ValueError("Arquivo TGZ inválido.") from exc

    def inspect(self, filename: str, raw: bytes) -> dict[str, Any]:
        """Inspeciona qualquer extensão e abre ZIP/TGZ de forma passiva."""

        if len(raw) > self.limits.max_upload_bytes:
            raise ValueError("Upload excede o limite permitido de 32 MiB.")
        safe_filename = PurePosixPath(filename.replace("\\", "/")).name
        if not safe_filename or safe_filename != filename:
            raise ValueError("Nome de arquivo inválido.")
        lowered = safe_filename.lower()
        if lowered.endswith(".zip"):
            artifacts, kind = self._inspect_zip(raw), "zip"
        elif lowered.endswith((".tgz", ".tar.gz")):
            artifacts, kind = self._inspect_tgz(raw), "tgz"
        else:
            artifacts, kind = [self._inspect_item(raw, safe_filename)], "file"
        return {
            "filename": safe_filename,
            "format": kind,
            "artifacts": artifacts,
            # Alias mantido para clientes da primeira versão da rota.
            "documents": artifacts,
            "artifact_count": len(artifacts),
            "document_count": len(artifacts),
            "skipped": [],
            "storage": "memory_only",
            "execution": "never",
        }

    def inspect_path(self, path: str | Path) -> dict[str, Any]:
        """Lê um arquivo local informado explicitamente pelo operador."""

        source = Path(path).expanduser()
        if not source.exists():
            raise ValueError(
                "Arquivo não encontrado. Informe o caminho real do arquivo."
            )
        if not source.is_file():
            raise ValueError("O caminho informado não é um arquivo regular.")
        if source.stat().st_size > self.limits.max_upload_bytes:
            raise ValueError("Arquivo excede o limite permitido de 32 MiB.")
        return self.inspect(source.name, source.read_bytes())
