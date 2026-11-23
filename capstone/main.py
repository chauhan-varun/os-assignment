#!/usr/bin/env python3
"""
SIM-OS: Integrated Operating System Resource Management Simulator.
Author: Varun Chauhan (Roll No: 2401010276)
Course: B.Tech CSE Sec B - Operating Systems Capstone

Integrates:
- CPU Process Scheduling (FCFS, SJF, SRTF, Priority, Round Robin)
- Memory Management (Contiguous Partitioning & Virtual Memory Page Replacement)
- Deadlock Handling (Banker's Algorithm & Wait-For Graph Cycle Detection)
- Storage Management (Disk Arm Scheduling & File Block Allocation)
- Host Linux OS Kernel Diagnostics
- Comprehensive Analytical Benchmarking & Visualization
"""

import sys
import os
import argparse
import subprocess
import shutil

# Ensure local capstone packages can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.scheduler import CPUScheduler, Process
from core.memory import ContiguousMemoryManager, PageReplacementSimulator
from core.deadlock import BankersAlgorithm, DeadlockDetector
from core.storage import DiskScheduler, FileSystemSimulator
from core.logger import setup_logger, get_logger
from analysis.benchmark_runner import BenchmarkRunner
from analysis.visualizer import generate_all_visualizations

# Setup logging
setup_logger(log_file="logs/sim_os.log")
logger = get_logger()

# ANSI Color codes
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RED = "\033[31m"
RESET = "\033[0m"


def print_banner():
    banner = f"""
{BLUE}{BOLD}========================================================================{RESET}
{CYAN}{BOLD}   SIM-OS: INTEGRATED OPERATING SYSTEM RESOURCE MANAGEMENT SIMULATOR   {RESET}
{BLUE}{BOLD}========================================================================{RESET}
{YELLOW}Student Name :{RESET} Varun Chauhan          {YELLOW}Roll Number :{RESET} 2401010276
{YELLOW}Course       :{RESET} B.Tech CSE Sec B        {YELLOW}Subject     :{RESET} OS Capstone Project
{BLUE}========================================================================{RESET}
"""
    print(banner)


def menu_cpu_scheduling():
    print(f"\n{GREEN}{BOLD}--- [1] CPU Process Scheduling Simulator ---{RESET}")
    print("1. Run Standard Workload Benchmark (FCFS, SJF, SRTF, Priority, RR)")
    print("2. Enter Custom Process Workload Interactively")
    print("3. Back to Main Menu")

    choice = input(f"\n{YELLOW}Select option [1-3]: {RESET}").strip()
    if choice == "1":
        runner = BenchmarkRunner()
        results = runner.run_cpu_benchmarks()
        print(f"\n{BOLD}{'Algorithm':<26} {'Avg TAT':<10} {'Avg WT':<10} {'Avg RT':<10} {'CPU Util':<10} {'Throughput'}{RESET}")
        print("-" * 75)
        for r in results:
            print(f"{r.algorithm:<26} {r.avg_turnaround_time:<10.2f} {r.avg_waiting_time:<10.2f} {r.avg_response_time:<10.2f} {r.cpu_utilization:<9.1f}% {r.throughput:<.4f}")

        print(f"\n{CYAN}{BOLD}Sample Gantt Chart (Round Robin Q=2):{RESET}")
        rr_res = [r for r in results if "Round Robin (Q=2)" in r.algorithm]
        if rr_res:
            print(rr_res[0].render_gantt_chart())

    elif choice == "2":
        try:
            n = int(input("Enter number of processes: "))
            procs = []
            for i in range(n):
                pid = input(f"PID for process {i+1} [e.g. P{i+1}]: ") or f"P{i+1}"
                at = int(input(f"  Arrival Time for {pid}: "))
                bt = int(input(f"  Burst Time for {pid}: "))
                prio = int(input(f"  Priority for {pid} (lower = higher priority): "))
                procs.append(Process(pid, at, bt, prio))

            print("\nSelect Algorithm:")
            print("1. FCFS\n2. SJF (Non-preemptive)\n3. SRTF (Preemptive SJF)\n4. Priority (Preemptive)\n5. Round Robin")
            algo_opt = input("Choice: ").strip()

            if algo_opt == "1":
                res = CPUScheduler.fcfs(procs)
            elif algo_opt == "2":
                res = CPUScheduler.sjf_non_preemptive(procs)
            elif algo_opt == "3":
                res = CPUScheduler.srtf_preemptive(procs)
            elif algo_opt == "4":
                res = CPUScheduler.priority_preemptive(procs)
            elif algo_opt == "5":
                q = int(input("Enter time quantum: "))
                res = CPUScheduler.round_robin(procs, q)
            else:
                print("Invalid algorithm option.")
                return

            print(f"\n{BOLD}Execution Metrics for {res.algorithm}:{RESET}")
            print(f"Avg Turnaround Time : {res.avg_turnaround_time:.2f}")
            print(f"Avg Waiting Time    : {res.avg_waiting_time:.2f}")
            print(f"CPU Utilization     : {res.cpu_utilization:.1f}%")
            print(f"\n{BOLD}Gantt Chart:{RESET}")
            print(res.render_gantt_chart())

        except Exception as e:
            print(f"{RED}[Error]: {e}{RESET}")


