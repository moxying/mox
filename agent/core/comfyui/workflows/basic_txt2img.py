import logging
from typing import Optional, List
from pydantic import BaseModel
import json
import traceback
import random

from core.comfyui.comfyui_client import ComfyUIClient


class BasicTxt2imgTask(BaseModel):
    task_id: int
    prompt: str

    # optional
    ckpt_name: Optional[str] = ""
    negative_prompt: Optional[str] = ""
    seed: Optional[int] = 0
    steps: Optional[int] = 5
    cfg: Optional[float] = 2.0
    sampler_name: Optional[str] = "dpmpp_sde"
    scheduler: Optional[str] = "scheduler"
    denoise: Optional[float] = 1.0
    batch_size: int = 4
    width: Optional[int] = 1024
    height: Optional[int] = 1024


class BasicTxt2imgTaskResult(BasicTxt2imgTask):
    images: Optional[List[bytes]] = None
    err_msg: Optional[str] = None


def run(
    comfyui_client: ComfyUIClient, task: BasicTxt2imgTask
) -> BasicTxt2imgTaskResult:
    logging.info(
        f"BasicTxt2imgTask run start, \
        task_id: {task.task_id} \
        prompt: {task.prompt}, \
        ckpt_name: {task.ckpt_name}, \
        negative_prompt: {task.negative_prompt} \
        seed: {task.seed}, \
        steps: {task.steps}, \
        cfg: {task.cfg}, \
        sampler_name: {task.sampler_name}, \
        scheduler: {task.scheduler}, \
        denoise: {task.denoise}, \
        batch_size: {task.batch_size}, \
        width: {task.width}, \
        height: {task.height}"
    )

    # check default
    task.ckpt_name = (
        "juggernautXL_v9Rdphoto2Lightning.safetensors"
        if task.ckpt_name == ""
        else task.ckpt_name
    )
    task.seed = random.randint(1, 110649831182997) if task.seed == 0 else task.seed
    task.steps = 5 if task.steps == 0 else task.steps
    task.cfg = 2.0 if task.cfg == 0.0 else task.cfg
    task.sampler_name = "dpmpp_sde" if task.sampler_name == "" else task.sampler_name
    task.scheduler = "normal" if task.scheduler == "" else task.scheduler
    task.denoise = 1.0 if task.denoise == 0.0 else task.denoise
    task.batch_size = 4 if task.batch_size == 0 else task.batch_size
    task.width = 1024 if task.width == 0 else task.width
    task.height = 1024 if task.height == 0 else task.height

    # workflow
    with open("resource/comfyui_workflows/basic_txt2img.json", "rb") as f:
        prompt_json = json.load(f)

    # ckpt_name
    prompt_json["4"]["inputs"]["ckpt_name"] = task.ckpt_name
    # prompt
    prompt_json["6"]["inputs"]["text"] = task.prompt
    # negative prompt
    prompt_json["7"]["inputs"]["text"] = task.negative_prompt
    # batch_size
    prompt_json["5"]["inputs"]["batch_size"] = task.batch_size
    # width
    prompt_json["5"]["inputs"]["width"] = task.width
    # height
    prompt_json["5"]["inputs"]["height"] = task.height
    # KSampler
    prompt_json["3"]["inputs"]["seed"] = task.seed
    prompt_json["3"]["inputs"]["steps"] = task.steps
    prompt_json["3"]["inputs"]["cfg"] = task.cfg
    prompt_json["3"]["inputs"]["sampler_name"] = task.sampler_name
    prompt_json["3"]["inputs"]["scheduler"] = task.scheduler
    prompt_json["3"]["inputs"]["denoise"] = task.denoise

    # queue prompt
    try:
        comfyui_result = comfyui_client.queue_prompt(
            task.task_uuid, prompt_json, result_image_node_id="10"
        )
    except Exception as err:
        traceback.print_exc()
        return BasicTxt2imgTaskResult(err_msg=f"comfyui queue prompt failed: {err}")
    logging.info(f"BasicTxt2imgTask get images len: {len(comfyui_result)}")
    return BasicTxt2imgTaskResult(
        images=comfyui_result,
        task_id=task.task_id,
        prompt=task.prompt,
        ckpt_name=task.ckpt_name,
        negative_prompt=task.negative_prompt,
        seed=task.seed,
        steps=task.steps,
        cfg=task.cfg,
        sampler_name=task.sampler_name,
        scheduler=task.scheduler,
        denoise=task.denoise,
        batch_size=task.batch_size,
        width=task.width,
        height=task.height,
    )
