import logging
from logging.handlers import MemoryHandler, QueueHandler, QueueListener
from logging import StreamHandler
import sys
from queue import SimpleQueue


from core.server.event import EventDispatcher
from core.models.common import *
from core.const import *

LOGGING_FORMAT_MAIN = "%(asctime)s - Agent - %(levelname)s - %(message)s"
LOGGING_FORMAT_DEBUG = "%(asctime)s - Agent - %(levelname)s - %(name)s - %(message)s"


class CustomMemoryHandler(MemoryHandler):
    def flush(self):
        self.acquire()
        try:
            for record in self.buffer:
                log = self.format(record)
                EventDispatcher().dispatch_event(
                    EVENT_TYPE_WS,
                    WSEvent(topic=TOPIC_COMMON_LOG, data=CommonLogEventData(log=log)),
                )
            self.buffer.clear()
        finally:
            self.release()


def init_logger():
    memory_handler = CustomMemoryHandler(
        capacity=1
    )  # capacity=1 日志立马刷到ws的queue内
    stream_handler = StreamHandler(stream=sys.stdout)

    # FIXME：这边不用queue其实应该也行，因为ws那边还有个queue
    queue = SimpleQueue()
    queue_handler = QueueHandler(queue)
    listener = QueueListener(
        queue,
        memory_handler,
        stream_handler,
    )
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOGGING_FORMAT_MAIN,
        # force=True,
        handlers=[queue_handler],
    )
    # enable debug logging for the asyncio module
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    listener.start()  # FIXME：stop是必须的？
    logging.info("init logger done")
