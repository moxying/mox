import threading
import queue
import os
import logging

from core.config import ConfigMgr


class StorageMgr:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_instance()
        return cls._instance

    def _init_instance(self):
        self._event_queue = queue.Queue()
        self.output_file_dir = ConfigMgr().get_conf("storage")["output_file_dir"]
        os.makedirs(self.output_file_dir, exist_ok=True)

    def save_image(self, filename: str, image: bytes):
        filepath = f"{self.output_file_dir}/{filename}"
        with open(filepath, "wb") as f:
            f.write(image)

    def delete_image(self, filename: str):
        filepath = f"{self.output_file_dir}/{filename}"
        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            logging.warn(f"try to delete a none exist file: {filepath}")
