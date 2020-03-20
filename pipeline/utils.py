import os
import random
import datetime
from email.utils import parseaddr
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib

import redis
import pgdb
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Config:
    filename = os.path.realpath(__file__)
    dirname = os.path.dirname(filename)
    config_filename = os.path.join(dirname, "config.yaml")

    with open(config_filename) as fp:
        data = yaml.load(fp, Loader=yaml.FullLoader)

    @classmethod
    def get_config(cls):
        return cls.data


config = Config.get_config()

server_config = config['pgdb']['server']
server_conn = pgdb.Connection(
    user=server_config["user"],
    host=server_config["host"],
    port=int(server_config["port"]),
    password=server_config["password"],
    database=server_config["database"],
)

redis_config = config['redis']
job_cache_conn = redis.Redis(**redis_config['job_cache'])
job_pipeline_conn = redis.Redis(**redis_config['pipeline'])

BROKER = config['BROKER']
BACKEND = config['BACKEND']

STATIC_INTERVAL_JOBS_KEY = config['STATIC_INTERVAL_JOBS_KEY']
JSON_INTERVAL_JOBS_KEY = config['JSON_INTERVAL_JOBS_KEY']
RENDER_INTERVAL_JOBS_KEY = config['RENDER_INTERVAL_JOBS_KEY']

STATIC_JOBS_PIPE_KEY = config['STATIC_JOBS_PIPE_KEY']
RENDER_JOBS_PIPE_KEY = config['RENDER_JOBS_PIPE_KEY']
JSON_JOBS_PIPE_KEY = config['JSON_JOBS_PIPE_KEY']
DINGDING_NOTIFICATION_LIST = config['DINGDING']['dingding_notification_list']
ACCESS_TOKEN = config['DINGDING']['access_token']
CONTENT_TASKS_CHANNEL = config['CONTENT_TASKS_CHANNEL']
C_URL = config['C_URL']

INTERVAL = config['INTERVAL']

JOB_RES_CHANNEL = config['JOB_RES_CHANNEL']

USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6',
]


def headless_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver


def make_headers():
    agent = random.choice(USER_AGENTS)
    return {'User-Agent': agent}


class SendEmail:
    def __init__(self, to_add):
        today = datetime.date.today().strftime('%Y%m%d')
        self.user = config['email_settings']['fromaddr']
        self.passwd = config['email_settings']['password']
        to_list = to_add
        to_addrs = to_list.split(';')
        self.to_add = to_addrs
        self.tag = "同花顺数据反馈 "+str(today)

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def get_attach(self, content):
        # 内容初始化，定义内容格式（普通文本，html）

        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = self._format_addr("爬虫任务检查报告<%s>" % self.user)
        # msg['To'] = self._format_addr("<%s>" %self.to_add)
        msg['To'] = ";".join(self.to_add)
        msg['Subject'] = Header(self.tag, 'utf-8').encode()
        return msg.as_string()

    def send(self, content):
        try:
            server = smtplib.SMTP_SSL(config['email_settings']['server'])
            server.login(self.user, self.passwd)
            server.sendmail("<%s>" % self.user, self.to_add,
                            self.get_attach(content))
            server.quit()
            print("send email successful")
        except Exception as e:
            print("send email failed %s" % e)
