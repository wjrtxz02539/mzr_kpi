import arrow
from functools import reduce
from flask_restful import Resource, reqparse
from mongoengine import Q
from .api import api

from ..bili import BiliReply
from ..tools import make_pagination


def get_reply_query():
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, help='用户ID')
    parser.add_argument('up_id', type=int, help='UP主ID')
    parser.add_argument('thread_id', type=int, help='版面ID')
    parser.add_argument('floor', type=int, help='楼层')
    parser.add_argument('start_time', type=str, help='起始时间')
    parser.add_argument('end_time', type=str, help='截至时间')
    parser.add_argument('content', type=str, help='内容')
    parser.add_argument('device', type=str, help='设备')
    parser.add_argument('has_replies', type=bool, help='是否有回复')
    parser.add_argument('dialog', type=int, help='会话ID')
    parser.add_argument('order_by', type=str, default='-time', help='排序')
    parser.add_argument('size', type=int, help='分页大小', default=10)
    parser.add_argument('start', type=int, help='分页起始', default=0)

    args = parser.parse_args()

    query_list = []
    if args['user_id'] is not None:
        query_list.append(Q(user_id=args['user_id']))
    if args['up_id'] is not None:
        query_list.append(Q(up_id=args['up_id']))
    if args['thread_id'] is not None:
        query_list.append(Q(thread_id=args['thread_id']))
    if args['floor'] is not None:
        query_list.append(Q(floor=args['floor']))
    if args['start_time'] is not None:
        start_time = arrow.get(args['start_time']).naive
        query_list.append(Q(time__gte=start_time))
    if args['end_time'] is not None:
        end_time = arrow.get(args['end_time']).naive
        query_list.append(Q(time__lte=end_time))
    if args['content'] is not None:
        query_list.append(Q(content__icontains=args['content']))
    if args['has_replies'] is not None:
        if args['has_replies']:
            query_list.append(Q(replies_count__gt=0))
        else:
            query_list.append(Q(replies__size=0))
    if args['dialog'] is not None:
        query_list.append(Q(dialog=args['dialog']))

    if len(query_list) > 0:
        query = reduce(lambda x, y: x & y, query_list)
    else:
        query = None

    return args, query


class Reply(Resource):
    def get(self, reply_id: str = None):
        if reply_id is not None:
            document = BiliReply.objects(reply_id=reply_id).first()
            if document is None:
                return 'Reply not found.', 404
            return document.to_dict()

        args, query = get_reply_query()
        cursor = BiliReply.objects(query).limit(args['size']).skip(args['start']).order_by(args['order_by'])

        result = list(map(lambda x: x.to_dict(), cursor))

        return make_pagination(data=result, total=cursor.count(), start=args['start'],
                               size=args['size'])


class ReplyTag(Resource):
    def get(self, field: str):
        args, query = get_reply_query()
        if field in ('user.sailings.name'):
            cursor = BiliReply.objects(query).aggregate([
                {
                    "$unwind": {
                        "path": "$user.sailings",
                        "includeArrayIndex": "arrayIndex",
                        "preserveNullAndEmptyArrays": False
                    }
                },
                {
                    "$group": {
                        "_id": "$user.sailings.name",
                        "count": {
                            "$sum": 1.0
                        }
                    }
                }
            ])
            result = map(lambda x: {'value': x['_id'], 'count': x['count']}, cursor)
        else:
            data = BiliReply.objects(query).item_frequencies(field)
            result = []
            for k, v in data.items():
                result.append({'value': k,
                               'count': v})
        return sorted(result, key=lambda x: x['count'], reverse=True)


class ReplyDateHistogram(Resource):
    def get(self):
        args, query = get_reply_query()
        start_time = args.get('start_time', None)
        end_time = args.get('end_time', None)
        if start_time is None or end_time is None:
            return 'Must assign param start_time and end_time', 400

        start_time = arrow.get(start_time)
        end_time = arrow.get(end_time)

        time_range = end_time - start_time

        thread_id = args.get('thread_id', None)
        if thread_id is not None:
            first = BiliReply.objects(thread_id=thread_id).order_by('time').first()
            last = BiliReply.objects(thread_id=thread_id).order_by('-time').first()
            if first is None:
                return []
            reply_time_range = arrow.get(last.time) - arrow.get(first.time)
            time_range = min(time_range, reply_time_range)

        group = {
            'year': {'$year': '$time'},
            'month': {'$month': '$time'},
            'day': {'$dayOfMonth': '$time'}
        }
        if time_range.days < 1 and time_range.seconds < 3600:
            group['seconds'] = {'$seconds': '$time'}
        if time_range.days < 1:
            group['minutes'] = {'$minutes': '$time'}
        if time_range.days < 15:
            group['hour'] = {'$hour': '$time'}

        pipeline = [
            {'$match': query.to_query(BiliReply)},
            {'$group': {'_id': group, 'count': {'$sum': 1}}},
        ]

        result = []
        for item in BiliReply.objects.aggregate(pipeline):
            result.append({'time': item['_id'], 'count': item['count']})

        return result


api.add_resource(Reply, '/reply', '/reply/<string:reply_id>')
api.add_resource(ReplyTag, '/reply/tag/<string:field>')
api.add_resource(ReplyDateHistogram, '/reply/date_histogram')
