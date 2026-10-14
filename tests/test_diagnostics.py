import json
from threading import Thread
import unittest

from celine.api import build_server
from celine.diagnostics import _loopback_target, diagnose
from celine.ecosystem import CelineEcosystem


class CommunicationDiagnosticTests(unittest.TestCase):
    def test_rejects_remote_and_non_health_targets(self) -> None:
        with self.assertRaises(ValueError):
            _loopback_target("https://example.com/health")
        with self.assertRaises(ValueError):
            _loopback_target("http://127.0.0.1:8787/audit")
        with self.assertRaises(ValueError):
            _loopback_target("http://user:password@127.0.0.1:8787/health")

    def test_reports_local_health_without_payload_or_credentials(self) -> None:
        ecosystem = CelineEcosystem(
            arcana_secret="segredo-de-teste", connector_environment={}
        )
        server = build_server("127.0.0.1", 0, ecosystem=ecosystem)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = diagnose(
                f"http://127.0.0.1:{server.server_port}/health", timeout=2
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertTrue(result.reachable)
        self.assertEqual(result.http_status, 200)
        self.assertIn(result.celine_status, {"operational", "operational_with_spec_gap"})
        self.assertFalse(result.external_network)
        serialized = json.dumps(result.__dict__ if hasattr(result, "__dict__") else str(result))
        self.assertNotIn("segredo-de-teste", serialized)

    def test_reports_unavailable_local_api_without_exception_details(self) -> None:
        result = diagnose("http://127.0.0.1:1/health", timeout=0.1)
        self.assertFalse(result.reachable)
        self.assertIsNone(result.http_status)
        self.assertNotIn("127.0.0.1", result.error or "")


if __name__ == "__main__":
    unittest.main()
