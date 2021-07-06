from datetime import datetime
from flask import request
from flask_restful import fields, marshal
from mongoengine import Document, IntField, StringField, DateTimeField


class APICounter(Document):
    total = IntField(default=0)
    path = StringField(required=True)
    last_visit = DateTimeField()

    marshal_field = {
        'id': fields.String,
        'total': fields.Integer,
        'path': fields.String
    }

    meta = {
        'collection': 'api_counter',
        'index_background': True,
        'strict': False,
        'indexes': [
            {
                'fields': ['path'],
                'unique': True
            }
        ]
    }

    @classmethod
    def count(cls):
        cls._get_collection().update_one({'path': request.path},
                                         {'$inc': {'total': 1}, '$set': {'last_visit': datetime.utcnow()}},
                                         upsert=True)
        return None

    def to_dict(self) -> dict:
        return marshal(self, self.marshal_field)
