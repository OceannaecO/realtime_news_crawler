#!/bin/bash

pushd $(realpath $(dirname $0))
mkdir -p logs
python manage.py migrate
python manage.py collectstatic --noinput
pip install --trusted-host mirrors.aliyun.com --index-url https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
python manage.py runserver 0.0.0.0:8000
uwsgi --ini uwsgi.ini