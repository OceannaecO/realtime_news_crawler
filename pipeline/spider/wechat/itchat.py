# itchat监听关注的公众号获取最新文章推送
import requests
import datetime
from jdtools import color_log as logging
from bs4 import BeautifulSoup
import sys
import itchat
# import全部消息类型
from itchat.content import *
import json
from ... import settings
import time
import subprocess
from .oss import AliyunOss

aliyun_oss = AliyunOss()
global qr_flag
qr_flag = False

headers = {
    'Content-Type': "application/json",
    'User-Agent': "PostmanRuntime/7.15.2",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Host': "oapi.dingtalk.com",
    'Accept-Encoding': "gzip, deflate",
    'Content-Length': "181",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
}

url = "https://oapi.dingtalk.com/robot/send"

def ec():
    querystring = {"access_token": settings.DINGDING_TOKEN}
    payload = {
        "msgtype": "text",
        "text": {
            "content": "itchat已登自动登出，请手动登入"
        },
        "at": {
            "atMobiles": settings.DINGDING_NOTIFICATION_LIST,
            "isAtAll": 'false'
        }
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers, params=querystring)
    print(response.text)
    print('exit')

    global qr_flag
    qr_flag = False

    subprocess.run(["ls"])
    subprocess.run(["pwd"])
    subprocess.run(["rm", "itchat.pkl"])
    time.sleep(5)
    spider = ItchatSpider()
    spider.run(False)


def lc():
    querystring = {"access_token": settings.DINGDING_TOKEN}
    payload = {
        "msgtype": "text",
        "text": {
            "content": "itchat已成功登录"
        },
        "at": {
            "atMobiles": settings.DINGDING_NOTIFICATION_LIST,
            "isAtAll": 'false'
        }
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers, params=querystring)
    print(response.text)
    print('login')

    global qr_flag
    qr_flag = False


def handle_qr(uuid, status, qrcode):
    f = open('./QR.png', 'w+b')
    f.write(qrcode)
    f.close()

    img_url = aliyun_oss.upload_image(
        './QR.png', "itchat/{}".format('QR.png')
    )

    global qr_flag
    if qr_flag:
        return

    querystring = {"access_token": settings.DINGDING_TOKEN}
    payload = {
        "msgtype": "link",
        "link": {
            "text": "请扫描二维码重新登录",
            "title": "请扫描二维码重新登录",
            "messageUrl": img_url,
            "picUrl": img_url
        },
        "at": {
            "atMobiles": settings.DINGDING_NOTIFICATION_LIST,
            "isAtAll": 'false'
        }
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers, params=querystring)
    print(response.text)
    print('send qr')
    if response.ok:
        qr_flag = True

class ItchatSpider:
    def __init__(self):
        self.gzh_name_dict = {}
        self.upload_dict = settings.TARGET_GZH_DICT
        self.enable_cmd_qr = False

    def run(self, enable_cmd_qr=False, qr_callback=handle_qr):
        self.enable_cmd_qr = enable_cmd_qr
        itchat.auto_login(hotReload=True, enableCmdQR=enable_cmd_qr, loginCallback=lc, exitCallback=ec,
                          qrCallback=qr_callback, picDir='./QR.png')
        # 处理微信公众号消息
        @itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING], isMpChat=True)
        def listen_msg_handler(msg):
            # 监听指定微信公众号推送的文章信息
            logging.info('接收到msg:'.format(msg))
            if msg.get('MsgType') != 49:
                return
            content = msg.get('Content')
            timestamp = msg.get('CreateTime')
            publishtime = datetime.datetime.fromtimestamp(timestamp)
            url = msg.get('Url')
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.find('title')
            thumburl = soup.find('thumburl')
            digest = soup.find('digest')
            logging.info('title: {}'.format(title.text))
            logging.info('digest: {}'.format(digest.text))
            logging.info('thumburl: {}'.format(thumburl.text))
            logging.info('url: {}'.format(url))
            logging.info('publishtime: {}'.format(publishtime))
            username = msg.get('FromUserName')
            usr_info = itchat.search_mps(userName=username)

            new_obj = {
                'title': title.text,
                'publishtime': publishtime,
                'digest': digest.text,
                'thumb_url': thumburl.text,
                'url': url,
                'gzh_name': usr_info.get('NickName')
            }
            logging.info('新文章: {}'.format(new_obj))

            # TODO: 处理爬取结果
        itchat.run()

