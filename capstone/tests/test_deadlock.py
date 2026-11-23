"""
Unit tests for Concurrency, Banker's Deadlock Avoidance, and WFG Cycle Detection.
"""

import unittest
from core.deadlock import BankersAlgorithm, DeadlockDetector
from core.exceptions import InvalidResourceRequestError


class TestDeadlockModule(unittest.TestCase):

    def setUp(self):
        self.resources = ["A", "B", "C"]
        self.available = {"A": 3, "B": 3, "C": 2}
        self.max_claim = {
            "P0": {"A": 7, "B": 5, "C": 3},
            "P1": {"A": 3, "B": 2, "C": 2},
            "P2": {"A": 9, "B": 0, "C": 2},
            "P3": {"A": 2, "B": 2, "C": 2},
            "P4": {"A": 4, "B": 3, "C": 3},
        }
        self.allocation = {
            "P0": {"A": 0, "B": 1, "C": 0},
            "P1": {"A": 2, "B": 0, "C": 0},
            "P2": {"A": 3, "B": 0, "C": 2},
            "P3": {"A": 2, "B": 1, "C": 1},
            "P4": {"A": 0, "B": 0, "C": 2},
        }
        self.banker = BankersAlgorithm(self.resources, self.available, self.max_claim, self.allocation)

    def test_initial_state_safety(self):
        safety = self.banker.is_safe_state()
        self.assertTrue(safety.is_safe)
        self.assertEqual(len(safety.safe_sequence), 5)
        # P1 is safe to finish first in this standard textbook state
        self.assertEqual(safety.safe_sequence[0], "P1")

    def test_valid_request_grant(self):
        # Request by P1: (1, 0, 2) <= Need (1, 2, 2) and <= Available (3, 3, 2)
        res = self.banker.request_resources("P1", {"A": 1, "B": 0, "C": 2})
        self.assertTrue(res.granted)
        self.assertTrue(res.resulting_safety.is_safe)
        self.assertEqual(self.banker.available["A"], 2)
        self.assertEqual(self.banker.available["C"], 0)

    def test_request_exceeding_need_denied(self):
        # P1 requests A=5 when Max is 3 and Alloc is 2 (Need is 1)
        res = self.banker.request_resources("P1", {"A": 5, "B": 0, "C": 0})
        self.assertFalse(res.granted)
        self.assertIn("exceeded", res.message.lower())

    def test_request_exceeding_available_denied(self):
        # P4 requests A=4, but Available is only 3
        res = self.banker.request_resources("P4", {"A": 4, "B": 0, "C": 0})
        self.assertFalse(res.granted)
        self.assertIn("insufficient", res.message.lower())

    def test_request_leading_to_unsafe_state_rejected(self):
        # P4 requests (3, 3, 0) -> leaves remaining Available (0, 0, 2), causing an UNSAFE state
        res = self.banker.request_resources("P4", {"A": 3, "B": 3, "C": 0})
        self.assertFalse(res.granted)
        self.assertIn("unsafe", res.message.lower())

    def test_wfg_cycle_detection(self):
        # Acyclic case
        acyclic_graph = {"P1": ["P2"], "P2": ["P3"], "P3": []}
        d1 = DeadlockDetector(acyclic_graph)
        res1 = d1.detect_cycles()
        self.assertFalse(res1.deadlock_detected)
        self.assertEqual(len(res1.detected_cycles), 0)

        # Cyclic case (Deadlock)
        cyclic_graph = {"P1": ["P2"], "P2": ["P3"], "P3": ["P1"]}
        d2 = DeadlockDetector(cyclic_graph)
        res2 = d2.detect_cycles()
        self.assertTrue(res2.deadlock_detected)
        self.assertGreater(len(res2.detected_cycles), 0)
        self.assertIn("P1", res2.deadlocked_nodes)


if __name__ == "__main__":
    unittest.main()
