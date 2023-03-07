# encoding: utf-8

"""
@author: fengxiaochuang
@file: Task.py
@time: 2022/2/10 10:58
"""
import logging
import os
import time

import requests
import json as JSON

import util
from core import Context


class Task(object):
    """
    任务模板, 只是规定了必须带上下文, 方便传递参数
    """

    def __init__(self, context: Context):
        self.context = context

    @staticmethod
    def base_url(uri: str = ""):
        """
        服务器基础路径
        :return:
        """
        server_config = os.getenv("server")
        if "url" in server_config:
            return server_config["url"] + uri
        else:
            raise Exception("无法读取server.url")

    @staticmethod
    def post(url, data=None, json=None, **kwargs):
        """
        封装post请求
        :param url:
        :param data:
        :param json:
        :param kwargs:
        :return:
        """
        random_str = util.random_str(6)
        logging.info("[req-%s] post url [%s], data 【%s】, json 【%s】, kwargs 【%s】", random_str, url, data,
                     json, kwargs)
        response = requests.post(url, data=data, json=json, **kwargs)
        Task.logging_response(random_str, response)
        return response

    @staticmethod
    def get(url, params=None, **kwargs):
        """
        封装get请求
        :param url:
        :param params:
        :param kwargs:
        :return:
        """
        random_str = util.random_str(6)
        logging.info("[req-%s] get url [%s], params 【%s】, kwargs 【%s】", random_str, url, params, JSON.dumps(kwargs))
        response = requests.get(url, params=params, **kwargs)
        Task.logging_response(random_str, response)
        return response

    @staticmethod
    def logging_response(random_str, response):
        content_type = response.headers.get("content-type")
        if 200 <= response.status_code < 300:
            logging.info("[res-%s][http] rev data with code [%d], cost time [%f], body length[%d], content type [%s]",
                         random_str, response.status_code, response.elapsed.total_seconds(), len(response.content),
                         content_type)
        else:
            logging.warning(
                "[res-%s][http] rev data with code [%d], cost time [%f], body length[%d], content type [%s]",
                random_str, response.status_code, response.elapsed.total_seconds(), len(response.content), content_type)
        # logging.info(response.text)
        if content_type is not None and "application/json" in content_type:
            res = JSON.loads(response.text)
            if "errorCode" in res:
                logging.info("[res-%s][ biz] rev errorCode [%d], errorMessage [%s], data【%s】", random_str,
                             res['errorCode'], res['errorMessage'], res['data'])
            else:
                logging.info("[res-%s][ biz] rev data【%s】", random_str, res)
        else:
            logging.info("[res-%s][ biz] rev data length【%d】", random_str, len(response.content))
