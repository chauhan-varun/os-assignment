# Operating Systems Lab Assignments

**Name:** Varun Chauhan  
**Roll Number:** 2401010276  
**Course:** B.Tech CSE Sec B  

This repository contains my submissions for the Operating Systems Lab assignments.

## Directory Structure & Tasks

### [1. System Calls and Process Creation](./1)
A Python script demonstrating fundamental OS concepts, including:
- Spawning a child process using `os.fork()`
- Process synchronization using `os.wait()`
- Executing Linux commands from a child process
- File I/O operations and interacting with device interfaces like `/dev/null`
- Safe error handling for missing files

### [2. OS Lab Environment Setup](./2)
A Python verification script that confirms the presence and proper configuration of:
- Python 3.12.14
- Ubuntu Linux / Windows Subsystem for Linux (WSL)
- Visual Studio Code

### [3. FCFS and SJF Scheduling](./3)
An interactive simulation of CPU scheduling algorithms:
- First-Come, First-Served (FCFS)
- Non-preemptive Shortest Job First (SJF)
- Evaluates both algorithms on the exact same dataset of processes, factoring in arrival times, burst times, and proper tie-breaking rules.
