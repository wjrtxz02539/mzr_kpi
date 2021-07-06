import os
import pytz
from dateutil.parser import parse as date_parse
from flask_restful.fields import Raw, MarshallingException
from datetime import datetime


def fix_timezone(time_object: datetime, timezone: str = None) -> datetime:
    """
    将时间对象转为环境变量设置或指定的时区。
    注意：原本无时区数据的时间对象的转换前默认时区为UTC

    :param time_object: 时间对象
    :param timezone: 指定时区
    :return:
    """
    if timezone is None:
        timezone = os.getenv('TZ', 'Asia/Shanghai')
    if time_object.tzinfo is None:
        # 无时区数据的对象，默认将其时区改为UTC
        time_object = time_object.replace(tzinfo=pytz.timezone('UTC'))
    return time_object.astimezone(pytz.timezone(timezone))


def fix_timezone_and_format(time_object: datetime, timezone: str = None, format='%Y-%m-%d %H:%M:%S') -> str:
    """
    将时间对象转为环境变量设置或指定的时区，并按指定格式输出
    注意：原本无时区数据的时间对象的转换前默认时区为UTC

    :param time_object: 时间对象
    :param timezone: 指定时区
    :param format: 时间格式
    :return:
    """
    time_object = fix_timezone(time_object, timezone=timezone)
    return time_object.strftime(format)


class FlaskDateTimeField(Raw):
    def __init__(self, timezone=None, time_format='%Y-%m-%d %H:%M:%S', **kwargs):
        super(FlaskDateTimeField, self).__init__(**kwargs)
        if timezone is None:
            self.timezone = os.getenv('TZ', 'Asia/Shanghai')
        else:
            self.timezone = timezone
        self.time_format = time_format

    def format(self, value: datetime):
        try:
            if isinstance(value, datetime):
                return fix_timezone_and_format(value, timezone=self.timezone, format=self.time_format)
                # return value.strftime(self.time_format)
            elif isinstance(value, str):
                value = date_parse(value)
                return fix_timezone_and_format(value, timezone=self.timezone, format=self.time_format)
                # return value.strftime(self.time_format)
            else:
                raise MarshallingException(
                    'Unsupported date format %s' % type(value)
                )
        except AttributeError as ae:
            raise MarshallingException(ae)
        except pytz.exceptions.UnknownTimeZoneError as ae:
            raise MarshallingException(ae)


def make_pagination(data: list, total: int, start: int, size: int, meta: dict = None) -> dict:
    if meta is None:
        meta = {}
    result = {
        'data': data,
        'pagination': {
            'total': total,
            'start': start,
            'size': size
        },
        'meta': meta
    }

    return result
