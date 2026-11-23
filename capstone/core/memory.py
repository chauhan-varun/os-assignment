"""
Memory Management & Virtual Memory Simulator.
Includes:
1. Contiguous Memory Allocation: First-Fit, Best-Fit, Worst-Fit with Internal & External Fragmentation.
2. Virtual Memory Page Replacement: FIFO, LRU, Optimal, and LFU with full frame state tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import copy
from collections import OrderedDict

from core.exceptions import MemoryAllocationError, InvalidMemoryAccessError
from core.logger import get_logger

logger = get_logger()


@dataclass
class MemoryBlock:
    block_id: int
    start_address: int
    size: int
    is_allocated: bool = False
    process_id: Optional[str] = None
    process_size: int = 0
    internal_fragmentation: int = 0


@dataclass
class ContiguousAllocResult:
    algorithm: str
    blocks: List[MemoryBlock]
    allocated_processes: List[Tuple[str, int, int]]  # (pid, req_size, block_id)
    unallocated_processes: List[Tuple[str, int]]     # (pid, req_size)
    total_internal_fragmentation: int = 0
    total_external_fragmentation: int = 0
    total_free_memory: int = 0
    utilization_percentage: float = 0.0


class ContiguousMemoryManager:
    """Simulates dynamic partition contiguous memory allocation."""

    def __init__(self, block_sizes: List[int]):
        if not block_sizes or any(s <= 0 for s in block_sizes):
            raise MemoryAllocationError("Initial block sizes must be non-empty and strictly positive.")

        self.initial_blocks = []
        addr = 0
        for i, s in enumerate(block_sizes):
            self.initial_blocks.append(MemoryBlock(block_id=i, start_address=addr, size=s))
            addr += s
        self.total_capacity = sum(block_sizes)

    def allocate(self, algorithm: str, requests: List[Tuple[str, int]]) -> ContiguousAllocResult:
        """
        Allocate memory for a list of (process_id, requested_size).
        Supported algorithms: 'First-Fit', 'Best-Fit', 'Worst-Fit'
        """
        algo_normalized = algorithm.strip().lower().replace("-", "").replace("_", "").replace(" ", "")
        valid_algos = {"firstfit": "First-Fit", "bestfit": "Best-Fit", "worstfit": "Worst-Fit"}

        if algo_normalized not in valid_algos:
            raise MemoryAllocationError(f"Unsupported contiguous allocation algorithm: {algorithm}")

        canonical_algo = valid_algos[algo_normalized]
        blocks = [copy.deepcopy(b) for b in self.initial_blocks]
        allocated = []
        unallocated = []

        for pid, req_size in requests:
            if req_size <= 0:
                raise MemoryAllocationError(f"Process {pid} requested invalid memory size: {req_size}")

            free_candidates = [b for b in blocks if not b.is_allocated and b.size >= req_size]

            if not free_candidates:
                unallocated.append((pid, req_size))
                continue

            chosen: MemoryBlock
            if canonical_algo == "First-Fit":
                chosen = free_candidates[0]
            elif canonical_algo == "Best-Fit":
                # Smallest block that fits
                chosen = min(free_candidates, key=lambda b: (b.size, b.block_id))
            else:  # Worst-Fit
                # Largest block available
                chosen = max(free_candidates, key=lambda b: (b.size, -b.block_id))

            chosen.is_allocated = True
            chosen.process_id = pid
            chosen.process_size = req_size
            chosen.internal_fragmentation = chosen.size - req_size
            allocated.append((pid, req_size, chosen.block_id))

        total_int_frag = sum(b.internal_fragmentation for b in blocks if b.is_allocated)
        total_free = sum(b.size for b in blocks if not b.is_allocated)

        # External fragmentation is the total unallocated free memory when at least one process could not be allocated
        # despite total free memory >= request
        ext_frag = 0
        for pid, req_size in unallocated:
            if total_free >= req_size:
                ext_frag = total_free
                break

        allocated_mem = sum(b.process_size for b in blocks if b.is_allocated)
        util_pct = (allocated_mem / self.total_capacity) * 100.0 if self.total_capacity > 0 else 0.0

        res = ContiguousAllocResult(
            algorithm=canonical_algo,
            blocks=blocks,
            allocated_processes=allocated,
            unallocated_processes=unallocated,
            total_internal_fragmentation=total_int_frag,
            total_external_fragmentation=ext_frag,
            total_free_memory=total_free,
            utilization_percentage=util_pct
        )
        logger.info(f"Contiguous Allocation [{canonical_algo}]: {len(allocated)} allocated, {len(unallocated)} unallocated.")
        return res


@dataclass
class PageStep:
    step_num: int
    page: int
    frames: List[Optional[int]]
    is_fault: bool
    evicted_page: Optional[int] = None


@dataclass
class PageReplacementResult:
    algorithm: str
    reference_string: List[int]
    num_frames: int
    steps: List[PageStep]
    total_page_faults: int
    total_page_hits: int
    fault_ratio: float
    hit_ratio: float


class PageReplacementSimulator:
    """Virtual Memory Page Replacement Simulator (FIFO, LRU, Optimal, LFU)."""

    def __init__(self, num_frames: int):
        if num_frames <= 0:
            raise InvalidMemoryAccessError(f"Number of frames must be positive ({num_frames}).")
        self.num_frames = num_frames

    def _validate_ref_string(self, ref_string: List[int]):
        if not ref_string:
            raise InvalidMemoryAccessError("Page reference string cannot be empty.")
        if any(p < 0 for p in ref_string):
            raise InvalidMemoryAccessError("Page numbers cannot be negative.")

    def fifo(self, ref_string: List[int]) -> PageReplacementResult:
        """First-In, First-Out (FIFO) Page Replacement."""
        self._validate_ref_string(ref_string)
        frames: List[Optional[int]] = [None] * self.num_frames
        fifo_queue: List[int] = []
        steps: List[PageStep] = []
        faults = 0

        for idx, page in enumerate(ref_string):
            if page in frames:
                steps.append(PageStep(idx + 1, page, list(frames), is_fault=False))
            else:
                faults += 1
                evicted = None
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                    fifo_queue.append(page)
                else:
                    evicted = fifo_queue.pop(0)
                    evict_idx = frames.index(evicted)
                    frames[evict_idx] = page
                    fifo_queue.append(page)

                steps.append(PageStep(idx + 1, page, list(frames), is_fault=True, evicted_page=evicted))

        hits = len(ref_string) - faults
        res = PageReplacementResult(
            algorithm="FIFO",
            reference_string=ref_string,
            num_frames=self.num_frames,
            steps=steps,
            total_page_faults=faults,
            total_page_hits=hits,
            fault_ratio=faults / len(ref_string),
            hit_ratio=hits / len(ref_string)
        )
        logger.info(f"Page Replacement [FIFO]: Faults={faults}, Hits={hits}, Fault Ratio={res.fault_ratio:.2%}")
        return res

    def lru(self, ref_string: List[int]) -> PageReplacementResult:
        """Least Recently Used (LRU) Page Replacement."""
        self._validate_ref_string(ref_string)
        frames: List[Optional[int]] = [None] * self.num_frames
        lru_order: OrderedDict[int, None] = OrderedDict()
        steps: List[PageStep] = []
        faults = 0

        for idx, page in enumerate(ref_string):
            if page in frames:
                lru_order.move_to_end(page)
                steps.append(PageStep(idx + 1, page, list(frames), is_fault=False))
            else:
                faults += 1
                evicted = None
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                    lru_order[page] = None
                else:
                    # Oldest used page is first item in OrderedDict
                    evicted, _ = lru_order.popitem(last=False)
                    evict_idx = frames.index(evicted)
                    frames[evict_idx] = page
                    lru_order[page] = None

                steps.append(PageStep(idx + 1, page, list(frames), is_fault=True, evicted_page=evicted))

        hits = len(ref_string) - faults
        res = PageReplacementResult(
            algorithm="LRU",
            reference_string=ref_string,
            num_frames=self.num_frames,
            steps=steps,
            total_page_faults=faults,
            total_page_hits=hits,
            fault_ratio=faults / len(ref_string),
            hit_ratio=hits / len(ref_string)
        )
        logger.info(f"Page Replacement [LRU]: Faults={faults}, Hits={hits}, Fault Ratio={res.fault_ratio:.2%}")
        return res

    def optimal(self, ref_string: List[int]) -> PageReplacementResult:
        """Belady's Optimal Page Replacement (MIN)."""
        self._validate_ref_string(ref_string)
        frames: List[Optional[int]] = [None] * self.num_frames
        steps: List[PageStep] = []
        faults = 0

        for idx, page in enumerate(ref_string):
            if page in frames:
                steps.append(PageStep(idx + 1, page, list(frames), is_fault=False))
            else:
                faults += 1
                evicted = None
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                else:
                    # Look ahead into future references
                    future = ref_string[idx + 1:]
                    farthest_idx = -1
                    victim = None

                    for f in frames:
                        if f not in future:
                            victim = f
                            break
                        else:
                            nxt = future.index(f)
                            if nxt > farthest_idx:
                                farthest_idx = nxt
                                victim = f

                    evicted = victim
                    evict_idx = frames.index(evicted)
                    frames[evict_idx] = page

                steps.append(PageStep(idx + 1, page, list(frames), is_fault=True, evicted_page=evicted))

        hits = len(ref_string) - faults
        res = PageReplacementResult(
            algorithm="Optimal",
            reference_string=ref_string,
            num_frames=self.num_frames,
            steps=steps,
            total_page_faults=faults,
            total_page_hits=hits,
            fault_ratio=faults / len(ref_string),
            hit_ratio=hits / len(ref_string)
        )
        logger.info(f"Page Replacement [Optimal]: Faults={faults}, Hits={hits}, Fault Ratio={res.fault_ratio:.2%}")
        return res

    def lfu(self, ref_string: List[int]) -> PageReplacementResult:
        """Least Frequently Used (LFU) Page Replacement."""
        self._validate_ref_string(ref_string)
        frames: List[Optional[int]] = [None] * self.num_frames
        freq: Dict[int, int] = {}
        insertion_time: Dict[int, int] = {}
        steps: List[PageStep] = []
        faults = 0

        for idx, page in enumerate(ref_string):
            freq[page] = freq.get(page, 0) + 1

            if page in frames:
                steps.append(PageStep(idx + 1, page, list(frames), is_fault=False))
            else:
                faults += 1
                evicted = None
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                    insertion_time[page] = idx
                else:
                    # Victim has lowest frequency; tie broken by FIFO insertion time
                    victim = min(frames, key=lambda p: (freq[p], insertion_time.get(p, 0)))
                    evicted = victim
                    evict_idx = frames.index(evicted)
                    frames[evict_idx] = page
                    insertion_time[page] = idx

                steps.append(PageStep(idx + 1, page, list(frames), is_fault=True, evicted_page=evicted))

        hits = len(ref_string) - faults
        res = PageReplacementResult(
            algorithm="LFU",
            reference_string=ref_string,
            num_frames=self.num_frames,
            steps=steps,
            total_page_faults=faults,
            total_page_hits=hits,
            fault_ratio=faults / len(ref_string),
            hit_ratio=hits / len(ref_string)
        )
        logger.info(f"Page Replacement [LFU]: Faults={faults}, Hits={hits}, Fault Ratio={res.fault_ratio:.2%}")
        return res
