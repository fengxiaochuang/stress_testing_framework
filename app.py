# encoding: utf-8

"""
@author: fengxiaochuang
@file: app.py
@time: 2022/2/9 16:16
"""
import json
import logging
import os
import random
import time
import multiprocessing
from typing import List
import yaml
import constants
import util
from biz.auth import Auth
from core import Account, Context, Pipeline
# 并发数
from pipeline import Basic, Demo

# 并发数
CONCURRENT_NUMBER = 10
# 并发加入速度, 防止压力瞬间增加导致服务崩溃
CONCURRENT_JOIN_SPEED = 1
# 压测时间(单位秒), 至少为 CONCURRENT_NUMBER * CONCURRENT_JOIN_SPEED
DURATION = 10

if __name__ == '__main__':
    log_path_dir = "logs/"
    # 环境变量赋值
    default_env = os.environ.copy()
    # 从配置文件中获取其他环境变量并追加赋值
    env_file = open("env.yaml", 'r')
    custom_env = yaml.full_load(env_file)
    full_env = dict(list(default_env.items()) + list(custom_env.items()))

    # 计算第几次压测
    serial_no = util.stress_serial_no(log_path_dir)
    # 本次压测文件路径
    log_dir = os.path.join(log_path_dir, str(serial_no).zfill(5))
    # 通过环境变量把日志路径传递到子进程中
    full_env['log_dir'] = log_dir
    # 新建本次压测的日志文件夹
    os.mkdir(log_dir)
    # 初始化日志路径
    log_file_name = os.path.join(log_dir, "master.log")
    logging.basicConfig(
        format="%(asctime)s.%(msecs)03d [master] [%(process)d-%(thread)d] %(levelname)s %(message)s",
        datefmt=constants.DATE_FORMAT,
        level=logging.INFO,
        handlers=[
            logging.FileHandler(log_file_name, encoding="utf-8", mode="a+"),
            logging.StreamHandler()
        ],
    )
    logging.info("system init environ 【%s】", json.dumps(custom_env))
    logging.info("process task has begin")
    multiprocessing.set_start_method("spawn")
    pool = multiprocessing.Pool(CONCURRENT_NUMBER, initializer=util.init_process, initargs=(full_env,))
    logging.info("thread pool init success")

    # 加载用户
    user_map = util.load_user()

    # 计算任务停止时间
    deadline = time.time() + DURATION

    # 收集进程中的数据
    contexts: List[Context] = multiprocessing.Manager().list()

    # 平台使用统一的access token
    appkey = full_env["aicp"]["appkey"]
    secretkey = full_env["aicp"]["secretkey"]
    sys_url = full_env["aicp"]["sysUrl"]
    res = Auth.run(sys_url, appkey, secretkey)
    access_token = res['token']
    # 提前一个小时过期
    token_expire_at = time.time() + float(res["life"]) - 3600

    for i in range(CONCURRENT_NUMBER):
        # 按照序号生成当前线程编号
        process_no = str(i + 1).zfill(5)
        # # 填充用户信息
        # user_list = list(user_map.keys())
        # # 从map中随机选择一个用户
        # selected_user = random.choice(user_list)
        # if selected_user is None:
        #     raise Exception("account list is empty, can't support create new process")
        # password = user_map[selected_user]
        # logging.info("selected id_card[%s] for new process [%s]", selected_user, process_no)
        # account = Account(selected_user, password)
        # # 从列表中删除该用户, 防止重复选择
        # del user_map[selected_user]

        # 初始化上下文, 改为从最外层传递进去
        context = Context(process_no, deadline, account=None)
        context.userToken = access_token
        context.tokenExpireAt = token_expire_at
        # 派发任务
        pool.apply_async(Pipeline.factory, args=(Demo, context, contexts, 1,), error_callback=util.throw_error)
        time.sleep(CONCURRENT_JOIN_SPEED)
        logging.info("one process join run queue, current process count [%d]", i + 1)
    pool.close()
    pool.join()
    logging.info("all process has finished")

    # 收集到的数据打印, 不保证有序
    for item in contexts:
        logging.info("process [%s] run complete, timer [%s], meta [%s]", item.processNo, item.timer(), item.meta)
