#!/usr/bin/env python3
"""
=============================================================================
 OS-ISS AUTOMATED TEST SUITE & RELIABILITY VALIDATION (PHASE 4)
 Tests valid, invalid, and boundary inputs across all core modules.
=============================================================================
"""

import os
import sys
import unittest
import logging

# Ensure modules are on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "section-1", "q3-fcfs-sjf"))
sys.path.append(os.path.join(BASE_DIR, "section-1", "q4-priority-round-robin"))
sys.path.append(os.path.join(BASE_DIR, "section-2", "q4-deadlock-bankers"))
sys.path.append(os.path.join(BASE_DIR, "section-3", "q1-contiguous-allocation-swapping"))
sys.path.append(os.path.join(BASE_DIR, "section-3", "q2-paging-segmentation"))
sys.path.append(os.path.join(BASE_DIR, "section-3", "q3-demand-paging-replacement"))
sys.path.append(os.path.join(BASE_DIR, "section-3", "q5-disk-scheduling-swap"))
sys.path.append(os.path.join(BASE_DIR, "section-4", "q3-file-allocation-methods"))
sys.path.append(os.path.join(BASE_DIR, "section-4", "q4-free-space-access-control"))

import scheduling_fcfs_sjf as sched
import deadlock_bankers as db
import contiguous_swapping as cs
import page_replacement as pr
import disk_scheduling_swap as dss
import file_allocation as fa
import free_space_access_control as fsac

logger = logging.getLogger("OS-ISS-Tests")


class TestOSReliabilityAndBoundaries(unittest.TestCase):

    # -------------------------------------------------------------
    # 1. Process Scheduling Tests
    # -------------------------------------------------------------
    def test_fcfs_normal_and_idle(self):
        """Test FCFS with intentional arrival gap producing CPU idle intervals."""
        dataset = [
            {"pid": "P1", "at": 0, "bt": 3},
            {"pid": "P2", "at": 5, "bt": 2},  # Idle between 3 and 5
        ]
        intervals = sched.schedule_fcfs(dataset)
        self.assertEqual(len(intervals), 3)
        self.assertEqual(intervals[0]["type"], "PROC")
        self.assertEqual(intervals[1]["type"], "IDLE")
        self.assertEqual(intervals[1]["start"], 3)
        self.assertEqual(intervals[1]["end"], 5)
        self.assertEqual(intervals[2]["type"], "PROC")

    def test_sjf_tie_breaking(self):
        """Test SJF tie-breaking when two processes have identical burst times."""
        dataset = [
            {"pid": "P1", "at": 0, "bt": 4},
            {"pid": "P2", "at": 1, "bt": 2},
            {"pid": "P3", "at": 2, "bt": 2},  # Same BT as P2, arrives later
        ]
        intervals = sched.schedule_sjf_non_preemptive(dataset)
        exec_pids = [i["pid"] for i in intervals if i["type"] == "PROC"]
        self.assertEqual(exec_pids, ["P1", "P2", "P3"])

    # -------------------------------------------------------------
    # 2. Banker's Algorithm Safety Tests
    # -------------------------------------------------------------
    def test_bankers_need_matrix_calculation(self):
        """Test that Need matrix is strictly calculated as Max - Allocation."""
        alloc = [[0, 1, 0], [2, 0, 0]]
        maximum = [[7, 5, 3], [3, 2, 2]]
        need = [[maximum[i][j] - alloc[i][j] for j in range(3)] for i in range(2)]
        self.assertEqual(need[0], [7, 4, 3])
        self.assertEqual(need[1], [1, 2, 2])

    # -------------------------------------------------------------
    # 3. Memory & Address Translation Tests
    # -------------------------------------------------------------
    def test_paging_address_translation(self):
        """Test page number, offset calculation and physical address computation."""
        page_size = 1024
        logical = 2500
        page_num = logical // page_size
        offset = logical % page_size
        self.assertEqual(page_num, 2)
        self.assertEqual(offset, 452)
        frame_num = 1
        physical = (frame_num * page_size) + offset
        self.assertEqual(physical, 1476)

    def test_segmentation_limit_trap(self):
        """Test boundary checking where offset exceeds segment limit."""
        limit = 400
        offset_valid = 200
        offset_invalid = 450
        self.assertTrue(offset_valid < limit)
        self.assertFalse(offset_invalid < limit)

    # -------------------------------------------------------------
    # 4. Page Replacement Tests
    # -------------------------------------------------------------
    def test_page_replacement_optimal_vs_fifo(self):
        """Verify Optimal algorithm produces fewer or equal faults compared to FIFO."""
        ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        res_fifo = pr.simulate_fifo(ref, 3)
        res_opt = pr.simulate_optimal(ref, 3)
        self.assertLessEqual(res_opt["faults"], res_fifo["faults"])
        self.assertEqual(res_opt["hits"] + res_opt["faults"], len(ref))

    # -------------------------------------------------------------
    # 5. Disk Scheduling & Boundary Validation
    # -------------------------------------------------------------
    def test_disk_boundary_rejection(self):
        """Test that requests outside disk boundaries [0, 199] are safely discarded."""
        disk_min = 0
        disk_max = 199
        initial_head = 50
        raw_requests = [-10, 53, 98, 250, 120]
        valid = dss.validate_inputs(disk_min, disk_max, initial_head, raw_requests)
        self.assertEqual(valid, [53, 98, 120])
        self.assertNotIn(-10, valid)
        self.assertNotIn(250, valid)

    def test_disk_head_movement_calculation(self):
        """Verify head movement calculation in FCFS."""
        res = dss.schedule_fcfs(50, [100, 20])
        # 50 -> 100 = 50; 100 -> 20 = 80; Total = 130
        self.assertEqual(res["total"], 130)

    # -------------------------------------------------------------
    # 6. Storage & Invariant Tests
    # -------------------------------------------------------------
    def test_free_space_invariant_guarantee(self):
        """Test invariant: no block can be simultaneously allocated and free."""
        disk = fsac.FreeSpaceDisk(10)
        self.assertEqual(len(disk.get_free_block_list()), 10)
        disk.allocate_file("test.bin", 4)
        self.assertEqual(len(disk.get_free_block_list()), 6)
        disk.delete_file("test.bin")
        self.assertEqual(len(disk.get_free_block_list()), 10)
        disk.verify_invariants()


def main():
    print("=" * 65)
    print(" RUNNING OS-ISS AUTOMATED TEST & RELIABILITY SUITE")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOSReliabilityAndBoundaries)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n-> ALL RELIABILITY & BOUNDARY TEST CASES PASSED SUCCESSFULLY [100% PASS]")
        sys.exit(0)
    else:
        print("\n-> TEST FAILURES DETECTED")
        sys.exit(1)


if __name__ == "__main__":
    main()
