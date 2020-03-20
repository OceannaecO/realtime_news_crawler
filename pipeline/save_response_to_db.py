"""
此脚本从redis获取爬虫爬取结果，然后保存到数据库中
"""
import json
from hashlib import md5
import pgdb
from utils import server_conn, job_cache_conn, JOB_RES_CHANNEL


def save_job_response(res_obj_list):
    query_str = """insert into server_document (job_id_id, url, url_hash, title, crawl_status, createtime, updatetime) values 
    ('%(job_id_id)s',%(url)s, %(url_hash)s, %(title)s, 'NO', now(), now()) ON CONFLICT (url_hash) DO NOTHING;"""
    for response_list in res_obj_list:
        if response_list is None or len(response_list) == 0:
            return
        container = []
        for job in response_list:
            job_id = job.get('job_id')
            title = job.get('title')
            url = job.get('url')
            if not title or not url or len(title) < 5:
                continue
            m5 = md5()
            m5.update(url.encode('utf-8'))
            url_hash = m5.hexdigest()
            container.append({
                'job_id_id': job_id,
                'title': title,
                'url': url,
                'url_hash': url_hash
            })
        res = server_conn.executemany(query_str, container)


def get_job_response():
    res_list = []
    p = job_cache_conn.pubsub()
    p.subscribe([JOB_RES_CHANNEL])
    for item in p.listen():
        if item['type'] == 'message':
            res_obj_list = json.loads(item['data'])
            if len(res_obj_list) > 0:
                save_res = save_job_response(res_obj_list)


if __name__ == '__main__':
    reponse_list = get_job_response()
