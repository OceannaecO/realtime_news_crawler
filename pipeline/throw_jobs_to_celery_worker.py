import json
import argparse
import string
import random
import redis
import time
from spider.mycelery import run_spider
from utils import job_pipeline_conn, STATIC_JOBS_PIPE_KEY, JSON_JOBS_PIPE_KEY, RENDER_JOBS_PIPE_KEY

keys = string.ascii_letters + string.digits


def throw_jobs_to_celery(_type):
    if _type == 'json':
        jobs = job_pipeline_conn.lrange(JSON_JOBS_PIPE_KEY, 0, 15)
        job_pipeline_conn.ltrim(JSON_JOBS_PIPE_KEY, 16, -1)

    elif _type == 'render':
        jobs = job_pipeline_conn.lrange(RENDER_JOBS_PIPE_KEY, 0, 15)
        job_pipeline_conn.ltrim(RENDER_JOBS_PIPE_KEY, 16, -1)

    else:
        jobs = job_pipeline_conn.lrange(STATIC_JOBS_PIPE_KEY, 0, 15)
        job_pipeline_conn.ltrim(STATIC_JOBS_PIPE_KEY, 16, -1)
    if jobs:
        jobs = json.dumps([json.loads(job) for job in jobs])
        jobs_key = 'REALTIME_JOBS' + '-' + \
            ''.join(random.sample(keys, 16)) + '-' + str(int(time.time()))

        job_pipeline_conn.set(jobs_key, jobs)
        job_pipeline_conn.expire(jobs_key, 180)
        if _type == 'json':
            res = run_spider.delay(jobs_key, int(time.time()))
        elif _type == 'render':
            run_spider.delay(jobs_key, int(time.time()))
        else:
            run_spider.delay(jobs_key, int(time.time()))

    else:
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('type', type=str)
    args = parser.parse_args()
    _type = args.type

    if _type in ['static', 'json', 'render']:
        while True:
            throw_jobs_to_celery(_type)
    else:
        print('参数有误')
