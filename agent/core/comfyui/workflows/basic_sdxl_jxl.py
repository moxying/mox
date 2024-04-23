import logging
from typing import Optional, List
from pydantic import BaseModel
import json
import traceback
import random

from core.comfyui.comfyui_client import ComfyUIClient


class BasicSDXLJXLTask(BaseModel):
    task_uuid: str
    prompt: str

    # optional
    negative_prompt: Optional[str] = ""
    seed: Optional[int] = 0
    batch_size: int = 1
    width: Optional[int] = 512
    height: Optional[int] = 768


class BasicSDXLJXLTaskResult(BaseModel):
    images: Optional[List[bytes]] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    seed: Optional[int] = None
    steps: Optional[int] = None
    cfg: Optional[float] = None
    sampler_name: Optional[str] = None
    scheduler: Optional[str] = None
    ckpt_name: Optional[str] = None
    err_msg: Optional[str] = None


def run(
    comfyui_client: ComfyUIClient, task: BasicSDXLJXLTask
) -> BasicSDXLJXLTaskResult:
    logging.info(
        f"BasicSDXLJXLTask run start, \
        prompt: {task.prompt}, \
        negative_prompt: {task.negative_prompt} \
        seed: {task.seed}, \
        batch_size: {task.batch_size}, \
        width: {task.width}, \
        height: {task.height}"
    )

    # check default
    task.seed = random.randint(1, 110649831182997) if task.seed == 0 else task.seed
    task.width = 1024 if task.width == 0 else task.width
    task.height = 1024 if task.height == 0 else task.height

    with open("resource/comfyui_workflows/basic_sdxl_jxl.json", "rb") as f:
        prompt_json = json.load(f)

    # prompt
    prompt_json["19"]["inputs"]["text"] = task.prompt
    # negative prompt
    prompt_json["20"]["inputs"]["text"] = task.negative_prompt
    # seed
    prompt_json["17"]["inputs"]["seed"] = task.seed
    # batch_size
    prompt_json["18"]["inputs"]["batch_size"] = task.batch_size
    # width
    prompt_json["18"]["inputs"]["width"] = task.width
    # height
    prompt_json["18"]["inputs"]["height"] = task.height

    # queue prompt
    try:
        comfyui_result = comfyui_client.queue_prompt(
            task.task_uuid, prompt_json, result_image_node_id="22"
        )
    except Exception as err:
        traceback.print_exc()
        return BasicSDXLJXLTaskResult(err_msg=f"comfyui queue prompt failed: {err}")
    logging.info(f"BasicSDXLJXLTask get images len: {len(comfyui_result)}")
    return BasicSDXLJXLTaskResult(
        images=comfyui_result,
        prompt=task.prompt,
        negative_prompt=task.negative_prompt,
        width=task.width,
        height=task.height,
        seed=task.seed,
        steps=5,
        cfg=2.0,
        sampler_name="dpmpp_sde",
        scheduler="normal",
        ckpt_name="juggernautXL_v9Rdphoto2Lightning.safetensors",
    )
