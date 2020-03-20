from scrapy import cmdline
import json
import subprocess


def ex_run(jobs):   
    if jobs:
        command = "cd renderspider/ && scrapy crawl render -a jobs={}".format(jobs)
        subprocess.call(command,shell=True)
