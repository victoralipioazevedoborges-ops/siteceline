import json
import unittest

from core_neural_mesh import Genesys1NeuralMesh, MeshValidationError


class NeuralMeshTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mesh = Genesys1NeuralMesh()

    def test_preserves_documented_towers_and_reports_gap(self) -> None:
        report = self.mesh.validation_report()
        self.assertEqual(self.mesh.node_count, 13)
        self.assertEqual(report["declared_node_count"], 19)
        self.assertEqual(report["issues"][0]["gap"], 6)
        self.assertEqual(self.mesh.get_node(7).role, "source_tower")
        self.assertEqual(self.mesh.get_node(12).role, "target_tower")

    def test_route_is_executable_and_deterministic(self) -> None:
        route = self.mesh.route()
        self.assertEqual([node.position for node in route.nodes], [7, 8, 9, 10, 11, 12])
        self.assertEqual(route.direction, "inverse")
        self.assertEqual(self.mesh.flow(), "Energy_Transfer: Tower_7_to_Tower_12_Inverse_Direction")

    def test_simulation_does_not_return_payload(self) -> None:
        secret_text = "conteudo-que-nao-deve-vazar"
        result = self.mesh.simulate(secret_text)
        serialized = json.dumps(result)
        self.assertNotIn(secret_text, serialized)
        self.assertEqual(result["payload_size_bytes"], len(secret_text.encode()))
        self.assertFalse(result["external_network"])

    def test_strict_validation_refuses_unknown_six_nodes(self) -> None:
        with self.assertRaises(MeshValidationError):
            self.mesh.validate(require_declared_count=True)


if __name__ == "__main__":
    unittest.main()
