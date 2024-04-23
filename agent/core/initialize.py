import logging

from core.config import ConfigMgr
from core.const import *
from core.db.db import init_orm
from core.logger.logger import init_logger


def initialize():

    # init logger
    init_logger()

    # init db
    init_orm(ConfigMgr().get_conf("db")["sqlite_file"])

    logging.info(f"basic initialize done")
