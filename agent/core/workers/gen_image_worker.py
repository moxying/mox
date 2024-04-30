import threading
from queue import Queue
import logging
from typing import Dict, List, Union, Any, Optional
from pydantic import BaseModel
import uuid
import os

from core.config import ConfigMgr
from core.comfyui.comfyui_client import ComfyUIClient
from core.comfyui.workflows import basic_sdxl_jxl
from core.comfyui.workflows.basic_sdxl_jxl import BasicSDXLJXLTask

from core.const import *
from core.models.common import WSEvent
from core.models.gen_image import *
from core.server.event import EventDispatcher
from core.models.gen_image_db import add_sd_image_db
from core.storage.storage_mgr import StorageMgr
from core.comfyui.comfyui_client import *
from core.utils.translator import Translator


class GenImageTask(BaseModel):
    task_uuid: str
    prompt: str
    negative_prompt: Optional[str] = ""
    batch_size: Optional[int] = 1
    width: Optional[int] = 512
    height: Optional[int] = 768
    seed: Optional[int] = 0
    style_name: Optional[str] = ""


class GenImageWorker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, name="GenImageWorker")
        self.task_queue = Queue()
        self.comfyui_client = ComfyUIClient()
        self.progress_value = 0

    def run(self):
        logging.info(f"GenImageWorker run start")
        while True:
            new_task: GenImageTask = self.task_queue.get()
            logging.info(
                f"GenImageWorker start handle new task: {new_task.task_uuid}, prompt: {new_task.prompt}"
            )
            EventDispatcher().dispatch_event(
                EVENT_TYPE_WS,
                WSEvent(
                    topic=TOPIC_GENIMAGE_START,
                    data=GenImageEventData(task_uuid=new_task.task_uuid),
                ),
            )
            EventDispatcher().add_event_listener(
                f"{EVENT_TYPE_INTERNAL_COMFYUI}_{new_task.task_uuid}",
                self.update_progress_listener,
            )
            basic_sdxl_jxl_task = BasicSDXLJXLTask(
                task_uuid=new_task.task_uuid,
                prompt=Translator().run(new_task.prompt),
                negative_prompt=new_task.negative_prompt,
                seed=new_task.seed,
                batch_size=new_task.batch_size,
                width=new_task.width,
                height=new_task.height,
            )
            basic_sdxl_jxl_task_result = basic_sdxl_jxl.run(
                self.comfyui_client, basic_sdxl_jxl_task
            )
            if basic_sdxl_jxl_task_result.err_msg != None:
                logging.error(
                    f"basic_sdxl_jxl_task failed: {basic_sdxl_jxl_task_result.err_msg}"
                )
                EventDispatcher().remove_event_listener(
                    f"{EVENT_TYPE_INTERNAL_COMFYUI}_{new_task.task_uuid}",
                    self.update_progress_listener,
                )
                EventDispatcher().dispatch_event(
                    EVENT_TYPE_WS,
                    WSEvent(
                        topic=TOPIC_GENIMAGE_FAILED,
                        data=GenImageEventData(
                            task_uuid=new_task.task_uuid,
                            err_msg=basic_sdxl_jxl_task_result.err_msg,
                        ),
                    ),
                )
                continue
            images = []
            for image in basic_sdxl_jxl_task_result.images:
                image_uuid = str(uuid.uuid4())
                image_name = image_uuid + ".png"
                StorageMgr().save_image(filename=image_name, image=image)
                add_sd_image_db(
                    uuid=image_uuid,
                    task_uuid=new_task.task_uuid,
                    name=image_name,
                    time_cost=0,
                    origin_prompt=new_task.prompt,
                    prompt=basic_sdxl_jxl_task_result.prompt,
                    negative_prompt=basic_sdxl_jxl_task_result.negative_prompt,
                    width=basic_sdxl_jxl_task_result.width,
                    height=basic_sdxl_jxl_task_result.height,
                    seed=basic_sdxl_jxl_task_result.seed,
                    steps=basic_sdxl_jxl_task_result.steps,
                    cfg=basic_sdxl_jxl_task_result.cfg,
                    sampler_name=basic_sdxl_jxl_task_result.sampler_name,
                    scheduler=basic_sdxl_jxl_task_result.scheduler,
                    ckpt_name=basic_sdxl_jxl_task_result.ckpt_name,
                )
                images.append(image_name)
            EventDispatcher().remove_event_listener(
                f"{EVENT_TYPE_INTERNAL_COMFYUI}_{new_task.task_uuid}",
                self.update_progress_listener,
            )
            EventDispatcher().dispatch_event(
                EVENT_TYPE_WS,
                WSEvent(
                    topic=TOPIC_GENIMAGE_END,
                    data=GenImageEventData(task_uuid=new_task.task_uuid, images=images),
                ),
            )
            logging.info(f"GenImageWorker task done, task_uuid: {new_task.task_uuid}")

    def update_progress_listener(self, event: ComfyUIEventData):
        logging.info(f"update_progress_listener: {event}")
        if event.progress_name == NAME_SUBMIT_TASK:
            self.progress_value = 1
            EventDispatcher().dispatch_event(
                EVENT_TYPE_WS,
                WSEvent(
                    topic=TOPIC_GENIMAGE_PROGRESS,
                    data=GenImageEventData(
                        task_uuid=event.task_uuid,
                        progress_tip=event.progress_name,
                        progress_value=self.progress_value,
                        progress_value_max=event.progress_value_max,
                    ),
                ),
            )
        elif event.progress_name == NAME_TASK_NODE_CACHED:
            self.progress_value += len(event.cached_nodes)
            EventDispatcher().dispatch_event(
                EVENT_TYPE_WS,
                WSEvent(
                    topic=TOPIC_GENIMAGE_PROGRESS,
                    data=GenImageEventData(
                        task_uuid=event.task_uuid,
                        progress_tip=event.progress_name,
                        progress_value=self.progress_value,
                        progress_value_max=event.progress_value_max,
                    ),
                ),
            )
        elif event.progress_name == NAME_TASK_NODE_START:
            self.progress_value += 1
            EventDispatcher().dispatch_event(
                EVENT_TYPE_WS,
                WSEvent(
                    topic=TOPIC_GENIMAGE_PROGRESS,
                    data=GenImageEventData(
                        task_uuid=event.task_uuid,
                        progress_tip=f"{event.progress_name}: {event.progress_tip}",
                        progress_value=self.progress_value,
                        progress_value_max=event.progress_value_max,
                    ),
                ),
            )
        elif event.progress_name == NAME_TASK_NODE_DOING:
            EventDispatcher().dispatch_event(
                EVENT_TYPE_WS,
                WSEvent(
                    topic=TOPIC_GENIMAGE_PROGRESS,
                    data=GenImageEventData(
                        task_uuid=event.task_uuid,
                        progress_tip=f"{event.progress_name}: {event.progress_tip}; 进度: {event.node_progress_value}/{event.node_progress_value_max}",
                        progress_value=self.progress_value,
                        progress_value_max=event.progress_value_max,
                    ),
                ),
            )
        elif event.progress_name == NAME_TASK_DONE:
            self.progress_value = event.progress_value_max
            EventDispatcher().dispatch_event(
                EVENT_TYPE_WS,
                WSEvent(
                    topic=TOPIC_GENIMAGE_PROGRESS,
                    data=GenImageEventData(
                        task_uuid=event.task_uuid,
                        progress_tip=event.progress_name,
                        progress_value=self.progress_value,
                        progress_value_max=event.progress_value_max,
                    ),
                ),
            )
        elif event.progress_name == NAME_TASK_FAILED:
            EventDispatcher().dispatch_event(
                EVENT_TYPE_WS,
                WSEvent(
                    topic=TOPIC_GENIMAGE_PROGRESS,
                    data=GenImageEventData(
                        task_uuid=event.task_uuid,
                        progress_tip=event.progress_name,
                        progress_value=self.progress_value,
                        progress_value_max=event.progress_value_max,
                        err_msg=event.err_msg,
                    ),
                ),
            )

    def add_task(self, new_task: GenImageTask):
        logging.info(f"GenImageTaskMgr add new task")
        self.task_queue.put(new_task)
