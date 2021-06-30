FROM alpine
WORKDIR /app
COPY . /app
RUN sed -i 's|dl-cdn.alpinelinux.org|mirrors.aliyun.com|g' /etc/apk/repositories
RUN apk add --no-cache py3-pip py3-requests py3-yaml py3-cryptography
RUN pip3 install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
RUN pip3 install -r requirements.docker -i https://mirrors.aliyun.com/pypi/simple/
RUN /usr/bin/crontab crontab.docker
RUN ln -sf /proc/1/fd/1 /app/docker.log
CMD ["/app/entry.sh"]