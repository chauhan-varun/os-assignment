"""
Custom exception hierarchy for the OS Resource Management Simulator.
Provides robust boundary and validation error handling.
"""

class SimOSError(Exception):
    """Base class for all simulator exceptions."""
    pass


class InvalidProcessError(SimOSError):
    """Raised when process parameters (burst, arrival, priority) are invalid."""
    pass


class InvalidQuantumError(SimOSError):
    """Raised when Round Robin time quantum is non-positive."""
    pass


class MemoryAllocationError(SimOSError):
    """Raised when memory allocation fails due to lack of space or fragmentation."""
    pass


class InvalidMemoryAccessError(SimOSError):
    """Raised when an illegal memory address or page request occurs."""
    pass


class DeadlockStateError(SimOSError):
    """Raised when system transitions into an unsafe or deadlocked state."""
    pass


class InvalidResourceRequestError(SimOSError):
    """Raised when a process requests resources exceeding its maximum claim or available pool."""
    pass


class StorageAllocationError(SimOSError):
    """Raised when disk allocation fails or block boundary is exceeded."""
    pass


class InvalidDiskRequestError(SimOSError):
    """Raised when disk cylinder/track requests fall outside valid disk geometry."""
    pass


class WorkloadParseError(SimOSError):
    """Raised when an input configuration file is malformed or missing fields."""
    pass
