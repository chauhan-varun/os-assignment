#!/usr/bin/env python3
"""
=============================================================================
 OPERATING SYSTEMS INTEGRATED SIMULATION SYSTEM (OS-ISS)
 An Integrated Resource Management and OS Simulation Platform
-----------------------------------------------------------------------------
 Student Name : Varun Chauhan
 Roll Number  : 2401010276
 Course       : B.Tech CSE Sec B
 Evaluation   : 100-Mark Capstone Practical Submission
=============================================================================
"""

import os
import sys
import time
import logging
import subprocess

# Configure centralized activity logging
LOG_FILE = "os_application.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("OS-ISS-App")
logger.info("Integrated OS Application initialized.")

# Add sections to path for direct imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "section-1", "q1-environment-setup"))
sys.path.append(os.path.join(BASE_DIR, "section-1", "q3-fcfs-sjf"))
sys.path.append(os.path.join(BASE_DIR, "section-1", "q4-priority-round-robin"))
sys.path.append(os.path.join(BASE_DIR, "section-1", "q5-scheduling-threads-ipc"))
sys.path.append(os.path.join(BASE_DIR, "section-2", "q2-race-lock-semaphore"))
sys.path.append(os.path.join(BASE_DIR, "section-2", "q3-classical-synchronization"))
sys.path.append(os.path.join(BASE_DIR, "section-2", "q4-deadlock-bankers"))
sys.path.append(os.path.join(BASE_DIR, "section-3", "q1-contiguous-allocation-swapping"))
sys.path.append(os.path.join(BASE_DIR, "section-3", "q2-paging-segmentation"))
sys.path.append(os.path.join(BASE_DIR, "section-3", "q3-demand-paging-replacement"))
sys.path.append(os.path.join(BASE_DIR, "section-3", "q5-disk-scheduling-swap"))
sys.path.append(os.path.join(BASE_DIR, "section-4", "q3-file-allocation-methods"))
sys.path.append(os.path.join(BASE_DIR, "section-4", "q4-free-space-access-control"))


def clear_screen():
    print("\n" + "=" * 70)


def print_header(title):
    print("=" * 70)
    print(f" {title.center(68)}")
    print("=" * 70)


# =====================================================================
# MODULE 1: PROCESS SCHEDULING SUITE
# =====================================================================
def menu_cpu_scheduling():
    import scheduling_fcfs_sjf as sched_1
    import scheduling_priority_rr as sched_2

    print_header("MODULE 1: PROCESS SCHEDULING & METRICS SUITE")
    print("1. Compare FCFS vs Non-Preemptive SJF (Standard Common Dataset)")
    print("2. Compare Priority vs Round Robin Scheduling (Common Dataset)")
    print("3. Round Robin with ASCII Gantt Chart & Performance Metrics")
    print("4. Return to Main Menu")

    choice = input("\nEnter choice [1-4]: ").strip()
    logger.info(f"User navigated to Scheduling Suite: option {choice}")

    common_dataset = [
        {"pid": "P1", "at": 0, "bt": 5, "prio": 3},
        {"pid": "P2", "at": 1, "bt": 3, "prio": 1},
        {"pid": "P3", "at": 2, "bt": 8, "prio": 4},
        {"pid": "P4", "at": 3, "bt": 6, "prio": 2},
    ]

    if choice == "1":
        sched_1.schedule_fcfs(common_dataset)
        sched_1.schedule_sjf_non_preemptive(common_dataset)
    elif choice == "2":
        sched_2.schedule_priority_non_preemptive(common_dataset)
        sched_2.schedule_round_robin(common_dataset, quantum=3)
    elif choice == "3":
        import metrics_threads_ipc as m_ipc
        m_ipc.demonstrate_scheduling_metrics()
    elif choice == "4":
        return
    else:
        print("Invalid option.")


# =====================================================================
# MODULE 2: MULTITHREADING, SYNCHRONIZATION & DEADLOCK
# =====================================================================
def menu_concurrency_deadlock():
    print_header("MODULE 2: CONCURRENCY, SYNCHRONIZATION & DEADLOCK")
    print("1. Race Condition Demo: Unprotected vs Mutex Lock vs Semaphore")
    print("2. Classical Synchronization Problems (Producer-Consumer, Readers-Writers, Philosophers)")
    print("3. Banker's Algorithm (Need Matrix & Safety Sequence)")
    print("4. Circular Wait Simulation & Deadlock Recovery")
    print("5. Return to Main Menu")

    choice = input("\nEnter choice [1-5]: ").strip()
    logger.info(f"User navigated to Concurrency/Deadlock Suite: option {choice}")

    if choice == "1":
        import race_lock_semaphore as rls
        rls.main()
    elif choice == "2":
        import classical_synchronization as cs
        cs.main()
    elif choice == "3":
        import deadlock_bankers as db
        db.run_bankers_algorithm()
    elif choice == "4":
        import deadlock_bankers as db
        db.demonstrate_circular_wait_and_prevention()
        db.run_deadlock_detection_and_recovery()
    elif choice == "5":
        return
    else:
        print("Invalid option.")


