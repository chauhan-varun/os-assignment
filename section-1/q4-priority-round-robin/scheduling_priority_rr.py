#!/usr/bin/env python3
"""
OS Lab - Section 1, Q4: Priority and Round Robin Scheduling
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import sys
import copy
from collections import deque


PRIORITY_CONVENTION = "Lower numeric value indicates HIGHER priority (e.g., Priority 1 > Priority 3)"


def get_process_data():
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        processes = []
        print("Enter Process Details (PID Arrival_Time Burst_Time Priority). Type 'done' to finish:")
        while True:
            line = input("> ").strip()
            if line.lower() == "done":
                break
            parts = line.split()
            if len(parts) != 4:
                print("Error: Expected 4 values (PID AT BT Priority). Example: P1 0 4 2")
                continue
            pid, at_s, bt_s, prio_s = parts
            try:
                at, bt, prio = int(at_s), int(bt_s), int(prio_s)
                if at < 0 or bt <= 0:
                    print("Error: Arrival >= 0 and Burst > 0 required.")
                    continue
                processes.append({"pid": pid, "at": at, "bt": bt, "prio": prio})
            except ValueError:
                print("Error: Numeric values must be integers.")
        if processes:
            return processes

    # Standard lab dataset
    return [
        {"pid": "P1", "at": 0, "bt": 5, "prio": 3},
        {"pid": "P2", "at": 1, "bt": 3, "prio": 1},  # Highest priority among initial jobs
        {"pid": "P3", "at": 2, "bt": 8, "prio": 4},
        {"pid": "P4", "at": 3, "bt": 6, "prio": 2},
        {"pid": "P5", "at": 25, "bt": 4, "prio": 1}, # Arrives after idle period
    ]


def schedule_priority_non_preemptive(raw_processes):
    print("\n" + "=" * 65)
    print(" 1. NON-PREEMPTIVE PRIORITY SCHEDULING")
    print("=" * 65)
    print(f"Priority Convention : {PRIORITY_CONVENTION}")
    print("Tie-breaking Rule   : Earlier Arrival Time, then Process ID.\n")

    pool = copy.deepcopy(raw_processes)
    current_time = 0
    intervals = []
    completed = []
    results = []
    total = len(pool)

    while len(completed) < total:
        ready = [p for p in pool if p["at"] <= current_time and p["pid"] not in completed]

        if not ready:
            next_arrival = min(p["at"] for p in pool if p["pid"] not in completed)
            intervals.append({"type": "IDLE", "start": current_time, "end": next_arrival})
            print(f"[Time {current_time:2d} -> {next_arrival:2d}] CPU is IDLE")
            current_time = next_arrival
            ready = [p for p in pool if p["at"] <= current_time and p["pid"] not in completed]

        # Lower priority number = Higher priority; tie-break on AT, then PID
        ready.sort(key=lambda p: (p["prio"], p["at"], p["pid"]))
        selected = ready[0]

        start_time = current_time
        end_time = current_time + selected["bt"]
        current_time = end_time
        completed.append(selected["pid"])

        intervals.append({"type": "PROC", "pid": selected["pid"], "start": start_time, "end": end_time})
        print(f"[Time {start_time:2d} -> {end_time:2d}] Process {selected['pid']} (Priority {selected['prio']}) finished.")

        ct = end_time
        tat = ct - selected["at"]
        wt = tat - selected["bt"]
        rt = start_time - selected["at"]
        results.append({**selected, "ct": ct, "tat": tat, "wt": wt, "rt": rt})

    print("\nExecution Sequence: " + " -> ".join(i["pid"] if i["type"] == "PROC" else "[IDLE]" for i in intervals))
    display_metrics_table(results)


def schedule_round_robin(raw_processes, quantum=2):
    print("\n" + "=" * 65)
    print(" 2. ROUND ROBIN (RR) SCHEDULING")
    print("=" * 65)
    print(f"Time Quantum (q)     : {quantum}")
    print("Ready Queue Strategy : First-In, First-Out (FIFO) queue with time slices.\n")

    processes = copy.deepcopy(raw_processes)
    processes.sort(key=lambda p: (p["at"], p["pid"]))

    # Track remaining bursts and first start time
    rem_bt = {p["pid"]: p["bt"] for p in processes}
    proc_map = {p["pid"]: p for p in processes}
    first_start = {}
    finish_time = {}

    current_time = 0
    ready_queue = deque()
    unadded = list(processes)
    slices = []

    # Advance to first arrival
    if unadded and unadded[0]["at"] > current_time:
        slices.append({"type": "IDLE", "start": current_time, "end": unadded[0]["at"]})
        current_time = unadded[0]["at"]

    # Initial enqueue
    while unadded and unadded[0]["at"] <= current_time:
        ready_queue.append(unadded.pop(0)["pid"])

    while ready_queue or unadded:
        if not ready_queue:
            # CPU is idle until next process arrives
            next_proc = unadded[0]
            slices.append({"type": "IDLE", "start": current_time, "end": next_proc["at"]})
            print(f"[Time {current_time:2d} -> {next_proc['at']:2d}] CPU is IDLE")
            current_time = next_proc["at"]
            while unadded and unadded[0]["at"] <= current_time:
                ready_queue.append(unadded.pop(0)["pid"])

        pid = ready_queue.popleft()
        if pid not in first_start:
            first_start[pid] = current_time

        execute_time = min(quantum, rem_bt[pid])
        start_time = current_time
        current_time += execute_time
        rem_bt[pid] -= execute_time

        slices.append({"type": "PROC", "pid": pid, "start": start_time, "end": current_time})
        print(f"[Time {start_time:2d} -> {current_time:2d}] Process {pid} executed slice (Remaining: {rem_bt[pid]})")

        # Check for newly arrived processes during this slice
        while unadded and unadded[0]["at"] <= current_time:
            ready_queue.append(unadded.pop(0)["pid"])

        if rem_bt[pid] > 0:
            ready_queue.append(pid)
        else:
            finish_time[pid] = current_time

    # Compute metrics
    results = []
    for p in raw_processes:
        pid = p["pid"]
        ct = finish_time[pid]
        tat = ct - p["at"]
        wt = tat - p["bt"]
        rt = first_start[pid] - p["at"]
        results.append({**p, "ct": ct, "tat": tat, "wt": wt, "rt": rt})

    print("\nExecution Slices Sequence:\n" + " -> ".join(
        f"{s['pid']}[{s['start']}-{s['end']}]" if s["type"] == "PROC" else f"[IDLE:{s['start']}-{s['end']}]"
        for s in slices
    ))
    display_metrics_table(results)


def display_metrics_table(results):
    print("-" * 65)
    print(f"{'PID':<6}{'Arrival':<10}{'Burst':<8}{'CT':<8}{'TAT':<8}{'WT':<8}{'RT':<8}")
    print("-" * 65)
    tot_tat, tot_wt, tot_rt = 0, 0, 0
    for r in results:
        print(f"{r['pid']:<6}{r['at']:<10}{r['bt']:<8}{r['ct']:<8}{r['tat']:<8}{r['wt']:<8}{r['rt']:<8}")
        tot_tat += r["tat"]
        tot_wt += r["wt"]
        tot_rt += r["rt"]
    n = len(results)
    print("-" * 65)
    print(f"Averages: TAT = {tot_tat/n:.2f}, WT = {tot_wt/n:.2f}, RT = {tot_rt/n:.2f}\n")


def main():
    print("=" * 65)
    print(" OS LAB - PRIORITY AND ROUND ROBIN CPU SCHEDULING")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    dataset = get_process_data()
    print("\nInput Dataset:")
    print("-" * 45)
    print(f"{'PID':<6}{'Arrival':<12}{'Burst':<10}{'Priority':<10}")
    print("-" * 45)
    for p in dataset:
        print(f"{p['pid']:<6}{p['at']:<12}{p['bt']:<10}{p['prio']:<10}")
    print("-" * 45)

    schedule_priority_non_preemptive(dataset)
    schedule_round_robin(dataset, quantum=3)


if __name__ == "__main__":
    main()
