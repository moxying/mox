import logging
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
)
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from secrets import compare_digest
import asyncio
import uvicorn
import threading

from core.config import ConfigMgr
from core.models.common import *
from core.storage.storage_mgr import StorageMgr

from .uvicorn_server import UvicornServer
from .middleware import api_middleware
from .ws_connection_mgr import WSConnectionMgr
from .event import EventDispatcher
from .exception_handlers import *


class BasicServer:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        if ConfigMgr().get_conf("server")["debug"]:
            self.uvicorn_log_level = "trace"
            self.fast_api_debug = True
            loop.set_debug(True)
        else:
            self.uvicorn_log_level = "critical"
            self.fast_api_debug = False

        self.loop = loop
        self.ws_event_queue: asyncio.Queue = asyncio.Queue()
        self.workers = dict()

        # init app api
        self.app = FastAPI(debug=self.fast_api_debug)
        if ConfigMgr().get_conf("server")["api_auth"]:
            self.credentials = dict()
            for auth in ConfigMgr().get_conf("server")["default_admin"].split(","):
                user, password = auth.split(":")
                self.credentials[user] = password

        # init api middleware
        api_middleware(self.app)

        # init exception handler
        self.app.add_exception_handler(
            RequestValidationError, request_validation_exception_handler
        )
        self.app.add_exception_handler(HTTPException, http_exception_handler)
        self.app.add_exception_handler(Exception, unhandled_exception_handler)

        # init ws connection mgr
        self.ws_connection_mgr = WSConnectionMgr()
        # init storage mgr
        self.storage_mgr = StorageMgr()

        # init event dispatcher
        dispatcher = EventDispatcher()
        threading.Thread(target=dispatcher.start_dispatching, daemon=True).start()
        dispatcher.add_event_listener(EVENT_TYPE_WS, self.ws_send_event_sync)

    async def run(self):
        host = ConfigMgr().get_conf("server")["host"]
        port = ConfigMgr().get_conf("server")["port"]
        logging.info(f"API Server start, server_name: {host}, port: {port}")
        uvicorn_config = uvicorn.Config(
            app=self.app,
            loop=self.loop,
            host=host,
            port=port,
            log_level=self.uvicorn_log_level,  # critical info trace
        )
        self.uvicorn_server = UvicornServer(uvicorn_config)
        await asyncio.gather(self.uvicorn_server.serve(), self._ws_event_loop())

    def ws_send_event_sync(self, event: WSEvent):
        # 在 asyncio 中，所有的事件循环操作都应该在同一个线程中完成，以确保线程安全性。但有时候，我们可能需要在不同的线程中调用事件循环。这时就可以使用 call_soon_threadsafe 来安全地将回调函数放入事件循环的队列中，以便稍后在事件循环中执行。
        self.loop.call_soon_threadsafe(self.ws_event_queue.put_nowait, event)

    async def _ws_event_loop(self):
        while True:
            event: WSEvent = await self.ws_event_queue.get()
            await self._ws_send_event(event)

    async def _ws_send_event(self, event: WSEvent):
        if event.topic == "todo":
            raise NotImplementedError()
        else:
            await self._ws_send_json(event)

    async def _ws_send_json(self, event: WSEvent):
        await self.ws_connection_mgr.send_json_event(event)

    def add_api_route(self, path: str, endpoint, **kwargs):
        if ConfigMgr().get_conf("server")["api_auth"]:
            return self.app.add_api_route(
                path,
                endpoint,
                response_model_exclude_none=True,
                dependencies=[Depends(self.auth)],
                **kwargs,
            )
        return self.app.add_api_route(
            path, endpoint, response_model_exclude_none=True, **kwargs
        )

    def auth(self, credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
        if credentials.username in self.credentials:
            if compare_digest(
                credentials.password, self.credentials[credentials.username]
            ):
                return True
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    def add_api_websocket_route(self, path: str, endpoint, **kwargs):
        return self.app.add_api_websocket_route(path, endpoint, **kwargs)

    def shutdown(self):
        try:
            self._cancel_all_tasks()
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.run_until_complete(self.loop.shutdown_default_executor())
        finally:
            asyncio.set_event_loop(None)
            self.loop.close()

    def _cancel_all_tasks(self):
        to_cancel = asyncio.all_tasks(self.loop)
        if not to_cancel:
            return

        for task in to_cancel:
            task.cancel()

        self.loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))

        for task in to_cancel:
            if task.cancelled():
                continue
            if task.exception() is not None:
                self.loop.call_exception_handler(
                    {
                        "message": "unhandled exception during asyncio.run() shutdown",
                        "exception": task.exception(),
                        "task": task,
                    }
                )

    def add_worker(self, worker_name: str, worker):
        if worker_name not in self.workers.keys():
            self.workers[worker_name] = worker
