from os import path, environ

import arrow
from git import Repo
from pymongo import MongoClient
from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

environ['http_proxy'] = 'http://192.168.6.26:7890'
environ['https_proxy'] = 'http://192.168.6.26:7890'

client = MongoClient(
    "mongodb://192.168.6.26:27017/?serverSelectionTimeoutMS=5000&connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-256",
    tz_aware=False)

up_dict = {
    27534330: 'aichan',
    161775300: 'arknight',
    256667467: 'bh3',
    401742377: 'genshin',
    318432901: 'mihoyo'
}
repo_path = './mzr_kpi_files'
repo = Repo(repo_path)


def get_sex(sex: int):
    if sex == 0:
        return '女'
    elif sex == 1:
        return '男'
    return '保密'


def get_plat(plat: int) -> str:
    if plat == 1:
        return '网页'
    elif plat == 2:
        return '安卓'
    elif plat == 3:
        return '苹果'
    else:
        return '未知'


def get_vip(vip: int) -> str:
    if vip == 0:
        return ''
    elif vip == 1:
        return '大会员'
    elif vip == 2:
        return '年度大会员'
    else:
        return str(vip)


def parse_list(raw):
    if raw is None:
        return ''
    else:
        return ','.join(raw)


def escape(raw: str):
    return ILLEGAL_CHARACTERS_RE.sub(r'⊠', raw)


def build_excel(thread_id):
    workbook = Workbook(write_only=True)
    sheet = workbook.create_sheet()
    sheet.append(('UP ID', '评论ID', '用户名', '楼层', '内容', '回复数量', '对话ID', '时间', '点赞', '设备', '用户ID', '性别', '签名',
                  '等级', 'VIP', '挂件', '粉丝牌'))
    for doc in client.bili.bili_reply.find({'thread_id': thread_id}, sort=[('time', -1)], no_cursor_timeout=True):
        temp = (
            str(doc['up_id']), str(doc['reply_id']), escape(doc['user']['username']), doc['floor'],
            escape(doc['content']), doc.get('replies_count', -1), str(doc['dialog']),
            doc['time'].strftime('%Y-%m-%d %H:%M:%S'), doc['like'], get_plat(doc.get('plat')),
            str(doc['user']['user_id']), get_sex(doc['user']['sex']), escape(doc['user']['sign']), doc['user']['level'],
            get_vip(doc['user']['vip']), escape(parse_list(doc['user']['pendants'])),
            escape(parse_list(map(lambda x: x['name'], doc['user']['sailings']))))
        sheet.append(temp)
        del temp

    return workbook


def push(user_id: int):
    repo.git.add(all=True)
    print('[{0}]Git Add.'.format(user_id))
    repo.index.commit('Update')
    print('[{0}]Git Commit.'.format(user_id))
    try:
        repo.remote(name='origin').push()
        print('[{0}]Git Pushed.'.format(user_id))
    except Exception:
        print('[{0}Git Push Failed.')


def walk_dynamic(user_id: int, last_days: int):
    dynamic_col = client.bili.bili_dynamic
    record_col = client.bili.bili_dynamic_run_record
    count = 0
    dynamic_list = list(
        dynamic_col.find({'user_id': user_id, 'time': {'$gte': arrow.get().shift(days=-last_days).naive}},
                         sort=[('time', -1)]))
    for dynamic in dynamic_list:
        record = record_col.find_one({'dynamic_id': dynamic['dynamic_id'], 'end_time': {'$exists': 1}},
                                     sort=[('start_time', -1)])

        if record is None:
            print('[{0}][{1}] Skip because no record.'.format(user_id, dynamic['dynamic_id']))
            continue

        if record.get('exported', False):
            print('[{0}][{1}] Skip.'.format(user_id, dynamic['dynamic_id']))
            continue
        workbook = build_excel(dynamic['thread_id'])

        time = arrow.get(dynamic['time']).to('Asia/Shanghai').strftime('%Y-%m-%d_%H-%M-%S')
        with open(path.join('{0}/{1}'.format(repo_path, up_dict[user_id]),
                            '{0}_{1}.xlsx'.format(dynamic['dynamic_id'], time)), 'wb') as f:
            workbook.save(f)
            del workbook
        record_col.update_one({'_id': record['_id']}, {'$set': {'exported': True}})
        print('[{0}][{1}] Exported with record: {2} at {3}.'.format(user_id, dynamic['dynamic_id'], str(record['_id']),
                                                                    time))
        count += 1
        if count % 10 == 0:
            push(user_id)

    if count % 10 != 0:
        push(user_id)


if __name__ == '__main__':
    walk_dynamic(27534330, 180)
    walk_dynamic(401742377, 365)
    walk_dynamic(256667467, 180)
    walk_dynamic(318432901, 180)
    walk_dynamic(161775300, 180)
