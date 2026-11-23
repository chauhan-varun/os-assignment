#!/usr/bin/env python3
"""
OS Lab - Section 4, Q4: Free-Space Management, Deletion and Access Control
Student Name: Varun Chauhan
Roll Number:  2401010276
Course:       B.Tech CSE Sec B
"""

import os
import pwd
import grp
import stat


# =====================================================================
# [PART 1] Free-Space Management (Bitmap, Free-List, Deletion, Invariant)
# =====================================================================
class FreeSpaceDisk:
    def __init__(self, num_blocks=16):
        self.num_blocks = num_blocks
        # 0 = Allocated, 1 = Free
        self.bitmap = [1] * num_blocks
        self.allocated_files = {}  # filename -> [block_ids]

    def get_free_block_list(self):
        return [i for i, bit in enumerate(self.bitmap) if bit == 1]

    def allocate_file(self, filename, block_count):
        print(f"\n[Allocation Request] File '{filename}' requesting {block_count} blocks...")
        free_blocks = self.get_free_block_list()
        if len(free_blocks) < block_count:
            print(f"  -> ERROR: Insufficient free blocks! Free: {len(free_blocks)}, Required: {block_count}")
            return False

        assigned = free_blocks[:block_count]
        for b in assigned:
            self.bitmap[b] = 0  # Mark as allocated
        self.allocated_files[filename] = assigned
        print(f"  -> GRANTED: Assigned blocks {assigned} to '{filename}'.")
        self.display_status()
        self.verify_invariants()
        return True

    def delete_file(self, filename):
        print(f"\n[Deletion Request] Deleting file '{filename}' and releasing its blocks...")
        if filename not in self.allocated_files:
            print(f"  -> Error: File '{filename}' not found.")
            return False

        released_blocks = self.allocated_files.pop(filename)
        for b in released_blocks:
            self.bitmap[b] = 1  # Mark back as free
        print(f"  -> RELEASED: Blocks {released_blocks} returned to free-space pool.")
        self.display_status()
        self.verify_invariants()
        return True

    def verify_invariants(self):
        # Invariant: No block can be both allocated and free
        allocated_blocks_set = set()
        for blist in self.allocated_files.values():
            for b in blist:
                assert b not in allocated_blocks_set, f"Block {b} allocated to multiple files!"
                allocated_blocks_set.add(b)

        free_blocks_set = set(self.get_free_block_list())
        intersection = allocated_blocks_set.intersection(free_blocks_set)
        assert len(intersection) == 0, f"Invariant Violation! Blocks {intersection} marked as both allocated and free!"
        assert len(allocated_blocks_set) + len(free_blocks_set) == self.num_blocks, "Invariant Violation: Block count mismatch!"
        print("  -> [INVARIANT CHECK PASSED] Consistency verified: All blocks uniquely accounted for.")

    def display_status(self):
        bitmap_str = "".join(["[1:FREE]" if b else "[0:USED]" for b in self.bitmap])
        free_list = self.get_free_block_list()
        print(f"  Bitmap State   : {bitmap_str}")
        print(f"  Free-Block List: {free_list} (Count: {len(free_list)})")


# =====================================================================
# [PART 2] POSIX Access Control & Principle of Least Privilege
# =====================================================================
def demonstrate_access_control():
    print("\n" + "=" * 65)
    print(" [PART 2] FILE ACCESS CONTROL & LEAST PRIVILEGE PRINCIPLE")
    print("=" * 65)

    test_file = "secure_access_test.txt"

    # 1. Create file with initial safe permissions (0o644: Owner rw, Group r, Others r)
    print(f"Creating controlled test file '{test_file}'...")
    with open(test_file, "w") as f:
        f.write("Confidential Lab Security Record.\nAuthorized Access Only.\n")

    os.chmod(test_file, 0o644)
    inspect_file_permissions(test_file, "Initial Safe State (0o644 / -rw-r--r--)")

    # 2. Principle of Least Privilege: Restrict to Owner-Only Read-Only (0o400)
    print("\nApplying Principle of Least Privilege (Owner Read-Only: 0o400)...")
    os.chmod(test_file, 0o400)
    inspect_file_permissions(test_file, "Restricted Owner Read-Only (0o400 / -r--------)")

    # 3. Test Allowed Operation: Reading file
    print("\nTesting Allowed Operation (Reading under 0o400 permissions):")
    try:
        with open(test_file, "r") as f:
            content = f.read().strip()
        print(f"  -> SUCCESS: Read allowed. Content snippet: '{content[:30]}...'")
    except Exception as e:
        print(f"  -> Failed: {e}")

    # 4. Test Denied Operation: Writing to read-only file
    print("\nTesting Denied Operation (Attempting write under 0o400 permissions):")
    try:
        with open(test_file, "w") as f:
            f.write("Unauthorized overwrite attempt!\n")
        print("  -> ERROR: Write unexpectedly succeeded!")
    except PermissionError as pe:
        print(f"  -> [ACCESS DENIED AS EXPECTED] Caught PermissionError: {pe}")
        print("     Kernel prevented unauthorized write in compliance with Least Privilege.")

    # 5. Restore Safe Permissions and Cleanup
    print("\nRestoring standard permissions (0o644) and removing temporary test file...")
    os.chmod(test_file, 0o644)
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"Cleanup: Removed '{test_file}'.")


def inspect_file_permissions(filepath, description):
    st = os.stat(filepath)
    mode = stat.S_IMODE(st.st_mode)
    owner = pwd.getpwuid(st.st_uid).pw_name
    group = grp.getgrgid(st.st_gid).gr_name
    print(f"  [{description}]")
    print(f"    Owner: {owner} | Group: {group}")
    print(f"    Octal Permissions: {oct(mode)} | Symbolic: {stat.filemode(st.st_mode)}")


def main():
    print("=" * 65)
    print(" OS LAB - FREE-SPACE MANAGEMENT, DELETION & ACCESS CONTROL")
    print(" Student Name : Varun Chauhan (2401010276) - B.Tech CSE Sec B")
    print("=" * 65)

    print("\n--- [PART 1] Free Space Management (Bitmap & Linked List) ---")
    disk = FreeSpaceDisk(num_blocks=12)
    disk.display_status()

    disk.allocate_file("kernel_image", 4)
    disk.allocate_file("user_doc.txt", 3)
    disk.allocate_file("db_tables", 4)

    # Deletion and reclamation
    disk.delete_file("user_doc.txt")
    disk.allocate_file("patch.bin", 2)

    demonstrate_access_control()

    print("\n" + "=" * 65)
    print(" EXPERIMENT SUCCESSFULLY COMPLETED")
    print("=" * 65)


if __name__ == "__main__":
    main()
