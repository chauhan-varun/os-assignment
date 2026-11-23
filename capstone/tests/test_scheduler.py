"""
Unit tests for CPU Scheduling Module.
Tests valid scenarios, boundary conditions, and invalid input exception handling.
"""

import unittest
from core.scheduler import CPUScheduler, Process
from core.exceptions import InvalidProcessError, InvalidQuantumError


class TestCPUScheduler(unittest.TestCase):

    def setUp(self):
        self.standard_processes = [
            Process("P1", arrival_time=0, burst_time=5, priority=2),
            Process("P2", arrival_time=1, burst_time=3, priority=1),
            Process("P3", arrival_time=2, burst_time=8, priority=3),
        ]

    # --- Valid Workload Tests ---

    def test_fcfs_valid(self):
        res = CPUScheduler.fcfs(self.standard_processes)
        self.assertEqual(res.algorithm, "FCFS")
        self.assertEqual(len(res.processes), 3)
        # P1 finishes at 5, P2 at 8, P3 at 16
        p_map = {p.pid: p for p in res.processes}
        self.assertEqual(p_map["P1"].completion_time, 5)
        self.assertEqual(p_map["P2"].completion_time, 8)
        self.assertEqual(p_map["P3"].completion_time, 16)
        self.assertAlmostEqual(res.avg_waiting_time, (0 + 4 + 6) / 3, places=2)

    def test_sjf_non_preemptive_valid(self):
        res = CPUScheduler.sjf_non_preemptive(self.standard_processes)
        p_map = {p.pid: p for p in res.processes}
        self.assertEqual(p_map["P1"].completion_time, 5)
        # At time 5, P2 (burst 3) runs before P3 (burst 8)
        self.assertEqual(p_map["P2"].completion_time, 8)
        self.assertEqual(p_map["P3"].completion_time, 16)

    def test_srtf_preemptive_valid(self):
        # P1 (0..1), P2 arrives with burst 3 < remaining 4, so P2 preempts P1
        res = CPUScheduler.srtf_preemptive(self.standard_processes)
        p_map = {p.pid: p for p in res.processes}
        self.assertEqual(p_map["P2"].completion_time, 4)
        self.assertEqual(p_map["P1"].completion_time, 8)
        self.assertEqual(p_map["P3"].completion_time, 16)

    def test_priority_scheduling(self):
        res_np = CPUScheduler.priority_non_preemptive(self.standard_processes)
        p_map = {p.pid: p for p in res_np.processes}
        # P1 completes at 5, then P2 (prio 1) executes before P3 (prio 3)
        self.assertEqual(p_map["P2"].completion_time, 8)

        res_pre = CPUScheduler.priority_preemptive(self.standard_processes)
        p_map_pre = {p.pid: p for p in res_pre.processes}
        # P2 preempts P1 at t=1 because priority 1 < 2
        self.assertEqual(p_map_pre["P2"].completion_time, 4)

    def test_round_robin_valid(self):
        res = CPUScheduler.round_robin(self.standard_processes, quantum=2)
        self.assertEqual(len(res.processes), 3)
        self.assertGreater(res.cpu_utilization, 0)
        # Invariants: TAT = CT - AT, WT = TAT - BT
        for p in res.processes:
            self.assertEqual(p.turnaround_time, p.completion_time - p.arrival_time)
            self.assertEqual(p.waiting_time, p.turnaround_time - p.burst_time)

    # --- Boundary & Edge Cases ---

    def test_single_process(self):
        procs = [Process("Solo", arrival_time=5, burst_time=10)]
        res = CPUScheduler.fcfs(procs)
        self.assertEqual(res.processes[0].start_time, 5)
        self.assertEqual(res.processes[0].completion_time, 15)
        self.assertEqual(res.processes[0].waiting_time, 0)
        self.assertEqual(res.idle_time, 5)

    def test_cpu_idle_gap(self):
        procs = [
            Process("P1", arrival_time=0, burst_time=2),
            Process("P2", arrival_time=10, burst_time=3),
        ]
        res = CPUScheduler.fcfs(procs)
        self.assertEqual(res.idle_time, 8)
        self.assertEqual(res.total_time, 13)

    # --- Invalid Input Handling ---

    def test_empty_workload(self):
        with self.assertRaises(InvalidProcessError):
            CPUScheduler.fcfs([])

    def test_negative_arrival_time(self):
        with self.assertRaises(InvalidProcessError):
            Process("Err1", arrival_time=-2, burst_time=5)

    def test_zero_or_negative_burst_time(self):
        with self.assertRaises(InvalidProcessError):
            Process("Err2", arrival_time=0, burst_time=0)
        with self.assertRaises(InvalidProcessError):
            Process("Err3", arrival_time=0, burst_time=-4)

    def test_invalid_round_robin_quantum(self):
        with self.assertRaises(InvalidQuantumError):
            CPUScheduler.round_robin(self.standard_processes, quantum=0)
        with self.assertRaises(InvalidQuantumError):
            CPUScheduler.round_robin(self.standard_processes, quantum=-3)


if __name__ == "__main__":
    unittest.main()
