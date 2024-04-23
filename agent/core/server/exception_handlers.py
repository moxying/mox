import sys
import logging
from typing import Union
from fastapi import Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.exception_handlers import http_exception_handler as _http_exception_handler
from fastapi.exception_handlers import (
    request_validation_exception_handler as _request_validation_exception_handler,
)
from fastapi.responses import JSONResponse
from fastapi.responses import PlainTextResponse
from fastapi.responses import Response
import traceback

from core.const import *


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    This is a wrapper to the default RequestValidationException handler of FastAPI.
    This function will be called when client input is not valid.
    """
    return JSONResponse(
        status_code=400,
        content={
            "code": ERR_CODE_INVALID_PARAM,
            "msg": f"please check request params: {exc.errors()}",
        },
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> Union[JSONResponse, Response]:
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        content={"code": ERR_CODE_HTTP_EXCEPTION, "msg": exc.detail},
        status_code=exc.status_code,
        headers=headers,
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> PlainTextResponse:
    """
    This middleware will log all unhandled exceptions.
    Unhandled exceptions are all exceptions that are not HTTPExceptions or RequestValidationErrors.
    """
    logging.error(f"unhandled_exception_handler was called: {exc}")
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )
    exception_type, exception_value, exception_traceback = sys.exc_info()
    logging.error(traceback.print_exc())
    exception_name = getattr(exception_type, "__name__", None)
    logging.error(
        f'{host}:{port} - "{request.method} {url}" 500 Internal Server Error <{exception_name}: {exception_value}>'
    )
    return JSONResponse(
        status_code=500,
        content={"code": ERR_CODE_INTERNAL_ERROR, "msg": "Internal Server Error"},
    )
