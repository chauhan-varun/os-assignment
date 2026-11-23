"""
Unit tests for Memory Management & Page Replacement Simulator.
"""

import unittest
from core.memory import ContiguousMemoryManager, PageReplacementSimulator
from core.exceptions import MemoryAllocationError, InvalidMemoryAccessError


class TestMemoryManager(unittest.TestCase):

    def setUp(self):
        self.block_sizes = [100, 500, 200, 300, 600]
        self.requests = [("P1", 212), ("P2", 417), ("P3", 112), ("P4", 426)]
        self.manager = ContiguousMemoryManager(self.block_sizes)

    def test_first_fit_allocation(self):
        res = self.manager.allocate("First-Fit", self.requests)
        self.assertEqual(res.algorithm, "First-Fit")
        # P1(212) -> Block 1 (size 500)
        # P2(417) -> Block 4 (size 600)
        # P3(112) -> Block 2 (size 200)
        # P4(426) -> cannot fit (only Block 0: 100, Block 3: 300 free)
        self.assertEqual(len(res.allocated_processes), 3)
        self.assertEqual(len(res.unallocated_processes), 1)
        self.assertEqual(res.unallocated_processes[0][0], "P4")
        self.assertGreater(res.total_internal_fragmentation, 0)

    def test_best_fit_allocation(self):
        res = self.manager.allocate("Best-Fit", self.requests)
        self.assertEqual(res.algorithm, "Best-Fit")
        # P1(212) fits best in 300 (frag 88)
        # P2(417) fits best in 500 (frag 83)
        # P3(112) fits best in 200 (frag 88)
        # P4(426) fits in 600 (frag 174) -> ALL 4 allocated!
        self.assertEqual(len(res.allocated_processes), 4)
        self.assertEqual(len(res.unallocated_processes), 0)

    def test_worst_fit_allocation(self):
        res = self.manager.allocate("Worst-Fit", self.requests)
        self.assertEqual(res.algorithm, "Worst-Fit")
        self.assertGreater(len(res.allocated_processes), 0)

    def test_invalid_requests(self):
        with self.assertRaises(MemoryAllocationError):
            self.manager.allocate("First-Fit", [("Err", -100)])
        with self.assertRaises(MemoryAllocationError):
            self.manager.allocate("Unsupported-Algo", [("P1", 50)])

    def test_invalid_block_sizes(self):
        with self.assertRaises(MemoryAllocationError):
            ContiguousMemoryManager([])
        with self.assertRaises(MemoryAllocationError):
            ContiguousMemoryManager([-50, 100])


class TestPageReplacement(unittest.TestCase):

    def setUp(self):
        self.ref_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        self.sim = PageReplacementSimulator(num_frames=3)

    def test_fifo_page_replacement(self):
        res = self.sim.fifo(self.ref_string)
        self.assertEqual(res.algorithm, "FIFO")
        self.assertEqual(res.total_page_faults, 15)
        self.assertEqual(res.total_page_hits, 5)
        self.assertAlmostEqual(res.fault_ratio, 15 / 20)

    def test_lru_page_replacement(self):
        res = self.sim.lru(self.ref_string)
        self.assertEqual(res.algorithm, "LRU")
        self.assertEqual(res.total_page_faults, 12)
        self.assertEqual(res.total_page_hits, 8)

    def test_optimal_page_replacement(self):
        res = self.sim.optimal(self.ref_string)
        self.assertEqual(res.algorithm, "Optimal")
        self.assertEqual(res.total_page_faults, 9)
        self.assertEqual(res.total_page_hits, 11)
        # Optimal must have fewer or equal faults than FIFO and LRU
        self.assertLessEqual(res.total_page_faults, 12)

    def test_lfu_page_replacement(self):
        res = self.sim.lfu(self.ref_string)
        self.assertEqual(res.algorithm, "LFU")
        self.assertGreater(res.total_page_hits, 0)

    def test_single_frame_boundary(self):
        sim1 = PageReplacementSimulator(num_frames=1)
        res = sim1.fifo([1, 2, 1, 2])
        self.assertEqual(res.total_page_faults, 4)

    def test_invalid_frames(self):
        with self.assertRaises(InvalidMemoryAccessError):
            PageReplacementSimulator(num_frames=0)
        with self.assertRaises(InvalidMemoryAccessError):
            PageReplacementSimulator(num_frames=-2)

    def test_empty_reference_string(self):
        with self.assertRaises(InvalidMemoryAccessError):
            self.sim.fifo([])


if __name__ == "__main__":
    unittest.main()
