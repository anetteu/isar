from enum import Enum


class TaskStatus(str, Enum):

    NotStarted: str = "not_started"
    Completed: str = "completed"
    InProgress: str = "in_progress"
    Failed: str = "failed"
    Unexpected: str = "error_unexpected"
