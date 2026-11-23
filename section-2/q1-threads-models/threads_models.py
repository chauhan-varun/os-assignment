#!/usr/bin/env python3
"""
OS Lab - Section 2, Q1: Thread Creation, Models and Benefits
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import math
import sys
import threading
import time


def compute_chunk(start, end, thread_tag=None, progress_callback=None):
    """
    Simulates a CPU-bound compute workload: calculating primes and square roots.
    """
    total = 0.0
    for i in range(start, end):
        total += math.sqrt(i)
        if thread_tag and progress_callback and (i - start) % max(1, (end - start) // 4) == 0:
            progress_callback(thread_tag, (i - start) / (end - start) * 100)
    return total


def single_threaded_baseline(total_items):
    print("\n--- [1] Single-Threaded Baseline Workload ---")
    start_t = time.perf_counter()
    result = compute_chunk(1, total_items + 1)
    duration = time.perf_counter() - start_t
    print(f"  Result computed : {result:.2f}")
    print(f"  Execution Time  : {duration:.4f} seconds")
    return duration, result


def multithreaded_workload(total_items, num_threads=4):
    print(f"\n--- [2] Multithreaded Workload ({num_threads} Worker Threads) ---")
    chunk_size = total_items // num_threads
    threads = []
    thread_results = [0.0] * num_threads

    def worker(idx, start, end):
        t_id = threading.get_native_id() if hasattr(threading, "get_native_id") else threading.get_ident()
        t_name = threading.current_thread().name
        print(f"  [Thread {idx+1}: {t_name} (TID {t_id})] Started range [{start} -> {end}]")

        def progress(tag, pct):
            print(f"    * [{tag}] Progress: {pct:4.1f}%")

        val = compute_chunk(start, end, f"Thread-{idx+1}", progress)
        thread_results[idx] = val
        print(f"  [Thread {idx+1}: {t_name}] Completed task.")

    start_t = time.perf_counter()
    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1 if i != num_threads - 1 else total_items + 1
        t = threading.Thread(target=worker, args=(i, start, end), name=f"WorkerThread-{i+1}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duration = time.perf_counter() - start_t
    total_res = sum(thread_results)
    print(f"  All {num_threads} worker threads joined.")
    print(f"  Aggregated Result: {total_res:.2f}")
    print(f"  Execution Time   : {duration:.4f} seconds")
    return duration, total_res


def main():
    print("=" * 65)
    print(" OS LAB - THREAD CREATION, MODELS AND PERFORMANCE BENEFITS")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    workload_size = 3_000_000
    print(f"Total Computation Workload: {workload_size:,} mathematical iterations.")

    t_single, res_single = single_threaded_baseline(workload_size)
    t_multi, res_multi = multithreaded_workload(workload_size, num_threads=4)

    print("\n--- [3] Performance Comparison & Analysis ---")
    print("-" * 55)
    print(f"{'Execution Mode':<25}{'Duration (s)':<18}{'Result Match'}")
    print("-" * 55)
    print(f"{'Single-Threaded':<25}{t_single:<18.4f}{'BASELINE'}")
    print(f"{'Multithreaded (4 threads)':<25}{t_multi:<18.4f}{math.isclose(res_single, res_multi, rel_tol=1e-5)}")
    print("-" * 55)

    print("\nTheoretical Notes:")
    print("1. Python GIL (Global Interpreter Lock):")
    print("   CPython uses a GIL preventing pure CPU-bound Python threads from running")
    print("   true parallel machine instructions across multiple CPU cores simultaneously.")
    print("2. Multithreading Models:")
    print("   - Many-to-One (User-Level Threads): Lightweight, no kernel overhead, but blocking I/O blocks all.")
    print("   - One-to-One (Kernel-Level Threads, standard Linux POSIX pthreads): True multiprocessor dispatch.")
    print("   - Many-to-Many: Hybrid model balancing kernel resources and lightweight user scheduling.")
    print("3. Real World Benefits:")
    print("   High responsiveness for UI/I/O tasks, concurrent networking, and shared address space.")


if __name__ == "__main__":
    main()
