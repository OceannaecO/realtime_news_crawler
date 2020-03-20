FROM python:3.6

ADD ./realtime_spider /app
WORKDIR /app
VOLUME /app

RUN pip install --trusted-host mirrors.aliyun.com --index-url https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r /app/requirements.txt
EXPOSE 8000