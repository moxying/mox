from typing import List
from typing import Dict, List, Union, Any, Optional
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.sqlite import TEXT

from core.db.common import Base
from core.db.db import get_session
from core.const import *
from .gen_image import *


class SDImageDB(Base):
    __tablename__ = "sd_image"

    uuid: Mapped[String] = mapped_column(String(64))
    task_uuid: Mapped[String] = mapped_column(String(64))
    name: Mapped[String] = mapped_column(String(512), default="")
    time_cost: Mapped[Integer] = mapped_column(Integer, default=0)
    origin_prompt: Mapped[TEXT] = mapped_column(TEXT, default="")
    prompt: Mapped[TEXT] = mapped_column(TEXT, default="")
    negative_prompt: Mapped[TEXT] = mapped_column(TEXT, default="")
    width: Mapped[Integer] = mapped_column(Integer, default=512)
    height: Mapped[Integer] = mapped_column(Integer, default=768)
    seed: Mapped[Integer] = mapped_column(Integer, default=0)
    steps: Mapped[Integer] = mapped_column(Integer, default=0)
    cfg: Mapped[Float] = mapped_column(Float, default=0)
    sampler_name: Mapped[String] = mapped_column(String(512), default="")
    scheduler: Mapped[String] = mapped_column(String(512), default="")
    ckpt_name: Mapped[String] = mapped_column(String(512), default="")


def add_sd_image_db(
    uuid: str,
    task_uuid: str,
    name: str,
    time_cost: int,
    origin_prompt: str,
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    seed: int,
    steps: int,
    cfg: float,
    sampler_name: str,
    scheduler: str,
    ckpt_name: str,
):
    with get_session() as s:
        sd_image = SDImageDB(
            uuid=uuid,
            task_uuid=task_uuid,
            name=name,
            time_cost=time_cost,
            origin_prompt=origin_prompt,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            seed=seed,
            steps=steps,
            cfg=cfg,
            sampler_name=sampler_name,
            scheduler=scheduler,
            ckpt_name=ckpt_name,
        )
        s.add(sd_image)
        s.commit()


def get_sd_image_list_db(
    page: int, page_size: int, timestamp_filter: int = None
) -> tuple[List[SDImage], int]:
    with get_session() as s:
        limit = page_size
        offset = page_size * (page - 1)

        q = s.query(SDImageDB)

        # filter
        if timestamp_filter and timestamp_filter != 0:
            q = q.filter(
                SDImageDB.created_at < datetime.fromtimestamp(timestamp_filter)
            )

        total = q.count()
        q = q.order_by(SDImageDB.created_at.desc())
        q = q.limit(limit).offset(offset)

        sd_images = q.all()

        return (
            [SDImage.model_validate(sd_image) for sd_image in sd_images],
            total,
        )


def get_sd_image_db(uuid: str) -> SDImage:
    with get_session() as s:
        sd_image_db = s.query(SDImageDB).filter(SDImageDB.uuid == uuid).first()
        if sd_image_db:
            return SDImage.model_validate(sd_image_db)
        else:
            return None


def delete_sd_image_db(uuid: str):
    with get_session() as s:
        s.query(SDImageDB).filter(SDImageDB.uuid == uuid).delete()
