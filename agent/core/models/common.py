from typing import Any, Optional
from pydantic import BaseModel


class CommonResponse(BaseModel):
    code: int = 0
    msg: Optional[str] = None
    data: Optional[Any] = None


class PageInfoRequest(BaseModel):
    page: int
    page_size: int


class PageInfoResponseData(BaseModel):
    page: int
    page_size: int
    total: int
    list: Optional[Any] = []


class PageInfoResponse(CommonResponse):
    data: Optional[PageInfoResponseData] = None


#
# Agent WS
#

TOPIC_COMMON_STATUS = "status"
TOPIC_COMMON_LOG = "log"


class CommonStatusEventData(BaseModel):
    status: str


class CommonLogEventData(BaseModel):
    log: str


class WSEvent(BaseModel):
    topic: str
    data: Optional[Any] = None
