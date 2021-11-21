# 阿里云DNS动态解析
- 支持多解析记录
- 支持Docker

## 配置方法
### 创建配置文件 setting.yml
```bash
cp setting.yml.sample setting.yml
vi setting.yml
```

```yaml
# 阿里云 Access Key ID
access_key_id: "XXX"

# 阿里云 Access Key Secret
access_key_secret: "XXXXXX"

# 阿里云 一级域名
rc_domain: 'github.com'

# 解析记录
rc_rr_list: ['www','*.git']
```

### 使用环境变量
```
export ACCESS_KEY_ID="xxxx"
export ACCESS_KEY_SECRET="xxxxx"
export RC_DOMAIN="example.com"
export RC_RR_LIST="foo,bar"
```

## Access Key
通过[阿里云Access Key管理](https://ak-console.aliyun.com/#/accesskey), 获取access_key_id，access_key_secret。

## 添加域名解析记录
修改好你使用的一级域名，通过[阿里云域名管理](https://netcn.console.aliyun.com/core/domain/list)，添加A记录，对一级域名的解析使用记录值为‘*’，A记录可以为你的二级域名，如 www.github.com, *.git.github.com。记录值随便写 8.8.8.8，因为后面会根据实际的IP进行动态更改。

## 使用 Docker 
```bash
docker run -d --name aliyun-ddns --restart always -v $(pwd)/setting.yml:/app/setting.yml:ro firxiao/aliyun-ddns 
```

## 手动配置
### 安装 python sdk, pyaml
```
pip install aliyun-python-sdk-alidns pyaml
```

### crontab 定时运行
```
crontab -e
```
```
# Run at every 10 minute
*/10 * * * * /usr/bin/python /path_to/aliyun_ddns.py >/dev/null 2>&1
```
