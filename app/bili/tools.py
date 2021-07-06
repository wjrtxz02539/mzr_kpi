import requests
from gevent import sleep
from requests.exceptions import ConnectionError, ReadTimeout
from .proxy import ProxyPool


def get(logger, url: str, params: dict = None, headers: dict = None, retry_count: int = 10) -> requests.Response:
    count = 0
    while True:
        proxies = ProxyPool.get_proxy()
        res = None
        try:
            if headers is None:
                headers = {}
            headers['Accept-Encoding'] = 'gzip'
            res = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=10)
            if res.status_code == 200:
                break
            elif res.status_code == 429:
                logger.warn('Hit rate limit.')
                sleep()

            if '412' in res.text:
                ProxyPool.delete_proxy(proxies)
                logger.debug('Delete proxies: {0}'.format(proxies))
            else:
                logger.warn('{0}: {1}'.format(res.status_code, res.text))
            if count > retry_count:
                logger.error('Retry limit exceed. URL: {0}\nParams: {1}'.format(url, params))
            count += 1
        except (ConnectionError, ReadTimeout) as err:
            ProxyPool.delete_proxy(proxies)
            logger.debug('Delete proxies: {0}'.format(proxies))
            if count > retry_count:
                logger.error('Retry limit exceed. Error: {0}\nURL: {1}\nParams: {2}'.format(err, url, params))
            count += 1
        except Exception as err:
            logger.warn('{0}: {1}\n{2}'.format(err.__class__, err.args, getattr(res, 'text', None)))
            if count > retry_count:
                logger.error('Retry limit exceed. Error: {0}\nURL: {1}\nParams: {2}'.format(err, url, params))
            count += 1
    return res
