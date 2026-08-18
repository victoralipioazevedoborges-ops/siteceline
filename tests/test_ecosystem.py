import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from celine.ecosystem import CelineEcosystem


class EcosystemTests(unittest.TestCase):
    def test_modules_are_coupled_and_local(self) -> None:
        ecosystem = CelineEcosystem(arcana_secret="segredo-de-teste")
        health = ecosystem.health()
        self.assertEqual(health["name"], "CELINE")
        self.assertEqual(len(health["modules"]), 7)
        self.assertFalse(health["external_network"])
        self.assertEqual(health["gemini_policy"], "blocked")

        analysis = ecosystem.analyze("uma análise local")
        self.assertEqual(analysis["provider"], "local_deterministic")

        route = ecosystem.route("mensagem")
        self.assertEqual(route["module"], "ZION")
        self.assertNotIn("mensagem", json.dumps(route))

    def test_pulse_simulation_is_sealed_and_has_no_physical_output(self) -> None:
        ecosystem = CelineEcosystem(arcana_secret="segredo-de-teste")
        result = ecosystem.simulate_pulses(10.0)
        self.assertEqual(result["profile"]["frequencies_hz"], [9_847.0, 9_874.0])
        self.assertEqual(result["profile"]["beat_frequency_hz"], 27.0)
        self.assertEqual(result["chunk"]["sample_count"], 480)
        self.assertFalse(result["physical_emission"])
        self.assertFalse(result["network_transmission"])
        self.assertTrue(ecosystem.verify_pulse_simulation(result))

        tampered = json.loads(json.dumps(result))
        tampered["profile"]["frequencies_hz"][0] = 1.0
        self.assertFalse(ecosystem.verify_pulse_simulation(tampered))

    def test_arcana_challenge_is_single_use(self) -> None:
        ecosystem = CelineEcosystem(arcana_secret="segredo-de-teste")
        challenge = ecosystem.issue_arcana_challenge()
        response = ecosystem.arcana.sign(
            challenge["session_id"], challenge["nonce"]
        )
        self.assertTrue(ecosystem.verify_arcana(challenge["session_id"], response))
        self.assertFalse(ecosystem.verify_arcana(challenge["session_id"], response))

    def test_teazer_session_can_be_closed(self) -> None:
        ecosystem = CelineEcosystem()
        session = ecosystem.open_teazer_session()
        self.assertEqual(ecosystem.teazer.active_count(), 1)
        self.assertTrue(ecosystem.close_teazer_session(session["session_id"]))
        self.assertEqual(ecosystem.teazer.active_count(), 0)

    def test_pattern_guard_redacts_sensitive_metadata(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            ecosystem = CelineEcosystem(audit_path=path)
            ecosystem.pattern_guard.record(
                "test", "ok", {"api_key": "nao-gravar", "count": 1}
            )
            event = json.loads(path.read_text(encoding="utf-8").splitlines()[-1])
            self.assertEqual(event["metadata"]["api_key"], "[REDACTED]")
            self.assertEqual(event["metadata"]["count"], 1)


if __name__ == "__main__":
    unittest.main()
