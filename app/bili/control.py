import json
from os import environ

from gevent.pool import Pool
from gevent import sleep
from mongoengine import connect
from ..logger import bili_logger


class Control:
    logger = bili_logger.getChild('Control')

    dynamic_thread: int = None
    reply_thread: int = None
    proxy_pool_url: str = None
    mongodb_url: str = None
    bili_user_id: str = None
    force: bool = None
    skip: int = 0
    last_days: int = None
    depth: int = None

    pool: Pool = None
    running_dynamic = set()
    running_replies = 0

    @classmethod
    def from_json_file(cls, path: str):
        with open(path, 'r') as f:
            data = json.load(f)
            cls.dynamic_thread = data['dynamic_thread']
            cls.reply_thread = data['reply_thread']
            cls.proxy_pool_url = data['proxy_pool_url']
            cls.mongodb_url = data['mongodb_url']
            cls.bili_user_id = data['bili_user_id']
            cls.force = data.get('force', False)
            cls.skip = data.get('skip', 0)
            cls.depth = data.get('depth', None)
            cls.last_days = data.get('last_days', None)

    @classmethod
    def from_env(cls):
        cls.mongodb_url = environ.get('MongoDB_URL', None)
        cls.proxy_pool_url = environ.get('Proxy_Pool_URL', None)

    @classmethod
    def init(cls):
        if cls.dynamic_thread is not None:
            cls.pool = Pool(size=cls.dynamic_thread + cls.reply_thread)
        if cls.mongodb_url is None:
            raise Exception('MongoDB URL is None.')
        connect(db='bili', host=cls.mongodb_url, tz_aware=False)

    @classmethod
    def wait_for_dynamic(cls):
        while len(cls.running_dynamic) >= cls.dynamic_thread:
            cls.logger.debug('Wait for dynamic: {0}'.format(cls.running_dynamic))
            sleep()

    @classmethod
    def wait_for_replies(cls):
        while cls.running_replies >= cls.reply_thread:
            cls.logger.debug('Wait for replies: {0}'.format(cls.running_replies))
            sleep()
