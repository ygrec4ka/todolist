from . import ValidationException, AccessDeniedException


class InvalidCredentialsException(ValidationException):
    def __init__(self):
        super().__init__(detail="Invalid email or password")


class TokenExpiredException(ValidationException):
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(detail=detail)


class TokenInvalidException(ValidationException):
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(detail=detail)


class TokenTypeException(ValidationException):
    def __init__(self, detail: str = "Invalid token type"):
        super().__init__(detail=detail)


class InsufficientPermissionsException(AccessDeniedException):
    def __init__(self):
        super().__init__(detail="Insufficient permissions")


class RefreshTokenRevokedException(AccessDeniedException):
    def __init__(self):
        super().__init__(detail="Refresh token has been revoked")
