import time
import datetime
from django.contrib import admin
from django.utils.html import format_html
from server.models import Job, Document
# Register your models here.


@admin.register(Job)
class JobAdminDisplay(admin.ModelAdmin):
    def display_url(self, obj):
        if obj.url:
            return format_html(
                "<a href='{}' target='_blank'>列表链接</a>",
                obj.url
            )
        return ""
    def save_model(self, request, obj, form, change):
        obj.save()

    list_filter = ['crawl_type']

    list_display = (
        'id',
        'crawl_type',
        'regulation',
        'source_url',
        'desc',
        'platform',
        'display_url',
    )
    ordering = [
        '-updatetime'
    ]


@admin.register(Document)
class DocumentAdminDisplay(admin.ModelAdmin):
    def display_url(self, obj):
        if obj.url:
            return format_html(
                "<a href='{}' target='_blank'>原文链接</a>",
                obj.url
            )
        return ""

    list_filter = ['job_id']

    list_display = (
        'job_id',
        'title',
        'display_url'
    )
    ordering = [
        '-updatetime'
    ]
