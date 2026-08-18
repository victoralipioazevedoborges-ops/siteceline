"""API HTTP local do ecossistema CELINE, sem dependências externas."""

from __future__ import annotations

import argparse
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .ecosystem import CelineEcosystem


class CelineRequestHandler(BaseHTTPRequestHandler):
    server_version = "CELINE/0.2"
    protocol_version = "HTTP/1.1"

    def __init__(self, *args: Any, ecosystem: CelineEcosystem, **kwargs: Any) -> None:
        self.ecosystem = ecosystem
        super().__init__(*args, **kwargs)

    def log_message(self, _format: str, *args: Any) -> None:
        self.ecosystem.pattern_guard.record(
            "http_log", "recorded", {"client": self.client_address[0]}
        )

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(raw)

    def _authorize(self) -> bool:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send(HTTPStatus.BAD_REQUEST, {"error": "Content-Length inválido."})
            return False
        allowed, reason = self.ecosystem.pattern_guard.authorize(
            client_ip=self.client_address[0],
            method=self.command,
            path=urlparse(self.path).path,
            content_length=content_length,
        )
        if not allowed:
            status = (
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE
                if "limite" in reason.lower() and "corpo" in reason.lower()
                else HTTPStatus.TOO_MANY_REQUESTS
                if "requisições" in reason.lower()
                else HTTPStatus.FORBIDDEN
            )
            self._send(status, {"error": reason})
        return allowed

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("JSON inválido.") from exc
        if not isinstance(data, dict):
            raise ValueError("O corpo JSON deve ser um objeto.")
        return data

    def do_GET(self) -> None:  # noqa: N802
        if not self._authorize():
            return
        path = urlparse(self.path).path
        if path == "/health":
            self._send(HTTPStatus.OK, self.ecosystem.health())
        elif path == "/modules":
            self._send(HTTPStatus.OK, {"modules": self.ecosystem.modules()})
        elif path == "/mesh":
            self._send(HTTPStatus.OK, self.ecosystem.mesh.to_dict())
        elif path == "/audit":
            self._send(
                HTTPStatus.OK,
                {"events": self.ecosystem.pattern_guard.recent(100)},
            )
        elif path == "/connectors":
            self._send(
                HTTPStatus.OK,
                {
                    "policy": "explicit_opt_in",
                    "automatic_forwarding": False,
                    "gemini": "blocked",
                    "connectors": self.ecosystem.connector_status(),
                },
            )
        else:
            self._send(HTTPStatus.NOT_FOUND, {"error": "Rota não encontrada."})

    def do_POST(self) -> None:  # noqa: N802
        if not self._authorize():
            return
        path = urlparse(self.path).path
        try:
            body = self._read_json()
            if path == "/luma":
                text = next(
                    (
                        body[key]
                        for key in ("prompt", "objetivo", "message", "command")
                        if isinstance(body.get(key), str)
                    ),
                    "",
                )
                self._send(HTTPStatus.OK, self.ecosystem.analyze(text))
            elif path == "/zion/route":
                payload = body.get("payload", body.get("message", ""))
                if not isinstance(payload, str):
                    raise ValueError("payload deve ser texto.")
                self._send(HTTPStatus.OK, self.ecosystem.route(payload))
            elif path == "/arcana/challenge":
                self._send(
                    HTTPStatus.CREATED,
                    self.ecosystem.issue_arcana_challenge(),
                )
            elif path == "/arcana/verify":
                session_id = body.get("session_id")
                response = body.get("response")
                if not isinstance(session_id, str) or not isinstance(response, str):
                    raise ValueError("session_id e response são obrigatórios.")
                valid = self.ecosystem.verify_arcana(session_id, response)
                self._send(
                    HTTPStatus.OK if valid else HTTPStatus.UNAUTHORIZED,
                    {"valid": valid},
                )
            elif path == "/teazer/session":
                self._send(
                    HTTPStatus.CREATED,
                    self.ecosystem.open_teazer_session(),
                )
            else:
                self._send(HTTPStatus.NOT_FOUND, {"error": "Rota não encontrada."})
        except ValueError as exc:
            self._send(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception:
            self.ecosystem.pattern_guard.record("request_error", "internal", {})
            self._send(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Erro interno."})

    def do_DELETE(self) -> None:  # noqa: N802
        if not self._authorize():
            return
        path = urlparse(self.path).path
        prefix = "/teazer/session/"
        if path.startswith(prefix):
            session_id = path[len(prefix) :]
            closed = self.ecosystem.close_teazer_session(session_id)
            self._send(
                HTTPStatus.OK if closed else HTTPStatus.NOT_FOUND,
                {"closed": closed},
            )
        else:
            self._send(HTTPStatus.NOT_FOUND, {"error": "Rota não encontrada."})


def build_server(
    host: str = "127.0.0.1",
    port: int = 8787,
    *,
    ecosystem: CelineEcosystem | None = None,
    allow_remote: bool = False,
) -> ThreadingHTTPServer:
    if not ip_address(host).is_loopback and not allow_remote:
        raise ValueError("Host remoto exige --allow-remote explícito.")
    active_ecosystem = ecosystem or CelineEcosystem(
        audit_path=Path("runtime") / "pattern_guard.jsonl"
    )
    handler = partial(CelineRequestHandler, ecosystem=active_ecosystem)
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="API local do ecossistema CELINE")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8787, type=int)
    parser.add_argument("--allow-remote", action="store_true")
    args = parser.parse_args()
    server = build_server(args.host, args.port, allow_remote=args.allow_remote)
    print(f"CELINE disponível em http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
