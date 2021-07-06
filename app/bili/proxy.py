import requests
from time import sleep
from traceback import format_exc
from urllib.parse import urljoin

from ..logger import bili_logger
from .control import Control

logger = bili_logger.getChild('ProxyPool')


class ProxyPool:
    @classmethod
    def get_proxy(cls) -> dict:
        try:
            res = requests.get(urljoin(Control.proxy_pool_url, '/get/'))
            data = res.json()
            try:
                proxy = 'http://{0}'.format(data['proxy'])
            except KeyError:
                if 'src' in data and data['src'] == 'no proxy':
                    sleep(3)
                    logger.warn('Not enough proxy')
                else:
                    logger.error(format_exc())
                return cls.get_proxy()
        except Exception:
            logger.warn('Unknown proxy error')
            return cls.get_proxy()
        return {'http': proxy, 'https': proxy}

    @classmethod
    def delete_proxy(cls, proxies: dict):
        proxy = proxies['http'].removeprefix('http://')
        requests.get(urljoin(Control.proxy_pool_url, '/delete/'), params={'proxy': proxy})

    @classmethod
    def count(cls, https: bool = False) -> int:
        res = requests.get(urljoin(Control.proxy_pool_url, '/count/')).json()
        if https:
            return res.get('count').get('https', 0)
        return res.get('count').get('total', 0)
