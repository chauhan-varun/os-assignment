#!/usr/bin/env python3
"""
OS Lab - Section 3, Q1: Contiguous Allocation, Swapping and Address Translation
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import copy


# =====================================================================
# 1. Contiguous Allocation: First Fit, Best Fit, Worst Fit
# =====================================================================
def allocate_first_fit(blocks_orig, processes):
    print("\n" + "-" * 55)
    print(" 1. FIRST FIT MEMORY ALLOCATION")
    print("-" * 55)
    blocks = copy.deepcopy(blocks_orig)
    allocation = {}

    for p in processes:
        allocated = False
        for b in blocks:
            if b["free"] >= p["size"]:
                b["free"] -= p["size"]
                b["assigned"].append(p["pid"])
                allocation[p["pid"]] = b["id"]
                allocated = True
                break
        if not allocated:
            allocation[p["pid"]] = "Unallocated"

    display_allocation_summary("First Fit", blocks, processes, allocation)


def allocate_best_fit(blocks_orig, processes):
    print("\n" + "-" * 55)
    print(" 2. BEST FIT MEMORY ALLOCATION")
    print("-" * 55)
    blocks = copy.deepcopy(blocks_orig)
    allocation = {}

    for p in processes:
        best_idx = -1
        min_rem = float("inf")
        for i, b in enumerate(blocks):
            if b["free"] >= p["size"]:
                rem = b["free"] - p["size"]
                if rem < min_rem:
                    min_rem = rem
                    best_idx = i

        if best_idx != -1:
            blocks[best_idx]["free"] -= p["size"]
            blocks[best_idx]["assigned"].append(p["pid"])
            allocation[p["pid"]] = blocks[best_idx]["id"]
        else:
            allocation[p["pid"]] = "Unallocated"

    display_allocation_summary("Best Fit", blocks, processes, allocation)


def allocate_worst_fit(blocks_orig, processes):
    print("\n" + "-" * 55)
    print(" 3. WORST FIT MEMORY ALLOCATION")
    print("-" * 55)
    blocks = copy.deepcopy(blocks_orig)
    allocation = {}

    for p in processes:
        worst_idx = -1
        max_rem = -1
        for i, b in enumerate(blocks):
            if b["free"] >= p["size"]:
                rem = b["free"] - p["size"]
                if rem > max_rem:
                    max_rem = rem
                    worst_idx = i

        if worst_idx != -1:
            blocks[worst_idx]["free"] -= p["size"]
            blocks[worst_idx]["assigned"].append(p["pid"])
            allocation[p["pid"]] = blocks[worst_idx]["id"]
        else:
            allocation[p["pid"]] = "Unallocated"

    display_allocation_summary("Worst Fit", blocks, processes, allocation)


def display_allocation_summary(method, blocks, processes, allocation):
    print(f"\n{method} Allocation Results:")
    print(f"{'Process':<10}{'Size':<10}{'Status / Block ID'}")
    print("-" * 40)
    for p in processes:
        res = allocation[p["pid"]]
        status = f"Allocated in Block {res}" if res != "Unallocated" else "UNALLOCATED (Insufficient space)"
        print(f"{p['pid']:<10}{str(p['size'])+' KB':<10}{status}")

    print("\nRemaining Block State:")
    print(f"{'Block ID':<10}{'Initial Size':<15}{'Remaining Free':<15}{'Processes Hosted'}")
    print("-" * 55)
    for b in blocks:
        procs_str = ", ".join(b["assigned"]) if b["assigned"] else "None"
        print(f"{b['id']:<10}{str(b['initial'])+' KB':<15}{str(b['free'])+' KB':<15}{procs_str}")


# =====================================================================
# 2. Hardware Address Translation (Base and Limit Register)
# =====================================================================
def demonstrate_address_translation():
    print("\n" + "=" * 65)
    print(" [PART 2] BASE AND LIMIT REGISTER ADDRESS TRANSLATION")
    print("=" * 65)

    base = 300040
    limit = 120900
    print(f"Memory Relocation Register (Base)  : {base}")
    print(f"Memory Protection Register (Limit) : {limit} bytes")

    test_addresses = [45000, 120900, 150000, 0]

    print("\nAddress Evaluation:")
    print("-" * 65)
    print(f"{'Logical Address':<18}{'Condition (< Limit)':<24}{'Result / Physical Addr'}")
    print("-" * 65)
    for logical in test_addresses:
        if 0 <= logical < limit:
            physical = base + logical
            print(f"{logical:<18}{f'{logical} < {limit} (Valid)':<24}{f'Valid -> Physical: {physical}'}")
        else:
            print(f"{logical:<18}{f'{logical} >= {limit} (Trap)':<24}{'TRAP: Memory Protection Fault!'}")
    print("-" * 65)


# =====================================================================
# 3. Swapping Simulation
# =====================================================================
def demonstrate_swapping():
    print("\n" + "=" * 65)
    print(" [PART 3] MEMORY SWAPPING SIMULATION")
    print("=" * 65)

    memory_slots = [
        {"slot": 1, "size": 100, "occupant": "OS Kernel (Protected)"},
        {"slot": 2, "size": 250, "occupant": "Process P1 (Active)"},
        {"slot": 3, "size": 150, "occupant": "Process P2 (Suspended / Blocked)"},
        {"slot": 4, "size": 300, "occupant": "FREE"},
    ]

    print("Memory State BEFORE Swapping:")
    print("-" * 55)
    for m in memory_slots:
        print(f"  Slot {m['slot']} [{m['size']:3d} KB] : {m['occupant']}")
    print("-" * 55)

    incoming_process = {"pid": "P3 (Urgent)", "size": 140}
    print(f"\nIncoming process {incoming_process['pid']} requests {incoming_process['size']} KB.")
    print("Action: Swapping out suspended 'Process P2' to Swap Backing Store...")

    # Swap out P2
    memory_slots[2]["occupant"] = f"{incoming_process['pid']} (SWAPPED IN)"
    print(f"Action: Loaded {incoming_process['pid']} into Slot 3.\n")

    print("Memory State AFTER Swapping:")
    print("-" * 55)
    for m in memory_slots:
        print(f"  Slot {m['slot']} [{m['size']:3d} KB] : {m['occupant']}")
    print("-" * 55)
    print("Swapping successfully simulated between Main Memory and Backing Store.")


def main():
    print("=" * 65)
    print(" OS LAB - CONTIGUOUS ALLOCATION, SWAPPING & ADDRESS TRANSLATION")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    # Memory Blocks (KB)
    initial_blocks = [
        {"id": 1, "initial": 100, "free": 100, "assigned": []},
        {"id": 2, "initial": 500, "free": 500, "assigned": []},
        {"id": 3, "initial": 200, "free": 200, "assigned": []},
        {"id": 4, "initial": 300, "free": 300, "assigned": []},
        {"id": 5, "initial": 600, "free": 600, "assigned": []},
    ]

    # Processes to Allocate
    processes = [
        {"pid": "P1", "size": 212},
        {"pid": "P2", "size": 417},
        {"pid": "P3", "size": 112},
        {"pid": "P4", "size": 426},
    ]

    print("\nInitial Memory Blocks :", [f"B{b['id']}:{b['initial']}KB" for b in initial_blocks])
    print("Processes Requesting  :", [f"{p['pid']}:{p['size']}KB" for p in processes])

    allocate_first_fit(initial_blocks, processes)
    allocate_best_fit(initial_blocks, processes)
    allocate_worst_fit(initial_blocks, processes)

    demonstrate_address_translation()
    demonstrate_swapping()


if __name__ == "__main__":
    main()