# =====================================================================
# MODULE 3: MEMORY & VIRTUAL MEMORY MANAGEMENT
# =====================================================================
def menu_memory_management():
    print_header("MODULE 3: MEMORY & VIRTUAL MEMORY MANAGEMENT")
    print("1. Contiguous Allocation (First Fit, Best Fit, Worst Fit)")
    print("2. Base & Limit Register Address Translation & Swapping")
    print("3. Paging & Segmentation Address Translation")
    print("4. Page Replacement Algorithms (FIFO, LRU, Optimal) & Thrashing Analysis")
    print("5. Return to Main Menu")

    choice = input("\nEnter choice [1-5]: ").strip()
    logger.info(f"User navigated to Memory Management Suite: option {choice}")

    if choice == "1":
        import contiguous_swapping as cs
        blocks = [
            {"id": 1, "initial": 100, "free": 100, "assigned": []},
            {"id": 2, "initial": 500, "free": 500, "assigned": []},
            {"id": 3, "initial": 200, "free": 200, "assigned": []},
            {"id": 4, "initial": 300, "free": 300, "assigned": []},
            {"id": 5, "initial": 600, "free": 600, "assigned": []},
        ]
        procs = [
            {"pid": "P1", "size": 212},
            {"pid": "P2", "size": 417},
            {"pid": "P3", "size": 112},
            {"pid": "P4", "size": 426},
        ]
        cs.allocate_first_fit(blocks, procs)
        cs.allocate_best_fit(blocks, procs)
        cs.allocate_worst_fit(blocks, procs)
    elif choice == "2":
        import contiguous_swapping as cs
        cs.demonstrate_address_translation()
        cs.demonstrate_swapping()
    elif choice == "3":
        import paging_segmentation as ps
        ps.demonstrate_paging()
        ps.demonstrate_segmentation()
    elif choice == "4":
        import page_replacement as pr
        pr.main()
    elif choice == "5":
        return
    else:
        print("Invalid option.")


# =====================================================================
# MODULE 4: STORAGE, FILE SYSTEMS & DISK SCHEDULING
# =====================================================================
def menu_storage_management():
    print_header("MODULE 4: STORAGE, FILE SYSTEMS & DISK SCHEDULING")
    print("1. Disk Head Traversal (FCFS, SSTF, SCAN, C-SCAN) Comparison")
    print("2. Swap-Space Bitmap Block Allocation & Reclamation")
    print("3. File Allocation Methods (Contiguous, Linked, Indexed)")
    print("4. Free Space Bitmap & Invariant Verification")
    print("5. Return to Main Menu")

    choice = input("\nEnter choice [1-5]: ").strip()
    logger.info(f"User navigated to Storage Management Suite: option {choice}")

    if choice == "1":
        import disk_scheduling_swap as dss
        dss.main()
    elif choice == "2":
        import disk_scheduling_swap as dss
        mgr = dss.SwapSpaceManager(16)
        mgr.allocate("Proc_A", 4)
        mgr.allocate("Proc_B", 6)
        mgr.release("Proc_A")
    elif choice == "3":
        import file_allocation as fa
        fa.main()
    elif choice == "4":
        import free_space_access_control as fsac
        fsac.main()
    elif choice == "5":
        return
    else:
        print("Invalid option.")


# =====================================================================
# MODULE 5: BASH INTEGRATION & SYSTEM DIAGNOSTICS
# =====================================================================
def run_bash_diagnostics():
    print_header("MODULE 5: BASH INTEGRATION & HOST DIAGNOSTICS")
    logger.info("Running host bash diagnostics.")

    commands = [
        ("Kernel Version", "uname -s -r -m"),
        ("CPU & Hardware Architecture", "lscpu | head -n 8"),
        ("Memory & Swap Utilization", "free -h"),
        ("Active Process Count", "ps aux | wc -l"),
    ]

    for title, cmd in commands:
        print(f"\n--- [Bash Command]: {title} (`{cmd}`) ---")
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            print(res.stdout.strip() if res.stdout else "No output.")
        except Exception as e:
            print(f"Error running command: {e}")
            logger.error(f"Command '{cmd}' failed: {e}")


# =====================================================================
# MODULE 6: AUTOMATED TEST & RELIABILITY RUNNER
# =====================================================================
def run_integrated_tests():
    print_header("MODULE 6: INTEGRATED TEST SUITE & VALIDATION RUNNER")
    logger.info("Executing automated test suite from integrated application.")
    import subprocess
    res = subprocess.run([sys.executable, "test_suite.py"])
    print(f"\nTest runner finished with exit code {res.returncode}.")


# =====================================================================
# MAIN MENU FLOW
# =====================================================================
def main_menu():
    while True:
        clear_screen()
        print("=" * 70)
        print(" OPERATING SYSTEMS INTEGRATED SIMULATION SYSTEM (OS-ISS)")
        print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
        print(" Capstone Submission - 100 Marks Evaluation Suite")
        print("=" * 70)
        print("  1. Process Scheduling & Performance Metrics (FCFS, SJF, Priority, RR)")
        print("  2. Multithreading, Concurrency, Synchronization & Deadlocks")
        print("  3. Memory Management, Address Translation & Virtual Memory")
        print("  4. Disk Scheduling, Storage Allocation & Free-Space Management")
        print("  5. Host OS Diagnostics & Bash Integration")
        print("  6. Automated Test Suite, Boundary Checks & Reliability Runner")
        print("  7. Exit Platform")
        print("=" * 70)

        choice = input("Select an option [1-7]: ").strip()
        logger.info(f"Main menu selected: {choice}")

        if choice == "1":
            menu_cpu_scheduling()
        elif choice == "2":
            menu_concurrency_deadlock()
        elif choice == "3":
            menu_memory_management()
        elif choice == "4":
            menu_storage_management()
        elif choice == "5":
            run_bash_diagnostics()
        elif choice == "6":
            run_integrated_tests()
        elif choice == "7":
            print("\nExiting OS Integrated Simulation System. Thank you!\n")
            logger.info("OS-ISS application terminated normally by user.")
            break
        else:
            print("\nInvalid choice. Please select 1 through 7.")

        input("\n[Press Enter to return to Main Menu...]")


if __name__ == "__main__":
    main_menu()
