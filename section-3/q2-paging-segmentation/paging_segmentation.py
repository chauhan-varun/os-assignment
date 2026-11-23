#!/usr/bin/env python3
"""
OS Lab - Section 3, Q2: Paging and Segmentation
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""


def demonstrate_paging():
    print("=" * 65)
    print(" [PART 1] PAGING ADDRESS TRANSLATION")
    print("=" * 65)

    PAGE_SIZE = 1024  # 1 KB = 1024 bytes
    print(f"Paging Parameters: Page Size = {PAGE_SIZE} bytes (Offset bits = 10)\n")

    # Page Table: Page Number -> {Frame Number, Valid/Invalid Bit}
    page_table = {
        0: {"frame": 5, "valid": True},
        1: {"frame": 6, "valid": True},
        2: {"frame": 1, "valid": True},
        3: {"frame": 2, "valid": True},
        4: {"frame": None, "valid": False},  # Not in physical RAM (Page Fault)
    }

    print("Current Process Page Table:")
    print("-" * 45)
    print(f"{'Page #':<10}{'Frame #':<12}{'Valid Bit':<12}{'Status'}")
    print("-" * 45)
    for p_num, entry in page_table.items():
        v_str = "1 (Valid)" if entry["valid"] else "0 (Invalid)"
        f_str = str(entry["frame"]) if entry["frame"] is not None else "-"
        st = "In Physical Memory" if entry["valid"] else "Page Fault (Swapped/Unmapped)"
        print(f"{p_num:<10}{f_str:<12}{v_str:<12}{st}")
    print("-" * 45)

    test_addresses = [2500, 1050, 4200, 7500]

    print("\nTranslating Logical Addresses:")
    for logical in test_addresses:
        print(f"\n-> Given Logical Address: {logical}")
        page_num = logical // PAGE_SIZE
        offset = logical % PAGE_SIZE
        print(f"   Calculation: Page Number = {logical} // {PAGE_SIZE} = {page_num}")
        print(f"                Offset      = {logical} %  {PAGE_SIZE} = {offset}")

        if page_num in page_table:
            entry = page_table[page_num]
            if entry["valid"]:
                frame_num = entry["frame"]
                physical_address = (frame_num * PAGE_SIZE) + offset
                print(f"   Page Table Lookup: Page {page_num} maps to Frame {frame_num} (Valid)")
                print(f"   Physical Address = ({frame_num} * {PAGE_SIZE}) + {offset} = {physical_address}")
            else:
                print(f"   Page Table Lookup: Page {page_num} marked INVALID (Bit=0).")
                print("   RESULT: [PAGE FAULT] Page not present in physical RAM; must load from swap.")
        else:
            print(f"   Page Table Lookup: Page {page_num} OUT OF PROCESS RANGE.")
            print("   RESULT: [SEGMENTATION FAULT / TRAP] Illegal memory reference.")


def demonstrate_segmentation():
    print("\n" + "=" * 65)
    print(" [PART 2] SEGMENTATION ADDRESS TRANSLATION")
    print("=" * 65)

    # Segment Table: Segment Number -> (Base, Limit)
    segment_table = {
        0: {"name": "Code Segment", "base": 1400, "limit": 1000},
        1: {"name": "Heap Segment", "base": 6300, "limit": 400},
        2: {"name": "Stack Segment", "base": 4300, "limit": 400},
        3: {"name": "Data Segment", "base": 3200, "limit": 1100},
    }

    print("Segment Table:")
    print("-" * 55)
    print(f"{'Seg #':<8}{'Segment Name':<18}{'Base Addr':<12}{'Limit (Bytes)':<12}")
    print("-" * 55)
    for seg_id, s in segment_table.items():
        print(f"{seg_id:<8}{s['name']:<18}{s['base']:<12}{s['limit']:<12}")
    print("-" * 55)

    test_queries = [
        (0, 450),   # Valid Code
        (1, 450),   # Trap: Offset 450 >= Limit 400
        (2, 200),   # Valid Stack
        (3, 1050),  # Valid Data
        (4, 50),    # Invalid Segment ID
    ]

    print("\nTranslating Segment Logical References (Segment #, Offset):")
    for seg_num, offset in test_queries:
        print(f"\n-> Reference: Segment={seg_num}, Offset={offset}")
        if seg_num in segment_table:
            base = segment_table[seg_num]["base"]
            limit = segment_table[seg_num]["limit"]
            name = segment_table[seg_num]["name"]
            print(f"   Segment Name: {name} (Base={base}, Limit={limit})")
            if offset < limit:
                phys = base + offset
                print(f"   Check: Offset ({offset}) < Limit ({limit}) -> VALID")
                print(f"   Physical Address = Base ({base}) + Offset ({offset}) = {phys}")
            else:
                print(f"   Check: Offset ({offset}) >= Limit ({limit}) -> VIOLATION")
                print("   RESULT: [TRAP: ADDRESSING ERROR] Offset exceeds segment boundary!")
        else:
            print(f"   RESULT: [TRAP: INVALID SEGMENT] Segment {seg_num} does not exist in segment table.")


def main():
    print("=" * 65)
    print(" OS LAB - PAGING AND SEGMENTATION ADDRESS TRANSLATION")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    demonstrate_paging()
    demonstrate_segmentation()


if __name__ == "__main__":
    main()
