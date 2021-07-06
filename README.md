# BiliComment

A spider for BiliBili comment.

## Spider Usage

Put `config.json` into `config` directory, and then `python . ./config/config.json`. A example config locate
at `/config/config.json.example`.

## API Usage

We use **uwsgi** to start our Web server(with very poor frontend).
`uwsgi --ini uwsgi.ini`

## ProxyPool Required

This project use [jhao104/proxy_pool](https://github.com/jhao104/proxy_pool) as a proxy pool. You need to deploy it
before start the spider.
