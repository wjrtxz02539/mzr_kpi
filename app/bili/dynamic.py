import json
import arrow
import re
from datetime import datetime
from typing import Optional
from traceback import format_exc

from flask_restful import fields, marshal
from mongoengine import Document, StringField, IntField, DateTimeField

from .reply import BiliReply
from .member import BiliUser
from .run_record import BiliDynamicRunRecord
from .tools import get
from ..tools import FlaskDateTimeField
from ..logger import bili_logger
from .control import Control


class BiliDynamic(Document):
    logger = bili_logger.getChild('Dynamic')

    dynamic_type = IntField(required=True)
    orig_dy_id = IntField()
    orig_type = IntField()
    video_id = StringField()
    dynamic_id = IntField()
    user_id = IntField()
    report_id = IntField()
    target_url = StringField()
    thread_id = IntField(required=True)
    description = StringField(required=True)
    time = DateTimeField(required=True)
    view = IntField(required=True)
    like = IntField(required=True)

    marshal_fields = {
        'dynamic_type': fields.Integer,
        'orig_dy_id': fields.Integer,
        'orig_type': fields.Integer,
        'video_id': fields.String,
        'dynamic_id': fields.Integer,
        'user_id': fields.Integer,
        'report_id': fields.Integer,
        'target_url': fields.String,
        'thread_id': fields.Integer,
        'description': fields.String,
        'time': FlaskDateTimeField(timezone='Asia/Shanghai'),
        'view': fields.Integer,
        'like': fields.Integer
    }

    meta = {
        'collection': 'bili_dynamic',
        'index_background': True,
        'strict': False,
        'indexes': [
            {
                'fields': ['dynamic_id'],
                'unique': True
            },
            'thread_id',
            'user_id'
        ]
    }

    dynamic_url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail"
    thread_type_map = {
        1: 17,
        2: 11,
        4: 17,
        8: 1,
        64: 12,
        256: 14,
        2048: 17
    }
    headers = {
        'referer': 'https://t.bilibili.com/'
    }

    thread_url = 'https://api.bilibili.com/x/v2/reply/main'

    pattern = re.compile(r'jQuery\d*_\d*\((.*)\)')

    @classmethod
    def format_base(cls, desc: dict) -> 'BiliDynamic':
        document = cls(dynamic_id=int(desc['dynamic_id_str']),
                       time=arrow.get(desc['timestamp']).naive,
                       user_id=desc['uid'],
                       view=desc['view'],
                       like=desc['like'])

        return document

    @classmethod
    def format_retweet(cls, source: dict) -> 'BiliDynamic':
        desc = source['desc']
        document = cls.format_base(desc)

        document.dynamic_type = 1
        document.report_id = int(desc['rid_str'])
        document.thread_id = document.dynamic_id
        document.orig_dy_id = int(desc['orig_dy_id_str'])
        document.orig_dy_type = desc['orig_type']

        card = json.loads(source['card'])
        document.description = card['item']['content']

        return document.save()

    @classmethod
    def format_normal(cls, source: dict) -> 'BiliDynamic':
        desc = source['desc']
        document = cls.format_base(desc)

        document.dynamic_type = 2
        document.report_id = int(desc['rid_str'])
        document.thread_id = document.report_id

        card = json.loads(source['card'])
        document.description = card['item']['description']

        return document.save()

    @classmethod
    def format_normal2(cls, source: dict) -> 'BiliDynamic':
        desc = source['desc']
        document = cls.format_base(desc)

        document.dynamic_type = 4
        document.report_id = int(desc['rid_str'])
        document.thread_id = document.dynamic_id

        card = json.loads(source['card'])
        document.description = card['item']['content']

        return document.save()

    @classmethod
    def format_video(cls, source: dict) -> 'BiliDynamic':
        desc = source['desc']
        document = cls.format_base(desc)

        document.dynamic_type = 8
        document.report_id = int(desc['rid_str'])
        document.thread_id = document.report_id
        document.video_id = desc['bvid']

        card = json.loads(source['card'])
        document.description = card['desc']

        return document.save()

    @classmethod
    def format_report(cls, source: dict) -> 'BiliDynamic':
        desc = source['desc']
        document = cls.format_base(desc)

        document.dynamic_type = 64
        document.report_id = int(desc['rid_str'])
        document.thread_id = document.report_id

        card = json.loads(source['card'])
        document.description = card['summary']

        return document.save()

    @classmethod
    def format_topic(cls, source: dict) -> 'BiliDynamic':
        desc = source['desc']
        document = cls.format_base(desc)

        document.dynamic_type = 2048
        document.report_id = int(desc['rid_str'])
        document.thread_id = document.dynamic_id

        card = json.loads(source['card'])
        document.description = card['vest']['content']
        document.target_url = card['sketch']['target_url']

        return document.save()

    @classmethod
    def format_music(cls, source: dict) -> 'BiliDynamic':
        desc = source['desc']
        document = cls.format_base(desc)

        document.dynamic_type = 256
        document.report_id = int(desc['rid_str'])
        document.thread_id = document.report_id

        card = json.loads(source['card'])
        document.description = card['intro']

        return document.save()

    @classmethod
    def format(cls, source: dict) -> 'BiliDynamic':
        dynamic_type = source['desc']['type']
        if dynamic_type == 1:
            return cls.format_retweet(source)
        elif dynamic_type == 2:
            return cls.format_normal(source)
        elif dynamic_type == 4:
            return cls.format_normal2(source)
        elif dynamic_type == 8:
            return cls.format_video(source)
        elif dynamic_type == 64:
            return cls.format_report(source)
        elif dynamic_type == 256:
            return cls.format_music(source)
        elif dynamic_type == 2048:
            return cls.format_topic(source)
        else:
            message = 'Unknown dynamic type [{0}] for {1}'.format(dynamic_type, source['desc']['dynamic_id_str'])
            cls.logger.error(message)
            raise Exception(message)

    @property
    def thread_type(self) -> int:
        return self.thread_type_map[self.dynamic_type]

    @property
    def last_run_record(self) -> Optional[BiliDynamicRunRecord]:
        return BiliDynamicRunRecord.objects(dynamic_id=self.dynamic_id).order_by('-_id').first()

    @property
    def last_run_time(self) -> datetime:
        if self.last_run_record is not None:
            return self.last_run_record.start_time
        return datetime.fromtimestamp(0)

    @classmethod
    def from_dynamic_dict(cls, dynamic_dict: dict) -> 'BiliDynamic':
        dynamic_id = dynamic_dict['desc']['dynamic_id_str']
        document = cls.objects(dynamic_id=dynamic_id).first()

        if document is not None:
            document.view = dynamic_dict['desc']['view']
            document.like = dynamic_dict['desc']['like']
            return document.save()

        document = cls.format(dynamic_dict)
        return document.save()

    def _walk(self, logger, params: dict):
        res = get(logger, self.thread_url, params=params, headers=self.headers)
        up = BiliUser.objects(user_id=self.user_id).first()
        try:
            data = json.loads(self.pattern.findall(res.text)[0])
        except IndexError or KeyError:
            logger.error(res.text)
            return
        if data['code'] != 0:
            logger.error('{0}: {1}'.format(data['code'], params))
            return
        data = data['data']
        if data['replies'] is not None:
            for reply in data['replies']:
                BiliReply.from_dict(self.thread_type, reply, up=up)

    def walk(self, force: bool = False) -> None:
        logger = self.logger.getChild(str(self.dynamic_id))
        try:
            base_params = {
                'callback': 'jQuery33109926635572966458_1624466178116',
                'jsonp': 'jsonp',
                'mode': 2,
                'plat': 1,
                'type': self.thread_type,
                'oid': self.thread_id
            }

            res = get(logger, self.thread_url, params={'next': 0, **base_params}, headers=self.headers)
            try:
                data = json.loads(self.pattern.findall(res.text)[0])['data']
                cursor = data['cursor']
                total = cursor['all_count']
            except (IndexError, KeyError) as err:
                logger.error('Get reply status failed. {0}\n{1}'.format(err, res.text))
                return
            if not force and (self.last_run_record is not None and self.last_run_record.end_time is not None):
                if int(total) == int(self.last_run_record.total):
                    logger.info('Skip because no new comment')
                    return

            logger.info('Start')

            if self.last_run_record is not None and self.last_run_record.end_time is None:
                run_record = self.last_run_record
            else:
                run_record = BiliDynamicRunRecord(dynamic_id=self.dynamic_id, view=self.view, like=self.like).save()
                run_record.total = total
                run_record.save()

            if run_record.progress == -1:
                next_pos = run_record.total
            else:
                next_pos = run_record.progress

            try:
                up = BiliUser.objects(user_id=self.user_id).first()
                if up is None:
                    up = BiliUser.from_user_id(self.user_id)
                while not cursor['is_end']:
                    params = {'next': next_pos, **base_params}
                    res = get(logger, self.thread_url, params=params, headers=self.headers)
                    try:
                        raw_data = json.loads(self.pattern.findall(res.text)[0])
                        code = raw_data['code']
                        data = raw_data['data']
                        cursor = data['cursor']
                    except (IndexError, KeyError) as err:
                        logger.error('Walk reply failed. {0}\n{1}'.format(err, res.text))
                        return
                    if code != 0:
                        logger.error('{0}: {1}'.format(code, params))
                        return
                    if data['replies'] is not None:
                        for reply in data['replies']:
                            BiliReply.from_dict(self.thread_type, reply, up=up)
                    next_pos = cursor['next']
            except Exception as err:
                logger.error('{0}: {1}\{2}'.format(err.__class__, err, format_exc()))
                return

            run_record.progress = 0
            run_record.end_time = datetime.utcnow()
            run_record.save()
            logger.info('Finished: {0}'.format(run_record.total))
        except Exception as err:
            logger.error(err)
        finally:
            Control.running_dynamic.remove(self.dynamic_id)

    def to_dict(self) -> dict:
        return marshal(self, self.marshal_fields)

    def to_dict_with_reply_stats(self) -> dict:
        data = self.to_dict()
        data['reply'] = {
            'total': BiliReply.objects(thread_id=self.thread_id).count()
        }
        return data
