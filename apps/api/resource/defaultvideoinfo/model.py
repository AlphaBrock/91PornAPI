# -*- coding=utf-8 -*-
from apps.api.base.auth.token_auth import auth
from flask import Blueprint, request, make_response, jsonify

default = Blueprint('default', __name__)


@default.route("/api/v1/default", methods=['GET'])
@auth.login_required
def index():
    return_dict = {
        "code": 0,
        "display_message": "",
        "tiktok_info": {
            "title": "",
            "wm_url": "",
            "mp3_url": "",
            "photo_url": ""
        }
    }
    data = request.args.to_dict()
    print(data)
    if len(data) == 0:
        return_dict['code'] = 403
        return_dict['display_message'] = "哥，要带参数才能查询到结果"
        return make_response(jsonify(return_dict), 200)
