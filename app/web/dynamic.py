from flask import render_template, request
from .blueprint import web
from ..bili import BiliDynamic, BiliUser, BiliReply, BiliDynamicRunRecord


def get_dynamic_data(dynamic: BiliDynamic) -> dict:
    size = int(request.args.get('size', 20))
    start = int(request.args.get('start', 0))
    order_by = request.args.get('order_by', '-time')
    user = BiliUser.objects(user_id=dynamic.user_id).first()
    reply_cursor = BiliReply.objects(thread_id=dynamic.thread_id).skip(start).limit(size).order_by(order_by)
    reply = {
        'total': reply_cursor.count(),
        'data': list(map(lambda x: x.to_dict(), reply_cursor))
    }
    return {'dynamic': dynamic.to_dict(), 'user': user, 'reply': reply,
            'run_record': BiliDynamicRunRecord.objects(dynamic_id=dynamic.dynamic_id).order_by('-_id').first()}


@web.route('/dynamic/<string:dynamic_id>')
def dynamic_page(dynamic_id: str = None):
    dynamic = BiliDynamic.objects(dynamic_id=dynamic_id).first()
    if dynamic is None:
        return '动态不存在', 404

    return render_template('dynamic.html', **get_dynamic_data(dynamic), pagination_url='/api/reply',
                           pagination_params={'thread_id': str(dynamic.thread_id)})


@web.route('/dynamic/thread/<string:thread_id>')
def dynamic_from_thread(thread_id: str):
    dynamic = BiliDynamic.objects(thread_id=thread_id).first()
    if dynamic is None:
        return '动态不存在', 404
    return render_template('dynamic.html', **get_dynamic_data(dynamic), pagination_url='/api/reply',
                           pagination_params={'thread_id': str(dynamic.thread_id)})


@web.route('/dynamic/user/<string:user_id>')
def dynamic_from_user(user_id: str):
    size = int(request.args.get('size', 1000))
    start = int(request.args.get('start', 0))
    order_by = request.args.get('order_by', '-time')

    user = BiliUser.objects(user_id=user_id).first()
    if user is None:
        return '用户不存在', 404

    dynamic_cursor = BiliDynamic.objects(user_id=user_id).limit(size).skip(start).order_by(order_by)
    dynamic = {
        'total': dynamic_cursor.count(),
        'data': list(map(lambda x: x.to_dict_with_reply_stats(), dynamic_cursor))
    }
    return render_template('dynamic_list.html', dynamic=dynamic, user=user.to_dict())
