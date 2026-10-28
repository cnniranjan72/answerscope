"""FastAPI application factory. Run: uvicorn app.main:create_app --factory"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from app.api.routes import router
from app.config import Settings, load_settings
from app.db import init_db
from app.errors import AppError

log = logging.getLogger("answerscope")


def _err(status: int, code: str, message: str, details=None) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message, "details": details}},
                        headers={"WWW-Authenticate": "Bearer"} if status == 401 else None)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    init_db(settings.db_path)
    app = FastAPI(
        title="AnswerScope",
        version="1.0.0",
        description="AI-visibility analysis of archived answers about Kasparro, with enforced human review. "
                    "Authenticate with `Authorization: Bearer <ANALYST_TOKEN|REVIEWER_TOKEN>`.",
    )
    app.state.settings = settings

    @app.exception_handler(AppError)
    async def app_error(_: Request, exc: AppError):
        return _err(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        details = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()[:20]]
        return _err(422, "request_validation_failed", "request body or parameters are invalid", details)

    @app.exception_handler(Exception)
    async def unexpected(_: Request, exc: Exception):
        log.exception("unhandled error")  # details go to the server log, never to the client
        return _err(500, "internal_error", "unexpected server error")

    app.include_router(router)

    @app.get("/", include_in_schema=False)
    def console():
        # Static review console; holds no data and calls the same token-protected API.
        return FileResponse(Path(__file__).with_name("static") / "index.html")

    return app

