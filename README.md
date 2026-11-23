# Operating Systems Laboratory – Complete Capstone Practical Portfolio

**Student Name:** Varun Chauhan  
**Roll Number:** 2401010276  
**Course:** B.Tech CSE Sec B  
**Academic Subject:** Operating Systems Lab (100-Mark Capstone Practical Submission)  

---

## 📌 Integrated Project Architecture

Per the project submission requirements, this repository is designed as **one unified, working application** that integrates the core resource-management components of an Operating System rather than an isolated set of unrelated programs.

```
os-assignment/
├── main.py                                           <-- Integrated Application & Menu Flow (Phases 1-3)
├── test_suite.py                                     <-- Automated Test Suite & Reliability Runner (Phase 4)
├── Report.md                                         <-- Complete 5-Phase Technical Project Report (Phase 5)
├── os_application.log                                <-- Centralized Activity & Audit Log File
├── README.md                                         <-- Master Documentation & Portfolio Index
│
├── section-1/                                        <-- Section 1: System Calls, Processes, CPU Scheduling and IPC
│   ├── q1-environment-setup/                         (verify_env.py, README.md, screenshots)
│   ├── q2-system-calls-processes/                    (process_syscalls.py, README.md, screenshots)
│   ├── q3-fcfs-sjf/                                  (scheduling_fcfs_sjf.py, README.md, screenshots)
│   ├── q4-priority-round-robin/                      (scheduling_priority_rr.py, README.md, screenshots)
│   └── q5-scheduling-threads-ipc/                    (metrics_threads_ipc.py, README.md, screenshots)
│
├── section-2/                                        <-- Section 2: Multithreading, Synchronization and Deadlock
│   ├── q1-threads-models/                            (threads_models.py, README.md, screenshots)
│   ├── q2-race-lock-semaphore/                       (race_lock_semaphore.py, README.md, screenshots)
│   ├── q3-classical-synchronization/                 (classical_synchronization.py, README.md, screenshots)
│   └── q4-deadlock-bankers/                          (deadlock_bankers.py, README.md, screenshots)
│
├── section-3/                                        <-- Section 3: Memory, Virtual Memory, Device & Disk Scheduling
│   ├── q1-contiguous-allocation-swapping/            (contiguous_swapping.py, README.md, screenshots)
│   ├── q2-paging-segmentation/                       (paging_segmentation.py, README.md, screenshots)
│   ├── q3-demand-paging-replacement/                 (page_replacement.py, README.md, screenshots)
│   ├── q4-device-management/                         (device_management.py, README.md, screenshots)
│   └── q5-disk-scheduling-swap/                      (disk_scheduling_swap.py, README.md, screenshots)
│
└── section-4/                                        <-- Section 4: File-System Interface and Implementation
    ├── q1-file-operations-sequential/                (file_operations.py, README.md, screenshots)
    ├── q2-direct-indexed-directory/                  (direct_indexed_directory.py, README.md, screenshots)
    ├── q3-file-allocation-methods/                   (file_allocation.py, README.md, screenshots)
    └── q4-free-space-access-control/                 (free_space_access_control.py, README.md, screenshots)
```

---

## 🎯 100-Mark Capstone Grading Rubric Alignment

