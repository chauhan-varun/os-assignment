# SIM-OS Comprehensive Benchmark & Performance Report
**Author:** Varun Chauhan (2401010276)  
**System:** Integrated Python-and-Bash OS Resource Management Simulator

---
## 1. CPU Scheduling Performance Comparison

| Algorithm | Avg Turnaround Time (TAT) | Avg Waiting Time (WT) | Avg Response Time (RT) | CPU Utilization (%) | Throughput (procs/unit) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **FCFS** | 17.00 | 11.40 | 11.40 | 100.0% | 0.1786 |
| **SJF (Non-Preemptive)** | 13.80 | 8.20 | 8.20 | 100.0% | 0.1786 |
| **SRTF (Preemptive SJF)** | 12.20 | 6.60 | 4.40 | 100.0% | 0.1786 |
| **Priority (Non-Preemptive)** | 16.20 | 10.60 | 10.60 | 100.0% | 0.1786 |
| **Priority (Preemptive)** | 15.20 | 9.60 | 7.80 | 100.0% | 0.1786 |
| **Round Robin (Q=2)** | 18.60 | 13.00 | 2.80 | 100.0% | 0.1786 |
| **Round Robin (Q=4)** | 18.60 | 13.00 | 6.00 | 100.0% | 0.1786 |

### Key Analytical Insights:
- **SJF / SRTF:** Achieves the lowest Average Waiting Time due to optimal scheduling of short jobs.
- **Round Robin:** Balances response time effectively across processes; lower time quantums provide rapid initial responsiveness at the expense of context-switch overhead.
- **Preemptive Priority:** Swiftly pre-empts low-priority background work in favor of high-priority critical tasks.

---
## 2. Memory Management Analysis

### Contiguous Allocation (Dynamic Partitioning)

| Algorithm | Allocated Processes | Unallocated Processes | Internal Frag (KB) | External Frag (KB) | Memory Utilization |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **First-Fit** | P1(212KB), P2(417KB), P3(112KB) | P4(426KB) | 559 KB | 0 KB | 43.6% |
| **Best-Fit** | P1(212KB), P2(417KB), P3(112KB), P4(426KB) | None | 433 KB | 0 KB | 68.6% |
| **Worst-Fit** | P1(212KB), P2(417KB), P3(112KB) | P4(426KB) | 659 KB | 0 KB | 43.6% |

### Virtual Memory Page Replacement Comparison

| Frame Capacity | FIFO Faults | LRU Faults | Optimal Faults | LFU Faults |
| :---: | :---: | :---: | :---: | :---: |
| **3 Frames** | 15 (25.0% hits) | 12 (40.0% hits) | 9 (55.0% hits) | 13 (35.0% hits) |
| **4 Frames** | 10 (50.0% hits) | 8 (60.0% hits) | 8 (60.0% hits) | 8 (60.0% hits) |
| **5 Frames** | 9 (55.0% hits) | 7 (65.0% hits) | 7 (65.0% hits) | 7 (65.0% hits) |

---
## 3. Concurrency & Deadlock Avoidance Analysis

**Initial Banker's System State:** SAFE (Safe Sequence: P1 -> P3 -> P0 -> P2 -> P4)

### Sample Resource Requests Tested:

- **P1 requests (A=1, B=0, C=2):** [GRANTED] Granted: Request by P1 approved. Safe sequence: P1 -> P3 -> P0 -> P2 -> P4
- **P4 requests (A=3, B=3, C=0):** [DENIED] Denied: Insufficient available resource A (3 requested, only 2 available). Process must wait.
- **P0 requests (A=0, B=2, C=0):** [DENIED] Denied: Granting request by P0 results in an UNSAFE state. Allocation rolled back.

### Wait-For Graph (WFG) Cycle Detection:

- Case `deadlock_free`: **NO DEADLOCK (Acyclic)**
- Case `deadlocked_cycle`: **DEADLOCK DETECTED! Cycles: [['P2', 'P3', 'P4', 'P2']]**

---
## 4. Disk Arm Scheduling & File System Storage

| Disk Scheduling Algorithm | Total Head Movement (Cylinders) | Average Seek Length |
| :--- | :---: | :---: |
| **FCFS** | 640 | 80.00 cylinders |
| **SSTF** | 236 | 29.50 cylinders |
| **SCAN** | 331 | 41.38 cylinders |
| **C-SCAN** | 382 | 47.75 cylinders |
| **LOOK** | 299 | 37.38 cylinders |
| **C-LOOK** | 322 | 40.25 cylinders |

### File Allocation Log & Block Lifecycle:

- `CREATE CONTIGUOUS 'system.log' (4 blks) -> OK [0, 1, 2, 3]`
- `CREATE CONTIGUOUS 'kernel.bin' (6 blks) -> OK [4, 5, 6, 7, 8, 9]`
- `CREATE LINKED 'user_data.csv' (5 blks) -> OK [10, 11, 12, 13, 14]`
- `CREATE INDEXED 'database.db' (4 blks) -> OK [16, 17, 18, 19]`
- `DELETE 'system.log' -> OK (blocks freed)`
- `CREATE CONTIGUOUS 'audit.txt' (5 blks) -> OK [20, 21, 22, 23, 24]`

**Remaining Free Blocks:** 11 / 32