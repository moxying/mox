import sys

if "." not in sys.path:
    sys.path.insert(0, ".")

import asyncio
import logging

from core import initialize
from core.server import server
from core.const import *
from core.workers.gen_image_worker import GenImageWorker


if __name__ == "__main__":
    print(f"Agent start...")

    # set asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # do global init
    initialize.initialize()

    # init api server
    srv = server.Server(loop)

    # init sd gen image worker
    gen_image_worker = GenImageWorker()
    gen_image_worker.daemon = True
    gen_image_worker.start()
    srv.add_worker(WORKER_GEN_IMAGE, gen_image_worker)

    # start api server
    try:
        loop.run_until_complete(srv.run())
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt: exit....")
        # Workaround: https://github.com/encode/uvicorn/issues/1579
        srv.uvicorn_server.should_exit = True
    finally:
        srv.shutdown()
