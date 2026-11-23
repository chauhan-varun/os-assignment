# Capstone Project Report: SIM-OS
## Design and Implementation of an Integrated Operating System Resource Management Simulator

**Course:** B.Tech Computer Science and Engineering (Section B)  
**Subject:** Operating Systems Laboratory Capstone  
**Student Name:** Varun Chauhan  
**Roll Number:** 2401010276  
**Academic Term:** 2026-2027  
**Evaluation Weight:** 100 Marks  

---

## Abstract

Operating systems act as the primary abstraction and control layer between computer hardware and user applications. The efficiency of a computer system fundamentally hinges upon the underlying resource management algorithms governing CPU scheduling, main memory allocation, virtual memory page replacement, concurrency and deadlock avoidance, and secondary disk scheduling. 

This report presents **SIM-OS**, an integrated, production-grade simulation and analytical platform implemented in Python 3 with POSIX Bash shell integration. SIM-OS provides a unified execution environment to model, analyze, and compare major operating system resource-management strategies under reproducible synthetic and realistic workloads. The platform incorporates a 37-test verification harness, extensive exception handling, structured activity logging, empirical performance visualization, and live Linux host telemetry probing. Benchmark evaluations across standardized workloads demonstrate theoretical correctness and validate algorithmic trade-offs across all simulated domains.

---

## Phase 1: System Design and Planning (20 Marks)

### 1.1 Problem Statement & Objectives
Traditional educational OS assignments often implement isolated, fragmented scripts that fail to demonstrate the interconnected nature of OS resource management. The objective of this capstone project is to develop a unified, cohesive application that:
1. Simulates four major OS resource management domains: **CPU Scheduling**, **Memory Management**, **Deadlock Avoidance & Detection**, and **Storage/Disk Management**.
2. Seamlessly integrates with the underlying Linux host environment through POSIX shell scripting and `/proc` filesystem telemetry.
3. Implements rigorous input validation, custom exception hierarchies, and timestamped audit logging.
4. Generates automated empirical comparative benchmarks and publication-grade visualizations.
5. Provides both an interactive terminal interface (TUI) and non-interactive command-line automation.

### 1.2 Architectural Decomposition
SIM-OS follows a modular, layered architecture:

```
+-------------------------------------------------------------------------+
|                           User Interface Layer                          |
|             Interactive Terminal Menu  |  POSIX CLI Flags (run.sh)      |
+-------------------------------------------------------------------------+
                                     |
+-------------------------------------------------------------------------+
|                       Orchestration & Analysis Layer                    |
|       BenchmarkRunner  |  Visualizer (Matplotlib)  |  Audit Logger      |
+-------------------------------------------------------------------------+
                                     |
+-------------------------------------------------------------------------+
|                           Core Simulation Layer                         |
|   CPUScheduler  |  MemoryManager  |  BankersEngine  |  DiskScheduler    |
+-------------------------------------------------------------------------+
                                     |
+-------------------------------------------------------------------------+
|                         Host OS Integration Layer                       |
|           Linux /proc Probe  |  vmstat  |  free  |  POSIX Signals       |
+-------------------------------------------------------------------------+
```

### 1.3 Data Design & Key Structures
- **Process Model (`Process`)**: Represents an execution thread with attributes: `pid`, `arrival_time`, `burst_time`, `priority`, `remaining_time`, `start_time`, `completion_time`, `turnaround_time`, `waiting_time`, and `response_time`.
- **Memory Block (`MemoryBlock`)**: Models dynamic memory partitions with: `block_id`, `start_address`, `size`, `is_allocated`, `process_id`, `process_size`, and `internal_fragmentation`.
- **Page Replacement Step (`PageStep`)**: Tracks virtual memory access state: `step_num`, `page`, `frames`, `is_fault`, and `evicted_page`.
- **Banker's Matrices**: Multi-resource state maintained as vectors and matrices: `Available[m]`, `Max[n][m]`, `Allocation[n][m]`, and `Need[n][m] = Max[n][m] - Allocation[n][m]`.
- **Disk Scheduling Record (`DiskScheduleResult`)**: Stores `seek_sequence`, `total_head_movement`, and `average_seek_length`.

---

## Phase 2: Core Resource-Management Modules (20 Marks)

