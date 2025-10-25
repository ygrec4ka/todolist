from . import NotFoundException, AccessDeniedException, ConflictException


class UserNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__(detail="User not found")


class UserAccessDeniedException(AccessDeniedException):
    def __init__(self):
        super().__init__(detail="Access denied to user")


class UserAlreadyExistsException(ConflictException):
    def __init__(self):
        super().__init__(detail="User already exists")


class UserNotActiveException(AccessDeniedException):
    def __init__(self):
        super().__init__(detail="User account is not active")


class UserNotVerifiedException(AccessDeniedException):
    def __init__(self):
        super().__init__(detail="User account is not verified")
