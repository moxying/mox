import logging
import uuid
import asyncio
from fastapi import (
    Depends,
    WebSocket,
    WebSocketDisconnect,
    Request,
)
import json
import random
from fastapi.responses import FileResponse
import traceback
from itertools import groupby
from datetime import datetime, timedelta


from core.config import ConfigMgr
from core.models.common import *
from core.models.config import *
from core.models.gen_image import *
from core.models.gen_image_db import *
from core.workers.gen_image_worker import GenImageWorker, GenImageTask
from core.storage.storage_mgr import StorageMgr

from .basic_server import BasicServer
from .exception_handlers import *


class Server(BasicServer):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__(loop)

        # init router websocket
        self.add_api_websocket_route("/ws", self.ws)

        # init router http

        # 获取配置
        self.add_api_route("/api/config", self.api_get_config, methods=["GET"])
        # 更新配置
        self.add_api_route("/api/config", self.api_update_config, methods=["PUT"])

        # 获取output内的文件
        self.add_api_route(
            "/api/file/output/{filename}", self.api_get_output_file, methods=["GET"]
        )
        # 创作图片
        self.add_api_route("/api/image/create", self.api_gen_image, methods=["POST"])
        # 获取图片列表
        self.add_api_route("/api/image/list", self.api_get_image_list, methods=["POST"])
        # 按日期分类的图片列表
        self.add_api_route(
            "/api/image/list/fragment",
            self.api_get_image_list_as_fragment,
            methods=["POST"],
        )
        # 删除图片
        self.add_api_route(
            "/api/image/{image_uuid}", self.api_delete_image, methods=["DELETE"]
        )
        # 获取随机提示词
        self.add_api_route(
            "/api/image/prompt/random", self.api_get_random_prompt, methods=["GET"]
        )

        logging.info("server init done")

    async def ws(self, websocket: WebSocket):
        try:
            await self.ws_connection_mgr.connect(websocket)
            await websocket.send_json(
                WSEvent(
                    topic=TOPIC_COMMON_STATUS,
                    data=CommonStatusEventData(status="running"),
                ).model_dump()
            )
            try:
                while True:
                    data = await websocket.receive_json()
                    logging.info(f"ws get data: {data}")
                    await websocket.send_json(
                        WSEvent(
                            topic=TOPIC_COMMON_STATUS,
                            data=CommonStatusEventData(status="running"),
                        ).model_dump()
                    )
            except WebSocketDisconnect:
                await self.ws_connection_mgr.disconnect()
        except Exception as err:
            if "already connect one client" in str(err):
                return
            logging.error(f"ws failed, err: {err}")
            traceback.print_exc()

    def api_get_config(self):
        return ConfigMgr().conf()

    def api_update_config(self, request: UpdateConfigRequest):
        return CommonResponse(data="done")

    def api_get_output_file(self, filename: str, request: Request):
        file_storage_dir = ConfigMgr().get_conf("storage")["output_file_dir"]
        return FileResponse(
            path=f"{file_storage_dir}/{filename}", media_type="image/png"
        )

    def api_gen_image(self, request: GenImageRequest) -> GenImageResponse:

        task_uuid = str(uuid.uuid4())
        gen_image_worker: GenImageWorker = self.workers[WORKER_GEN_IMAGE]
        gen_image_worker.add_task(
            GenImageTask(
                task_uuid=task_uuid,
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                batch_size=request.batch_size,
                width=request.width,
                height=request.height,
                seed=request.seed,
            )
        )

        return GenImageResponse(data=GenImageResponseData(task_uuid=task_uuid))

    def api_get_image_list(self, request: GetImageListRequest):
        list, total = get_sd_image_list_db(
            page=request.page, page_size=request.page_size
        )
        return GetImageListResponse(
            data=GetImageListResponseData(
                page=request.page, page_size=request.page_size, total=total, list=list
            )
        )

    def api_get_image_list_as_fragment(self, request: GetImageListAsFragmentRequest):
        list, total = get_sd_image_list_db(
            page=request.page,
            page_size=request.page_size,
            timestamp_filter=request.timestamp_filter,
        )

        # iter array to fragment, group by date
        # 今天
        # 昨天
        # datetime 。。。
        current_date = datetime.now().date()
        yesterday_date = current_date - timedelta(days=1)

        def custom_key_func(elem: SDImage):
            if elem.created_at.date() == current_date:
                return "今天"
            elif elem.created_at.date() == yesterday_date:
                return "昨天"
            else:
                return elem.created_at.date().strftime("%Y年%m月%d日")

        grouped = groupby(list, key=custom_key_func)
        fragments = []
        for key, groupe in grouped:
            fragments.append(SDImageFragment(date=key, list=groupe))
        return GetImageListAsFragmentResponse(
            data=GetImageListAsFragmentResponseData(
                page=request.page,
                page_size=request.page_size,
                total=total,
                cur_total=len(list),
                list=fragments,
            )
        )

    def api_delete_image(self, image_uuid: str):
        sd_image: SDImage = get_sd_image_db(image_uuid)
        if sd_image:
            delete_sd_image_db(image_uuid)
            StorageMgr().delete_image(sd_image.name)
        return CommonResponse(data="delete done")

    def api_get_random_prompt(self, lang: str = None):
        if not lang or len(lang) == 0:
            lang = "zh-cn"
        with open("resource/prompt_example.json", "r", encoding="utf-8") as f:
            examples = json.load(f)
        index = random.randint(0, len(examples))
        return GetRandomPromptResponse(data=examples[index][lang])
