import arrow

from .dynamic import BiliDynamic
from ..logger import bili_logger
from .tools import get
from .control import Control

space_history_url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history'
space_logger = bili_logger.getChild('Space')


def walk_space(user_id: str, offset_dynamic_id: str = '0', skip: int = 0, max_depth: int = None,
               last_days: int = None, force: bool = False):
    logger = space_logger.getChild(user_id)
    params = {
        'host_uid': user_id,
        'offset_dynamic_id': offset_dynamic_id,
        'need_top': 1,
        'platform': 'web'
    }
    res = get(space_logger, space_history_url, params)

    data = {}
    cards = []
    try:
        data = res.json()['data']
        cards = data['cards']
    except KeyError as err:
        logger.error('Failed to get space detail. {0}\n{1}'.format(err, res.text))

    last_dynamic_id = '0'
    dynamic_list = []
    for card in cards:
        temp = BiliDynamic.from_dynamic_dict(card)
        logger.info('Found dynamic {0} at {1}.'.format(temp.dynamic_id, temp.time))
        dynamic_list.append(temp)
        last_dynamic_id = str(temp.dynamic_id)

    oldest_time = None
    if last_days is not None:
        oldest_time = arrow.utcnow().shift(days=-last_days).naive
    for dynamic in sorted(dynamic_list, key=lambda x: x.time, reverse=True):
        if skip > 0:
            skip -= 1
            continue
        if max_depth is not None:
            if max_depth >= 0:
                max_depth -= 1
            else:
                logger.info('Hit depth limit')
                return

        if oldest_time is not None:
            if dynamic.time < oldest_time:
                logger.info('Hit time limit')
                return

        # 等待空位
        Control.wait_for_dynamic()

        # 检测是否已经执行
        if dynamic.dynamic_id in Control.running_dynamic:
            logger.info('Skip because already running')
            continue

        Control.running_dynamic.add(dynamic.dynamic_id)
        Control.pool.spawn(dynamic.walk, force=force)

    logger.info('Walk complete, wait for dynamic.')
    Control.wait_for_dynamic()

    if data['has_more'] == 1:
        walk_space(user_id, last_dynamic_id, skip=skip, max_depth=max_depth, last_days=last_days, force=force)
