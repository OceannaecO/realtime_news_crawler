import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
from spider.utils import MyselfError


class RenderSpider:

    def __init__(self, only_check=False):
        self.only_check = only_check
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def start_crawl(self, job):
        res = []
        try:
            self.url = job.get('url')
            self.headers = job.get('headers', {})
            regulation = job.get('regulation')
            regulation = json.loads(regulation)
            self.job_id = job.get('id', -1)

            self.url_xpath = regulation.get('url_xpath')
            self.title_xpath = regulation.get('title_xpath')

            results = self.sync_crawl()
            if not results:
                raise MyselfError('爬取结果为空')
            else:
                if self.only_check:
                    json.loads(job.get('content_regulation', '{}'))
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

    def close_web_driver(self):
        self.driver.quit()

    def sync_crawl(self):
        if self.headers is None:
            self.headers = {}
        res = []
        self.driver.get(self.url)
        url_items = self.driver.find_elements_by_xpath(self.url_xpath)

        title_items = url_items
        if self.title_xpath and self.title_xpath != self.url_xpath:
            title_items = self.driver.find_elements_by_xpath(self.title_xpath)

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
                    'url': urljoin(self.url, url_items[i].get_attribute('href')),
                    'title': title,
                    'job_id': self.job_id,
                })
            except Exception:
                continue

        return res


if __name__ == '__main__':
    job = {
        'id': 19,
        'url': 'http://finance.ce.cn/rolling/index.shtml',
        'is_display': False,
        'is_proxy': False,
        'crawl_type': 'RENDER',
        'regulation':
        '{"url_xpath":"//td[@class=\'font14\']//a","title_xpath":"//td[@class=\'font14\']//a"}',
        'interval': 15,
        'content_regulation': '',
        'charset': ''
    }
    spider = RenderSpider()
    print(spider.start_crawl(job))
