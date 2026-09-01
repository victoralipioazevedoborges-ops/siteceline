"""Pattern Guard: autorização e trilha de auditoria local da CELINE."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timezone
from ipaddress import ip_address
import json
from pathlib import Path
from threading import RLock
from time import monotonic
from typing import Any


class PatternGuard:
    """Aplica limites locais e registra eventos sem armazenar o conteúdo."""

    sensitive_fragments = ("secret", "token", "password", "payload", "api_key")

    def __init__(
        self,
        *,
        audit_path: str | Path | None = None,
        max_body_bytes: int = 65_536,
        max_requests_per_minute: int = 120,
        max_events: int = 1_000,
    ) -> None:
        self.audit_path = Path(audit_path) if audit_path else None
        self.max_body_bytes = max_body_bytes
        self.max_requests_per_minute = max_requests_per_minute
        self._events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = RLock()

    @staticmethod
    def is_loopback(client_ip: str) -> bool:
        try:
            return ip_address(client_ip).is_loopback
        except ValueError:
            return False

    def _sanitize(self, metadata: dict[str, Any] | None) -> dict[str, Any]:
        clean: dict[str, Any] = {}
        for key, value in (metadata or {}).items():
            lowered = key.lower()
            if any(fragment in lowered for fragment in self.sensitive_fragments):
                clean[key] = "[REDACTED]"
            elif isinstance(value, (str, int, float, bool)) or value is None:
                clean[key] = value
            else:
                clean[key] = str(value)
        return clean

    def record(
        self,
        action: str,
        outcome: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "outcome": outcome,
            "metadata": self._sanitize(metadata),
        }
        line = json.dumps(event, ensure_ascii=False, sort_keys=True)
        with self._lock:
            self._events.append(event)
            if self.audit_path:
                self.audit_path.parent.mkdir(parents=True, exist_ok=True)
                with self.audit_path.open("a", encoding="utf-8") as stream:
                    stream.write(line + "\n")
        return event

    def authorize(
        self,
        *,
        client_ip: str,
        method: str,
        path: str,
        content_length: int,
    ) -> tuple[bool, str]:
        if not self.is_loopback(client_ip):
            self.record("request", "denied", {"reason": "non_loopback", "path": path})
            return False, "Somente conexões locais são permitidas."
        if content_length < 0 or content_length > self.max_body_bytes:
            self.record("request", "denied", {"reason": "body_limit", "path": path})
            return False, "Corpo da requisição acima do limite."

        now = monotonic()
        with self._lock:
            bucket = self._requests[client_ip]
            while bucket and now - bucket[0] >= 60:
                bucket.popleft()
            if len(bucket) >= self.max_requests_per_minute:
                self.record("request", "denied", {"reason": "rate_limit", "path": path})
                return False, "Limite local de requisições atingido."
            bucket.append(now)
        self.record("request", "allowed", {"method": method, "path": path})
        return True, "allowed"

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._events)[-max(0, min(limit, 500)) :]
