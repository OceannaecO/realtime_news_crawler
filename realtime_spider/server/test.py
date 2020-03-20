from .models import Job
import json
    # STATUS = (
    #     ('PENDING', 'Pending'),
    #     ('PASS', 'Pass'),
    #     ('FAIL', 'Fail')
    # )

    # CRAWL_TYPE = (
    #     ('STATIC', 'Static'),
    #     ('JSON', 'Json'),
    #     ('RENDER', 'Render'),
    #     ('OTHER', 'Other')
    # )

    # status = models.CharField(max_length=16, choices=STATUS, default='PENDING', verbose_name="状态")
    # desc = models.CharField(max_length=128, blank=True)
    # is_display = models.BooleanField(default=False)
    # platform = models.CharField(max_length=64, blank=True)
    # source = models.CharField(max_length=64)
    # is_proxy = models.BooleanField(default=False)
    # crawl_type = models.CharField(max_length=16, choices=CRAWL_TYPE, default='OTHER', verbose_name="爬取方式")
    # url = models.CharField(max_length=512)
    # regulation =  models.TextField(verbose_name="网页列表处理规则")
    # headers = models.TextField(blank=True)
    # # 网页处理规则，静态页面为xpath字符串，api
    # regulation =  models.TextField(verbose_name="网页列表处理规则")
    # charset = models.CharField(max_length=16, verbose_name="指定字符集")
    # interval = models.IntegerField(verbose_name="爬取时间间隔", default=60)
    # content_regulation =  models.TextField(verbose_name="网页正文处理规则")
    # creator = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, related_name='%(class)s_requests_created')
j = Job()
j.status = 'PASS'
j.source = 'web'
j.desc = 'test'
j.crawl_type = 'STATIC'
j.interval = 15
j.url = 'http://www.financialnews.com.cn/hg/4'
j.headers = json.dumps({})
test_regulation = {"url_xpath":"//div[@class='left']//ul//li//a","title_xpath":"//div[@class='left']//ul//li//a"}
j.regulation = json.dumps(test_regulation)
res = j.save()

