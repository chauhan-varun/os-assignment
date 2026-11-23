#!/usr/bin/env python3
"""
OS Lab - Section 2, Q3: Classical Synchronization Problems
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import threading
import time
import random


# =====================================================================
# 1. Producer-Consumer Problem (Finite Circular Buffer with Semaphores)
# =====================================================================
BUFFER_CAPACITY = 4
TOTAL_ITEMS_TO_PRODUCE = 6


def run_producer_consumer():
    print("\n" + "=" * 65)
    print(" 1. PRODUCER-CONSUMER PROBLEM (CIRCULAR BUFFER)")
    print("=" * 65)
    print(f"Buffer Capacity: {BUFFER_CAPACITY}, Total Items: {TOTAL_ITEMS_TO_PRODUCE}")

    buffer = [None] * BUFFER_CAPACITY
    in_idx = 0
    out_idx = 0

    mutex = threading.Lock()
    empty_slots = threading.Semaphore(BUFFER_CAPACITY)
    full_slots = threading.Semaphore(0)

    def producer():
        nonlocal in_idx
        for item_id in range(1, TOTAL_ITEMS_TO_PRODUCE + 1):
            time.sleep(random.uniform(0.01, 0.03))
            empty_slots.acquire()
            with mutex:
                buffer[in_idx] = item_id
                print(f"  [Producer] Inserted item {item_id:2d} at index {in_idx}. Buffer: {[x for x in buffer if x is not None]}")
                in_idx = (in_idx + 1) % BUFFER_CAPACITY
            full_slots.release()
        print("  [Producer] Finished production.")

    def consumer():
        nonlocal out_idx
        for _ in range(TOTAL_ITEMS_TO_PRODUCE):
            time.sleep(random.uniform(0.02, 0.04))
            full_slots.acquire()
            with mutex:
                item = buffer[out_idx]
                buffer[out_idx] = None
                print(f"  [Consumer] Removed item  {item:2d} from index {out_idx}. Buffer: {[x for x in buffer if x is not None]}")
                out_idx = (out_idx + 1) % BUFFER_CAPACITY
            empty_slots.release()
        print("  [Consumer] Finished consumption.")

    t_prod = threading.Thread(target=producer, name="Producer")
    t_cons = threading.Thread(target=consumer, name="Consumer")
    t_prod.start()
    t_cons.start()
    t_prod.join()
    t_cons.join()
    print("Producer-Consumer completed successfully without deadlock or buffer overflow.")


# =====================================================================
# 2. Readers-Writers Problem (Reader Preference with Protected Count)
# =====================================================================
def run_readers_writers():
    print("\n" + "=" * 65)
    print(" 2. READERS-WRITERS PROBLEM (EXCLUSIVE WRITING, CONCURRENT READING)")
    print("=" * 65)

    shared_data = 100
    reader_count = 0
    rc_mutex = threading.Lock()
    write_lock = threading.Lock()

    def reader(reader_id, iterations=2):
        nonlocal reader_count
        for i in range(iterations):
            time.sleep(random.uniform(0.01, 0.03))
            with rc_mutex:
                reader_count += 1
                if reader_count == 1:
                    write_lock.acquire()  # First reader blocks writers
                print(f"  [Reader {reader_id}] Entered. Active Readers: {reader_count}")

            # Critical section (Reading)
            print(f"    -> [Reader {reader_id}] Read shared value: {shared_data}")
            time.sleep(0.01)

            with rc_mutex:
                reader_count -= 1
                print(f"  [Reader {reader_id}] Exited. Remaining Readers: {reader_count}")
                if reader_count == 0:
                    write_lock.release()  # Last reader unblocks writers

    def writer(writer_id, iterations=2):
        nonlocal shared_data
        for i in range(iterations):
            time.sleep(random.uniform(0.02, 0.04))
            write_lock.acquire()
            # Exclusive Critical Section (Writing)
            shared_data += 10
            print(f"  *** [Writer {writer_id}] EXCLUSIVE WRITE: Updated shared data to {shared_data} ***")
            time.sleep(0.01)
            write_lock.release()

    threads = []
    threads.append(threading.Thread(target=reader, args=(1,)))
    threads.append(threading.Thread(target=writer, args=(1,)))
    threads.append(threading.Thread(target=reader, args=(2,)))
    threads.append(threading.Thread(target=writer, args=(2,)))
    threads.append(threading.Thread(target=reader, args=(3,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"Readers-Writers completed. Final shared data value: {shared_data}")


# =====================================================================
# 3. Dining Philosophers Problem (Deadlock Prevention via Resource Hierarchy)
# =====================================================================
def run_dining_philosophers():
    print("\n" + "=" * 65)
    print(" 3. DINING PHILOSOPHERS PROBLEM (RESOURCE HIERARCHY SOLUTION)")
    print("=" * 65)
    print("Deadlock Prevention: Asymmetric fork acquisition (lower numbered fork acquired first).")

    num_philosophers = 5
    forks = [threading.Lock() for _ in range(num_philosophers)]
    iterations = 2

    def philosopher(p_id):
        left_fork = p_id
        right_fork = (p_id + 1) % num_philosophers

        # Resource ordering to prevent circular wait: always pick lower index first
        first_fork = min(left_fork, right_fork)
        second_fork = max(left_fork, right_fork)

        for it in range(iterations):
            # Thinking
            print(f"  [Philosopher {p_id}] Thinking...")
            time.sleep(random.uniform(0.01, 0.03))

            # Pick forks
            with forks[first_fork]:
                print(f"  [Philosopher {p_id}] Acquired Fork {first_fork}")
                with forks[second_fork]:
                    print(f"  [Philosopher {p_id}] Acquired Fork {second_fork} -> EATING (Meal {it+1})")
                    time.sleep(0.02)
                    print(f"  [Philosopher {p_id}] Finished eating meal {it+1}. Released Fork {second_fork}")
                print(f"  [Philosopher {p_id}] Released Fork {first_fork}")

        print(f"  [Philosopher {p_id}] Fully satisfied and leaves table.")

    threads = [threading.Thread(target=philosopher, args=(i,), name=f"Phil-{i}") for i in range(num_philosophers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("All philosophers dined successfully without circular wait or deadlock.")


def main():
    print("=" * 65)
    print(" OS LAB - CLASSICAL SYNCHRONIZATION PROBLEMS")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    run_producer_consumer()
    run_readers_writers()
    run_dining_philosophers()

    print("\n" + "=" * 65)
    print(" ALL THREE CLASSICAL SYNCHRONIZATION PROBLEMS RESOLVED SAFELY")
    print("=" * 65)


if __name__ == "__main__":
    main()
