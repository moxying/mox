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
    scheduler: Optional[str] = "normal"
    denoise: Optional[float] = 1.0
    batch_size: Optional[int] = 4
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    task_tags: Optional[dict] = {}


class Txt2imgResponse(CommonResponse):
    class Data(BaseModel):
        id: int

    data: Optional[Data] = None


class AddCollectionRequest(BaseModel):
    name: str


class DeleteCollectionRequest(BaseModel):
    name: str


class AddImagesToCollectionRequest(BaseModel):
    name: str
    image_uuid_list: List[str]


class DeleteImagesFromCollectionRequest(BaseModel):
    name: str
    image_uuid_list: List[str]


class GetImageListAsFragmentRequest(PageInfoRequest):
    timestamp_filter: Optional[int] = None
    collection_filter: Optional[str] = None


class GetImageListAsFragmentResponse(PageInfoResponse):

    class Data(PageInfoResponse.Data):
        class SDImageFragment(BaseModel):
            date: str
            list: List[SDImage]

        list: List[SDImageFragment]
        cur_total: int

    data: Optional[Data] = None
