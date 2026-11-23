#!/usr/bin/env python3
"""
OS Lab - Section 1, Q2: System Calls and Process Creation
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import os
import sys
import subprocess


def demonstrate_file_operations():
    print("\n--- [A] Controlled File Operations (Create, Write, Read, Close) ---")
    filename = "controlled_test_file.txt"

    # 1. Create and Write
    print(f"[File] Creating and opening '{filename}' for writing...")
    fd = os.open(filename, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o644)
    record = b"Operating Systems Lab: System Call Verification Record.\nStudent: Varun Chauhan (2401010276)\n"
    bytes_written = os.write(fd, record)
    os.close(fd)
    print(f"[File] Successfully wrote {bytes_written} bytes and closed file descriptor.")

    # 2. Read and Verify
    print(f"[File] Reopening '{filename}' to read contents...")
    fd = os.open(filename, os.O_RDONLY)
    read_data = os.read(fd, 1024).decode("utf-8")
    os.close(fd)
    print(f"[File Content]:\n{read_data.strip()}")

    # Cleanup after demo
    if os.path.exists(filename):
        os.remove(filename)
        print(f"[File] Cleanup: Removed '{filename}'.")


def demonstrate_device_interfaces():
    print("\n--- [B] Device & Special Kernel Interface Inspection ---")

    # 1. Inspecting /dev/null
    print("[Device /dev/null] Testing write to null device...")
    try:
        with open("/dev/null", "w") as dev_null:
            dev_null.write("Data written to /dev/null should be silently discarded.\n")
        print("[Device /dev/null] Successfully written to /dev/null (data discarded as expected).")
    except Exception as e:
        print(f"[Device /dev/null] Error: {e}")

    # 2. Inspecting /dev/zero
    print("[Device /dev/zero] Reading 16 null bytes from /dev/zero...")
    try:
        with open("/dev/zero", "rb") as dev_zero:
            zero_bytes = dev_zero.read(16)
        print(f"[Device /dev/zero] Bytes read: {list(zero_bytes)}")
    except Exception as e:
        print(f"[Device /dev/zero] Error: {e}")

    # 3. Inspecting /proc/version
    if os.path.exists("/proc/version"):
        try:
            with open("/proc/version", "r") as f:
                kernel_info = f.readline().strip()
            print(f"[Kernel Interface /proc/version]:\n  {kernel_info}")
        except Exception as e:
            print(f"[Kernel Interface /proc/version] Error: {e}")


def demonstrate_error_handling():
    print("\n--- [C] Error Handling for Invalid Paths & Failed Operations ---")
    invalid_path = "/nonexistent_root_dir/restricted/fake_file.txt"
    print(f"[Error Handling] Attempting to open invalid path: '{invalid_path}'...")
    try:
        with open(invalid_path, "r") as f:
            f.read()
    except FileNotFoundError as fnf:
        print(f"[Error Handled Successfully] FileNotFoundError caught: {fnf}")
    except PermissionError as pe:
        print(f"[Error Handled Successfully] PermissionError caught: {pe}")
    except Exception as ex:
        print(f"[Error Handled Successfully] Exception caught: {type(ex).__name__}: {ex}")


def demonstrate_process_creation():
    print("\n--- [D] Process Creation, PID/PPID, Exec, and Wait ---")
    parent_pid = os.getpid()
    print(f"[Parent Process] Running PID: {parent_pid}")

    pid = os.fork()

    if pid == 0:
        # Inside Child Process
        child_pid = os.getpid()
        child_ppid = os.getppid()
        print(f"  [Child Process] Spawned successfully!")
        print(f"  [Child Process] PID: {child_pid}, PPID: {child_ppid}")
        print("  [Child Process] Executing harmless Linux command: 'uname -s -r -m'")
        sys.stdout.flush()
        
        # Execute harmless Linux command
        subprocess.run(["uname", "-s", "-r", "-m"])
        print("  [Child Process] Task finished. Exiting with status code 0.")
        os._exit(0)
    elif pid > 0:
        # Inside Parent Process
        print(f"[Parent Process] Forked child process with PID: {pid}. Waiting for child to terminate...")
        waited_pid, status = os.waitpid(pid, 0)
        exit_code = os.waitstatus_to_exitcode(status) if hasattr(os, "waitstatus_to_exitcode") else (status >> 8)
        print(f"[Parent Process] Reaped child {waited_pid} with exit code: {exit_code}")
    else:
        print("[Parent Process] Fork failed!")
        sys.exit(1)


def main():
    print("=" * 65)
    print(" OS LAB - SYSTEM CALLS, PROCESS CREATION & DEVICE INTERFACES")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    demonstrate_file_operations()
    demonstrate_device_interfaces()
    demonstrate_error_handling()
    demonstrate_process_creation()

    print("\n" + "=" * 65)
    print(" DEMONSTRATION COMPLETE: ALL REQUIREMENTS MET")
    print("=" * 65)


if __name__ == "__main__":
    main()
