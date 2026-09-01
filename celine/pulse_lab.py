"""Pulse Lab seguro da CELINE para as frequências 9.847 e 9.874 Hz.

Este módulo gera somente amostras numéricas em memória. Ele não abre placa de
som, socket, rádio, GPIO, USB ou qualquer interface capaz de produzir emissão
física. A continuidade é obtida pelo índice absoluto de amostra, permitindo
comparar blocos sucessivos com uma geração única de igual duração.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite, pi, sin, sqrt
from struct import pack
from threading import RLock
from typing import Any

from core_neural_mesh import Genesys1NeuralMesh


class PulseConfigurationError(ValueError):
    """Configuração ou duração incompatível com a simulação segura."""


@dataclass(frozen=True, slots=True)
class DualFrequencyProfile:
    primary_hz: float = 9_847.0
    secondary_hz: float = 9_874.0
    sample_rate_hz: int = 48_000
    component_amplitude: float = 0.45
    max_duration_ms: float = 1_000.0

    def __post_init__(self) -> None:
        frequencies = (self.primary_hz, self.secondary_hz)
        if not all(isfinite(value) and value > 0 for value in frequencies):
            raise PulseConfigurationError("Frequências devem ser positivas e finitas.")
        if self.primary_hz == self.secondary_hz:
            raise PulseConfigurationError("As duas frequências devem ser distintas.")
        if self.sample_rate_hz <= 2 * max(frequencies):
            raise PulseConfigurationError(
                "A taxa de amostragem deve superar duas vezes a maior frequência."
            )
        if not 0 < self.component_amplitude <= 0.5:
            raise PulseConfigurationError(
                "A amplitude de cada componente deve estar entre 0 e 0,5."
            )
        if not isfinite(self.max_duration_ms) or self.max_duration_ms <= 0:
            raise PulseConfigurationError("A duração máxima deve ser positiva.")

    @property
    def beat_hz(self) -> float:
        return abs(self.secondary_hz - self.primary_hz)

    @property
    def center_hz(self) -> float:
        return (self.primary_hz + self.secondary_hz) / 2

    @property
    def nyquist_hz(self) -> float:
        return self.sample_rate_hz / 2

    def to_dict(self) -> dict[str, Any]:
        return {
            "frequencies_hz": [self.primary_hz, self.secondary_hz],
            "beat_frequency_hz": self.beat_hz,
            "center_frequency_hz": self.center_hz,
            "sample_rate_hz": self.sample_rate_hz,
            "nyquist_hz": self.nyquist_hz,
            "nyquist_margin_hz": self.nyquist_hz
            - max(self.primary_hz, self.secondary_hz),
            "component_amplitude": self.component_amplitude,
            "maximum_combined_amplitude": 2 * self.component_amplitude,
            "phase_continuity": True,
            "requested_modulator": "Hz_to_Electromagnetic_Pulse",
            "implemented_medium": "in_memory_digital_waveform",
            "physical_emission": False,
            "audio_output": False,
            "network_output": False,
            "claimed_network_cleaning": "not_established",
            "claimed_clone_prevention": "not_established",
        }


@dataclass(frozen=True, slots=True)
class PulseChunk:
    start_sample: int
    sample_rate_hz: int
    samples: tuple[float, ...]

    @property
    def sample_count(self) -> int:
        return len(self.samples)

    @property
    def end_sample(self) -> int:
        return self.start_sample + self.sample_count

    def pcm16_bytes(self) -> bytes:
        encoded = bytearray()
        for value in self.samples:
            clipped = max(-1.0, min(1.0, value))
            encoded.extend(pack("<h", round(clipped * 32_767)))
        return bytes(encoded)

    def summary(self, profile: DualFrequencyProfile) -> dict[str, Any]:
        if not self.samples:
            raise PulseConfigurationError("Um bloco não pode ser vazio.")
        peak = max(abs(value) for value in self.samples)
        rms = sqrt(sum(value * value for value in self.samples) / self.sample_count)

        def phase_degrees(frequency_hz: float, sample_index: int) -> float:
            cycles = frequency_hz * sample_index / self.sample_rate_hz
            return (cycles % 1.0) * 360.0

        return {
            "start_sample": self.start_sample,
            "end_sample_exclusive": self.end_sample,
            "sample_count": self.sample_count,
            "duration_ms": self.sample_count * 1_000 / self.sample_rate_hz,
            "peak": peak,
            "rms": rms,
            "pcm16_sha256": sha256(self.pcm16_bytes()).hexdigest(),
            "start_phase_degrees": {
                str(profile.primary_hz): phase_degrees(
                    profile.primary_hz, self.start_sample
                ),
                str(profile.secondary_hz): phase_degrees(
                    profile.secondary_hz, self.start_sample
                ),
            },
            "next_phase_degrees": {
                str(profile.primary_hz): phase_degrees(
                    profile.primary_hz, self.end_sample
                ),
                str(profile.secondary_hz): phase_degrees(
                    profile.secondary_hz, self.end_sample
                ),
            },
            "raw_samples_exposed": False,
        }


class DualFrequencyPulseEngine:
    """Gerador determinístico, limitado e contínuo de dois tons digitais."""

    def __init__(self, profile: DualFrequencyProfile | None = None) -> None:
        self.profile = profile or DualFrequencyProfile()
        self._cursor = 0
        self._lock = RLock()

    @property
    def cursor(self) -> int:
        with self._lock:
            return self._cursor

    def reset(self) -> None:
        with self._lock:
            self._cursor = 0

    def render(self, duration_ms: float) -> PulseChunk:
        if isinstance(duration_ms, bool) or not isinstance(duration_ms, (int, float)):
            raise PulseConfigurationError("duration_ms deve ser numérico.")
        duration = float(duration_ms)
        if (
            not isfinite(duration)
            or duration <= 0
            or duration > self.profile.max_duration_ms
        ):
            raise PulseConfigurationError(
                f"duration_ms deve estar entre 0 e {self.profile.max_duration_ms}."
            )
        sample_count = round(self.profile.sample_rate_hz * duration / 1_000)
        if sample_count < 1:
            raise PulseConfigurationError("Duração insuficiente para uma amostra.")

        with self._lock:
            start_sample = self._cursor
            self._cursor += sample_count

        amplitude = self.profile.component_amplitude
        sample_rate = self.profile.sample_rate_hz
        primary = self.profile.primary_hz
        secondary = self.profile.secondary_hz
        samples = tuple(
            amplitude
            * (
                sin(2 * pi * primary * sample_index / sample_rate)
                + sin(2 * pi * secondary * sample_index / sample_rate)
            )
            for sample_index in range(start_sample, start_sample + sample_count)
        )
        return PulseChunk(
            start_sample=start_sample,
            sample_rate_hz=sample_rate,
            samples=samples,
        )


class CelinePulseLab:
    """Acopla o gerador à topologia GENESYS sem transmissão física ou IP."""

    name = "PULSE_LAB"

    def __init__(
        self,
        mesh: Genesys1NeuralMesh,
        profile: DualFrequencyProfile | None = None,
    ) -> None:
        self.mesh = mesh
        self.engine = DualFrequencyPulseEngine(profile)

    def dispersion_plan(self) -> dict[str, Any]:
        route_positions = {node.position for node in self.mesh.route().nodes}
        node_count = self.mesh.node_count
        frequencies = [
            self.engine.profile.primary_hz,
            self.engine.profile.secondary_hz,
        ]
        return {
            "mode": "software_topology_plan",
            "scope": "all_configured_mesh_nodes",
            "configured_nodes": node_count,
            "declared_nodes": self.mesh.declared_node_count,
            "unresolved_gap": self.mesh.declared_node_count - node_count,
            "nodes": [
                {
                    "position": node.position,
                    "name": node.name,
                    "frequencies_hz": frequencies,
                    "phase_offset_degrees": (node.position - 1) * 360 / node_count,
                    "on_documented_route_7_to_12": node.position in route_positions,
                }
                for node in self.mesh.nodes
            ],
            "physical_emission": False,
            "network_transmission": False,
        }

    def status(self) -> dict[str, Any]:
        return {
            "module": self.name,
            "status": "online_simulation_only",
            "profile": self.engine.profile.to_dict(),
            "dispersion": self.dispersion_plan(),
            "safety_boundary": (
                "No audio, radio, GPIO, USB, socket or network interface is opened."
            ),
        }

    def simulate(self, duration_ms: float = 100.0) -> dict[str, Any]:
        chunk = self.engine.render(duration_ms)
        return {
            "module": self.name,
            "status": "simulated",
            "profile": self.engine.profile.to_dict(),
            "chunk": chunk.summary(self.engine.profile),
            "dispersion": self.dispersion_plan(),
            "physical_emission": False,
            "network_transmission": False,
        }
