import ast
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INFRASTRUCTURE_ROOT = PROJECT_ROOT / "src" / "infrastructure"


class InfrastructureCleanArchitectureTest(unittest.TestCase):
    def test_infrastructure_does_not_depend_on_presentation_layer(self) -> None:
        violations: list[str] = []

        for path in INFRASTRUCTURE_ROOT.rglob("*.py"):
            module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(module):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith("src.presentation"):
                        violations.append(f"{path}: from {node.module} import ...")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("src.presentation"):
                            violations.append(f"{path}: import {alias.name}")

        self.assertEqual([], violations, "\n".join(violations))
