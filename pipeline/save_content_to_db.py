"""
此脚本从redis获取爬虫爬取结果，然后保存到数据库中
"""
import re
import json
from hashlib import md5
import random
import time
import requests
import gevent
import traceback
from gevent import monkey, Greenlet
import redis
import pgdb
from lxml import etree

from generate_wordcloud import generate_wordfrequency
from utils import (server_conn, job_cache_conn,
                   CONTENT_TASKS_CHANNEL, headless_chrome_driver, make_headers)

gevent.monkey.patch_socket()


def crawl_static_content(task, only_check=False):
    try:
        headers = make_headers()
        url = task.get('url')
        regulation = json.loads(task.get('regulation'))
        charset = regulation.get('charset', 'utf-8')
        resp = requests.get(url, headers=headers)
        job_desc = task.get('job_desc')
        if charset == 'auto':
            resp = resp.text
        else:
            resp = resp.content.decode(charset)
        xpath = regulation.get('xpath', '')
        html_tree = etree.HTML(resp)
        if xpath:
            contents = html_tree.xpath(xpath)
            content = ''.join([''.join(i.xpath('.//text()'))
                               for i in contents])
            content = re.sub('\s|<[^<]+?>|\r|\'|\"| ', '', content)
            if only_check and content:
                return {'status': True, 'content': content}
            elif only_check:
                return {'status': False, 'error_msg': '正文爬取为空', 'job': task['job']}
            return {'url': url, 'content': content, 'job_desc': job_desc}
        else:
            if only_check:
                return {'status': False, 'error_msg': '没有正文规则', 'job': task['job']}
            return {'url': url, 'content': '', 'job_desc': job_desc}
    except Exception as e:
        if only_check:
            return {'status': False, 'error_msg': e, 'job': task['job']}
        return {'url': url, 'content': '', 'job_desc': job_desc}


def crawl_render_content(task, only_check=False):
    driver = headless_chrome_driver()
    try:
        url = task.get('url')
        regulation = json.loads(task.get('regulation'))
        driver.get(url)
        xpath = regulation.get('xpath', '')
        items = driver.find_elements_by_xpath(xpath)
        if items:
            content = items.text
            re.sub('\s|<[^<]+?>|\r|\"|\'| ', '', content)
            driver.quit()
            if only_check and content:
                return {'status': True, 'content': content}
            elif only_check:
                return {'status': False, 'error_msg': '正文爬取为空', 'job': task['job']}
            return {'url': url, 'content': content}
        else:
            driver.quit()
            if only_check:
                return {'status': False, 'error_msg': '正文爬取为空', 'job': task['job']}
            return {'url': url, 'content': ''}
    except Exception as e:
        driver.quit()
        if only_check:
            return {'status': False, 'error_msg': e, 'job': task['job']}
        return {'url': url, 'content': ''}


def save_content(content_tasks, only_check=False):
    """
    content_regulation
    {"type": "static" or "render","xpath": "//div[@class='mainContent pt0']"}
    """
    data_list = []
    threads = []
    for task in content_tasks:
        regulation = json.loads(task.get('regulation'))
        crawl_static_content(task)
        if regulation.get('type', 'static') == 'static':
            threads.append(gevent.spawn(crawl_static_content,
                                        task, only_check=only_check))
        else:
            threads.append(gevent.spawn(crawl_render_content,
                                        task, only_check=only_check))
    gevent.joinall(threads)
    for thread in threads:
        resp = thread.value
        if resp:
            data_list.append(resp)
    if only_check:
        return data_list
    query_str = """
        INSERT INTO 
            server_document 
            (url_hash, content, title, url, crawl_status) 
        values
            (%(url_hash)s, %(content)s, 'title', 'url', 'YES')
        ON CONFLICT 
            (url_hash) 
        DO UPDATE SET 
            content = EXCLUDED.content, 
            crawl_status=EXCLUDED.crawl_status
    """
    if data_list is None or len(data_list) == 0:
        return
    container = []
    for job in data_list:
        content = job.get('content')
        url = job.get('url')
        job_desc = job.get('job_desc')
        m5 = md5()
        m5.update(url.encode('utf-8'))
        url_hash = m5.hexdigest()
        if content and job_desc == '今日热榜':
            try:
                generate_wordfrequency(content, url_hash)
            except:
                traceback.print_exc()
        container.append(
            {
                'url_hash': url_hash,
                'content': content
            }
        )
    res = server_conn.executemany(query_str, container)


def listening_content_task():
    res_list = []
    p = job_cache_conn.pubsub()
    p.subscribe([CONTENT_TASKS_CHANNEL])
    for item in p.listen():
        if item['type'] == 'message':
            content_tasks = json.loads(item['data'])
            if len(content_tasks) > 0:
                save_content(content_tasks)


if __name__ == '__main__':
    reponse_list = listening_content_task()
