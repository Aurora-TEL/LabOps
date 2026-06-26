from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings


ERROR_CODE_BY_STATUS = {
    400: 40000,
    401: 40001,
    403: 40003,
    404: 40004,
    409: 40900,
    422: 40000,
}


def error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": ERROR_CODE_BY_STATUS.get(status_code, 50000), "message": message, "data": None},
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        _ = request
        return error_response(exc.status_code, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        _ = request
        first_error = exc.errors()[0] if exc.errors() else {}
        location = ".".join(str(part) for part in first_error.get("loc", []))
        message = first_error.get("msg", "request validation error")
        return error_response(422, f"{location}: {message}" if location else str(message))

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "name": settings.project_name,
            "version": settings.version,
            "docs": "/docs",
            "api": settings.api_v1_prefix,
        }

    return app


app = create_app()
