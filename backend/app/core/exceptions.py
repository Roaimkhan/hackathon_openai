from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__("authentication_error", message, status.HTTP_401_UNAUTHORIZED)


class ConflictError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__("conflict", message, status.HTTP_409_CONFLICT)


class NotFoundError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__("not_found", message, status.HTTP_404_NOT_FOUND)


class ForbiddenError(AppError):
    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__("forbidden", message, status.HTTP_403_FORBIDDEN)


class BadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__("bad_request", message, status.HTTP_400_BAD_REQUEST)


def error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


def success_payload(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"data": data, "meta": meta or {}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return JSONResponse(status_code=exc.status_code, content=error_payload(exc.code, exc.message), headers=headers)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_payload("validation_error", "Request validation failed"),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_payload("internal_error", "An unexpected error occurred"),
        )
