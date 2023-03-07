# encoding: utf-8

"""
@author: fengxiaochuang
@file: Context.py
@time: 2022/2/10 10:49
"""
import time

from constants import START_AT
from core import Account


class Context(object):
    """
    单个进程上线文传递, 抽取出来常用的信息
    """
    account = None
    processNo = None
    userToken = None
    tokenExpireAt = None
    deadline = None
    meta = {}

    def __init__(self, processNo, deadline, account: Account = None, userToken=None, tokenExpireAt=None, _meta=None):
        # 进程编号
        self.processNo = processNo
        # 进程终止的时间点
        self.deadline = deadline
        # 用户账号
        self.account = account
        # 用户token
        self.userToken = userToken
        # 设置token过期时间
        self.tokenExpireAt = tokenExpireAt
        self.meta = None
        # 扩展元数据信息
        if _meta is None:
            self.meta = {}
        self.meta[START_AT] = time.time()

    def set(self, key, value):
        """
        设置元数据
        :param key:
        :param value:
        :return:
        """
        self.meta[key] = value

    def get(self, key, default=None):
        """
        获取元数据
        :param key:
        :param default: 
        :return:
        """
        if key in self.meta:
            return self.meta[key]
        else:
            return default

    def inc(self, key):
        """
        int 递增
        :param key:
        :return:
        """
        if key in self.meta:
            self.meta[key] = self.meta[key] + 1
        else:
            self.meta[key] = 1
        return self.meta[key]

    def timer(self):
        start_at = self.get(START_AT)
        return "st: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_at))) + " / ct: " \
               + str(time.time() - start_at)
