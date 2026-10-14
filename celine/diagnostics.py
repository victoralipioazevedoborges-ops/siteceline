"""Diagnóstico local e redigido da comunicação com a API CELINE."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from http.client import HTTPConnection
from ipaddress import ip_address
import json
from urllib.parse import urlsplit


@dataclass(frozen=True, slots=True)
class CommunicationDiagnostic:
    """Resultado mínimo, sem payload, credencial ou endereço do usuário."""

    reachable: bool
    http_status: int | None
    celine_status: str | None
    external_network: bool | None
    error: str | None


def _loopback_target(url: str) -> tuple[str, int, str]:
    parsed = urlsplit(url)
    if parsed.scheme != "http" or not parsed.hostname:
        raise ValueError("O diagnóstico aceita somente URL HTTP local absoluta.")
    try:
        loopback = ip_address(parsed.hostname).is_loopback
    except ValueError:
        loopback = parsed.hostname.casefold() == "localhost"
    if not loopback:
        raise ValueError("O diagnóstico é restrito a endereços de loopback.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("A URL de diagnóstico não aceita credencial, query ou fragmento.")
    path = parsed.path or "/health"
    if path != "/health":
        raise ValueError("O diagnóstico consulta exclusivamente a rota /health.")
    return parsed.hostname, parsed.port or 80, path


def diagnose(url: str = "http://127.0.0.1:8787/health", timeout: float = 2.0) -> CommunicationDiagnostic:
    """Consulta somente o health check local e resume a resposta permitida."""

    if timeout <= 0 or timeout > 10:
        raise ValueError("Timeout deve estar entre 0 e 10 segundos.")
    host, port, path = _loopback_target(url)
    connection = HTTPConnection(host, port, timeout=timeout)
    try:
        connection.request("GET", path, headers={"Accept": "application/json"})
        response = connection.getresponse()
        raw = response.read(65_537)
        if len(raw) > 65_536:
            return CommunicationDiagnostic(
                reachable=True,
                http_status=response.status,
                celine_status=None,
                external_network=None,
                error="Resposta local excedeu o limite de diagnóstico.",
            )
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = None
        if not isinstance(payload, dict):
            return CommunicationDiagnostic(
                reachable=True,
                http_status=response.status,
                celine_status=None,
                external_network=None,
                error="Resposta local não contém JSON de saúde válido.",
            )
        status = payload.get("status")
        external_network = payload.get("external_network")
        return CommunicationDiagnostic(
            reachable=True,
            http_status=response.status,
            celine_status=status if isinstance(status, str) else None,
            external_network=(
                external_network if isinstance(external_network, bool) else None
            ),
            error=None,
        )
    except (ConnectionError, OSError, TimeoutError) as exc:
        return CommunicationDiagnostic(
            reachable=False,
            http_status=None,
            celine_status=None,
            external_network=None,
            error=f"API local indisponível: {type(exc).__name__}.",
        )
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verifica a comunicação local com a API CELINE sem acessar a internet."
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8787/health",
        help="URL local /health (padrão: http://127.0.0.1:8787/health)",
    )
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()
    try:
        result = diagnose(args.url, args.timeout)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
