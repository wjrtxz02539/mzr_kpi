from flask_restful import fields, marshal
from mongoengine import Document, StringField, IntField, EmbeddedDocument, BooleanField, EmbeddedDocumentListField, \
    ListField
from mongoengine.errors import NotUniqueError


class BiliUserSailingEmbedded(EmbeddedDocument):
    name = StringField(required=True)
    is_fan = BooleanField(default=False)
    number = IntField()

    marshal_fields = {
        'name': fields.String,
        'is_fan': fields.Boolean,
        'number': fields.Integer
    }

    @classmethod
    def from_cardbg(cls, cardbg: dict) -> 'BiliUserSailingEmbedded':
        sailing = BiliUserSailingEmbedded()
        sailing.name = cardbg['name']
        if cardbg.get('fan', {}).get('is_fan', 0) == 1:
            sailing.is_fan = True
            sailing.number = cardbg['fan']['number']
        return sailing

    def to_dict(self) -> dict:
        return marshal(self, self.marshal_fields)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


class BiliUser(Document):
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
        'user_id': fields.Integer,
        'username': fields.String,
        'avatar': fields.String,
        'sex': fields.Integer,
        'sign': fields.String,
        'level': fields.Integer,
        'vip': fields.Integer,
        'sailings': fields.List(fields.Nested(BiliUserSailingEmbedded.marshal_fields)),
        'pendants': fields.List(fields.String)
    }

    meta = {
        'collection': 'bili_user',
        'index_background': True,
        'strict': False,
        'indexes': [
            {
                'fields': ['user_id'],
                'unique': True
            },
            'username'
        ]
    }

    @staticmethod
    def parse_sex(sex: str) -> int:
        if sex == '女':
            return 0
        elif sex == '男':
            return 1
        else:
            return 2

    @classmethod
    def trans_member(cls, member_data: dict) -> dict:
        sailing = None
        cardbg = member_data['user_sailing'].get('cardbg')
        pendant = member_data['pendant'].get('name', '')
        if cardbg is not None:
            sailing = BiliUserSailingEmbedded.from_cardbg(cardbg)
        data = {
            'user_id': member_data['mid'],
            'username': member_data['uname'],
            'sex': cls.parse_sex(member_data['sex']),
            'sign': member_data['sign'],
            'level': member_data['level_info']['current_level'],
            'vip': member_data['vip']['vipType'],
            'avatar': member_data['avatar'],
            'sailings': [],
            'pendants': []
        }
        if sailing is not None:
            data['sailings'].append(sailing)
        if pendant != '':
            data['pendants'].append(pendant)

        return data

    @classmethod
    def from_dict(cls, member_data: dict) -> 'BiliUser':
        try:
            sailing = None
            cardbg = member_data['user_sailing'].get('cardbg')
            pendant = member_data['pendant'].get('name', '')
            if cardbg is not None:
                sailing = BiliUserSailingEmbedded.from_cardbg(cardbg)
            document = cls.objects(user_id=member_data['mid']).first()
            if document is not None:
                if sailing is not None and sailing not in document.sailings:
                    document.sailings.append(sailing)
                if pendant != '' and pendant not in document.pendants:
                    document.pendants.append(pendant)
                if document.avatar is None:
                    document.avatar = member_data['avatar']
                return document.save()

            try:
                document = cls(user_id=member_data['mid'], username=member_data['uname'],
                               sex=cls.parse_sex(member_data['sex']), sign=member_data['sign'],
                               level=member_data['level_info']['current_level'],
                               vip=member_data['vip']['vipType'], avatar=member_data['avatar'])
                if sailing is not None:
                    document.sailings.append(sailing)
                if pendant != '':
                    document.pendants.append(pendant)
                return document.save()
            except NotUniqueError:
                document = cls.objects(user_id=member_data['mid']).first()
                if sailing is not None and sailing not in document.sailings:
                    document.sailings.append(sailing)
                if pendant != '' and pendant not in document.pendants:
                    document.pendants.append(pendant)
                if document.avatar is None:
                    document.avatar = member_data['avatar']
                return document.save()
        except KeyError as err:
            print('{0}\n{1}'.format(err, member_data))

    def to_dict(self) -> dict:
        return marshal(self, self.marshal_fields)
