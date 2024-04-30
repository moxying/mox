from core.const import *
from core.models.common import *


class UpdateConfigRequest(BaseModel):
    key: str
    value: dict
