"""
Deadlock Avoidance and Detection Module.
Includes:
1. Banker's Algorithm (Safety check & Resource-Request algorithm) for multi-instance resources.
2. Resource Allocation Graph (RAG) and Wait-For-Graph (WFG) cycle detection for deadlock identification.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Set
import copy

from core.exceptions import DeadlockStateError, InvalidResourceRequestError
from core.logger import get_logger

logger = get_logger()


@dataclass
class SafetyResult:
    is_safe: bool
    safe_sequence: List[str]
    work_progression: List[Dict[str, int]]
    error_message: Optional[str] = None


@dataclass
class ResourceRequestResult:
    granted: bool
    message: str
    resulting_safety: SafetyResult
    new_available: Dict[str, int]
    new_allocation: Dict[str, Dict[str, int]]
    new_need: Dict[str, Dict[str, int]]


class BankersAlgorithm:
    """Simulates Dijkstra's Banker's Algorithm for deadlock avoidance."""

    def __init__(
        self,
        resource_names: List[str],
        available: Dict[str, int],
        max_claim: Dict[str, Dict[str, int]],
        allocation: Dict[str, Dict[str, int]],
    ):
        self.resource_names = sorted(list(resource_names))
        self.available = copy.deepcopy(available)
        self.max_claim = copy.deepcopy(max_claim)
        self.allocation = copy.deepcopy(allocation)
        self.processes = sorted(list(self.max_claim.keys()))

        self._validate_matrices()
        self.need = self._compute_need()

    def _validate_matrices(self):
        # Validate available
        for r in self.resource_names:
            if r not in self.available or self.available[r] < 0:
                raise InvalidResourceRequestError(f"Resource {r} available count invalid: {self.available.get(r)}")

        # Validate allocation and max claim
        for p in self.processes:
            if p not in self.allocation:
                raise InvalidResourceRequestError(f"Process {p} missing from allocation matrix.")
            for r in self.resource_names:
                alloc = self.allocation[p].get(r, 0)
                max_c = self.max_claim[p].get(r, 0)
                if alloc < 0 or max_c < 0:
                    raise InvalidResourceRequestError(f"Negative values for process {p}, resource {r}.")
                if alloc > max_c:
                    raise InvalidResourceRequestError(
                        f"Allocation exceeds max claim for process {p}, resource {r}: ({alloc} > {max_c})."
                    )

    def _compute_need(self) -> Dict[str, Dict[str, int]]:
        need: Dict[str, Dict[str, int]] = {}
        for p in self.processes:
            need[p] = {}
            for r in self.resource_names:
                need[p][r] = self.max_claim[p][r] - self.allocation[p][r]
        return need

    def is_safe_state(self) -> SafetyResult:
        """Executes Banker's Safety Algorithm to verify if system is in a safe state."""
        work = copy.deepcopy(self.available)
        finish = {p: False for p in self.processes}
        safe_seq: List[str] = []
        work_history: List[Dict[str, int]] = [copy.deepcopy(work)]

        while len(safe_seq) < len(self.processes):
            found = False
            for p in self.processes:
                if not finish[p]:
                    # Check if Need[p] <= Work
                    can_allocate = all(self.need[p][r] <= work[r] for r in self.resource_names)
                    if can_allocate:
                        for r in self.resource_names:
                            work[r] += self.allocation[p][r]
                        finish[p] = True
                        safe_seq.append(p)
                        work_history.append(copy.deepcopy(work))
                        found = True
                        break

            if not found:
                deadlocked = [p for p in self.processes if not finish[p]]
                msg = f"System is in an UNSAFE state! Deadlocked/Blocked processes: {', '.join(deadlocked)}"
                logger.warning(msg)
                return SafetyResult(is_safe=False, safe_sequence=[], work_progression=work_history, error_message=msg)

        logger.info(f"System is in SAFE state. Safe sequence: {' -> '.join(safe_seq)}")
        return SafetyResult(is_safe=True, safe_sequence=safe_seq, work_progression=work_history)

    def request_resources(self, pid: str, request: Dict[str, int]) -> ResourceRequestResult:
        """
        Processes a resource request from process `pid`.
        Returns ResourceRequestResult detailing whether request was granted or denied.
        """
        if pid not in self.processes:
            raise InvalidResourceRequestError(f"Unknown process: {pid}")

        # Check 1: Request <= Need[pid]
        for r in self.resource_names:
            req_val = request.get(r, 0)
            if req_val < 0:
                raise InvalidResourceRequestError(f"Negative request value for resource {r}: {req_val}")
            if req_val > self.need[pid][r]:
                msg = f"Error: Process {pid} exceeded maximum need for {r} ({req_val} > {self.need[pid][r]})."
                logger.error(msg)
                return ResourceRequestResult(
                    granted=False,
                    message=msg,
                    resulting_safety=SafetyResult(False, [], []),
                    new_available=self.available,
                    new_allocation=self.allocation,
                    new_need=self.need
                )

        # Check 2: Request <= Available
        for r in self.resource_names:
            req_val = request.get(r, 0)
            if req_val > self.available[r]:
                msg = f"Denied: Insufficient available resource {r} ({req_val} requested, only {self.available[r]} available). Process must wait."
                logger.warning(msg)
                return ResourceRequestResult(
                    granted=False,
                    message=msg,
                    resulting_safety=SafetyResult(False, [], []),
                    new_available=self.available,
                    new_allocation=self.allocation,
                    new_need=self.need
                )

        # Pretend allocation
        temp_avail = copy.deepcopy(self.available)
        temp_alloc = copy.deepcopy(self.allocation)
        temp_need = copy.deepcopy(self.need)

        for r in self.resource_names:
            req_val = request.get(r, 0)
            temp_avail[r] -= req_val
            temp_alloc[pid][r] += req_val
            temp_need[pid][r] -= req_val

        # Test safety of pretend state
        test_banker = BankersAlgorithm(
            resource_names=self.resource_names,
            available=temp_avail,
            max_claim=self.max_claim,
            allocation=temp_alloc
        )
        safety = test_banker.is_safe_state()

        if safety.is_safe:
            # Commit changes
            self.available = temp_avail
            self.allocation = temp_alloc
            self.need = temp_need
            msg = f"Granted: Request by {pid} approved. Safe sequence: {' -> '.join(safety.safe_sequence)}"
            logger.info(msg)
            return ResourceRequestResult(
                granted=True,
                message=msg,
                resulting_safety=safety,
                new_available=self.available,
                new_allocation=self.allocation,
                new_need=self.need
            )
        else:
            msg = f"Denied: Granting request by {pid} results in an UNSAFE state. Allocation rolled back."
            logger.warning(msg)
            return ResourceRequestResult(
                granted=False,
                message=msg,
                resulting_safety=safety,
                new_available=self.available,
                new_allocation=self.allocation,
                new_need=self.need
            )


@dataclass
class DeadlockDetectionResult:
    deadlock_detected: bool
    deadlocked_nodes: List[str]
    detected_cycles: List[List[str]]


class DeadlockDetector:
    """Graph-based Deadlock Detection using Wait-For Graph (WFG) cycle detection."""

    def __init__(self, adjacency_list: Dict[str, List[str]]):
        self.adj = copy.deepcopy(adjacency_list)

    def detect_cycles(self) -> DeadlockDetectionResult:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []
        path: List[str] = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Cycle found
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            path.pop()
            rec_stack.remove(node)

        for node in list(self.adj.keys()):
            if node not in visited:
                dfs(node)

        deadlocked_nodes = sorted(list({node for cycle in cycles for node in cycle}))
        is_deadlocked = len(cycles) > 0

        if is_deadlocked:
            logger.warning(f"Deadlock detected! Cycles: {cycles}")
        else:
            logger.info("No deadlock detected in Wait-For Graph.")

        return DeadlockDetectionResult(
            deadlock_detected=is_deadlocked,
            deadlocked_nodes=deadlocked_nodes,
            detected_cycles=cycles
        )
