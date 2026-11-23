"""
Unit tests for Storage, Disk Scheduling, and File Allocation.
"""

import unittest
from core.storage import DiskScheduler, FileSystemSimulator
from core.exceptions import InvalidDiskRequestError, StorageAllocationError


class TestStorageModule(unittest.TestCase):

    def setUp(self):
        self.requests = [98, 183, 37, 122, 14, 124, 65, 67]
        self.initial_head = 53
        self.cylinders = 200

    def test_fcfs_disk_scheduling(self):
        res = DiskScheduler.fcfs(self.requests, self.initial_head, self.cylinders)
        self.assertEqual(res.algorithm, "FCFS")
        self.assertEqual(res.total_head_movement, 640)
        self.assertEqual(res.seek_sequence[0], 53)
        self.assertEqual(res.seek_sequence[1], 98)

    def test_sstf_disk_scheduling(self):
        res = DiskScheduler.sstf(self.requests, self.initial_head, self.cylinders)
        self.assertEqual(res.algorithm, "SSTF")
        self.assertEqual(res.total_head_movement, 236)
        # SSTF total seek must be significantly less than FCFS
        self.assertLess(res.total_head_movement, 640)

    def test_scan_and_look(self):
        res_scan = DiskScheduler.scan(self.requests, self.initial_head, self.cylinders, direction="right")
        self.assertEqual(res_scan.algorithm, "SCAN")
        self.assertIn(199, res_scan.seek_sequence)  # SCAN reaches cylinder boundary 199

        res_look = DiskScheduler.look(self.requests, self.initial_head, self.cylinders, direction="right")
        self.assertEqual(res_look.algorithm, "LOOK")
        self.assertNotIn(199, res_look.seek_sequence)  # LOOK reverses at max request (183)

    def test_c_scan_and_c_look(self):
        res_cscan = DiskScheduler.c_scan(self.requests, self.initial_head, self.cylinders, direction="right")
        self.assertEqual(res_cscan.algorithm, "C-SCAN")

        res_clook = DiskScheduler.c_look(self.requests, self.initial_head, self.cylinders, direction="right")
        self.assertEqual(res_clook.algorithm, "C-LOOK")

    def test_invalid_disk_requests(self):
        with self.assertRaises(InvalidDiskRequestError):
            DiskScheduler.fcfs([], 50, 200)
        with self.assertRaises(InvalidDiskRequestError):
            DiskScheduler.fcfs([50, 250], 50, 200)  # 250 >= 200
        with self.assertRaises(InvalidDiskRequestError):
            DiskScheduler.fcfs([50], -5, 200)

    def test_file_system_allocation(self):
        fs = FileSystemSimulator(total_blocks=16)
        self.assertEqual(fs.get_free_block_count(), 16)

        # Contiguous allocation
        f1 = fs.allocate_contiguous("f1.txt", 4)
        self.assertEqual(f1.allocated_blocks, [0, 1, 2, 3])
        self.assertEqual(fs.get_free_block_count(), 12)

        # Linked allocation
        f2 = fs.allocate_linked("f2.txt", 3)
        self.assertEqual(f2.allocated_blocks, [4, 5, 6])
        self.assertEqual(fs.get_free_block_count(), 9)

        # Indexed allocation (requires 1 index block + 2 data blocks)
        f3 = fs.allocate_indexed("f3.txt", 2)
        self.assertEqual(f3.index_block, 7)
        self.assertEqual(f3.allocated_blocks, [8, 9])
        self.assertEqual(fs.get_free_block_count(), 6)

        # Deletion
        fs.delete_file("f1.txt")
        self.assertEqual(fs.get_free_block_count(), 10)

    def test_file_system_errors(self):
        fs = FileSystemSimulator(total_blocks=5)
        fs.allocate_contiguous("f1.txt", 4)
        with self.assertRaises(StorageAllocationError):
            fs.allocate_contiguous("f1.txt", 1)  # Duplicate name
        with self.assertRaises(StorageAllocationError):
            fs.allocate_contiguous("overflow.txt", 3)  # Only 1 block left


if __name__ == "__main__":
    unittest.main()
