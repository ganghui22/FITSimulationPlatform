import base64
import json
import time
import socketio
import requests
import threading
from bs4 import BeautifulSoup
import cv2
import cv2 as cv
import numpy as np
from pyzbar import pyzbar as pyzbar
import qrcode_terminal
import six
import logging

"""
Author: ganghui22
Date: 2022-01-23 16:29:01
LastEditTime: 2022-01-29 17:54:24
LastEditors: ganghui22
Description: 微信模块
FilePath: /workspace/wechat_program/main.py
"""


class WechatMessage(object):
    """微信message类"""

    def __init__(self,
                 FromUserName: str = None,
                 ToUserName: str = None,
                 MsgType: int = None,
                 Content: str = None,
                 ActionUserName: str = None,
                 PushContent: str = None,
                 ActionNickName: str = None):
        """微信message类

        :param:
        :param FromUserName: 消息来源
        :param ToUserName: 消息去处
        :param MsgType: 消息类型，1为文本消息
        :param Content: 消息内容
        :param ActionUserName: 群聊中会有，其他为空
        :param PushContent: 推送的消息(手机弹窗时的消息提示)
        :param ActionNickName: 备注名
        """
        self.FromUserName = FromUserName
        self.ToUserName = ToUserName
        self.Content = Content
        self.ActionUserName = ActionUserName
        self.MsgType = MsgType
        self.PushContent = PushContent
        self.ActionNickName = ActionNickName

    @classmethod
    def FromMessage(cls, message: json):
        wechatmessage = WechatMessage()
        for (key, value) in six.iteritems(message):
            wechatmessage.__dict__[key] = value
        return wechatmessage


