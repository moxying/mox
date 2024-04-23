import threading
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import gc
import time
import logging

from core.config import ConfigMgr


class Translator:

    _instance = None
    _lock = threading.Lock()
    _model_lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_instance()
        return cls._instance

    def _init_instance(self):
        self.model = None
        self.tokenizer = None

    def _unload_model(self):
        with self._lock:
            del self.model
            del self.tokenizer
            gc.collect()
            self.model = None
            self.tokenizer = None

    @staticmethod
    def detect_language(input_str):
        # 统计中文和英文字符的数量
        count_cn = count_en = 0
        for char in input_str:
            if "\u4e00" <= char <= "\u9fff":
                count_cn += 1
            elif char.isalpha():
                count_en += 1

        # 根据统计的字符数量判断主要语言
        if count_cn > count_en:
            return "zh-cn"
        elif count_en > count_cn:
            return "en"
        else:
            return "unknow"

    def run(self, en_text: str):
        if not en_text or len(en_text) == 0:
            return ""
        if Translator.detect_language(en_text) != "zh-cn":
            return en_text
        with self._lock:
            start_t = time.time()
            if not self.model:
                debug = ConfigMgr().get_conf("translator")["debug"]
                if debug:
                    pretrained_model_name_or_path = "models/translation/opus-mt-zh-en"
                else:
                    raise NotImplementedError()
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    pretrained_model_name_or_path=pretrained_model_name_or_path,
                    local_files_only=True,
                )
                device = ConfigMgr().get_conf("translator")["device"]
                self.model.to(device)
                self.tokenizer = AutoTokenizer.from_pretrained(
                    pretrained_model_name_or_path=pretrained_model_name_or_path,
                    local_files_only=True,
                )
                logging.debug(f"[Translator] model load cost {time.time()-start_t}s")

                delay = ConfigMgr().get_conf("translator")["unload_model_seconds"]
                threading.Timer(delay, self._unload_model)
            with torch.no_grad():
                encoded = self.tokenizer([en_text], return_tensors="pt", padding=True)
                encoded.to(self.model.device)
                sequences = self.model.generate(**encoded)
                res = self.tokenizer.batch_decode(sequences, skip_special_tokens=True)
                logging.debug(f"[Translator] trans cost {time.time()-start_t}s")
                return res[0]
