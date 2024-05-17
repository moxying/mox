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
from core.models.gen_image.object import *
from core.models.gen_image.db import *
from core.models.gen_image.api import *
from core.workers.gen_image_worker import GenImageWorker, GenImageTask
from core.storage.storage_mgr import StorageMgr

from .basic_server import BasicServer
from .exception_handlers import *


class Server(BasicServer):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__(loop)

        # init router websocket
        self.add_api_websocket_route("/ws", self.ws)

        #
        # init router http
        #

        # 获取随机提示词
        self.add_api_route(
            "/api/image/prompt/random", self.api_get_random_prompt, methods=["GET"]
        )
        # 获取任务列表
        self.add_api_route("/api/image/tasks", self.api_image_tasks, methods=["POST"])

        # 文生图、调整-重新生成
        self.add_api_route("/api/image/txt2img", self.api_txt2img, methods=["POST"])
        # 变化
        self.add_api_route("/api/image/img2img", self.api_img2img, methods=["POST"])
        # 高清
        self.add_api_route(
            "/api/image/img2img/upscale", self.api_img2img_upscale, methods=["POST"]
        )
        # 调整-局部重绘
        self.add_api_route(
            "/api/image/img2img/inpainting",
            self.api_img2img_inpainting,
            methods=["POST"],
        )
        # 扩图
        self.add_api_route(
            "/api/image/img2img/outpainting",
            self.api_img2img_outpainting,
            methods=["POST"],
        )

        # 获取收藏夹列表
        self.add_api_route(
            "/api/image/collections",
            self.api_get_collection_list,
            methods=["GET"],
        )
        # 创建收藏夹
        self.add_api_route(
            "/api/image/collection",
            self.api_add_image_collection,
            methods=["POST"],
        )
        # 删除收藏夹
        self.add_api_route(
            "/api/image/collection",
            self.api_delete_image_collection,
            methods=["DELETE"],
        )
        # 添加到收藏夹
        self.add_api_route(
            "/api/image/collection/add",
            self.api_add_images_to_collection,
            methods=["POST"],
        )
        # 从收藏夹移除
        self.add_api_route(
            "/api/image/collection/delete",
            self.api_delete_images_from_collection,
            methods=["POST"],
        )

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

        # 获取output内的文件
        self.add_api_route(
            "/api/file/output/{filename}", self.api_get_output_file, methods=["GET"]
        )

        # 获取配置
        self.add_api_route("/api/config", self.api_get_config, methods=["GET"])
        # 更新配置
        self.add_api_route("/api/config", self.api_update_config, methods=["PUT"])

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

    # 获取随机提示词
    def api_get_random_prompt(self, lang: str = None):
        if not lang or len(lang) == 0:
            lang = "zh-cn"
        with open("resource/prompt_example.json", "r", encoding="utf-8") as f:
            examples = json.load(f)
        index = random.randint(0, len(examples))
        return GetRandomPromptResponse(data=examples[index][lang])

    # 获取任务列表
    def api_image_tasks(self, request: GetImageTasksRequest) -> GetImageTasksResponse:
        list, total = get_gen_image_task_list_db(
            page=request.page, page_size=request.page_size
        )
        return GetImageTasksResponse(
            data=GetImageTasksResponse.Data(
                page=request.page, page_size=request.page_size, total=total, list=list
            )
        )

    # 文生图、调整-重新生成
    def api_txt2img(self, request: Txt2imgRequest) -> Txt2imgResponse:

        logging.debug(f"api_txt2img request: {request.model_dump_json()}")

        # add task to db
        task_id = add_gen_image_task_db(
            task_type=TaskType.TXT2IMG.value,
            task_tags=request.task_tags,
            origin_prompt=request.origin_prompt,
            negative_prompt=request.negative_prompt,
            batch_size=request.batch_size,
            width=request.width,
            height=request.height,
            seed=request.seed,
            steps=request.steps,
            cfg=request.cfg,
            sampler_name=request.sampler_name,
            scheduler=request.scheduler,
            denoise=request.denoise,
            ckpt_name=request.ckpt_name,
        )
        logging.debug(f"new txt2img task, add to db done, id: {task_id}")

        # add task to work
        gen_image_worker: GenImageWorker = self.workers[WORKER_GEN_IMAGE]
        gen_image_worker.add_task(
            GenImageWorkerTask(task_id=task_id, task_type=TaskType.TXT2IMG)
        )

        return Txt2imgResponse(data=Txt2imgResponse.Data(id=task_id))

    # 变化
    def api_img2img(self):
        pass

    # 高清
    def api_img2img_upscale(self):
        pass

    # 调整-局部重绘
    def api_img2img_inpainting(self):
        pass

    # 扩图
    def api_img2img_outpainting(self):
        pass

    # 获取收藏夹列表
    def api_get_collection_list(self):
        collections = get_image_collection_list()
        return CommonResponse(data=collections)

    # 创建收藏夹
    def api_add_image_collection(self, request: AddCollectionRequest):
        try:
            add_image_collection(request.name)
        except Exception as err:
            if "UNIQUE constraint failed" in f"{err}":
                return CommonResponse(code=ERR_CODE_INVALID_PARAM, msg="名称已经存在")
            raise err

        return CommonResponse()

    # 删除收藏夹
    def api_delete_image_collection(self, request: DeleteCollectionRequest):
        delete_image_collection(request.name)
        return CommonResponse()

    # 添加到收藏夹
    def api_add_images_to_collection(self, request: AddImagesToCollectionRequest):
        add_images_to_collection(request.image_uuid_list, request.name)
        return CommonResponse()

    # 从收藏夹移除
    def api_delete_images_from_collection(
        self, request: DeleteImagesFromCollectionRequest
    ):
        delete_images_from_collection(request.image_uuid_list, request.name)
        return CommonResponse()

    # 按日期分类的图片列表
    def api_get_image_list_as_fragment(self, request: GetImageListAsFragmentRequest):
        list, total = get_sd_image_list_db(
            page=request.page,
            page_size=request.page_size,
            timestamp_filter=request.timestamp_filter,
            collection_filter=request.collection_filter,
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
            fragments.append(
                GetImageListAsFragmentResponse.Data.SDImageFragment(
                    date=key, list=groupe
                )
            )
        return GetImageListAsFragmentResponse(
            data=GetImageListAsFragmentResponse.Data(
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
            StorageMgr().delete_image(f"{sd_image.uuid}.{sd_image.format}")
        return CommonResponse(data="delete done")

    def api_get_output_file(self, filename: str, request: Request):
        file_storage_dir = ConfigMgr().get_conf("storage")["output_file_dir"]
        return FileResponse(
            path=f"{file_storage_dir}/{filename}", media_type="image/png"
        )

    def api_get_config(self):
        return ConfigMgr().conf()

    def api_update_config(self, request: UpdateConfigRequest):
        return CommonResponse(data="done")