class WechatServer:
    def __init__(self, wx_id: str, func_on_msgs, func_on_event, url: str = 'http://81.70.197.166:8898'):
        """指定账号登陆

        :param:
        :param wx_id: 要登陆的微信号
        :param url: 服务器服务地址
        """
        self.url = url
        self.sio = socketio.Client(logger=False, engineio_logger=False)
        self.current_wx_id = wx_id
        requests.adapters.DEFAULT_RETRIES = 5
        self.s = requests.session()
        self.s.keep_alive = False
        self.func_on_msgs = func_on_msgs
        self.func_on_event = func_on_event
        self.wx_name = None
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("WechatSever")
        self.logger.info('Everything Is OK!!')

        @self.sio.on('OnWeChatMsgs')
        def OnWeChatMsgs(message):
            """
            接受到消息时触发

            :param message:
            :return:
            """
            if 'CurrentPacket' in message:
                if 'Data' in message['CurrentPacket']:
                    message = message['CurrentPacket']['Data']
            if message['ToUserName'] == self.current_wx_id:
                if 'MsgType' in message:
                    # 文本消息
                    if message['MsgType'] == 1:
                        # 消息来源他人
                        if message['FromUserName'] != self.current_wx_id:
                            # 来自群聊的消息
                            if message['FromUserName'][-9:] == '@chatroom':
                                self.logger.info('message from chatroom:{},content:{}'.format(message['FromUserName'],
                                                                                              message['Content']))
                            # 来自个人的消息
                            else:
                                self.logger.info('message from individual:{},content:{}'.format(message['FromUserName'],
                                                                                                message['Content']))
                            wechat_message = WechatMessage.FromMessage(message)
                            self.func_on_msgs(self, wechat_message)
                        # 消息来源自己
                        else:
                            print('send message to:{},content:{}'.format(message['ToUserName'], message['Content']))

        @self.sio.on('OnWeChatEvents')
        def OnWeChatEvents(message):
            """
            事件触发
            :param message:
            :return: None
            """
            print("*" * 30, "OnWeChatEvents", "*" * 30)
            print(message)

        def thread_job():
            self.sio.connect(self.url, transports=['websocket'])
            threading.Thread()
            self.sio.wait()
            self.sio.disconnect()

        add_thread = threading.Thread(target=thread_job)
        add_thread.start()
        try:
            if self.Is_Offline():
                self, logging.warning("检测到指定的微信账号未在给定的服务器中登陆，尝试历史登陆.....")
                if self.History_Login():
                    self.logger.warning("历史登陆失败，尝试扫码登陆....")
                    self.GetQRcode()
                else:
                    self.logger.info("已成功请求历史登陆，请在主设备上确认")
        except requests.exceptions.ConnectionError:
            self.logger.error("未检测到服务器端口的回复，请检测服务器上的服务是否部署,5秒中后尝试重新连接")
            time.sleep(5)

    def Say(self, to_user_name: str, content: str, at_users: str = None) -> None:
        """发送文本消息

        :param to_user_name:要发送消息的联系人的wx_id
        :param content:要发送消息的文本内容
        :param at_users:需要@的用户，仅在群聊中有效，必须是默认用户名(message中的‘ActionNickName’)
        :return:None
        """
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        url = self.url + '/v1/LuaApiCaller?funcname=SendMsg&timeout=10&wxid=' + self.current_wx_id
        if at_users is None:
            at_users = ""
        post_json = {
            "ToUserName": to_user_name,
            "Content": content,
            "MsgType": 1,
            "AtUsers": at_users
        }
        res = requests.request('post', url, json=post_json, headers=headers)
        self.logger.info("send message to {}:{}".format(to_user_name, content))

    def SayImage(self, to_user_name: str, base64_image: str) -> None:
        """
        发送图片
        :param to_user_name:
        :param base64_image:
        :return:
        """
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        url = self.url + '/v1/LuaApiCaller?funcname=SendImage&timeout=10&wxid=' + self.current_wx_id
        post_json = {
            "ToUserName": to_user_name,
            "ImageBase64": base64_image
        }
        res = requests.request('post', url, json=post_json, headers=headers)
        print(res.text)

    def History_Login(self) -> str:
        """
        历史登陆该微信

        :return:None
        """
        url = self.url + '/v1/Login/Push'
        payload = {'wxid': self.current_wx_id}
        res = self.s.get(url, params=payload)
        if res.json()['ErrMsg'] == 'err':
            return 'err'
        else:
            return None

    def GetQRcode(self) -> None:
        """获取该微信号的登陆二维码

        :return: None
        """
        url = self.url + '/v1/Login/GetQRcode'
        payload = {
            'isIPad': 2,
            'wxid': self.current_wx_id
        }
        res = self.s.get(url, params=payload)
        base64qrcode = BeautifulSoup(res.text).img['src'].split(",")[1]
        print(base64qrcode)
        image = base64.b64decode(base64qrcode)
        image = np.frombuffer(image, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        barcodes = pyzbar.decode(image)
        for barcode in barcodes:
            # 提取二维码的边界框的位置
            # 画出图像中条形码的边界框
            (x, y, w, h) = barcode.rect
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # 提取二维码数据为字节对象，所以如果我们想在输出图像上
            # 画出来，就需要先将它转换成字符串
            barcodeData = barcode.data.decode("UTF8")
            barcodeType = barcode.type

            # 绘出图像上条形码的数据和条形码类型
            text = "{} ({})".format(barcodeData, barcodeType)
            cv.putText(image, text, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 125), 2)
            # 向终端打印条形码数据和条形码类型
            print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
            print("请用微信扫描以下二维码，登陆微信")
            qrcode_terminal.draw(barcodeData)

    def Is_Offline(self) -> bool:
        """
        查看微信号是否在线，在线返回False，不在线返回True

        :return: bool
        """
        url = self.url + '/v1/WeChatInfo'
        payload = None
        res = self.s.get(url, params=payload).text
        WechatUsers = json.loads(res)
        for WechatUser in WechatUsers['WeChatUsers']:
            if self.current_wx_id[:-4] + '****' == WechatUser['Wxid']:
                self.wx_name = WechatUser['NickName']
                return False
        return True


# SocketIO Client
# sio = socketio.AsyncClient(logger=True, engineio_logger=True)

# -----------------------------------------------------
# Socketio
# -----------------------------------------------------


def onmessage(wechatserver: WechatServer, message: WechatMessage):
    # 来自群的消息
    if message.FromUserName[-9:] == '@chatroom':
        # 在群中被@的消息
        if '@' + wechatserver.wx_name in message.Content:
            if message.ActionNickName == '':
                wechatserver.Say(message.FromUserName, '@' + message.PushContent[:-7] + " " + "好的呀",
                                 message.ActionUserName)
            else:
                wechatserver.Say(message.FromUserName, '@' + message.ActionNickName + " " + "好的呀",
                                 message.ActionUserName)
        # 在群中没有被@的消息
        else:
            pass
    # 来自个人的消息
    else:
        wechatserver.Say(message.FromUserName, "Ok~")
        if message.Content == "发我一张图片":
            image = open(r'/home/xdy/图片/1.jpeg', 'rb')
            base64_image = base64.b64encode(image.read()).decode()
            image.close()
            wechatserver.SayImage(message.FromUserName, base64_image)


def onevent(wechatserver: WechatServer, event: json):
    print('onevent')


global flag


def main():
    # wxid_6upszurr9wlv12 bot1
    # wxid_517djxubg7rz22 bot2
    wechatserver = WechatServer('wxid_6upszurr9wlv12', onmessage, onevent)


if __name__ == '__main__':
    main()
