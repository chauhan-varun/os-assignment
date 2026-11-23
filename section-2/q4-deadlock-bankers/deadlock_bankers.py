#!/usr/bin/env python3
"""
OS Lab - Section 2, Q4: Deadlock Handling and Banker's Algorithm
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import threading
import time
import copy


# =====================================================================
# [PART 1] Controlled Deadlock Simulation (Circular Wait & Timeout)
# =====================================================================
def demonstrate_circular_wait_and_prevention():
    print("=" * 65)
    print(" [PART 1] CIRCULAR WAIT DEADLOCK & COFFMAN CONDITIONS")
    print("=" * 65)
    print("The 4 Necessary Coffman Conditions for Deadlock:")
    print("  1. Mutual Exclusion : Resources cannot be shared simultaneously.")
    print("  2. Hold and Wait    : A process holds resources while requesting others.")
    print("  3. No Preemption    : Resources cannot be forcibly seized.")
    print("  4. Circular Wait    : P0 waits for P1's resource, and P1 waits for P0's.\n")

    res_A = threading.Lock()
    res_B = threading.Lock()
    deadlock_detected = False

    def thread_1_work():
        nonlocal deadlock_detected
        print("  [Thread 1] Acquiring Resource A...")
        res_A.acquire()
        print("  [Thread 1] Acquired Resource A. Holding A and requesting Resource B...")
        time.sleep(0.05)
        # Controlled acquisition with timeout to prevent permanent program lockup
        acquired = res_B.acquire(timeout=0.2)
        if not acquired:
            print("  [Thread 1] TIMEOUT DETECTED! Deadlock avoided by breaking Hold-and-Wait.")
            deadlock_detected = True
        else:
            print("  [Thread 1] Acquired Resource B.")
            res_B.release()
        res_A.release()

    def thread_2_work():
        print("  [Thread 2] Acquiring Resource B...")
        res_B.acquire()
        print("  [Thread 2] Acquired Resource B. Holding B and requesting Resource A...")
        time.sleep(0.05)
        acquired = res_A.acquire(timeout=0.2)
        if not acquired:
            print("  [Thread 2] TIMEOUT DETECTED! Deadlock avoided by breaking Hold-and-Wait.")
        else:
            print("  [Thread 2] Acquired Resource A.")
            res_A.release()
        res_B.release()

    print("Simulating circular wait attempt between Thread 1 (A->B) and Thread 2 (B->A)...")
    t1 = threading.Thread(target=thread_1_work)
    t2 = threading.Thread(target=thread_2_work)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print("\nDemonstrating Deadlock Prevention via Resource Hierarchy (Global Lock Ordering):")
    print("Rule: Both threads MUST acquire Resource A before Resource B.")

    def ordered_worker(t_name):
        with res_A:
            print(f"  [{t_name}] Acquired Resource A.")
            time.sleep(0.02)
            with res_B:
                print(f"  [{t_name}] Acquired Resource B -> Executing critical task.")
            print(f"  [{t_name}] Released Resource B.")
        print(f"  [{t_name}] Released Resource A.")

    t1_safe = threading.Thread(target=ordered_worker, args=("SafeThread-1",))
    t2_safe = threading.Thread(target=ordered_worker, args=("SafeThread-2",))
    t1_safe.start()
    t2_safe.start()
    t1_safe.join()
    t2_safe.join()
    print("Safe execution completed: Strict resource ordering broke the Circular Wait condition.\n")


# =====================================================================
# [PART 2] Banker's Safety Algorithm & Need Matrix
# =====================================================================
def run_bankers_algorithm():
    print("=" * 65)
    print(" [PART 2] BANKER'S DEADLOCK AVOIDANCE ALGORITHM")
    print("=" * 65)

    processes = ["P0", "P1", "P2", "P3", "P4"]
    resources = ["A", "B", "C"]

    # Allocation Matrix
    allocation = [
        [0, 1, 0],  # P0
        [2, 0, 0],  # P1
        [3, 0, 2],  # P2
        [2, 1, 1],  # P3
        [0, 0, 2],  # P4
    ]

    # Maximum Demand Matrix
    maximum = [
        [7, 5, 3],  # P0
        [3, 2, 2],  # P1
        [9, 0, 2],  # P2
        [2, 2, 2],  # P3
        [4, 3, 3],  # P4
    ]

    # Available Vector
    available = [3, 3, 2]

    num_p = len(processes)
    num_r = len(resources)

    # 1. Calculate Need Matrix: Need[i][j] = Maximum[i][j] - Allocation[i][j]
    need = [[maximum[i][j] - allocation[i][j] for j in range(num_r)] for i in range(num_p)]

    print("Calculated Need Matrix (Max - Allocation):")
    print("-" * 50)
    print(f"{'PID':<6}{'Allocation':<15}{'Maximum':<15}{'Need'}")
    print("-" * 50)
    for i in range(num_p):
        alloc_str = f"[{' '.join(map(str, allocation[i]))}]"
        max_str = f"[{' '.join(map(str, maximum[i]))}]"
        need_str = f"[{' '.join(map(str, need[i]))}]"
        print(f"{processes[i]:<6}{alloc_str:<15}{max_str:<15}{need_str}")
    print("-" * 50)
    print(f"Initial Available Resources: {available}\n")

    # 2. Banker's Safety Algorithm
    work = list(available)
    finish = [False] * num_p
    safe_sequence = []

    print("Executing Safety Evaluation Steps:")
    step = 1
    while len(safe_sequence) < num_p:
        found_candidate = False
        for i in range(num_p):
            if not finish[i]:
                # Check if Need[i] <= Work
                can_satisfy = all(need[i][j] <= work[j] for j in range(num_r))
                if can_satisfy:
                    print(f"  Step {step}: {processes[i]} can finish (Need {need[i]} <= Work {work}).")
                    for j in range(num_r):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(processes[i])
                    print(f"          New Work Vector after releasing allocation: {work}")
                    found_candidate = True
                    step += 1
                    break
        if not found_candidate:
            break

    if len(safe_sequence) == num_p:
        print("\n-> SYSTEM IS IN A SAFE STATE!")
        print(f"Safe Execution Sequence: <{' -> '.join(safe_sequence)}>")
    else:
        print("\n-> SYSTEM IS IN AN UNSAFE STATE! Potential deadlock detected.")


# =====================================================================
# [PART 3] Deadlock Detection & Controlled Recovery
# =====================================================================
def run_deadlock_detection_and_recovery():
    print("\n" + "=" * 65)
    print(" [PART 3] DEADLOCK DETECTION AND CONTROLLED RECOVERY")
    print("=" * 65)

    processes = ["P0", "P1", "P2", "P3"]
    # P0 holds R1, requests R0; P1 holds R0, requests R1; both available = [0, 0]
    alloc = [[0, 1], [1, 0], [1, 1], [0, 0]]
    request = [[1, 0], [0, 1], [1, 0], [0, 0]]
    avail = [0, 0]

    print("Initial State with Contrived Resource Deadlock:")
    for i, p in enumerate(processes):
        print(f"  {p}: Allocated={alloc[i]}, Requesting={request[i]}")
    print(f"Available: {avail}")

    # Detection algorithm
    work = list(avail)
    finish = [alloc[i] == [0, 0] for i in range(len(processes))]

    progress = True
    while progress:
        progress = False
        for i in range(len(processes)):
            if not finish[i]:
                if all(request[i][j] <= work[j] for j in range(len(work))):
                    for j in range(len(work)):
                        work[j] += alloc[i][j]
                    finish[i] = True
                    progress = True

    deadlocked_procs = [processes[i] for i in range(len(processes)) if not finish[i]]

    if deadlocked_procs:
        print(f"\n[Detection Result]: Deadlock detected involving: {deadlocked_procs}")
        # Recovery through controlled process termination
        victim = deadlocked_procs[-1]
        victim_idx = processes.index(victim)
        print(f"\n[Recovery Action]: Terminating victim process '{victim}' to reclaim its resources...")
        reclaimed = alloc[victim_idx]
        for j in range(len(avail)):
            avail[j] += reclaimed[j]
        alloc[victim_idx] = [0, 0]
        request[victim_idx] = [0, 0]
        print(f"Reclaimed resources {reclaimed}. Updated Available: {avail}")
        print("Remaining processes can now proceed to completion without deadlock.")
    else:
        print("\n[Detection Result]: No deadlock found.")


def main():
    demonstrate_circular_wait_and_prevention()
    run_bankers_algorithm()
    run_deadlock_detection_and_recovery()


if __name__ == "__main__":
    main()
