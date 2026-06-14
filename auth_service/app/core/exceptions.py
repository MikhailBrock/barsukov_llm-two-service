from fastapi import HTTPException


class BaseHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class UserAlreadyExistsError(BaseHTTPException):
    def __init__(self):
        super().__init__(409, "User already exists")


class InvalidCredentialsError(BaseHTTPException):
    def __init__(self):
        super().__init__(401, "Invalid credentials")


class InvalidTokenError(BaseHTTPException):
    def __init__(self):
        super().__init__(401, "Invalid token")


class TokenExpiredError(BaseHTTPException):
    def __init__(self):
        super().__init__(401, "Token has expired")


class UserNotFoundError(BaseHTTPException):
    def __init__(self):
        super().__init__(404, "User not found")


class PermissionDeniedError(BaseHTTPException):
    def __init__(self):
        super().__init__(403, "Permission denied")
