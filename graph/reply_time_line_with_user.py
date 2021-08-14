import arrow
from pymongo import MongoClient
import matplotlib.pyplot as plt
import matplotlib.dates as md
import pandas as pd

client = MongoClient(
    "mongodb://192.168.6.26:27017/?serverSelectionTimeoutMS=5000&connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-256",
    tz_aware=False)
bili = client.bili
aichain_top_from_0401 = bili.aichain_top_from_0401

reply = bili.bili_reply
group = {
    'year': {'$year': '$time'},
    'month': {'$month': '$time'},
    'day': {'$dayOfMonth': '$time'},
    'hour': {'$hour': '$time'},
    'minutes': {'$minute': '$time'}
}

start_time = arrow.get('2021-04-07')
end_time = arrow.get('2021-04-09')

pipeline = [
    {'$match': {'user_id': 8271698, 'time': {'$gte': start_time.naive, '$lte': end_time.naive}}},
    {'$group': {'_id': group, 'count': {'$sum': 1}}}
]

cursor = reply.aggregate(pipeline)


def get_datetime(raw: dict):
    t = raw['_id']
    time = arrow.get(
        '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:00'.format(t['year'], t['month'], t['day'], t['hour'], t['minutes']))
    return time.naive


# 自定义时间刻度如何显示
def time_ticks(x, pos):
    # 在 pandas 中，按 10min 生成的时间序列与 matplotlib 要求的类型不一致
    # 需要转换成 matplotlib 支持的类型
    x = md.num2date(x)

    if x.hour != 0 and x.minute != 0 and x.second != 0:
        fmt = None
    elif x.hour != 0 and x.minute == 0 and x.second == 0:
        # 时间格式化的标准是按 10:10:10.0000 标记的
        fmt = '%H:%M'
    elif x.hour == 0 and x.minute == 0 and x.second == 0:
        fmt = '%Y-%m-%d %H:%M'
    else:
        fmt = None
    # 根据 fmt 的要求画时间刻度
    if fmt is not None:
        label = x.strftime(fmt)
    else:
        label = ''

    return label


data = []
for item in cursor:
    time = get_datetime(item)
    data.append({
        'time': time,
        'count': item['count']
    })

data.sort(key=lambda doc: doc['time'])

fig = plt.figure(figsize=(100, 7))
ax = fig.add_subplot()
x = pd.date_range(data[0]['time'], data[-1]['time'], freq='T')

data_dict = {}
for item in data:
    time = item['time'].strftime('%Y-%m-%d %H:%M:%S')
    data_dict[time] = item['count']

x_list = []
y_list = []
for pos in x:
    count = data_dict.get(str(pos), 0)
    y_list.append(count)
    if count == 0:
        x_list.append('')
    else:
        x_list.append(str(pos))

print('Plot')
ax.plot(x, y_list)
formatter = plt.FuncFormatter(time_ticks)
ax.xaxis.set_major_formatter(formatter)

locator = md.MinuteLocator()
ax.xaxis.set_major_locator(locator=locator)
print('Show')
fig.autofmt_xdate()
plt.show()
