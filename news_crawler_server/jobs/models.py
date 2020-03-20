import json
from django.db import models, connection


class BaseModel(models.Model):
    createtime = models.DateTimeField(auto_now_add=True, null=True)
    updatetime = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class User(models.Model):
    """用户
    """
    username = models.CharField(max_length=64,
                                primary_key=True,
                                verbose_name="用户名")
    nickname = models.CharField(max_length=64, verbose_name="用户昵称")
    password = models.CharField(max_length=64, verbose_name="密码")

    def __str__(self):
        return "%s-%s" % (self.username, self.nickname)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"


class Rate(models.Model):
    """爬虫工作星级
    """
    value = models.IntegerField(default=0, verbose_name="爬虫工作星级")
    creator = models.ForeignKey(User, models.SET_NULL, null=True)

    class Meta:
        verbose_name = "爬虫工作星级"
        verbose_name_plural = "爬虫工作星级"


class Category(models.Model):
    """爬虫分类
    """
    name = models.CharField(max_length=64,
                            primary_key=True,
                            verbose_name="分类名称")

    def __str__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name = "分类名称"
        verbose_name_plural = "分类名称"


class Tag(models.Model):
    """爬虫标签
    """
    name = models.CharField(max_length=64,
                            primary_key=True,
                            verbose_name="标签名")
    creator = models.ForeignKey(User, models.SET_NULL, null=True)

    def __str__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"


class Job(BaseModel):
    """爬虫工作信息
    """
    STATUS = (('PENDING', 'Pending'), ('PASS', 'Pass'), ('FAIL', 'Fail'))

    CRAWL_TYPE = (('STATIC', 'Static'), ('JSON', 'Json'), ('RENDER', 'Render'),
                  ('OTHER', 'Other'))

    CRAWL_STATUS = (
        ('RIGHT', '爬取正常'), ('LIST_WRONG', '列表爬取异常'), ('CONTENT_WRONG', '正文爬取异常')
    )

    status = models.CharField(max_length=16,
                              choices=STATUS,
                              default='PENDING',
                              verbose_name="状态")
    desc = models.CharField(max_length=128, blank=True)
    is_display = models.BooleanField(default=False)
    platform = models.CharField(max_length=64, blank=True)
    source = models.CharField(max_length=64)
    is_proxy = models.BooleanField(default=False)
    crawl_type = models.CharField(max_length=16,
                                  choices=CRAWL_TYPE,
                                  default='OTHER',
                                  verbose_name="爬取方式")
    url = models.CharField(max_length=512)
    regulation = models.TextField(verbose_name="网页列表处理规则")
    headers = models.TextField(blank=True)
    # 网页处理规则，静态页面为xpath字符串，api
    charset = models.CharField(max_length=16, verbose_name="指定字符集", blank=True)
    interval = models.IntegerField(verbose_name="爬取时间间隔", default=60)
    content_regulation = models.TextField(verbose_name="网页正文处理规则", blank=True)
    source_url = models.TextField(verbose_name="网页原地址", blank=True, default='')
    crawl_status = models.CharField(
        default='RIGHT', verbose_name='任务状态', max_length=16, choices=CRAWL_STATUS)
    latest_crawl_time = models.DateTimeField(
        null=True, default=None, blank=True)
    is_checked = models.BooleanField(default=False, verbose_name='检查状态')

    creator = models.ForeignKey(User,
                                models.SET_NULL,
                                blank=True,
                                null=True,
                                related_name='%(class)s_requests_created')
    follower = models.ManyToManyField(User,
                                      through='JobToFollower',
                                      through_fields=('job_id', 'user'))
    category = models.ManyToManyField(Category,
                                      through='JobToCategory',
                                      through_fields=('job_id', 'category'))
    tag = models.ManyToManyField(Tag,
                                 through='JobToTag',
                                 through_fields=('job_id', 'tag'))
    rate = models.ManyToManyField(Rate,
                                  through='JobToRate',
                                  through_fields=('job_id', 'rate'))

    class Meta:
        verbose_name = "爬虫工作"
        verbose_name_plural = "爬虫工作"
        unique_together = (('url', 'platform'),)


class JobToCategory(BaseModel):
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class JobToTag(BaseModel):
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class JobToRate(BaseModel):
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE)
    rate = models.ForeignKey(Rate, on_delete=models.CASCADE)


class JobToFollower(BaseModel):
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Document(BaseModel):
    job_id = models.ForeignKey(Job, models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=512)
    url = models.CharField(max_length=512)
    url_hash = models.CharField(max_length=32, unique=True, default='')
    content = models.TextField(verbose_name="正文", blank=True, null=True)
    publishtime = models.DateTimeField(null=True)
    meta = models.TextField(blank=True, null=True)
    crawl_status = models.CharField(max_length=4, default='NO')


class ArticleWordfrequency(BaseModel):
    document_url_hash = models.CharField(max_length=32, unique=True, default='')
    wordfrequency = models.TextField()
