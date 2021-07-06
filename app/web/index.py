from cachetools import cached, TTLCache
from flask import render_template
from .blueprint import web
from ..bili import BiliDynamic, BiliUser, ProxyPool


@cached(TTLCache(maxsize=8, ttl=20))
def get_user_stats(user_id) -> dict:
    return {
        'user': BiliUser.objects(user_id=user_id).first().to_dict(),
        'dynamic_total': BiliDynamic.objects(user_id=user_id).count()
    }


@cached(TTLCache(maxsize=8, ttl=20))
def get_total(query_class) -> int:
    return query_class.objects.count()


@web.route('/')
def index():
    data = {
        'dynamic_total': get_total(BiliDynamic),
        'user_total': get_total(BiliUser),
        'show_list': [
            get_user_stats(27534330),
            get_user_stats(401742377),
            get_user_stats(500615835),
            get_user_stats(256667467),
            get_user_stats(161775300)
        ],
        'proxy_count': ProxyPool.count()
    }
    return render_template('index.html', **data)