### 2.1 CPU Scheduling Module (`core/scheduler.py`)
Implements five core scheduling algorithms:
1. **First-Come, First-Served (FCFS)**: Non-preemptive scheduling in strict arrival order. Susceptible to the *convoy effect*.
2. **Shortest Job First (SJF Non-Preemptive)**: Selects available processes with minimum CPU burst.
3. **Shortest Remaining Time First (SRTF Preemptive SJF)**: Continuously preempts the CPU when a newly arrived process possesses a shorter remaining burst than the running process.
4. **Priority Scheduling (Preemptive & Non-Preemptive)**: Prioritizes processes based on numerical priority ranks (lower integer indicates higher priority).
5. **Round Robin (RR)**: Time-sliced fair sharing with configurable quantum $Q$. Generates dynamic ready-queue transitions and ASCII Gantt charts.

### 2.2 Memory Management Module (`core/memory.py`)
1. **Contiguous Allocation**: Simulates dynamic partitioning strategies:
   - **First-Fit**: Allocates the first hole with sufficient size.
   - **Best-Fit**: Allocates the smallest hole that satisfies the request, minimizing immediate wasted space.
   - **Worst-Fit**: Allocates the largest available hole, leaving large residual holes.
   - Quantifies internal fragmentation, external fragmentation, and overall memory utilization.
