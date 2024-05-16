from typing import Dict, List, Union, Any, Optional
from pydantic import BaseModel, validator, Field
from datetime import datetime
from enum import Enum

from core.const import *
from core.models.common import *


class TaskType(Enum):
    TXT2IMG = "txt2img"


class ImageCollection(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    name: str


class SDImage(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    uuid: str
    format: str
    origin_prompt: str
    image_file_deleted: bool
    task_type: str
    task_tags: Optional[List[str]] = None
    collections: Optional[List[str]] = None

    prompt: str
    negative_prompt: Optional[str] = None
    width: Optional[int] = 0
    height: Optional[int] = 0
    seed: Optional[int] = 0
    steps: Optional[int] = 0
    cfg: Optional[float] = 0.0
    sampler_name: Optional[str] = None
    scheduler: Optional[str] = None
    denoise: Optional[float] = 0.0
    ckpt_name: Optional[str] = None

    class Config:
        from_attributes = True


class GenImageTask(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    task_type: str
    task_tags: Optional[dict] = None
    task_status: str
    err_msg: Optional[str] = None
    origin_prompt: str

    prompt: str
    negative_prompt: Optional[str] = None
    batch_size: int
    width: Optional[int] = 0
    height: Optional[int] = 0
    seed: Optional[int] = 0
    steps: Optional[int] = 0
    cfg: Optional[float] = 0.0
    sampler_name: Optional[str] = None
    scheduler: Optional[str] = None
    denoise: Optional[float] = 0.0
    ckpt_name: Optional[str] = None

    result_images: Optional[List[SDImage]] = None


class GenImageWorkerTask(BaseModel):
    task_id: int
    task_type: TaskType
