from typing import Any, Optional, List

from pydantic import BaseModel


class CrystoolsMonitor(BaseModel):
    class Gpu(BaseModel):
        gpu_utilization: int
        vram_total: int
        vram_used: int
        vram_used_percent: float

    cpu_utilization: float
    ram_total: int
    ram_used: int
    ram_used_percent: float
    hdd_total: int
    hdd_used: int
    hdd_used_percent: float
    device_type: str
    gpus: List[Gpu]
