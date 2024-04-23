import yaml
import logging
from yaml.loader import SafeLoader
import threading
import os

from core.const import *


class ConfigMgr:

    _instance = None
    _lock = threading.Lock()
    _conf = {}

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_instance()
        return cls._instance

    def _init_instance(self):
        config_file = CONFIG_FILENAME
        use_default = False
        if not os.path.exists(config_file):
            logging.info(
                f"{config_file} not exist, use default {DEFAULT_CONFIG_FILENAME}"
            )
            use_default = True
            config_file = DEFAULT_CONFIG_FILENAME
        with open(config_file) as f:
            config = yaml.load(f, Loader=SafeLoader)
        self._conf.update(config)
        if use_default:
            with open(CONFIG_FILENAME, "w") as f:
                yaml.dump(self._conf, f)
        logging.info(f"load_config done: {self._conf} ")

    def conf(self):
        with self._lock:
            return self._conf

    def get_conf(self, key: str):
        with self._lock:
            if key in self._conf:
                return self._conf[key]
            else:
                return {}

    def update_conf(self, key: str, value: any):
        with self._lock:
            if key not in self._conf:
                return
            self._conf[key] = value
            with open(CONFIG_FILENAME, "w") as f:
                yaml.dump(self._conf, f)
