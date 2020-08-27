# -*- coding=utf-8 -*-
import base64
import datetime
import random
import re
import threading
from ipaddress import IPv4Address
from fake_useragent import UserAgent

import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from config.config import setup_log, VIDEO_TYPE, DB_PATH
from apps.api.base.db import init_db

logger = setup_log()
ua = UserAgent()


def calculate_video_upload_time(time_info):
    """
    转换下视频上传时间
    :param time_info:
    :return:
    """
    global videoTime
    num = re.compile('[0-9]+').search(time_info).group(0)
    if "秒" in time_info:
        videoTime = datetime.datetime.now() - datetime.timedelta(seconds=int(num))
    if "分钟" in time_info:
        videoTime = datetime.datetime.now() - datetime.timedelta(minutes=int(num))
    elif "小时" in time_info:
        videoTime = datetime.datetime.now() - datetime.timedelta(hours=int(num))
    elif "天" in time_info:
        videoTime = datetime.datetime.now() - datetime.timedelta(days=int(num))
    elif "月" in time_info:
        videoTime = datetime.datetime.now() - relativedelta(months=int(num))
    elif "年" in time_info:
        videoTime = datetime.datetime.now() - relativedelta(years=int(num))
    return videoTime.strftime('%Y-%m-%d %H:%M:%S')


def calculate_video_time(vide_time):
    """
    转换下视频时长
    :param vide_time:
    :return:
    """
    pass


def download_html(url, params):
    """
    下载网页
    :param url:
    :return:
    """
    HEADERS = {
        "User-Agent": ua.random,
        "Host": "91porn.com",
        "referer": url,
        "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
    }
    print(HEADERS)
    payload = {
        "session_language": "cn_CN"
    }
    # response = requests.request("POST", url, headers=HEADERS, params=params, data=payload, proxies=PROXIES)
    response = requests.request("POST", url, headers=HEADERS, params=params, data=payload)
    return response.text


def get_page_num(url, video_type):
    """
    获取网页页数
    :param video_type:
    :return:
    """
    try:
        html = download_html(url, video_type)
        v = BeautifulSoup(html, "lxml").find('div', class_="login_register_header")
        video_num = v.h4.font.string.split("的")[1].replace(' ', '')
        a = int(video_num) % 24
        if a != 0:
            page_num = int(video_num) // 24 + 1
        else:
            page_num = int(video_num) // 24
        print(("获取:{}, 页数成功，视频数:{}, 页数:{}".format(video_type, video_num, page_num)))
        logger.info("获取:{}, 页数成功，视频数:{}, 页数:{}".format(video_type, video_num, page_num))
        return page_num
    except Exception as e:
        print(("获取:{}, 页数失败，抛出异常:{}".format(video_type, e)))
        logger.exception("获取:{}, 页数失败，抛出异常:{}".format(video_type, e))
        return 0


def read_video_html_url(url, video_type, page_num):
    """
    获取视频页地址信息
    :return:
    """
    video_type['page'] = page_num
    html = download_html(url, video_type)
    try:
        video_info = BeautifulSoup(html, 'lxml').find_all('div', class_='well well-sm videos-text-align')
        video_infos = []
        for info in video_info:
            video_html_url = info.a['href']
            video_pic = info.a.div.img['src']
            video_duration = info.a.div.span.string
            video_title = info.find(class_='video-title title-truncate m-t-5').string
            info = str(info)
            add_time = re.compile('<span class="info">添加时间:</span>\s+([^<]+)').search(info)
            author = re.compile('<span class="info">作者:</span>\s+([^<]+)').search(info)
            check = re.compile('<span class="info">查看:</span>\s+([0-9]+)').search(info)
            video_infos.append([video_title, video_duration, video_html_url, video_pic,
                                calculate_video_upload_time(add_time.group(1).replace(" ", "")),
                                author.group(1).replace(" ", ""), check.group(1).replace(" ", "")])
        return video_infos
    except Exception as e:
        logger.exception("获取视频网页地址出错，抛出异常:{}".format(e))
        return None


def decrypted(input, key):
    """
    91porn的js解密代码
    function strencode(input, key) {
        input = atob(input);
        len = key.length;
        code = '';
        for (i = 0; i < input.length; i++) {
            k = i % len;
            code += String.fromCharCode(input.charCodeAt(i) ^ key.charCodeAt(k));
        }
        return code;
        return atob(code);
    }
    :return:
    """
    _input = base64.b64decode(input)
    _len = len(key)
    code = ''
    for i in range(len(_input)):
        k = i % _len
        code += chr((_input[i] ^ key[k]) & 0xffff)
    return base64.b64decode(code.encode())


def read_video_url(video_title, video_pic, video_html_url, video_duration, author, check, uptime):
    """
    获取视频地址
    :param video_html_urls:
    :return:
    """
    try:
        params = {}
        html = download_html(video_html_url, params)
        # video_encode_url = re.compile(r'document.write\(strencode\(([^)]+)').search(html)
        video_encode_url = BeautifulSoup(html, 'lxml').find('source')
        if video_encode_url is not None:
            # encrypted_url = video_encode_url.group(1).replace('"', '').split(',')
            # source = decrypted(encrypted_url[0].encode(), encrypted_url[1].encode())
            # src = BeautifulSoup(source, 'lxml').find_all('source')[0]['src']
            src = video_encode_url['src']
            VIDEO_INFO.append((video_title, video_html_url, src, video_duration, video_pic, author, check, uptime))
            logger.info(
                "视频名称:{}, 视频图片:{}, 视频网页地址:{}, 视频地址:{}, 视频时长:{}, 作者:{}, 观看数:{}, 上传时间:{}".format(video_title, video_pic,
                                                                                               video_html_url, src,
                                                                                               video_duration, author,
                                                                                               check, uptime))
        else:
            logger.warning("视频链接: {}, 加密信息获取为空".format(video_html_url))
    except Exception as e:
        logger.exception("获取视频链接出错，抛出异常:{}".format(e))


def multithread_read_video_url(video_infos):
    """
    加个多线程获取视频链接吧，后续看看用异步处理如何
    :param video_infos:
    :return:
    """
    threads = []
    for i in range(len(video_infos)):
        video_title = video_infos[i][0]
        video_duration = video_infos[i][1]
        video_html_url = video_infos[i][2]
        video_pic = video_infos[i][3]
        uptime = video_infos[i][4]
        author = video_infos[i][5]
        check = video_infos[i][6]
        t = threading.Thread(target=read_video_url,
                             args=(video_title, video_pic, video_html_url, video_duration, author, check, uptime))
        t.setDaemon(True)
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()


if __name__ == '__main__':

    url = "http://91porn.com/v.php"
    for _type in VIDEO_TYPE:
        video_type = VIDEO_TYPE.get(_type)
        DB = init_db.Database(DB_PATH, VIDEO_TYPE.get('DB').get(_type))
        page_num = get_page_num(url, video_type)
        if page_num == 0:
            page_num = 100

        flag = 1
        while flag <= page_num:
            VIDEO_INFO = []
            video_infos = read_video_html_url(url, video_type, flag)
            if video_infos is None:
                pass
            else:
                multithread_read_video_url(video_infos)
                DB.insert_video_info(VIDEO_INFO)
            flag += 1
        DB.close()
