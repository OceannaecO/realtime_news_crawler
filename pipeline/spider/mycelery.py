import redis
import json
import time

from gevent import Greenlet
import gevent
from celery import Celery, platforms
import gevent.monkey

from spider.utils import job_pipeline_conn, BROKER, JOB_RES_CHANNEL
from spider.general import JsonSpider, StaticSpider, RenderSpider
from renderspider.renderspider.run import ex_run
gevent.monkey.patch_socket()
platforms.C_FORCE_ROOT = True  # 设置root权限

# CELERYD_FORCE_EXECV 防止死锁
# CELERYD_CONCURRENCY 设置子进程的最大数
# CELERYD_MAX_TASKS_PER_CHILD 每个celery最多执行多少个任务后销毁重建
celery_config = {'CELERYD_CONCURRENCY': 30, 
                 'CELERYD_MAX_TASKS_PER_CHILD': 10,
                 'CELERY_TIMEZONE': 'Asia/Shanghai',
                 'CELERYD_FORCE_EXECV': True}

app = Celery('celery_task', broker=BROKER)

app.config_from_object(celery_config)


def gevent_jobs_handler(jobs, only_check=False):
    res_list = []
    crawl_type = 'OTHER'
    for job in jobs:
        crawl_type = job.get('crawl_type')
        if crawl_type == 'JSON':
            s = JsonSpider(only_check=only_check)
            break
        elif crawl_type == 'STATIC':
            s = StaticSpider(only_check=only_check)
            
    threads = [gevent.spawn(s.start_crawl, job) for job in jobs]
    result = gevent.joinall(threads)
    
    return [thread.value for thread in threads]
    
    
@app.task
def run_spider(jobs, pubtime):
    current_ts = int(time.time())
    if current_ts - pubtime > 60:
        job_pipeline_conn.delete(jobs)
        return
    jobs_list = job_pipeline_conn.get(jobs)
    jobs_list = json.loads(jobs_list)
    if jobs_list:
        job = jobs_list[0]
        crawl_type = job.get('crawl_type')
        if crawl_type == 'RENDER':
            ex_run(jobs)
        else:
            res_list = gevent_jobs_handler(jobs_list)
            res_str = json.dumps(res_list)
            job_pipeline_conn.publish(JOB_RES_CHANNEL, res_str)
    job_pipeline_conn.delete(jobs)
            
            
if __name__ == "__main__":
    test_url = 'http://api.xuangubao.cn/api/messages/new?limit=10'
    test_headers = {}
    test_regulation = {'list_path': ["Messages"],
                       "url_path": ["Url"], "title_path": ["Title"]}
    jobs = [{'id': 1, 'url': test_url, 'headers': test_headers,
             'regulation': test_regulation, 'crawl_type': 'JSON'}]
    res_list = gevent_jobs_handler(jobs)
