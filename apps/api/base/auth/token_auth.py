# -*- coding=utf-8 -*-
"""
token鉴权复杂了点，相当于脱了裤子放屁，不过那又如何呢，不显摆下不行啊
"""
import base64
from functools import wraps

import pyaes
from flask import request, make_response, jsonify
from werkzeug.datastructures import Authorization
from config.config import setup_log, SECRET_KEY, SECRET_IV
from apps.api.base.db.pool import pool

logger = setup_log()


def aes_decryption(token):
    """
    虽然不知道是否有必要对token加密混淆，但为了装逼，还是加上去吧
    :param token:
    :return:
    """
    try:
        data_string = base64.b64decode(token)
        decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(SECRET_KEY.encode(), iv=SECRET_IV.encode()))
        result = decrypter.feed(data_string) + decrypter.feed()
        return bytes.decode(result).split(':')[0], bytes.decode(result).split(':')[1]
    except Exception as e:
        logger.error("解密token异常, {}".format(e))
        return None, None


def query_sqlite(user_name):
    """
    从数据库查询对应用户的token
    :param user_name:
    :return:
    """
    try:
        conn = pool.get()
        sql = """select token from Auth where user='%s'""" % user_name
        with conn:
            for i in conn.execute(sql):
                return i[0]
    except Exception as e:
        logger.exception("sql执行失败，抛出异常:{}".format(e))
        return None


class HTTPAuth(object):
    def __init__(self, scheme=None, realm=None, header=None):
        self.scheme = scheme
        self.realm = realm or "Authentication Required"
        self.header = header
        self.auth_error_callback = None

        def default_auth_error(status):
            return_dic = {
                "code": 401,
                "dispMessage": "哥，没有授权不能使用接口"
            }
            return jsonify(return_dic), status

        self.error_handler(default_auth_error)

    def error_handler(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            res = f(*args, **kwargs)
            res = make_response(res)
            if res.status_code == 200:
                res.status_code = 401
            return res

        self.auth_error_callback = decorated
        return decorated

    def authenticate_header(self):
        return '{0} realm="{1}"'.format(self.scheme, self.realm)

    def get_auth(self):
        auth = None
        if self.header is None or self.header == 'Authorization':
            auth = request.authorization
            if auth is None and 'Authorization' in request.headers:
                try:
                    auth_type, token = request.headers['Authorization'].split(
                        None, 1)
                    auth = Authorization(auth_type, {'token': token})
                except (ValueError, KeyError):
                    pass
        elif self.header in request.headers:
            auth = Authorization(self.scheme,
                                 {'token': request.headers[self.header]})
        if auth is not None and auth.type.lower() != self.scheme.lower():
            auth = None
        return auth

    def login_required(self, f=None):
        def login_required_internal(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                auth = self.get_auth()
                if request.method != 'OPTIONS':
                    status = None
                    if auth is None:
                        status = 401
                    else:
                        user_name, header_token = aes_decryption(dict(auth).get('token'))
                        if user_name is None:
                            status = 401
                        else:
                            sql_token = query_sqlite(user_name)
                            if sql_token != header_token:
                                status = 401
                    if status:
                        try:
                            return self.auth_error_callback(status)
                        except TypeError:
                            return self.auth_error_callback()
                return f(*args, **kwargs)

            return decorated

        if f:
            return login_required_internal(f)
        return login_required_internal


class HTTPTokenAuth(HTTPAuth):
    def __init__(self, scheme='Bearer', realm=None, header=None):
        super(HTTPTokenAuth, self).__init__(scheme, realm, header)

        self.verify_token_callback = None

    def verify_token(self, f):
        self.verify_token_callback = f
        return f

    def authenticate(self, auth):
        if auth:
            token = auth['token']
        else:
            token = ""
        if self.verify_token_callback:
            return self.verify_token_callback(token)


auth = HTTPTokenAuth()
