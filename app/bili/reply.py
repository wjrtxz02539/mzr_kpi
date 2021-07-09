import re
import json
from math import ceil
from datetime import datetime

from flask_restful import fields, marshal
from mongoengine import Document, IntField, StringField, DateTimeField, ListField, BooleanField, EmbeddedDocument, \
    EmbeddedDocumentField, EmbeddedDocumentListField

from .member import BiliUser, BiliUserSailingEmbedded
from ..logger import bili_logger
from ..tools import FlaskDateTimeField
from .tools import get
from .control import Control


class BiliReplyUserEmbedded(EmbeddedDocument):
    user_id = IntField(required=True)
    username = StringField(required=True)
    avatar = StringField()
    sex = IntField(required=True)
    sign = StringField()
    level = IntField(required=True)
    vip = IntField()
    sailings = EmbeddedDocumentListField(BiliUserSailingEmbedded)
    pendants = ListField(StringField())

    marshal_fields = {
        **BiliUser.marshal_fields
    }

    @classmethod
    def from_dict(cls, user: dict) -> 'BiliReplyUserEmbedded':
        document = cls()
        document.user_id = user['user_id']
        document.username = user['username']
        document.avatar = user['avatar']
        document.sex = user['sex']
        document.sign = user['sign']
        document.level = user['level']
        document.vip = user['vip']
        document.sailings = user['sailings']
        document.pendants = user['pendants']
        return document


class BiliReplyMiniUserEmbedded(EmbeddedDocument):
    user_id = IntField(required=True)
    username = StringField(required=True)

    marshal_fields = {
        'user_id': fields.String,
        'username': fields.String
    }

    @classmethod
    def from_user(cls, user: BiliUser) -> 'BiliReplyMiniUserEmbedded':
        document = cls()
        document.user_id = user.user_id
        document.username = user.username
        return document


class BiliReply(Document):
    logger = bili_logger.getChild('Reply')

    up_id = IntField()
    reply_id = IntField(required=True)
    thread_id = IntField(required=True)
    floor = IntField(required=True)
    root = IntField()
    parent = IntField()
    dialog = IntField()
    time = DateTimeField(required=True)
    like = IntField()
    user_id = IntField(required=True)
    user = EmbeddedDocumentField(BiliReplyUserEmbedded, required=True)
    up = EmbeddedDocumentField(BiliReplyMiniUserEmbedded, required=True)
    content = StringField(required=True)
    device = StringField(default='')
    plat = IntField()  # 1=Web, 2=Android, 3=iOS
    replies_count = IntField()
    has_folded = BooleanField()
    is_folded = BooleanField()
    invisible = BooleanField()

    marshal_fields = {
        'up_id': fields.Integer,
        'reply_id': fields.Integer,
        'thread_id': fields.Integer,
        'floor': fields.Integer,
        'root': fields.Integer,
        'parent': fields.Integer,
        'dialog': fields.Integer,
        'time': FlaskDateTimeField(timezone='UTC'),
        'like': fields.Integer,
        'user_id': fields.Integer,
        'content': fields.String,
        'device': fields.String,
        'plat': fields.Integer,
        'replies_count': fields.Integer,
        'has_folded': fields.Boolean,
        'is_folded': fields.Boolean,
        'invisible': fields.Boolean,
        'user': fields.Nested(BiliReplyUserEmbedded.marshal_fields),
        'up': fields.Nested(BiliReplyMiniUserEmbedded.marshal_fields)
    }

    meta = {
        'collection': 'bili_reply',
        'index_background': True,
        'strict': False,
        'indexes': [
            {
                'fields': ['reply_id'],
                'unique': True
            }
        ]
    }

    pattern = re.compile(r'jQuery\d*_\d*\((.*)\)')

    reply_url = 'https://api.bilibili.com/x/v2/reply/reply'
    headers = {
        'referer': 'https://t.bilibili.com/'
    }

    def walk_sub_replies(self, thread_type: int, up: BiliUser, root: int, page: int):
        Control.running_replies += 1
        params = {
            'callback': 'jQuery33109926635572966458_1624466178116',
            'jsonp': 'jsonp',
            'pn': page,
            'ps': 20,
            'root': root,
            'type': thread_type,
            'oid': self.thread_id
        }
        res = get(self.logger, self.reply_url, params=params, headers=self.headers)
        try:
            raw_data = json.loads(self.pattern.findall(res.text)[0])
            code = raw_data['code']
            data = raw_data['data']
            if code != 0:
                self.logger.error('{0}: {1}'.format(code, params))
                return
            if data['replies'] is not None:
                for reply in data['replies']:
                    BiliReply.from_dict(thread_type, reply, up=up)
        except (IndexError, KeyError) as err:
            self.logger.error('Failed to walk sub replies. {0}\n{1}'.format(err, res.text))
            return
        finally:
            Control.running_replies -= 1

    @classmethod
    def from_dict(cls, thread_type: int, reply_data: dict, up: BiliUser) -> 'BiliReply':
        try:
            member = BiliUser.trans_member(reply_data['member'])

            document = cls(reply_id=reply_data['rpid'], floor=reply_data.get('floor', -1), root=reply_data['root'],
                           thread_id=reply_data['oid'], up_id=up.user_id,
                           parent=reply_data['parent'], dialog=reply_data['dialog'],
                           time=datetime.fromtimestamp(reply_data['ctime']), like=reply_data['like'],
                           user_id=member['user_id'], content=reply_data['content']['message'],
                           device=reply_data['content']['device'], plat=reply_data['content']['plat'],
                           has_folded=reply_data['folder']['has_folded'],
                           is_folded=reply_data['folder']['is_folded'],
                           invisible=reply_data['invisible'])

            document.user = BiliReplyUserEmbedded.from_dict(member)
            document.up = BiliReplyMiniUserEmbedded.from_user(up)

            document.replies_count = reply_data.get('rcount', 0)
            replies = reply_data['replies']
            if document.replies_count > 0:
                if replies is None or (document.replies_count > len(replies)):
                    for page in range(1, ceil(document.replies_count / 20) + 1):
                        Control.wait_for_replies()
                        try:
                            Control.pool.spawn(document.walk_sub_replies, thread_type, up, document.reply_id, page)
                        except Exception as err:
                            cls.logger.error(err)
                else:
                    for item in replies:
                        cls.from_dict(thread_type=thread_type, reply_data=item, up=up)
            try:
                old = cls.objects(reply_id=document.reply_id).first()
                if old is not None:
                    old.update(like=document.like, replies_count=document.replies_count, plat=document.plat)
                else:
                    document.save()
            except Exception as err:
                cls.logger.error(err)
            return document
        except KeyError as err:
            reply_data.pop('replies')
            cls.logger.error('{0}\n{1}'.format(err, reply_data))

    def to_dict(self) -> dict:
        data = marshal(self, self.marshal_fields)
        return data
