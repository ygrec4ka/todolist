from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Базовое исключение API"""

    def __init__(self, status_code: int, detail: str):
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


class NotFoundException(BaseAPIException):
    """Исключение для случаев, когда ресурс не найден"""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class AccessDeniedException(BaseAPIException):
    """Исключение когда у пользователя нет прав"""

    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class ValidationException(BaseAPIException):
    """Исключение для ошибок валидации данных"""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ConflictException(BaseAPIException):
    """Исключение для конфликтующих данных"""

    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


# Перебросил все импорты кастомных исключений для более удобного использования
from .tasks import TaskNotFoundException, TaskAccessDeniedException
from .users import (
    UserNotFoundException,
    UserAccessDeniedException,
    UserAlreadyExistsException,
    UserNotActiveException,
    UserNotVerifiedException,
)
from .notes import NoteNotFoundException, NoteAccessDeniedException
from .comments import CommentNotFoundException, CommentAccessDeniedException
from .auth import (
    InvalidCredentialsException,
    TokenExpiredException,
    TokenInvalidException,
    RefreshTokenRevokedException,
    InsufficientPermissionsException,
)
