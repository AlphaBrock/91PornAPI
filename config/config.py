# -*- coding=utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler

# 本地调试用的代理
PROXIES = {
    "http": "http://127.0.0.1:1087",
    "https": "http://127.0.0.1:1087",
}
# 91中不通网页的视频
VIDEO_TYPE = {
    "默认": {
        "next": "watch"
    },
    "当前最热": {
        "category": "hot",
        "viewtype": "basic"
    },
    "本月最热": {
        "category": "top",
        "viewtype": "basic"
    },
    "10分钟以上": {
        "category": "long",
        "viewtype": "basic"
    },
    "本月收藏": {
        "category": "tf",
        "viewtype": "basic"
    },
    "最近加精": {
        "category": "rf",
        "viewtype": "basic"
    },
    "上月最热": {
        "category": "top",
        "m": -1,
        "viewtype": "basic"
    },
    "本月讨论": {
        "category": "md",
        "viewtype": "basic"
    },
    "高清": {
        "category": "hd",
        "viewtype": "basic"
    },
    "DB": {
        "默认": "DefaultVideoInfo",
        "当前最热": "HotVideoInfo",
        "本月最热": "TopVideoInfo",
        "10分钟以上": "LongVideoInfo",
        "本月收藏": "TfVideoInfo",
        "最近加精": "RfVideoInfo",
        "上月最热": "LastTopVideoInfo",
        "本月讨论": "MdVideoInfo",
        "高清": "HDVideoInfo"
    }
}
# 数据库路径
DB_PATH = "/Users/rizhiyi/github/91PornAPI/database/91PornVideoInfo.db"

# aes加密信息
SECRET_KEY = "1qaz0plm2wsxhgyi"
SECRET_IV = "w7sdncj09olxnbxs"

def setup_log():
    """
    日志打印方式s
    :return:
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(threadName)s] [%(levelname)s] [%(module)s.%(funcName)s] [%(filename)s:%(lineno)d] %(message)s")
    filehandler = logging.handlers.TimedRotatingFileHandler("/Users/rizhiyi/github/91PornAPI/log/91porn.log", when='d', interval=1,
                                                            backupCount=7)
    filehandler.suffix = "%Y-%m-%d_%H-%M-%S.log"
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    return logger