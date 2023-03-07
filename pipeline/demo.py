# encoding: utf-8

"""
@author: fengxiaochuang
@file: basic.py
@time: 2022/2/9 18:30
"""
import logging
import random

from core import Pipeline


class Demo(Pipeline):

    def run(self):
        times = self.get("run_times", 0)
        logging.info("i am running, run times %d", times)
        abc = self.get("abc")
        if abc is None:
            self.set("abc", random.random())
