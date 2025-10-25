from core.exceptions import NotFoundException, AccessDeniedException


class TaskNotFoundException(NotFoundException):
    """Исключение если задача не найдена"""

    def __init__(self):
        super().__init__(
            detail=f"Task not found",
        )


class TaskAccessDeniedException(AccessDeniedException):
    """Исключение когда нет доступа к задаче"""

    def __init__(self):
        super().__init__(detail="Access denied to task")