2. **Virtual Memory Page Replacement**:
   - **FIFO**: Replaces oldest loaded page; tracks Belady's anomaly.
   - **LRU**: Replaces the page unreferenced for the longest duration using an `OrderedDict` access history.
   - **Optimal (Belady's MIN)**: Looks ahead into the future reference stream to evict the page unreferenced for the longest future duration.
   - **LFU**: Evicts the least frequently requested page, breaking ties by FIFO arrival.

### 2.3 Deadlock Avoidance and Detection Module (`core/deadlock.py`)
1. **Dijkstra's Banker's Algorithm**:
   - **Safety Algorithm**: Evaluates whether system resources can safely satisfy all maximum claims.
   - **Resource-Request Algorithm**: Intercepts process requests, performs safety testing on pretend allocations, and grants or denies requests with rollback on unsafe states.
2. **Wait-For Graph (WFG) Deadlock Detection**:
   - Represents process dependency cycles using an adjacency list.
   - Applies Depth-First Search (DFS) with recursion stack tracking to isolate circular wait conditions.

### 2.4 Storage & Disk Management Module (`core/storage.py`)
1. **Disk Head Scheduling**:
   - **FCFS**: Sequential request processing.
   - **SSTF**: Greedily chooses requests closest to the current head position.
   - **SCAN (Elevator)**: Sweeps in one direction to the disk boundary before reversing.
   - **C-SCAN**: Sweeps in one direction, then immediately jumps back to the opposite boundary without servicing requests on the return pass.
   - **LOOK / C-LOOK**: Bounds arm reversals strictly to the minimum and maximum active requests without traveling to track boundaries.
2. **File Allocation Simulation**:
   - Simulates **Contiguous**, **Linked**, and **Indexed** file block allocation over a 32-block simulated disk with bit-vector free-space management.

### 2.5 Bash Shell Host Integration (`bash/host_telemetry.sh`)
Integrates Linux operating system inspection:
- Reads `/proc/version` and `/proc/cpuinfo` for kernel and architecture diagnostics.
- Reads `/proc/loadavg` for 1m, 5m, and 15m run-queue load averages.
- Reads `/proc/meminfo` to report physical RAM, active buffers, cache, and swap space.
- Inspects real POSIX process states and memory usage using `ps -eo`.
- Displays real disk mount points and block usage using `df -h`.

---

## Phase 3: Analysis and Comparison (20 Marks)

### 3.1 Experimental Workload Configuration
Standardized workloads were executed across all simulated domains:
- **CPU Workload**: 5 processes with arrival times $[0, 1, 2, 3, 4]$, bursts $[8, 4, 9, 5, 2]$, and priorities $[3, 1, 4, 2, 5]$.
- **Memory Partitions**: Initial block sizes $[100, 500, 200, 300, 600]$ KB with allocation requests $P_1(212\text{ KB}), P_2(417\text{ KB}), P_3(112\text{ KB}), P_4(426\text{ KB})$.
- **Page Access String**: 20-reference sequence: `[7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]`.
- **Disk Requests**: Cylinder sequence `[98, 183, 37, 122, 14, 124, 65, 67]` starting at cylinder `53` on a 200-cylinder disk.

### 3.2 Empirical Results and Comparative Tables

#### CPU Scheduling Benchmark Summary
| Algorithm | Avg Turnaround Time (TAT) | Avg Waiting Time (WT) | Avg Response Time (RT) | CPU Utilization (%) | Throughput |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **FCFS** | 17.00 | 11.40 | 11.40 | 100.0% | 0.1786 |
| **SJF (Non-Preemptive)** | 13.80 | 8.20 | 8.20 | 100.0% | 0.1786 |
| **SRTF (Preemptive SJF)** | 12.20 | 6.60 | 3.40 | 100.0% | 0.1786 |
| **Priority (Non-Preemptive)** | 16.20 | 10.60 | 10.60 | 100.0% | 0.1786 |
| **Priority (Preemptive)** | 15.20 | 9.60 | 6.60 | 100.0% | 0.1786 |
| **Round Robin ($Q=2$)** | 18.60 | 13.00 | 2.60 | 100.0% | 0.1786 |
| **Round Robin ($Q=4$)** | 18.60 | 13.00 | 4.60 | 100.0% | 0.1786 |

**Technical Observation**: SRTF minimized Average Waiting Time (6.60) by scheduling shorter remaining bursts immediately. Round Robin ($Q=2$) provided the best response time (2.60) for interactive processes at the cost of higher average turnaround time.

#### Memory Allocation Strategy Comparison
| Strategy | Allocated Processes | Unallocated Processes | Internal Frag | External Frag | Utilization |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **First-Fit** | $P_1, P_2, P_3$ | $P_4(426\text{ KB})$ | 559 KB | 0 KB | 43.6% |
| **Best-Fit** | $P_1, P_2, P_3, P_4$ | None | 433 KB | 0 KB | **68.6%** |
| **Worst-Fit** | $P_1, P_2, P_3$ | $P_4(426\text{ KB})$ | 659 KB | 0 KB | 43.6% |

**Technical Observation**: Best-Fit successfully allocated all four processes by packing them into tightly matching partitions, achieving 68.6% utilization. Worst-Fit and First-Fit fragmented large blocks prematurely, failing to accommodate $P_4$.

#### Page Replacement Algorithms Across Frame Capacities
| Frame Capacity | FIFO Faults (Hit Rate) | LRU Faults (Hit Rate) | Optimal Faults (Hit Rate) | LFU Faults (Hit Rate) |
| :---: | :---: | :---: | :---: | :---: |
| **3 Frames** | 15 (25.0%) | 12 (40.0%) | **9 (55.0%)** | 13 (35.0%) |
| **4 Frames** | 10 (50.0%) | **8 (60.0%)** | **8 (60.0%)** | **8 (60.0%)** |
| **5 Frames** | 9 (55.0%) | **7 (65.0%)** | **7 (65.0%)** | **7 (65.0%)** |

**Technical Observation**: Belady's Optimal algorithm achieved the theoretical upper bound on hits (55% at 3 frames). LRU closely tracked Optimal as frame size increased to 5, achieving parity at 65% hit rate.

#### Disk Arm Scheduling Comparison
| Algorithm | Total Head Movement | Average Seek Length | Reduction vs FCFS |
| :--- | :---: | :---: | :---: |
| **FCFS** | 640 cylinders | 80.00 cylinders | Baseline (0%) |
| **SSTF** | **236 cylinders** | **29.50 cylinders** | **63.1% Reduction** |
| **SCAN** | 331 cylinders | 41.38 cylinders | 48.3% Reduction |
| **C-SCAN** | 382 cylinders | 47.75 cylinders | 40.3% Reduction |
| **LOOK** | 299 cylinders | 37.38 cylinders | 53.3% Reduction |
| **C-LOOK** | 322 cylinders | 40.25 cylinders | 49.7% Reduction |

**Technical Observation**: SSTF reduced total arm movement from 640 to 236 cylinders. LOOK offered the best bounded trajectory by eliminating seek overhead to boundary tracks 0 and 199.

---

## Phase 4: Testing and Reliability (20 Marks)

### 4.1 Test Suite Structure
The verification suite is implemented using Python's standard `unittest` framework across 5 specialized test modules:
1. `test_scheduler.py`: 11 tests verifying scheduling accuracy, invariants ($TAT = CT - AT$, $WT = TAT - BT$), idle intervals, single-process execution, and negative burst/quantum exceptions.
2. `test_memory.py`: 10 tests verifying partition allocation, zero fragmentation boundaries, Belady's page fault sequences, single-frame limits, and negative frame/page exceptions.
3. `test_deadlock.py`: 6 tests verifying safety sequence generation, valid request grants, request denial when exceeding need or available pools, unsafe state rollback, and cycle detection in Wait-For Graphs.
4. `test_storage.py`: 9 tests verifying seek distances, track boundary handling, LOOK vs SCAN turnaround limits, contiguous/linked/indexed file allocation, duplicate file errors, and disk full limits.
5. `test_integrated.py`: 1 comprehensive end-to-end test verifying full benchmark reporting, CSV data exports, and pipeline integrity.

### 4.2 Error Handling and Exception Hierarchy
SIM-OS enforces strict type and range validations via `core/exceptions.py`:
- `InvalidProcessError`: Rejects negative arrival times and non-positive burst times.
- `InvalidQuantumError`: Rejects Round Robin quantum values $\le 0$.
- `MemoryAllocationError`: Flags unsupported strategies and invalid partition requests.
- `InvalidMemoryAccessError`: Flags non-positive frame counts and empty reference strings.
- `InvalidResourceRequestError`: Intercepts banker requests exceeding maximum claims.
- `InvalidDiskRequestError`: Flags seek requests beyond physical cylinder boundaries.
- `StorageAllocationError`: Intercepts file creation conflicts and disk exhaustion.

### 4.3 Activity Audit Logging
All system events, state transitions, allocation decisions, and security rejections are logged to `logs/sim_os.log` with timestamped records:
```
2026-11-23 21:07:20,832 - [SimOS] [INFO] (scheduler.py:117) - FCFS executed: 5 processes, Total Time: 28, Avg WT: 11.40
2026-11-23 21:07:20,854 - [SimOS] [WARNING] (deadlock.py:148) - Denied: Insufficient available resource A (3 requested, only 2 available).
```

---

## Phase 5: Documentation and Demonstration (20 Marks)

### 5.1 Interactive & Automated Demonstration Modes
SIM-OS provides two primary operating modes:
1. **Interactive TUI (`./run.sh` / `main.py`)**: A text-based console interface allowing users to step through individual algorithm simulations, supply custom parameters interactively, and view ASCII Gantt charts.
2. **Automated Batch CLI (`./run.sh --benchmark`)**: Executes all workloads, outputs performance metrics, and generates high-resolution figures.

### 5.2 Artifact Verification
- **Source Code**: Clean, fully typed, documented Python 3 and Bash scripts.
- **Trace Logs**: Stored in `output/traces/` (`cpu_scheduling_trace.txt`, `memory_management_trace.txt`, etc.).
- **Analytical Charts**: Saved in `output/charts/` (`cpu_scheduling_comparison.png`, `page_replacement_faults.png`, etc.).
- **Audit Logs**: Persisted in `logs/sim_os.log`.

### 5.3 System Demonstration Figures & Screenshots

#### Figure 1: Main Menu Interface
![Figure 1: Main Menu](output/screenshots/figure1_main_menu.png)

#### Figure 2: CPU Scheduling Input and Output (Gantt & Metrics)
![Figure 2: CPU Scheduling Input and Output](output/screenshots/figure2_cpu_scheduling.png)

#### Figure 3: Memory Partitioning and Banker's Deadlock Avoidance
![Figure 3: Memory Partitioning and Banker's Deadlock Avoidance](output/screenshots/figure3_memory_deadlock_storage.png)

#### Figure 4: Benchmark Charts and Comparison Analytics
![Figure 4: Comparative Benchmark Visualizations](output/screenshots/figure4_benchmark_charts.png)

#### Figure 5: Test Summary and Invalid-Input Handling Verification
![Figure 5: Test Summary & Exception Handling Verification](output/screenshots/figure5_test_summary_error_handling.png)

---

## Conclusion

The SIM-OS Capstone Project successfully fulfills all five development phases outlined in the academic requirements. By combining Python's algorithmic capabilities with POSIX Bash shell telemetry, the platform bridges theoretical operating system concepts with practical system-level observations. The modular design, comprehensive 37-test verification harness, and empirical visualizations provide a solid, publication-grade foundation for operating system education and performance analysis.
