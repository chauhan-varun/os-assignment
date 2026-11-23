#!/usr/bin/env python3
"""
OS Lab - Section 4, Q2: Direct, Indexed Access and Directory Structures
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import os
import struct


# =====================================================================
# [PART 1] Direct and Indexed File Access (Fixed-Size Records)
# =====================================================================
RECORD_FORMAT = "i20s10s"  # int (ID), string 20 (Name), string 10 (Dept)
RECORD_SIZE = struct.calcsize(RECORD_FORMAT)  # Exact fixed byte length


def demonstrate_direct_and_indexed_access():
    print("=" * 65)
    print(" [PART 1] DIRECT AND INDEXED FILE ACCESS")
    print("=" * 65)
    filename = "records_binary.dat"

    records = [
        (101, b"Varun Chauhan       ", b"CSE       "),
        (102, b"Aarav Sharma        ", b"CSE       "),
        (103, b"Rohan Gupta         ", b"IT        "),
        (104, b"Priya Singh         ", b"ECE       "),
    ]

    print(f"Record Format: (ID: int, Name: 20 bytes, Dept: 10 bytes) -> Fixed Record Size: {RECORD_SIZE} bytes")

    # 1. Write Fixed-Size Binary Records and Build Index
    index_table = {}  # Key (ID) -> File Byte Offset
    with open(filename, "wb") as f:
        for idx, r in enumerate(records):
            offset = f.tell()
            packed_bytes = struct.pack(RECORD_FORMAT, *r)
            f.write(packed_bytes)
            index_table[r[0]] = offset
            print(f"  Written Record {r[0]} at Offset {offset:3d} bytes.")

    print(f"\nConstructed In-Memory Index Table: {index_table}")

    # 2. Direct Access by Record Number
    target_record_idx = 2  # 0-indexed -> 3rd record (103)
    target_offset = target_record_idx * RECORD_SIZE
    print(f"\nDirect Access to Record #{target_record_idx + 1}:")
    print(f"  Calculated Byte Location = {target_record_idx} * {RECORD_SIZE} = {target_offset} bytes.")

    with open(filename, "rb") as f:
        f.seek(target_offset)
        raw_data = f.read(RECORD_SIZE)
        r_id, r_name, r_dept = struct.unpack(RECORD_FORMAT, raw_data)
        print(f"  -> Direct Retrieved: ID={r_id}, Name='{r_name.decode().strip()}', Dept='{r_dept.decode().strip()}'")

    # 3. Indexed Access by Search Key
    search_key = 104
    print(f"\nIndexed Access for Key ID = {search_key}:")
    if search_key in index_table:
        byte_loc = index_table[search_key]
        print(f"  Index hit! Key {search_key} located at byte offset {byte_loc}.")
        with open(filename, "rb") as f:
            f.seek(byte_loc)
            raw = f.read(RECORD_SIZE)
            r_id, r_name, r_dept = struct.unpack(RECORD_FORMAT, raw)
            print(f"  -> Index Retrieved: ID={r_id}, Name='{r_name.decode().strip()}', Dept='{r_dept.decode().strip()}'")
    else:
        print(f"  Key {search_key} not found in index.")

    if os.path.exists(filename):
        os.remove(filename)


# =====================================================================
# [PART 2] Directory Structures Simulation (Single, Two-Level, Tree)
# =====================================================================
class DirectoryNode:
    def __init__(self, name, is_dir=True):
        self.name = name
        self.is_dir = is_dir
        self.children = {} if is_dir else None  # name -> DirectoryNode

    def add_child(self, name, is_dir=True):
        if not self.is_dir:
            print(f"Error: '{self.name}' is a file, not a directory.")
            return False
        if name in self.children:
            print(f"Error: Duplicate entry '{name}' rejected in '{self.name}'.")
            return False
        self.children[name] = DirectoryNode(name, is_dir)
        print(f"  Created {'Directory' if is_dir else 'File'} '{name}' inside '{self.name}'.")
        return True

    def delete_child(self, name):
        if name in self.children:
            del self.children[name]
            print(f"  Deleted '{name}' from '{self.name}'.")
            return True
        print(f"  Error: '{name}' not found in '{self.name}'.")
        return False

    def display_tree(self, prefix=""):
        node_type = "[DIR]" if self.is_dir else "[FILE]"
        print(f"{prefix}{node_type} {self.name}")
        if self.is_dir:
            for child in sorted(self.children.values(), key=lambda c: (not c.is_dir, c.name)):
                child.display_tree(prefix + "    ")


def demonstrate_directory_structures():
    print("\n" + "=" * 65)
    print(" [PART 2] DIRECTORY STRUCTURE SIMULATION")
    print("=" * 65)

    # 1. Single-Level Directory Simulation
    print("--- 1. Single-Level Directory Simulation ---")
    single_root = DirectoryNode("SingleLevelRoot")
    single_root.add_child("file1.txt", is_dir=False)
    single_root.add_child("file2.txt", is_dir=False)
    # Duplicate rejection
    print("Attempting duplicate filename creation:")
    single_root.add_child("file1.txt", is_dir=False)
    single_root.display_tree()

    # 2. Hierarchical Tree Directory Structure
    print("\n--- 2. Hierarchical Tree Directory Structure ---")
    root = DirectoryNode("root")
    root.add_child("home", is_dir=True)
    root.add_child("etc", is_dir=True)
    root.add_child("var", is_dir=True)

    home_node = root.children["home"]
    home_node.add_child("user_varun", is_dir=True)
    home_node.add_child("user_guest", is_dir=True)

    varun_node = home_node.children["user_varun"]
    varun_node.add_child("lab_report.pdf", is_dir=False)
    varun_node.add_child("main.py", is_dir=False)
    varun_node.add_child("projects", is_dir=True)

    proj_node = varun_node.children["projects"]
    proj_node.add_child("os_simulation.py", is_dir=False)

    print("\nFinal Parent-Child Directory Tree Structure:")
    print("-" * 50)
    root.display_tree()
    print("-" * 50)

    # Delete operation
    print("\nDeleting 'user_guest' directory from '/home':")
    home_node.delete_child("user_guest")
    root.display_tree()


def main():
    print("=" * 65)
    print(" OS LAB - DIRECT/INDEXED ACCESS & DIRECTORY STRUCTURES")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    demonstrate_direct_and_indexed_access()
    demonstrate_directory_structures()


if __name__ == "__main__":
    main()
