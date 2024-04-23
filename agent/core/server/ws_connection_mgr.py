from fastapi import WebSocket
import logging

from core.models.common import WSEvent


class WSConnectionMgr:
    def __init__(self):
        self.connection = None

    async def connect(self, websocket: WebSocket):
        if self.connection:
            err_msg = f"already connect one client"
            logging.warn(err_msg)
            raise Exception(err_msg)
        await websocket.accept()
        logging.info(f"ws new connection")
        self.connection = websocket

    async def disconnect(self):
        self.connection = None
        logging.info(f"ws client disconnect")

    async def send_json_event(self, event: WSEvent):
        if not self.connection:
            # logging.warn(
            #     f"client disconnect, ignore event, event: {event.model_dump(exclude_unset=True)}"
            # )
            return
        await self.connection.send_json(event.model_dump(exclude_unset=True))
