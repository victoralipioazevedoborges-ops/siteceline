"""Orquestrador dos módulos do ecossistema CELINE."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core_neural_mesh import Genesys1NeuralMesh

from .connectors import ConnectorRegistry, Transport
from .modules import ArcanaModule, LumaModule, TeazerModule, ZionModule
from .pattern_guard import PatternGuard


class CelineEcosystem:
    module_catalog = {
        "CELINE": "Ecossistema e orquestração local",
        "LUMA": "Análise, validação e fiscalização local",
        "ARCANA": "Desafio-resposta e controle de sessão",
        "ZION": "Roteamento auditável sobre a malha GENESYS 1",
        "TEAZER": "Isolamento e encerramento de sessões locais",
        "PATTERN_GUARD": "Política, limites e auditoria redigida",
    }

    def __init__(
        self,
        *,
        audit_path: str | Path | None = None,
        arcana_secret: str | bytes | None = None,
        connector_environment: dict[str, str] | None = None,
        connector_transport: Transport | None = None,
    ) -> None:
        self.mesh = Genesys1NeuralMesh()
        self.pattern_guard = PatternGuard(audit_path=audit_path)
        self.luma = LumaModule()
        self.arcana = ArcanaModule(secret=arcana_secret)
        self.zion = ZionModule(self.mesh)
        self.teazer = TeazerModule()
        self.connectors = ConnectorRegistry.defaults(
            environment=connector_environment,
            transport=connector_transport,
        )
        self.pattern_guard.record("ecosystem_start", "ok", {"name": "CELINE"})

    def modules(self) -> list[dict[str, str]]:
        return [
            {"name": name, "role": role, "status": "online"}
            for name, role in self.module_catalog.items()
        ]

    def health(self) -> dict[str, Any]:
        validation = self.mesh.validation_report()
        connectors = self.connectors.status()
        return {
            "name": "CELINE",
            "version": "0.2.0",
            "status": (
                "operational_with_spec_gap"
                if validation["issues"]
                else "operational"
            ),
            "external_network": self.connectors.any_enabled(),
            "external_network_policy": "explicit_opt_in_no_automatic_forwarding",
            "enabled_connectors": [
                item["name"] for item in connectors if item["enabled"]
            ],
            "gemini_policy": "blocked",
            "bind_policy": "loopback_only",
            "mesh": validation,
            "modules": self.modules(),
            "teazer_active_sessions": self.teazer.active_count(),
            "arcana_persistent_secret": self.arcana.uses_persistent_secret,
        }

    def connector_status(self) -> list[dict[str, Any]]:
        return self.connectors.status()

    def connector_request(
        self,
        name: str,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Executa uma saída explicitamente habilitada sem registrar conteúdo."""

        result = self.connectors.request_json(name, method, path, payload)
        self.pattern_guard.record(
            "connector_request",
            "completed",
            {"connector": name, "method": method.upper(), "path": path},
        )
        return result

    def analyze(self, text: str) -> dict[str, Any]:
        result = self.luma.analyze(text)
        self.pattern_guard.record(
            "luma_analyze",
            "ok",
            {"characters": result["analysis"]["characters"]},
        )
        return result

    def route(self, payload: str | bytes) -> dict[str, Any]:
        result = self.zion.route(payload)
        self.pattern_guard.record(
            "zion_route",
            "ok",
            {
                "payload_size_bytes": result["payload_size_bytes"],
                "payload_sha256": result["payload_sha256"],
            },
        )
        return result

    def issue_arcana_challenge(self) -> dict[str, Any]:
        result = self.arcana.issue_challenge()
        self.pattern_guard.record("arcana_challenge", "issued", {})
        return result

    def verify_arcana(self, session_id: str, response: str) -> bool:
        valid = self.arcana.verify(session_id, response)
        self.pattern_guard.record(
            "arcana_verify", "accepted" if valid else "denied", {}
        )
        return valid

    def open_teazer_session(self) -> dict[str, Any]:
        session = self.teazer.open_session()
        self.pattern_guard.record("teazer_session", "opened", {})
        return session

    def close_teazer_session(self, session_id: str) -> bool:
        closed = self.teazer.close_session(session_id)
        self.pattern_guard.record(
            "teazer_session", "closed" if closed else "not_found", {}
        )
        return closed
