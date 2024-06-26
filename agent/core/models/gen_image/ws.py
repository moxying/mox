from typing import Dict, List, Union, Any, Optional
from pydantic import BaseModel, validator, Field
from datetime import datetime

from core.const import *
from core.models.common import *


TOPIC_GENIMAGE_PROGRESS = "genimage_progress"
TOPIC_GENIMAGE_END = "genimage_end"
TOPIC_GENIMAGE_FAILED = "genimage_failed"


class GenImageEvent(WSEvent):
    class Data(BaseModel):
        task_id: int

        # progress
        progress_name: Optional[str] = None
        progress_tip: Optional[str] = None
        progress_value: Optional[int] = None
        progress_value_max: Optional[int] = None

        # result
        images: Optional[List[str]] = None
        err_msg: Optional[str] = None

    data: Data
