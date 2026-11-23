"""
Integrated end-to-end test suite for OS Simulator.
Verifies complete benchmark execution, JSON loading, and report generation.
"""

import unittest
import os
import shutil
from analysis.benchmark_runner import BenchmarkRunner


class TestIntegratedSystem(unittest.TestCase):

    def setUp(self):
        self.test_output_dir = "output/test_run"
        self.runner = BenchmarkRunner(sample_dir="sample_inputs", output_dir=self.test_output_dir)

    def tearDown(self):
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)

    def test_full_benchmark_pipeline(self):
        report = self.runner.generate_markdown_report()
        self.assertTrue(len(report) > 500)
        self.assertIn("CPU Scheduling Performance Comparison", report)
        self.assertIn("Virtual Memory Page Replacement Comparison", report)
        self.assertIn("Deadlock", report)
        self.assertIn("Disk Arm Scheduling", report)

        summary_file = os.path.join(self.test_output_dir, "benchmark_summary.md")
        self.assertTrue(os.path.exists(summary_file))

        csv_file = os.path.join(self.test_output_dir, "cpu_scheduling_comparison.csv")
        self.assertTrue(os.path.exists(csv_file))


if __name__ == "__main__":
    unittest.main()
