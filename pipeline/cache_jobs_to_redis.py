"""
此脚本从server拿到所有已通过任务，并且按照不同的crawl_type,interval
打包成不同大小的包然后放在redis作为缓存,建议每隔一段时间更新一次
"""
import json
import random
import time
import redis
import pgdb
from utils import (
    server_conn,
    job_cache_conn,
    INTERVAL,
    RENDER_INTERVAL_JOBS_KEY,
    JSON_INTERVAL_JOBS_KEY,
    STATIC_INTERVAL_JOBS_KEY,
)


def get_web_jobs():
    jobs_list = server_conn.query(
        '''
            select id, url, is_display, is_proxy, crawl_type, regulation, interval,
            charset from server_job where status='PASS' and crawl_type != 'OTHER';
        '''
    )
    return jobs_list


def package_jobs(jobs, return_jobs=False):
    if jobs:
        random.shuffle(jobs)
        static_15_jobs = []
        static_30_jobs = []
        static_60_jobs = []
        json_15_jobs = []
        json_30_jobs = []
        json_60_jobs = []
        render_15_jobs = []
        render_30_jobs = []
        render_60_jobs = []

        for job in jobs:
            crawl_type = job.get('crawl_type')
            if crawl_type == 'STATIC':
                if job.get('interval') == INTERVAL[0]:
                    static_15_jobs.append(job)
                if job.get('interval') == INTERVAL[1]:
                    static_30_jobs.append(job)
                if job.get('interval') == INTERVAL[2]:
                    static_60_jobs.append(job)

            elif crawl_type == 'JSON':
                if job.get('interval') == INTERVAL[0]:
                    json_15_jobs.append(job)
                if job.get('interval') == INTERVAL[1]:
                    json_30_jobs.append(job)
                if job.get('interval') == INTERVAL[2]:
                    json_60_jobs.append(job)

            elif crawl_type == 'RENDER':
                if job.get('interval') == INTERVAL[0]:
                    render_15_jobs.append(job)
                if job.get('interval') == INTERVAL[1]:
                    render_30_jobs.append(job)
                if job.get('interval') == INTERVAL[2]:
                    render_60_jobs.append(job)

        store_different_interval_jobs_to_redis(static_15_jobs, 15)
        store_different_interval_jobs_to_redis(static_30_jobs, 30)
        store_different_interval_jobs_to_redis(static_60_jobs, 60)

        store_different_interval_jobs_to_redis(
            json_15_jobs, 15, crawl_type='JSON')
        store_different_interval_jobs_to_redis(
            json_30_jobs, 30, crawl_type='JSON')
        store_different_interval_jobs_to_redis(
            json_60_jobs, 60, crawl_type='JSON')

        store_different_interval_jobs_to_redis(
            render_15_jobs, 15, crawl_type='RENDER')
        store_different_interval_jobs_to_redis(
            render_30_jobs, 30, crawl_type='RENDER')
        store_different_interval_jobs_to_redis(
            render_60_jobs, 60, crawl_type='RENDER')

        if return_jobs:
            static_jobs = static_15_jobs + static_30_jobs + static_60_jobs
            json_jobs = json_15_jobs + json_30_jobs + json_60_jobs
            render_jobs = render_15_jobs + render_30_jobs + render_60_jobs
            return static_jobs, json_jobs, render_jobs


def store_different_interval_jobs_to_redis(jobs, interval, crawl_type='STATIC'):
    if crawl_type == 'JSON':
        redis_key = JSON_INTERVAL_JOBS_KEY.format(interval)
        if jobs:
            job_cache_conn.set(redis_key, json.dumps(jobs))
        else:
            job_cache_conn.set(redis_key, '')

    elif crawl_type == 'RENDER':
        redis_key = RENDER_INTERVAL_JOBS_KEY.format(interval)
        if jobs:
            job_cache_conn.set(redis_key, json.dumps(jobs))
        else:
            job_cache_conn.set(redis_key, '')

    else:
        redis_key = STATIC_INTERVAL_JOBS_KEY.format(interval)
        if jobs:
            job_cache_conn.set(redis_key, json.dumps(jobs))
        else:
            job_cache_conn.set(redis_key, '')


if __name__ == '__main__':
    jobs = get_web_jobs()
    package_jobs(jobs)
    time.sleep(300)
