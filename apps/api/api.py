# -*- coding=utf-8 -*-
from flask import Flask, jsonify
from apps.api.base.auth.token_auth import auth
from apps.api.resource.defaultvideoinfo.model import default

app = Flask(__name__)
app.register_blueprint(default)


@app.route("/")
@auth.login_required()
def hello():
    return_dic = {
        "code": 400,
        "dispMessage": "哥，这个接口没东西"
    }
    return jsonify(return_dic)


if __name__ == '__main__':
    app.run(debug=True)
