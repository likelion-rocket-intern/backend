from enum import Enum

class TaskStatus(str, Enum):
    """작업 상태를 나타내는 Enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskResumeStatus(str, Enum):
    """이력서 분석 상태를 나타내는 Enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    PARSING = "parsing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"