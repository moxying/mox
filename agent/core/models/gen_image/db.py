from typing import List
from typing import Dict, List, Union, Any, Optional
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean, Float, ARRAY
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.sqlite import TEXT
import uuid

from core.db.common import Base
from core.db.db import get_session
from core.const import *
from .object import *


class ImageCollectionDB(Base):
    __tablename__ = "image_collection"

    name: Mapped[String] = mapped_column(String(256), default="", unique=True)


class SDImageDB(Base):
    __tablename__ = "sd_image"

    uuid: Mapped[String] = mapped_column(String(64), index=True)
    format: Mapped[String] = mapped_column(String(512), default="")
    time_cost: Mapped[Integer] = mapped_column(Integer, default=0)
    origin_prompt: Mapped[TEXT] = mapped_column(TEXT, default="")
    image_file_deleted: Mapped[Boolean] = mapped_column(Boolean, default=False)
    task_type: Mapped[String] = mapped_column(String(64), default="")
    task_tags: Mapped[ARRAY[String]] = mapped_column(ARRAY[String(64)], default=[])
    collections: Mapped[ARRAY[String]] = mapped_column(ARRAY[String(256)], default=[])

    prompt: Mapped[TEXT] = mapped_column(TEXT, default="")
    negative_prompt: Mapped[TEXT] = mapped_column(TEXT, default="")
    width: Mapped[Integer] = mapped_column(Integer, default=512)
    height: Mapped[Integer] = mapped_column(Integer, default=768)
    seed: Mapped[Integer] = mapped_column(Integer, default=0)
    steps: Mapped[Integer] = mapped_column(Integer, default=0)
    cfg: Mapped[Float] = mapped_column(Float, default=0.0)
    sampler_name: Mapped[String] = mapped_column(String(512), default="")
    scheduler: Mapped[String] = mapped_column(String(512), default="")
    denoise: Mapped[Float] = mapped_column(Float, default=0.0)
    ckpt_name: Mapped[String] = mapped_column(String(512), default="")

    gen_image_task_id = mapped_column(Integer, ForeignKey("gen_image_task.id"))


class GenImageTaskDB(Base):

    __tablename__ = "gen_image_task"

    task_type: Mapped[String] = mapped_column(String(64), default="")
    task_tags: Mapped[ARRAY[String]] = mapped_column(ARRAY[String(64)], default=[])
    task_status: Mapped[String] = mapped_column(String(64), default="")
    err_msg: Mapped[TEXT] = mapped_column(TEXT, default="")
    origin_prompt: Mapped[TEXT] = mapped_column(TEXT, default="")

    # txt2img
    prompt: Mapped[TEXT] = mapped_column(TEXT, default="")
    negative_prompt: Mapped[TEXT] = mapped_column(TEXT, default="")
    batch_size: Mapped[Integer] = mapped_column(Integer, default=0)
    width: Mapped[Integer] = mapped_column(Integer, default=512)
    height: Mapped[Integer] = mapped_column(Integer, default=768)
    seed: Mapped[Integer] = mapped_column(Integer, default=0)
    steps: Mapped[Integer] = mapped_column(Integer, default=0)
    cfg: Mapped[Float] = mapped_column(Float, default=0.0)
    sampler_name: Mapped[String] = mapped_column(String(512), default="")
    scheduler: Mapped[String] = mapped_column(String(512), default="")
    denoise: Mapped[Float] = mapped_column(Float, default=0.0)
    ckpt_name: Mapped[String] = mapped_column(String(512), default="")

    result_images = relationship("SDImageDB")


def add_gen_image_task_db(
    task_type: str,
    task_tags: List[str],
    origin_prompt: str,
    negative_prompt: str,
    batch_size: int,
    width: int,
    height: int,
    seed: int,
    steps: int,
    cfg: float,
    sampler_name: str,
    scheduler: str,
    denoise: float,
    ckpt_name: str,
) -> int:
    with get_session() as s:
        gen_image_task = GenImageTaskDB()
        gen_image_task.task_type = task_type
        gen_image_task.task_tags = task_tags
        gen_image_task.task_status = TASK_DOING
        gen_image_task.origin_prompt = origin_prompt
        gen_image_task.negative_prompt = negative_prompt
        gen_image_task.batch_size = batch_size
        gen_image_task.width = width
        gen_image_task.height = height
        gen_image_task.seed = seed
        gen_image_task.steps = steps
        gen_image_task.cfg = cfg
        gen_image_task.sampler_name = sampler_name
        gen_image_task.scheduler = scheduler
        gen_image_task.denoise = denoise
        gen_image_task.ckpt_name = ckpt_name

        s.add(gen_image_task)
        s.commit()
        return gen_image_task.id


def get_gen_image_task_db(task_id: int) -> GenImageTask:
    with get_session() as s:
        gen_image_task = (
            s.query(GenImageTaskDB).filter(GenImageTaskDB.id == task_id).one()
        )
        return GenImageTask.model_validate(gen_image_task)


def get_gen_image_task_list_db(
    page: int, page_size: int, status: str = None
) -> tuple[List[GenImageTask], int]:
    with get_session() as s:
        limit = page_size
        offset = page_size * (page - 1)

        q = s.query(GenImageTaskDB)

        if status is not None and len(status) != 0:
            q = q.filter(GenImageTaskDB.task_status == status)

        total = q.count()
        q = q.order_by(GenImageTaskDB.created_at.desc())
        q = q.limit(limit).offset(offset)

        tasks = q.all()

        return (
            [GenImageTask.model_validate(task) for task in tasks],
            total,
        )


def add_sd_images_db(
    uuid_list: List[str],
    format: str,
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
    denoise: float,
    ckpt_name: str,
    gen_image_task_id: int,
):
    with get_session() as s:
        gen_image_task = (
            s.query(GenImageTaskDB).filter(GenImageTaskDB.id == gen_image_task_id).one()
        )
        if len(uuid_list) != gen_image_task.batch_size:
            raise Exception(
                f"image len mismatch, expect: {gen_image_task.batch_size}, got: {len(uuid_list)}"
            )
        for index in range(gen_image_task.batch_size):
            sd_image = SDImageDB(
                uuid=uuid_list[index],
                format=format,
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
                denoise=denoise,
                ckpt_name=ckpt_name,
            )
            s.add(sd_image)
            gen_image_task.result_images.append(sd_image)
        s.commit()


def get_sd_image_list_db(
    page: int,
    page_size: int,
    timestamp_filter: int = None,
    collection_filter: str = None,
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
        if collection_filter and len(collection_filter) != 0:
            q = q.filter(SDImageDB.collections.contains([collection_filter]))

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
        sd_image_db = s.query(SDImageDB).filter(SDImageDB.uuid == uuid).first()
        if sd_image_db:
            sd_image_db.image_file_deleted = True
            s.commit()
        return


def get_image_collection_list():
    with get_session() as s:
        image_collections = s.query(ImageCollectionDB).all()
        return [
            ImageCollection.model_validate(image_collection)
            for image_collection in image_collections
        ]


def add_image_collection(name: str):
    with get_session() as s:
        image_collection = ImageCollectionDB()
        image_collection.name = name
        s.add(image_collection)
        s.commit()


def delete_image_collection(name: str):
    with get_session() as s:
        s.query(ImageCollectionDB).filter(ImageCollectionDB.name == name).delete()
        s.commit()
