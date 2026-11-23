"""
Comprehensive Benchmark Runner for OS Simulator.
Executes multi-algorithm comparisons across standardized workloads.
Exports results to console, Markdown reports, and CSV files.
"""

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import csv
from typing import Dict, Any, List

from core.scheduler import CPUScheduler, Process, ScheduleResult
from core.memory import ContiguousMemoryManager, PageReplacementSimulator
from core.deadlock import BankersAlgorithm, DeadlockDetector
from core.storage import DiskScheduler, FileSystemSimulator
from core.logger import get_logger

logger = get_logger()


def load_json(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


class BenchmarkRunner:
    """Orchestrates comprehensive multi-algorithm benchmarking."""

    def __init__(self, sample_dir: str = "sample_inputs", output_dir: str = "output/reports"):
        self.sample_dir = sample_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run_cpu_benchmarks(self) -> List[ScheduleResult]:
        workload = load_json(os.path.join(self.sample_dir, "cpu_workload.json"))
        procs = [
            Process(
                pid=p["pid"],
                arrival_time=p["arrival_time"],
                burst_time=p["burst_time"],
                priority=p.get("priority", 0)
            )
            for p in workload["processes"]
        ]

        results = [
            CPUScheduler.fcfs(procs),
            CPUScheduler.sjf_non_preemptive(procs),
            CPUScheduler.srtf_preemptive(procs),
            CPUScheduler.priority_non_preemptive(procs),
            CPUScheduler.priority_preemptive(procs),
        ]

        for q in workload.get("round_robin_quantums", [2, 4]):
            results.append(CPUScheduler.round_robin(procs, quantum=q))

        # Save to CSV
        csv_path = os.path.join(self.output_dir, "cpu_scheduling_comparison.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Algorithm", "Avg_TAT", "Avg_WT", "Avg_RT", "CPU_Utilization_%", "Throughput"])
            for r in results:
                writer.writerow([
                    r.algorithm,
                    f"{r.avg_turnaround_time:.2f}",
                    f"{r.avg_waiting_time:.2f}",
                    f"{r.avg_response_time:.2f}",
                    f"{r.cpu_utilization:.2f}",
                    f"{r.throughput:.4f}"
                ])

        return results

    def run_memory_benchmarks(self) -> Dict[str, Any]:
        workload = load_json(os.path.join(self.sample_dir, "memory_workload.json"))
        c_workload = workload["contiguous_allocation"]
        block_sizes = c_workload["block_sizes_kb"]
        requests = [(r["pid"], r["size_kb"]) for r in c_workload["process_requests"]]

        manager = ContiguousMemoryManager(block_sizes)
        contiguous_results = [
            manager.allocate("First-Fit", requests),
            manager.allocate("Best-Fit", requests),
            manager.allocate("Worst-Fit", requests),
        ]

        p_workload = workload["page_replacement"]
        ref_string = p_workload["reference_string"]
        page_results = {}

        for frames in p_workload["test_frame_capacities"]:
            sim = PageReplacementSimulator(num_frames=frames)
            page_results[frames] = {
                "FIFO": sim.fifo(ref_string),
                "LRU": sim.lru(ref_string),
                "Optimal": sim.optimal(ref_string),
                "LFU": sim.lfu(ref_string),
            }

        return {
            "contiguous": contiguous_results,
            "page_replacement": page_results
        }

    def run_deadlock_benchmarks(self) -> Dict[str, Any]:
        workload = load_json(os.path.join(self.sample_dir, "deadlock_workload.json"))
        b_state = workload["bankers_state"]

        banker = BankersAlgorithm(
            resource_names=b_state["resources"],
            available=b_state["available"],
            max_claim=b_state["max_claim"],
            allocation=b_state["allocation"]
        )
        initial_safety = banker.is_safe_state()

        request_outcomes = []
        for req_item in b_state["sample_requests"]:
            pid = req_item["pid"]
            req = req_item["request"]
            res = banker.request_resources(pid, req)
            request_outcomes.append({
                "pid": pid,
                "request": req,
                "granted": res.granted,
                "message": res.message
            })

        wfg_cases = workload["wait_for_graph_cases"]
        wfg_results = {}
        for case_name, adj in wfg_cases.items():
            detector = DeadlockDetector(adj)
            wfg_results[case_name] = detector.detect_cycles()

        return {
            "initial_safety": initial_safety,
            "request_outcomes": request_outcomes,
            "wfg_results": wfg_results
        }

    def run_storage_benchmarks(self) -> Dict[str, Any]:
        workload = load_json(os.path.join(self.sample_dir, "storage_workload.json"))
        d_workload = workload["disk_scheduling"]
        reqs = d_workload["request_queue"]
        head = d_workload["initial_head_position"]
        cylinders = d_workload["total_cylinders"]
        direction = d_workload["direction"]

        disk_results = [
            DiskScheduler.fcfs(reqs, head, cylinders),
            DiskScheduler.sstf(reqs, head, cylinders),
            DiskScheduler.scan(reqs, head, cylinders, direction),
            DiskScheduler.c_scan(reqs, head, cylinders, direction),
            DiskScheduler.look(reqs, head, cylinders, direction),
            DiskScheduler.c_look(reqs, head, cylinders, direction),
        ]

        # File system simulation
        f_workload = workload["file_allocation"]
        fs = FileSystemSimulator(total_blocks=f_workload["total_disk_blocks"])
        fs_events = []
        for op in f_workload["operations"]:
            try:
                if op["op"] == "create":
                    alloc_type = op["type"]
                    name = op["name"]
                    blks = op["blocks"]
                    if alloc_type == "contiguous":
                        meta = fs.allocate_contiguous(name, blks)
                    elif alloc_type == "linked":
                        meta = fs.allocate_linked(name, blks)
                    else:
                        meta = fs.allocate_indexed(name, blks)
                    fs_events.append(f"CREATE {alloc_type.upper()} '{name}' ({blks} blks) -> OK {meta.allocated_blocks}")
                elif op["op"] == "delete":
                    fs.delete_file(op["name"])
                    fs_events.append(f"DELETE '{op['name']}' -> OK (blocks freed)")
            except Exception as e:
                fs_events.append(f"OP FAILED ({op}): {str(e)}")

        return {
            "disk_results": disk_results,
            "fs_events": fs_events,
            "free_blocks_remaining": fs.get_free_block_count()
        }

    def generate_markdown_report(self) -> str:
        cpu_res = self.run_cpu_benchmarks()
        mem_res = self.run_memory_benchmarks()
        dl_res = self.run_deadlock_benchmarks()
        st_res = self.run_storage_benchmarks()

        report_lines = [
            "# SIM-OS Comprehensive Benchmark & Performance Report",
            "**Author:** Varun Chauhan (2401010276)  ",
            "**System:** Integrated Python-and-Bash OS Resource Management Simulator\n",
            "---",
            "## 1. CPU Scheduling Performance Comparison\n",
            "| Algorithm | Avg Turnaround Time (TAT) | Avg Waiting Time (WT) | Avg Response Time (RT) | CPU Utilization (%) | Throughput (procs/unit) |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |"
        ]

        for r in cpu_res:
            report_lines.append(
                f"| **{r.algorithm}** | {r.avg_turnaround_time:.2f} | {r.avg_waiting_time:.2f} | {r.avg_response_time:.2f} | {r.cpu_utilization:.1f}% | {r.throughput:.4f} |"
            )

        report_lines.extend([
            "\n### Key Analytical Insights:",
            "- **SJF / SRTF:** Achieves the lowest Average Waiting Time due to optimal scheduling of short jobs.",
            "- **Round Robin:** Balances response time effectively across processes; lower time quantums provide rapid initial responsiveness at the expense of context-switch overhead.",
            "- **Preemptive Priority:** Swiftly pre-empts low-priority background work in favor of high-priority critical tasks.\n",
            "---",
            "## 2. Memory Management Analysis\n",
            "### Contiguous Allocation (Dynamic Partitioning)\n",
            "| Algorithm | Allocated Processes | Unallocated Processes | Internal Frag (KB) | External Frag (KB) | Memory Utilization |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |"
        ])

        for cr in mem_res["contiguous"]:
            alloc_str = ", ".join(f"{pid}({sz}KB)" for pid, sz, _ in cr.allocated_processes) or "None"
            unalloc_str = ", ".join(f"{pid}({sz}KB)" for pid, sz in cr.unallocated_processes) or "None"
            report_lines.append(
                f"| **{cr.algorithm}** | {alloc_str} | {unalloc_str} | {cr.total_internal_fragmentation} KB | {cr.total_external_fragmentation} KB | {cr.utilization_percentage:.1f}% |"
            )

        report_lines.extend([
            "\n### Virtual Memory Page Replacement Comparison\n",
            "| Frame Capacity | FIFO Faults | LRU Faults | Optimal Faults | LFU Faults |",
            "| :---: | :---: | :---: | :---: | :---: |"
        ])

        for frames, algos in mem_res["page_replacement"].items():
            report_lines.append(
                f"| **{frames} Frames** | {algos['FIFO'].total_page_faults} ({algos['FIFO'].hit_ratio:.1%} hits) | {algos['LRU'].total_page_faults} ({algos['LRU'].hit_ratio:.1%} hits) | {algos['Optimal'].total_page_faults} ({algos['Optimal'].hit_ratio:.1%} hits) | {algos['LFU'].total_page_faults} ({algos['LFU'].hit_ratio:.1%} hits) |"
            )

        report_lines.extend([
            "\n---",
            "## 3. Concurrency & Deadlock Avoidance Analysis\n",
            f"**Initial Banker's System State:** {'SAFE (Safe Sequence: ' + ' -> '.join(dl_res['initial_safety'].safe_sequence) + ')' if dl_res['initial_safety'].is_safe else 'UNSAFE'}\n",
            "### Sample Resource Requests Tested:\n"
        ])

        for outcome in dl_res["request_outcomes"]:
            req_str = ", ".join(f"{k}={v}" for k, v in outcome["request"].items())
            status = "GRANTED" if outcome["granted"] else "DENIED"
            report_lines.append(f"- **{outcome['pid']} requests ({req_str}):** [{status}] {outcome['message']}")

        report_lines.extend([
            "\n### Wait-For Graph (WFG) Cycle Detection:\n"
        ])

        for case, res in dl_res["wfg_results"].items():
            state = f"DEADLOCK DETECTED! Cycles: {res.detected_cycles}" if res.deadlock_detected else "NO DEADLOCK (Acyclic)"
            report_lines.append(f"- Case `{case}`: **{state}**")

        report_lines.extend([
            "\n---",
            "## 4. Disk Arm Scheduling & File System Storage\n",
            "| Disk Scheduling Algorithm | Total Head Movement (Cylinders) | Average Seek Length |",
            "| :--- | :---: | :---: |"
        ])

        for dr in st_res["disk_results"]:
            report_lines.append(f"| **{dr.algorithm}** | {dr.total_head_movement} | {dr.average_seek_length:.2f} cylinders |")

        report_lines.extend([
            "\n### File Allocation Log & Block Lifecycle:\n"
        ])
        for event in st_res["fs_events"]:
            report_lines.append(f"- `{event}`")
        report_lines.append(f"\n**Remaining Free Blocks:** {st_res['free_blocks_remaining']} / 32")

        report_content = "\n".join(report_lines)
        report_file = os.path.join(self.output_dir, "benchmark_summary.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        return report_content


def run_all_benchmarks():
    runner = BenchmarkRunner()
    content = runner.generate_markdown_report()
    print(content)
