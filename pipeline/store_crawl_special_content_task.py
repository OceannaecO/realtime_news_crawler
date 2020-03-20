"""
将今日热榜的任务发送给爬虫
"""
import json
import random
import time
import datetime
import redis
import pgdb
from utils import (server_conn, job_pipeline_conn, CONTENT_TASKS_CHANNEL)


def get_content_jobs():
    now = datetime.datetime.now()
    six_minute_before = now - datetime.timedelta(minutes=9000)
    jobs_list = server_conn.query('''
          select 
            sd.url,sj.content_regulation,sj.charset, sj.desc as job_desc
          from 
            server_document as sd 
          inner join 
            server_job as sj
          on 
            sd.job_id_id = sj.id
          where 
            sd.createtime >= '%s' 
          and 
            sd.crawl_status = 'NO' 
          and 
            sj.content_regulation != '' 
          and
            (sd.content is null or sd.content = '')
          and
            sj.desc in ('今日热榜')
          limit 
            30;
        ''' % (six_minute_before, ))
    return jobs_list


def package_jobs_to_redis(jobs):
    job_list = []
    if jobs:
        for job in jobs:
            url = job.get('url', '')
            regulation = job.get('content_regulation', '')
            charset = job.get('charset', '')
            job_desc = job.get('job_desc', '')
            if url and regulation:
                job_list.append({
                    'url': url,
                    'regulation': regulation,
                    'charset': charset,
                    'job_desc': job_desc
                })
        job_list = json.dumps(job_list)
        job_pipeline_conn.publish(CONTENT_TASKS_CHANNEL, job_list)


if __name__ == '__main__':
    jobs = get_content_jobs()
    package_jobs_to_redis(jobs)
    # print(jobs)
    time.sleep(10)
