#!/usr/bin/env python3
"""
OS Lab - Section 4, Q3: Contiguous, Linked and Indexed Allocation
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import copy


TOTAL_DISK_BLOCKS = 32


class SimulatedDisk:
    def __init__(self, size=TOTAL_DISK_BLOCKS):
        self.size = size
        # None = free, or string filename
        self.blocks = [None] * size
        self.file_table = {}

    def get_free_blocks(self):
        return [i for i, b in enumerate(self.blocks) if b is None]

    def display_disk_map(self):
        print("\nDisk Block Map (Total 32 Blocks):")
        line = ""
        for i, occupant in enumerate(self.blocks):
            label = occupant if occupant else "."
            line += f"[{i:02d}:{label:<4}] "
            if (i + 1) % 8 == 0:
                print("  " + line)
                line = ""
        free_count = self.blocks.count(None)
        print(f"Free Blocks: {free_count}/{self.size} (Allocated: {self.size - free_count})\n")


# =====================================================================
# 1. Contiguous Allocation
# =====================================================================
def allocate_contiguous(disk, filename, num_blocks):
    print(f"\n[Contiguous Allocation Request] File '{filename}', Size: {num_blocks} blocks")
    if filename in disk.file_table:
        print(f"  Error: Duplicate file '{filename}' rejected.")
        return False
    if num_blocks <= 0:
        print("  Error: Block count must be positive.")
        return False

    # Find contiguous run of free blocks
    start_idx = -1
    consecutive = 0
    for i in range(disk.size):
        if disk.blocks[i] is None:
            if consecutive == 0:
                start_idx = i
            consecutive += 1
            if consecutive == num_blocks:
                break
        else:
            consecutive = 0
            start_idx = -1

    if consecutive < num_blocks:
        print(f"  REJECTED: Insufficient contiguous space! (Requested {num_blocks} contiguous blocks)")
        return False

    # Allocate blocks
    for i in range(start_idx, start_idx + num_blocks):
        disk.blocks[i] = filename

    # Metadata: Start block and length
    disk.file_table[filename] = {"method": "Contiguous", "start": start_idx, "length": num_blocks}
    print(f"  -> SUCCESS: Allocated blocks [{start_idx} -> {start_idx + num_blocks - 1}] to '{filename}'.")
    return True


# =====================================================================
# 2. Linked Allocation
# =====================================================================
def allocate_linked(disk, filename, num_blocks):
    print(f"\n[Linked Allocation Request] File '{filename}', Size: {num_blocks} blocks")
    if filename in disk.file_table:
        print(f"  Error: Duplicate file '{filename}' rejected.")
        return False
    if num_blocks <= 0:
        print("  Error: Block count must be positive.")
        return False

    free_blocks = disk.get_free_blocks()
    if len(free_blocks) < num_blocks:
        print(f"  REJECTED: Insufficient disk space! Free: {len(free_blocks)}, Needed: {num_blocks}")
        return False

    allocated = free_blocks[:num_blocks]
    for b in allocated:
        disk.blocks[b] = filename

    # Metadata: Start Block, End Block, and Linked Pointers
    links = {allocated[i]: allocated[i + 1] for i in range(len(allocated) - 1)}
    links[allocated[-1]] = -1  # EOF
    disk.file_table[filename] = {
        "method": "Linked",
        "start": allocated[0],
        "end": allocated[-1],
        "chain": allocated,
        "pointers": links,
    }
    print(f"  -> SUCCESS: Allocated linked chain: {' -> '.join(map(str, allocated))} -> EOF")
    return True


# =====================================================================
# 3. Indexed Allocation
# =====================================================================
def allocate_indexed(disk, filename, num_blocks):
    print(f"\n[Indexed Allocation Request] File '{filename}', Size: {num_blocks} data blocks (+1 index block)")
    if filename in disk.file_table:
        print(f"  Error: Duplicate file '{filename}' rejected.")
        return False
    if num_blocks <= 0:
        print("  Error: Block count must be positive.")
        return False

    needed_total = num_blocks + 1
    free_blocks = disk.get_free_blocks()
    if len(free_blocks) < needed_total:
        print(f"  REJECTED: Insufficient disk space! Free: {len(free_blocks)}, Needed: {needed_total}")
        return False

    index_block = free_blocks[0]
    data_blocks = free_blocks[1:needed_total]

    disk.blocks[index_block] = f"IDX:{filename}"
    for b in data_blocks:
        disk.blocks[b] = filename

    # Metadata: Index block holding pointer table
    disk.file_table[filename] = {
        "method": "Indexed",
        "index_block": index_block,
        "data_blocks": data_blocks,
    }
    print(f"  -> SUCCESS: Index Block = {index_block}, Data Blocks = {data_blocks}")
    return True


def demonstrate_comparisons():
    print("\n" + "=" * 65)
    print(" COMPARATIVE EVALUATION OF FILE ALLOCATION METHODS")
    print("=" * 65)
    print(f"{'Method':<14}{'Access Speed':<18}{'Storage Overhead':<20}{'Fragmentation'}")
    print("-" * 65)
    print(f"{'Contiguous':<14}{'Fast Direct Access':<18}{'Minimal (2 integers)':<20}{'External Fragmentation'}")
    print(f"{'Linked':<14}{'Slow Sequential':<18}{'Pointer per block':<20}{'Zero External'}")
    print(f"{'Indexed':<14}{'Fast Direct/Random':<18}{'1 Index Block/file':<20}{'Zero External'}")
    print("-" * 65)


def main():
    print("=" * 65)
    print(" OS LAB - CONTIGUOUS, LINKED AND INDEXED FILE ALLOCATION")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    # 1. Contiguous Demo
    disk_c = SimulatedDisk()
    allocate_contiguous(disk_c, "fileA", 4)
    allocate_contiguous(disk_c, "fileB", 6)
    allocate_contiguous(disk_c, "fileC", 8)
    allocate_contiguous(disk_c, "fileD", 20)  # Rejection
    disk_c.display_disk_map()

    # 2. Linked Demo
    disk_l = SimulatedDisk()
    # Pre-occupy some blocks to create fragmented gaps
    disk_l.blocks[2] = disk_l.blocks[5] = disk_l.blocks[8] = "SYS"
    allocate_linked(disk_l, "doc1", 5)
    disk_l.display_disk_map()

    # 3. Indexed Demo
    disk_i = SimulatedDisk()
    disk_i.blocks[0] = disk_i.blocks[1] = "BOOT"
    allocate_indexed(disk_i, "app.bin", 4)
    disk_i.display_disk_map()

    demonstrate_comparisons()


if __name__ == "__main__":
    main()
