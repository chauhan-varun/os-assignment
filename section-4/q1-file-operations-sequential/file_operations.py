#!/usr/bin/env python3
"""
OS Lab - Section 4, Q1: File Operations and Sequential Access
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import os
import stat
import time


SANDBOX_DIR = "./sandbox_fs_q1"


def setup_sandbox():
    if not os.path.exists(SANDBOX_DIR):
        os.makedirs(SANDBOX_DIR, exist_ok=True)
    print(f"[Sandbox] Dedicated directory created/verified: '{SANDBOX_DIR}'")


def demonstrate_file_operations():
    print("\n--- [1] Create, Write, Close, Reopen, and Sequential Read ---")
    orig_file = os.path.join(SANDBOX_DIR, "students_records.csv")

    # 1. Create and Write Structured Records
    print(f"Creating and writing structured records to '{orig_file}'...")
    with open(orig_file, "w") as f:
        f.write("RollNo,Name,Course,Semester\n")
        f.write("2401010276,Varun Chauhan,B.Tech CSE,4\n")
        f.write("2401010277,Aarav Sharma,B.Tech CSE,4\n")
        f.write("2401010278,Rohan Gupta,B.Tech IT,4\n")
    print("Initial records written successfully.")

    # 2. Sequential Read
    print(f"\nSequential Reading from '{orig_file}':")
    print("-" * 50)
    with open(orig_file, "r") as f:
        for line_no, line in enumerate(f, 1):
            print(f"  Line {line_no}: {line.strip()}")
    print("-" * 50)

    # 3. Append New Record Without Overwriting
    print("\n--- [2] Appending New Record ---")
    new_record = "2401010279,Priya Singh,B.Tech CSE,4\n"
    with open(orig_file, "a") as f:
        f.write(new_record)
    print(f"Appended: {new_record.strip()}")

    print("Verifying updated contents sequentially:")
    with open(orig_file, "r") as f:
        for line_no, line in enumerate(f, 1):
            print(f"  Line {line_no}: {line.strip()}")

    # 4. Rename File and List Directory
    print("\n--- [3] File Rename and Directory Listing ---")
    renamed_file = os.path.join(SANDBOX_DIR, "student_roster_archived.csv")
    os.rename(orig_file, renamed_file)
    print(f"Renamed '{orig_file}' -> '{renamed_file}'")

    print(f"Directory listing of '{SANDBOX_DIR}':")
    for item in os.listdir(SANDBOX_DIR):
        print(f"  * {item}")

    # 5. Inspect Metadata (Size, Permissions, Timestamps)
    print("\n--- [4] Inspect File Metadata ---")
    file_stat = os.stat(renamed_file)
    mode_octal = oct(stat.S_IMODE(file_stat.st_mode))
    mtime_str = time.ctime(file_stat.st_mtime)
    ctime_str = time.ctime(file_stat.st_ctime)

    print(f"Metadata for '{os.path.basename(renamed_file)}':")
    print(f"  - File Size          : {file_stat.st_size} bytes")
    print(f"  - Octal Permissions  : {mode_octal} ({stat.filemode(file_stat.st_mode)})")
    print(f"  - Inode Number       : {file_stat.st_ino}")
    print(f"  - Number of Links    : {file_stat.st_nlink}")
    print(f"  - Last Modified Time : {mtime_str}")
    print(f"  - Metadata Change    : {ctime_str}")

    # 6. Delete File and Error Handling
    print("\n--- [5] File Deletion and Safe Error Handling ---")
    os.remove(renamed_file)
    print(f"Deleted test file '{renamed_file}'.")

    # Error handling on deleted/missing file
    print("\nAttempting to read deleted file to demonstrate error handling:")
    try:
        with open(renamed_file, "r") as f:
            f.read()
    except FileNotFoundError as e:
        print(f"  -> Caught Expected Error: [FileNotFoundError] {e}")

    # Cleanup Sandbox
    if os.path.exists(SANDBOX_DIR):
        os.rmdir(SANDBOX_DIR)
        print(f"Cleanup: Removed sandbox directory '{SANDBOX_DIR}'.")


def main():
    print("=" * 65)
    print(" OS LAB - FILE OPERATIONS, SEQUENTIAL ACCESS & METADATA")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    setup_sandbox()
    demonstrate_file_operations()

    print("\n" + "=" * 65)
    print(" FILE OPERATIONS EXPERIMENT COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    main()
