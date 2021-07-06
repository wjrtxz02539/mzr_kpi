import arrow
from functools import reduce
from flask_restful import Resource, reqparse
from mongoengine import Q
from .api import api

from ..tools import make_pagination
from ..bili import BiliDynamic


class Dynamic(Resource):
    def get(self, dynamic_id: str = None):
        if dynamic_id is not None:
            document = BiliDynamic.objects(dynamic_id=dynamic_id).first()
            if document is None:
                return 'Dynamic id not found', 404
            return document.to_dict()

        parser = reqparse.RequestParser()
        parser.add_argument('dynamic_type', type=int, help='动态类型')
        parser.add_argument('user_id', type=int, help='用户id')
        parser.add_argument('thread_id', type=int, help='版面id')
        parser.add_argument('description', type=str, help='动态内容')
        parser.add_argument('order_by', type=str, default='-time', help='排序')
        parser.add_argument('start_time', type=str, help='起始时间')
        parser.add_argument('end_time', type=str, help='截止时间')
        parser.add_argument('size', type=int, help='分页大小', default=10)
        parser.add_argument('start', type=int, help='分页起始', default=0)

        args = parser.parse_args()

        query_list = []
        if args['dynamic_type'] is not None:
            query_list.append(Q(dynamic_type=args['dynamic_type']))
        if args['user_id'] is not None:
            query_list.append(Q(user_id=args['user_id']))
        if args['thread_id'] is not None:
            query_list.append(Q(thread_id=args['thread_id']))
        if args['description'] is not None:
            query_list.append(Q(description__icontains=args['description']))
        if args['start_time'] is not None:
            start_time = arrow.get(args['start_time']).naive
            query_list.append(Q(time__gte=start_time))
        if args['end_time'] is not None:
            end_time = arrow.get(args['end_time']).naive
            query_list.append(Q(time__lte=end_time))

        if len(query_list) > 0:
            query = reduce(lambda x, y: x & y, query_list)
        else:
            query = None

        cursor = BiliDynamic.objects(query).limit(args['size']).skip(args['start']).order_by(args['order_by'])

        return make_pagination(data=list(map(lambda x: x.to_dict(), cursor)), total=cursor.count(), start=args['start'],
                               size=args['size'])


api.add_resource(Dynamic, '/dynamic', '/dynamic/<string:dynamic_id>')
