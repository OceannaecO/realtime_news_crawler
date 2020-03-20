#!/bin/bash
#pip3 install --no-cache-dir git+http://install:china2019@www.profeto.cn:32769/deploy/jdtools.git --index-url https://mirrors.aliyun.com/pypi/simple/
supervisord -c /etc/supervisor/supervisord.conf
tail -f /app_pipeline/run_pipeline.sh