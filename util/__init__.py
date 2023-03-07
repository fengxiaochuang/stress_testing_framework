# encoding: utf-8

"""
@author: fengxiaochuang
@file: __init__.py.py
@time: 2022/2/10 15:01
"""
import csv
import logging
import os
import random
import re
import signal


def stress_serial_no(log_path_dir):
    # 计算第几次压测
    dir_list = os.listdir(log_path_dir)
    last_serial_no = 0
    for dir_item in dir_list:
        if re.match(r'\d+', dir_item):
            if int(dir_item) > last_serial_no:
                last_serial_no = int(dir_item)

    current_serial_no: int = last_serial_no + 1
    return current_serial_no


def load_user():
    # 从csv中加载全部用户
    user_map: dict = {}
    with open("account.csv", newline="") as accountFile:
        reader = csv.DictReader(accountFile, fieldnames=("idcard", "password"), delimiter='\t')
        for row in reader:
            username = row['idcard']
            password = row['password']
            if username is None or password is None:
                continue
            else:
                user_map[username] = password
    return user_map


def init_process(env):
    """
    初始化进程信息
    :param env:
    :return:
    """
    os.environ = env


def throw_error(e):
    """
    子进程异常处理
    :param e:
    :return:
    """
    logging.error(e.__cause__, e)
    os.kill(os.getpid(), signal.SIGTERM)


def random_str(num):
    """
    随机字符串生成
    :return:
    """
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    salt = ''
    for i in range(num):
        salt += random.choice(chars)
    return salt
