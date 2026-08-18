import json
import unittest

from celine.connectors import (
    ConnectorDisabledError,
    ConnectorPolicyError,
    ConnectorRegistry,
    ConnectorSpec,
)


class ConnectorTests(unittest.TestCase):
    def test_gemini_name_host_path_and_payload_are_blocked(self) -> None:
        with self.assertRaises(ConnectorPolicyError):
            ConnectorRegistry(
                (
                    ConnectorSpec(
                        name="gemini",
                        base_url="https://example.com",
                        enabled_env="CELINE_TEST_ENABLED",
                        allowed_path_prefixes=("/models",),
                    ),
                )
            )
        with self.assertRaises(ConnectorPolicyError):
            ConnectorRegistry(
                (
                    ConnectorSpec(
                        name="external_ai",
                        base_url="https://generativelanguage.googleapis.com/v1",
                        enabled_env="CELINE_TEST_ENABLED",
                        allowed_path_prefixes=("/models",),
                    ),
                )
            )

        registry = ConnectorRegistry.defaults(
            environment={
                "CELINE_OPENAI_ENABLED": "true",
                "OPENAI_API_KEY": "segredo-de-teste",
            },
            transport=lambda *_args: {"status": 200, "data": {}},
        )
        with self.assertRaises(ConnectorPolicyError):
            registry.request_json(
                "openai",
                "POST",
                "/responses",
                {"model": "gemini-pro", "input": "teste"},
            )

    def test_remote_plain_http_is_rejected(self) -> None:
        with self.assertRaises(ConnectorPolicyError):
            ConnectorRegistry(
                (
                    ConnectorSpec(
                        name="unsafe",
                        base_url="http://example.com/api",
                        enabled_env="CELINE_UNSAFE_ENABLED",
                        allowed_path_prefixes=("/run",),
                    ),
                )
            )

    def test_remote_literal_ip_and_prefix_confusion_are_rejected(self) -> None:
        with self.assertRaises(ConnectorPolicyError):
            ConnectorRegistry(
                (
                    ConnectorSpec(
                        name="metadata",
                        base_url="https://169.254.169.254",
                        enabled_env="CELINE_METADATA_ENABLED",
                        allowed_path_prefixes=("/latest",),
                    ),
                )
            )

        registry = ConnectorRegistry.defaults(
            environment={
                "CELINE_GITHUB_ENABLED": "true",
                "GITHUB_TOKEN": "segredo-de-teste",
            },
            transport=lambda *_args: {"status": 200, "data": {}},
        )
        with self.assertRaises(ConnectorPolicyError):
            registry.request_json("github", "GET", "/userland")

    def test_connectors_are_disabled_by_default(self) -> None:
        registry = ConnectorRegistry.defaults(environment={})
        self.assertFalse(registry.any_enabled())
        with self.assertRaises(ConnectorDisabledError):
            registry.request_json("openai", "POST", "/responses", {})

    def test_explicit_request_uses_fixed_destination_without_exposing_secret(self) -> None:
        captured = {}

        def fake_transport(url, method, headers, body, timeout, max_response_bytes):
            captured.update(
                {
                    "url": url,
                    "method": method,
                    "headers": dict(headers),
                    "body": body,
                    "timeout": timeout,
                    "max_response_bytes": max_response_bytes,
                }
            )
            return {"status": 200, "data": {"ok": True}}

        secret = "chave-que-nao-pode-aparecer-no-status"
        registry = ConnectorRegistry.defaults(
            environment={
                "CELINE_OPENAI_ENABLED": "true",
                "OPENAI_API_KEY": secret,
            },
            transport=fake_transport,
        )
        status_json = json.dumps(registry.status())
        self.assertNotIn(secret, status_json)

        result = registry.request_json(
            "openai",
            "POST",
            "/responses",
            {"model": "gpt-test", "input": "pedido explícito"},
        )
        self.assertEqual(result["status"], 200)
        self.assertEqual(captured["url"], "https://api.openai.com/v1/responses")
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["headers"]["Authorization"], f"Bearer {secret}")


if __name__ == "__main__":
    unittest.main()
