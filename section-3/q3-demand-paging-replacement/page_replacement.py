#!/usr/bin/env python3
"""
OS Lab - Section 3, Q3: Demand Paging, Page Replacement and Thrashing
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""


def simulate_fifo(ref_string, frame_count):
    frames = []
    faults = 0
    hits = 0
    history = []

    for page in ref_string:
        if page in frames:
            hits += 1
            status = "HIT "
        else:
            faults += 1
            status = "MISS"
            if len(frames) < frame_count:
                frames.append(page)
            else:
                frames.pop(0)  # Remove oldest entered page
                frames.append(page)
        history.append({"page": page, "status": status, "frames": list(frames)})

    return {"name": "FIFO", "faults": faults, "hits": hits, "history": history}


def simulate_lru(ref_string, frame_count):
    frames = []
    faults = 0
    hits = 0
    history = []
    last_used = {}

    for t, page in enumerate(ref_string):
        if page in frames:
            hits += 1
            status = "HIT "
        else:
            faults += 1
            status = "MISS"
            if len(frames) < frame_count:
                frames.append(page)
            else:
                # Evict page with minimum last_used timestamp
                victim = min(frames, key=lambda p: last_used[p])
                v_idx = frames.index(victim)
                frames[v_idx] = page
        last_used[page] = t
        history.append({"page": page, "status": status, "frames": list(frames)})

    return {"name": "LRU", "faults": faults, "hits": hits, "history": history}


def simulate_optimal(ref_string, frame_count):
    frames = []
    faults = 0
    hits = 0
    history = []

    for idx, page in enumerate(ref_string):
        if page in frames:
            hits += 1
            status = "HIT "
        else:
            faults += 1
            status = "MISS"
            if len(frames) < frame_count:
                frames.append(page)
            else:
                # Find page not used for longest time in future
                furthest_use = -1
                victim = frames[0]
                for p in frames:
                    try:
                        next_use = ref_string[idx + 1:].index(p)
                    except ValueError:
                        next_use = float("inf")  # Never referenced again
                    if next_use > furthest_use:
                        furthest_use = next_use
                        victim = p
                v_idx = frames.index(victim)
                frames[v_idx] = page
        history.append({"page": page, "status": status, "frames": list(frames)})

    return {"name": "Optimal", "faults": faults, "hits": hits, "history": history}


def display_simulation_run(sim_result, frame_count):
    name = sim_result["name"]
    faults = sim_result["faults"]
    hits = sim_result["hits"]
    history = sim_result["history"]
    total = len(history)

    print(f"\n--- Algorithm: {name} (Frames: {frame_count}) ---")
    header = f"{'Ref Page':<10}" + "".join([f"Frame {i+1:<5}" for i in range(frame_count)]) + f"{'Result':<8}"
    print(header)
    print("-" * len(header))

    for h in history:
        f_cols = ""
        for i in range(frame_count):
            if i < len(h["frames"]):
                f_cols += f"{h['frames'][i]:<8}"
            else:
                f_cols += f"{'-':<8}"
        print(f"{h['page']:<10}{f_cols}{h['status']:<8}")

    fault_ratio = (faults / total) * 100
    hit_ratio = (hits / total) * 100
    print("-" * len(header))
    print(f"Total References: {total} | Page Faults: {faults} ({fault_ratio:.1f}%) | Hits: {hits} ({hit_ratio:.1f}%)")


def run_comparison(ref_string, frame_count):
    res_fifo = simulate_fifo(ref_string, frame_count)
    res_lru = simulate_lru(ref_string, frame_count)
    res_opt = simulate_optimal(ref_string, frame_count)

    display_simulation_run(res_fifo, frame_count)
    display_simulation_run(res_lru, frame_count)
    display_simulation_run(res_opt, frame_count)

    return res_fifo, res_lru, res_opt


def demonstrate_thrashing_concept(ref_string):
    print("\n" + "=" * 65)
    print(" [ANALYSIS] THRASHING BEHAVIOUR ACROSS ALLOCATED FRAMES")
    print("=" * 65)
    print("Thrashing occurs when the working set of active pages exceeds available frames,")
    print("causing the OS to spend more time swapping pages than executing instructions.\n")

    print(f"{'Allocated Frames':<18}{'FIFO Faults':<15}{'LRU Faults':<15}{'Optimal Faults':<15}")
    print("-" * 65)
    for f in range(2, 6):
        rf = simulate_fifo(ref_string, f)
        rl = simulate_lru(ref_string, f)
        ro = simulate_optimal(ref_string, f)
        note = " (High Thrashing Risk!)" if f == 2 else ""
        print(f"{f:<18}{rf['faults']:<15}{rl['faults']:<15}{ro['faults']:<15}{note}")
    print("-" * 65)


def main():
    print("=" * 65)
    print(" OS LAB - DEMAND PAGING, PAGE REPLACEMENT & THRASHING")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    print(f"Reference String ({len(reference_string)} references):")
    print(" ", reference_string)

    print("\n[Trial 1] Execution with 3 Frames:")
    run_comparison(reference_string, 3)

    print("\n" + "=" * 65)
    print("[Trial 2] Execution with 4 Frames:")
    run_comparison(reference_string, 4)

    demonstrate_thrashing_concept(reference_string)


if __name__ == "__main__":
    main()
