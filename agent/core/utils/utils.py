from fastapi import UploadFile
import shutil
from pathlib import Path


def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()


def get_value_index_in_enum(value, enum_class):
    for index, item in enumerate(enum_class):
        if item.value == value:
            return index
    return None
