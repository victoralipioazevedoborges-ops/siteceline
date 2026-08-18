"""Módulos operacionais mínimos do ecossistema CELINE."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import hmac
import os
import secrets
from threading import RLock
from typing import Any

from core_neural_mesh import Genesys1NeuralMesh


class LumaModule:
    """Análise determinística local, com ponto de extensão para modelo futuro."""

    name = "LUMA"

    def analyze(self, text: str) -> dict[str, Any]:
        normalized = " ".join(text.split())
        raw = normalized.encode("utf-8")
        return {
            "module": self.name,
            "status": "online_local",
            "analysis": {
                "characters": len(normalized),
                "words": len(normalized.split()) if normalized else 0,
                "sha256": sha256(raw).hexdigest(),
                "empty": not bool(normalized),
            },
            "provider": "local_deterministic",
            "external_network": False,
        }


class ZionModule:
    name = "ZION"

    def __init__(self, mesh: Genesys1NeuralMesh) -> None:
        self.mesh = mesh

    def route(self, payload: str | bytes) -> dict[str, Any]:
        result = self.mesh.simulate(payload)
        result["module"] = self.name
        return result


class TeazerModule:
    name = "TEAZER"

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def open_session(self) -> dict[str, Any]:
        session_id = secrets.token_urlsafe(24)
        session = {
            "session_id": session_id,
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "external_network": False,
        }
        with self._lock:
            self._sessions[session_id] = session
        return session

    def close_session(self, session_id: str) -> bool:
        with self._lock:
            return self._sessions.pop(session_id, None) is not None

    def active_count(self) -> int:
        with self._lock:
            return len(self._sessions)


class ArcanaModule:
    """Desafio-resposta local baseado em HMAC-SHA256."""

    name = "ARCANA"

    def __init__(self, secret: str | bytes | None = None, ttl_seconds: int = 120) -> None:
        configured = secret or os.getenv("CELINE_ARCANA_SECRET")
        self._secret = (
            configured.encode("utf-8") if isinstance(configured, str) else configured
        ) or secrets.token_bytes(32)
        self.uses_persistent_secret = configured is not None
        self.ttl_seconds = ttl_seconds
        self._challenges: dict[str, tuple[str, datetime]] = {}
        self._lock = RLock()

    def issue_challenge(self) -> dict[str, Any]:
        session_id = secrets.token_urlsafe(18)
        nonce = secrets.token_urlsafe(24)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds)
        with self._lock:
            self._challenges[session_id] = (nonce, expires_at)
        return {
            "session_id": session_id,
            "nonce": nonce,
            "expires_at": expires_at.isoformat(),
            "algorithm": "HMAC-SHA256",
            "persistent_secret": self.uses_persistent_secret,
        }

    def sign(self, session_id: str, nonce: str) -> str:
        message = f"{session_id}:{nonce}".encode("utf-8")
        return hmac.new(self._secret, message, sha256).hexdigest()

    def verify(self, session_id: str, response: str) -> bool:
        with self._lock:
            challenge = self._challenges.pop(session_id, None)
        if challenge is None:
            return False
        nonce, expires_at = challenge
        if datetime.now(timezone.utc) >= expires_at:
            return False
        expected = self.sign(session_id, nonce)
        return hmac.compare_digest(expected, response)