def menu_memory_management():
    print(f"\n{GREEN}{BOLD}--- [2] Memory Management Simulator ---{RESET}")
    print("1. Contiguous Dynamic Partition Allocation (First-Fit, Best-Fit, Worst-Fit)")
    print("2. Virtual Memory Page Replacement (FIFO, LRU, Optimal, LFU)")
    print("3. Back to Main Menu")

    choice = input(f"\n{YELLOW}Select option [1-3]: {RESET}").strip()
    if choice == "1":
        blocks = [100, 500, 200, 300, 600]
        reqs = [("P1", 212), ("P2", 417), ("P3", 112), ("P4", 426)]
        print(f"Simulating Initial Block Partitions: {blocks} KB")
        print(f"Process Requests: {reqs} KB\n")

        manager = ContiguousMemoryManager(blocks)
        for algo in ["First-Fit", "Best-Fit", "Worst-Fit"]:
            res = manager.allocate(algo, reqs)
            print(f"{BOLD}[{res.algorithm}]{RESET} Allocated: {len(res.allocated_processes)}, Unallocated: {len(res.unallocated_processes)}, Internal Frag: {res.total_internal_fragmentation} KB, Memory Util: {res.utilization_percentage:.1f}%")

    elif choice == "2":
        ref_str = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        frames = 3
        print(f"Page Reference String: {ref_str}")
        print(f"Physical Frames Capacity: {frames}\n")
        sim = PageReplacementSimulator(num_frames=frames)

        for name, fn in [("FIFO", sim.fifo), ("LRU", sim.lru), ("Optimal", sim.optimal), ("LFU", sim.lfu)]:
            res = fn(ref_str)
            print(f"{BOLD}{name:<8}{RESET} Page Faults: {res.total_page_faults:<3} Hits: {res.total_page_hits:<3} Hit Ratio: {res.hit_ratio:.1%}")


def menu_deadlock():
    print(f"\n{GREEN}{BOLD}--- [3] Concurrency & Deadlock Simulator ---{RESET}")
    print("1. Banker's Algorithm (Safety & Resource-Request Evaluation)")
    print("2. Wait-For Graph (WFG) Deadlock Cycle Detection")
    print("3. Back to Main Menu")

    choice = input(f"\n{YELLOW}Select option [1-3]: {RESET}").strip()
    if choice == "1":
        runner = BenchmarkRunner()
        dl_res = runner.run_deadlock_benchmarks()
        safety = dl_res["initial_safety"]
        print(f"Initial State Safe? : {BOLD}{'YES' if safety.is_safe else 'NO'}{RESET}")
        if safety.is_safe:
            print(f"Safe Sequence       : {' -> '.join(safety.safe_sequence)}")

        print("\nTesting Sample Resource Requests:")
        for o in dl_res["request_outcomes"]:
            print(f"  • {o['pid']} requesting {o['request']} -> {o['message']}")

    elif choice == "2":
        runner = BenchmarkRunner()
        dl_res = runner.run_deadlock_benchmarks()
        for case, res in dl_res["wfg_results"].items():
            status = f"{RED}DEADLOCK (Cycles: {res.detected_cycles}){RESET}" if res.deadlock_detected else f"{GREEN}DEADLOCK-FREE (Acyclic){RESET}"
            print(f"  • Case [{case}]: {status}")


