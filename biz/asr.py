# encoding: utf-8

"""
@author: fengxiaochuang
@file: asr.py
@time: 2022/2/10 10:46
"""
import asyncio
import json
import logging
import os
import random
import time
import traceback

import websockets
from websockets.connection import State

from core import Task, Context

# meta 记录音频发送了多少片
AUDIO_CHUNK = "audio_chunk"


class FreeTalkStream:

    def __init__(self, context):
        self.context = context
        self.record_content = ""

    async def _send(self, ws, data):
        # pcm_s16le_16k 格式下 200ms 的分片长度
        chunk = 12800
        length = len(data)
        count = length // chunk
        logging.info("ws will send audio chunk count [%d], chunk size [%d]", count, chunk)
        if length % chunk > 0:
            count = count + 1
        for i in range(0, count):
            if not self._running or ws.state != State.OPEN:
                break
            if time.time() >= self.context.deadline:
                logging.warning("send ws data at deadline, will stop, current chunk [%d], ", i + 1)
                break
            logging.debug("  > [audio slice]")
            await ws.send(data[chunk * i:chunk * (i + 1)])
            # 向上下文中加入chunk信息
            self.context.inc(AUDIO_CHUNK)
            await asyncio.sleep(0.2)  # 等待 200ms
        if ws.state == State.OPEN:
            cmd = {"command": "END", "cancel": False}
            msg = json.dumps(cmd)
            logging.info("  > " + msg)
            await ws.send(msg)

    async def run(self, ws_url: str, headers: dict, config: dict, data):
        """
        WebSocket 交互
        :param ws_url: 连接地址
        :param headers: header头信息
        :param config: start 配置参数
        :param data: 音频数据
        :return:
        """
        ws = None
        # 创建连接
        try:
            logging.info("websocket connect to [%s]", ws_url)
            ws = await websockets.connect(ws_url,
                                          extra_headers=headers, ping_interval=30, ping_timeout=30, close_timeout=120, )
            logging.info("websocket connect successful")
            self._running = True
            # 发送 START 命令
            cmd = {"command": "START", "config": config}
            msg = json.dumps(cmd)
            logging.info(" > " + msg)
            await ws.send(msg)

            # 接收 START 响应，也可能是 ERROR 或 FATAL_ERROR 响应
            msg = await ws.recv()
            logging.info(" < " + msg)
            m = json.loads(msg)
            if m["respType"] == "START":
                logging.info("websocket recv [START]")
                task = asyncio.get_event_loop().create_task(self._send(ws, data))
                async for msg in ws:
                    logging.info(" < " + msg)
                    try:
                        response = json.loads(msg)
                        if response["sentence"]["isFinal"]:
                            result_text = response["sentence"]["role"] + "：" + response["sentence"]["result"]["text"]
                            self.record_content = self.record_content + result_text + "\n"
                    except Exception as _:
                        pass
                    # 写入特定的文件
                    m = json.loads(msg)
                    if m["respType"] == "END":
                        logging.info("websocket recv [END]")
                        self._running = False
                        break
                await task
            else:
                logging.info("failed to start")
            await ws.close()
        except websockets.ConnectionClosed as closeError:
            logging.warning("websocket connection closed, code: [%d], reason: [%s]", closeError.code, closeError.reason)
        except RuntimeError as e:
            logging.error("websocket runtime error,connection will close")
            logging.error(e.__cause__)

        # 关闭websocket连接
        if ws is not None and ws.state == State.OPEN:
            logging.info("websocket close normal")
            await ws.close()


class ASR(Task):
    # 登录地址不会发生变化, 所以设置成常量
    RECOGNISE_URI = "/v10/asr/freetalk/{property}/continue_stream"
    AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "audio")

    def __init__(self, context: Context):
        """
        初始化
        :param context:
        :param property: :class: str
        """
        super().__init__(context)
        # 随机property
        self.property = random.choice(["cn_16k_common"])
        # 随机音频时长
        self.ws_url = self.base_url(self.RECOGNISE_URI).replace("http", "ws") \
            .replace("{property}", self.property) + "?appkey=" + os.getenv("aicp")["appkey"]

        self.asr_config = {
            "addPunc": True,
            "audioFormat": "pcm_s16le_16k",
            "digitNorm": True,
            "interimResults": True,
            "textSmooth": True,
            "tppContextRange": 0,
            "makeParagraph": False,
            "nbest": 1,
            "wordTpp": True,
            "outputPinyin": False,
            "vocab": ""
        }
        # 认证配置
        self.headers = {"X-Hci-Access-Token": self.context.userToken}
        print(self.headers)

    def run(self):
        ft = FreeTalkStream(self.context)
        loop = asyncio.get_event_loop()
        now = time.time()
        # 随机选取音频文件
        audio_list = os.listdir(self.AUDIO_DIR)
        audio_name = random.choice(audio_list)
        audio_filename = os.path.join(self.AUDIO_DIR, audio_name)
        audio_file_stat = os.stat(audio_filename)
        audio_data = open(audio_filename, "rb").read()
        logging.info("selected audio filename [%s], file size[%d]", audio_name, audio_file_stat.st_size)
        if now < self.context.deadline:
            try:
                self.context.set(AUDIO_CHUNK, 0)
                loop.run_until_complete(
                    ft.run(self.ws_url, self.headers, self.asr_config, audio_data)
                )
                audio_chunk = self.context.get(AUDIO_CHUNK, 0)
                if audio_chunk > 0:
                    logging.info("asr run successful, send audio chunk count %d, duration %f",
                                 audio_chunk, audio_chunk / 5.0)
            except Exception as e:
                logging.error("asr error: " + traceback.format_exc())
        else:
            loop.close()
        # 完成一次之后休息1s
        time.sleep(1)
