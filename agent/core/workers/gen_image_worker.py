import threading
from queue import Queue
import logging
from typing import Dict, List, Union, Any, Optional
from pydantic import BaseModel
import uuid
import os
from enum import Enum
import traceback

from core.config import ConfigMgr
from core.comfyui.comfyui_client import ComfyUIClient
from core.comfyui.workflows import basic_txt2img
from core.comfyui.workflows.basic_txt2img import BasicTxt2imgTask
from core.const import *
from core.models.common import WSEvent
from core.models.gen_image.object import *
from core.models.gen_image.ws import *
from core.models.gen_image.db import *
from core.server.event import EventDispatcher

from core.storage.storage_mgr import StorageMgr
from core.comfyui.comfyui_client import *
from core.utils.translator import Translator
from core.utils.unionenum import enum_union
from core.utils.utils import get_value_index_in_enum

class GenImageWorkerProgressNameBefore(Enum):
    START = "任务开始"
    TRANSLATION = "翻译成中文"


class GenImageWorkerProgressNameAfter(Enum):
    END = "任务结束"


GenImageWorkerProgressName = enum_union(
    GenImageWorkerProgressNameBefore,
    ComfyUIProgressName,
    GenImageWorkerProgressNameAfter,
)


class GenImageWorker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, name="GenImageWorker")
        self.task_queue = Queue()
        self.comfyui_client = ComfyUIClient()
        self.progress_value = 0

    def run(self):
        logging.info(f"GenImageWorker run start")
        while True:
            try:
                new_task: GenImageWorkerTask = self.task_queue.get()
                logging.info(
                    f"GenImageWorker start handle new task: {new_task.task_id}"
                )
                gen_image_task = get_gen_image_task_db(new_task.task_id)
                EventDispatcher().dispatch_event(
                    EVENT_TYPE_WS,
                    WSEvent(
                        topic=TOPIC_GENIMAGE_PROGRESS,
                        data=GenImageEvent.Data(
                            task_id=new_task.task_id,
                            progress_name=TOPIC_GENIMAGE_PROGRESS,
                            progress_tip=GenImageWorkerProgressNameBefore.START.value,
                            progress_value=list(GenImageWorkerProgressName).index(
                                GenImageWorkerProgressNameBefore.START
                            ),
                            progress_value_max=len(GenImageWorkerProgressName),
                        ),
                    ),
                )
                EventDispatcher().add_event_listener(
                    event_type=f"{EVENT_TYPE_INTERNAL_COMFYUI}_{new_task.task_id}",
                    listener=self.update_progress_listener,
                )

                match new_task.task_type:
                    case TaskType.TXT2IMG:
                        prompt = Translator().run(gen_image_task.prompt)
                        EventDispatcher().dispatch_event(
                            EVENT_TYPE_WS,
                            WSEvent(
                                topic=TOPIC_GENIMAGE_PROGRESS,
                                data=GenImageEvent.Data(
                                    task_id=new_task.task_id,
                                    progress_name=TOPIC_GENIMAGE_PROGRESS,
                                    progress_tip=GenImageWorkerProgressNameBefore.TRANSLATION.value,
                                    progress_value=list(
                                        GenImageWorkerProgressName
                                    ).index(
                                        GenImageWorkerProgressNameBefore.TRANSLATION
                                    ),
                                    progress_value_max=len(GenImageWorkerProgressName),
                                ),
                            ),
                        )
                        basic_txt2img_task = BasicTxt2imgTask(
                            task_id=new_task.task_id,
                            prompt=prompt,
                            ckpt_name=gen_image_task.ckpt_name,
                            negative_prompt=gen_image_task.negative_prompt,
                            seed=gen_image_task.seed,
                            steps=gen_image_task.steps,
                            cfg=gen_image_task.cfg,
                            sampler_name=gen_image_task.sampler_name,
                            scheduler=gen_image_task.scheduler,
                            denoise=gen_image_task.denoise,
                            batch_size=gen_image_task.batch_size,
                            width=gen_image_task.width,
                            height=gen_image_task.height,
                        )
                        basic_txt2img_task_result = basic_txt2img.run(
                            self.comfyui_client, basic_txt2img_task
                        )
                        # task failed
                        if basic_txt2img_task_result.err_msg != None:
                            err_msg = f"basic_txt2img_task failed: {basic_txt2img_task_result.err_msg}"
                            logging.error(err_msg)
                            # update task status to db
                            update_gen_image_task_status(
                                task_id=gen_image_task.id,
                                task_status=TASK_FAILED,
                                err_msg=err_msg,
                            )
                            EventDispatcher().remove_event_listener(
                                f"{EVENT_TYPE_INTERNAL_COMFYUI}_{new_task.task_id}",
                                self.update_progress_listener,
                            )
                            EventDispatcher().dispatch_event(
                                EVENT_TYPE_WS,
                                WSEvent(
                                    topic=TOPIC_GENIMAGE_FAILED,
                                    data=GenImageEvent.Data(
                                        task_id=new_task.task_id,
                                        err_msg=err_msg,
                                    ),
                                ),
                            )
                            continue
                        images = []
                        image_uuid_list = []
                        for image in basic_txt2img_task_result.images:
                            image_uuid = str(uuid.uuid4())
                            image_name = image_uuid + ".png"
                            StorageMgr().save_image(filename=image_name, image=image)
                            images.append(image_name)
                            image_uuid_list.append(image_uuid)
                        add_sd_images_db(
                            uuid_list=image_uuid_list,
                            format="PNG",
                            origin_prompt=gen_image_task.origin_prompt,
                            prompt=basic_txt2img_task_result.prompt,
                            negative_prompt=basic_txt2img_task_result.negative_prompt,
                            width=basic_txt2img_task_result.width,
                            height=basic_txt2img_task_result.height,
                            seed=basic_txt2img_task_result.seed,
                            steps=basic_txt2img_task_result.steps,
                            cfg=basic_txt2img_task_result.cfg,
                            sampler_name=basic_txt2img_task_result.sampler_name,
                            scheduler=basic_txt2img_task_result.scheduler,
                            denoise=basic_txt2img_task_result.denoise,
                            ckpt_name=basic_txt2img_task_result.ckpt_name,
                            gen_image_task_id=gen_image_task.id,
                        )
                        update_gen_image_task_status(task_id=gen_image_task.id,task_status=TASK_DONE)
                    case _:
                        logging.warning(
                            f"not support target task type: {new_task.task_type}, task id: {new_task.task_id}"
                        )
                        continue

                EventDispatcher().remove_event_listener(
                    f"{EVENT_TYPE_INTERNAL_COMFYUI}_{new_task.task_id}",
                    self.update_progress_listener,
                )
                EventDispatcher().dispatch_event(
                    EVENT_TYPE_WS,
                    WSEvent(
                        topic=TOPIC_GENIMAGE_END,
                        data=GenImageEvent.Data(
                            task_id=new_task.task_id, images=images
                        ),
                    ),
                )
                logging.info(f"GenImageWorker task done, task_id: {new_task.task_id}")
            except Exception as err:
                traceback.print_exc()
                logging.error(f"GenImageWorker loop err: {err}")
                continue

    def update_progress_listener(self, event: ComfyUIEventData):
        logging.info(f"update_progress_listener: {event}")
        progress_tip = f"{event.progress_name}"
        if event.progress_tip and len(event.progress_tip) != 0:
            progress_tip = f"{progress_tip}: {event.progress_tip}"
        if event.node_id != None:
            progress_tip = f"{progress_tip} {event.node_progress_value}/{event.node_progress_value_max}"

        EventDispatcher().dispatch_event(
            EVENT_TYPE_WS,
            WSEvent(
                topic=TOPIC_GENIMAGE_PROGRESS,
                data=GenImageEvent.Data(
                    task_id=event.task_id,
                    progress_name=TOPIC_GENIMAGE_PROGRESS,
                    progress_tip=progress_tip,
                    progress_value=get_value_index_in_enum(event.progress_name, GenImageWorkerProgressName),
                    progress_value_max=len(GenImageWorkerProgressName),
                ),
            ),
        )

    def add_task(self, new_task: GenImageTask):
        logging.info(f"GenImageTaskMgr add new task")
        self.task_queue.put(new_task)
