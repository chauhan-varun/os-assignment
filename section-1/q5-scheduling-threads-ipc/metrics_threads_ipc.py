#!/usr/bin/env python3
"""
OS Lab - Section 1, Q5: Scheduling Metrics, Threads and IPC
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import multiprocessing as mp
import threading
import time
from collections import deque


def render_ascii_gantt(chart_items):
    """
    Renders an ASCII Gantt chart with exact time boundaries.
    chart_items: list of dicts with keys 'label', 'start', 'end'
    """
    print("\nGantt Chart Representation:")
    top_bar = "+"
    label_bar = "|"
    time_markers = [str(chart_items[0]["start"])]
    marker_line = str(chart_items[0]["start"])

    for item in chart_items:
        duration = item["end"] - item["start"]
        width = max(len(item["label"]) + 2, duration * 3)
        top_bar += "-" * width + "+"
        label_bar += f"{item['label']:^{width}}|"
        time_str = str(item["end"])
        spaces_needed = width - len(time_str) + 1
        marker_line += " " * (width - len(time_str) + 1) + time_str

    print(top_bar)
    print(label_bar)
    print(top_bar)
    # Print aligned timeline
    timeline = ""
    curr = 0
    for item in chart_items:
        duration = item["end"] - item["start"]
        width = max(len(item["label"]) + 2, duration * 3)
        if not timeline:
            timeline += str(item["start"])
        pad = width - len(str(item["end"]))
        timeline += " " * pad + str(item["end"])
    print(timeline)


def demonstrate_scheduling_metrics():
    print("=" * 65)
    print(" [PART 1] SCHEDULING METRICS & ASCII GANTT CHART (ROUND ROBIN)")
    print("=" * 65)

    processes = [
        {"pid": "P1", "at": 0, "bt": 5},
        {"pid": "P2", "at": 1, "bt": 4},
        {"pid": "P3", "at": 2, "bt": 2},
        {"pid": "P4", "at": 14, "bt": 3},  # Creates CPU idle period from 11 to 14
    ]
    quantum = 3

    print(f"Dataset with Time Quantum q = {quantum}:")
    for p in processes:
        print(f"  {p['pid']}: Arrival={p['at']}, Burst={p['bt']}")

    rem_bt = {p["pid"]: p["bt"] for p in processes}
    first_start = {}
    completion_time = {}
    timeline = []
    ready_q = deque()
    unadded = list(processes)
    curr_t = 0

    while ready_q or unadded:
        if not ready_q:
            next_p = unadded[0]
            if curr_t < next_p["at"]:
                timeline.append({"label": "IDLE", "start": curr_t, "end": next_p["at"]})
                curr_t = next_p["at"]
            while unadded and unadded[0]["at"] <= curr_t:
                ready_q.append(unadded.pop(0)["pid"])

        pid = ready_q.popleft()
        if pid not in first_start:
            first_start[pid] = curr_t

        exec_len = min(quantum, rem_bt[pid])
        start_t = curr_t
        curr_t += exec_len
        rem_bt[pid] -= exec_len
        timeline.append({"label": pid, "start": start_t, "end": curr_t})

        while unadded and unadded[0]["at"] <= curr_t:
            ready_q.append(unadded.pop(0)["pid"])

        if rem_bt[pid] > 0:
            ready_q.append(pid)
        else:
            completion_time[pid] = curr_t

    render_ascii_gantt(timeline)

    # Detailed metrics calculation
    print("\nCalculated Metrics:")
    print("-" * 70)
    print(f"{'PID':<6}{'AT':<6}{'BT':<6}{'CT':<6}{'TAT (CT-AT)':<15}{'WT (TAT-BT)':<15}{'RT (First-AT)':<12}")
    print("-" * 70)
    tot_tat = tot_wt = tot_rt = 0
    for p in processes:
        pid = p["pid"]
        ct = completion_time[pid]
        tat = ct - p["at"]
        wt = tat - p["bt"]
        rt = first_start[pid] - p["at"]
        tot_tat += tat
        tot_wt += wt
        tot_rt += rt
        print(f"{pid:<6}{p['at']:<6}{p['bt']:<6}{ct:<6}{tat:<15}{wt:<15}{rt:<12}")
    n = len(processes)
    print("-" * 70)
    print(f"Average Turnaround Time (TAT) : {tot_tat/n:.2f}")
    print(f"Average Waiting Time    (WT)  : {tot_wt/n:.2f}")
    print(f"Average Response Time   (RT)  : {tot_rt/n:.2f}")


def worker_task(thread_id, task_slice, shared_results):
    t_native_id = threading.get_native_id() if hasattr(threading, "get_native_id") else threading.get_ident()
    thread_name = threading.current_thread().name
    print(f"  -> [{thread_name} (Native ID: {t_native_id})] Processing data slice: {task_slice}")
    partial_sum = sum(x * x for x in task_slice)
    time.sleep(0.05)  # Simulate compute workload
    shared_results[thread_id] = partial_sum
    print(f"  <- [{thread_name}] Completed. Partial sum of squares = {partial_sum}")


def demonstrate_threading():
    print("\n" + "=" * 65)
    print(" [PART 2] MULTITHREADING DEMONSTRATION USING PYTHON THREADING")
    print("=" * 65)
    numbers = list(range(1, 21))
    print(f"Dataset to process: {numbers} (Total {len(numbers)} numbers)")

    # Divide workload across 3 worker threads
    slices = [numbers[0:7], numbers[7:14], numbers[14:20]]
    threads = []
    results = {}

    for i, s in enumerate(slices):
        t = threading.Thread(target=worker_task, args=(f"Worker-{i+1}", s, results), name=f"Thread-{i+1}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_sum_of_squares = sum(results.values())
    expected = sum(x * x for x in numbers)
    print(f"\nAll worker threads finished. Total aggregated sum: {total_sum_of_squares} (Expected: {expected})")
    print(f"Thread work breakdown: {results}")


def sender_process(pipe_conn, send_queue):
    sender_pid = mp.current_process().pid
    print(f"  [Sender Process (PID {sender_pid})] Generating OS status payload...")
    msg_pipe = {"event": "CPU_TEMP_ALERT", "level": "WARNING", "temp_c": 78.4}
    pipe_conn.send(msg_pipe)
    print(f"  [Sender Process (PID {sender_pid})] Transmitted via Pipe: {msg_pipe}")

    msg_queue = ["Memory_Usage: 64%", "Active_Threads: 12", "Swap_Free: 4096MB"]
    send_queue.put(msg_queue)
    print(f"  [Sender Process (PID {sender_pid})] Transmitted via Queue: {msg_queue}")
    pipe_conn.close()


def receiver_process(pipe_conn, recv_queue):
    receiver_pid = mp.current_process().pid
    print(f"  [Receiver Process (PID {receiver_pid})] Waiting to receive data...")
    received_from_pipe = pipe_conn.recv()
    print(f"  [Receiver Process (PID {receiver_pid})] Received via Pipe: {received_from_pipe}")

    received_from_queue = recv_queue.get()
    print(f"  [Receiver Process (PID {receiver_pid})] Received via Queue: {received_from_queue}")
    pipe_conn.close()


def demonstrate_ipc():
    print("\n" + "=" * 65)
    print(" [PART 3] INTER-PROCESS COMMUNICATION (IPC) VIA PIPE & QUEUE")
    print("=" * 65)

    pipe_parent, pipe_child = mp.Pipe()
    queue = mp.Queue()

    p_sender = mp.Process(target=sender_process, args=(pipe_child, queue), name="SenderProc")
    p_receiver = mp.Process(target=receiver_process, args=(pipe_parent, queue), name="ReceiverProc")

    p_receiver.start()
    p_sender.start()

    p_sender.join()
    p_receiver.join()
    print("\nIPC demonstration successfully completed between independent processes.")


def main():
    print("=" * 65)
    print(" OS LAB - SCHEDULING METRICS, MULTITHREADING AND IPC")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    demonstrate_scheduling_metrics()
    demonstrate_threading()
    demonstrate_ipc()

    print("\n" + "=" * 65)
    print(" LAB EXPERIMENT COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    main()
