import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import os

from .common import Base
from core.config import ConfigMgr


def init_orm(sqlite_file: str):
    if len(sqlite_file) == 0:
        raise Exception("sqlite_file is empty")
    os.makedirs(os.path.dirname(sqlite_file), exist_ok=True)
    global new_session
    # 初始化数据库连接
    db_conf = ConfigMgr().get_conf("db")
    engine = create_engine(
        f"sqlite:///{sqlite_file}",
        echo=db_conf[
            "debug"
        ],  # 程序运行时反馈执行过程中的关键对象，包括ORM构建的sql语句
        future=True,  # 使用 SQLAlchemy 2.0 API，向后兼容
        max_overflow=0,  # 超过连接池大小外最多创建的连接
        pool_size=5,  # 连接池的大小默认为 5 个，设置为 0 时表示连接无限制
        pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
        pool_recycle=3600,  # 设置时间以限制数据库自动断开
    )
    # 创建表到数据库表中
    Base.metadata.create_all(engine)
    new_session = sessionmaker(engine)

    logging.info(f"init orm done, using sqlite db: {sqlite_file}")


@contextlib.contextmanager
def get_session():
    global new_session
    s = new_session()
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()
