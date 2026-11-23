#!/usr/bin/env python3
"""
OS Lab - Section 1, Q3: FCFS and SJF Scheduling
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import sys
import copy


def get_process_data():
    """
    Returns verified process dataset. Can accept interactive input or default to standard test set.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        processes = []
        print("Enter Process Details (PID Arrival_Time Burst_Time). Type 'done' when finished:")
        while True:
            line = input("> ").strip()
            if line.lower() == "done":
                break
            parts = line.split()
            if len(parts) != 3:
                print("Error: Expected 3 values (e.g., P1 0 5). Try again.")
                continue
            pid, at_s, bt_s = parts
            try:
                at = int(at_s)
                bt = int(bt_s)
                if at < 0 or bt <= 0:
                    print("Error: Arrival time must be >= 0 and Burst time must be > 0.")
                    continue
                processes.append({"pid": pid, "at": at, "bt": bt})
            except ValueError:
                print("Error: Arrival time and Burst time must be integers.")
        if processes:
            return processes

    # Standard lab dataset with intentional arrival gap to demonstrate CPU idle intervals
    return [
        {"pid": "P1", "at": 0, "bt": 4},
        {"pid": "P2", "at": 1, "bt": 3},
        {"pid": "P3", "at": 2, "bt": 1},
        {"pid": "P4", "at": 10, "bt": 2},  # Gap creates idle time from 8 to 10
        {"pid": "P5", "at": 12, "bt": 5},
    ]


def schedule_fcfs(raw_processes):
    print("\n" + "=" * 60)
    print(" 1. FIRST-COME, FIRST-SERVED (FCFS) SCHEDULING")
    print("=" * 60)
    print("Rule: Processes are served strictly in order of Arrival Time.")
    print("Tie-breaker: Process ID order.\n")

    # Preserve original data by deep copying
    processes = copy.deepcopy(raw_processes)
    # Sort by arrival time, then pid
    processes.sort(key=lambda p: (p["at"], p["pid"]))

    current_time = 0
    intervals = []
    results = []

    for p in processes:
        if current_time < p["at"]:
            intervals.append({"type": "IDLE", "start": current_time, "end": p["at"]})
            print(f"[Time {current_time:2d} -> {p['at']:2d}] CPU is IDLE")
            current_time = p["at"]

        start_time = current_time
        end_time = current_time + p["bt"]
        current_time = end_time

        intervals.append({"type": "PROC", "pid": p["pid"], "start": start_time, "end": end_time})
        print(f"[Time {start_time:2d} -> {end_time:2d}] Process {p['pid']} executed (Burst: {p['bt']})")

        ct = end_time
        tat = ct - p["at"]
        wt = tat - p["bt"]
        rt = start_time - p["at"]
        results.append({**p, "ct": ct, "tat": tat, "wt": wt, "rt": rt})

    # Summary
    print("\nExecution Sequence: " + " -> ".join(item["pid"] if item["type"] == "PROC" else "[IDLE]" for item in intervals))
    display_table(results)
    return intervals


def schedule_sjf_non_preemptive(raw_processes):
    print("\n" + "=" * 60)
    print(" 2. SHORTEST JOB FIRST (SJF) SCHEDULING - NON-PREEMPTIVE")
    print("=" * 60)
    print("Rule: At scheduling time, select the arrived process with the shortest burst.")
    print("Tie-breaker: Earlier Arrival Time, then Process ID.\n")

    # Preserve original data
    pool = copy.deepcopy(raw_processes)
    current_time = 0
    intervals = []
    results = []
    completed = []
    total = len(pool)

    while len(completed) < total:
        ready = [p for p in pool if p["at"] <= current_time and p["pid"] not in completed]

        if not ready:
            next_arrival = min(p["at"] for p in pool if p["pid"] not in completed)
            intervals.append({"type": "IDLE", "start": current_time, "end": next_arrival})
            print(f"[Time {current_time:2d} -> {next_arrival:2d}] CPU is IDLE")
            current_time = next_arrival
            ready = [p for p in pool if p["at"] <= current_time and p["pid"] not in completed]

        # Select shortest burst time; tie breaker: arrival time, then pid
        ready.sort(key=lambda p: (p["bt"], p["at"], p["pid"]))
        selected = ready[0]

        start_time = current_time
        end_time = current_time + selected["bt"]
        current_time = end_time
        completed.append(selected["pid"])

        intervals.append({"type": "PROC", "pid": selected["pid"], "start": start_time, "end": end_time})
        print(f"[Time {start_time:2d} -> {end_time:2d}] Process {selected['pid']} executed (Burst: {selected['bt']})")

        ct = end_time
        tat = ct - selected["at"]
        wt = tat - selected["bt"]
        rt = start_time - selected["at"]
        results.append({**selected, "ct": ct, "tat": tat, "wt": wt, "rt": rt})

    print("\nExecution Sequence: " + " -> ".join(item["pid"] if item["type"] == "PROC" else "[IDLE]" for item in intervals))
    display_table(results)
    return intervals


def display_table(results):
    print("\nProcess Performance Metrics:")
    print("-" * 65)
    print(f"{'PID':<6}{'Arrival':<10}{'Burst':<8}{'CT':<8}{'TAT':<8}{'WT':<8}{'RT':<8}")
    print("-" * 65)
    total_tat, total_wt, total_rt = 0, 0, 0
    for r in results:
        print(f"{r['pid']:<6}{r['at']:<10}{r['bt']:<8}{r['ct']:<8}{r['tat']:<8}{r['wt']:<8}{r['rt']:<8}")
        total_tat += r["tat"]
        total_wt += r["wt"]
        total_rt += r["rt"]
    n = len(results)
    print("-" * 65)
    print(f"Averages: TAT = {total_tat/n:.2f}, WT = {total_wt/n:.2f}, RT = {total_rt/n:.2f}")


def main():
    print("=" * 65)
    print(" OS LAB - FCFS AND SJF (NON-PREEMPTIVE) CPU SCHEDULING")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    dataset = get_process_data()
    print("\nOriginal Input Dataset (Preserved across algorithms):")
    print("-" * 40)
    print(f"{'PID':<8}{'Arrival Time':<15}{'Burst Time':<12}")
    print("-" * 40)
    for p in dataset:
        print(f"{p['pid']:<8}{p['at']:<15}{p['bt']:<12}")
    print("-" * 40)

    schedule_fcfs(dataset)
    schedule_sjf_non_preemptive(dataset)


if __name__ == "__main__":
    main()
