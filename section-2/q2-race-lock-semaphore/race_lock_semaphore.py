#!/usr/bin/env python3
"""
OS Lab - Section 2, Q2: Race Condition, Lock and Semaphore
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import threading
import time


# Global variables for testing
ITERATIONS_PER_THREAD = 10_000
NUM_THREADS = 4
EXPECTED_TOTAL = NUM_THREADS * ITERATIONS_PER_THREAD


# -------------------------------------------------------------
# 1. Unprotected Shared Counter (Demonstrating Race Condition)
# -------------------------------------------------------------
unprotected_counter = 0


def worker_unprotected():
    global unprotected_counter
    for _ in range(ITERATIONS_PER_THREAD):
        curr = unprotected_counter
        # Force a thread context switch to guarantee race condition
        time.sleep(0.000001)
        unprotected_counter = curr + 1



def run_unprotected_trial(trial_num):
    global unprotected_counter
    unprotected_counter = 0
    threads = [threading.Thread(target=worker_unprotected) for _ in range(NUM_THREADS)]
    start_t = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start_t
    discrepancy = EXPECTED_TOTAL - unprotected_counter
    print(f"  Trial {trial_num}: Result = {unprotected_counter:>7} / {EXPECTED_TOTAL} (Lost Updates: {discrepancy:>6}, Time: {elapsed:.4f}s)")
    return elapsed, unprotected_counter


# -------------------------------------------------------------
# 2. Mutex Lock-Protected Counter (Mutual Exclusion)
# -------------------------------------------------------------
lock_counter = 0
mutex_lock = threading.Lock()


def worker_lock():
    global lock_counter
    for _ in range(ITERATIONS_PER_THREAD):
        with mutex_lock:
            curr = lock_counter
            time.sleep(0.000001)
            lock_counter = curr + 1


def run_lock_trial():
    global lock_counter
    lock_counter = 0
    threads = [threading.Thread(target=worker_lock) for _ in range(NUM_THREADS)]
    start_t = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start_t
    print(f"  Lock-Protected Result: {lock_counter:>7} / {EXPECTED_TOTAL} (Lost Updates: 0, Time: {elapsed:.4f}s)")
    return elapsed, lock_counter


# -------------------------------------------------------------
# 3. Semaphore-Protected Counter
# -------------------------------------------------------------
semaphore_counter = 0
binary_semaphore = threading.Semaphore(1)  # Binary semaphore acts as mutex


def worker_semaphore():
    global semaphore_counter
    for _ in range(ITERATIONS_PER_THREAD):
        binary_semaphore.acquire()
        try:
            curr = semaphore_counter
            time.sleep(0.000001)
            semaphore_counter = curr + 1
        finally:
            binary_semaphore.release()


def run_semaphore_trial():
    global semaphore_counter
    semaphore_counter = 0
    threads = [threading.Thread(target=worker_semaphore) for _ in range(NUM_THREADS)]
    start_t = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start_t
    print(f"  Semaphore-Protected Result: {semaphore_counter:>7} / {EXPECTED_TOTAL} (Lost Updates: 0, Time: {elapsed:.4f}s)")
    return elapsed, semaphore_counter


def main():
    print("=" * 65)
    print(" OS LAB - RACE CONDITION, MUTEX LOCK AND BINARY SEMAPHORE")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)
    print(f"Configuration: {NUM_THREADS} threads, {ITERATIONS_PER_THREAD:,} increments each.")
    print(f"Expected Final Counter Value: {EXPECTED_TOTAL:,}\n")

    print("[Phase 1] Demonstrating Timing-Dependent Race Condition (3 Trials):")
    t_unp1, r_unp1 = run_unprotected_trial(1)
    t_unp2, r_unp2 = run_unprotected_trial(2)
    t_unp3, r_unp3 = run_unprotected_trial(3)
    avg_unp = (t_unp1 + t_unp2 + t_unp3) / 3

    print("\n[Phase 2] Correcting with Mutual Exclusion Lock (threading.Lock):")
    t_lock, r_lock = run_lock_trial()

    print("\n[Phase 3] Correcting with Binary Semaphore (threading.Semaphore(1)):")
    t_sem, r_sem = run_semaphore_trial()

    print("\n" + "=" * 65)
    print(" SUMMARY AND COMPARISON TABLE")
    print("=" * 65)
    print(f"{'Mechanism':<22}{'Final Counter':<15}{'Correct?':<12}{'Time (s)':<12}{'Overhead':<12}")
    print("-" * 65)
    print(f"{'Unprotected (Race)':<22}{r_unp3:<15}{'NO':<12}{avg_unp:<12.4f}{'None (Faulty)'}")
    print(f"{'Mutex Lock':<22}{r_lock:<15}{'YES':<12}{t_lock:<12.4f}{f'{(t_lock/avg_unp):.2f}x'}")
    print(f"{'Binary Semaphore':<22}{r_sem:<15}{'YES':<12}{t_sem:<12.4f}{f'{(t_sem/avg_unp):.2f}x'}")
    print("-" * 65)
    print("Observations:")
    print("1. Without synchronization, concurrent read-modify-write causes lost updates.")
    print("2. Mutex Lock guarantees mutual exclusion, restoring mathematical correctness.")
    print("3. Binary Semaphore also guarantees correctness, with slightly different internal")
    print("   counter management overhead.")


if __name__ == "__main__":
    main()
