import json
from threading import Thread
import unittest
from urllib.request import Request, urlopen

from celine.api import build_server
from celine.ecosystem import CelineEcosystem


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ecosystem = CelineEcosystem(arcana_secret="segredo-de-teste")
        cls.server = build_server("127.0.0.1", 0, ecosystem=cls.ecosystem)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, path: str, body: dict | None = None) -> tuple[int, dict]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=2) as response:
            return response.status, json.loads(response.read())

    def test_health_endpoint(self) -> None:
        status, payload = self.request("/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload["name"], "CELINE")
        self.assertEqual(payload["bind_policy"], "loopback_only")
        self.assertEqual(payload["gemini_policy"], "blocked")

    def test_connectors_endpoint_discloses_policy_but_not_credentials(self) -> None:
        status, payload = self.request("/connectors")
        self.assertEqual(status, 200)
        self.assertEqual(payload["gemini"], "blocked")
        self.assertFalse(payload["automatic_forwarding"])
        serialized = json.dumps(payload)
        self.assertNotIn("segredo-de-teste", serialized)

    def test_luma_and_zion_endpoints(self) -> None:
        status, analysis = self.request("/luma", {"prompt": "teste local"})
        self.assertEqual(status, 200)
        self.assertEqual(analysis["module"], "LUMA")

        status, route = self.request("/zion/route", {"message": "conteúdo"})
        self.assertEqual(status, 200)
        self.assertEqual(route["module"], "ZION")
        self.assertNotIn("conteúdo", json.dumps(route))

    def test_pulse_lab_profile_and_simulation_are_software_only(self) -> None:
        status, profile = self.request("/pulse-lab")
        self.assertEqual(status, 200)
        self.assertEqual(profile["profile"]["frequencies_hz"], [9_847.0, 9_874.0])
        self.assertFalse(profile["profile"]["physical_emission"])

        status, result = self.request(
            "/pulse-lab/simulate", {"duration_ms": 5.0}
        )
        self.assertEqual(status, 200)
        self.assertEqual(result["chunk"]["sample_count"], 240)
        self.assertFalse(result["physical_emission"])
        self.assertFalse(result["network_transmission"])
        self.assertIn("arcana_integrity_seal", result)


if __name__ == "__main__":
    unittest.main()
