import os
import redis

import pgdb
import yaml
from jdtools import TradeDate, color_log as logging


class Config:
    logging.info("Load config.yaml.")
    # filename = os.path.realpath(__file__)
    # dirname = os.path.dirname(filename)
    dirname = '/app_pipeline'
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

JOB_RES_CHANNEL = config['JOB_RES_CHANNEL']

redis_config = config['redis']
job_cache_conn = redis.Redis(**redis_config['job_cache'])
job_pipeline_conn = redis.Redis(**redis_config['pipeline'])

RENDER_INTERVAL_JOBS_KEY = config['RENDER_INTERVAL_JOBS_KEY']

