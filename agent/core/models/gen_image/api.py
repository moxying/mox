from typing import Dict, List, Union, Any, Optional
from pydantic import BaseModel, validator, Field
from datetime import datetime

from core.const import *
from core.models.common import *

from .object import *


class GetRandomPromptResponse(CommonResponse):
    data: Optional[str]


class GetImageTasksRequest(PageInfoRequest):
    pass


class GetImageTasksResponse(PageInfoResponse):
    pass


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
    task_tags: Optional[List[str]] = None


class Txt2imgResponse(CommonResponse):
    class Data(BaseModel):
        id: int

    data: Optional[Data] = None


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
