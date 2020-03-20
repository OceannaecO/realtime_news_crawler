import os
import random
import redis
import yaml


class Config:
    filename = os.path.realpath(__file__)
    dirname = os.path.dirname(filename)
    config_filename = os.path.join(dirname, "config.yaml")

    with open(config_filename) as fp:
        data = yaml.load(fp, Loader=yaml.FullLoader)

    @classmethod
    def get_config(cls):
        return cls.data


class MyselfError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo


config = Config.get_config()

redis_config = config['redis']
job_pipeline_conn = redis.Redis(**redis_config['pipeline'])

BROKER = config['BROKER']
BACKEND = config['BACKEND']

JOB_RES_CHANNEL = config['JOB_RES_CHANNEL']


USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6',
]


def make_headers():
    agent = random.choice(USER_AGENTS)
    return {'User-Agent': agent}
