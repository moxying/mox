import time
import logging
from fastapi import (
    FastAPI,
    Request,
    Response,
)

from core.config import ConfigMgr


def api_middleware(app: FastAPI):

    @app.middleware("http")
    async def log_and_time(req: Request, call_next):
        ts = time.time()
        res: Response = await call_next(req)
        duration = str(round(time.time() - ts, 4))
        res.headers["X-Process-Time"] = duration
        endpoint = req.scope.get("path", "err")
        if ConfigMgr().get_conf("server")["api_log"] and endpoint.startswith("/api"):
            method = req.scope.get("method", "err")
            cli = req.scope.get("client", ("0:0.0.0", 0))[0]
            logging.info(
                f"[Access] {res.status_code} {method} {endpoint} {cli} {duration}s"
            )
        return res
