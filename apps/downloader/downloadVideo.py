# -*- coding=utf-8 -*-
"""
多线程视频下载器
"""
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock
from time import time
import random
from fake_useragent import UserAgent


import requests
from ipaddress import IPv4Address
from config.config import PROXIES, setup_log

logger = setup_log()
lock = Lock()
ua = UserAgent()


class Downloader(object):
    def __init__(self, videoUrl, threadNum, videoFile):
        self.url = videoUrl
        self.num = threadNum
        self.name = videoFile
        HEADERS = {"User-Agent": ua.random, "Host": "91porn.com", "referer": self.url,
                   "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))}
        r = requests.request("HEAD", self.url, headers=HEADERS, proxies=PROXIES)
        self.size = int(r.headers['Content-Length'])

    def down(self, start, end):
        HEADERS = {"User-Agent": ua.random, "Host": "91porn.com", "referer": self.url,
                   "X-Forwarded-For": str(IPv4Address(random.getrandbits(32))),
                   'Range': "bytes={}-{}".format(start, end)}
        # stream = True 下载的数据不会保存在内存中
        r = requests.request("GET", self.url, headers=HEADERS, proxies=PROXIES)
        # 写入文件对应位置,加入文件锁
        lock.acquire()
        with open(self.name, "rb+") as fp:
            fp.seek(start)
            fp.write(r.content)
            lock.release()
            # 释放锁

    def run(self):
        startTime = time()
        # 创建一个和要下载文件一样大小的文件
        fp = open(self.name, "wb")
        fp.truncate(self.size)
        fp.close()
        # 启动多线程写文件
        part = self.size // self.num
        pool = ThreadPoolExecutor(max_workers=self.num)
        futures = []
        for i in range(self.num):
            start = part * i
            if i == self.num - 1:
                end = self.size
            else:
                end = start + part - 1
            futures.append(pool.submit(self.down, start, end))
        wait(futures)
        endTime = time()
        logger.info("{}下载完成,文件大小: {:.2f}MB,用时: {:.2f}秒, 平均速度: {:.2f}MB/s.".format(self.name, self.size / 1024 / 1024,
                                                                                  endTime - startTime,
                                                                                  self.size / 1024 / 1024 / (
                                                                                              endTime - startTime)))
