import json
import re
import time
from datetime import datetime
import requests_async as async_requests
import requests
import asyncio
from spider.utils import make_headers, MyselfError


def safeget(dct, keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


class JsonSpider:
    def __init__(self, only_check=False):
        self.only_check = only_check

    def start_crawl(self, job):
        try:
            self.url = job.get('url')
            headers = job.get('headers', '')
            if headers:
                self.headers = headers
            else:
                self.headers = make_headers()
            regulation = job.get('regulation')
            regulation = json.loads(regulation)
            self.job_id = job.get('id', -1)

            if regulation is not None:
                self.list_path = regulation.get('list_path', [])
                self.url_path = regulation.get('url_path', [])
                self.title_path = regulation.get('title_path', [])
                self.preprocess = regulation.get('preprocess')

            results = self.sync_crawl()
            if not results:
                raise MyselfError('爬取结果为空')
            else:
                if self.only_check:
                    return {'status': True, 'job': job, 'content_task': results[0]}
                else:
                    return results
        except Exception as e:
            if self.only_check:
                return {
                    'status': False,
                    'error_msg': e,
                    'job': job
                }
            else:
                return None

    def sync_crawl(self):
        res = []
        response = requests.get(url=self.url, headers=self.headers)
        if response.ok:
            if self.preprocess and self.preprocess.get('type') == 'TRIM':
                trim_index = self.preprocess.get('meta').get('index')
                json_str = response.text[trim_index[0]:trim_index[1]]
                json_obj = json.loads(json_str)
            else:
                json_obj = response.json()
            if len(self.list_path) > 0:
                item_list = safeget(json_obj, self.list_path)
            else:
                item_list = json_obj
        for item in item_list:
            try:
                url = safeget(item, self.url_path)
                title = safeget(item, self.title_path)
                if title and len(title) > 2:
                    title = re.sub('\s|<[^<]+?>|\r|\'|\"| ', '',title)
                else:
                    continue
                if url is not None and title is not None:
                    res.append({
                        'url': url,
                        'title': title,
                        'job_id': self.job_id,
                    })
            except Exception:
                continue
        return res


if __name__ == '__main__':
    job = {
        'id': 16,
        'url': 'http://api.mp.cnfol.com//index/indexcjh/top_articles?category_id=-1&page=1&minid=138756088&_=1568699984061',
        'is_display': False,
        'is_proxy': False,
        'crawl_type': 'JSON',
        'regulation': '{"list_path":["data"], "url_path": ["url"], "title_path": ["title"], "preprocess": {"type":"TRIM", "meta":{"index": [12,-2]}}}',
        'interval': 15,
        'content_regulation': '',
        'charset': ''
    }
    spider = JsonSpider()
    print(spider.start_crawl(job))
