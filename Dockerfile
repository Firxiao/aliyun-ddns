FROM alpine
WORKDIR /app
COPY . /app
RUN sed -i 's|dl-cdn.alpinelinux.org|mirrors.aliyun.com|g' /etc/apk/repositories
RUN apk add --no-cache py3-pip gcc musl-dev python3-dev libffi-dev openssl-dev
RUN pip3 install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
RUN /usr/bin/crontab crontab.txt
CMD ["/app/entry.sh"]