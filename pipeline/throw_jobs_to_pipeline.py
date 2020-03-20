"""
此脚本按照不同任务的时间间隔将任务丢到任务的pipeline里面去
"""
import time
import json
import argparse
import redis
from utils import job_pipeline_conn, job_cache_conn, INTERVAL, STATIC_JOBS_PIPE_KEY, JSON_JOBS_PIPE_KEY, RENDER_JOBS_PIPE_KEY,\
    STATIC_INTERVAL_JOBS_KEY, JSON_INTERVAL_JOBS_KEY, RENDER_INTERVAL_JOBS_KEY


def throw_different_jobs(interval):
    static_jobs_key = STATIC_INTERVAL_JOBS_KEY.format(interval)
    json_jobs_key = JSON_INTERVAL_JOBS_KEY.format(interval)
    render_jobs_key = RENDER_INTERVAL_JOBS_KEY.format(interval)

    static_jobs = job_cache_conn.get(static_jobs_key)
    json_jobs = job_cache_conn.get(json_jobs_key)
    render_jobs = job_cache_conn.get(render_jobs_key)

    if static_jobs:
        jobs = json.loads(static_jobs)
        jobs = [json.dumps(job) for job in jobs]
        res = job_pipeline_conn.rpush(STATIC_JOBS_PIPE_KEY, *jobs)

    if json_jobs:
        jobs = json.loads(json_jobs)
        jobs = [json.dumps(job) for job in jobs]
        job_pipeline_conn.rpush(JSON_JOBS_PIPE_KEY, *jobs)

    if render_jobs:
        jobs = json.loads(render_jobs)
        jobs = [json.dumps(job) for job in jobs]
        job_pipeline_conn.rpush(RENDER_JOBS_PIPE_KEY, *jobs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('interval', type=int)
    args = parser.parse_args()
    interval = args.interval

    if interval in INTERVAL:
        throw_different_jobs(interval)
        time.sleep(interval)
