FROM python:3.6

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
# RUN apt-get clean
RUN apt update -y
RUN apt install -y supervisor git
RUN apt-get install -y libnss3 libgconf-2-4

# Install Chrome for Selenium
RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb
RUN dpkg -i /chrome.deb || apt-get install -yf
RUN rm /chrome.deb

# Install chromedriver for Selenium
RUN wget https://chromedriver.storage.googleapis.com/76.0.3809.126/chromedriver_linux64.zip
RUN ls
RUN unzip chromedriver_linux64.zip
RUN ls
RUN mv chromedriver /usr/local/bin/chromedriver
RUN chown root:root /usr/local/bin/chromedriver
RUN chmod +x /usr/local/bin/chromedriver

ADD . /app_pipeline

RUN cd /app_pipeline && pip3 install --no-cache-dir -r requirements.txt --trusted-host mirrors.aliyun.com --index-url https://mirrors.aliyun.com/pypi/simple/
COPY pipeline.conf /etc/supervisor/conf.d/

COPY run_pipeline.sh /

RUN chmod a+x /run_pipeline.sh




