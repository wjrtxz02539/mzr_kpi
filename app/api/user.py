from functools import reduce
from flask_restful import Resource, reqparse
from mongoengine import Q
from .api import api

from ..bili import BiliUser
from ..tools import make_pagination


class User(Resource):
    def get(self, user_id: str = None):
        if user_id is not None:
            document = BiliUser.objects(user_id=user_id).first()
            if document is None:
                return 'User id not found', 404
            return document.to_dict()

        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='用户名')
        parser.add_argument('sex', type=int, help='性别')
        parser.add_argument('order_by', type=str, default='user_id', help='排序')
        parser.add_argument('sign', type=str, help='签名')
        parser.add_argument('max_level', type=int, help='最大用户等级')
        parser.add_argument('min_level', type=int, help='最小用户等级')
        parser.add_argument('vip', type=int, help='会员')
        parser.add_argument('size', type=int, help='分页大小', default=10)
        parser.add_argument('start', type=int, help='分页起始', default=0)

        args = parser.parse_args()

        query_list = []
        if args['username'] is not None:
            query_list.append(Q(username__icontains=args['username']))
        if args['sex'] is not None:
            query_list.append(Q(sex=args['sex']))
        if args['sign'] is not None:
            query_list.append(Q(sign__icontains=args['sign']))
        if args['max_level'] is not None:
            query_list.append(Q(level__lte=args['max_level']))
        if args['min_level'] is not None:
            query_list.append(Q(level__gte=args['min_level']))
        if args['vip'] is not None:
            query_list.append(Q(vip=args['vip']))

        if len(query_list) > 0:
            query = reduce(lambda x, y: x & y, query_list)
        else:
            query = None

        cursor = BiliUser.objects(query).limit(args['size']).skip(args['start']).order_by(args['order_by'])

        return make_pagination(data=list(map(lambda x: x.to_dict(), cursor)), total=cursor.count(), start=args['start'],
                               size=args['size'])


api.add_resource(User, '/user', '/user/<string:user_id>')
