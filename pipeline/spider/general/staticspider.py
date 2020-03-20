import json
import time
import re
from lxml import etree
from urllib.parse import urljoin
import requests
from spider.utils import make_headers, MyselfError


class StaticSpider:
    def __init__(self, only_check=False):
        self.only_check = only_check

    def start_crawl(self, job):
        try:
            self.url = job.get('url')
            headers = job.get('headers', '')
            if headers:
                self.headers = json.loads(headers)
            else:
                self.headers = make_headers()
            regulation = job.get('regulation')
            regulation = json.loads(regulation)
            self.job_id = job.get('id', -1)

            self.url_xpath = regulation.get('url_xpath')
            self.title_xpath = regulation.get('title_xpath')
            self.charset = job.get('charset')

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
        tree = etree.HTML(response.content.decode(
            self.charset if self.charset else 'utf8'))
        url_items = tree.xpath(self.url_xpath)
        title_items = url_items
        if self.title_xpath and self.title_xpath != self.url_xpath:
            title_items = tree.xpath(self.title_xpath)

        if len(title_items) != len(url_items):
            return res
        for i in range(0, len(url_items)):
            try:
                title = title_items[i].text
                if title and len(title) > 2:
                    title = re.sub('\s|<[^<]+?>|\r|\'|\"| ', '', title)
                else:
                    continue
                res.append({
                    'url': urljoin(self.url, url_items[i].attrib['href']),
                    'title': title,
                    'job_id': self.job_id,
                })
            except Exception:
                continue

        return res


if __name__ == '__main__':
    job = {'id': 1,
           'url': 'https://www.gelonghui.com/',
           'is_display': False,
           'is_proxy': False,
           'crawl_type': 'STATIC',
           'regulation': '{"url_xpath": "//*[@id=\'__layout\']/div/section/section/section/section/div/section/section/ul/li/section/a", "title_xpath": "//*[@id=\'__layout\']/div/section/section/section/section/div/section/section/ul/li/section/a/h2"}',
           'interval': 60,
           'content_regulation': '{"type": "static","xpath":"//article[@class=\'article-with-html\']","charset": "utf-8"}',
           'charset': '',
           'headers': '{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}'}
    spider = StaticSpider()
    print(spider.start_crawl(job))
