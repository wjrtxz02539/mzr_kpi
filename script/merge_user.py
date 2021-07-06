import time
import arrow
import schedule
from bson import ObjectId
from app import BiliReply, BiliUser, BiliReplyUserEmbedded
from mongoengine import connect

connect(db='bili',
        host='mongodb://@192.168.1.1:27017/?serverSelectionTimeoutMS=5000&connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-256')


def merge_user(user: BiliReplyUserEmbedded):
    document: BiliUser = BiliUser.objects(user_id=user.user_id).first()
    if document is None:
        document = BiliUser(user_id=user.user_id, username=user.username, avatar=user.avatar, sex=user.sex,
                            sign=user.sign, level=user.level, vip=user.vip, sailings=user.sailings,
                            pendants=user.pendants)
        modified = True
    else:
        modified = False
        if document.sign is None and user.sign is not None:
            document.sign = user.sign
            modified = True
        if document.avatar is None and user.avatar is not None:
            document.avatar = user.avatar
            modified = True
        if user.level > document.level:
            document.level = user.level
            modified = True
        if document.vip is None and user.vip is not None:
            document.vip = user.vip
            modified = True

        old_sailings_set = set(document.sailings)
        new_sailings_set = set(user.sailings)
        if old_sailings_set != new_sailings_set:
            document.sailings = list(new_sailings_set.union(old_sailings_set))
            modified = True

        old_pendants_set = set(document.pendants)
        new_pendants_set = set(user.pendants)
        if old_pendants_set != new_pendants_set:
            document.pendants = list(new_pendants_set.union(old_pendants_set))
            modified = True

    if modified:
        document.save()


def merge_with_minutes(minutes: int):
    start_time = arrow.utcnow().shift(minutes=-minutes).naive
    start_oid = ObjectId.from_datetime(start_time)
    count = 0

    for reply in BiliReply.objects(id__gte=start_oid).timeout(False).no_cache().batch_size(1000):
        reply: BiliReply
        merge_user(reply.user)
        count += 1
        if count % 1000 == 0:
            message = '[{0}] {1}'.format(start_time, count)
            print(message)
    print('[{0}] {1} Done.'.format(start_time, count))


if __name__ == '__main__':
    merge_with_minutes(10)
    schedule.every(10).minutes.do(merge_with_minutes, minutes=10)
    while True:
        schedule.run_pending()
        time.sleep(1)
