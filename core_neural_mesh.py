"""Núcleo executável da topologia GENESYS 1 da CELINE.

O arquivo original descrevia a malha apenas por meio de strings. Esta versão
preserva os nomes e o fluxo 7 -> 12, mas acrescenta validação, roteamento e uma
simulação determinística que nunca transmite o conteúdo recebido.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Iterable


class MeshValidationError(ValueError):
    """Indica que a topologia não satisfaz uma invariável obrigatória."""


@dataclass(frozen=True, slots=True)
class MeshNode:
    position: int
    name: str
    role: str = "conduit"


@dataclass(frozen=True, slots=True)
class MeshRoute:
    source: int
    target: int
    direction: str
    nodes: tuple[MeshNode, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "direction": self.direction,
            "nodes": [asdict(node) for node in self.nodes],
        }


class Genesys1NeuralMesh:
    """Topologia de software compatível com a descrição GENESYS 1.

    A especificação declara 19 microchips, mas o único commit existente define
    13 elementos. A divergência é preservada e reportada, em vez de serem
    inventados seis componentes sem fonte documental.
    """

    declared_node_count = 19
    source_tower_position = 7
    target_tower_position = 12
    direction = "inverse"

    original_sequence = (
        "Quantum_Willow_3x_Liquid_Ferrous",
        "Quantum_Willow",
        "Pure_Liquid",
        "Liquid_Ferrous",
        "Pure_Ferrous",
        "Quantum_Willow",
        "Electrostatic_Dam_Tower",
        "Pure_Ferrous",
        "Liquid_Ferrous",
        "Pure_Liquid",
        "Quantum_Willow_3x_Liquid_Ferrous",
        "Electrodynamic_Bus_Tower",
        "Quantum_Willow",
    )

    def __init__(
        self,
        nodes: Iterable[str] | None = None,
        *,
        input_signal: str = "Willow_Q1_Gold24k_LiquidFerrous_Hz",
        modulator: str = "Hz_to_Electromagnetic_Pulse",
    ) -> None:
        sequence = tuple(nodes or self.original_sequence)
        self.input_signal = input_signal
        self.modulator = modulator
        self.nodes = tuple(
            MeshNode(
                position=index,
                name=name,
                role=(
                    "source_tower"
                    if index == self.source_tower_position
                    else "target_tower"
                    if index == self.target_tower_position
                    else "conduit"
                ),
            )
            for index, name in enumerate(sequence, start=1)
        )

    @property
    def input(self) -> str:
        """Compatibilidade com o atributo existente no commit inicial."""

        return self.input_signal

    @property
    def mesh(self) -> list[str]:
        """Compatibilidade com a lista existente no commit inicial."""

        return [node.name for node in self.nodes]

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    def get_node(self, position: int) -> MeshNode:
        if position < 1 or position > self.node_count:
            raise MeshValidationError(
                f"Posição {position} fora da topologia 1..{self.node_count}."
            )
        return self.nodes[position - 1]

    def validation_report(self) -> dict[str, Any]:
        issues: list[dict[str, Any]] = []
        if self.node_count != self.declared_node_count:
            issues.append(
                {
                    "code": "DECLARED_COUNT_MISMATCH",
                    "declared": self.declared_node_count,
                    "configured": self.node_count,
                    "gap": self.declared_node_count - self.node_count,
                }
            )

        source = self.get_node(self.source_tower_position)
        target = self.get_node(self.target_tower_position)
        if source.name != "Electrostatic_Dam_Tower":
            issues.append({"code": "SOURCE_TOWER_MISMATCH", "found": source.name})
        if target.name != "Electrodynamic_Bus_Tower":
            issues.append({"code": "TARGET_TOWER_MISMATCH", "found": target.name})

        repeated = {
            name: count
            for name, count in Counter(self.mesh).items()
            if count > 1
        }
        return {
            "status": "valid_with_spec_gap" if issues else "valid",
            "declared_node_count": self.declared_node_count,
            "configured_node_count": self.node_count,
            "source_tower_position": self.source_tower_position,
            "target_tower_position": self.target_tower_position,
            "repeated_components": repeated,
            "issues": issues,
        }

    def validate(self, *, require_declared_count: bool = False) -> dict[str, Any]:
        report = self.validation_report()
        fatal_codes = {"SOURCE_TOWER_MISMATCH", "TARGET_TOWER_MISMATCH"}
        if require_declared_count:
            fatal_codes.add("DECLARED_COUNT_MISMATCH")
        fatal = [item for item in report["issues"] if item["code"] in fatal_codes]
        if fatal:
            raise MeshValidationError(f"Topologia inválida: {fatal}")
        return report

    def route(
        self,
        source: int | None = None,
        target: int | None = None,
    ) -> MeshRoute:
        source = source or self.source_tower_position
        target = target or self.target_tower_position
        self.validate()
        self.get_node(source)
        self.get_node(target)
        step = 1 if target >= source else -1
        positions = range(source, target + step, step)
        return MeshRoute(
            source=source,
            target=target,
            direction=self.direction if source < target else "forward",
            nodes=tuple(self.get_node(position) for position in positions),
        )

    def flow(self) -> str:
        """Mantém a resposta histórica do núcleo original."""

        return "Energy_Transfer: Tower_7_to_Tower_12_Inverse_Direction"

    def simulate(self, payload: str | bytes) -> dict[str, Any]:
        raw = payload.encode("utf-8") if isinstance(payload, str) else payload
        route = self.route()
        return {
            "event": "mesh_route",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload_sha256": sha256(raw).hexdigest(),
            "payload_size_bytes": len(raw),
            "route": route.to_dict(),
            "external_network": False,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": "GENESYS 1",
            "input_signal": self.input_signal,
            "modulator": self.modulator,
            "nodes": [asdict(node) for node in self.nodes],
            "validation": self.validation_report(),
        }


celine_mesh = Genesys1NeuralMesh()


if __name__ == "__main__":
    import json

    print(json.dumps(celine_mesh.to_dict(), ensure_ascii=False, indent=2))
