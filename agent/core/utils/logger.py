import logging
from logging.handlers import WatchedFileHandler

level_relations = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "crit": logging.CRITICAL,
}  # 日志级别关系映射


class Logger(object):
    def init_logger(
        logger_name,
        filename,
        level="info",
    ):
        logger = logging.getLogger(logger_name)
        format_str = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        logger.setLevel(level_relations.get(level))
        th = WatchedFileHandler(filename=filename)
        th.setFormatter(format_str)
        logger.addHandler(th)
        return logger
