# encoding: utf-8

"""
@author: fengxiaochuang
@file: login.py
@time: 2022/2/10 10:46
"""
import os
import time

from biz.auth import Auth
from core import Task


class Login(Task):
    # 登录地址不会发生变化, 所以设置成常量
    AUTH_URI = "/v10/auth/get-access-token"

    def __init__(self, context):
        super().__init__(context)

    def run(self):
        if self.context.account is None:
            raise Exception("account is null")
        appkey = os.getenv("aicp")["appkey"]
        secretkey = os.getenv("aicp")["secretkey"]
        sys_url = os.getenv("aicp")["sysUrl"]
        res = Auth.run(sys_url, appkey, secretkey)
        access_token = res["access_token"]
        # 用户token设置
        self.context.userToken = access_token
        # 过期时间设置(提前一个小时过期)
        self.context.tokenExpireAt = time.time() + res["expires_in"] - 3600
        # 登录方式不再提供用户名方式登录了, 需要主动获取用户名
        self.context.account.username = appkey
