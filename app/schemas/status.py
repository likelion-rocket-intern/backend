from enum import Enum

class TaskStatus(str, Enum):
    """작업 상태를 나타내는 Enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"