# -*- coding=utf-8 -*-
"""
此处用于生成相应的API key使用，其他地方不会做调用处理
"""
import base64
import hashlib
import os
import sys
import pyaes
import sqlite3
from config.config import SECRET_KEY, SECRET_IV, DB_PATH


def aes_encryption(user_name, token):
    """
    加密生成信息
    :param user_name:
    :return:
    """
    user_info = """%s:%s""" % (user_name, token)
    encrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(SECRET_KEY.encode(), SECRET_IV.encode()))
    _passwd = encrypter.feed(user_info) + encrypter.feed()
    return base64.b64encode(_passwd)


def insert_sqlite(user_name, token, auth_token):
    """
    插入生成的鉴权码
    :param user_name:
    :param token:
    :param auth_token:
    :return:
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    sql_cmd = "INSERT INTO Auth (user, token, auth_token) VALUES ('{}','{}', '{}');".format(user_name, token, auth_token)
    cur.execute(sql_cmd)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # 特别注意，username不允许重复，否则鉴权将不可用
    user_name = sys.argv[0]
    token = hashlib.sha1(os.urandom(24)).hexdigest()
    # user_name = "chenfei"
    # token = "b8f16edcc0f339b85faae57c77aa4b76"
    auth_token = aes_encryption(user_name, token)
    insert_sqlite(user_name, token, bytes.decode(auth_token))
    print('your auth_token is:{}'.format(bytes.decode(auth_token)))
