#!/usr/bin/env python3
"""
OS Lab - Section 3, Q4: Device Management Simulation
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

from collections import deque
import time


class Device:
    def __init__(self, name, dev_type):
        self.name = name
        self.dev_type = dev_type  # 'Dedicated', 'Shared', 'Virtual'
        self.status = "IDLE"      # 'IDLE' or 'BUSY'
        self.owner = None
        self.queue = deque()

    def request_access(self, process_id):
        print(f"\n[Event: Request] Process '{process_id}' requesting access to {self.dev_type} Device '{self.name}'.")
        if self.dev_type == "Dedicated":
            if self.status == "IDLE":
                self.status = "BUSY"
                self.owner = process_id
                print(f"  -> GRANTED: Process '{process_id}' assigned Dedicated Device '{self.name}'.")
            else:
                print(f"  -> DENIED: Dedicated Device '{self.name}' currently locked by '{self.owner}'.")
                self.queue.append(process_id)
                print(f"  -> Enqueued '{process_id}' into device waiting queue: {list(self.queue)}")
        elif self.dev_type == "Shared":
            if self.status == "IDLE":
                self.status = "BUSY"
                self.owner = process_id
                print(f"  -> GRANTED: Process '{process_id}' accessing Shared Device '{self.name}'.")
            else:
                self.queue.append(process_id)
                print(f"  -> QUEUED: Process '{process_id}' enqueued (FCFS Shared Queue: {list(self.queue)})")

    def release_access(self, process_id):
        print(f"\n[Event: Release] Process '{process_id}' releasing {self.dev_type} Device '{self.name}'.")
        if self.owner == process_id:
            self.owner = None
            if self.queue:
                next_proc = self.queue.popleft()
                self.owner = next_proc
                self.status = "BUSY"
                print(f"  -> REASSIGNED: Device '{self.name}' immediately allocated to next waiting process: '{next_proc}'.")
            else:
                self.status = "IDLE"
                print(f"  -> Device '{self.name}' is now IDLE.")
        else:
            print(f"  -> Warning: Process '{process_id}' does not own device '{self.name}'.")

    def print_state(self):
        print(f"  [Device Status] {self.name} ({self.dev_type}) | Status: {self.status} | Owner: {self.owner} | Queue: {list(self.queue)}")


class FiniteDeviceBuffer:
    def __init__(self, capacity=3):
        self.capacity = capacity
        self.buffer = []

    def produce(self, item, sender):
        print(f"\n[Buffer Insert Attempt] '{sender}' -> Item: '{item}'")
        if len(self.buffer) >= self.capacity:
            print(f"  -> [BUFFER FULL] Cannot insert '{item}'. Buffer capacity ({self.capacity}) reached!")
            return False
        self.buffer.append(item)
        print(f"  -> Inserted. Buffer contents: {self.buffer} (Size: {len(self.buffer)}/{self.capacity})")
        return True

    def consume(self, receiver):
        print(f"\n[Buffer Remove Attempt] '{receiver}' requesting item...")
        if not self.buffer:
            print("  -> [BUFFER EMPTY] No items available to consume.")
            return None
        item = self.buffer.pop(0)
        print(f"  -> Removed '{item}'. Buffer contents: {self.buffer} (Size: {len(self.buffer)}/{self.capacity})")
        return item


def demonstrate_device_management():
    print("=" * 65)
    print(" OS LAB - DEVICE MANAGEMENT SIMULATION")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    # 1. Dedicated Device Demonstration
    print("\n--- 1. Dedicated Device (Laser Printer) ---")
    printer = Device("LaserPrinter_01", "Dedicated")
    printer.print_state()

    printer.request_access("Process_P1")
    printer.print_state()

    printer.request_access("Process_P2")
    printer.request_access("Process_P3")
    printer.print_state()

    printer.release_access("Process_P1")
    printer.print_state()

    printer.release_access("Process_P2")
    printer.print_state()

    printer.release_access("Process_P3")
    printer.print_state()

    # 2. Shared Device Demonstration
    print("\n--- 2. Shared Device (NVMe Solid State Disk) ---")
    disk = Device("NVMe_Storage", "Shared")
    disk.request_access("Database_Server")
    disk.request_access("Web_Server")
    disk.request_access("Backup_Agent")
    disk.print_state()

    disk.release_access("Database_Server")
    disk.print_state()

    # 3. Virtual Device & Finite Spooling Buffer
    print("\n--- 3. Virtual Device & Spooling Buffer Simulation ---")
    print("Software Abstraction: Spooler intercepts slow printer requests")
    print("and decouples the high-speed CPU from the slow physical print engine.\n")

    spool_buf = FiniteDeviceBuffer(capacity=3)
    spool_buf.produce("Doc_1.pdf", "P1")
    spool_buf.produce("Doc_2.pdf", "P2")
    spool_buf.produce("Doc_3.pdf", "P3")
    # Buffer is now full
    spool_buf.produce("Doc_4.pdf", "P4")

    # Spooler consumes items for printing
    spool_buf.consume("Printer_Daemon")
    # Now space is available
    spool_buf.produce("Doc_4.pdf", "P4")

    spool_buf.consume("Printer_Daemon")
    spool_buf.consume("Printer_Daemon")
    spool_buf.consume("Printer_Daemon")
    # Buffer is now empty
    spool_buf.consume("Printer_Daemon")

    print("\n--- 4. CPU & Device Independence Explanation ---")
    print("1. Direct Memory Access (DMA): Transfers data blocks directly between memory and")
    print("   device controllers without constant CPU register intervention.")
    print("2. Interrupt-Driven I/O: The CPU issues an I/O command and continues executing")
    print("   other user processes. Once the device finishes, it asserts an interrupt")
    print("   request (IRQ), invoking the OS Interrupt Service Routine (ISR).")


def main():
    demonstrate_device_management()


if __name__ == "__main__":
    main()
