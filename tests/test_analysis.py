from __future__ import annotations

import csv
import json
import shutil
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from reliability_cli.analysis import analyze_component, compare_components
from reliability_cli.models import compute_metrics, exponential_reliability, weibull_reliability


class ModelTests(unittest.TestCase):
    def test_compute_metrics(self) -> None:
        metrics = compute_metrics(operating_time=1000, failures=2)
        self.assertAlmostEqual(metrics.failure_rate, 0.002)
        self.assertAlmostEqual(metrics.mtbf, 500.0)

    def test_reliability_functions(self) -> None:
        self.assertAlmostEqual(exponential_reliability(100, 0.001), 0.9048374180, places=6)
        self.assertAlmostEqual(weibull_reliability(100, 400, 2.0), 0.9394130628, places=6)


class AnalyzeWorkflowTests(unittest.TestCase):
    def _reset_output_root(self, name: str) -> Path:
        output_root = PROJECT_ROOT / ".tmp-tests" / name
        shutil.rmtree(output_root, ignore_errors=True)
        output_root.mkdir(parents=True, exist_ok=True)
        return output_root

    def test_analyze_component_writes_outputs(self) -> None:
        tmp_dir = self._reset_output_root("analyze")
        try:
            output_dir = tmp_dir / "results"
            result = analyze_component(
                input_path="examples/component_a.csv",
                time_col="hours",
                failure_col="failures",
                out_dir=str(output_dir),
                model="weibull",
                theta=4000,
                beta=2.2,
                criticality="medium",
                tmax=5000,
                name="component_a",
            )

            self.assertEqual(result.name, "component_a")
            self.assertTrue((output_dir / "metrics.csv").exists())
            self.assertTrue((output_dir / "recommendations.csv").exists())
            self.assertTrue((output_dir / "summary.json").exists())
            self.assertTrue((output_dir / "component_a_reliability.png").exists())

            with (output_dir / "summary.json").open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            self.assertEqual(payload["component"], "component_a")
            self.assertIn("recommendations", payload)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_compare_components_writes_outputs(self) -> None:
        tmp_dir = self._reset_output_root("compare")
        try:
            output_dir = tmp_dir / "compare"
            results = compare_components(
                input_path="examples/components.csv",
                name_col="component",
                time_col="operating_time",
                failure_col="failures",
                theta_col="theta",
                beta_col="beta",
                criticality_col="criticality",
                out_dir=str(output_dir),
                model="weibull",
                tmax=10000,
            )
            self.assertEqual(len(results), 3)
            self.assertTrue((output_dir / "comparison_overlay.png").exists())

            with (output_dir / "metrics.csv").open("r", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 3)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
