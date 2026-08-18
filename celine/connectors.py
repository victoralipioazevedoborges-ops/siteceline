"""Conectores externos governados do ecossistema CELINE.

Nenhum conector é habilitado automaticamente. Destinos, caminhos e nomes de
variáveis de ambiente são definidos em código; chaves nunca aparecem no estado
público. Identificadores, hosts, caminhos ou payloads relacionados ao Gemini
são recusados antes de qualquer tentativa de rede.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import json
import os
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
)


class ConnectorPolicyError(ValueError):
    """Uma definição ou requisição viola a política de saída da CELINE."""


class ConnectorDisabledError(PermissionError):
    """O conector existe, mas não foi habilitado explicitamente."""


class ConnectorRequestError(RuntimeError):
    """A comunicação externa falhou sem expor corpo ou credencial."""


_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
_ENV_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{1,127}$")
_TRUTHY = frozenset({"1", "true", "yes", "on"})
_BLOCKED_TOKENS = (
    "gemini",
    "google-genai",
    "google.generativeai",
    "generativelanguage.googleapis.com",
)
_BLOCKED_HOSTS = frozenset(
    {
        "generativelanguage.googleapis.com",
        "ai.google.dev",
    }
)


def _contains_blocked_token(value: str) -> bool:
    lowered = value.casefold()
    return any(token in lowered for token in _BLOCKED_TOKENS)


def _is_loopback_host(host: str) -> bool:
    if host.casefold() == "localhost":
        return True
    try:
        from ipaddress import ip_address

        return ip_address(host).is_loopback
    except ValueError:
        return False


def _is_disallowed_literal_host(host: str) -> bool:
    """Recusa IP literal remoto; destinos externos devem ter hostname fixo."""

    try:
        from ipaddress import ip_address

        address = ip_address(host)
    except ValueError:
        return False
    return not address.is_loopback


@dataclass(frozen=True, slots=True)
class ConnectorSpec:
    """Definição imutável de um destino permitido."""

    name: str
    base_url: str
    enabled_env: str
    allowed_path_prefixes: tuple[str, ...]
    secret_env: str | None = None
    auth_header: str = "Authorization"
    auth_prefix: str = "Bearer "
    extra_headers: Mapping[str, str] = field(default_factory=dict)


Transport = Callable[
    [str, str, Mapping[str, str], bytes | None, float, int],
    dict[str, Any],
]


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(  # type: ignore[override]
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def _network_transport(
    url: str,
    method: str,
    headers: Mapping[str, str],
    body: bytes | None,
    timeout: float,
    max_response_bytes: int,
) -> dict[str, Any]:
    request = Request(url, data=body, headers=dict(headers), method=method)
    opener = build_opener(_NoRedirect)
    try:
        with opener.open(request, timeout=timeout) as response:
            status = response.status
            raw = response.read(max_response_bytes + 1)
    except HTTPError as exc:
        raise ConnectorRequestError(
            f"O serviço externo respondeu com HTTP {exc.code}."
        ) from None
    except (URLError, TimeoutError, OSError) as exc:
        raise ConnectorRequestError(
            f"Falha de transporte para o serviço externo: {type(exc).__name__}."
        ) from None

    if len(raw) > max_response_bytes:
        raise ConnectorRequestError("Resposta externa excedeu o limite local.")
    try:
        payload = json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ConnectorRequestError("O serviço externo não devolveu JSON válido.") from None
    return {"status": status, "data": payload}


class ConnectorRegistry:
    """Registro allowlist com habilitação individual e transporte injetável."""

    def __init__(
        self,
        specs: tuple[ConnectorSpec, ...] = (),
        *,
        environment: Mapping[str, str] | None = None,
        transport: Transport | None = None,
        max_request_bytes: int = 65_536,
        max_response_bytes: int = 1_048_576,
    ) -> None:
        self._environment = os.environ if environment is None else environment
        self._transport = transport or _network_transport
        self.max_request_bytes = max_request_bytes
        self.max_response_bytes = max_response_bytes
        self._specs: dict[str, ConnectorSpec] = {}
        for spec in specs:
            self.register(spec)

    @classmethod
    def defaults(
        cls,
        *,
        environment: Mapping[str, str] | None = None,
        transport: Transport | None = None,
    ) -> "ConnectorRegistry":
        return cls(
            (
                ConnectorSpec(
                    name="openai",
                    base_url="https://api.openai.com/v1",
                    enabled_env="CELINE_OPENAI_ENABLED",
                    secret_env="OPENAI_API_KEY",
                    allowed_path_prefixes=("/responses", "/models", "/embeddings"),
                ),
                ConnectorSpec(
                    name="anthropic",
                    base_url="https://api.anthropic.com/v1",
                    enabled_env="CELINE_ANTHROPIC_ENABLED",
                    secret_env="ANTHROPIC_API_KEY",
                    auth_header="x-api-key",
                    auth_prefix="",
                    extra_headers={"anthropic-version": "2023-06-01"},
                    allowed_path_prefixes=("/messages", "/models"),
                ),
                ConnectorSpec(
                    name="github",
                    base_url="https://api.github.com",
                    enabled_env="CELINE_GITHUB_ENABLED",
                    secret_env="GITHUB_TOKEN",
                    extra_headers={"X-GitHub-Api-Version": "2022-11-28"},
                    allowed_path_prefixes=("/repos/", "/user"),
                ),
                ConnectorSpec(
                    name="google_drive",
                    base_url="https://www.googleapis.com/drive/v3",
                    enabled_env="CELINE_GOOGLE_DRIVE_ENABLED",
                    secret_env="GOOGLE_DRIVE_ACCESS_TOKEN",
                    allowed_path_prefixes=("/files", "/about", "/changes"),
                ),
                ConnectorSpec(
                    name="ollama",
                    base_url="http://127.0.0.1:11434/api",
                    enabled_env="CELINE_OLLAMA_ENABLED",
                    allowed_path_prefixes=("/generate", "/chat", "/tags", "/embed"),
                ),
            ),
            environment=environment,
            transport=transport,
        )

    @staticmethod
    def _validate_spec(spec: ConnectorSpec) -> None:
        if not _NAME_PATTERN.fullmatch(spec.name):
            raise ConnectorPolicyError("Nome de conector inválido.")
        if _contains_blocked_token(f"{spec.name} {spec.base_url}"):
            raise ConnectorPolicyError("Gemini é bloqueado pela política da CELINE.")
        if not _ENV_PATTERN.fullmatch(spec.enabled_env):
            raise ConnectorPolicyError("Variável de habilitação inválida.")
        if spec.secret_env and not _ENV_PATTERN.fullmatch(spec.secret_env):
            raise ConnectorPolicyError("Variável de credencial inválida.")

        parsed = urlsplit(spec.base_url)
        if not parsed.hostname or parsed.scheme not in {"http", "https"}:
            raise ConnectorPolicyError("base_url deve ser uma URL HTTP(S) absoluta.")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ConnectorPolicyError("base_url não pode conter credencial, query ou fragmento.")
        host = parsed.hostname.casefold()
        if host in _BLOCKED_HOSTS or host.endswith(".generativelanguage.googleapis.com"):
            raise ConnectorPolicyError("Host do Gemini bloqueado pela política da CELINE.")
        if parsed.scheme == "http" and not _is_loopback_host(host):
            raise ConnectorPolicyError("Serviços remotos exigem HTTPS.")
        if _is_disallowed_literal_host(host):
            raise ConnectorPolicyError("IP literal remoto não é permitido.")
        if host.endswith((".local", ".internal", ".localhost")):
            raise ConnectorPolicyError("Hostname interno não é permitido.")
        if ".." in parsed.path.split("/"):
            raise ConnectorPolicyError("base_url contém travessia de caminho.")

        if not spec.allowed_path_prefixes:
            raise ConnectorPolicyError("Todo conector exige caminhos permitidos.")
        for prefix in spec.allowed_path_prefixes:
            if (
                not prefix.startswith("/")
                or prefix.startswith("//")
                or "?" in prefix
                or "#" in prefix
                or ".." in prefix.split("/")
                or _contains_blocked_token(prefix)
            ):
                raise ConnectorPolicyError("Prefixo de caminho inválido ou bloqueado.")
        for header, value in {
            spec.auth_header: spec.auth_prefix,
            **dict(spec.extra_headers),
        }.items():
            if not header or "\n" in header or "\r" in header:
                raise ConnectorPolicyError("Nome de cabeçalho inválido.")
            if "\n" in value or "\r" in value:
                raise ConnectorPolicyError("Valor de cabeçalho inválido.")

    def register(self, spec: ConnectorSpec) -> None:
        self._validate_spec(spec)
        if spec.name in self._specs:
            raise ConnectorPolicyError(f"Conector já registrado: {spec.name}.")
        self._specs[spec.name] = spec

    def status(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for name in sorted(self._specs):
            spec = self._specs[name]
            enabled = self._environment.get(spec.enabled_env, "").casefold() in _TRUTHY
            configured = not spec.secret_env or bool(self._environment.get(spec.secret_env))
            result.append(
                {
                    "name": name,
                    "base_url": spec.base_url,
                    "enabled": enabled,
                    "configured": configured,
                    "ready": enabled and configured,
                    "enabled_env": spec.enabled_env,
                    "secret_env": spec.secret_env,
                }
            )
        return result

    def any_enabled(self) -> bool:
        return any(item["enabled"] for item in self.status())

    def request_json(
        self,
        name: str,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
        *,
        timeout: float = 15.0,
    ) -> dict[str, Any]:
        spec = self._specs.get(name)
        if spec is None:
            raise ConnectorPolicyError("Conector não registrado.")
        if self._environment.get(spec.enabled_env, "").casefold() not in _TRUTHY:
            raise ConnectorDisabledError(
                f"Habilite {name} explicitamente por {spec.enabled_env}."
            )
        if _contains_blocked_token(f"{name} {path}"):
            raise ConnectorPolicyError("Gemini é bloqueado pela política da CELINE.")
        if (
            not path.startswith("/")
            or path.startswith("//")
            or "?" in path
            or "#" in path
            or ".." in path.split("/")
        ):
            raise ConnectorPolicyError("Caminho externo inválido.")
        def path_matches(prefix: str) -> bool:
            if prefix.endswith("/"):
                return path.startswith(prefix)
            return path == prefix or path.startswith(prefix + "/")

        if not any(path_matches(prefix) for prefix in spec.allowed_path_prefixes):
            raise ConnectorPolicyError("Caminho não incluído na allowlist do conector.")

        method = method.upper()
        if method not in {"GET", "POST"}:
            raise ConnectorPolicyError("Somente GET e POST são permitidos.")
        if timeout <= 0 or timeout > 30:
            raise ConnectorPolicyError("Timeout deve estar entre 0 e 30 segundos.")

        body: bytes | None = None
        if payload is not None:
            serialized = json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            if _contains_blocked_token(serialized):
                raise ConnectorPolicyError("Payload relacionado ao Gemini foi bloqueado.")
            body = serialized.encode("utf-8")
            if len(body) > self.max_request_bytes:
                raise ConnectorPolicyError("Payload externo excedeu o limite local.")
        if method == "GET" and body is not None:
            raise ConnectorPolicyError("GET não aceita payload neste adaptador.")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "CELINE/0.2",
            **dict(spec.extra_headers),
        }
        if spec.secret_env:
            secret = self._environment.get(spec.secret_env)
            if not secret:
                raise ConnectorDisabledError(
                    f"Credencial ausente na variável {spec.secret_env}."
                )
            headers[spec.auth_header] = f"{spec.auth_prefix}{secret}"

        url = spec.base_url.rstrip("/") + path
        return self._transport(
            url,
            method,
            headers,
            body,
            timeout,
            self.max_response_bytes,
        )
