# encoding: utf-8

"""
@author: fengxiaochuang
@file: Pipeline.py
@time: 2022/2/11 9:48
"""
import logging
import os
import time
import traceback

import constants
from core import Context
from abc import ABCMeta, abstractmethod


class Pipeline(metaclass=ABCMeta):
    """
    抽象Pipeline类方法
    """

    def __init__(self, context: Context, contexts: list, delay: float = 0.01):
        """
        任务执行器
        :param context: 任务传递上下文
        :param delay: 一轮任务完成之后延迟多长时间启动下一次
        :return:
        """
        self.context = context
        log_dir = os.getenv("log_dir")
        log_file_name = os.path.join(log_dir, context.processNo + ".log")
        logging.basicConfig(
            format="%(asctime)s.%(msecs)03d [" + context.processNo + "] [%(process)d-%(thread)d] %(levelname)s %(message)s",
            level=logging.INFO,
            datefmt=constants.DATE_FORMAT,
            handlers=[
                logging.FileHandler(log_file_name, encoding="utf-8", mode="a+"),
                logging.StreamHandler()
            ],
        )
        # 初始化上下文
        logging.info("pipeline init successful")
        while True:
            now = time.time()
            if now >= context.deadline:
                break
            try:
                # 执行任务列表
                self.run()
            except Exception as _e:
                logging.error(
                    "[" + context.processNo + "] runtime error: when run with error: " + traceback.format_exc())
            # 执行间隔时间
            time.sleep(delay)
            self.context.inc(constants.TASK_RUN_COUNTS)
            logging.info(
                "============ tasks [%s] loop counts [%d], current loop cost [%f] ============",
                self.__class__, self.context.get(constants.TASK_RUN_COUNTS), time.time() - now)
        contexts.append(self.context)
        logging.info("pipeline run finished")

    @staticmethod
    def factory(clazz: classmethod, context: Context, contexts: list, *args):
        """
        静态工厂方法，根据clazz生成Pipeline的子类, 并调用对应的run方法
        :param clazz:
        :param context:
        :param contexts: 环境参数收集器
        :param args:
        :return:
        """
        return clazz(context, contexts, *args)

    @abstractmethod
    def run(self):
        """
        抽象方法, 继承Pipeline后需要实现的方法
        :return:
        """
        pass

    def set(self, key, value):
        return self.context.set(key, value)

    def get(self, key, default=None):
        return self.context.get(key, default)

    def inc(self, key):
        return self.context.inc(key)
