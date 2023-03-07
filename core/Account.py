# encoding: utf-8

"""
@author: fengxiaochuang
@file: Account.py
@time: 2022/2/10 10:49
"""


class Account(object):
    """
    用户身份信息
    """
    username = None
    password = None

    def __init__(self, username, password):
        self.username = username
        self.password = password
