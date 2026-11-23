#!/usr/bin/env python3
"""
OS Lab - Section 3, Q5: Disk Scheduling and Swap-Space Management
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import copy


# =====================================================================
# [PART 1] Disk Scheduling Algorithms (FCFS, SSTF, SCAN, C-SCAN)
# =====================================================================
def validate_inputs(disk_min, disk_max, initial_head, requests):
    if not (disk_min <= initial_head <= disk_max):
        raise ValueError(f"Initial head position {initial_head} is outside disk range [{disk_min}, {disk_max}].")
    valid_requests = []
    for r in requests:
        if disk_min <= r <= disk_max:
            valid_requests.append(r)
        else:
            print(f"Warning: Discarding out-of-range request {r} (Valid range [{disk_min}, {disk_max}]).")
    return valid_requests


def schedule_fcfs(initial_head, requests):
    path = [initial_head] + list(requests)
    total_movement = sum(abs(path[i] - path[i - 1]) for i in range(1, len(path)))
    avg_movement = total_movement / len(requests)
    return {"name": "FCFS", "path": path, "total": total_movement, "avg": avg_movement}


def schedule_sstf(initial_head, requests):
    path = [initial_head]
    pending = list(requests)
    curr = initial_head

    while pending:
        closest = min(pending, key=lambda req: abs(req - curr))
        path.append(closest)
        pending.remove(closest)
        curr = closest

    total_movement = sum(abs(path[i] - path[i - 1]) for i in range(1, len(path)))
    avg_movement = total_movement / len(requests)
    return {"name": "SSTF", "path": path, "total": total_movement, "avg": avg_movement}


def schedule_scan(initial_head, requests, disk_min=0, disk_max=199, direction="high"):
    path = [initial_head]
    left = sorted([r for r in requests if r < initial_head])
    right = sorted([r for r in requests if r >= initial_head])

    if direction == "high":
        # Move up to disk_max, then reverse down
        path.extend(right)
        if right and path[-1] != disk_max and left:
            path.append(disk_max)  # Hit boundary
        path.extend(reversed(left))
    else:
        # Move down to disk_min, then reverse up
        path.extend(reversed(left))
        if left and path[-1] != disk_min and right:
            path.append(disk_min)
        path.extend(right)

    total_movement = sum(abs(path[i] - path[i - 1]) for i in range(1, len(path)))
    avg_movement = total_movement / len(requests)
    return {"name": f"SCAN ({direction.upper()})", "path": path, "total": total_movement, "avg": avg_movement}


def schedule_cscan(initial_head, requests, disk_min=0, disk_max=199, direction="high"):
    path = [initial_head]
    left = sorted([r for r in requests if r < initial_head])
    right = sorted([r for r in requests if r >= initial_head])

    if direction == "high":
        path.extend(right)
        path.append(disk_max)
        path.append(disk_min)  # Wrap to bottom
        path.extend(left)
    else:
        path.extend(reversed(left))
        path.append(disk_min)
        path.append(disk_max)  # Wrap to top
        path.extend(reversed(right))

    total_movement = sum(abs(path[i] - path[i - 1]) for i in range(1, len(path)))
    avg_movement = total_movement / len(requests)
    return {"name": f"C-SCAN ({direction.upper()})", "path": path, "total": total_movement, "avg": avg_movement}


# =====================================================================
# [PART 2] Swap-Space Block Map Management
# =====================================================================
class SwapSpaceManager:
    def __init__(self, total_blocks=16):
        self.total_blocks = total_blocks
        # 0 = Free, 1 = Allocated
        self.bitmap = [0] * total_blocks
        self.allocated_map = {}  # pid -> [block_ids]

    def allocate(self, pid, num_blocks):
        print(f"\n[Swap Request] Process '{pid}' requesting {num_blocks} swap blocks...")
        free_indices = [i for i, bit in enumerate(self.bitmap) if bit == 0]
        if len(free_indices) < num_blocks:
            print(f"  -> REJECTED: Insufficient swap space! Available: {len(free_indices)}, Required: {num_blocks}")
            return False

        assigned = free_indices[:num_blocks]
        for idx in assigned:
            self.bitmap[idx] = 1
        self.allocated_map[pid] = assigned
        print(f"  -> ALLOCATED: Process '{pid}' assigned Swap Blocks: {assigned}")
        self.display_state()
        return True

    def release(self, pid):
        print(f"\n[Swap Release] Releasing swap space for process '{pid}'...")
        if pid not in self.allocated_map:
            print(f"  -> Error: No swap blocks allocated to '{pid}'.")
            return
        freed = self.allocated_map.pop(pid)
        for idx in freed:
            self.bitmap[idx] = 0
        print(f"  -> FREED: Returned Swap Blocks {freed} to free space pool.")
        self.display_state()

    def display_state(self):
        map_str = "".join(["[■]" if b else "[ ]" for b in self.bitmap])
        free_count = self.bitmap.count(0)
        print(f"  Swap Bitmap Map : {map_str} ({free_count}/{self.total_blocks} free)")


def main():
    print("=" * 65)
    print(" OS LAB - DISK SCHEDULING AND SWAP-SPACE MANAGEMENT")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    disk_min = 0
    disk_max = 199
    initial_head = 53
    requests = [98, 183, 37, 122, 14, 124, 65, 67]

    valid_reqs = validate_inputs(disk_min, disk_max, initial_head, requests)
    print(f"Disk Range          : [{disk_min} -> {disk_max}] Cylinders")
    print(f"Initial Head Position: {initial_head}")
    print(f"Disk Request Queue  : {valid_reqs}\n")

    res_fcfs = schedule_fcfs(initial_head, valid_reqs)
    res_sstf = schedule_sstf(initial_head, valid_reqs)
    res_scan = schedule_scan(initial_head, valid_reqs, disk_min, disk_max, direction="high")
    res_cscan = schedule_cscan(initial_head, valid_reqs, disk_min, disk_max, direction="high")

    algorithms = [res_fcfs, res_sstf, res_scan, res_cscan]

    print("=" * 65)
    print(" DISK SCHEDULING RESULTS & TRAVERSAL PATHS")
    print("=" * 65)
    for alg in algorithms:
        path_str = " -> ".join(map(str, alg["path"]))
        print(f"\nAlgorithm: {alg['name']}")
        print(f"  Head Traversal Path : {path_str}")
        print(f"  Total Head Movement : {alg['total']} cylinders")
        print(f"  Average Head Move   : {alg['avg']:.2f} cylinders/request")

    print("\n" + "=" * 65)
    print(" ALGORITHM COMPARISON & CHARACTERISTICS")
    print("=" * 65)
    print(f"{'Algorithm':<18}{'Total Movement':<18}{'Fairness':<15}{'Starvation Risk'}")
    print("-" * 65)
    print(f"{'FCFS':<18}{str(res_fcfs['total'])+' cyl':<18}{'Strictly Fair':<15}{'None'}")
    print(f"{'SSTF':<18}{str(res_sstf['total'])+' cyl':<18}{'Unfair':<15}{'High (distant requests)'}")
    print(f"{'SCAN (Elevator)':<18}{str(res_scan['total'])+' cyl':<18}{'Moderate':<15}{'Low'}")
    print(f"{'C-SCAN':<18}{str(res_cscan['total'])+' cyl':<18}{'High (Uniform)':<15}{'Virtually None'}")
    print("-" * 65)

    print("\n" + "=" * 65)
    print(" [PART 2] SWAP-SPACE MANAGEMENT DEMONSTRATION")
    print("=" * 65)
    swap_mgr = SwapSpaceManager(total_blocks=16)
    swap_mgr.display_state()

    swap_mgr.allocate("Process_Alpha", 4)
    swap_mgr.allocate("Process_Beta", 6)
    swap_mgr.allocate("Process_Gamma", 8)  # Should reject due to insufficient space
    swap_mgr.release("Process_Alpha")
    swap_mgr.allocate("Process_Gamma", 8)  # Now fits


if __name__ == "__main__":
    main()
