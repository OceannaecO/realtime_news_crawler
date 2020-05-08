from hashlib import md5
import json
import time

import gevent
import gevent.monkey

from utils import server_conn, SendEmail
from spider.general import JsonSpider, StaticSpider, RenderSpider
from cache_jobs_to_redis import package_jobs
from spider.mycelery import gevent_jobs_handler
from save_content_to_db import save_content


gevent.monkey.patch_socket()


def get_web_jobs():
    jobs_list = server_conn.query(
        '''
            select id, url, is_display, is_proxy, crawl_type, regulation, platform, interval, content_regulation,
            charset from server_job where status='PASS' and crawl_type != 'OTHER' and is_checked = false limit 10;
        '''
    )
    return jobs_list


def update_data_by_format_sql(query_str, jobs, is_job=False):
    ids = []
    for job in jobs:
        if is_job:
            ids.append(job['job']['id'])
        else:
            ids.append(job['id'])
    if ids:
        if len(ids) > 1:
            ids = str(tuple(ids))
        else:
            ids = str(tuple(ids)).replace(',', '')
        query_str = query_str % (ids)
        server_conn.execute(query_str)


def main():
    jobs = get_web_jobs()
    query_str = "update server_job set is_checked = true where id in %s;"
    update_data_by_format_sql(query_str, jobs)

    list_error_job_container = []
    static_jobs, json_jobs, render_jobs = package_jobs(jobs, return_jobs=True)
    results = gevent_jobs_handler(
        static_jobs, only_check=True) + gevent_jobs_handler(render_jobs, only_check=True) + gevent_jobs_handler(json_jobs, only_check=True)
    content_tasks = []
    for i in results:
        if not i.get('status'):
            list_error_job_container.append(
                {
                    'job': i.get('job'),
                    'error_msg': str(i.get('error_msg')),
                }
            )
        else:
            content_task = {
                'url': i['content_task']['url'],
                'regulation': i['job']['content_regulation'],
                'charset': i['job']['charset'],
                'job_id': i['job']['id'],
                'job': i['job']
            }
            content_tasks.append(content_task)
    content_crawl_result = save_content(content_tasks, only_check=True)

    query_str = "update server_job set crawl_status = 'LIST_WRONG' where id in %s;"
    update_data_by_format_sql(query_str, list_error_job_container, is_job=True)

    content_error_job_container = []
    for i in content_crawl_result:
        if not i.get('status'):
            content_error_job_container.append(
                {
                    'job': i.get('job'),
                    'error_msg': str(i.get('error_msg')),
                }
            )

    query_str = "update server_job set crawl_status = 'CONTENT_WRONG' where id in %s;"
    update_data_by_format_sql(
        query_str, content_error_job_container, is_job=True)

    email_ = SendEmail('')
    email_.send("""
    列表错误任务:{}
    正文错误任务:{}
    """.format([{'job_id': i['job']['id'], 'error_msg': i['error_msg']} for i in list_error_job_container],
               [{'job_id': i['job']['id'], 'error_msg': i['error_msg']} for i in content_error_job_container]))


if __name__ == '__main__':
    main()
    time.sleep(600)
