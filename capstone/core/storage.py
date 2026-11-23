"""
Storage, File Allocation, and Disk Scheduling Module.
Includes:
1. Disk Arm Scheduling: FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK.
2. File System Block Allocation: Contiguous, Linked, and Indexed Allocation with free-space bitmap tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import copy

from core.exceptions import StorageAllocationError, InvalidDiskRequestError
from core.logger import get_logger

logger = get_logger()


@dataclass
class DiskScheduleResult:
    algorithm: str
    seek_sequence: List[int]
    total_head_movement: int
    average_seek_length: float
    initial_head: int
    direction: str


class DiskScheduler:
    """Simulates disk head scheduling algorithms."""

    @staticmethod
    def _validate_params(requests: List[int], initial_head: int, total_cylinders: int):
        if not requests:
            raise InvalidDiskRequestError("Disk request queue cannot be empty.")
        if initial_head < 0 or initial_head >= total_cylinders:
            raise InvalidDiskRequestError(
                f"Initial head position {initial_head} is outside cylinder range [0, {total_cylinders - 1}]."
            )
        for req in requests:
            if req < 0 or req >= total_cylinders:
                raise InvalidDiskRequestError(
                    f"Request {req} is outside valid cylinder boundary [0, {total_cylinders - 1}]."
                )

    @staticmethod
    def fcfs(requests: List[int], initial_head: int, total_cylinders: int = 200) -> DiskScheduleResult:
        """First-Come, First-Served Disk Scheduling."""
        DiskScheduler._validate_params(requests, initial_head, total_cylinders)
        seq = [initial_head] + list(requests)
        total_seek = sum(abs(seq[i] - seq[i - 1]) for i in range(1, len(seq)))
        avg_seek = total_seek / len(requests)
        return DiskScheduleResult("FCFS", seq, total_seek, avg_seek, initial_head, "N/A")

    @staticmethod
    def sstf(requests: List[int], initial_head: int, total_cylinders: int = 200) -> DiskScheduleResult:
        """Shortest Seek Time First Disk Scheduling."""
        DiskScheduler._validate_params(requests, initial_head, total_cylinders)
        pending = list(requests)
        seq = [initial_head]
        curr = initial_head
        total_seek = 0

        while pending:
            closest = min(pending, key=lambda r: abs(r - curr))
            total_seek += abs(closest - curr)
            curr = closest
            seq.append(curr)
            pending.remove(closest)

        avg_seek = total_seek / len(requests)
        return DiskScheduleResult("SSTF", seq, total_seek, avg_seek, initial_head, "N/A")

    @staticmethod
    def scan(requests: List[int], initial_head: int, total_cylinders: int = 200, direction: str = "right") -> DiskScheduleResult:
        """SCAN (Elevator) Disk Scheduling."""
        DiskScheduler._validate_params(requests, initial_head, total_cylinders)
        direction = direction.lower()
        left = sorted([r for r in requests if r < initial_head])
        right = sorted([r for r in requests if r >= initial_head])

        seq = [initial_head]
        if direction in ("right", "up", "high"):
            seq.extend(right)
            if left:
                seq.append(total_cylinders - 1)
                seq.extend(reversed(left))
        else:
            seq.extend(reversed(left))
            if right:
                seq.append(0)
                seq.extend(right)

        total_seek = sum(abs(seq[i] - seq[i - 1]) for i in range(1, len(seq)))
        avg_seek = total_seek / len(requests)
        return DiskScheduleResult("SCAN", seq, total_seek, avg_seek, initial_head, direction)

    @staticmethod
    def c_scan(requests: List[int], initial_head: int, total_cylinders: int = 200, direction: str = "right") -> DiskScheduleResult:
        """Circular SCAN (C-SCAN) Disk Scheduling."""
        DiskScheduler._validate_params(requests, initial_head, total_cylinders)
        direction = direction.lower()
        left = sorted([r for r in requests if r < initial_head])
        right = sorted([r for r in requests if r >= initial_head])

        seq = [initial_head]
        if direction in ("right", "up", "high"):
            seq.extend(right)
            if left:
                seq.append(total_cylinders - 1)
                seq.append(0)
                seq.extend(left)
        else:
            seq.extend(reversed(left))
            if right:
                seq.append(0)
                seq.append(total_cylinders - 1)
                seq.extend(reversed(right))

        total_seek = sum(abs(seq[i] - seq[i - 1]) for i in range(1, len(seq)))
        avg_seek = total_seek / len(requests)
        return DiskScheduleResult("C-SCAN", seq, total_seek, avg_seek, initial_head, direction)

    @staticmethod
    def look(requests: List[int], initial_head: int, total_cylinders: int = 200, direction: str = "right") -> DiskScheduleResult:
        """LOOK Disk Scheduling."""
        DiskScheduler._validate_params(requests, initial_head, total_cylinders)
        direction = direction.lower()
        left = sorted([r for r in requests if r < initial_head])
        right = sorted([r for r in requests if r >= initial_head])

        seq = [initial_head]
        if direction in ("right", "up", "high"):
            seq.extend(right)
            seq.extend(reversed(left))
        else:
            seq.extend(reversed(left))
            seq.extend(right)

        total_seek = sum(abs(seq[i] - seq[i - 1]) for i in range(1, len(seq)))
        avg_seek = total_seek / len(requests)
        return DiskScheduleResult("LOOK", seq, total_seek, avg_seek, initial_head, direction)

    @staticmethod
    def c_look(requests: List[int], initial_head: int, total_cylinders: int = 200, direction: str = "right") -> DiskScheduleResult:
        """Circular LOOK (C-LOOK) Disk Scheduling."""
        DiskScheduler._validate_params(requests, initial_head, total_cylinders)
        direction = direction.lower()
        left = sorted([r for r in requests if r < initial_head])
        right = sorted([r for r in requests if r >= initial_head])

        seq = [initial_head]
        if direction in ("right", "up", "high"):
            seq.extend(right)
            seq.extend(left)
        else:
            seq.extend(reversed(left))
            seq.extend(reversed(right))

        total_seek = sum(abs(seq[i] - seq[i - 1]) for i in range(1, len(seq)))
        avg_seek = total_seek / len(requests)
        return DiskScheduleResult("C-LOOK", seq, total_seek, avg_seek, initial_head, direction)


@dataclass
class FileMetadata:
    name: str
    size_blocks: int
    allocation_type: str
    allocated_blocks: List[int]
    index_block: Optional[int] = None


class FileSystemSimulator:
    """Simulates Contiguous, Linked, and Indexed block allocation with bit-vector free space tracking."""

    def __init__(self, total_blocks: int = 64):
        if total_blocks <= 0:
            raise StorageAllocationError("Total disk blocks must be positive.")
        self.total_blocks = total_blocks
        self.bitmap = [0] * total_blocks  # 0 = free, 1 = allocated
        self.directory: Dict[str, FileMetadata] = {}

    def get_free_block_count(self) -> int:
        return self.bitmap.count(0)

    def allocate_contiguous(self, filename: str, num_blocks: int) -> FileMetadata:
        """Allocates contiguous blocks for file."""
        if filename in self.directory:
            raise StorageAllocationError(f"File {filename} already exists.")
        if num_blocks <= 0:
            raise StorageAllocationError(f"Requested blocks must be positive: {num_blocks}")

        # Find contiguous run of 0s
        start_idx = -1
        current_run = 0
        for i in range(self.total_blocks):
            if self.bitmap[i] == 0:
                if current_run == 0:
                    start_idx = i
                current_run += 1
                if current_run == num_blocks:
                    break
            else:
                current_run = 0
                start_idx = -1

        if current_run < num_blocks:
            raise StorageAllocationError(
                f"Contiguous allocation failed for {filename}: Cannot find {num_blocks} consecutive free blocks (External Fragmentation)."
            )

        allocated = list(range(start_idx, start_idx + num_blocks))
        for b in allocated:
            self.bitmap[b] = 1

        meta = FileMetadata(filename, num_blocks, "Contiguous", allocated)
        self.directory[filename] = meta
        logger.info(f"Contiguous allocated {filename}: blocks {allocated}")
        return meta

    def allocate_linked(self, filename: str, num_blocks: int) -> FileMetadata:
        """Allocates linked blocks for file (any free blocks scattered across disk)."""
        if filename in self.directory:
            raise StorageAllocationError(f"File {filename} already exists.")
        if num_blocks <= 0:
            raise StorageAllocationError(f"Requested blocks must be positive: {num_blocks}")

        free_indices = [i for i, val in enumerate(self.bitmap) if val == 0]
        if len(free_indices) < num_blocks:
            raise StorageAllocationError(
                f"Linked allocation failed for {filename}: Insufficient disk space ({len(free_indices)} free, {num_blocks} needed)."
            )

        allocated = free_indices[:num_blocks]
        for b in allocated:
            self.bitmap[b] = 1

        meta = FileMetadata(filename, num_blocks, "Linked", allocated)
        self.directory[filename] = meta
        logger.info(f"Linked allocated {filename}: blocks {allocated}")
        return meta

    def allocate_indexed(self, filename: str, num_blocks: int) -> FileMetadata:
        """Allocates indexed file (1 index block + N data blocks)."""
        if filename in self.directory:
            raise StorageAllocationError(f"File {filename} already exists.")
        if num_blocks <= 0:
            raise StorageAllocationError(f"Requested blocks must be positive: {num_blocks}")

        needed = num_blocks + 1  # 1 index block
        free_indices = [i for i, val in enumerate(self.bitmap) if val == 0]
        if len(free_indices) < needed:
            raise StorageAllocationError(
                f"Indexed allocation failed for {filename}: Insufficient blocks ({len(free_indices)} free, {needed} needed)."
            )

        index_block = free_indices[0]
        data_blocks = free_indices[1:needed]

        self.bitmap[index_block] = 1
        for b in data_blocks:
            self.bitmap[b] = 1

        meta = FileMetadata(filename, num_blocks, "Indexed", data_blocks, index_block=index_block)
        self.directory[filename] = meta
        logger.info(f"Indexed allocated {filename}: Index block {index_block}, Data blocks {data_blocks}")
        return meta

    def delete_file(self, filename: str):
        if filename not in self.directory:
            raise StorageAllocationError(f"File {filename} does not exist in directory.")

        meta = self.directory.pop(filename)
        for b in meta.allocated_blocks:
            self.bitmap[b] = 0
        if meta.index_block is not None:
            self.bitmap[meta.index_block] = 0
        logger.info(f"Deleted file {filename}, freed blocks.")
