# -*- coding: utf-8 -*-
import scrapy
import json
import re
from urllib.parse import urljoin
from lxml import etree
from scrapy_splash import SplashRequest
from utils import job_pipeline_conn, JOB_RES_CHANNEL
import time


class RenderSpider(scrapy.Spider):
    name = 'render'

    def __init__(self, jobs, only_check=False):

        self.only_check = only_check
        self.jobs = jobs
        jobs_list = job_pipeline_conn.get(self.jobs)
        job_pipeline_conn.delete(self.jobs)
        jobs_list = json.loads(jobs_list)
        self.start_urls = []
        self.start_url_2_job = {}
        for job in jobs_list:
            # 这个地方的含义是不在这个列表域名范围内的网页不会被爬取
            # self.allowed_domains = [self.job['url']]
            url = job['url']
            self.start_url_2_job[url] = job
            self.start_urls.append(url)

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 2})

    def parse(self, response):
        res = []
        try:
            url = response.url
            job = self.start_url_2_job[url]
            results = [self.sync_crawl(response, job)]
            if not results:
                print('爬取结果为空')
            else:
                if self.only_check:
                    return {'status': True, 'job': job, 'content_task': results[0]}
                else:
                    result_str = json.dumps(results)
                    job_pipeline_conn.publish(JOB_RES_CHANNEL, result_str)
        except Exception as e:
            if self.only_check:
                return {
                    'status': False,
                    'error_msg': e,
                    'job': job
                }
            else:
                return None

    def sync_crawl(self, response, job=''):
        origin_url = response.url
        regulation = job.get('regulation')
        regulation = json.loads(regulation)
        job_id = job.get('id', -1)
        url_xpath = regulation.get('url_xpath')
        title_xpath = regulation.get('title_xpath')
        res = []
        url_items = response.xpath(url_xpath).getall()
        title_items = url_items
        if title_xpath and title_xpath != url_xpath:
            title_items = response.xpath(title_xpath).getall()

        if len(title_items) != len(url_items):
            return res
        for i in range(0, len(url_items)):
            try:
                url_xpath = etree.HTML(url_items[i])
                title = url_xpath.xpath(
                    "//text()")[0] if len(url_xpath.xpath("//text()")) > 0 else None
                url = url_xpath.xpath(
                    "//@href")[0] if len(url_xpath.xpath("//text()")) > 0 else None
                if title and len(title) > 2:
                    title = re.sub('\s|<[^<]+?>|\r|\'|\"| ', '', title)
                else:
                    continue
                res.append({
                    'url': urljoin(origin_url, url),
                    'title': title,
                    'job_id': job_id,
                })
            except Exception:
                continue
        return res
