from math import cos, hypot, pi, sin
import unittest

from core_neural_mesh import Genesys1NeuralMesh
from celine.pulse_lab import (
    CelinePulseLab,
    DualFrequencyProfile,
    DualFrequencyPulseEngine,
    PulseConfigurationError,
)


class PulseLabTests(unittest.TestCase):
    def test_exact_frequencies_beat_and_nyquist_margin(self) -> None:
        profile = DualFrequencyProfile()
        self.assertEqual(profile.primary_hz, 9_847.0)
        self.assertEqual(profile.secondary_hz, 9_874.0)
        self.assertEqual(profile.beat_hz, 27.0)
        self.assertEqual(profile.center_hz, 9_860.5)
        self.assertGreater(profile.nyquist_hz, profile.secondary_hz)
        self.assertFalse(profile.to_dict()["physical_emission"])

    def test_successive_chunks_are_phase_continuous(self) -> None:
        sequential = DualFrequencyPulseEngine()
        first = sequential.render(5.0)
        second = sequential.render(5.0)

        single = DualFrequencyPulseEngine().render(10.0)
        self.assertEqual(first.samples + second.samples, single.samples)
        self.assertEqual(second.start_sample, first.end_sample)

    def test_one_second_spectrum_contains_both_requested_components(self) -> None:
        chunk = DualFrequencyPulseEngine().render(1_000.0)

        def measured_amplitude(frequency_hz: float) -> float:
            count = chunk.sample_count
            sine = sum(
                value * sin(2 * pi * frequency_hz * index / chunk.sample_rate_hz)
                for index, value in enumerate(chunk.samples)
            )
            cosine = sum(
                value * cos(2 * pi * frequency_hz * index / chunk.sample_rate_hz)
                for index, value in enumerate(chunk.samples)
            )
            return 2 * hypot(sine, cosine) / count

        self.assertAlmostEqual(measured_amplitude(9_847.0), 0.45, places=9)
        self.assertAlmostEqual(measured_amplitude(9_874.0), 0.45, places=9)
        self.assertAlmostEqual(measured_amplitude(9_000.0), 0.0, places=9)

    def test_dispersion_is_a_plan_for_all_known_nodes_not_network_output(self) -> None:
        lab = CelinePulseLab(Genesys1NeuralMesh())
        plan = lab.dispersion_plan()
        self.assertEqual(plan["configured_nodes"], 13)
        self.assertEqual(plan["declared_nodes"], 19)
        self.assertEqual(plan["unresolved_gap"], 6)
        self.assertEqual(len(plan["nodes"]), 13)
        self.assertFalse(plan["physical_emission"])
        self.assertFalse(plan["network_transmission"])

    def test_duration_is_bounded(self) -> None:
        engine = DualFrequencyPulseEngine()
        with self.assertRaises(PulseConfigurationError):
            engine.render(0)
        with self.assertRaises(PulseConfigurationError):
            engine.render(1_001)
        with self.assertRaises(PulseConfigurationError):
            engine.render(True)


if __name__ == "__main__":
    unittest.main()
