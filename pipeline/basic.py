# encoding: utf-8

"""
@author: fengxiaochuang
@file: basic.py
@time: 2022/2/9 18:30
"""
import logging
import random
import time

from biz import ASR, Login
from core import Pipeline


class Basic(Pipeline):

    def run(self):
        """
        任务执行列表
        :return:
        """
        # 初始化用户相关
        # 判断是否需要生成token
        if self.context.tokenExpireAt is None or self.context.tokenExpireAt < time.time():
            Login(self.context).run()
        # asr 任务
        ASR(self.context, ).run()
        # // asr2