def menu_storage():
    print(f"\n{GREEN}{BOLD}--- [4] Storage & Disk Scheduling Simulator ---{RESET}")
    print("1. Disk Arm Scheduling (FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK)")
    print("2. File System Block Allocation (Contiguous, Linked, Indexed)")
    print("3. Back to Main Menu")

    choice = input(f"\n{YELLOW}Select option [1-3]: {RESET}").strip()
    if choice == "1":
        runner = BenchmarkRunner()
        st_res = runner.run_storage_benchmarks()
        print(f"\n{BOLD}{'Algorithm':<12} {'Total Seek Movement':<22} {'Average Seek Length'}{RESET}")
        print("-" * 55)
        for dr in st_res["disk_results"]:
            print(f"{dr.algorithm:<12} {dr.total_head_movement:<22} {dr.average_seek_length:.2f} cylinders")

    elif choice == "2":
        runner = BenchmarkRunner()
        st_res = runner.run_storage_benchmarks()
        print(f"\n{BOLD}File System Lifecycle Simulation Log:{RESET}")
        for ev in st_res["fs_events"]:
            print(f"  • {ev}")
        print(f"\n{CYAN}Remaining Free Blocks: {st_res['free_blocks_remaining']} / 32{RESET}")


def menu_telemetry():
    print(f"\n{GREEN}{BOLD}--- [5] Host Linux Kernel Telemetry Probe ---{RESET}")
    subprocess.run(["bash", "bash/host_telemetry.sh"])


def menu_full_benchmark():
    print(f"\n{GREEN}{BOLD}--- [6] Running Full Benchmark Suite & Analytical Charts ---{RESET}")
    runner = BenchmarkRunner()
    report = runner.generate_markdown_report()
    print(report)
    print(f"\n{CYAN}Generating graphical comparison charts...{RESET}")
    generate_all_visualizations()
    print(f"{GREEN}✓ Benchmark report saved to: output/reports/benchmark_summary.md{RESET}")
    print(f"{GREEN}✓ Visual charts saved to: output/charts/{RESET}")


def menu_test_suite():
    print(f"\n{GREEN}{BOLD}--- [7] Running Automated Verification Test Suite ---{RESET}")
    if shutil.which("uv"):
        cmd = ["uv", "run", "python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]
    else:
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]
    subprocess.run(cmd)


def interactive_main():
    while True:
        print_banner()
        print(f"{BOLD}MAIN MENU:{RESET}")
        print("  1. CPU Scheduling Simulation")
        print("  2. Memory Management Simulation (Partitioning & Paging)")
        print("  3. Concurrency & Deadlock Simulation (Banker's & RAG)")
        print("  4. Storage & Disk Arm Scheduling Simulation")
        print("  5. Host Linux OS Telemetry Inspection (Bash Integration)")
        print("  6. Full Integrated System Benchmark & Analytical Charts")
        print("  7. Run Test Suite (Boundary, Error & Verification Tests)")
        print("  8. Exit")

        opt = input(f"\n{YELLOW}Enter option [1-8]: {RESET}").strip()
        if opt == "1":
            menu_cpu_scheduling()
        elif opt == "2":
            menu_memory_management()
        elif opt == "3":
            menu_deadlock()
        elif opt == "4":
            menu_storage()
        elif opt == "5":
            menu_telemetry()
        elif opt == "6":
            menu_full_benchmark()
        elif opt == "7":
            menu_test_suite()
        elif opt == "8":
            print(f"\n{CYAN}Thank you for evaluating SIM-OS! Exiting.{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}Invalid selection. Please choose an option from 1 to 8.{RESET}")

        input(f"\n{YELLOW}Press Enter to return to main menu...{RESET}")


def main():
    parser = argparse.ArgumentParser(description="SIM-OS Integrated Resource Management Simulator")
    parser.add_argument("-b", "--benchmark", action="store_true", help="Run full benchmark suite and exit")
    parser.add_argument("-t", "--test", action="store_true", help="Run unittest suite and exit")
    parser.add_argument("-s", "--telemetry", action="store_true", help="Run host telemetry probe and exit")
    parser.add_argument("-c", "--charts", action="store_true", help="Generate all visual comparison charts")

    args = parser.parse_args()

    if args.benchmark:
        menu_full_benchmark()
    elif args.test:
        menu_test_suite()
    elif args.telemetry:
        menu_telemetry()
    elif args.charts:
        generate_all_visualizations()
    else:
        interactive_main()


if __name__ == "__main__":
    main()
