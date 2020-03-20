#!/bin/bash
pip install --trusted-host mirrors.aliyun.com --index-url https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

pushd $(realpath $(dirname $0))

DATE_N=`date "+%Y-%m-%d %H:%M:%S"`
if [ $# -eq 1 ]; then
    echo $1
    if [ $1 == 'worker' ]; then
        echo "${DATE_N} worker"
        celery worker -A spider.mycelery
    fi
fi
