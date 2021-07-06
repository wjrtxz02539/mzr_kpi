from flask import render_template
from .blueprint import web
from ..bili import BiliDynamic, BiliUser, BiliReply


@web.route('/user/<string:user_id>')
def user_page(user_id: str):
    user = BiliUser.objects(user_id=user_id).first()
    if user is None:
        return '用户不存在', 404
    replies = list(map(lambda x: x.to_dict(), BiliReply.objects(user_id=user_id).limit(10).order_by('-time')))
    return render_template('user.html', dynamic_total=BiliDynamic.objects(user_id=user_id).count(), user=user,
                           reply_total=BiliReply.objects(user_id=user_id).count(), replies=replies,
                           pagination_url='/api/reply', pagination_params={'user_id': user_id})
