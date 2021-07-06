from datetime import datetime

from flask_restful import fields
from mongoengine import Document, IntField, DateTimeField

from ..tools import FlaskDateTimeField


class BiliDynamicRunRecord(Document):
    dynamic_id = IntField(required=True)
    total = IntField()
    view = IntField()
    like = IntField()
    progress = IntField(default=-1)
    start_time = DateTimeField(default=datetime.utcnow)
    end_time = DateTimeField()

    marshal_field = {
        'dynamic_id': fields.Integer,
        'total': fields.Integer,
        'progress': fields.Integer,
        'start_time': FlaskDateTimeField(timezone='Asia/Shanghai'),
        'end_time': FlaskDateTimeField(timezone='Asia/Shanghai')
    }

    meta = {
        'collection': 'bili_dynamic_run_record',
        'index_background': True,
        'strict': False,
        'indexes': [
            {
                'fields': ['dynamic_id']
            }
        ]
    }
