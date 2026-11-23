"""
CPU Process Scheduling Module.
Simulates FCFS, SJF, SRTF, Priority (Preemptive & Non-Preemptive), and Round Robin.
Generates comprehensive performance metrics and textual Gantt charts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import copy

from core.exceptions import InvalidProcessError, InvalidQuantumError
from core.logger import get_logger

logger = get_logger()


@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0  # Lower integer = higher priority by convention

    # Dynamic execution tracking
    remaining_time: int = 0
    start_time: Optional[int] = None
    completion_time: int = 0
    turnaround_time: int = 0
    waiting_time: int = 0
    response_time: int = 0

    def __post_init__(self):
        if self.arrival_time < 0:
            raise InvalidProcessError(f"Process {self.pid}: Arrival time cannot be negative ({self.arrival_time}).")
        if self.burst_time <= 0:
            raise InvalidProcessError(f"Process {self.pid}: Burst time must be strictly positive ({self.burst_time}).")
        self.remaining_time = self.burst_time


@dataclass
class ScheduleResult:
    algorithm: str
    processes: List[Process]
    gantt_chart: List[Tuple[str, int, int]]  # (pid, start_time, end_time)
    avg_turnaround_time: float = 0.0
    avg_waiting_time: float = 0.0
    avg_response_time: float = 0.0
    cpu_utilization: float = 0.0
    throughput: float = 0.0
    total_time: int = 0
    idle_time: int = 0

    def calculate_metrics(self):
        if not self.processes:
            return

        n = len(self.processes)
        self.avg_turnaround_time = sum(p.turnaround_time for p in self.processes) / n
        self.avg_waiting_time = sum(p.waiting_time for p in self.processes) / n
        self.avg_response_time = sum(p.response_time for p in self.processes) / n

        if self.total_time > 0:
            busy_time = self.total_time - self.idle_time
            self.cpu_utilization = (busy_time / self.total_time) * 100.0
            self.throughput = n / self.total_time
        else:
            self.cpu_utilization = 100.0
            self.throughput = 0.0

    def render_gantt_chart(self) -> str:
        if not self.gantt_chart:
            return "No execution logged."

        # Merge adjacent identical PIDs
        merged = []
        for pid, s, e in self.gantt_chart:
            if s == e:
                continue
            if merged and merged[-1][0] == pid and merged[-1][2] == s:
                merged[-1] = (pid, merged[-1][1], e)
            else:
                merged.append((pid, s, e))

        # Top bar
        top = "+"
        middle = "|"
        bottom = "+"
        timeline = str(merged[0][1])

        for pid, s, e in merged:
            label = f" {pid} "
            width = max(len(label), (e - s) * 2)
            padded = label.center(width)
            top += "-" * width + "+"
            middle += padded + "|"
            bottom += "-" * width + "+"
            end_str = str(e)
            timeline += " " * (width + 1 - len(end_str)) + end_str

        return f"{top}\n{middle}\n{bottom}\n{timeline}"


class CPUScheduler:
    """CPU Scheduling simulation suite."""

    @staticmethod
    def _validate_workload(processes: List[Process]):
        if not processes:
            raise InvalidProcessError("Process workload list cannot be empty.")

    @staticmethod
    def fcfs(processes: List[Process]) -> ScheduleResult:
        """First-Come, First-Served (FCFS) Scheduling."""
        CPUScheduler._validate_workload(processes)
        procs = sorted([copy.deepcopy(p) for p in processes], key=lambda x: (x.arrival_time, x.pid))
        
        current_time = 0
        idle_time = 0
        gantt: List[Tuple[str, int, int]] = []

        for p in procs:
            if current_time < p.arrival_time:
                idle_start = current_time
                idle_time += p.arrival_time - current_time
                current_time = p.arrival_time
                gantt.append(("IDLE", idle_start, current_time))

            p.start_time = current_time
            p.response_time = p.start_time - p.arrival_time
            current_time += p.burst_time
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            p.remaining_time = 0
            gantt.append((p.pid, p.start_time, p.completion_time))

        res = ScheduleResult("FCFS", procs, gantt, total_time=current_time, idle_time=idle_time)
        res.calculate_metrics()
        logger.info(f"FCFS executed: {len(procs)} processes, Total Time: {current_time}, Avg WT: {res.avg_waiting_time:.2f}")
        return res

    @staticmethod
    def sjf_non_preemptive(processes: List[Process]) -> ScheduleResult:
        """Shortest Job First (Non-Preemptive)."""
        CPUScheduler._validate_workload(processes)
        pending = [copy.deepcopy(p) for p in processes]
        completed: List[Process] = []
        gantt: List[Tuple[str, int, int]] = []

        current_time = 0
        idle_time = 0

        while pending:
            available = [p for p in pending if p.arrival_time <= current_time]
            if not available:
                # Advance to next arrival
                next_arr = min(p.arrival_time for p in pending)
                gantt.append(("IDLE", current_time, next_arr))
                idle_time += next_arr - current_time
                current_time = next_arr
                available = [p for p in pending if p.arrival_time <= current_time]

            # Pick shortest burst, tie breaker: arrival time, then pid
            chosen = min(available, key=lambda x: (x.burst_time, x.arrival_time, x.pid))
            pending.remove(chosen)

            chosen.start_time = current_time
            chosen.response_time = chosen.start_time - chosen.arrival_time
            current_time += chosen.burst_time
            chosen.completion_time = current_time
            chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
            chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
            chosen.remaining_time = 0

            gantt.append((chosen.pid, chosen.start_time, chosen.completion_time))
            completed.append(chosen)

        # Sort back by original PID order or completion
        completed.sort(key=lambda x: x.pid)
        res = ScheduleResult("SJF (Non-Preemptive)", completed, gantt, total_time=current_time, idle_time=idle_time)
        res.calculate_metrics()
        logger.info(f"SJF Non-Preemptive executed: Avg WT: {res.avg_waiting_time:.2f}")
        return res

    @staticmethod
    def srtf_preemptive(processes: List[Process]) -> ScheduleResult:
        """Shortest Remaining Time First (Preemptive SJF)."""
        CPUScheduler._validate_workload(processes)
        procs = [copy.deepcopy(p) for p in processes]
        n = len(procs)
        proc_map = {p.pid: p for p in procs}

        current_time = 0
        completed_count = 0
        idle_time = 0
        gantt: List[Tuple[str, int, int]] = []
        last_pid = None

        while completed_count < n:
            available = [p for p in procs if p.arrival_time <= current_time and p.remaining_time > 0]
            if not available:
                if last_pid != "IDLE":
                    gantt.append(("IDLE", current_time, current_time + 1))
                else:
                    gantt[-1] = ("IDLE", gantt[-1][1], current_time + 1)
                idle_time += 1
                current_time += 1
                last_pid = "IDLE"
                continue

            chosen = min(available, key=lambda x: (x.remaining_time, x.arrival_time, x.pid))

            if chosen.start_time is None:
                chosen.start_time = current_time
                chosen.response_time = current_time - chosen.arrival_time

            if last_pid == chosen.pid:
                gantt[-1] = (chosen.pid, gantt[-1][1], current_time + 1)
            else:
                gantt.append((chosen.pid, current_time, current_time + 1))

            chosen.remaining_time -= 1
            current_time += 1
            last_pid = chosen.pid

            if chosen.remaining_time == 0:
                chosen.completion_time = current_time
                chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
                chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
                completed_count += 1

        procs.sort(key=lambda x: x.pid)
        res = ScheduleResult("SRTF (Preemptive SJF)", procs, gantt, total_time=current_time, idle_time=idle_time)
        res.calculate_metrics()
        logger.info(f"SRTF executed: Avg WT: {res.avg_waiting_time:.2f}")
        return res

    @staticmethod
    def priority_non_preemptive(processes: List[Process]) -> ScheduleResult:
        """Priority Scheduling (Non-Preemptive). Lower priority number = Higher priority."""
        CPUScheduler._validate_workload(processes)
        pending = [copy.deepcopy(p) for p in processes]
        completed: List[Process] = []
        gantt: List[Tuple[str, int, int]] = []

        current_time = 0
        idle_time = 0

        while pending:
            available = [p for p in pending if p.arrival_time <= current_time]
            if not available:
                next_arr = min(p.arrival_time for p in pending)
                gantt.append(("IDLE", current_time, next_arr))
                idle_time += next_arr - current_time
                current_time = next_arr
                available = [p for p in pending if p.arrival_time <= current_time]

            chosen = min(available, key=lambda x: (x.priority, x.arrival_time, x.pid))
            pending.remove(chosen)

            chosen.start_time = current_time
            chosen.response_time = chosen.start_time - chosen.arrival_time
            current_time += chosen.burst_time
            chosen.completion_time = current_time
            chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
            chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
            chosen.remaining_time = 0

            gantt.append((chosen.pid, chosen.start_time, chosen.completion_time))
            completed.append(chosen)

        completed.sort(key=lambda x: x.pid)
        res = ScheduleResult("Priority (Non-Preemptive)", completed, gantt, total_time=current_time, idle_time=idle_time)
        res.calculate_metrics()
        logger.info(f"Priority Non-Preemptive executed: Avg WT: {res.avg_waiting_time:.2f}")
        return res

    @staticmethod
    def priority_preemptive(processes: List[Process]) -> ScheduleResult:
        """Priority Scheduling (Preemptive)."""
        CPUScheduler._validate_workload(processes)
        procs = [copy.deepcopy(p) for p in processes]
        n = len(procs)

        current_time = 0
        completed_count = 0
        idle_time = 0
        gantt: List[Tuple[str, int, int]] = []
        last_pid = None

        while completed_count < n:
            available = [p for p in procs if p.arrival_time <= current_time and p.remaining_time > 0]
            if not available:
                if last_pid != "IDLE":
                    gantt.append(("IDLE", current_time, current_time + 1))
                else:
                    gantt[-1] = ("IDLE", gantt[-1][1], current_time + 1)
                idle_time += 1
                current_time += 1
                last_pid = "IDLE"
                continue

            chosen = min(available, key=lambda x: (x.priority, x.arrival_time, x.pid))

            if chosen.start_time is None:
                chosen.start_time = current_time
                chosen.response_time = current_time - chosen.arrival_time

            if last_pid == chosen.pid:
                gantt[-1] = (chosen.pid, gantt[-1][1], current_time + 1)
            else:
                gantt.append((chosen.pid, current_time, current_time + 1))

            chosen.remaining_time -= 1
            current_time += 1
            last_pid = chosen.pid

            if chosen.remaining_time == 0:
                chosen.completion_time = current_time
                chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
                chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
                completed_count += 1

        procs.sort(key=lambda x: x.pid)
        res = ScheduleResult("Priority (Preemptive)", procs, gantt, total_time=current_time, idle_time=idle_time)
        res.calculate_metrics()
        logger.info(f"Priority Preemptive executed: Avg WT: {res.avg_waiting_time:.2f}")
        return res

    @staticmethod
    def round_robin(processes: List[Process], quantum: int) -> ScheduleResult:
        """Round Robin Scheduling with configurable time quantum."""
        CPUScheduler._validate_workload(processes)
        if quantum <= 0:
            raise InvalidQuantumError(f"Round Robin quantum must be positive integer ({quantum}).")

        procs = sorted([copy.deepcopy(p) for p in processes], key=lambda x: (x.arrival_time, x.pid))
        proc_dict = {p.pid: p for p in procs}

        current_time = 0
        idle_time = 0
        gantt: List[Tuple[str, int, int]] = []
        ready_queue: List[Process] = []
        visited = set()

        # Add initial arrivals
        for p in procs:
            if p.arrival_time <= current_time and p.pid not in visited:
                ready_queue.append(p)
                visited.add(p.pid)

        while ready_queue or len(visited) < len(procs):
            if not ready_queue:
                # Find next arriving process
                unvisited = [p for p in procs if p.pid not in visited]
                next_arr = min(p.arrival_time for p in unvisited)
                gantt.append(("IDLE", current_time, next_arr))
                idle_time += next_arr - current_time
                current_time = next_arr

                for p in unvisited:
                    if p.arrival_time <= current_time and p.pid not in visited:
                        ready_queue.append(p)
                        visited.add(p.pid)
                continue

            current = ready_queue.pop(0)

            if current.start_time is None:
                current.start_time = current_time
                current.response_time = current_time - current.arrival_time

            exec_time = min(quantum, current.remaining_time)
            start_slice = current_time
            current_time += exec_time
            current.remaining_time -= exec_time

            gantt.append((current.pid, start_slice, current_time))

            # Add newly arrived processes while this slice was executing
            for p in procs:
                if p.arrival_time <= current_time and p.pid not in visited:
                    ready_queue.append(p)
                    visited.add(p.pid)

            if current.remaining_time > 0:
                ready_queue.append(current)
            else:
                current.completion_time = current_time
                current.turnaround_time = current.completion_time - current.arrival_time
                current.waiting_time = current.turnaround_time - current.burst_time

        procs.sort(key=lambda x: x.pid)
        res = ScheduleResult(f"Round Robin (Q={quantum})", procs, gantt, total_time=current_time, idle_time=idle_time)
        res.calculate_metrics()
        logger.info(f"Round Robin (Q={quantum}) executed: Avg WT: {res.avg_waiting_time:.2f}")
        return res
