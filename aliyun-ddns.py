#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import logging
import os
import sys
import yaml
import re
import requests
from datetime import date, datetime, timedelta

from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordInfoRequest
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkcore import client

try:
    with open(sys.path[0] + '/setting.yml', 'r') as f:
        s = yaml.safe_load(f)
        # print(yaml.dump(s, default_flow_style=False))
        # 阿里云 Access Key ID
        access_key_id = s['access_key_id']
        # 阿里云 Access Key Secret
        access_key_secret = s['access_key_secret']
        # 阿里云 一级域名
        rc_domain = s['rc_domain']
        # 解析记录
        rc_rr_list = s['rc_rr_list']
except:
    access_key_id = os.getenv("ACCESS_KEY_ID")
    access_key_secret = os.getenv("ACCESS_KEY_SECRET")
    rc_domain = os.getenv("RC_DOMAIN")
    rc_rr_list = os.getenv("RC_RR_LIST").split(",")

# 返回内容格式
rc_format = 'json'
# 日志保留天数
logs_keep_days = 10

"""
定义日志
"""

# logging
today = date.today()
log_dir = sys.path[0]
log_file = log_dir + "/aliyun-ddns-" + str(today) + ".log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
    datefmt="%Y-%m-%dT%H:%M:%SZ%z",
    filename=log_file,
    filemode='a')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter(
    '%(asctime)s  %(filename)s : %(levelname)s  %(message)s', "%Y-%m-%dT%H:%M:%SZ%z")
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
for root, dirs, files in os.walk(log_dir):
    for name in files:
        if ".log" in name:
            _log_file = os.path.join(root, name)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(_log_file))
            if datetime.now() - file_mtime > timedelta(days=logs_keep_days):
                os.remove(_log_file)

"""
获取域名的解析信息
"""


def check_records(dns_domain):
    clt = client.AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')
    request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    request.set_DomainName(dns_domain)
    request.set_accept_format(rc_format)
    result = clt.do_action_with_exception(request).decode('utf-8')
    result = json.JSONDecoder().decode(result)
    return result


"""
根据域名解析记录ID查询上一次的IP记录
"""


def get_old_ip(_record_id):
    clt = client.AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')
    request = DescribeDomainRecordInfoRequest.DescribeDomainRecordInfoRequest()
    request.set_RecordId(_record_id)
    request.set_accept_format(rc_format)
    result = clt.do_action_with_exception(request)
    result = json.JSONDecoder().decode(result.decode('utf-8'))
    result = result['Value']
    return result


"""
更新阿里云域名解析记录信息
"""


def update_dns(dns_rr, dns_type, dns_value, dns_record_id, dns_ttl, dns_format):
    clt = client.AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')
    request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    request.set_RR(dns_rr)
    request.set_Type(dns_type)
    request.set_Value(dns_value)
    request.set_RecordId(dns_record_id)
    request.set_TTL(dns_ttl)
    request.set_accept_format(dns_format)
    result = clt.do_action_with_exception(request)
    return result


"""
通过 myip.ipip.net 获取当前主机的外网IP
"""


def get_my_public_ip():
    #    get_ip_method = os.popen('curl -m 30 -s myip.ipip.net')
    #    get_ip_responses = get_ip_method.readlines()[0]
    get_ip_method = requests.get('http://myip.ipip.net')
    get_ip_responses = get_ip_method.text
    get_ip_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
    get_ip_value = get_ip_pattern.findall(get_ip_responses)[0]
    return get_ip_value


if __name__ == '__main__':
    # 获取当前公网的IP
    public_ip = get_my_public_ip()
    logging.info("当前公网IP: %s", public_ip)

    dns_records = check_records(rc_domain)
    for rc_rr in rc_rr_list:
        # 之前的解析记录
        old_ip = ""
        record_id = ""
        for record in dns_records["DomainRecords"]["Record"]:
            if record["Type"] == 'A' and record["RR"] == rc_rr:
                record_id = record["RecordId"]
                logging.debug("%s.%s recordID is %s" %
                              (record["RR"], rc_domain, record_id))
                if record_id != "":
                    old_ip = get_old_ip(record_id)
                    break

        if record_id == "":
            logging.warning('警告: 在 %s 中未发现 %s, 请先添加!', rc_domain, rc_rr)
            continue

        if old_ip == public_ip:
            logging.info("域名 %s.%s 的A记录为%s,公网IP未发生改变",
                         rc_rr, rc_domain, old_ip)
        else:
            logging.info("域名 %s.%s 的A记录为%s,公网IP为%s", rc_rr,
                         rc_domain, old_ip, public_ip)
            rc_type = 'a'  # 记录类型, DDNS填写A记录
            rc_value = public_ip  # 新的解析记录值
            rc_record_id = record_id  # 记录ID
            rc_ttl = '1000'  # 解析记录有效生存时间TTL,单位:秒

            update_info = update_dns(
                rc_rr, rc_type, rc_value, rc_record_id, rc_ttl, rc_format)
            logging.info("更新信息: %s", update_info)
            if update_info:
                logging.info("公网IP更新成功.")
            else:
                logging.error("公网IP更新失败.")