| Phase | Meaningful Title | Task Completed in Repository | Submission Evidence | Marks |
| :---: | :--- | :--- | :--- | :---: |
| **Phase 1** | **System Design and Planning** | Modular architecture, unified I/O pipelines, data models for processes, memory frames, lock hierarchies. | Documented in [`Report.md`](./Report.md#phase-1-system-design-and-planning-20-marks), clean folder decomposition. | **20** |
| **Phase 2** | **Core Resource-Management Modules** | Reusable modules for CPU scheduling, memory management, deadlock handling, storage, and host Bash integration. | Unified interactive CLI flow in [`main.py`](./main.py) with menu system. | **20** |
| **Phase 3** | **Analysis and Comparison** | Common datasets run across algorithms, metrics tables (TAT, WT, RT, Hit Ratios, Cylinder Seek). | Detailed comparison tables in [`Report.md`](./Report.md#phase-3-analysis-and-comparison-20-marks) and module outputs. | **20** |
| **Phase 4** | **Testing and Reliability** | Automated testing of valid, boundary, and illegal inputs; structured activity logging. | [`test_suite.py`](./test_suite.py) (100% pass) and activity logging in [`os_application.log`](./os_application.log). | **20** |
| **Phase 5** | **Documentation and Demonstration** | Comprehensive documentation, execution steps, embedded terminal screenshots across all 18 practicals. | 18 individual practical `README.md` files with actual user screenshots. | **20** |
| **Total** | | | | **100** |

---

## 🚀 Execution Guide

### 1. Run the Integrated Application (Unified CLI)
```bash
python3 main.py
```
This launches the interactive main menu providing access to all 5 core resource-management suites, host Bash diagnostics, and test runners.

### 2. Run the Automated Test Suite
```bash
python3 test_suite.py
```
Executes comprehensive unit and boundary tests covering scheduling idle-period detection, tie-breaking, Banker's need matrices, paging/segmentation traps, thrashing limits, disk ranges, and storage allocation invariant guarantees.

---

## 🗂 Complete Practical Index & Navigation

### Section 1: System Calls, Processes, CPU Scheduling and IPC

| Q# | Practical Title | Script | Documentation | Screenshots |
| :---: | :--- | :---: | :---: | :---: |
| **Q1** | **Lab Environment Setup** | [`verify_env.py`](./section-1/q1-environment-setup/verify_env.py) | [`README.md`](./section-1/q1-environment-setup/README.md) | Included |
| **Q2** | **System Calls & Process Creation** | [`process_syscalls.py`](./section-1/q2-system-calls-processes/process_syscalls.py) | [`README.md`](./section-1/q2-system-calls-processes/README.md) | Included |
| **Q3** | **FCFS and SJF Scheduling** | [`scheduling_fcfs_sjf.py`](./section-1/q3-fcfs-sjf/scheduling_fcfs_sjf.py) | [`README.md`](./section-1/q3-fcfs-sjf/README.md) | Included |
| **Q4** | **Priority & Round Robin Scheduling** | [`scheduling_priority_rr.py`](./section-1/q4-priority-round-robin/scheduling_priority_rr.py) | [`README.md`](./section-1/q4-priority-round-robin/README.md) | Included |
| **Q5** | **Scheduling Metrics, Threads & IPC** | [`metrics_threads_ipc.py`](./section-1/q5-scheduling-threads-ipc/metrics_threads_ipc.py) | [`README.md`](./section-1/q5-scheduling-threads-ipc/README.md) | Included |

### Section 2: Multithreading, Synchronization and Deadlock

| Q# | Practical Title | Script | Documentation | Screenshots |
| :---: | :--- | :---: | :---: | :---: |
| **Q1** | **Thread Creation, Models & Benefits** | [`threads_models.py`](./section-2/q1-threads-models/threads_models.py) | [`README.md`](./section-2/q1-threads-models/README.md) | Included |
| **Q2** | **Race Condition, Lock & Semaphore** | [`race_lock_semaphore.py`](./section-2/q2-race-lock-semaphore/race_lock_semaphore.py) | [`README.md`](./section-2/q2-race-lock-semaphore/README.md) | Included |
| **Q3** | **Classical Synchronization Problems** | [`classical_synchronization.py`](./section-2/q3-classical-synchronization/classical_synchronization.py) | [`README.md`](./section-2/q3-classical-synchronization/README.md) | Included |
| **Q4** | **Deadlock Handling & Banker's Algorithm** | [`deadlock_bankers.py`](./section-2/q4-deadlock-bankers/deadlock_bankers.py) | [`README.md`](./section-2/q4-deadlock-bankers/README.md) | Included |

### Section 3: Memory, Virtual Memory, Device Management and Disk Scheduling

| Q# | Practical Title | Script | Documentation | Screenshots |
| :---: | :--- | :---: | :---: | :---: |
| **Q1** | **Contiguous Allocation & Swapping** | [`contiguous_swapping.py`](./section-3/q1-contiguous-allocation-swapping/contiguous_swapping.py) | [`README.md`](./section-3/q1-contiguous-allocation-swapping/README.md) | Included |
| **Q2** | **Paging and Segmentation** | [`paging_segmentation.py`](./section-3/q2-paging-segmentation/paging_segmentation.py) | [`README.md`](./section-3/q2-paging-segmentation/README.md) | Included |
| **Q3** | **Page Replacement & Thrashing** | [`page_replacement.py`](./section-3/q3-demand-paging-replacement/page_replacement.py) | [`README.md`](./section-3/q3-demand-paging-replacement/README.md) | Included |
| **Q4** | **Device Management Simulation** | [`device_management.py`](./section-3/q4-device-management/device_management.py) | [`README.md`](./section-3/q4-device-management/README.md) | Included |
| **Q5** | **Disk Scheduling & Swap Space** | [`disk_scheduling_swap.py`](./section-3/q5-disk-scheduling-swap/disk_scheduling_swap.py) | [`README.md`](./section-3/q5-disk-scheduling-swap/README.md) | Included |

### Section 4: File-System Interface and Implementation

| Q# | Practical Title | Script | Documentation | Screenshots |
| :---: | :--- | :---: | :---: | :---: |
| **Q1** | **File Operations & Sequential Access** | [`file_operations.py`](./section-4/q1-file-operations-sequential/file_operations.py) | [`README.md`](./section-4/q1-file-operations-sequential/README.md) | Included |
| **Q2** | **Direct/Indexed Access & Directories** | [`direct_indexed_directory.py`](./section-4/q2-direct-indexed-directory/direct_indexed_directory.py) | [`README.md`](./section-4/q2-direct-indexed-directory/README.md) | Included |
| **Q3** | **Contiguous, Linked & Indexed Allocation** | [`file_allocation.py`](./section-4/q3-file-allocation-methods/file_allocation.py) | [`README.md`](./section-4/q3-file-allocation-methods/README.md) | Included |
| **Q4** | **Free-Space & Access Control** | [`free_space_access_control.py`](./section-4/q4-free-space-access-control/free_space_access_control.py) | [`README.md`](./section-4/q4-free-space-access-control/README.md) | Included |
