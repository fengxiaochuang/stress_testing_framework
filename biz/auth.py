# encoding: utf-8

"""
@author: fengxiaochuang
@file: auth.py
@time: 2022/2/10 10:46
"""
import base64
import json

from core import Task


class Auth(object):
    # 登录地址不会发生变化, 所以设置成常量
    AUTH_URI = "/v10/auth/get-access-token"

    @staticmethod
    def run(sys_url: str, appkey: str, secretkey: str):
        params = {
            "appkey": appkey,
        }
        basic_byte = str(appkey + ":" + secretkey).encode("utf8")
        headers = {
            "Authorization": "Basic " + base64.b64encode(basic_byte).decode("utf8")
        }
        # 从环境边变量中获取信息
        auth_url = sys_url + Auth.AUTH_URI
        response = Task.get(auth_url, params=params, headers=headers)
        res = json.loads(response.text)
        return res
