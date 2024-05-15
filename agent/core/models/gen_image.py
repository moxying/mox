from typing import Dict, List, Union, Any, Optional
from pydantic import BaseModel, validator, Field
from datetime import datetime

from core.const import *
from core.models.common import *


TOPIC_GENIMAGE_START = "genimage_start"
TOPIC_GENIMAGE_PROGRESS = "genimage_progress"
TOPIC_GENIMAGE_END = "genimage_end"
TOPIC_GENIMAGE_FAILED = "genimage_failed"


class GenImageEventData(BaseModel):
    task_uuid: str
    progress_tip: Optional[str] = None
    progress_value: Optional[int] = None
    progress_value_max: Optional[int] = None
    images: Optional[List[str]] = None
    err_msg: Optional[str] = None


class GenImageEvent(WSEvent):
    data: GenImageEventData


class ImageCollection(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: str


class Txt2imgRequest(BaseModel):
    origin_prompt: str
    ckpt_name: str
    negative_prompt: Optional[str] = ""
    seed: Optional[int] = 0
    steps: Optional[int] = 5
    cfg: Optional[float] = 2.0
    sampler_name: Optional[str] = "dpmpp_sde"
    scheduler: Optional[str] = "scheduler"
    denoise: Optional[float] = 1.0
    batch_size: Optional[int] = 4
    width: Optional[int] = 1024
    height: Optional[int] = 1024


class Txt2imgResponseData(BaseModel):
    task_uuid: str


class Txt2imgResponse(CommonResponse):
    data: Optional[Txt2imgResponseData] = None


class SDImage(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: str
    format: str
    time_cost: int
    origin_prompt: str
    image_file_deleted: bool
    task_type: str
    task_tags: Optional[List[str]] = None

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
    task_uuid: str
    task_type: str
    task_tags: Optional[List[str]] = None
    task_status: str
    err_msg: Optional[str] = None
    origin_prompt: str
    batch_size: int

    result_images: Optional[List[SDImage]] = None


class GenImageResultRequest(BaseModel):
    task_uuid: str


class GenImageResultResponse(CommonResponse):
    data: List[SDImage]


class GetImageListRequest(PageInfoRequest):
    pass


class GetImageListResponseData(PageInfoResponseData):
    list: List[SDImage]


class GetImageListResponse(PageInfoResponse):
    data: Optional[GetImageListResponseData] = None


class GetImageListAsFragmentRequest(PageInfoRequest):
    timestamp_filter: Optional[int] = None


class SDImageFragment(BaseModel):
    date: str
    list: List[SDImage]


class GetImageListAsFragmentResponseData(PageInfoResponseData):
    list: List[SDImageFragment]
    cur_total: int


class GetImageListAsFragmentResponse(PageInfoResponse):
    data: Optional[GetImageListAsFragmentResponseData] = None


class ComfyUIEventData(BaseModel):
    task_uuid: str
    progress_name: str
    progress_value_max: int
    progress_tip: Optional[str] = None
    node_id: Optional[str] = None
    cached_nodes: Optional[List[str]] = None
    node_progress_value: Optional[int] = None
    node_progress_value_max: Optional[int] = None
    err_msg: Optional[str] = None


class GetRandomPromptResponse(CommonResponse):
    data: Optional[str]
